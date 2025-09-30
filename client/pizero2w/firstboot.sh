#!/usr/bin/env bash
set -euo pipefail

# --- base packages ---
apt-get update
apt-get -y upgrade
apt-get -y install \
  git wget cmake curl vim htop i2c-tools pigpio \
  python3 python3-pip python3-venv python3-setuptools python3-smbus python3-pigpio\
  alsa-utils pulseaudio pulseaudio-utils libasound2 mpv 

# edit gpio service
# sudo systemctl edit pigpiod
# sudo cat /etc/systemd/system/pigpiod.service
# sudo systemctl daemon-reload
# sudo systemctl enable --now pigpiod

# --- WM8960-Audio-HAT ---
git clone https://github.com/Fl0p/WM8960-Audio-HAT.git
cd WM8960-Audio-HAT
sudo ./install.sh
sudo reboot

# --- test ---