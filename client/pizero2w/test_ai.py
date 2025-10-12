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
        time.sleep(2)
        pixels.fill((0, 0, 0))
    elif keyword_index == 1:
        # Keyword 1: Only purple light for 2 seconds
        pixels.fill((128, 0, 128))
        time.sleep(2)
        pixels.fill((0, 0, 0))


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


# Initialize components
keywords = ["hey-pee-dar", "hey-pipi"]
detector = WakeWordDetector(keywords)
detector.set_callback(on_wake_word_detected)

encoder = RotaryEncoder(pin_btn=23, pin_enc_a=27, pin_enc_b=22)
encoder.set_button_callback(on_button_press)
encoder.set_rotation_callback(on_encoder_rotation)

print("Listening... Say:", ", ".join(keywords))
print("[RUN] Encoder callbacks armed")

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
    encoder.cleanup()
    detector.cleanup()
    print("[CLEANUP] All resources cleaned up", flush=True)

