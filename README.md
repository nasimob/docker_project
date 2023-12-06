# docker_project
# PolyBot: Your Telegram Bot with YOLO5 Object Detection

PolyBot is a Telegram bot that incorporates YOLO5 object detection capabilities. It allows users to interact with Telegram and perform object detection on images sent to the bot.

## Features

- **ObjectDetectionBot:** Detects objects in images sent to the bot using YOLO5.

## Prerequisites

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)
- create a Telegram Bot:

    Download and install telegram desktop (you can use your phone app as well).
    here : https://desktop.telegram.org/
    Once installed, create your own Telegram Bot by following this section to create a bot.
    here :https://core.telegram.org/bots/features#botfather
    Once you have your telegram token you can move to the next step.

## Getting Started
1. Clone the repository:
2. Create a .env file in the project root and add your environment variables:
TELEGRAM_TOKEN=your-telegram-token
TELEGRAM_APP_URL=https://your-app-url.com
BUCKET_NAME=your-s3-bucket-name
REGION=your-bucket-region
3.run the service by :./run_all.sh
be careful when running run_all.sh the init_ngrok.sh will kill all ngrok tunnels if you dont want that you can delete init_ngrok.sh  from the run_all.sh and change the TELEGRAM_APP_URL in the .env file manually
4.start sending photos to the bot.

  
