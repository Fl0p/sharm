#!/usr/bin/env python3
import pvporcupine, pyaudio, struct, sys, os
import subprocess
import time
import getpass
import board
import neopixel
import random
import glob

ACCESS_KEY = os.getenv("PV_ACCESS_KEY", "YOUR_PICOVOICE_ACCESS_KEY")

# Path to custom wake word model
keywords = ["hey-pee-dar", "hey-pipi"]
keyword_paths = [os.path.join(os.path.dirname(__file__), f"{kw}.ppn") for kw in keywords]

porcupine = pvporcupine.create(access_key=ACCESS_KEY, keyword_paths=keyword_paths)

# Initialize NeoPixel
LED_PIN = board.D10
LED_COUNT = 7
BRIGHTNESS = 0.2
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=BRIGHTNESS, auto_write=True, pixel_order=neopixel.GRB)

pa = pyaudio.PyAudio()
stream = pa.open(rate=porcupine.sample_rate,
                 channels=1, format=pyaudio.paInt16,
                 input=True, frames_per_buffer=porcupine.frame_length)

print(f"Running as user: {getpass.getuser()}")
print("Listening... Say:", ", ".join(keywords))
try:
    while True:
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        idx = porcupine.process(pcm)
        if idx >= 0:
            print(f"Wake word: {keywords[idx]}")
            if idx == 0:
                # Keyword 0: Play sound and light up blue
                sounds_dir = os.path.join(os.path.dirname(__file__), "sounds")
                hello_files = glob.glob(os.path.join(sounds_dir, "hello_*.wav"))
                if hello_files:
                    random_sound = random.choice(hello_files)
                    env = os.environ.copy()
                    env['XDG_RUNTIME_DIR'] = '/tmp/xdg_runtime'
                    subprocess.Popen(["aplay", random_sound], env=env)
                pixels.fill((0, 0, 128))
                time.sleep(2)
                pixels.fill((0, 0, 0))
            elif idx == 1:
                # Keyword 1: Only purple light for 2 seconds
                pixels.fill((128, 0, 128))
                time.sleep(2)
                pixels.fill((0, 0, 0))
except KeyboardInterrupt:
    pass
finally:
    pixels.fill((0, 0, 0))
    try:
        pixels.deinit()
    except Exception:
        pass
    stream.stop_stream(); stream.close(); pa.terminate(); porcupine.delete()
