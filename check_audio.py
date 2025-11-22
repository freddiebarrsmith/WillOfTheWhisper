#!/usr/bin/env python3
"""
Audio Device Checker - Check what microphones are available
"""

import sounddevice as sd
import sys


def main():
    """Check available audio devices"""
    print("\n" + "="*60)
    print("🎤 Audio Device Checker")
    print("="*60)
    
    try:
        # List all audio devices
        devices = sd.query_devices()
        print("Available audio devices:")
        print("-" * 40)
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:  # Has input capability
                print(f"Device {i}: {device['name']}")
                print(f"  - Input channels: {device['max_input_channels']}")
                print(f"  - Sample rate: {device['default_samplerate']}")
                print()
        
        # Check default device
        default_device = sd.default.device
        print(f"Default input device: {default_device[0]}")
        print(f"Default output device: {default_device[1]}")
        
        # Test recording capability
        print("\nTesting recording capability...")
        try:
            # Try to record 1 second
            test_recording = sd.rec(int(1 * 16000), samplerate=16000, channels=1, dtype='float64')
            sd.wait()
            print("✅ Recording test successful!")
        except Exception as e:
            print(f"❌ Recording test failed: {e}")
            print("\nThis usually means:")
            print("1. No microphone permissions granted")
            print("2. No microphone connected")
            print("3. Microphone is being used by another app")
            
            print("\nTo fix:")
            print("1. Go to System Preferences > Security & Privacy > Privacy > Microphone")
            print("2. Add Terminal or your Python app to the list")
            print("3. Make sure it's checked/enabled")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
