#!/bin/bash

cd $(dirname $0)

pwd

#load .env
if [ -f .env ]; then
    source .env
fi

docker compose down || true

docker compose up -d --build

if [ $? -eq 0 ]; then
    echo "Docker container started successfully"
else
    echo "Error starting Docker container"
    exit 1
fi

echo "run 'mpv http://localhost:${MPD_STREAM_PORT}' to listen to the stream"

echo "do you want to start listening to the SNAPSERVER stream? (y/n)"
read answer

if [ "$answer" = "y" ]; then
    snapclient -h localhost -p ${SNAPSERVER_PORT}
fi

echo "do you want to start listening to the MPD stream? (y/n)"
read answer

if [ "$answer" = "y" ]; then
    mpv http://localhost:${MPD_STREAM_PORT} \
    --cache=no \
    --demuxer-readahead-secs=0 \
    --demuxer-max-bytes=8 \
    --untimed \
    --no-cache-pause \
    --hr-seek=no \
    --audio-buffer=0 \
    --autosync=0
fi

exit 0

