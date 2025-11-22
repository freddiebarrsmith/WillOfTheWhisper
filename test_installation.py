#!/usr/bin/env python3
"""
Test script for WhisperControl installation
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import whisper
        print("✓ OpenAI Whisper imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Whisper: {e}")
        return False
    
    try:
        import sounddevice
        print("✓ SoundDevice imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SoundDevice: {e}")
        return False
    
    try:
        import soundfile
        print("✓ SoundFile imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SoundFile: {e}")
        return False
    
    try:
        import pynput
        print("✓ PyInput imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PyInput: {e}")
        return False
    
    try:
        import pyperclip
        print("✓ PyPerClip imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PyPerClip: {e}")
        return False
    
    try:
        import yaml
        print("✓ PyYAML imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PyYAML: {e}")
        return False
    
    try:
        import webrtcvad
        print("✓ WebRTC VAD imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import WebRTC VAD: {e}")
        return False
    
    return True

def test_whisper_model():
    """Test if Whisper model can be loaded"""
    print("\nTesting Whisper model loading...")
    
    try:
        import whisper
        model = whisper.load_model("tiny")  # Use tiny model for testing
        print("✓ Whisper tiny model loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to load Whisper model: {e}")
        return False

def test_audio_devices():
    """Test if audio devices are available"""
    print("\nTesting audio devices...")
    
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        print(f"✓ Found {len(devices)} audio devices")
        
        # Check for default input device
        default_input = sd.default.device[0]
        if default_input is not None:
            print(f"✓ Default input device: {devices[default_input]['name']}")
        else:
            print("⚠ No default input device found")
        
        return True
    except Exception as e:
        print(f"✗ Failed to query audio devices: {e}")
        return False

def test_permissions():
    """Test if required permissions are available"""
    print("\nTesting permissions...")
    
    # Test microphone access
    try:
        import sounddevice as sd
        with sd.InputStream(samplerate=16000, channels=1, blocksize=1024):
            print("✓ Microphone access available")
    except Exception as e:
        print(f"✗ Microphone access failed: {e}")
        print("  Make sure to grant microphone permissions in System Preferences")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from config import Config
        
        config = Config()
        print("✓ Configuration loaded successfully")
        print(f"  Activation mode: {config.activation_mode}")
        print(f"  Whisper model: {config.whisper_model}")
        print(f"  Hotkey: {config.hotkey_combination}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False

def main():
    """Run all tests"""
    print("WhisperControl Installation Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_whisper_model,
        test_audio_devices,
        test_permissions,
        test_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! WhisperControl is ready to use.")
        print("\nTo start WhisperControl:")
        print("  python src/main.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Grant microphone permissions in System Preferences")
        print("3. Check if all dependencies are installed correctly")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
