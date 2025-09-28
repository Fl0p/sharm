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
    
    # WS2812B timing constants (nanoseconds -> microseconds)
    # More precise timing for WS2812B
    T0H = 400   # 0.4us = 400ns -> 0.4us  
    T0L = 850   # 0.85us = 850ns -> 0.85us
    T1H = 800   # 0.8us = 800ns -> 0.8us
    T1L = 450   # 0.45us = 450ns -> 0.45us
    
    # Build waveform for each pixel
    for r, g, b in colors:
        # WS2812 expects GRB order
        for byte_val in [g, r, b]:
            for bit in range(7, -1, -1):  # MSB first
                if (byte_val >> bit) & 1:
                    # Send '1' bit: high for T1H, low for T1L
                    pi.wave_add_generic([
                        pigpio.pulse(1 << LED_PIN, 0, T1H),
                        pigpio.pulse(0, 1 << LED_PIN, T1L)
                    ])
                else:
                    # Send '0' bit: high for T0H, low for T0L
                    pi.wave_add_generic([
                        pigpio.pulse(1 << LED_PIN, 0, T0H),
                        pigpio.pulse(0, 1 << LED_PIN, T0L)
                    ])
    
    # Add reset pulse (>50us low = 50000ns)
    pi.wave_add_generic([pigpio.pulse(0, 1 << LED_PIN, 50000)])
    
    wid = pi.wave_create()
    if wid >= 0:
        pi.wave_send_once(wid)
        
        # Wait for transmission to finish
        while pi.wave_tx_busy():
            time.sleep(0.001)
        pi.wave_delete(wid)

def color_all(r, g, b):
    """ Fill the entire strip with one color """
    send_pixels([(r, g, b)] * LED_COUNT)

try:
    print("Starting LED test... Press Ctrl+C to stop")
    while True:
        print("Red")
        color_all(255, 0, 0)  # red
        time.sleep(1)
        print("Green") 
        color_all(0, 255, 0)  # green
        time.sleep(1)
        print("Blue")
        color_all(0, 0, 255)  # blue
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping... turning off LEDs")
    color_all(0, 0, 0)  # turn off on exit
    time.sleep(0.1)  # give time for the off command to complete
    pi.wave_clear()  # clear any remaining waves
    pi.stop()
    print("Done.")
