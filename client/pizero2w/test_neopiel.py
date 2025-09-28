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
    pi.wave_clear()
    
    # WS2812 timing constants (in microseconds)
    T0H = 0.4   # 0 bit high time
    T0L = 0.85  # 0 bit low time  
    T1H = 0.8   # 1 bit high time
    T1L = 0.45  # 1 bit low time
    
    # Build waveform for each pixel
    for r, g, b in colors:
        # WS2812 expects GRB order
        for byte_val in [g, r, b]:
            for bit in range(7, -1, -1):  # MSB first
                if (byte_val >> bit) & 1:
                    # Send '1' bit
                    pi.wave_add_generic([pigpio.pulse(1 << LED_PIN, 0, int(T1H * 1000)),
                                       pigpio.pulse(0, 1 << LED_PIN, int(T1L * 1000))])
                else:
                    # Send '0' bit  
                    pi.wave_add_generic([pigpio.pulse(1 << LED_PIN, 0, int(T0H * 1000)),
                                       pigpio.pulse(0, 1 << LED_PIN, int(T0L * 1000))])
    
    # Add reset pulse (>50us low)
    pi.wave_add_generic([pigpio.pulse(0, 1 << LED_PIN, 100)])
    
    wid = pi.wave_create()
    pi.wave_send_once(wid)
    
    # Wait for transmission to finish
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
