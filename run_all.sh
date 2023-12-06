#!/bin/bash

# Run init_ngrok.sh
echo "Running init_ngrok.sh..."
./init_ngrok.sh

# Wait for ngrok to start
sleep 5

# Run docker-compose
echo "Running docker-compose..."
docker compose up -d

# Wait for Docker containers to start
sleep 20

# Run init_rep_set.sh
echo "Running init_rep_set.sh..."
./init_rep_set.sh

echo "All scripts executed successfully."
