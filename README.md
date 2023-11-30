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
MONGO_URI=mongodb://mongo(mongo-container-name):27017/your-database

run the service by :docker-compose up -d
Usage

    Send images to PolyBot to perform object detection.
  
