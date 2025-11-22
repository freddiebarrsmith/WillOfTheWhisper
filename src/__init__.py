"""
WhisperControl - Voice Dictation Tool for macOS
"""

__version__ = "1.0.0"
__author__ = "WhisperControl Team"

from config import Config
from .audio_capture import AudioCapture
from .whisper_transcriber import WhisperTranscriber
from .system_integration import SystemIntegration

__all__ = [
    'Config',
    'AudioCapture', 
    'WhisperTranscriber',
    'SystemIntegration'
]
