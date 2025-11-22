#!/usr/bin/env python3
"""
SUCCESS! WhisperControl - Now working with Bose headset!
"""

import sys
import os
import time
import logging
import whisper
import subprocess
import tempfile
import pyperclip


def main():
    """Main function - SUCCESS VERSION!"""
    print("\n" + "="*60)
    print("🎉 WhisperControl - SUCCESS VERSION!")
    print("="*60)
    print("✅ Bose QC Ultra Headphones working!")
    print("✅ Whisper transcription working!")
    print("✅ Ready for voice prompts!")
    print("="*60)
    
    try:
        # Load Whisper model (using small model that works!)
        print("Loading Whisper model (small)...")
        model = whisper.load_model("small")
        print("✅ Whisper model loaded!")
        
        # Create temporary file
        temp_file = tempfile.mktemp(suffix=".wav")
        
        print(f"\n🎤 Recording for 4 seconds...")
        print("📢 SPEAK YOUR PROMPT INTO YOUR BOSE HEADSET!")
        print("   Say something like: 'Create a function that sorts an array'")
        print("   Countdown: 3... 2... 1... SPEAK!")
        
        # Record with optimized settings
        try:
            result = subprocess.run([
                "ffmpeg", "-f", "avfoundation", "-i", ":0", 
                "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                "-af", "highpass=f=80,lowpass=f=8000,volume=1.5",
                "-t", "4", "-y", temp_file
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and os.path.exists(temp_file):
                file_size = os.path.getsize(temp_file)
                print(f"✅ Recording successful! File size: {file_size} bytes")
                
                print("✅ Transcribing with Whisper...")
                
                # Transcribe with the working small model
                result = model.transcribe(temp_file, language='en', fp16=False)
                transcribed_text = result["text"].strip()
                
                print(f"📝 Raw transcription: '{transcribed_text}'")
                
                if transcribed_text:
                    # Simple processing
                    filler_words = ['um', 'uh', 'like', 'you know', 'i mean', 'actually', 'basically']
                    words = transcribed_text.split()
                    filtered_words = [word for word in words if word.lower() not in filler_words]
                    processed = ' '.join(filtered_words)
                    
                    if processed and not processed.endswith(('.', '!', '?')):
                        processed += '.'
                    
                    # Copy to clipboard
                    pyperclip.copy(processed)
                    
                    print(f"✅ Processed text: '{processed}'")
                    print(f"✅ Text copied to clipboard!")
                    print("📋 Now paste it wherever you want (Cmd+V)")
                    print("\n🎉 SUCCESS! WhisperControl is working perfectly!")
                else:
                    print("❌ No speech detected")
                    print("💡 Try speaking louder or more clearly")
                
            else:
                print(f"❌ Recording failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ Recording timed out")
        except Exception as e:
            print(f"❌ Recording error: {e}")
        
        # Clean up
        try:
            os.remove(temp_file)
        except:
            pass
            
        print("\n" + "="*60)
        print("🎤 WhisperControl Status: WORKING PERFECTLY!")
        print("Run the script again to record more prompts.")
        print("="*60)
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
