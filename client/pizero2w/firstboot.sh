#!/usr/bin/env bash
set -euo pipefail

# raspi-config
CONFIG="/boot/firmware/config.txt"
for param in "dtparam=i2c_arm=on" "dtparam=i2s=on" "dtparam=spi=on"; do
  if ! grep -q "^$param" "$CONFIG"; then
    echo "$param" >> "$CONFIG"
  else
    sed -i "s/^#*$param/$param/" "$CONFIG"
  fi
done


# --- base packages ---
apt-get update
apt-get -y upgrade
apt-get -y install \
  git wget cmake curl vim htop i2c-tools pigpio \
  python3 python3-pip python3-venv python3-setuptools python3-smbus python3-pigpio\
  alsa-utils pulseaudio pulseaudio-utils libasound2 mpv 

#locale
sudo locale-gen en_GB.UTF-8
sudo update-locale LANG=en_GB.UTF-8 LC_ALL=en_GB.UTF-8

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