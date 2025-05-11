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

echo "create fifo ${FIFO_PATH} ${FIFO_PATH_STEREO}"
rm -f ${FIFO_PATH}
mkfifo ${FIFO_PATH}
chmod 666 ${FIFO_PATH}

rm -f ${FIFO_PATH_STEREO}
mkfifo ${FIFO_PATH_STEREO}
chmod 666 ${FIFO_PATH_STEREO}
echo "FIFO created"

echo "Starting JACK server"
jackd -R -S -d dummy -r48000 -p64 &
JACK_PID=$!
sleep 2

jack_connect system:playback_1 system:capture_1
jack_connect system:playback_2 system:capture_2

# # Check JACK connections
echo "Checking JACK connections"
jack_lsp
jack_lsp -c
echo "JACK ready. ALSA-applications can open pcm 'jack'."

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

# echo "Starting PulseAudio service from pulse.sh..."
# ./pulse.sh
# # Assuming pulse.sh will exit on error due to 'set -e'
# echo "PulseAudio service script call completed."

echo "Starting mpd Client on port ${MPD_CLIENT_PORT} stream port ${MPD_STREAM_PORT}"
mpd /etc/mpd.conf
sleep 2 #give mpd a moment to start or fail
if ! mpc status > /dev/null 2>&1; then
    echo "MPD failed to start. Check /var/log/mpd/mpd.log"
    cat /var/log/mpd/mpd.log || true
    exit 1
fi
echo "MPD started."


echo "Starting ympd with port ${YMPD_PORT}"
ympd -w ${YMPD_PORT} &
YMPD_PID=$!
sleep 2 # Give ympd a moment to start or fail
# Check if process is running by PID and listening on port
if ! kill -0 $YMPD_PID > /dev/null 2>&1; then
    echo "ympd failed to start (process $YMPD_PID not found)."
    # You might want to check ympd logs here if available
    cat /var/log/ympd/ympd.log || true
    sleep 10
    exit 1
else
    echo "ympd started successfully. PID: $YMPD_PID. Listening on port ${YMPD_PORT}."
fi


echo "--------------------------------"
echo "Avahi-browse show services"
avahi-browse -a -t -r
echo "--------------------------------"

echo "Starting snapserver"
snapserver -c /etc/snapserver.conf