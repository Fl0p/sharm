#!/usr/bin/env python3
"""
UPS HAT Battery Monitor for Raspberry Pi
Monitors CW2015 fuel gauge via I2C and power adapter status via GPIO.
"""
import sys
import time
import struct

import smbus
import RPi.GPIO as GPIO

# CW2015 I2C configuration
CW2015_ADDR      = 0x62
REG_VCELL        = 0x02
REG_SOC          = 0x04
REG_MODE         = 0x0A

# GPIO and I2C settings
POWER_GPIO       = 4   # High when external power is present
I2C_BUS_NUM      = 1   # /dev/i2c-1 on modern Raspberry Pi

# Monitoring interval
READ_INTERVAL_S  = 2.0

def read_word_swapped(bus, addr, reg):
    """Read a 16-bit word and swap bytes (SMBus is little-endian on wire)."""
    raw = bus.read_word_data(addr, reg)
    return struct.unpack("<H", struct.pack(">H", raw))[0]

def read_voltage_v(bus):
    """Return battery voltage in volts."""
    w = read_word_swapped(bus, CW2015_ADDR, REG_VCELL)
    # LSB = 0.305 mV
    return (w * 0.305) / 1000.0

def read_soc_percent(bus):
    """Return state of charge in percent as float."""
    w = read_word_swapped(bus, CW2015_ADDR, REG_SOC)
    return w / 256.0

def quick_start(bus):
    """
    Wake CW2015 and force a quick-start fuel gauge estimation.
    Writes 0x30 to MODE register to trigger quick-start.
    """
    try:
        bus.write_word_data(CW2015_ADDR, REG_MODE, 0x30)
    except Exception as e:
        print(f"QuickStart warning: {e}", file=sys.stderr)

def setup_gpio():
    """Initialize GPIO for power detection."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(POWER_GPIO, GPIO.IN)

def is_power_present():
    """Check if external power adapter is connected."""
    return GPIO.input(POWER_GPIO) == GPIO.HIGH

def main():
    """Main monitoring loop."""
    setup_gpio()

    # Initialize I2C bus
    try:
        bus = smbus.SMBus(I2C_BUS_NUM)
    except FileNotFoundError:
        print("ERROR: I2C bus /dev/i2c-1 not found.", file=sys.stderr)
        print("Enable I2C in raspi-config.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print("ERROR: Permission denied.", file=sys.stderr)
        print("Run with sudo or add your user to the 'i2c' group.", file=sys.stderr)
        sys.exit(1)

    print("\nInitializing CW2015 fuel gauge...")
    quick_start(bus)
    print("Ready. Press Ctrl+C to exit.\n")

    try:
        while True:
            voltage_v = read_voltage_v(bus)
            soc = read_soc_percent(bus)

            print("=" * 20)
            print(f"Voltage: {voltage_v:5.2f} V")
            print(f"Battery: {soc:5.1f}%")

            # Battery status
            if soc >= 100.0:
                print("Status:  FULL")
            elif soc < 5.0:
                print("Status:  LOW - CHARGE SOON!")
            else:
                print("Status:  OK")

            # Power adapter status
            if is_power_present():
                print("Power:   Adapter Connected")
            else:
                print("Power:   On Battery")

            print("=" * 20)
            print()

            time.sleep(READ_INTERVAL_S)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Cleanup
        try:
            bus.close()
        except Exception:
            pass
        GPIO.cleanup()
        print("Cleanup complete.")

if __name__ == "__main__":
    main()
