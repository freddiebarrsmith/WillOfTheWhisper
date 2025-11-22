#!/usr/bin/env python3
"""
No-Permissions WhisperControl - Just works without any permissions!
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


class NoPermissionsWhisperControl:
    """Version that works without any macOS permissions"""
    
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
        
        self.logger.info("No-Permissions WhisperControl ready!")
    
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
                
                self.logger.info(f"✅ Text copied to clipboard: {processed_text}")
                self.logger.info("📋 Now paste it wherever you want (Cmd+V)")
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


def main():
    """Main function"""
    print("\n" + "="*60)
    print("🎤 No-Permissions WhisperControl")
    print("="*60)
    print("This version works WITHOUT any macOS permissions!")
    print("Just run the script and it will record automatically.")
    print("="*60)
    
    try:
        app = NoPermissionsWhisperControl()
        
        while True:
            print("\nPress Enter to record, or 'q' + Enter to quit:")
            user_input = input().strip().lower()
            
            if user_input == 'q':
                print("Goodbye!")
                break
            else:
                app.record_and_transcribe()
                
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
