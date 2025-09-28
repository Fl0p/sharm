#!/usr/bin/env python3
import pigpio
import time
import sys
import os

PIN_BTN = 24
SLEEP_SEC = 0.1

def ts():
    t = time.time()
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)) + f".{int((t % 1)*1000):03d}"

def main():
    print(f"[INIT] Python={sys.version.split()[0]} argv={sys.argv} cwd={os.getcwd()}", flush=True)
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("pigpiod is not running! Start it with: sudo pigpiod")

    rev = pi.get_hardware_revision()
    print(f"[INIT] pigpio connected, hw_rev=0x{rev:X}", flush=True)

    pi.set_mode(PIN_BTN, pigpio.INPUT)
    pi.set_pull_up_down(PIN_BTN, pigpio.PUD_UP)

    initial = pi.read(PIN_BTN)
    print(f"[CFG] Set PIN {PIN_BTN} as INPUT with PUD_UP", flush=True)
    print(f"[STATE] {ts()} initial_level={initial}", flush=True)

    last = initial
    counter = 0
    print("[RUN] Polling started (Ctrl+C to exit)", flush=True)
    try:
        while True:
            val = pi.read(PIN_BTN)
            if val != last:
                print(f"[EDGE] {ts()} level={val}", flush=True)
                last = val

            counter += 1
            if counter % int(1 / SLEEP_SEC) == 0:
                # Heartbeat once per ~1s
                print(f"[HB]  {ts()} level={val}", flush=True)
            time.sleep(SLEEP_SEC)
    except KeyboardInterrupt:
        print("\n[EXIT] KeyboardInterrupt", flush=True)
    finally:
        pi.stop()
        print("[CLEANUP] pigpio stopped", flush=True)

if __name__ == "__main__":
    main()
