"""
Main application for WhisperControl
"""

import logging
import sys
import time
import threading
from pathlib import Path
from typing import Optional
import os
import numpy as np

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from audio_capture import AudioCapture
from whisper_transcriber import WhisperTranscriber
from system_integration import SystemIntegration
from app_detector import AppDetector
from plugins import PluginManager
from audio_preprocessor import AudioPreprocessor
from code_processor import CodeTerminologyProcessor, CodeContext
from voice_commands import VoiceCommandProcessor
from performance_monitor import PerformanceMonitor
from prompt_processor import PromptVoiceProcessor
from prompt_text_processor import PromptTextProcessor


class WhisperControl:
    """Main WhisperControl application"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = Config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize components
        self.audio_capture = AudioCapture(self.config)
        self.whisper_transcriber = WhisperTranscriber(self.config)
        self.system_integration = SystemIntegration(self.config)
        self.app_detector = AppDetector()
        self.plugin_manager = PluginManager(self.config.ai_assistants_config)
        
        # Enhanced components
        self.audio_preprocessor = AudioPreprocessor(self.config.audio_sample_rate)
        self.code_processor = CodeTerminologyProcessor()
        self.voice_command_processor = VoiceCommandProcessor()
        self.performance_monitor = PerformanceMonitor(self.config.ai_assistants_config)
        
        # Prompt-focused components
        self.prompt_voice_processor = PromptVoiceProcessor()
        self.prompt_text_processor = PromptTextProcessor()
        
        # State
        self.is_running = False
        self.current_recording_file: Optional[str] = None
        
        # Setup callbacks
        self._setup_callbacks()
        
        self.logger.info("WhisperControl initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        # Create logs directory
        Path(self.config.log_dir).mkdir(exist_ok=True)
        
        # Setup logger
        logger = logging.getLogger("whispercontrol")
        logger.setLevel(getattr(logging, self.config.log_level))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        log_file = Path(self.config.log_dir) / "whispercontrol.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _setup_callbacks(self) -> None:
        """Setup callbacks for audio capture"""
        self.audio_capture.on_recording_start = self._on_recording_start
        self.audio_capture.on_recording_stop = self._on_recording_stop
        self.audio_capture.on_audio_data = self._on_audio_data
    
    def _on_recording_start(self) -> None:
        """Callback when recording starts"""
        self.logger.info("Recording started")
        
        # Play start sound if enabled
        if self.config.audio_notification:
            self._play_notification_sound("start")
        
        # Show notification if enabled
        if self.config.visual_notification:
            self._show_notification("Recording started", "Speak now...")
    
    def _on_recording_stop(self) -> None:
        """Callback when recording stops"""
        self.logger.info("Recording stopped")
        
        # Play stop sound if enabled
        if self.config.audio_notification:
            self._play_notification_sound("stop")
        
        # Process the recording
        self._process_recording()
    
    def _on_audio_data(self, audio_data) -> None:
        """Callback for audio data (for real-time processing if needed)"""
        # This could be used for real-time audio analysis
        pass
    
    def _play_notification_sound(self, sound_type: str) -> None:
        """Play notification sound - gentle, less irritating sounds"""
        try:
            # Check if sounds are enabled in config
            if not self.config.audio_notification:
                return
            
            if sound_type == "start":
                # Gentle start sound - use Purr
                os.system("afplay -v 0.2 /System/Library/Sounds/Purr.aiff 2>/dev/null")
            elif sound_type == "stop":
                # Gentle stop sound - use Purr
                os.system("afplay -v 0.2 /System/Library/Sounds/Purr.aiff 2>/dev/null")
            elif sound_type == "error":
                # Gentle error sound - quieter Basso
                os.system("afplay -v 0.15 /System/Library/Sounds/Basso.aiff 2>/dev/null")
        except Exception:
            # Silently fail - don't log sound errors
            pass
    
    def _show_notification(self, title: str, message: str) -> None:
        """Show system notification"""
        try:
            os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
        except Exception as e:
            self.logger.warning(f"Failed to show notification: {e}")
    
    def _process_recording(self) -> None:
        """Process the recorded audio with enhanced features"""
        try:
            # Start performance monitoring
            start_time = time.time()
            
            # Check if there's audio data before trying to save
            if not self.audio_capture.audio_data or len(self.audio_capture.audio_data) == 0:
                self.logger.warning("No audio data collected - recording may have been too short")
                self._show_notification("Recording Error", "No audio data captured. Try speaking longer.")
                return
            
            # Save the recording
            try:
                self.current_recording_file = self.audio_capture.save_recording()
            except ValueError as e:
                self.logger.error(f"Error saving recording: {e}")
                self._show_notification("Recording Error", "No audio data to save")
                return
            
            # Enhanced audio preprocessing
            self.logger.info("Preprocessing audio...")
            audio_data = self._load_and_preprocess_audio()
            
            # Check if file exists and has content
            if not os.path.exists(self.current_recording_file):
                self.logger.error(f"Recording file not found: {self.current_recording_file}")
                self._show_notification("Error", "Recording file not found")
                return
            
            file_size = os.path.getsize(self.current_recording_file)
            if file_size < 1000:  # Less than 1KB is likely empty/corrupt
                self.logger.warning(f"Recording file is very small ({file_size} bytes), may be empty")
            
            # Transcribe the audio
            self.logger.info("Transcribing audio...")
            transcribed_text = self.whisper_transcriber.transcribe_file(self.current_recording_file)
            
            # Clean up whitespace-only transcriptions
            if transcribed_text:
                transcribed_text = transcribed_text.strip()
            
            if transcribed_text and len(transcribed_text) > 0:
                self.logger.info(f"Raw transcription: {transcribed_text}")
                
                # Process with prompt-focused voice commands first
                processed_text = self.prompt_voice_processor.process_command(transcribed_text)
                
                # Get current app info for context
                app_info = self.app_detector.get_active_app_info()
                assistant_type = self._detect_assistant_type(app_info)
                
                # Apply prompt-specific text processing
                final_text = self.prompt_text_processor.enhance_for_ai_assistant(processed_text, assistant_type)
                
                self.logger.info(f"Final processed prompt: {final_text}")
                
                self.logger.info(f"Active app: {app_info['name']} - {app_info['title']}")
                
                # Use plugin system to send text
                success = self._send_text_with_plugins(final_text, app_info)
                
                if success:
                    self._show_notification("Prompt Sent", f"'{final_text[:50]}...'")
                else:
                    self._show_notification("Error", "Failed to send prompt")
                    self._play_notification_sound("error")
            else:
                self.logger.warning("Empty transcription")
                self._show_notification("No Speech Detected", "Please try again")
                self._play_notification_sound("error")
            
            # Clean up temporary file
            if self.config.cleanup_temp_files and self.current_recording_file:
                try:
                    os.remove(self.current_recording_file)
                    self.logger.debug(f"Cleaned up temporary file: {self.current_recording_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to clean up temporary file: {e}")
            
            # Record performance metrics
            total_time = time.time() - start_time
            self.performance_monitor._record_success("recording_processing", total_time)
            self.logger.info(f"Recording processing completed in {total_time:.2f}s")
        
        except Exception as e:
            self.logger.error(f"Error processing recording: {e}")
            self.performance_monitor._record_error("recording_processing", str(e))
            self._show_notification("Error", f"Processing failed: {str(e)}")
            self._play_notification_sound("error")
    
    def _load_and_preprocess_audio(self) -> np.ndarray:
        """Load and preprocess audio for better transcription"""
        try:
            import soundfile as sf
            import numpy as np
            
            # Load audio file
            audio_data, sample_rate = sf.read(self.current_recording_file)
            
            # Preprocess audio
            enhanced_audio = self.audio_preprocessor.enhance_for_whisper(audio_data)
            
            # Save enhanced audio
            enhanced_file = self.current_recording_file.replace('.wav', '_enhanced.wav')
            sf.write(enhanced_file, enhanced_audio, 16000)
            
            # Update recording file to use enhanced version
            self.current_recording_file = enhanced_file
            
            return enhanced_audio
            
        except Exception as e:
            self.logger.warning(f"Audio preprocessing failed: {e}")
            return None
    
    def _detect_assistant_type(self, app_info: dict) -> str:
        """Detect the type of AI assistant"""
        app_name = app_info.get('name', '').lower()
        window_title = app_info.get('title', '').lower()
        
        if 'cursor' in app_name or 'cursor' in window_title:
            return 'cursor'
        elif 'qwen' in app_name or 'tongyi' in app_name or 'qwen' in window_title:
            return 'qwen'
        elif 'visual studio code' in app_name or 'code' in app_name:
            return 'roo'
        else:
            return 'general'
    
    def _send_text_with_plugins(self, text: str, app_info: dict) -> bool:
        """Send text using the plugin system"""
        try:
            # Use plugin manager to find appropriate handler
            if self.config.use_smart_detection:
                success = self.plugin_manager.send_text(text, app_info)
                if success:
                    return True
            
            # Fallback to generic handler if enabled
            if self.config.fallback_to_generic:
                self.logger.info("Using fallback generic handler")
                return self.system_integration.process_transcribed_text(text)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Plugin system failed: {e}")
            # Fallback to original system integration
            return self.system_integration.process_transcribed_text(text)
    
    def start(self) -> None:
        """Start the WhisperControl application"""
        if self.is_running:
            self.logger.warning("Application is already running")
            return
        
        self.logger.info("Starting WhisperControl...")
        
        try:
            # Start audio capture
            self.audio_capture.start()
            
            self.is_running = True
            
            self.logger.info("WhisperControl started successfully")
            self._show_notification("WhisperControl", "Started successfully")
            
            # Print usage instructions
            self._print_usage_instructions()
            
        except Exception as e:
            self.logger.error(f"Failed to start WhisperControl: {e}")
            raise
    
    def stop(self) -> None:
        """Stop the WhisperControl application"""
        if not self.is_running:
            return
        
        self.logger.info("Stopping WhisperControl...")
        
        try:
            # Stop audio capture
            self.audio_capture.stop()
            
            # Cleanup whisper model
            self.whisper_transcriber.cleanup()
            
            self.is_running = False
            
            self.logger.info("WhisperControl stopped")
            self._show_notification("WhisperControl", "Stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping WhisperControl: {e}")
    
    def _print_usage_instructions(self) -> None:
        """Print usage instructions"""
        print("\n" + "="*60)
        print("WhisperControl - Extensible Voice Dictation Tool")
        print("="*60)
        
        if self.config.activation_mode in ['hotkey', 'both']:
            print(f"Hotkey: {self.config.hotkey_combination}")
            print(f"Mode: {self.config.hotkey_mode}")
        
        if self.config.activation_mode in ['voice', 'both']:
            print("Voice activation: Enabled")
            print(f"Silence timeout: {self.config.voice_silence_timeout}s")
        
        print(f"Whisper model: {self.config.whisper_model}")
        print(f"Smart detection: {'Enabled' if self.config.use_smart_detection else 'Disabled'}")
        
        # Show available handlers
        handlers = self.plugin_manager.get_available_handlers()
        print(f"\nAvailable AI Assistant Handlers:")
        for handler in handlers:
            print(f"  - {handler['name']} (Priority: {handler['priority']})")
        
        print("\nSupported Applications:")
        print("  - VS Code with Roo extension")
        print("  - Cursor IDE")
        print("  - Qwen Code")
        print("  - Any application (generic handler)")
        
        print("\nPrompt-Focused Features:")
        print("  - Optimized for AI assistant prompts")
        print("  - Natural language processing for better prompts")
        print("  - Context-aware prompt enhancement")
        print("  - Assistant-specific prompt optimization")
        print("  - Advanced audio preprocessing for conversational speech")
        
        print("\nUsage:")
        print("- Press and hold the hotkey to record")
        print("- Speak your prompt naturally")
        print("- Release the hotkey to send to AI assistant")
        print("- Say 'ask how to implement authentication'")
        print("- Say 'create a React component'")
        print("- Say 'explain async await'")
        print("- Say 'help me debug this error'")
        print("- Automatically optimizes prompts for each AI assistant")
        print("\nPerformance Monitoring:")
        print("- Real-time performance tracking")
        print("- Automatic optimization")
        print("- Performance reports available")
        print("\nPress Ctrl+C to stop")
        print("="*60 + "\n")
    
    def run(self) -> None:
        """Run the application (blocking)"""
        try:
            self.start()
            
            # Keep running until interrupted
            while self.is_running:
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.stop()


def main():
    """Main entry point"""
    try:
        app = WhisperControl()
        app.run()
    except Exception as e:
        print(f"Failed to start WhisperControl: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
