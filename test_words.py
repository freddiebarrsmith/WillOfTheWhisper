#!/usr/bin/env python3
"""Test script for word recognition from sign language"""

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

# Track detected words
detected_words = []
current_word_letters = []

def letter_callback(gesture_type, data=None):
    """Callback for individual letters"""
    if gesture_type.value.startswith("letter_"):
        letter = gesture_type.value.replace("letter_", "").upper()
        current_word_letters.append(letter)
        print(f"  Letter: {letter} (word so far: {''.join(current_word_letters)})")

def word_callback(word: str):
    """Callback for complete words"""
    global current_word_letters
    print(f"\n{'='*60}")
    print(f"📝 WORD RECOGNIZED: '{word.upper()}'")
    print(f"{'='*60}\n")
    detected_words.append(word.upper())
    current_word_letters.clear()

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create recognizer
print("Initializing word recognition from sign language...")
recognizer = create_gesture_recognizer(config)

if not recognizer:
    print("❌ Failed to create gesture recognizer")
    sys.exit(1)

# Register callbacks
processor = recognizer.gesture_manager.get_active_processor()
if processor:
    print(f"Active processor: {processor.get_name()}")
    
    # Register for letters
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        gesture_type = GestureType.from_letter(letter)
        recognizer.register_callback(gesture_type, letter_callback)
    
    # Register word callback
    recognizer.register_word_callback(word_callback)
else:
    print("❌ No processor available")
    sys.exit(1)

print("\n" + "="*60)
print("✅ Word Recognition Ready!")
print("="*60)
print("\n📹 Camera is active")
print("\n✋ HOW TO USE:")
print("   1. Spell words using ASL fingerspelling (A-Z)")
print("   2. Hold each letter for 1-2 seconds")
print("   3. Wait 2 seconds after last letter to complete word")
print("   4. Or show a space gesture to force word completion")
print("\n💡 Example:")
print("   Spell: H-E-L-L-O")
print("   After 2 seconds: 'HELLO' will be recognized")
print("\nPress Ctrl+C to stop\n")

# Start
if not recognizer.start():
    print("❌ Failed to start")
    sys.exit(1)

try:
    while recognizer.is_running():
        # Show current word being built
        current = recognizer.get_current_word()
        if current:
            # Update display every second
            time.sleep(1.0)
        else:
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\n" + "="*60)
    print("Stopping...")
    print("="*60)
    recognizer.stop()
    
    if detected_words:
        print(f"\n📝 Detected words: {' '.join(detected_words)}")
    print("Done!")

