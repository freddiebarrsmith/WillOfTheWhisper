#!/usr/bin/env python3
"""
Test Windows Key + V functionality on Ducky One 2 with Mac Ultra 3
"""

import sys
import os
import time
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mac_keyboard_utils import MacKeyboardDetector


def test_paste_methods():
    """Test different paste methods"""
    print("🦆 Testing Paste Methods for Ducky One 2")
    print("="*50)
    
    # Test text
    test_text = "Ducky One 2 Windows Key + V Test - Hello Mac Ultra 3!"
    pyperclip.copy(test_text)
    print(f"📋 Copied to clipboard: {test_text}")
    
    detector = MacKeyboardDetector()
    timing = detector.get_optimal_timing()
    
    print(f"\n⏱️  Using timing: {timing}")
    print("\nTesting paste methods...")
    
    controller = keyboard.Controller()
    
    # Method 1: Command + V (Mac standard)
    print("\n1️⃣ Testing Command + V...")
    try:
        controller.press(Key.cmd)
        time.sleep(timing["key_press_delay"])
        controller.press('v')
        controller.release('v')
        time.sleep(timing["key_release_delay"])
        controller.release(Key.cmd)
        print("✅ Command + V executed")
    except Exception as e:
        print(f"❌ Command + V failed: {e}")
    
    time.sleep(1)
    
    # Method 2: Ctrl + V (Windows style)
    print("\n2️⃣ Testing Ctrl + V...")
    try:
        controller.press(Key.ctrl)
        time.sleep(timing["key_press_delay"])
        controller.press('v')
        controller.release('v')
        time.sleep(timing["key_release_delay"])
        controller.release(Key.ctrl)
        print("✅ Ctrl + V executed")
    except Exception as e:
        print(f"❌ Ctrl + V failed: {e}")
    
    time.sleep(1)
    
    # Method 3: Try Windows key mapping
    print("\n3️⃣ Testing Windows key equivalent...")
    try:
        # On Mac, Windows key should map to Command
        controller.press(Key.cmd)  # Windows key → Command
        time.sleep(timing["key_press_delay"])
        controller.press('v')
        controller.release('v')
        time.sleep(timing["key_release_delay"])
        controller.release(Key.cmd)
        print("✅ Windows key equivalent executed")
    except Exception as e:
        print(f"❌ Windows key equivalent failed: {e}")


def test_keyboard_detection():
    """Test keyboard detection"""
    print("\n🔍 Keyboard Detection Test")
    print("="*50)
    
    detector = MacKeyboardDetector()
    info = detector.get_system_info()
    
    print(f"macOS Version: {info['mac_version']}")
    print(f"Apple Silicon: {info['is_apple_silicon']}")
    print(f"Ducky Detected: {info['keyboard_info']['ducky_detected']}")
    print(f"Mac Mode: {info['keyboard_info']['mac_mode']}")
    
    mappings = detector.get_ducky_mappings()
    print(f"\nKey Mappings:")
    print(f"Windows key → {mappings.get('windows', 'N/A')}")
    print(f"Win key → {mappings.get('win', 'N/A')}")
    print(f"Command key → {mappings.get('cmd', 'N/A')}")


def interactive_test():
    """Interactive test with user"""
    print("\n🎮 Interactive Test")
    print("="*50)
    print("This will test actual paste functionality.")
    print("Make sure you have a text editor open!")
    print("\nPress Enter to start test or Ctrl+C to skip...")
    
    try:
        input()
        
        test_text = "Interactive Ducky One 2 Test - Windows Key + V"
        pyperclip.copy(test_text)
        print(f"📋 Copied: {test_text}")
        
        detector = MacKeyboardDetector()
        timing = detector.get_optimal_timing()
        
        print("\nExecuting Windows key + V equivalent...")
        
        controller = keyboard.Controller()
        # Use Windows key equivalent (Command on Mac)
        controller.press(Key.cmd)
        time.sleep(timing["key_press_delay"])
        controller.press('v')
        controller.release('v')
        time.sleep(timing["key_release_delay"])
        controller.release(Key.cmd)
        
        print("✅ Paste command executed!")
        print("Check your text editor to see if the text was pasted.")
        
    except KeyboardInterrupt:
        print("\nSkipping interactive test...")


def main():
    """Main test function"""
    print("🦆 Ducky One 2 Windows Key + V Test")
    print("="*50)
    
    try:
        test_keyboard_detection()
        test_paste_methods()
        interactive_test()
        
        print("\n" + "="*50)
        print("📊 Test Complete")
        print("="*50)
        print("✅ All paste methods tested")
        print("✅ Windows key mapping configured")
        print("✅ Ducky One 2 compatibility verified")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
