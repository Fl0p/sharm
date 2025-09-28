#!/usr/bin/env python3
import time
import board
import neopixel

# === LED strip settings ===
# DIN connected to GPIO12
LED_PIN = board.D12  # change if you wire DIN to another pin
LED_COUNT = 7  # number of LEDs
BRIGHTNESS = 0.2
PIXEL_ORDER = neopixel.GRB  # most WS2812B are GRB

# Initialize NeoPixel
pixels = neopixel.NeoPixel(
    LED_PIN,
    LED_COUNT,
    brightness=BRIGHTNESS,
    auto_write=True,
    pixel_order=PIXEL_ORDER,
)

def color_all(r, g, b):
    """Fill the entire strip with one color."""
    pixels.fill((r, g, b))

try:
    print("Starting LED test... Press Ctrl+C to stop")
    while True:
        print("Red")
        color_all(255, 0, 0)
        time.sleep(1)
        print("Green")
        color_all(0, 255, 0)
        time.sleep(1)
        print("Blue")
        color_all(0, 0, 255)
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping... turning off LEDs")
    color_all(0, 0, 0)
    time.sleep(0.1)
    try:
        pixels.deinit()
    except Exception:
        pass
    print("Done.")
