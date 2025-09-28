#!/usr/bin/env python3
import pigpio
import time
import sys

# GPIO pins (BCM numbering)
PIN_A = 22
PIN_B = 23
PIN_BTN = 24

# Debounce/glitch filters in microseconds
GLITCH_AB_US = 2000   # 2 ms for encoder channels
GLITCH_BTN_US = 5000  # 5 ms for push button

class RotaryEncoder:
    """
    Full-step quadrature decoder using pigpio callbacks.
    Counts every valid state transition (x4 resolution).
    """
    # Valid transitions encoded as previous_state << 2 | current_state
    # State is 2-bit: (A<<1 | B)
    _TRANSITION_TABLE = {
        0b0001: +1, 0b0010: -1, 0b0100: -1, 0b0111: +1,
        0b1000: +1, 0b1011: -1, 0b1101: -1, 0b1110: +1
    }

    def __init__(self, pi: pigpio.pi, pin_a: int, pin_b: int):
        self.pi = pi
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.position = 0

        # Ensure inputs + pull-ups
        for p in (self.pin_a, self.pin_b):
            self.pi.set_mode(p, pigpio.INPUT)
            self.pi.set_pull_up_down(p, pigpio.PUD_UP)
            self.pi.set_glitch_filter(p, GLITCH_AB_US)

        # Read initial 2-bit state
        a = self.pi.read(self.pin_a)
        b = self.pi.read(self.pin_b)
        self._state = (a << 1) | b

        # Keep references to callbacks!
        self.cb_a = self.pi.callback(self.pin_a, pigpio.EITHER_EDGE, self._edge)
        self.cb_b = self.pi.callback(self.pin_b, pigpio.EITHER_EDGE, self._edge)

    def _edge(self, gpio: int, level: int, tick: int):
        # Read both channels atomically-ish
        a = self.pi.read(self.pin_a)
        b = self.pi.read(self.pin_b)
        new_state = (a << 1) | b

        key = (self._state << 2) | new_state
        delta = self._TRANSITION_TABLE.get(key, 0)
        if delta:
            self.position += delta
            print(f"[ENC] pos={self.position} (delta={delta}, A={a}, B={b})")
        self._state = new_state

    def cancel(self):
        self.cb_a.cancel()
        self.cb_b.cancel()

class PushButton:
    """Simple falling-edge button with optional glitch filter."""
    def __init__(self, pi: pigpio.pi, pin: int, on_press):
        self.pi = pi
        self.pin = pin
        self.on_press = on_press

        self.pi.set_mode(self.pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pin, pigpio.PUD_UP)
        self.pi.set_glitch_filter(self.pin, GLITCH_BTN_US)

        self.cb = self.pi.callback(self.pin, pigpio.FALLING_EDGE, self._pressed)

    def _pressed(self, gpio: int, level: int, tick: int):
        # level==0 on falling edge due to pull-up
        try:
            self.on_press()
        except Exception as e:
            print(f"[BTN] handler error: {e}", file=sys.stderr)

    def cancel(self):
        self.cb.cancel()

def main():
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("pigpiod is not running! Start it with: sudo pigpiod")

    enc = RotaryEncoder(pi, PIN_A, PIN_B)

    def handle_press():
        print("[BTN] pressed")

    btn = PushButton(pi, PIN_BTN, handle_press)

    print("Rotate the encoder on GPIO22/23 and press the button on GPIO24 (Ctrl+C to exit)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        btn.cancel()
        enc.cancel()
        pi.stop()

if __name__ == "__main__":
    main()
