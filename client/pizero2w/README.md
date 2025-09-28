This is sharm client for rasppery zero
---

#1 SB Components audio codec hat WM8960 chip
- driver https://github.com/ubopod/WM8960-Audio-HAT#

#2 Waveshare UPS HAT (C) 
- setup https://www.waveshare.com/wiki/UPS_HAT_(C)

# Neopixel




pigpio‑daemon
```
sudo apt update
sudo apt install pigpio python3-pigpio
sudo systemctl enable --now pigpiod

```

venv
```
python3 -m venv ~/venv
source ~/venv/bin/activate
```

deps
```
pip install rpi_ws281x pigpio
```