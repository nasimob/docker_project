#!/bin/bash
#kill all ngrok connection so the ngrok will be the first one in the tunnels
killall ngrok
ngrok http 8443 > /dev/null &
# Wait for ngrok to be available
while ! nc -z localhost 4040; do
  sleep 5 #
done
ngrok_url="$(curl -s localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')"
echo $ngrok_url

# Check if .env file exists and if NGROK_URL is already set
if [ -e .env ]; then
  sed -i "s|^TELEGRAM_APP_URL=.*$|TELEGRAM_APP_URL=$ngrok_url|" .env
fi

