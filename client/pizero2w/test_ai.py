#!/usr/bin/env python3
import os
import time
import subprocess
import random
import glob
import getpass
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

# Global MPV process and state
mpv_process = None
radio_is_playing = False


def ts():
    """Generate timestamp string"""
    t = time.time()
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)) + f".{int((t % 1)*1000):03d}"


def get_audio_env():
    """Get environment with PulseAudio settings"""
    env = os.environ.copy()
    env['XDG_RUNTIME_DIR'] = '/tmp/xdg_runtime'
    return env


def flash_pixels(color, duration=1):
    """Flash pixels with given color for duration seconds"""
    pixels.fill(color)
    time.sleep(duration)
    pixels.fill((0, 0, 0))


def stop_mpv():
    """Stop MPV if it's running"""
    global mpv_process
    if mpv_process and mpv_process.poll() is None:
        mpv_process.terminate()
        try:
            mpv_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            mpv_process.kill()
        print(f"[MPV] {ts()} Stopped")
        mpv_process = None
        return True
    return False


def toggle_radio():
    """Toggle radio playback on/off"""
    global mpv_process, radio_is_playing
    
    if radio_is_playing:
        # Radio is playing, stop it
        stop_mpv()
        radio_is_playing = False
        print(f"[RADIO] {ts()} OFF")
        flash_pixels((128, 0, 0), 0.1)
    else:
        # Radio is not playing, start it
        mpv_process = subprocess.Popen(["mpv", "https://stream.radioparadise.com/aac-128"], env=get_audio_env())
        radio_is_playing = True
        print(f"[RADIO] {ts()} ON")
        flash_pixels((128, 0, 128))


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
            subprocess.Popen(["aplay", random_sound], env=get_audio_env())
        flash_pixels((0, 0, 128))
    elif keyword_index == 1:
        # Keyword 1: Toggle radio
        toggle_radio()


# Encoder rotation handler
def on_encoder_rotation(direction, position, degrees, rotations):
    """Handler for encoder rotation"""
    print(f"[ENC] {ts()} {direction} rotations={rotations} remainder={degrees:.1f}° (raw={position})", flush=True)
    
    # Adjust volume using amixer
    try:
        if direction == "CW":
            subprocess.run(["amixer", "set", "Master", "5%+"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif direction == "CCW":
            subprocess.run(["amixer", "set", "Master", "5%-"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        print(f"[VOL] {ts()} Volume {direction}", flush=True)
    except Exception as e:
        print(f"[VOL] {ts()} Error adjusting volume: {e}", flush=True)


# Button press handler
def on_button_press(level, tick):
    """Handler for button events"""
    if level == 2:
        print(f"[WD]  {ts()} watchdog timeout", flush=True)
        return
    print(f"[BTN] {ts()} level={level} tick={tick}", flush=True)
    
    # Toggle radio
    toggle_radio()


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

ups = UPS(auto_update=True, update_interval=10.0)
ups.initialize()
ups.on_battery_change(on_battery_change)
ups.on_power_change(on_power_change)
ups.on_low_battery(on_low_battery)

print(f"Running as user: {getpass.getuser()}")
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
    stop_mpv()
    radio_is_playing = False
    pixels.fill((0, 0, 0))
    try:
        pixels.deinit()
    except Exception:
        pass
    ups.cleanup()
    encoder.cleanup()
    detector.cleanup()
    print("[CLEANUP] All resources cleaned up", flush=True)

