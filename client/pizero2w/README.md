This is sharm client for rasppery zero
---

#1 SB Components audio codec hat WM8960 chip
- setup https://learn.sb-components.co.uk/Audio-Codec-HAT-for-Raspberry-Pi
- fixed driver https://github.com/ubopod/WM8960-Audio-HAT#

#2 Waveshare UPS HAT (C) 
- setup https://www.waveshare.com/wiki/UPS_HAT_(C)

# Neopixel
DIN -> GPIO10 (MOSI). Enable SPI for sudo-less usage:
```
sudo raspi-config  # Interface Options -> SPI -> Enable
# or add to /boot/config.txt:
# dtparam=spi=on
```
Run without sudo:
```
python3 client/pizero2w/test_neopiel.py
```


# Install system
```
sudo raspi-config
#enable spi i2c
sudo update-locale LANG=en_GB.UTF-8 LC_ALL=en_GB.UTF-8
sudo apt update
sudo apt install -y git wget cmake
sudo apt install -y i2c-tools
sudo apt install -y libasound2 alsa-utils mpv
sudo apt install -y python3
sudo apt install -y --upgrade python3-setuptools
sudo apt install -y python3-venv python3-pip
```

# GPIO
```
sudo apt install -y pigpio python3-pigpio
sudo systemctl edit pigpiod
```

# exit
```
[Service]
ExecStart=
ExecStart=/usr/bin/pigpiod -t 1 -s 10 -x 0x08C00000
```

```
sudo systemctl enable --now pigpiod
```

venv
```
python3 -m venv ~/venv --system-site-packages
source ~/venv/bin/activate
pip install --upgrade pip
```

deps
```
pip install --upgrade adafruit-blinka adafruit-python-shell adafruit-circuitpython-neopixel
```