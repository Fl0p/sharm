#!/bin/bash

cd $(dirname $0)

pwd

#load .env
if [ -f .env ]; then
    source .env
fi

docker compose down --rmi all || true

docker compose up -d --build --force-recreate

if [ $? -eq 0 ]; then
    echo "Docker container started successfully"
else
    echo "Error starting Docker container"
    exit 1
fi

exit 0

echo "run 'mpv http://localhost:${MPD_STREAM_PORT}' to listen to the stream"

echo "do you want to start listening to the SNAPSERVER stream? (y/n)"
read answer

if [ "$answer" = "y" ]; then
    #snapclient -h localhost -p ${SNAPSERVER_PORT}
    snapclient -h localhost -p ${SNAPSERVER_PORT} --logsink null -i 1 --player file:filename=stdout | \
    ffplay -f s16le -ar 48000 -ch_layout 5.1 -af "pan=mono|c0=c2" -fflags nobuffer -flags low_delay -probesize 32 -analyzeduration 0 -
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

