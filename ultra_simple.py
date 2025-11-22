#!/usr/bin/env python3
"""
Ultra Simple WhisperControl - Just works!
"""

import sys
import os
import time
import logging
import whisper
import sounddevice as sd
import soundfile as sf
import numpy as np
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key


class UltraSimpleWhisperControl:
    """Ultra simple version that just works"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Load Whisper model
        self.logger.info("Loading Whisper model...")
        self.model = whisper.load_model("base")
        self.logger.info("Whisper model loaded!")
        
        # Audio settings
        self.sample_rate = 16000
        self.duration = 3  # Record for 3 seconds
        
        self.logger.info("Ultra Simple WhisperControl ready!")
    
    def start(self):
        """Start the simple version"""
        self.logger.info("Starting Ultra Simple WhisperControl...")
        self.logger.info("Press 'r' to record, 'q' to quit")
        
        # Simple key listener
        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char == 'r':
                    self.record_and_transcribe()
                elif hasattr(key, 'char') and key.char == 'q':
                    self.logger.info("Quitting...")
                    return False
            except AttributeError:
                pass
        
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    
    def record_and_transcribe(self):
        """Record audio and transcribe"""
        try:
            self.logger.info("Recording for 3 seconds... Speak now!")
            
            # Record audio
            audio_data = sd.rec(int(self.duration * self.sample_rate), 
                              samplerate=self.sample_rate, 
                              channels=1, 
                              dtype='float64')
            sd.wait()  # Wait until recording is finished
            
            self.logger.info("Recording finished! Transcribing...")
            
            # Save to temporary file
            temp_file = "temp_recording.wav"
            sf.write(temp_file, audio_data, self.sample_rate)
            
            # Transcribe
            result = self.model.transcribe(temp_file)
            transcribed_text = result["text"].strip()
            
            if transcribed_text:
                self.logger.info(f"Transcribed: {transcribed_text}")
                
                # Simple processing
                processed_text = self.process_text(transcribed_text)
                
                # Copy to clipboard
                pyperclip.copy(processed_text)
                
                # Paste
                self.paste_text()
                
                self.logger.info(f"Sent: {processed_text}")
            else:
                self.logger.warning("No speech detected")
            
            # Clean up
            try:
                os.remove(temp_file)
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Error: {e}")
    
    def process_text(self, text):
        """Simple text processing"""
        # Remove filler words
        filler_words = ['um', 'uh', 'like', 'you know', 'i mean', 'actually', 'basically']
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in filler_words]
        
        processed = ' '.join(filtered_words)
        
        # Ensure proper punctuation
        if processed and not processed.endswith(('.', '!', '?')):
            processed += '.'
        
        return processed
    
    def paste_text(self):
        """Paste text using Cmd+V"""
        try:
            time.sleep(0.1)  # Small delay
            
            with keyboard.Controller() as controller:
                controller.press(Key.cmd)
                controller.press('v')
                controller.release('v')
                controller.release(Key.cmd)
            
            self.logger.info("Text pasted!")
            
        except Exception as e:
            self.logger.error(f"Failed to paste: {e}")


def main():
    """Main function"""
    print("\n" + "="*60)
    print("🎤 Ultra Simple WhisperControl")
    print("="*60)
    print("Commands:")
    print("- Press 'r' to record and transcribe")
    print("- Press 'q' to quit")
    print("- Make sure to grant microphone permissions!")
    print("="*60)
    
    try:
        app = UltraSimpleWhisperControl()
        app.start()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
