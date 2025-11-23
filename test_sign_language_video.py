#!/usr/bin/env python3
"""Test script for sign language recognition with video preview"""

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
    
    # Extract letter, number, or word
    if "Word" in sign_name:
        word = sign_name.split()[-1]
        print(f"\n{'='*60}")
        print(f"✋ ASL WORD SIGN: '{word}'")
        print(f"{'='*60}\n")
        detected_signs.append(f"WORD:{word}")
    elif "Letter" in sign_name:
        letter = sign_name.split()[-1]
        print(f"  Letter: {letter}")
        detected_signs.append(letter)
    elif "Number" in sign_name:
        number = sign_name.split()[-1]
        print(f"\n{'='*60}")
        print(f"🔢 NUMBER: {number}")
        print(f"{'='*60}\n")
        detected_signs.append(f"NUM:{number}")
    elif "Thumbs" in sign_name:
        direction = "Up" if "Up" in sign_name else "Down"
        print(f"\n{'='*60}")
        print(f"👍 THUMBS {direction}")
        print(f"{'='*60}\n")

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Enable preview
config['gestures']['show_preview'] = True

# Create recognizer
print("Initializing sign language recognition with video preview...")
recognizer = create_gesture_recognizer(config)

if not recognizer:
    print("❌ Failed to create gesture recognizer")
    sys.exit(1)

# Register callbacks for all sign types
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
print("✅ Sign Language Recognition with Video Preview Ready!")
print("="*60)
print("\n📹 Camera window will open showing:")
print("   - Live camera feed")
print("   - Detected signs in real-time")
print("   - Visual representation of signs")
print("\n✋ Try showing:")
print("   - ASL word signs (YES, NO, THANK YOU, etc.)")
print("   - ASL letters (A-Z)")
print("   - ASL numbers (1-10)")
print("\nPress Q in the video window to quit")
print("Press Ctrl+C to stop\n")

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

