#!/usr/bin/env python3
"""
One-Shot WhisperControl - Records once and exits
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


def main():
    """Main function - records once and exits"""
    print("\n" + "="*60)
    print("🎤 One-Shot WhisperControl")
    print("="*60)
    print("This will record for 3 seconds, transcribe, and copy to clipboard.")
    print("="*60)
    
    try:
        # Load Whisper model
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("✅ Whisper model loaded!")
        
        # Audio settings
        sample_rate = 16000
        duration = 3
        
        print(f"\n🎤 Recording for {duration} seconds... Speak now!")
        
        # Record audio
        audio_data = sd.rec(int(duration * sample_rate), 
                          samplerate=sample_rate, 
                          channels=1, 
                          dtype='float64')
        sd.wait()  # Wait until recording is finished
        
        print("✅ Recording finished! Transcribing...")
        
        # Save to temporary file
        temp_file = "temp_recording.wav"
        sf.write(temp_file, audio_data, sample_rate)
        
        # Transcribe
        result = model.transcribe(temp_file)
        transcribed_text = result["text"].strip()
        
        if transcribed_text:
            print(f"📝 Transcribed: {transcribed_text}")
            
            # Simple processing
            filler_words = ['um', 'uh', 'like', 'you know', 'i mean', 'actually', 'basically']
            words = transcribed_text.split()
            filtered_words = [word for word in words if word.lower() not in filler_words]
            processed = ' '.join(filtered_words)
            
            if processed and not processed.endswith(('.', '!', '?')):
                processed += '.'
            
            # Copy to clipboard
            pyperclip.copy(processed)
            
            print(f"✅ Text copied to clipboard: {processed}")
            print("📋 Now paste it wherever you want (Cmd+V)")
        else:
            print("❌ No speech detected")
        
        # Clean up
        try:
            os.remove(temp_file)
        except:
            pass
            
        print("\n🎉 Done! Run the script again to record more.")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
