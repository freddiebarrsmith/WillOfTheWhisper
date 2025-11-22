#!/usr/bin/env python3
"""
Simple WhisperControl - Voice prompts for AI assistants
"""

import sys
import os
import time
import logging
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from audio_capture import AudioCapture
from whisper_transcriber import WhisperTranscriber
from system_integration import SystemIntegration
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key


class SimpleWhisperControl:
    """Simple WhisperControl without complex plugins"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = Config()
        
        # Initialize components
        self.audio_capture = AudioCapture(self.config)
        self.whisper_transcriber = WhisperTranscriber(self.config)
        self.system_integration = SystemIntegration(self.config)
        
        # State
        self.is_running = False
        self.current_recording_file = None
        
        # Setup logging
        self._setup_logging()
        
        self.logger.info("Simple WhisperControl initialized")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('whispercontrol.log')
            ]
        )
    
    def start(self):
        """Start WhisperControl"""
        try:
            self.logger.info("Starting Simple WhisperControl...")
            
            # Setup hotkey listener
            self._setup_hotkey_listener()
            
            self.is_running = True
            self.logger.info("Simple WhisperControl started successfully")
            
            # Print usage instructions
            self._print_usage_instructions()
            
            # Keep running
            while self.is_running:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as e:
            self.logger.error(f"Error starting WhisperControl: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop WhisperControl"""
        self.logger.info("Stopping Simple WhisperControl...")
        self.is_running = False
    
    def _setup_hotkey_listener(self):
        """Setup hotkey listener"""
        try:
            # Parse hotkey from config
            hotkey_parts = self.config.hotkey_combination.split('+')
            
            # Convert to pynput keys
            keys = []
            for part in hotkey_parts:
                part = part.strip().lower()
                if part == 'cmd':
                    keys.append(Key.cmd)
                elif part == 'shift':
                    keys.append(Key.shift)
                elif part == 'ctrl':
                    keys.append(Key.ctrl)
                elif part == 'alt':
                    keys.append(Key.alt)
                elif part == '9':
                    keys.append('9')
                else:
                    keys.append(part)
            
            # Create hotkey string for GlobalHotKeys
            hotkey_string = '+'.join(str(k) for k in keys)
            
            # Create listener
            listener = keyboard.GlobalHotKeys({
                hotkey_string: self._on_hotkey_press
            })
            
            listener.start()
            self.logger.info(f"Hotkey listener started for: {self.config.hotkey_combination}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup hotkey listener: {e}")
            # Fallback to simple key listener
            self._setup_simple_listener()
    
    def _setup_simple_listener(self):
        """Setup simple key listener as fallback"""
        try:
            self.logger.info("Setting up simple key listener...")
            
            def on_press(key):
                try:
                    # Check for Shift+9
                    if hasattr(key, 'char') and key.char == '9':
                        # Check if shift is pressed
                        with keyboard.Controller() as controller:
                            if controller.pressed(Key.shift):
                                self._on_hotkey_press()
                except AttributeError:
                    pass
            
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            self.logger.info("Simple key listener started")
            
        except Exception as e:
            self.logger.error(f"Failed to setup simple listener: {e}")
    
    def _on_hotkey_press(self):
        """Handle hotkey press"""
        try:
            self.logger.info("Hotkey pressed - starting recording...")
            
            # Start recording
            self.audio_capture.start_recording()
            
            # Wait for user to release hotkey
            self._wait_for_hotkey_release()
            
            # Stop recording
            self.audio_capture.stop_recording()
            
            # Process the recording
            self._process_recording()
            
        except Exception as e:
            self.logger.error(f"Error handling hotkey: {e}")
    
    def _wait_for_hotkey_release(self):
        """Wait for hotkey to be released"""
        # Simple implementation - wait a bit then stop
        time.sleep(2)  # Record for 2 seconds
    
    def _process_recording(self):
        """Process the recorded audio"""
        try:
            # Save the recording
            self.current_recording_file = self.audio_capture.save_recording()
            
            if not self.current_recording_file:
                self.logger.warning("No recording file saved")
                return
            
            # Transcribe the audio
            self.logger.info("Transcribing audio...")
            transcribed_text = self.whisper_transcriber.transcribe_file(self.current_recording_file)
            
            if transcribed_text:
                self.logger.info(f"Transcribed: {transcribed_text}")
                
                # Simple text processing
                processed_text = self._process_prompt_text(transcribed_text)
                
                # Send to clipboard and paste
                self._send_text(processed_text)
                
                self.logger.info(f"Sent prompt: {processed_text}")
            else:
                self.logger.warning("Empty transcription")
            
            # Clean up
            if self.config.cleanup_temp_files and self.current_recording_file:
                try:
                    os.remove(self.current_recording_file)
                except Exception as e:
                    self.logger.warning(f"Failed to clean up: {e}")
            
        except Exception as e:
            self.logger.error(f"Error processing recording: {e}")
    
    def _process_prompt_text(self, text: str) -> str:
        """Simple prompt text processing"""
        # Remove common filler words
        filler_words = ['um', 'uh', 'like', 'you know', 'i mean', 'actually', 'basically']
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in filler_words]
        
        # Join back together
        processed = ' '.join(filtered_words)
        
        # Ensure it ends with proper punctuation
        if processed and not processed.endswith(('.', '!', '?')):
            processed += '.'
        
        return processed
    
    def _send_text(self, text: str):
        """Send text via clipboard and paste"""
        try:
            # Copy to clipboard
            pyperclip.copy(text)
            
            # Wait a moment
            time.sleep(0.1)
            
            # Paste with Cmd+V
            with keyboard.Controller() as controller:
                controller.press(Key.cmd)
                controller.press('v')
                controller.release('v')
                controller.release(Key.cmd)
            
            self.logger.info("Text sent successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to send text: {e}")
    
    def _print_usage_instructions(self):
        """Print usage instructions"""
        print("\n" + "="*60)
        print("🎤 Simple WhisperControl - Voice Prompts for AI Assistants")
        print("="*60)
        print(f"Hotkey: {self.config.hotkey_combination}")
        print("\nUsage:")
        print("- Hold the hotkey and speak your prompt")
        print("- Release the hotkey to send")
        print("- Example: 'ask how to implement authentication'")
        print("- Example: 'create a React component'")
        print("- Example: 'explain async await'")
        print("\nPress Ctrl+C to stop")
        print("="*60)


def main():
    """Main entry point"""
    try:
        app = SimpleWhisperControl()
        app.start()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
