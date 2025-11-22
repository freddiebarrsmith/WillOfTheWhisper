#!/usr/bin/env python3
"""
Audio Device Diagnostic - Comprehensive audio system check
"""

import subprocess
import sys


def main():
    """Comprehensive audio diagnostic"""
    print("\n" + "="*60)
    print("🔍 Audio Device Diagnostic")
    print("="*60)
    
    print("1. Checking system audio devices...")
    try:
        result = subprocess.run(["system_profiler", "SPAudioDataType"], 
                              capture_output=True, text=True)
        print("System Audio Devices:")
        print(result.stdout)
        
        if "Input Channels" not in result.stdout:
            print("❌ NO INPUT DEVICES FOUND!")
            print("This means no microphone is detected by macOS")
        else:
            print("✅ Input devices found")
            
    except Exception as e:
        print(f"Error checking system audio: {e}")
    
    print("\n2. Checking FFmpeg audio devices...")
    try:
        result = subprocess.run(["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""], 
                              capture_output=True, text=True)
        print("FFmpeg Audio Devices:")
        print(result.stderr)  # FFmpeg outputs device list to stderr
        
        if "AVFoundation audio devices:" in result.stderr and "[" not in result.stderr.split("AVFoundation audio devices:")[1]:
            print("❌ NO AUDIO INPUT DEVICES IN FFMPEG!")
        else:
            print("✅ Audio input devices found in FFmpeg")
            
    except Exception as e:
        print(f"Error checking FFmpeg: {e}")
    
    print("\n3. Checking sox audio devices...")
    try:
        result = subprocess.run(["sox", "--help"], capture_output=True, text=True)
        print("Sox is installed and working")
        
        # Try to list sox devices
        result = subprocess.run(["sox", "-V"], capture_output=True, text=True)
        print("Sox version info:")
        print(result.stderr[:200] + "..." if len(result.stderr) > 200 else result.stderr)
        
    except Exception as e:
        print(f"Sox error: {e}")
    
    print("\n" + "="*60)
    print("🔧 DIAGNOSIS & SOLUTIONS")
    print("="*60)
    
    print("PROBLEM: No microphone detected by macOS")
    print("\nSOLUTIONS:")
    print("1. Check if microphone is physically connected")
    print("2. Go to System Preferences > Sound > Input")
    print("   - Make sure a microphone is selected")
    print("   - Check if input level shows activity when you speak")
    print("3. Try connecting a USB microphone")
    print("4. Check if microphone is enabled in System Preferences")
    print("5. Restart your Mac")
    print("\nIf you have a Mac Studio, it may not have a built-in microphone.")
    print("You'll need to connect an external microphone.")
    
    print("\n" + "="*60)
    print("🎤 NEXT STEPS")
    print("="*60)
    print("1. Connect a microphone (USB or built-in)")
    print("2. Check System Preferences > Sound > Input")
    print("3. Run this diagnostic again")
    print("4. Once microphone is detected, WhisperControl will work!")


if __name__ == "__main__":
    main()
