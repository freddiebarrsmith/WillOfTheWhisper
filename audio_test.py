#!/usr/bin/env python3
"""
Audio Level Test - Check if microphone is picking up sound
"""

import subprocess
import tempfile
import os
import time


def test_audio_levels():
    """Test if microphone is picking up sound"""
    print("\n" + "="*60)
    print("🎤 Audio Level Test")
    print("="*60)
    print("This will test if your Bose headset is picking up sound")
    print("="*60)
    
    temp_file = tempfile.mktemp(suffix=".wav")
    
    print("🎤 Recording for 3 seconds...")
    print("📢 SPEAK INTO YOUR BOSE HEADSET NOW!")
    print("   Say: 'Hello, this is a test'")
    
    try:
        # Record with higher quality settings
        result = subprocess.run([
            "ffmpeg", "-f", "avfoundation", "-i", ":0", 
            "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-af", "volume=2.0",  # Boost volume
            "-t", "3", "-y", temp_file
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists(temp_file):
            file_size = os.path.getsize(temp_file)
            print(f"✅ Recording successful! File size: {file_size} bytes")
            
            # Test with Whisper
            print("🔍 Testing with Whisper...")
            whisper_result = subprocess.run([
                "python", "-c", 
                f"""
import whisper
model = whisper.load_model('base')
result = model.transcribe('{temp_file}')
print('Raw transcription:', repr(result['text']))
print('Cleaned transcription:', result['text'].strip())
"""
            ], capture_output=True, text=True, timeout=30)
            
            print("Whisper output:")
            print(whisper_result.stdout)
            if whisper_result.stderr:
                print("Whisper errors:")
                print(whisper_result.stderr)
            
            # Check if we got any transcription
            if whisper_result.stdout and "Cleaned transcription:" in whisper_result.stdout:
                transcription_line = [line for line in whisper_result.stdout.split('\n') if 'Cleaned transcription:' in line][0]
                transcription = transcription_line.split('Cleaned transcription: ')[1]
                
                if transcription.strip():
                    print(f"🎉 SUCCESS! Whisper detected: '{transcription}'")
                    return True
                else:
                    print("❌ Whisper detected no speech")
            else:
                print("❌ Whisper failed to process audio")
            
        else:
            print(f"❌ Recording failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Clean up
        try:
            os.remove(temp_file)
        except:
            pass
    
    return False


def main():
    """Main function"""
    success = test_audio_levels()
    
    print("\n" + "="*60)
    if success:
        print("🎉 AUDIO IS WORKING!")
        print("Your Bose headset is picking up speech correctly.")
        print("WhisperControl should work perfectly now!")
    else:
        print("❌ AUDIO ISSUES DETECTED")
        print("\nTroubleshooting:")
        print("1. Check System Preferences > Sound > Input")
        print("   - Make sure 'Bose QC Ultra Headphones' is selected")
        print("   - Check input level - should show activity when you speak")
        print("2. Try speaking louder or closer to the microphone")
        print("3. Check if microphone is muted on the headset")
        print("4. Try disconnecting and reconnecting the headset")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
