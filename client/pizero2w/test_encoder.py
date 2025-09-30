#!/usr/bin/env python3
import pigpio
import time
import sys
import os

PIN_BTN = 23
PIN_ENC_A = 27
PIN_ENC_B = 22
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

    # Button setup
    pi.set_mode(PIN_BTN, pigpio.INPUT)
    pi.set_pull_up_down(PIN_BTN, pigpio.PUD_UP)
    pi.set_glitch_filter(PIN_BTN, GLITCH_US)
    pi.set_watchdog(PIN_BTN, WATCHDOG_MS)

    initial = pi.read(PIN_BTN)
    print(f"[CFG] BTN PIN {PIN_BTN}: INPUT, PUD_UP, glitch={GLITCH_US}us, watchdog={WATCHDOG_MS}ms", flush=True)
    print(f"[STATE] {ts()} initial_level={initial}", flush=True)

    # Encoder setup
    pi.set_mode(PIN_ENC_A, pigpio.INPUT)
    pi.set_mode(PIN_ENC_B, pigpio.INPUT)
    pi.set_pull_up_down(PIN_ENC_A, pigpio.PUD_UP)
    pi.set_pull_up_down(PIN_ENC_B, pigpio.PUD_UP)
    
    enc_a_initial = pi.read(PIN_ENC_A)
    enc_b_initial = pi.read(PIN_ENC_B)
    print(f"[CFG] ENC PIN {PIN_ENC_A} (A): INPUT, PUD_UP, initial={enc_a_initial}", flush=True)
    print(f"[CFG] ENC PIN {PIN_ENC_B} (B): INPUT, PUD_UP, initial={enc_b_initial}", flush=True)
    
    # Encoder position tracking
    encoder_pos = 0
    last_encoded = (enc_a_initial << 1) | enc_b_initial

    def _btn_cb(gpio, level, tick):
        # level: 0 falling, 1 rising, 2 watchdog timeout
        if level == 2:
            print(f"[WD]  {ts()} gpio={gpio} watchdog timeout", flush=True)
            return
        print(f"[BTN] {ts()} gpio={gpio} level={level} tick={tick}", flush=True)

    def _enc_cb(gpio, level, tick):
        nonlocal encoder_pos, last_encoded
        
        # Read both encoder pins
        a = pi.read(PIN_ENC_A)
        b = pi.read(PIN_ENC_B)
        encoded = (a << 1) | b
        
        # Determine direction based on state transition
        sum_val = (last_encoded << 2) | encoded
        
        if sum_val in (0b0001, 0b0111, 0b1110, 0b1000):
            encoder_pos -= 1
        elif sum_val in (0b0010, 0b1011, 0b1101, 0b0100):
            encoder_pos += 1
        
        # Convert to degrees (80 pulses per rotation -> 360 degrees)
        degrees = encoder_pos * 4.5
        rotations = int(degrees // 360)
        remainder = degrees % 360
        
        direction = "CW " if sum_val in (0b0010, 0b1011, 0b1101, 0b0100) else "CCW"
        print(f"[ENC] {ts()} {direction} rotations={rotations} remainder={remainder:.1f}° (raw={encoder_pos}) A={a} B={b}", flush=True)
        
        last_encoded = encoded

    # keep reference to avoid GC
    cb_btn = pi.callback(PIN_BTN, pigpio.EITHER_EDGE, _btn_cb)
    cb_enc_a = pi.callback(PIN_ENC_A, pigpio.EITHER_EDGE, _enc_cb)
    cb_enc_b = pi.callback(PIN_ENC_B, pigpio.EITHER_EDGE, _enc_cb)
    print("[RUN] Callbacks armed (Ctrl+C to exit)", flush=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[EXIT] KeyboardInterrupt", flush=True)
    finally:
        cb_btn.cancel()
        cb_enc_a.cancel()
        cb_enc_b.cancel()
        pi.set_watchdog(PIN_BTN, 0)
        pi.stop()
        print("[CLEANUP] callbacks canceled, pigpio stopped", flush=True)

if __name__ == "__main__":
    main()
