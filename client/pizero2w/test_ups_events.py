#!/usr/bin/env python3
"""
UPS HAT Battery Monitor - Event-driven example
Demonstrates event subscription usage.
"""
import time
from ups import UPS, BatteryStatus


def on_battery_changed(voltage: float, soc: float, status: BatteryStatus):
    """Called when battery state changes."""
    print(f"📊 Battery changed: {soc:.1f}% ({voltage:.2f}V) - {status.value}")


def on_power_changed(is_connected: bool):
    """Called when power adapter connection changes."""
    if is_connected:
        print("🔌 Power adapter CONNECTED")
    else:
        print("🔋 Running on BATTERY")


def on_low_battery(voltage: float, soc: float):
    """Called when battery is low."""
    print(f"⚠️  LOW BATTERY ALERT: {soc:.1f}% ({voltage:.2f}V) - CHARGE SOON!")


def main():
    """Event-driven monitoring example."""
    print("\nUPS HAT Event Monitor")
    print("Press Ctrl+C to exit.\n")
    
    try:
        with UPS() as ups:
            # Subscribe to events
            ups.on_battery_change(on_battery_changed)
            ups.on_power_change(on_power_changed)
            ups.on_low_battery(on_low_battery)
            
            print("Subscribed to events. Monitoring...\n")
            
            # Event loop
            while True:
                ups.update()  # Check state and trigger events
                time.sleep(1.0)
    
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"ERROR: {e}")
        return 1
    
    print("Done.")
    return 0


if __name__ == "__main__":
    exit(main())
