#!/bin/bash

# WhisperControl Setup Script for macOS

echo "Setting up WhisperControl..."

# Check if Python 3.9+ is installed
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.9+ is required. Current version: $python_version"
    echo "Please install Python 3.9+ from https://python.org"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Whisper model
echo "Downloading Whisper base model..."
python3 -c "import whisper; whisper.load_model('base')"

# Create necessary directories
mkdir -p temp logs

echo "Setup complete!"
echo "To run WhisperControl:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run: python src/main.py"
echo ""
echo "Make sure to grant microphone permissions to Terminal/Python in System Preferences > Security & Privacy > Microphone"
