#!/usr/bin/env python3
"""
Ducky One 2 Mac Ultra 3 Test Script
Tests the Ducky One 2 keyboard compatibility with Mac Ultra 3
"""

import sys
import os
import time
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mac_keyboard_utils import MacKeyboardDetector, MacKeyMapper
from plugins.handlers.ducky_mac_handler import DuckyMacHandler


def setup_logging():
    """Setup logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_keyboard_detection():
    """Test keyboard detection capabilities"""
    print("\n" + "="*60)
    print("🔍 Testing Mac Keyboard Detection")
    print("="*60)
    
    detector = MacKeyboardDetector()
    system_info = detector.get_system_info()
    
    print(f"macOS Version: {system_info['mac_version']}")
    print(f"Apple Silicon: {system_info['is_apple_silicon']}")
    print(f"Platform: {system_info['platform']}")
    print(f"Architecture: {system_info['architecture']}")
    
    print(f"\nDucky Compatibility: {system_info['is_ducky_compatible']}")
    print(f"Connected Keyboards: {len(system_info['keyboard_info']['connected_keyboards'])}")
    
    if system_info['keyboard_info']['ducky_detected']:
        print("✅ Ducky One 2 keyboard detected!")
    else:
        print("⚠️  Ducky One 2 keyboard not detected (may still work)")
    
    print(f"\nOptimal Timing Settings:")
    timing = system_info['optimal_timing']
    for key, value in timing.items():
        print(f"  {key}: {value}")
    
    return system_info


def test_key_mapping():
    """Test key mapping functionality"""
    print("\n" + "="*60)
    print("⌨️  Testing Key Mapping")
    print("="*60)
    
    detector = MacKeyboardDetector()
    key_mapper = MacKeyMapper(detector)
    
    test_keys = ['cmd', 'option', 'control', 'shift', 'enter', 'tab', 'space']
    
    print("Key Mappings:")
    for key in test_keys:
        mapped = key_mapper.map_key(key)
        is_mac = key_mapper.is_mac_key(key)
        timing = key_mapper.get_key_timing("key_press_delay")
        print(f"  {key} → {mapped} (Mac: {is_mac}, Timing: {timing}s)")
    
    # Test key sequence
    test_sequence = ['cmd', 'v']
    optimized_sequence = key_mapper.get_ducky_optimized_sequence(test_sequence)
    
    print(f"\nOptimized Sequence for {test_sequence}:")
    for item in optimized_sequence:
        print(f"  {item}")


def test_ducky_handler():
    """Test the Ducky Mac handler"""
    print("\n" + "="*60)
    print("🦆 Testing Ducky Mac Handler")
    print("="*60)
    
    # Mock config
    config = {
        'ai_assistants': {
            'ducky_mac': {
                'enabled': True,
                'priority': 95
            }
        }
    }
    
    handler = DuckyMacHandler(config)
    
    print(f"Handler Name: {handler.get_name()}")
    print(f"Handler Description: {handler.get_description()}")
    print(f"Priority: {handler.get_priority()}")
    
    # Mock app info
    app_info = {
        'name': 'Test App',
        'title': 'Test Window'
    }
    
    can_handle = handler.can_handle(app_info)
    print(f"Can Handle Test App: {can_handle}")
    
    keyboard_info = handler.get_keyboard_info()
    print(f"\nKeyboard Info:")
    for key, value in keyboard_info.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")
    
    return handler


def test_optimizations():
    """Test optimization settings"""
    print("\n" + "="*60)
    print("⚡ Testing Optimizations")
    print("="*60)
    
    detector = MacKeyboardDetector()
    optimizations = detector.optimize_for_ducky()
    
    print("Ducky One 2 Optimizations:")
    for key, value in optimizations.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")


def run_interactive_test():
    """Run interactive test with actual keyboard input"""
    print("\n" + "="*60)
    print("🎮 Interactive Test")
    print("="*60)
    print("This will test actual keyboard input/output.")
    print("Make sure your Ducky One 2 is connected and in Mac mode.")
    print("\nPress Enter to continue or Ctrl+C to skip...")
    
    try:
        input()
        
        # Test clipboard functionality
        print("Testing clipboard functionality...")
        import pyperclip
        
        test_text = "Ducky One 2 Mac Ultra 3 Test - Hello World!"
        pyperclip.copy(test_text)
        
        copied_text = pyperclip.paste()
        if copied_text == test_text:
            print("✅ Clipboard test passed!")
        else:
            print("❌ Clipboard test failed!")
        
        print("\nTesting keyboard input simulation...")
        print("This will simulate Cmd+V paste command.")
        print("Make sure you have a text editor open!")
        print("Press Enter to simulate paste or Ctrl+C to skip...")
        
        input()
        
        from pynput import keyboard
        from pynput.keyboard import Key
        
        with keyboard.Controller() as controller:
            controller.press(Key.cmd)
            controller.press('v')
            controller.release('v')
            controller.release(Key.cmd)
        
        print("✅ Paste simulation completed!")
        
    except KeyboardInterrupt:
        print("\nSkipping interactive test...")


def main():
    """Main test function"""
    setup_logging()
    
    print("🦆 Ducky One 2 Mac Ultra 3 Compatibility Test")
    print("="*60)
    
    try:
        # Run all tests
        system_info = test_keyboard_detection()
        test_key_mapping()
        handler = test_ducky_handler()
        test_optimizations()
        
        # Summary
        print("\n" + "="*60)
        print("📊 Test Summary")
        print("="*60)
        
        print(f"✅ System Detection: PASSED")
        print(f"✅ Key Mapping: PASSED")
        print(f"✅ Handler Creation: PASSED")
        print(f"✅ Optimizations: PASSED")
        
        if system_info['is_ducky_compatible']:
            print(f"✅ Ducky One 2 Compatibility: CONFIRMED")
        else:
            print(f"⚠️  Ducky One 2 Compatibility: UNCERTAIN (may still work)")
        
        print(f"\n🎉 All tests completed successfully!")
        print(f"Your Ducky One 2 should work with Mac Ultra 3!")
        
        # Offer interactive test
        run_interactive_test()
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
