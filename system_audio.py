#!/usr/bin/env python3
"""
System Audio WhisperControl - Uses system audio capture
"""

import sys
import os
import time
import logging
import whisper
import subprocess
import tempfile
import pyperclip


def record_with_system_audio():
    """Record using system audio tools"""
    print("🎤 Recording using system audio tools...")
    
    # Create temporary file
    temp_file = tempfile.mktemp(suffix=".wav")
    
    try:
        # Try using sox (if available)
        print("Trying with sox...")
        result = subprocess.run([
            "sox", "-d", temp_file, "trim", "0", "3"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Recording successful with sox!")
            return temp_file
        else:
            print(f"sox failed: {result.stderr}")
            
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"sox not available: {e}")
    
    try:
        # Try using ffmpeg (if available)
        print("Trying with ffmpeg...")
        result = subprocess.run([
            "ffmpeg", "-f", "avfoundation", "-i", ":0", "-t", "3", "-y", temp_file
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Recording successful with ffmpeg!")
            return temp_file
        else:
            print(f"ffmpeg failed: {result.stderr}")
            
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"ffmpeg not available: {e}")
    
    try:
        # Try using rec (if available)
        print("Trying with rec...")
        result = subprocess.run([
            "rec", "-r", "16000", "-c", "1", temp_file, "trim", "0", "3"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Recording successful with rec!")
            return temp_file
        else:
            print(f"rec failed: {result.stderr}")
            
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"rec not available: {e}")
    
    return None


def main():
    """Main function"""
    print("\n" + "="*60)
    print("🎤 System Audio WhisperControl")
    print("="*60)
    print("Using system audio tools instead of Python libraries")
    print("="*60)
    
    try:
        # Load Whisper model
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("✅ Whisper model loaded!")
        
        print("\n🎤 Recording for 3 seconds... Speak now!")
        
        # Record using system tools
        temp_file = record_with_system_audio()
        
        if not temp_file or not os.path.exists(temp_file):
            print("❌ Could not record audio with any system tool")
            print("\nTroubleshooting:")
            print("1. Check if microphone is connected")
            print("2. Try: brew install sox")
            print("3. Try: brew install ffmpeg")
            print("4. Check System Preferences > Sound > Input")
            return
        
        print("✅ Recording finished! Transcribing...")
        
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
