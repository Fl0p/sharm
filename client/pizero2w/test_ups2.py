import sys
import time
import struct

import smbus
import RPi.GPIO as GPIO

CW2015_ADDR      = 0x62
REG_VCELL        = 0x02
REG_SOC          = 0x04
REG_MODE         = 0x0A

POWER_GPIO       = 4   # High when external power is present
I2C_BUS_NUM      = 1   # /dev/i2c-1 on modern Raspberry Pi

READ_INTERVAL_S  = 2.0

def read_word_swapped(bus, addr, reg):
    """Read a 16-bit word and swap bytes (SMBus is little-endian on wire)."""
    raw = bus.read_word_data(addr, reg)
    # Convert 0xAABB -> 0xBBAA (SMBus returns LSB first)
    return struct.unpack("<H", struct.pack(">H", raw))[0]

def read_voltage_v(bus):
    """Return battery voltage in volts."""
    w = read_word_swapped(bus, CW2015_ADDR, REG_VCELL)
    # LSB = 0.305 mV on this board/driver path; no >> 2 needed here
    return (w * 0.305) / 1000.0

def read_soc_percent(bus):
    """Return state of charge in percent as float."""
    w = read_word_swapped(bus, CW2015_ADDR, REG_SOC)
    return w / 256.0

def quick_start(bus):
    """
    Wake CW2015 and force a quick-start estimation.
    Some boards expect write_word_data(REG_MODE, 0x30).
    """
    try:
        bus.write_word_data(CW2015_ADDR, REG_MODE, 0x30)
    except Exception as e:
        print(f"QuickStart warning: {e}", file=sys.stderr)

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(POWER_GPIO, GPIO.IN)

def is_power_present():
    return GPIO.input(POWER_GPIO) == GPIO.HIGH

def main():
    setup_gpio()

    try:
        bus = smbus.SMBus(I2C_BUS_NUM)
    except FileNotFoundError:
        print("I2C bus /dev/i2c-1 not found. Enable I2C in raspi-config.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print("Permission denied. Run with sudo or add your user to the 'i2c' group.", file=sys.stderr)
        sys.exit(1)

    print("\nInitializing CW2015 ...")
    quick_start(bus)

    try:
        while True:
            voltage_v = read_voltage_v(bus)
            soc = read_soc_percent(bus)

            print("++++++++++++++++++++")
            print(f"Voltage: {voltage_v:5.2f} V")
            print(f"Battery: {soc:5.2f}%")

            if soc >= 100.0:
                print("Battery FULL")
            elif soc < 5.0:
                print("Battery LOW")

            print("Power Adapter Plug In" if is_power_present() else "Power Adapter Unplug")
            print("++++++++++++++++++++")

            time.sleep(READ_INTERVAL_S)

    except KeyboardInterrupt:
        print("\nExiting on user request.")
    finally:
        try:
            bus.close()
        except Exception:
            pass
        GPIO.cleanup()

if __name__ == "__main__":
    main()