import time
from pathlib import Path
from flask import Flask, request ,jsonify
from detect import run
import uuid
import yaml
from loguru import logger
import os
import boto3
import pymongo

# Create an S3 client
# Boto3 will look for credentials in the default location(~/.aws/credentials)
#s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
# TODO (docker run -v ~/.aws/credentials:/root/.aws/credentials ...rest of the command)
# Create an S3 client with a specific region
s3 = boto3.client('s3', region_name='eu-north-1')

# List all S3 buckets

response = s3.list_buckets()

# Print the bucket names just to make s3 is working
print("S3 Buckets:")
for bucket in response['Buckets']:
    print(bucket['Name'])

# when running the docker image use the -e (env variable)
# TODO  (docker run -e BUCKET_NAME=nasimob-bucket ... rest of the command)
images_bucket = os.environ['BUCKET_NAME']

# creating a Mongo_Client instance, representing a connection to a MongoDB server.
#mongodb://mongo1:27017,mongo2:27018,mongo3:27019/?replicaSet=myReplicaSet':
# This is the connection string specifying the MongoDB replica set configuration.
# It includes the addresses and port numbers of the replica set members
# (mongo1:27017, mongo2:27018, mongo3:27019) and the name of the replica set (myReplicaSet).
mongo_client = pymongo.MongoClient('mongodb://mongo1:27017,mongo2:27018,mongo3:27019/?replicaSet=myReplicaSet')

#This selects the MongoDB database named 'yolo5-db' from the connected MongoDB server.
# If the database does not exist, MongoDB will create it when you first write data to it
db = mongo_client['yolo5-db']
#Selecting a Collection:(if it does not exist create one -this is done auto)
collection = db['predicted_summaries']

with open("data/coco128.yaml", "r") as stream:
    names = yaml.safe_load(stream)['names']

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    # Generates a UUID for this current prediction HTTP request.
    # This id can be used as a reference in logs to identify and track individual prediction requests.
    prediction_id = str(uuid.uuid4())

    logger.info(f'prediction: {prediction_id}. start processing')

    # Receives a URL parameter representing the image to download from S3
    img_name = request.args.get('imgName')
    # TODO download img_name from S3, store the local image path in original_img_path
    #  The bucket name should be provided as an env var BUCKET_NAME.
    original_img_path = download_image(img_name)
    logger.info(f'prediction: {prediction_id}/{original_img_path}. Download img completed')

    # Predicts the objects in the image
    run(
        weights='yolov5s.pt',
        data='data/coco128.yaml',
        source=original_img_path,
        project='static/data',
        name=prediction_id,
        save_txt=True
    )

    logger.info(f'prediction: {prediction_id}/{original_img_path}. done')

    # This is the path for the predicted image with labels
    # The predicted image typically includes bounding boxes drawn around the detected objects, along with class labels and possibly confidence scores.
    predicted_img_path = Path(f'static/data/{prediction_id}/{original_img_path}')

    # TODO Uploads the predicted image (predicted_img_path) to S3 (be careful not to override the original image).
    upload_predicted_image(predicted_img_path, img_name)
    # Parse prediction labels and create a summary
    pred_summary_path = Path(f'static/data/{prediction_id}/labels/{original_img_path.split(".")[0]}.txt')
    if pred_summary_path.exists():
        with open(pred_summary_path) as f:
            labels = f.read().splitlines()
            labels = [line.split(' ') for line in labels]
            labels = [{
                'class': names[int(l[0])],
                'cx': float(l[1]),
                'cy': float(l[2]),
                'width': float(l[3]),
                'height': float(l[4]),
            } for l in labels]

        logger.info(f'prediction: {prediction_id}/{original_img_path}. prediction summary:\n\n{labels}')

        prediction_summary = {
            'prediction_id': prediction_id,
            'original_img_path': str(original_img_path),
            #MongoDB expects JSON-serializable data, and PosixPath is not directly serializable
            'predicted_img_path': str(predicted_img_path),
            #convert the PosixPath object to a string before inserting it into the MongoDB collection
            'labels': labels,
            'time': time.time()
        }

        # TODO store the prediction_summary in MongoDB


        store_in_mongodb(prediction_summary)
        prediction_summary['_id'] = str(prediction_summary['_id'])

        return jsonify(prediction_summary)
    else:
        return jsonify({'error': f'prediction: {prediction_id}/{original_img_path}. prediction result not found'}), 404


def download_image(img_name):
    try:
        s3.download_file(images_bucket, img_name, img_name)
        return str(img_name)
    except Exception as e:
        print(f"Error downloading {img_name}: {e}")
        return None


def upload_predicted_image(predicted_img_path, img_name):
    predicted_img_path_tostore = f'predicted_{img_name}'
    s3.upload_file(str(predicted_img_path), images_bucket, predicted_img_path_tostore)

def store_in_mongodb(prediction_summary):
    collection.insert_one(prediction_summary)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)
