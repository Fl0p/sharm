#!/usr/bin/env python3
import time
import pigpio

# === LED strip settings ===
LED_PIN = 14         # GPIO pin for LED strip
LED_COUNT = 7        # number of LEDs
FREQ = 800000       # WS2812 frequency = 800 kHz

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("❌ Failed to connect to pigpio daemon. Make sure it's running with sudo.")

def send_pixels(colors):
    """
    Send an array of [(R, G, B), ...] to the strip.
    """
    # WS2812 expects GRB order; pigpio adds the latch automatically.
    data = bytearray()
    for r, g, b in colors:
        data += bytes([g, r, b])

    # Build the wave and transmit
    pi.wave_clear()
    pi.wave_add_serial(LED_PIN, FREQ, data, 0, 8, 2)  # 8-bit, T1=1us, T2=2us by default
    wid = pi.wave_create()
    pi.wave_send_once(wid)

    # wait for transmission to finish
    while pi.wave_tx_busy():
        time.sleep(0.001)
    pi.wave_delete(wid)

def color_all(r, g, b):
    """ Fill the entire strip with one color """
    send_pixels([(r, g, b)] * LED_COUNT)

try:
    while True:
        color_all(255, 0, 0)  # red
        time.sleep(0.5)
        color_all(0, 255, 0)  # green
        time.sleep(0.5)
        color_all(0, 0, 255)  # blue
        time.sleep(0.5)

except KeyboardInterrupt:
    color_all(0, 0, 0)  # turn off on exit
    pi.stop()
