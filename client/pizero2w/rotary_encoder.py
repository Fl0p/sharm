#!/usr/bin/env python3
import pigpio
import time
import sys


class RotaryEncoder:
    """Rotary encoder with button using pigpio"""
    
    def __init__(self, pin_btn=23, pin_enc_a=27, pin_enc_b=22, 
                 watchdog_ms=1000, glitch_us=100, pulses_per_rotation=80, debug=False):
        """
        Initialize rotary encoder
        
        Args:
            pin_btn: GPIO pin for button
            pin_enc_a: GPIO pin for encoder A
            pin_enc_b: GPIO pin for encoder B
            watchdog_ms: Watchdog timeout in milliseconds
            glitch_us: Glitch filter in microseconds
            pulses_per_rotation: Number of pulses per full rotation
            debug: Enable debug logging
        """
        self.pin_btn = pin_btn
        self.pin_enc_a = pin_enc_a
        self.pin_enc_b = pin_enc_b
        self.watchdog_ms = watchdog_ms
        self.glitch_us = glitch_us
        self.pulses_per_rotation = pulses_per_rotation
        self.debug = debug
        
        # Callbacks
        self.button_callback = None
        self.rotation_callback = None
        
        # Position tracking
        self.encoder_pos = 0
        
        # State buffer for debouncing
        self.state_buffer = []
        
        # Initialize pigpio
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpiod is not running! Start it with: sudo pigpiod")
        
        # Button setup
        self.pi.set_mode(self.pin_btn, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pin_btn, pigpio.PUD_UP)
        self.pi.set_glitch_filter(self.pin_btn, self.glitch_us)
        self.pi.set_watchdog(self.pin_btn, self.watchdog_ms)
        
        # Encoder setup
        self.pi.set_mode(self.pin_enc_a, pigpio.INPUT)
        self.pi.set_mode(self.pin_enc_b, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pin_enc_a, pigpio.PUD_UP)
        self.pi.set_pull_up_down(self.pin_enc_b, pigpio.PUD_UP)
        self.pi.set_glitch_filter(self.pin_enc_a, self.glitch_us)
        self.pi.set_glitch_filter(self.pin_enc_b, self.glitch_us)
        
        enc_a_initial = self.pi.read(self.pin_enc_a)
        enc_b_initial = self.pi.read(self.pin_enc_b)
        self.last_encoded = (enc_a_initial << 1) | enc_b_initial
        
        # Set up callbacks
        self.cb_btn = self.pi.callback(self.pin_btn, pigpio.EITHER_EDGE, self._btn_handler)
        self.cb_enc_a = self.pi.callback(self.pin_enc_a, pigpio.EITHER_EDGE, self._enc_handler)
        self.cb_enc_b = self.pi.callback(self.pin_enc_b, pigpio.EITHER_EDGE, self._enc_handler)
    
    def set_button_callback(self, callback):
        """
        Set callback for button events
        
        Args:
            callback: Function(level, tick) - level: 0=pressed, 1=released, 2=timeout
        """
        self.button_callback = callback
    
    def set_rotation_callback(self, callback):
        """
        Set callback for rotation events
        
        Args:
            callback: Function(direction, position, degrees, rotations) 
                      direction: 'CW' or 'CCW'
        """
        self.rotation_callback = callback
    
    def _btn_handler(self, gpio, level, tick):
        """Internal button event handler"""
        if self.button_callback:
            self.button_callback(level, tick)
    
    def _enc_handler(self, gpio, level, tick):
        """Internal encoder event handler"""
        a = self.pi.read(self.pin_enc_a)
        b = self.pi.read(self.pin_enc_b)
        encoded = (a << 1) | b
        
        if self.debug:
            print(f"[ENC_DBG] Handler called: gpio={gpio} A={a} B={b} encoded={encoded:02b}", flush=True)
        
        # Add state to buffer
        self.state_buffer.append(encoded)
        
        if self.debug:
            print(f"[ENC_DBG] Buffer: {[f'{s:02b}' for s in self.state_buffer]}", flush=True)
        
        # Process buffer only when both A=1 and B=1 (stable state)
        if encoded == 0b11:
            if self.debug:
                print(f"[ENC_DBG] A=1 B=1 detected, processing buffer...", flush=True)
            
            # Remove duplicates while preserving order
            unique_states = []
            for state in self.state_buffer:
                if not unique_states or unique_states[-1] != state:
                    unique_states.append(state)
            
            if self.debug:
                print(f"[ENC_DBG] Unique states: {[f'{s:02b}' for s in unique_states]}", flush=True)
            
            # Need at least 2 states to determine direction
            if len(unique_states) >= 2:
                # Use the second-to-last unique state as previous state
                prev_state = unique_states[-2]
                
                # Check sequence for CW: 11 -> 01 -> 00 -> 10 -> 11
                # or CCW: 11 -> 10 -> 00 -> 01 -> 11
                sum_val = (prev_state << 2) | encoded
                
                if self.debug:
                    print(f"[ENC_DBG] prev_state={prev_state:02b} current={encoded:02b} sum_val={sum_val:04b}", flush=True)
                
                if sum_val in (0b0001, 0b0111, 0b1110, 0b1000):
                    self.encoder_pos -= 1
                    direction = 'CCW'
                    if self.debug:
                        print(f"[ENC_DBG] CCW detected, pos={self.encoder_pos}", flush=True)
                elif sum_val in (0b0010, 0b1011, 0b1101, 0b0100):
                    self.encoder_pos += 1
                    direction = 'CW'
                    if self.debug:
                        print(f"[ENC_DBG] CW detected, pos={self.encoder_pos}", flush=True)
                else:
                    if self.debug:
                        print(f"[ENC_DBG] No valid direction, clearing buffer", flush=True)
                    # Clear buffer and update last state
                    self.state_buffer = []
                    self.last_encoded = encoded
                    return
                
                degrees = self.encoder_pos * (360.0 / self.pulses_per_rotation)
                rotations = int(degrees // 360)
                remainder = degrees % 360
                
                if self.rotation_callback:
                    self.rotation_callback(direction, self.encoder_pos, remainder, rotations)
            else:
                if self.debug:
                    print(f"[ENC_DBG] Not enough unique states ({len(unique_states)}), skipping", flush=True)
            
            # Clear buffer and update last state
            self.state_buffer = []
            self.last_encoded = encoded
        
        # Limit buffer size to prevent memory issues
        if len(self.state_buffer) > 10:
            self.state_buffer = self.state_buffer[-10:]
    
    def get_position(self):
        """Get current encoder position"""
        return self.encoder_pos
    
    def reset_position(self):
        """Reset encoder position to 0"""
        self.encoder_pos = 0
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'cb_btn'):
            self.cb_btn.cancel()
        if hasattr(self, 'cb_enc_a'):
            self.cb_enc_a.cancel()
        if hasattr(self, 'cb_enc_b'):
            self.cb_enc_b.cancel()
        if hasattr(self, 'pi'):
            self.pi.set_watchdog(self.pin_btn, 0)
            self.pi.stop()

