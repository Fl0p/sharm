#!/usr/bin/env python3
import time
import sys
import os
from rotary_encoder import RotaryEncoder

def ts():
    t = time.time()
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)) + f".{int((t % 1)*1000):03d}"

def main():
    print(f"[INIT] Python={sys.version.split()[0]} argv={sys.argv} cwd={os.getcwd()}", flush=True)
    
    # Create encoder instance
    encoder = RotaryEncoder(
        pin_btn=23,
        pin_enc_a=27,
        pin_enc_b=22,
        watchdog_ms=1000,
        glitch_us=0,
        pulses_per_rotation=80
    )
    
    print(f"[INIT] RotaryEncoder initialized", flush=True)
    print(f"[CFG] BTN PIN 23, ENC_A PIN 27, ENC_B PIN 22", flush=True)

    def button_callback(level, tick):
        # level: 0 falling, 1 rising, 2 watchdog timeout
        if level == 2:
            print(f"[WD]  {ts()} watchdog timeout", flush=True)
            return
        print(f"[BTN] {ts()} level={level} tick={tick}", flush=True)

    def rotation_callback(direction, position, degrees, rotations):
        print(f"[ENC] {ts()} {direction} rotations={rotations} remainder={degrees:.1f}° (raw={position})", flush=True)
    
    encoder.set_button_callback(button_callback)
    encoder.set_rotation_callback(rotation_callback)
    
    print("[RUN] Callbacks armed (Ctrl+C to exit)", flush=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[EXIT] KeyboardInterrupt", flush=True)
    finally:
        encoder.cleanup()
        print("[CLEANUP] encoder cleaned up", flush=True)

if __name__ == "__main__":
    main()
