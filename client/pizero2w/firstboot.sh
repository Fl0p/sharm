#!/usr/bin/env bash
set -euo pipefail

# check if sudo
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# raspi-config
echo "Enabling i2c, i2s, spi"
CONFIG="/boot/firmware/config.txt"
for param in "dtparam=i2c_arm=on" "dtparam=i2s=on" "dtparam=spi=on"; do
  if ! grep -q "^$param" "$CONFIG"; then
    echo "$param" >> "$CONFIG"
  else
    sed -i "s/^#*$param/$param/" "$CONFIG"
  fi
done

# locale setup first to avoid warnings during package installation
echo "Updating locale"
sed -i 's/^# *en_GB.UTF-8/en_GB.UTF-8/' /etc/locale.gen
locale-gen en_GB.UTF-8
update-locale LANG=en_GB.UTF-8 LC_ALL=en_GB.UTF-8
export LANG=en_GB.UTF-8
export LC_ALL=en_GB.UTF-8

echo "Updating system"
# --- base packages ---
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -y -o Dpkg::Options::="--force-confnew" upgrade
apt-get -y -o Dpkg::Options::="--force-confnew" install \
  git wget cmake curl vim htop i2c-tools pigpio \
  python3 python3-pip python3-venv python3-setuptools python3-smbus python3-pigpio\
  alsa-utils pulseaudio pulseaudio-utils libasound2 mpv

# edit gpio service
# sudo systemctl edit pigpiod
mkdir -p /etc/systemd/system/pigpiod.service.d
sudo tee /etc/systemd/system/pigpiod.service.d/override.conf > /dev/null <<'EOF'
[Service]
ExecStart=
ExecStart=/usr/bin/pigpiod -t 0 -s 10 -x 0x08C00010
EOF
systemctl daemon-reload
systemctl restart pigpiod
systemctl enable --now pigpiod
#check gpio
raspi-gpio get 23


# --- WM8960-Audio-HAT ---
echo "Installing WM8960-Audio-HAT"
CURRENT_DIR=$(pwd)
cd /tmp
git clone https://github.com/Fl0p/WM8960-Audio-HAT.git
cd WM8960-Audio-HAT
./install.sh
cd "$CURRENT_DIR"
rm -rf /tmp/WM8960-Audio-HAT
reboot

# --- test ---