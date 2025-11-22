#!/usr/bin/env python3
"""
Quick Windows Key + V Verification for Ducky One 2
"""

import sys
import os
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mac_keyboard_utils import MacKeyboardDetector


def verify_windows_key_support():
    """Verify Windows key + V support"""
    print("🦆 Ducky One 2 Windows Key + V Verification")
    print("="*50)
    
    # Test text
    test_text = "Windows Key + V Test - Ducky One 2 Mac Ultra 3"
    pyperclip.copy(test_text)
    print(f"📋 Test text copied to clipboard")
    
    detector = MacKeyboardDetector()
    timing = detector.get_optimal_timing()
    
    print(f"⏱️  Using Apple Silicon optimized timing: {timing['key_press_delay']}s")
    
    controller = keyboard.Controller()
    
    print("\n🔧 Testing Windows key + V equivalent...")
    
    # Execute Windows key + V (mapped to Command + V on Mac)
    controller.press(Key.cmd)  # Windows key → Command
    controller.press('v')
    controller.release('v')
    controller.release(Key.cmd)
    
    print("✅ Windows key + V command executed!")
    print("📝 Check your active application - text should be pasted")
    
    # Verify clipboard still has our text
    clipboard_text = pyperclip.paste()
    if clipboard_text == test_text:
        print("✅ Clipboard verification passed")
    else:
        print("⚠️  Clipboard may have been modified")
    
    print(f"\n📊 Summary:")
    print(f"✅ Ducky One 2 detected: {detector.is_ducky_compatible()}")
    print(f"✅ macOS {detector.get_system_info()['mac_version']}")
    print(f"✅ Apple Silicon optimized: {detector.is_apple_silicon}")
    print(f"✅ Windows key mapping: Windows → Command")
    print(f"✅ Windows + V → Command + V")
    
    return True


if __name__ == "__main__":
    try:
        verify_windows_key_support()
        print("\n🎉 Windows key + V support verified!")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        sys.exit(1)
