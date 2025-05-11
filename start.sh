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

echo "Starting D-Bus daemon"
# Ensure D-Bus is running (dependency for systemd units)
RUNNING_DBUS=$(ps aux | grep '[d]bus-daemon --system' | cat)
if [ -z "$RUNNING_DBUS" ]; then
    echo "D-Bus daemon not running, attempting to start..."
    service dbus start
    sleep 1 # Give dbus a moment to start
else
    echo "D-Bus daemon is already running."
fi

echo "Starting Avahi daemon"
avahi-daemon -D --no-chroot
ps aux | grep avahi-daemon | cat

echo "Starting mpd Client on port ${MPD_CLIENT_PORT} stream port ${MPD_STREAM_PORT}"
mpd /etc/mpd.conf

echo "Avahi-browse show services"
avahi-browse -a -t -r

echo "Starting ympd with port ${YMPD_PORT}"
ympd -w ${YMPD_PORT} &

echo "--------------------------------"

echo "Starting snapserver"
snapserver -c /etc/snapserver.conf