"""
Audio capture module with hotkey and voice activation support
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time
import os
from pathlib import Path
from typing import Optional, Callable, List
import logging
from pynput import keyboard
import webrtcvad

from config import Config
from noise_filter import NoiseFilter


class AudioCapture:
    """Audio capture with hotkey and voice activation support"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Audio settings
        self.sample_rate = config.audio_sample_rate
        self.channels = config.audio_channels
        self.chunk_size = config.audio_chunk_size
        
        # State management
        self.is_recording = False
        self.is_hotkey_pressed = False
        self.recording_thread: Optional[threading.Thread] = None
        self.audio_data: List[np.ndarray] = []
        self.recording_start_time: Optional[float] = None
        self.pending_audio_chunks: List[np.ndarray] = []  # Store audio before recording starts
        
        # Voice activity detection
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 0-3
        self.voice_detected = False
        self.silence_start_time: Optional[float] = None
        
        # Noise filter to ignore keyboard/mouse clicks
        self.noise_filter = NoiseFilter(self.sample_rate)
        
        # Track consecutive speech frames to avoid triggering on single clicks
        # Increased for mechanical keyboards which can sometimes pass initial filter
        self.consecutive_speech_frames = 0
        self.min_speech_frames = self.config.voice_min_speech_frames  # configurable consecutive frames required
        self.max_pending_chunks = 10  # store ~200-400ms of pre-roll audio
        
        # Callbacks
        self.on_recording_start: Optional[Callable] = None
        self.on_recording_stop: Optional[Callable] = None
        self.on_audio_data: Optional[Callable] = None
        
        # Hotkey listener
        self.hotkey_listener: Optional[keyboard.Listener] = None
        
        # Continuous voice monitoring (for voice-only mode)
        self.voice_monitoring_thread: Optional[threading.Thread] = None
        self.voice_monitoring_active = False
        self.monitoring_stream: Optional[sd.InputStream] = None
        
        # Ensure temp directory exists
        Path(config.temp_dir).mkdir(exist_ok=True)
    
    def start(self) -> None:
        """Start the audio capture system"""
        self.logger.info("Starting audio capture system")
        
        # Start hotkey listener if enabled
        if self.config.hotkey_enabled and self.config.activation_mode in ['hotkey', 'both']:
            self._start_hotkey_listener()
        
        # Start voice activation if enabled
        if self.config.voice_enabled and self.config.activation_mode in ['voice', 'both']:
            self._start_voice_monitoring()
    
    def stop(self) -> None:
        """Stop the audio capture system"""
        self.logger.info("Stopping audio capture system")
        
        # Stop any ongoing recording
        if self.is_recording:
            self.stop_recording()
        
        # Stop hotkey listener
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        # Stop voice monitoring
        self._stop_voice_monitoring()
    
    def _start_hotkey_listener(self) -> None:
        """Start listening for hotkey presses"""
        try:
            # Parse hotkey combination
            key_combo = self._parse_hotkey_combination(self.config.hotkey_combination)
            
            # Create hotkey listener
            self.hotkey_listener = keyboard.GlobalHotKeys({
                key_combo: self._on_hotkey_press
            })
            self.hotkey_listener.start()
            
            self.logger.info(f"Hotkey listener started: {self.config.hotkey_combination}")
            
        except Exception as e:
            self.logger.error(f"Failed to start hotkey listener: {e}")
    
    def _parse_hotkey_combination(self, combo: str) -> str:
        """Parse hotkey combination string to pynput format"""
        # Convert common formats to pynput format
        combo = combo.lower().replace('cmd', '<cmd>').replace('ctrl', '<ctrl>')
        combo = combo.replace('alt', '<alt>').replace('shift', '<shift>')
        combo = combo.replace('space', ' ')
        return combo
    
    def _on_hotkey_press(self) -> None:
        """Handle hotkey press"""
        if self.config.hotkey_mode == 'push_to_talk':
            if not self.is_recording:
                self.start_recording()
            else:
                self.stop_recording()
        elif self.config.hotkey_mode == 'toggle':
            if not self.is_recording:
                self.start_recording()
            else:
                self.stop_recording()
    
    def _start_voice_monitoring(self) -> None:
        """Start continuous voice activity monitoring"""
        if self.voice_monitoring_active:
            return
        
        self.logger.info("Starting continuous voice activity monitoring")
        self.voice_monitoring_active = True
        
        # Start monitoring thread
        self.voice_monitoring_thread = threading.Thread(
            target=self._voice_monitoring_loop,
            daemon=True
        )
        self.voice_monitoring_thread.start()
    
    def _stop_voice_monitoring(self) -> None:
        """Stop voice activity monitoring"""
        self.logger.info("Stopping voice activity monitoring")
        self.voice_monitoring_active = False
        
        # Stop monitoring stream
        if self.monitoring_stream:
            try:
                self.monitoring_stream.stop()
                self.monitoring_stream.close()
            except Exception as e:
                self.logger.warning(f"Error stopping monitoring stream: {e}")
            finally:
                self.monitoring_stream = None
        
        # Wait for thread to finish
        if self.voice_monitoring_thread:
            self.voice_monitoring_thread.join(timeout=1.0)
    
    def _voice_monitoring_loop(self) -> None:
        """Continuous voice monitoring loop - listens for voice even when not recording"""
        try:
            self.logger.info("Voice monitoring loop started - listening for speech...")
            
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.chunk_size,
                callback=self._monitoring_callback
            ) as stream:
                self.monitoring_stream = stream
                
                while self.voice_monitoring_active:
                    time.sleep(0.1)
                    
        except Exception as e:
            self.logger.error(f"Error in voice monitoring loop: {e}")
            self.voice_monitoring_active = False
    
    def _monitoring_callback(self, indata, frames, time, status) -> None:
        """Callback for continuous voice monitoring"""
        if status:
            self.logger.warning(f"Monitoring callback status: {status}")
        
        # Only monitor if not already recording (to avoid conflicts)
        if not self.is_recording:
            self._detect_voice_activity_for_monitoring(indata)
    
    def start_recording(self) -> None:
        """Start recording audio"""
        if self.is_recording:
            return
        
        self.logger.info("Starting audio recording")
        self.is_recording = True
        
        # IMPORTANT: Add pending audio chunks first to capture the words that triggered recording
        if self.pending_audio_chunks:
            self.audio_data = self.pending_audio_chunks.copy()  # Start with pre-captured audio
            self.logger.debug(f"Added {len(self.pending_audio_chunks)} pending audio chunks to capture first words")
            self.pending_audio_chunks = []  # Clear pending chunks
        else:
            self.audio_data = []  # Clear any previous data
        
        self.recording_start_time = time.time()
        self.voice_detected = True  # Mark that we've detected voice
        self.silence_start_time = None  # Reset silence timer
        
        # No delay - start recording thread immediately
        # Start recording thread
        self.recording_thread = threading.Thread(target=self._recording_loop)
        self.recording_thread.start()
        
        # Notify callback
        if self.on_recording_start:
            self.on_recording_start()
    
    def stop_recording(self) -> None:
        """Stop recording audio"""
        if not self.is_recording:
            return
        
        self.logger.info("Stopping audio recording")
        self.is_recording = False
        
        # Wait for recording thread to finish (but don't join from within the thread itself)
        if self.recording_thread and self.recording_thread.is_alive():
            # Check if we're calling from within the recording thread
            if threading.current_thread() != self.recording_thread:
                try:
                    self.recording_thread.join(timeout=1.0)
                except RuntimeError as e:
                    # Can't join current thread - that's okay, it will finish naturally
                    self.logger.debug(f"Could not join recording thread: {e}")
        
        # Reset voice detection state for next monitoring cycle
        self.voice_detected = False
        self.silence_start_time = None
        self.consecutive_speech_frames = 0
        
        # Notify callback
        if self.on_recording_stop:
            self.on_recording_stop()
    
    def _recording_loop(self) -> None:
        """Main recording loop"""
        try:
            self.logger.debug(f"Starting recording loop: sample_rate={self.sample_rate}, channels={self.channels}, chunk_size={self.chunk_size}")
            
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.chunk_size,
                callback=self._audio_callback
            ) as stream:
                self.logger.debug("Audio stream opened successfully")
                
                # No delay - stream starts capturing immediately
                # Audio callback is already active, no need to wait
                
                while self.is_recording:
                    time.sleep(0.1)
                    
                    # Check for maximum recording duration
                    if (self.recording_start_time and 
                        time.time() - self.recording_start_time > self.config.max_recording_duration):
                        self.logger.warning("Maximum recording duration reached")
                        self.is_recording = False
                        break
                    
                    # Voice activation logic is now handled by continuous monitoring
                    # No need to check here anymore
                
                self.logger.debug(f"Recording loop ended. Collected {len(self.audio_data)} audio chunks")
            
            # Recording loop ended - notify callback if we were recording
            if not self.is_recording and self.recording_start_time:
                # Log how much data we collected
                total_samples = sum(len(chunk) for chunk in self.audio_data) if self.audio_data else 0
                duration = total_samples / self.sample_rate if total_samples > 0 else 0
                self.logger.info(f"Recording stopped. Collected {len(self.audio_data)} chunks, {duration:.2f}s of audio")
                
                # Reset state
                self.voice_detected = False
                self.silence_start_time = None
                self.consecutive_speech_frames = 0
                
                # Notify callback (but don't call stop_recording to avoid thread join issues)
                if self.on_recording_stop:
                    self.on_recording_stop()
        
        except Exception as e:
            self.logger.error(f"Error in recording loop: {e}", exc_info=True)
            self.is_recording = False
            # Reset state
            self.voice_detected = False
            self.silence_start_time = None
            self.consecutive_speech_frames = 0
            # Notify callback
            if self.on_recording_stop:
                self.on_recording_stop()
    
    def _audio_callback(self, indata, frames, time, status) -> None:
        """Callback for audio input"""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        
        if self.is_recording:
            # Store audio data - ensure we have valid data
            if indata is not None and len(indata) > 0:
                self.audio_data.append(indata.copy())
            else:
                self.logger.debug("Received empty audio chunk in callback")
            
            # Voice activity detection
            if self.config.voice_enabled:
                self._detect_voice_activity(indata)
            
            # Notify callback with audio data
            if self.on_audio_data:
                self.on_audio_data(indata)
    
    def _detect_voice_activity(self, audio_chunk: np.ndarray) -> None:
        """Detect voice activity in audio chunk (when recording)"""
        try:
            # Convert to 16-bit PCM for VAD
            audio_int16 = (audio_chunk * 32767).astype(np.int16)
            
            # VAD expects 10ms, 20ms, or 30ms frames
            frame_duration_ms = 20
            frame_size = int(self.sample_rate * frame_duration_ms / 1000)
            
            if len(audio_int16) >= frame_size:
                # Take first frame for VAD
                frame = audio_int16[:frame_size]
                
                # Detect voice activity
                is_speech = self.vad.is_speech(frame.tobytes(), self.sample_rate)
                
                current_time = time.time()
                
                if is_speech:
                    self.voice_detected = True
                    self.silence_start_time = None
                else:
                    if self.voice_detected:
                        if self.silence_start_time is None:
                            self.silence_start_time = current_time
                        elif (current_time - self.silence_start_time > 
                              self.config.voice_silence_timeout):
                            # Silence timeout reached, stop recording
                            self.logger.info("Silence timeout reached, stopping recording")
                            self.stop_recording()
        
        except Exception as e:
            self.logger.error(f"Error in voice activity detection: {e}")
    
    def _detect_voice_activity_for_monitoring(self, audio_chunk: np.ndarray) -> None:
        """Detect voice activity for continuous monitoring (when not recording)"""
        try:
            # Skip if already recording (shouldn't happen, but safety check)
            if self.is_recording:
                return
            
            # Store audio chunks before recording starts to avoid missing first words
            # Keep last 5 chunks (about 200-300ms of audio) to capture the trigger
            self.pending_audio_chunks.append(audio_chunk.copy())
            if len(self.pending_audio_chunks) > self.max_pending_chunks:
                self.pending_audio_chunks.pop(0)  # Remove oldest
            
            # First, filter out keyboard/mouse clicks and other noise
            filtered_chunk, is_noise = self.noise_filter.filter_audio(audio_chunk)
            
            if is_noise:
                # This is a click or noise, ignore it and reset speech counter
                self.consecutive_speech_frames = 0
                self.logger.debug("Ignoring click/noise sound")
                return
            
            # Convert to 16-bit PCM for VAD
            audio_int16 = (filtered_chunk * 32767).astype(np.int16)
            
            # VAD expects 10ms, 20ms, or 30ms frames
            frame_duration_ms = 20
            frame_size = int(self.sample_rate * frame_duration_ms / 1000)
            
            if len(audio_int16) >= frame_size:
                # Take first frame for VAD
                frame = audio_int16[:frame_size]
                
                # Detect voice activity
                is_speech = self.vad.is_speech(frame.tobytes(), self.sample_rate)
                
                if is_speech:
                    # Increment consecutive speech frames
                    self.consecutive_speech_frames += 1
                    
                    # Only start recording if we have sustained speech (not just a click)
                    if self.consecutive_speech_frames >= self.min_speech_frames:
                        # Voice detected and we're not recording - start recording!
                        self.logger.info("Voice detected - starting recording")
                        self.consecutive_speech_frames = 0  # Reset counter
                        self.start_recording()
                else:
                    # Not speech, reset counter
                    self.consecutive_speech_frames = 0
        
        except Exception as e:
            self.logger.error(f"Error in voice monitoring detection: {e}")
            self.consecutive_speech_frames = 0
    
    def _handle_voice_activation(self) -> None:
        """Handle voice activation logic (legacy - now handled by monitoring callback)"""
        # This is now handled by _detect_voice_activity_for_monitoring
        pass
    
    def save_recording(self, filename: Optional[str] = None) -> str:
        """Save recorded audio to file"""
        if not self.audio_data:
            raise ValueError("No audio data to save")
        
        if filename is None:
            timestamp = int(time.time())
            filename = f"recording_{timestamp}.wav"
        
        filepath = Path(self.config.temp_dir) / filename
        
        # Concatenate all audio chunks
        full_audio = np.concatenate(self.audio_data, axis=0)
        
        # Check if audio has actual content (not just silence)
        audio_energy = np.mean(full_audio ** 2)
        self.logger.debug(f"Audio energy: {audio_energy:.6f}, Duration: {len(full_audio) / self.sample_rate:.2f}s")
        
        if audio_energy < 1e-6:
            self.logger.warning("Recording appears to be mostly silence")
        
        # Save as WAV file
        sf.write(filepath, full_audio, self.sample_rate)
        
        self.logger.info(f"Saved recording to {filepath} ({len(full_audio) / self.sample_rate:.2f}s, energy: {audio_energy:.6f})")
        return str(filepath)
    
    def get_recording_duration(self) -> float:
        """Get the duration of the current recording"""
        if not self.recording_start_time:
            return 0.0
        
        return time.time() - self.recording_start_time
    
    def clear_recording(self) -> None:
        """Clear current recording data"""
        self.audio_data = []
        self.recording_start_time = None
        self.voice_detected = False
        self.silence_start_time = None
