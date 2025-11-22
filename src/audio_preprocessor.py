"""
Enhanced audio preprocessing and noise reduction
"""

import numpy as np
import scipy.signal
import logging
from typing import Tuple, Optional
import soundfile as sf
from pathlib import Path


class AudioPreprocessor:
    """Advanced audio preprocessing for better transcription quality"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.logger = logging.getLogger(__name__)
        
        # Audio enhancement parameters
        self.noise_gate_threshold = 0.01
        self.compression_ratio = 3.0
        self.high_pass_freq = 80.0
        self.low_pass_freq = 8000.0
        
        # Initialize filters
        self._init_filters()
    
    def _init_filters(self) -> None:
        """Initialize audio filters"""
        # High-pass filter to remove low-frequency noise
        self.high_pass_filter = self._create_high_pass_filter(
            self.high_pass_freq, self.sample_rate
        )
        
        # Low-pass filter to remove high-frequency noise
        self.low_pass_filter = self._create_low_pass_filter(
            self.low_pass_freq, self.sample_rate
        )
        
        # Band-pass filter for voice frequency range
        self.band_pass_filter = self._create_band_pass_filter(
            300.0, 3400.0, self.sample_rate
        )
    
    def _create_high_pass_filter(self, freq: float, sample_rate: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create high-pass Butterworth filter"""
        nyquist = sample_rate / 2
        normalized_freq = freq / nyquist
        
        # Ensure normalized frequency is valid
        if normalized_freq <= 0 or normalized_freq >= 1:
            normalized_freq = 0.01  # Default to 1% of Nyquist frequency
        
        return scipy.signal.butter(4, normalized_freq, btype='high')
    
    def _create_low_pass_filter(self, freq: float, sample_rate: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create low-pass Butterworth filter"""
        nyquist = sample_rate / 2
        normalized_freq = freq / nyquist
        
        # Ensure normalized frequency is valid
        if normalized_freq <= 0 or normalized_freq >= 1:
            normalized_freq = 0.99  # Default to 99% of Nyquist frequency
        
        return scipy.signal.butter(4, normalized_freq, btype='low')
    
    def _create_band_pass_filter(self, low_freq: float, high_freq: float, sample_rate: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create band-pass Butterworth filter"""
        nyquist = sample_rate / 2
        low_norm = low_freq / nyquist
        high_norm = high_freq / nyquist
        
        # Ensure normalized frequencies are valid
        if low_norm <= 0 or low_norm >= 1 or high_norm <= 0 or high_norm >= 1 or low_norm >= high_norm:
            # Fallback to simple high-pass filter
            return self._create_high_pass_filter(300.0, sample_rate)
        
        return scipy.signal.butter(4, [low_norm, high_norm], btype='band')
    
    def preprocess_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply comprehensive audio preprocessing"""
        try:
            # Ensure audio is mono
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Normalize audio
            audio_data = self._normalize_audio(audio_data)
            
            # Apply noise gate
            audio_data = self._apply_noise_gate(audio_data)
            
            # Apply band-pass filter for voice frequencies
            audio_data = self._apply_filter(audio_data, self.band_pass_filter)
            
            # Apply dynamic range compression
            audio_data = self._apply_compression(audio_data)
            
            # Apply spectral subtraction for noise reduction
            audio_data = self._apply_spectral_subtraction(audio_data)
            
            # Final normalization
            audio_data = self._normalize_audio(audio_data)
            
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Audio preprocessing failed: {e}")
            return audio_data
    
    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio to prevent clipping"""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val * 0.95
        return audio_data
    
    def _apply_noise_gate(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply noise gate to remove background noise"""
        gate_mask = np.abs(audio_data) > self.noise_gate_threshold
        return audio_data * gate_mask
    
    def _apply_filter(self, audio_data: np.ndarray, filter_coeffs: Tuple[np.ndarray, np.ndarray]) -> np.ndarray:
        """Apply Butterworth filter"""
        try:
            b, a = filter_coeffs
            return scipy.signal.filtfilt(b, a, audio_data)
        except Exception as e:
            self.logger.debug(f"Filter application failed: {e}")
            return audio_data
    
    def _apply_compression(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply dynamic range compression"""
        # Simple compression algorithm
        threshold = 0.3
        compressed = np.copy(audio_data)
        
        # Compress signals above threshold
        above_threshold = np.abs(compressed) > threshold
        compressed[above_threshold] = np.sign(compressed[above_threshold]) * (
            threshold + (np.abs(compressed[above_threshold]) - threshold) / self.compression_ratio
        )
        
        return compressed
    
    def _apply_spectral_subtraction(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply spectral subtraction for noise reduction"""
        try:
            # Simple spectral subtraction
            fft = np.fft.fft(audio_data)
            magnitude = np.abs(fft)
            phase = np.angle(fft)
            
            # Estimate noise floor (simple approach)
            noise_floor = np.percentile(magnitude, 20)
            
            # Apply spectral subtraction
            enhanced_magnitude = np.maximum(
                magnitude - noise_floor * 0.5,
                magnitude * 0.1
            )
            
            # Reconstruct signal
            enhanced_fft = enhanced_magnitude * np.exp(1j * phase)
            enhanced_audio = np.real(np.fft.ifft(enhanced_fft))
            
            return enhanced_audio
            
        except Exception as e:
            self.logger.debug(f"Spectral subtraction failed: {e}")
            return audio_data
    
    def detect_speech_segments(self, audio_data: np.ndarray, frame_size: int = 1024) -> list:
        """Detect speech segments in audio"""
        segments = []
        frame_length = frame_size / self.sample_rate
        
        for i in range(0, len(audio_data) - frame_size, frame_size // 2):
            frame = audio_data[i:i + frame_size]
            
            # Calculate energy
            energy = np.sum(frame ** 2)
            
            # Calculate zero-crossing rate
            zcr = np.sum(np.diff(np.sign(frame)) != 0) / len(frame)
            
            # Simple voice activity detection
            if energy > 0.001 and zcr < 0.3:
                start_time = i / self.sample_rate
                end_time = (i + frame_size) / self.sample_rate
                segments.append((start_time, end_time))
        
        return segments
    
    def enhance_for_whisper(self, audio_data: np.ndarray) -> np.ndarray:
        """Optimize audio specifically for Whisper transcription"""
        try:
            # Resample to 16kHz if needed
            if self.sample_rate != 16000:
                audio_data = self._resample_audio(audio_data, 16000)
            
            # Apply voice-specific preprocessing
            audio_data = self.preprocess_audio(audio_data)
            
            # Ensure proper length (Whisper works best with certain lengths)
            target_length = int(16000 * 30)  # 30 seconds max
            if len(audio_data) > target_length:
                audio_data = audio_data[:target_length]
            
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Whisper optimization failed: {e}")
            return audio_data
    
    def _resample_audio(self, audio_data: np.ndarray, target_rate: int) -> np.ndarray:
        """Resample audio to target sample rate"""
        try:
            from scipy.signal import resample
            target_length = int(len(audio_data) * target_rate / self.sample_rate)
            return resample(audio_data, target_length)
        except Exception as e:
            self.logger.debug(f"Resampling failed: {e}")
            return audio_data
