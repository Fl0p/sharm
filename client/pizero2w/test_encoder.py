#!/usr/bin/env python3
import pigpio
import time

# Encoder pins
PIN_A = 22
PIN_B = 23
PIN_BTN = 24

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpiod is not running! Start it with: sudo pigpiod")

# Configure pins as inputs with pull-up resistors
for pin in (PIN_A, PIN_B, PIN_BTN):
    pi.set_mode(pin, pigpio.INPUT)
    pi.set_pull_up_down(pin, pigpio.PUD_UP)

# State variables
position = 0
last_a = pi.read(PIN_A)

def rotary_callback(gpio, level, tick):
    """Handle rotary encoder rotation."""
    global position, last_a
    a = pi.read(PIN_A)
    b = pi.read(PIN_B)
    if a != last_a:
        if a == b:
            position += 1
        else:
            position -= 1
        print(f"Encoder position: {position}")
        last_a = a

def button_callback(gpio, level, tick):
    """Handle button press."""
    if level == 0:  # button pressed
        print("Button pressed")

# Register callbacks
pi.callback(PIN_A, pigpio.EITHER_EDGE, rotary_callback)
pi.callback(PIN_BTN, pigpio.FALLING_EDGE, button_callback)

print("Rotate the encoder on GPIO22/23 and press the button on GPIO24 (Ctrl+C to exit)")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    pi.stop()
