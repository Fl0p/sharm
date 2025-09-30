This is sharm client for rasppery zero
===

# SB Components audio codec hat WM8960 chip
---
- setup https://learn.sb-components.co.uk/Audio-Codec-HAT-for-Raspberry-Pi
- fixed driver https://github.com/Fl0p/WM8960-Audio-HAT.git

# UPS-Lite V1.3 by XiaoJ
---
- setup https://github.com/linshuqin329/UPS-Lite/blob/master/UPS-Lite_V1.3_CW2015/Instructions%20for%20UPS-Lite%20V1.3.pdf
- repo https://github.com/linshuqin329/UPS-Lite
- test:
```
while true; do echo "$(date +%H:%M:%S) - Reg 0x08: $(i2cget -y 1 0x62 0x08)  Reg 0x0A: $(i2cget -y 1 0x62 0x0A)"; sleep 0.5; done
```

# Neopixel
---
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


#pinout 
```
+-----+-----------+---------+     +-----+-----------+---------+
| Pin |   Name    |         |     | Pin |   Name    |         |
+-----+-----------+---------+     +-----+-----------+---------+
|  1  |  3.3V     |         |     |  2  |  5V       |         |
|  3  |  SDA1     | WM8960* |     |  4  |  5V       | Neopix  |
|  5  |  SCL1     | WM8960* |     |  6  |  GND      | Neopix  |
|  7  |  GPIO4    | UPS     |     |  8  |  TXD0     |         |
|  9  |  GND      |         |     | 10  |  RXD0     |         |
| 11  |  GPIO17   | WM8960_ |     | 12  |  GPIO18   | WM8960  |
| 13  |  GPIO27   | Enc_A   |     | 14  |  GND      | Enc_Gnd |
| 15  |  GPIO22   | Enc_B   |     | 16  |  GPIO23   | Enc_Btn |
| 17  |  3.3V     | Enc_Vcc |     | 18  |  GPIO24   | WM8960? |
| 19  |  MOSI     | Neopix  |     | 20  |  GND      | WM8960  |
| 21  |  MISO     |         |     | 22  |  GPIO25   |         |
| 23  |  SCLK     |         |     | 24  |  CE0      |         |
| 25  |  GND      | WM8960  |     | 26  |  CE1      |         |
| 27  |  SDA0     |         |     | 28  |  SCL0     |         |
| 29  |  GPIO5    |         |     | 30  |  GND      |         |
| 31  |  GPIO6    |         |     | 32  |  GPIO12   |         |
| 33  |  GPIO13   |         |     | 34  |  GND      | WM8960  |
| 35  |  GPIO19   | WM8960  |     | 36  |  GPIO16   |         |
| 37  |  GPIO26   |         |     | 38  |  GPIO20   | WM8960  |
| 39  |  GND      |         |     | 40  |  GPIO21   | WM8960  |
+-----+-----------+---------+     +-----+-----------+---------+

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
---
- Install
```
sudo apt install -y pigpio python3-pigpio
```

- edit
```
sudo systemctl edit pigpiod
```
change to
```
[Service]
ExecStart=
ExecStart=/usr/bin/pigpiod -t 0 -s 10 -x 0x08C00010
```

```
sudo systemctl enable --now pigpiod
```


Read gpio
```
while true; do raspi-gpio get 4; sleep 0.2; done
while true; do raspi-gpio get 27; sleep 0.2; done
while true; do raspi-gpio get 22; sleep 0.2; done
while true; do raspi-gpio get 23; sleep 0.2; done
```

# Python
---

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