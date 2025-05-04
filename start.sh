#!/bin/bash

cd $(dirname $0)
pwd

if [ -z "$SHARM" ]; then
    echo "Should be run in a SHARM container"
    exit 1
fi

# load .env
if [ -f .env ]; then
    source .env
fi

mkfifo ${FIFO_PATH}
chmod 666 ${FIFO_PATH}

echo "Starting mpd Client on port ${MPD_CLIENT_PORT} stream port ${MPD_STREAM_PORT}"
mpd /etc/mpd.conf

echo "Starting snapserver"
snapserver -d -c /etc/snapserver.conf

echo "Starting ympd with port ${YMPD_PORT}"
ympd -w ${YMPD_PORT}