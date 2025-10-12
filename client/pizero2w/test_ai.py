#!/usr/bin/env python3
import os
import time
import subprocess
import random
import glob
import board
import neopixel

from wake_word_detector import WakeWordDetector
from rotary_encoder import RotaryEncoder
from ups import UPS, BatteryStatus


# Initialize NeoPixel
LED_PIN = board.D10
LED_COUNT = 7
BRIGHTNESS = 0.2
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=BRIGHTNESS, auto_write=True, pixel_order=neopixel.GRB)


def ts():
    """Generate timestamp string"""
    t = time.time()
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)) + f".{int((t % 1)*1000):03d}"


# Wake word detection handler
def on_wake_word_detected(keyword_index, keyword_name):
    """Handler for wake word detection"""
    print(f"[WAKE] {ts()} Wake word detected: {keyword_name}")
    
    if keyword_index == 0:
        # Keyword 0: Play sound and light up blue
        sounds_dir = os.path.join(os.path.dirname(__file__), "sounds")
        hello_files = glob.glob(os.path.join(sounds_dir, "hello_*.wav"))
        if hello_files:
            random_sound = random.choice(hello_files)
            subprocess.Popen(["aplay", random_sound])
        pixels.fill((0, 0, 128))
    elif keyword_index == 1:
        # Keyword 1: Purple light
        pixels.fill((128, 0, 128))


# Encoder rotation handler
def on_encoder_rotation(direction, position, degrees, rotations):
    """Handler for encoder rotation"""
    print(f"[ENC] {ts()} {direction} rotations={rotations} remainder={degrees:.1f}° (raw={position})", flush=True)


# Button press handler
def on_button_press(level, tick):
    """Handler for button events"""
    if level == 2:
        print(f"[WD]  {ts()} watchdog timeout", flush=True)
        return
    print(f"[BTN] {ts()} level={level} tick={tick}", flush=True)


# UPS battery change handler
def on_battery_change(voltage, soc, status):
    """Handler for battery state changes"""
    print(f"[UPS] {ts()} Battery: {voltage:.2f}V {soc:.1f}% [{status.value}]", flush=True)


# UPS power change handler
def on_power_change(is_connected):
    """Handler for power adapter connection changes"""
    state = "CONNECTED" if is_connected else "DISCONNECTED"
    print(f"[UPS] {ts()} Power adapter: {state}", flush=True)


# UPS low battery alert handler
def on_low_battery(voltage, soc):
    """Handler for low battery alert"""
    print(f"[UPS] {ts()} ⚠️  LOW BATTERY ALERT! {voltage:.2f}V {soc:.1f}%", flush=True)


# Initialize components
keywords = ["hey-pee-dar", "hey-pipi"]
detector = WakeWordDetector(keywords)
detector.set_callback(on_wake_word_detected)

encoder = RotaryEncoder(pin_btn=23, pin_enc_a=27, pin_enc_b=22)
encoder.set_button_callback(on_button_press)
encoder.set_rotation_callback(on_encoder_rotation)

ups = UPS(auto_update=True, update_interval=2.0)
ups.initialize()
ups.on_battery_change(on_battery_change)
ups.on_power_change(on_power_change)
ups.on_low_battery(on_low_battery)

print("Listening... Say:", ", ".join(keywords))
print("[RUN] Encoder callbacks armed")
print("[RUN] UPS monitoring started")

# Main loop
try:
    while True:
        detector.process_audio()
except KeyboardInterrupt:
    print("\n[EXIT] KeyboardInterrupt", flush=True)
finally:
    pixels.fill((0, 0, 0))
    try:
        pixels.deinit()
    except Exception:
        pass
    ups.cleanup()
    encoder.cleanup()
    detector.cleanup()
    print("[CLEANUP] All resources cleaned up", flush=True)

