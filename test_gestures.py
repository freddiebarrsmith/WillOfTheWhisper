#!/usr/bin/env python3
"""
Example script for testing gesture recognition (thumbs up/down)
"""

import sys
import os
import time
import logging
import warnings
import yaml

# Suppress protobuf deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, module='google.protobuf')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gesture_recognizer import GestureRecognizer, create_gesture_recognizer
from gestures import GestureType


def thumbs_up_callback(gesture_type, data=None):
    """Callback for thumbs up gesture"""
    print("\n" + "="*50)
    print("👍 THUMBS UP detected!")
    print("="*50 + "\n")
    # Add your action here, e.g., approve, like, confirm, etc.


def thumbs_down_callback(gesture_type, data=None):
    """Callback for thumbs down gesture"""
    print("\n" + "="*50)
    print("👎 THUMBS DOWN detected!")
    print("="*50 + "\n")
    # Add your action here, e.g., reject, dislike, cancel, etc.


def main():
    """Main function"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load config
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Create gesture recognizer
    recognizer = create_gesture_recognizer(config)
    if not recognizer:
        print("Failed to create gesture recognizer")
        print("Make sure you have installed: pip install opencv-python mediapipe")
        return
    
    # Check if processor is available
    processor = recognizer.gesture_manager.get_active_processor()
    if not processor:
        print("\n❌ Camera not available!")
        print("\nTo fix this on macOS:")
        print("1. Go to System Settings > Privacy & Security > Camera")
        print("2. Enable camera access for Terminal (or Python)")
        print("3. If Terminal is not listed, run this script once and it should prompt")
        print("\nAlternatively, you can grant permission via:")
        print("  System Settings > Privacy & Security > Camera")
        return
    
    # Register callbacks
    recognizer.register_callback(GestureType.THUMBS_UP, thumbs_up_callback)
    recognizer.register_callback(GestureType.THUMBS_DOWN, thumbs_down_callback)
    
    print("\n" + "="*60)
    print("Starting gesture recognition...")
    print("="*60)
    print("\n📹 Camera is active")
    print("👆 Show THUMBS UP to the camera")
    print("👇 Show THUMBS DOWN to the camera")
    print("\n💡 Tips:")
    print("   - Hold the gesture steady for 1-2 seconds")
    print("   - Make sure your hand is clearly visible")
    print("   - There's a 0.5s cooldown between detections")
    print("\nPress Ctrl+C to stop\n")
    
    # Start recognition
    if not recognizer.start():
        print("Failed to start gesture recognition")
        return
    
    try:
        # Keep running
        while recognizer.is_running():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping gesture recognition...")
        recognizer.stop()
        print("Done!")


if __name__ == "__main__":
    main()

