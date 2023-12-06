import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
import  boto3
import requests

s3 = boto3.client('s3', region_name=os.environ['REGION'])
images_bucket = os.environ['BUCKET_NAME']
class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(chat_id,InputFile(img_path))

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        if 'text' in msg:
            text_content = msg['text']
            self.send_text(msg['chat']['id'], f'Your original message: {text_content}')
        else :
            self.send_text(msg['chat']['id'], 'Message does not contain text.')



class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])


class ObjectDetectionBot(Bot):
    def download_image_pred_from_s3(self,img_name,):
        try:
            base = f'predicted_{img_name}'
            s3.download_file(images_bucket, base, base)
            return str(base)
        except Exception as e:
            print(f"Error downloading {base}: {e}")
            return None
    def clean_response(self , pred_response):
        base_string = 'Detected Objects:\n'
        objects_dict = {}
        for label in pred_response['labels'] :
            class_type = label['class']
            if class_type in objects_dict:
                objects_dict[class_type] += 1
            else:
                objects_dict[class_type] = 1
        for class_t , counts in objects_dict.items() :
            base_string += f"{class_t}: {counts}\n"
        return  base_string
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if self.is_current_msg_photo(msg):
            # TODO download the user photo (utilize download_user_photo)
            path = self.download_user_photo(msg)
            photo_name = path.split('/')[-1]

            # TODO upload the photo to S3
            s3.upload_file(str(path), images_bucket, str(photo_name))
            # TODO send a request to the `yolo5` service for prediction

            prediction_url = f'http://docker_project-yolo5-1:8081/predict?imgName={str(photo_name)}'
            response = requests.post(prediction_url)
            if response.status_code == 200 :
                response = self.clean_response(response.json())
            else:
                print('pred req failed')
            # TODO send results to the Telegram end-user
            self.send_text(msg['chat']['id'], response)
            path = self.download_image_pred_from_s3(photo_name)
            self.send_photo(msg['chat']['id'],path)
        elif "text" in msg:
            content_msg =msg['text']
            self.send_text(msg['chat']['id'], f'Your original message: {content_msg}\n send me a photo')
        else:
            self.send_text(msg['chat']['id'], "i don't know how to handle this  \n send me a photo")
