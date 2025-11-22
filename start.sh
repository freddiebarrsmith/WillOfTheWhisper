#!/bin/bash

# WhisperControl Launcher Script

echo "Starting WhisperControl..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Check if installation is working
echo "Testing installation..."
python test_installation.py

if [ $? -eq 0 ]; then
    echo "Starting WhisperControl..."
    python src/main.py
else
    echo "Installation test failed. Please check the errors above."
    exit 1
fi
