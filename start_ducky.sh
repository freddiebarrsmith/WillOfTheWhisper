#!/bin/bash
# Ducky One 2 Mac Ultra 3 Startup Script

echo "🦆 Starting WhisperControl with Ducky One 2 Mac Ultra 3 Support"
echo "=============================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Ducky One 2 is detected
echo "🔍 Checking Ducky One 2 compatibility..."
python3 -c "
import sys
sys.path.append('src')
from mac_keyboard_utils import MacKeyboardDetector
detector = MacKeyboardDetector()
info = detector.get_system_info()
if info['is_ducky_compatible']:
    print('✅ Ducky One 2 detected and compatible!')
    print(f'📱 macOS {info[\"mac_version\"]} ({info[\"architecture\"]})')
    print('⚡ Apple Silicon optimizations enabled')
else:
    print('⚠️  Ducky One 2 not detected, but generic Mac support enabled')
"

echo ""
echo "🎤 Starting WhisperControl..."
echo "Hotkey: Shift+9 (press and hold to record, release to send)"
echo "Press Ctrl+C to stop"
echo ""

# Start WhisperControl with Ducky Mac handler
python3 src/main.py
