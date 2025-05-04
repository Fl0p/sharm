#!/bin/bash

cd $(dirname $0)
pwd

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg could not be found"
    exit 1
fi

mkfifo /tmp/snap_fifo
mkfifo /tmp/snap_ch1
mkfifo /tmp/snap_ch2
mkfifo /tmp/snap_ch3
mkfifo /tmp/snap_ch4
mkfifo /tmp/snap_ch5
mkfifo /tmp/snap_ch6


ffmpeg -f s16le -ac 6 -ar 48000 -i /tmp/snap_fifo \
  -filter_complex "[0:a]channelsplit=channel_layout=5.1[ch1][ch2][ch3][ch4][ch5][ch6]" \
  -map "[ch1]" -f s16le /tmp/snap_ch1 \
  -map "[ch2]" -f s16le /tmp/snap_ch2 \
  -map "[ch3]" -f s16le /tmp/snap_ch3 \
  -map "[ch4]" -f s16le /tmp/snap_ch4 \
  -map "[ch5]" -f s16le /tmp/snap_ch5 \
  -map "[ch6]" -f s16le /tmp/snap_ch6
