#!/bin/bash

pwd
ls -la
whoami

if [ -z "$SHARM" ]; then
    echo "Should be run in a SHARM container"
    exit 1
fi

# load .env
if [ -f .env ]; then
    source .env
fi

echo "Starting mpd Client on port ${MPD_CLIENT_PORT} stream port ${MPD_STREAM_PORT}"
mpd /etc/mpd.conf

echo "Starting ympd with port ${YMPD_PORT}"
ympd -w ${YMPD_PORT}