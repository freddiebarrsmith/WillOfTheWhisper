#!/usr/bin/env python3
"""Simple gesture recognition test - run this directly"""

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

def thumbs_up_callback(gesture_type, data=None):
    print("\n" + "="*60)
    print("👍 THUMBS UP detected!")
    print("="*60 + "\n")

def thumbs_down_callback(gesture_type, data=None):
    print("\n" + "="*60)
    print("👎 THUMBS DOWN detected!")
    print("="*60 + "\n")

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create recognizer
print("Initializing gesture recognition...")
recognizer = create_gesture_recognizer(config)

if not recognizer:
    print("❌ Failed to create gesture recognizer")
    sys.exit(1)

# Register callbacks
recognizer.register_callback(GestureType.THUMBS_UP, thumbs_up_callback)
recognizer.register_callback(GestureType.THUMBS_DOWN, thumbs_down_callback)

print("\n" + "="*60)
print("✅ Gesture recognition ready!")
print("="*60)
print("\n📹 Camera is active")
print("👆 Show THUMBS UP to the camera")
print("👇 Show THUMBS DOWN to the camera")
print("\n💡 Hold the gesture steady for 1-2 seconds")
print("Press Ctrl+C to stop\n")

# Start
if not recognizer.start():
    print("❌ Failed to start")
    sys.exit(1)

try:
    while recognizer.is_running():
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\nStopping...")
    recognizer.stop()
    print("Done!")

