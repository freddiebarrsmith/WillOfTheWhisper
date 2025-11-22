#!/usr/bin/env python3
"""
Force-Run WhisperControl - Bypasses permission checks and tries anyway
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
    """Main function - force run without permission checks"""
    print("\n" + "="*60)
    print("🎤 Force-Run WhisperControl")
    print("="*60)
    print("Bypassing permission checks - trying anyway!")
    print("="*60)
    
    try:
        # Load Whisper model
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("✅ Whisper model loaded!")
        
        # Debug: List all audio devices
        print("\n🔍 Debugging audio devices...")
        try:
            devices = sd.query_devices()
            print("Available devices:")
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    print(f"  {i}: {device['name']} (inputs: {device['max_input_channels']})")
        except Exception as e:
            print(f"Could not query devices: {e}")
        
        # Try different approaches
        sample_rate = 16000
        duration = 3
        
        print(f"\n🎤 Attempting to record for {duration} seconds...")
        print("Speak now!")
        
        # Try with explicit device selection
        try:
            # Try device 0 first
            print("Trying device 0...")
            audio_data = sd.rec(int(duration * sample_rate), 
                              samplerate=sample_rate, 
                              channels=1, 
                              dtype='float64',
                              device=0)
            sd.wait()
            print("✅ Recording successful with device 0!")
            
        except Exception as e1:
            print(f"Device 0 failed: {e1}")
            
            try:
                # Try default device
                print("Trying default device...")
                audio_data = sd.rec(int(duration * sample_rate), 
                                  samplerate=sample_rate, 
                                  channels=1, 
                                  dtype='float64')
                sd.wait()
                print("✅ Recording successful with default device!")
                
            except Exception as e2:
                print(f"Default device failed: {e2}")
                
                try:
                    # Try with different sample rate
                    print("Trying with different sample rate...")
                    audio_data = sd.rec(int(duration * 44100), 
                                      samplerate=44100, 
                                      channels=1, 
                                      dtype='float64')
                    sd.wait()
                    print("✅ Recording successful with 44.1kHz!")
                    sample_rate = 44100
                    
                except Exception as e3:
                    print(f"All recording attempts failed:")
                    print(f"  Device 0: {e1}")
                    print(f"  Default: {e2}")
                    print(f"  44.1kHz: {e3}")
                    print("\n❌ Cannot record audio. This usually means:")
                    print("  1. No microphone connected")
                    print("  2. Microphone permission denied")
                    print("  3. Another app is using the microphone")
                    return
        
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
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
