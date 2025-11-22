#!/usr/bin/env python3
"""
WhisperControl - Right-Click to Record & Auto-Paste Version
"""

import sys
import os
import time
import logging
import whisper
import subprocess
import tempfile
import pyperclip
import threading
from pynput import mouse
from pynput.mouse import Button, Listener
import pyautogui


class WhisperControl:
    def __init__(self):
        self.model = None
        self.is_recording = False
        self.recording_thread = None
        self.temp_file = None
        self.listener = None
        
    def load_model(self):
        """Load Whisper model"""
        print("Loading Whisper model...")
        self.model = whisper.load_model("small")
        print("✅ Whisper model loaded!")
        
    def start_recording(self):
        """Start recording audio"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.temp_file = tempfile.mktemp(suffix=".wav")
        
        print("🎤 Recording... (Right-click again to stop)")
        
        # Start recording in background
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.start()
        
    def stop_recording(self):
        """Stop recording and process"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join(timeout=2)
            
        print("✅ Processing...")
        
        # Process the recording
        self._process_recording()
        
    def _record_audio(self):
        """Record audio in background thread"""
        try:
            # Continuous recording until stopped
            result = subprocess.run([
                "ffmpeg", "-f", "avfoundation", "-i", ":0", 
                "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                "-af", "highpass=f=80,lowpass=f=8000,volume=1.5",
                "-y", self.temp_file
            ], capture_output=True, text=True, timeout=30)
            
        except Exception as e:
            print(f"❌ Recording error: {e}")
            
    def _process_recording(self):
        """Process the recorded audio"""
        try:
            if not os.path.exists(self.temp_file):
                print("❌ No recording file found")
                return
                
            file_size = os.path.getsize(self.temp_file)
            if file_size < 1000:  # Less than 1KB
                print("❌ Recording too short")
                return
                
            print(f"✅ Recording size: {file_size} bytes")
            print("✅ Transcribing...")
            
            # Transcribe
            result = self.model.transcribe(self.temp_file, language='en', fp16=False)
            transcribed_text = result["text"].strip()
            
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
                
                print(f"📝 Transcribed: '{transcribed_text}'")
                print(f"✅ Processed: '{processed}'")
                print("✅ Auto-pasting and pressing Enter...")
                
                # Auto-paste and press Enter
                pyautogui.hotkey('cmd', 'v')  # Paste
                time.sleep(0.1)
                pyautogui.press('enter')  # Press Enter
                
                print("🎉 Done! Ready for next recording.")
            else:
                print("❌ No speech detected")
                print("💡 Try speaking louder or more clearly")
                
        except Exception as e:
            print(f"❌ Processing error: {e}")
        finally:
            # Clean up
            try:
                if self.temp_file and os.path.exists(self.temp_file):
                    os.remove(self.temp_file)
            except:
                pass
                
    def on_click(self, x, y, button, pressed):
        """Handle mouse clicks"""
        if button == Button.right and pressed:
            if not self.is_recording:
                self.start_recording()
            else:
                self.stop_recording()
                
    def start(self):
        """Start the WhisperControl system"""
        print("\n" + "="*60)
        print("🎉 WhisperControl - Right-Click Version!")
        print("="*60)
        print("✅ Right-click to start recording")
        print("✅ Right-click again to stop & auto-paste")
        print("✅ No more 'call ended' messages!")
        print("="*60)
        
        # Load model
        self.load_model()
        
        print("\n🎤 Ready! Right-click to start recording...")
        print("📢 Speak your prompt, then right-click again to stop")
        print("🔄 The text will be automatically pasted and Enter pressed")
        print("\nPress Ctrl+C to quit")
        
        # Start mouse listener
        self.listener = Listener(on_click=self.on_click)
        self.listener.start()
        
        try:
            # Keep running
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nGoodbye!")
        finally:
            if self.listener:
                self.listener.stop()


def main():
    """Main function"""
    try:
        whisper_control = WhisperControl()
        whisper_control.start()
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
