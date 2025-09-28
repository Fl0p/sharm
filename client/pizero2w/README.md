This is sharm client for rasppery zero
---

#1 SB Components audio codec hat WM8960 chip
- driver https://github.com/ubopod/WM8960-Audio-HAT#

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


# Install
```
sudo apt update
sudo apt install -y python3-venv python3-pip
sudo apt install pigpio python3-pigpio
sudo systemctl enable --now pigpiod

```

venv
```
python3 -m venv ~/venv
source ~/venv/bin/activate
pip install --upgrade pip
```

deps
```
pip install adafruit-blinka adafruit-circuitpython-neopixel
```