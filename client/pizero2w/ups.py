#!/usr/bin/env python3
"""
UPS HAT Battery Monitor - Reusable class for Raspberry Pi
Provides event-driven interface for CW2015 fuel gauge and power monitoring.
"""
import sys
import struct
import threading
import time
from enum import Enum
from typing import Callable, Optional

import smbus
import RPi.GPIO as GPIO


class BatteryStatus(Enum):
    """Battery charge status."""
    FULL = "FULL"
    OK = "OK"
    LOW = "LOW"


class UPS:
    """
    UPS HAT monitor with event subscription support.
    
    Events:
    - on_battery_change: Called when battery voltage/SOC changes
    - on_power_change: Called when power adapter connection changes
    - on_low_battery: Called when battery drops below threshold
    """
    
    # CW2015 I2C configuration
    CW2015_ADDR = 0x62
    REG_VCELL = 0x02
    REG_SOC = 0x04
    REG_MODE = 0x0A
    
    # GPIO and I2C settings
    POWER_GPIO = 4
    I2C_BUS_NUM = 1
    
    # Battery thresholds
    LOW_BATTERY_THRESHOLD = 5.0   # %
    FULL_BATTERY_THRESHOLD = 100.0  # %
    
    def __init__(self, auto_update: bool = False, update_interval: float = 1.0):
        """
        Initialize UPS monitor.
        
        Args:
            auto_update: If True, automatically call update() in background thread
            update_interval: Interval in seconds for auto updates (default: 1.0)
        """
        self._bus: Optional[smbus.SMBus] = None
        self._initialized = False
        
        # Auto update configuration
        self._auto_update = auto_update
        self._update_interval = update_interval
        self._update_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Event callbacks
        self._on_battery_change: Optional[Callable] = None
        self._on_power_change: Optional[Callable] = None
        self._on_low_battery: Optional[Callable] = None
        
        # State tracking for events
        self._last_power_state: Optional[bool] = None
        self._last_soc: Optional[float] = None
        self._last_voltage: Optional[float] = None
        self._low_battery_notified = False
    
    def initialize(self):
        """Initialize I2C bus and GPIO."""
        if self._initialized:
            return
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.POWER_GPIO, GPIO.IN)
        
        # Initialize I2C
        try:
            self._bus = smbus.SMBus(self.I2C_BUS_NUM)
        except FileNotFoundError:
            raise RuntimeError("I2C bus /dev/i2c-1 not found. Enable I2C in raspi-config.")
        except PermissionError:
            raise PermissionError("Permission denied. Run with sudo or add user to 'i2c' group.")
        
        # Quick start fuel gauge
        self._quick_start()
        self._initialized = True
        
        # Start auto-update thread if enabled
        if self._auto_update:
            self._start_auto_update()
    
    def cleanup(self):
        """Release resources."""
        # Stop auto-update thread
        if self._update_thread and self._update_thread.is_alive():
            self._stop_event.set()
            self._update_thread.join(timeout=2.0)
        
        if self._bus:
            try:
                self._bus.close()
            except Exception:
                pass
            self._bus = None
        
        try:
            GPIO.cleanup()
        except Exception:
            pass
        
        self._initialized = False
    
    # Event subscription methods
    def on_battery_change(self, callback: Callable[[float, float, BatteryStatus], None]):
        """Subscribe to battery state changes. Callback: (voltage, soc, status)"""
        self._on_battery_change = callback
    
    def on_power_change(self, callback: Callable[[bool], None]):
        """Subscribe to power adapter connection changes. Callback: (is_connected)"""
        self._on_power_change = callback
    
    def on_low_battery(self, callback: Callable[[float, float], None]):
        """Subscribe to low battery alerts. Callback: (voltage, soc)"""
        self._on_low_battery = callback
    
    # Reading methods
    def read_voltage(self) -> float:
        """Return battery voltage in volts."""
        if not self._initialized:
            raise RuntimeError("UPS not initialized. Call initialize() first.")
        
        w = self._read_word_swapped(self.REG_VCELL)
        return (w * 0.305) / 1000.0
    
    def read_soc(self) -> float:
        """Return state of charge in percent."""
        if not self._initialized:
            raise RuntimeError("UPS not initialized. Call initialize() first.")
        
        w = self._read_word_swapped(self.REG_SOC)
        return w / 256.0
    
    def is_power_connected(self) -> bool:
        """Check if external power adapter is connected."""
        if not self._initialized:
            raise RuntimeError("UPS not initialized. Call initialize() first.")
        
        return GPIO.input(self.POWER_GPIO) == GPIO.HIGH
    
    def get_battery_status(self, soc: float) -> BatteryStatus:
        """Get battery status based on SOC."""
        if soc >= self.FULL_BATTERY_THRESHOLD:
            return BatteryStatus.FULL
        elif soc < self.LOW_BATTERY_THRESHOLD:
            return BatteryStatus.LOW
        else:
            return BatteryStatus.OK
    
    def update(self):
        """
        Read current state and trigger events if changes detected.
        Call this periodically in your main loop.
        """
        if not self._initialized:
            raise RuntimeError("UPS not initialized. Call initialize() first.")
        
        voltage = self.read_voltage()
        soc = self.read_soc()
        power_connected = self.is_power_connected()
        status = self.get_battery_status(soc)
        
        # Check for battery changes
        if (self._last_voltage != voltage or self._last_soc != soc):
            if self._on_battery_change:
                self._on_battery_change(voltage, soc, status)
            self._last_voltage = voltage
            self._last_soc = soc
        
        # Check for power adapter changes
        if self._last_power_state != power_connected:
            if self._on_power_change:
                self._on_power_change(power_connected)
            self._last_power_state = power_connected
        
        # Check for low battery
        if status == BatteryStatus.LOW and not self._low_battery_notified:
            if self._on_low_battery:
                self._on_low_battery(voltage, soc)
            self._low_battery_notified = True
        elif status != BatteryStatus.LOW:
            self._low_battery_notified = False
    
    # Private methods
    def _read_word_swapped(self, reg: int) -> int:
        """Read a 16-bit word and swap bytes."""
        raw = self._bus.read_word_data(self.CW2015_ADDR, reg)
        return struct.unpack("<H", struct.pack(">H", raw))[0]
    
    def _quick_start(self):
        """Wake CW2015 and force quick-start fuel gauge estimation."""
        try:
            self._bus.write_word_data(self.CW2015_ADDR, self.REG_MODE, 0x30)
        except Exception as e:
            print(f"QuickStart warning: {e}", file=sys.stderr)
    
    def _start_auto_update(self):
        """Start background thread for automatic updates."""
        if self._update_thread and self._update_thread.is_alive():
            return
        
        self._stop_event.clear()
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
    
    def _update_loop(self):
        """Background thread loop for automatic updates."""
        while not self._stop_event.is_set():
            try:
                self.update()
            except Exception as e:
                print(f"Auto-update error: {e}", file=sys.stderr)
            
            self._stop_event.wait(self._update_interval)
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        return False
