#!/usr/bin/env python3
"""
Permission-Aware WhisperControl - Requests microphone permissions properly
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
import subprocess


def request_microphone_permission():
    """Request microphone permission from macOS"""
    print("🔐 Requesting microphone permission...")
    
    try:
        # Try to access microphone - this should trigger permission request
        print("Testing microphone access...")
        test_recording = sd.rec(int(0.1 * 16000), samplerate=16000, channels=1, dtype='float64')
        sd.wait()
        print("✅ Microphone permission granted!")
        return True
    except Exception as e:
        print(f"❌ Microphone permission needed: {e}")
        
        # Try to open System Preferences to microphone settings
        try:
            print("Opening System Preferences to microphone settings...")
            subprocess.run([
                "open", 
                "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"
            ], check=True)
            print("📱 Please grant microphone permission in System Preferences")
            print("   Then restart this script")
            return False
        except Exception as pref_error:
            print(f"Could not open System Preferences: {pref_error}")
            print("Please manually go to:")
            print("   System Preferences > Security & Privacy > Privacy > Microphone")
            print("   Add Terminal to the list and enable it")
            return False


def main():
    """Main function"""
    print("\n" + "="*60)
    print("🎤 Permission-Aware WhisperControl")
    print("="*60)
    
    # Request microphone permission first
    if not request_microphone_permission():
        print("\n❌ Microphone permission required to continue")
        print("Please grant permission and run the script again")
        return
    
    try:
        # Load Whisper model
        print("\nLoading Whisper model...")
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
            
        print("\n🎉 Success! Run the script again to record more.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if "permission" in str(e).lower() or "access" in str(e).lower():
            print("\nThis looks like a permission issue.")
            print("Please grant microphone permission and try again.")


if __name__ == "__main__":
    main()
