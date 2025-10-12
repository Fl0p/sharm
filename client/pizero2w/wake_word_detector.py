#!/usr/bin/env python3
import pvporcupine
import pyaudio
import struct
import os


class WakeWordDetector:
    """Wake word detection using Picovoice Porcupine"""
    
    def __init__(self, keywords, keyword_paths=None, access_key=None):
        """
        Initialize wake word detector
        
        Args:
            keywords: List of keyword names
            keyword_paths: List of paths to .ppn files (optional, will auto-generate from keywords)
            access_key: Picovoice access key (optional, will use PV_ACCESS_KEY env var)
        """
        self.keywords = keywords
        
        if access_key is None:
            access_key = os.getenv("PV_ACCESS_KEY", "YOUR_PICOVOICE_ACCESS_KEY")
        
        if keyword_paths is None:
            keyword_paths = [
                os.path.join(os.path.dirname(__file__), f"{kw}.ppn") 
                for kw in keywords
            ]
        
        self.keyword_paths = keyword_paths
        self.porcupine = pvporcupine.create(
            access_key=access_key, 
            keyword_paths=keyword_paths
        )
        
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )
        
        self.callback = None
    
    def set_callback(self, callback):
        """
        Set callback function to be called when wake word is detected
        
        Args:
            callback: Function(keyword_index, keyword_name) to call on detection
        """
        self.callback = callback
    
    def process_audio(self):
        """
        Process one frame of audio and check for wake word
        
        Returns:
            keyword_index if detected, -1 otherwise
        """
        pcm = self.stream.read(
            self.porcupine.frame_length, 
            exception_on_overflow=False
        )
        pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
        idx = self.porcupine.process(pcm)
        
        if idx >= 0 and self.callback:
            self.callback(idx, self.keywords[idx])
        
        return idx
    
    def cleanup(self):
        """Clean up resources"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.pa:
            self.pa.terminate()
        if self.porcupine:
            self.porcupine.delete()

