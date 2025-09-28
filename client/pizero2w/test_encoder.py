#!/usr/bin/env python3
import pigpio
import time
import sys
import os

PIN_BTN = 24
WATCHDOG_MS = 1000   # emits level=2 if no edge for this period
GLITCH_US   = 0      # start with 0; raise to 2000–5000 later if you see bounce

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
    pi.set_glitch_filter(PIN_BTN, GLITCH_US)
    pi.set_watchdog(PIN_BTN, WATCHDOG_MS)

    initial = pi.read(PIN_BTN)
    print(f"[CFG] PIN {PIN_BTN}: INPUT, PUD_UP, glitch={GLITCH_US}us, watchdog={WATCHDOG_MS}ms", flush=True)
    print(f"[STATE] {ts()} initial_level={initial}", flush=True)

    def _cb(gpio, level, tick):
        # level: 0 falling, 1 rising, 2 watchdog timeout
        if level == 2:
            print(f"[WD]  {ts()} gpio={gpio} watchdog timeout", flush=True)
            return
        print(f"[CB]  {ts()} gpio={gpio} level={level} tick={tick}", flush=True)

    # keep reference to avoid GC
    cb = pi.callback(PIN_BTN, pigpio.EITHER_EDGE, _cb)
    print("[RUN] Callback armed on EITHER_EDGE (Ctrl+C to exit)", flush=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[EXIT] KeyboardInterrupt", flush=True)
    finally:
        cb.cancel()
        pi.set_watchdog(PIN_BTN, 0)
        pi.stop()
        print("[CLEANUP] callback canceled, pigpio stopped", flush=True)

if __name__ == "__main__":
    main()
