#!/usr/bin/env python3
"""Test script for sign language recognition (ASL alphabet and numbers)"""

import sys
import os
import time
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gesture_recognizer import create_gesture_recognizer
from gestures import GestureType
import yaml

# Track detected signs
detected_signs = []

def sign_callback(gesture_type, data=None):
    """Callback for any sign language gesture"""
    sign_name = gesture_type.value.replace("_", " ").title()
    
    # Extract letter or number
    if "Letter" in sign_name:
        letter = sign_name.split()[-1]
        print(f"\n{'='*60}")
        print(f"✋ SIGN DETECTED: Letter '{letter}'")
        print(f"{'='*60}\n")
        detected_signs.append(letter)
    elif "Number" in sign_name:
        number = sign_name.split()[-1]
        print(f"\n{'='*60}")
        print(f"✋ SIGN DETECTED: Number {number}")
        print(f"{'='*60}\n")
        detected_signs.append(number)
    elif "Word" in sign_name:
        word = sign_name.replace("Word ", "").replace("_", " ").title()
        print(f"\n{'='*60}")
        print(f"✋ ASL WORD SIGN: '{word}'")
        print(f"{'='*60}\n")
        detected_signs.append(word)
    elif "Thumbs" in sign_name:
        direction = "Up" if "Up" in sign_name else "Down"
        print(f"\n{'='*60}")
        print(f"👍 THUMBS {direction} detected!")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'='*60}")
        print(f"✋ SIGN DETECTED: {sign_name}")
        print(f"{'='*60}\n")

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create recognizer
print("Initializing sign language recognition...")
recognizer = create_gesture_recognizer(config)

if not recognizer:
    print("❌ Failed to create gesture recognizer")
    sys.exit(1)

# Check which processor is active
processor = recognizer.gesture_manager.get_active_processor()
if processor:
    print(f"Active processor: {processor.get_name()}")
    # Register for all gesture types
    for gesture_type in GestureType:
        if gesture_type != GestureType.UNKNOWN:
            recognizer.register_callback(gesture_type, sign_callback)
else:
    print("❌ No processor available")
    sys.exit(1)

print("\n" + "="*60)
print("✅ Sign Language Recognition Ready!")
print("="*60)
print("\n📹 Camera is active")
print("\n✋ ASL WORD SIGNS:")
print("   Show complete word signs: YES, NO, THANK YOU, PLEASE, etc.")
print("\n✋ ASL ALPHABET:")
print("   Show letters A-Z using ASL fingerspelling")
print("\n🔢 ASL NUMBERS:")
print("   Show numbers 1-10 using ASL number signs")
print("\n👍 THUMBS:")
print("   Show thumbs up or thumbs down")
print("\n💡 Tips:")
print("   - Hold each sign steady for 1-2 seconds")
print("   - Make sure your hand is clearly visible")
print("   - There's a 1s cooldown between detections")
print("\nPress Ctrl+C to stop\n")

# Start
if not recognizer.start():
    print("❌ Failed to start")
    sys.exit(1)

try:
    while recognizer.is_running():
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\n" + "="*60)
    print("Stopping...")
    print("="*60)
    recognizer.stop()
    
    if detected_signs:
        print(f"\n📝 Detected signs: {' '.join(detected_signs)}")
    print("Done!")

