#!/usr/bin/env python3
"""
UPS HAT Battery Monitor Test
Simple monitoring loop using the UPS class.
"""
import time
from ups import UPS


def main():
    """Main monitoring loop."""
    print("\nUPS HAT Battery Monitor")
    print("Press Ctrl+C to exit.\n")
    
    try:
        with UPS() as ups:
            print("Initialized successfully.\n")
            
            while True:
                # Read current state
                voltage = ups.read_voltage()
                soc = ups.read_soc()
                power_connected = ups.is_power_connected()
                status = ups.get_battery_status(soc)
                
                # Display
                print("=" * 40)
                print(f"Voltage: {voltage:5.2f} V")
                print(f"Battery: {soc:5.1f}%")
                print(f"Status:  {status.value}")
                
                if power_connected:
                    print("Power:   Adapter Connected")
                else:
                    print("Power:   On Battery")
                
                print("=" * 40)
                print()
                
                # Trigger events (optional, for event-driven usage)
                ups.update()
                
                time.sleep(2.0)
    
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"ERROR: {e}")
        return 1
    
    print("Done.")
    return 0


if __name__ == "__main__":
    exit(main())