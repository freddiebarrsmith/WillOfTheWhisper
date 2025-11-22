#!/usr/bin/env python3
"""
Multi-Tool WhisperControl - Uses multiple audio recording methods
"""

import sys
import os
import time
import logging
import whisper
import subprocess
import tempfile
import pyperclip


def record_with_multiple_tools():
    """Record using multiple audio tools with different approaches"""
    print("🎤 Recording using multiple audio tools...")
    
    # Create temporary file
    temp_file = tempfile.mktemp(suffix=".wav")
    
    # Try different FFmpeg approaches
    ffmpeg_attempts = [
        # Try different device indices
        ["ffmpeg", "-f", "avfoundation", "-i", ":0", "-t", "3", "-y", temp_file],
        ["ffmpeg", "-f", "avfoundation", "-i", ":1", "-t", "3", "-y", temp_file],
        ["ffmpeg", "-f", "avfoundation", "-i", ":2", "-t", "3", "-y", temp_file],
        # Try with different audio formats
        ["ffmpeg", "-f", "avfoundation", "-i", ":0", "-acodec", "pcm_s16le", "-ar", "16000", "-t", "3", "-y", temp_file],
        # Try with device name
        ["ffmpeg", "-f", "avfoundation", "-i", "Built-in Microphone", "-t", "3", "-y", temp_file],
    ]
    
    for i, cmd in enumerate(ffmpeg_attempts):
        try:
            print(f"Trying FFmpeg approach {i+1}...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                print(f"✅ Recording successful with FFmpeg approach {i+1}!")
                return temp_file
            else:
                print(f"FFmpeg approach {i+1} failed: {result.stderr[:100]}...")
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"FFmpeg approach {i+1} error: {e}")
    
    # Try sox
    try:
        print("Trying with sox...")
        result = subprocess.run([
            "sox", "-d", "-r", "16000", "-c", "1", temp_file, "trim", "0", "3"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
            print("✅ Recording successful with sox!")
            return temp_file
        else:
            print(f"sox failed: {result.stderr}")
            
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"sox error: {e}")
    
    # Try rec (sox's rec command)
    try:
        print("Trying with rec...")
        result = subprocess.run([
            "rec", "-r", "16000", "-c", "1", temp_file, "trim", "0", "3"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
            print("✅ Recording successful with rec!")
            return temp_file
        else:
            print(f"rec failed: {result.stderr}")
            
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"rec error: {e}")
    
    return None


def main():
    """Main function"""
    print("\n" + "="*60)
    print("🎤 Multi-Tool WhisperControl")
    print("="*60)
    print("Trying multiple audio recording methods")
    print("="*60)
    
    try:
        # Load Whisper model
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("✅ Whisper model loaded!")
        
        print("\n🎤 Recording for 3 seconds... Speak now!")
        
        # Record using multiple tools
        temp_file = record_with_multiple_tools()
        
        if not temp_file or not os.path.exists(temp_file):
            print("❌ Could not record audio with any tool")
            print("\nTroubleshooting:")
            print("1. Check System Preferences > Sound > Input")
            print("2. Make sure a microphone is selected")
            print("3. Try: ffmpeg -f avfoundation -list_devices true -i \"\"")
            print("4. Check if another app is using the microphone")
            return
        
        # Check file size
        file_size = os.path.getsize(temp_file)
        print(f"📁 Recorded file size: {file_size} bytes")
        
        if file_size < 1000:  # Less than 1KB is probably empty
            print("❌ Recorded file seems too small - may be empty")
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
