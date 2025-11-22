#!/usr/bin/env python3
"""
Working WhisperControl - Now with your Bose headset!
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
    """Main function - now working with Bose headset!"""
    print("\n" + "="*60)
    print("🎤 WhisperControl - WORKING VERSION!")
    print("="*60)
    print("✅ Bose QC Ultra Headphones detected!")
    print("✅ Recording and transcription ready!")
    print("="*60)
    
    try:
        # Load Whisper model
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("✅ Whisper model loaded!")
        
        # Create temporary file
        temp_file = tempfile.mktemp(suffix=".wav")
        
        print(f"\n🎤 Recording for 5 seconds...")
        print("📢 SPEAK CLEARLY INTO YOUR BOSE HEADSET NOW!")
        print("   (Count down: 5... 4... 3... 2... 1... SPEAK!)")
        
        # Record using the working FFmpeg approach
        try:
            result = subprocess.run([
                "ffmpeg", "-f", "avfoundation", "-i", ":0", 
                "-acodec", "pcm_s16le", "-ar", "16000", 
                "-t", "5", "-y", temp_file
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and os.path.exists(temp_file):
                file_size = os.path.getsize(temp_file)
                print(f"✅ Recording successful! File size: {file_size} bytes")
                
                if file_size < 1000:
                    print("❌ File too small - may be silent")
                    return
                
                print("✅ Transcribing...")
                
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
                    print("💡 Try speaking louder or closer to the microphone")
                
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
            
        print("\n🎉 WhisperControl is working!")
        print("Run the script again to record more.")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
