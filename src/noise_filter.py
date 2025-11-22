"""
Noise filter to detect and ignore accidental sounds like keyboard/mouse clicks
"""

import numpy as np
import logging
from typing import Tuple


class NoiseFilter:
    """Filters out non-speech sounds like keyboard clicks and mouse clicks
    
    This filter uses multiple audio characteristics to distinguish between:
    - Speech: Sustained sounds with lower frequencies, smoother waveforms
    - Keyboard clicks: Very short, sharp transients with high frequencies
    - Mouse clicks: Similar to keyboard but slightly different frequency profile
    - Environmental noise: Various patterns depending on source
    
    Examples:
    - Mechanical keyboard "click" → Very short (<30ms), high frequency, sharp transient → FILTERED
    - Human speech "hello" → Sustained (>100ms), lower frequency, smooth → PASSED
    - Mouse click → Very short (<20ms), high frequency burst → FILTERED
    - Typing sequence → Multiple short bursts → FILTERED
    """
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.logger = logging.getLogger(__name__)
        
        # Characteristics of keyboard/mouse clicks
        self.click_max_duration_ms = 50  # Clicks are very short (<50ms)
        self.click_min_duration_ms = 5   # Minimum click duration
        self.speech_min_duration_ms = 150  # Speech needs to be longer (increased for mechanical keyboards)
        
        # Energy thresholds (mechanical keyboards are LOUD)
        self.click_energy_threshold = 0.005  # Lowered - clicks have high energy in short bursts
        self.speech_energy_threshold = 0.001  # Speech has more sustained but lower peak energy
        
        # Frequency characteristics
        # Mechanical keyboards have VERY high frequency content (clicky sounds)
        self.click_high_freq_ratio = 0.35  # Clicks have >35% energy in high frequencies (2kHz+)
        self.speech_high_freq_ratio = 0.15  # Speech has <15% energy in high frequencies
        
        # Zero-crossing rate (clicks have very high ZCR due to sharp transients)
        self.click_zcr_threshold = 0.4  # Clicks have high zero-crossing rate
        self.speech_zcr_threshold = 0.25  # Speech has lower zero-crossing rate
        
        # Mechanical keyboard specific: very sharp attack (sudden onset)
        self.mechanical_keyboard_attack_threshold = 0.3  # Very sharp attack characteristic
    
    def is_click_or_noise(self, audio_chunk: np.ndarray) -> bool:
        """Detect if audio chunk is a keyboard/mouse click or other noise"""
        try:
            if len(audio_chunk) == 0:
                return True  # Empty chunk is noise
            
            # Convert to mono if stereo
            if len(audio_chunk.shape) > 1:
                audio_chunk = np.mean(audio_chunk, axis=1)
            
            # Calculate duration
            duration_ms = (len(audio_chunk) / self.sample_rate) * 1000
            
            # Longer sounds (>100ms) are very likely speech, be less aggressive
            if duration_ms > self.speech_min_duration_ms:
                # Only filter if it's clearly a click pattern (very sharp transient)
                return self._is_sharp_transient(audio_chunk) and duration_ms < 50
            
            # Check 1: Duration - clicks are very short
            if duration_ms < self.click_max_duration_ms:
                # Could be a click, check other characteristics
                return self._analyze_click_characteristics(audio_chunk, duration_ms)
            
            # Check 2: Very short bursts are likely clicks
            if duration_ms < self.speech_min_duration_ms:
                # Analyze if it's a sustained sound or a click
                return self._is_short_burst(audio_chunk, duration_ms)
            
            # Longer sounds are likely speech
            return False
            
        except Exception as e:
            self.logger.debug(f"Error in noise detection: {e}")
            return False  # On error, assume it's not noise (safer)
    
    def _analyze_click_characteristics(self, audio_chunk: np.ndarray, duration_ms: float) -> bool:
        """Analyze audio characteristics to determine if it's a click
        
        Example analysis:
        - Mechanical keyboard press: 
          * Duration: ~15ms
          * Energy: High (0.02) - loud click
          * ZCR: Very high (0.6) - sharp transient
          * High freq: 45% - lots of high frequency content
          * Spectral centroid: 3500Hz - very bright
          * Attack: Very sharp (0.4)
          → Result: IS_CLICK (filtered)
        
        - Human speech "hello":
          * Duration: ~500ms
          * Energy: Moderate (0.003) - sustained
          * ZCR: Low (0.2) - smooth waveform
          * High freq: 12% - mostly low/mid frequencies
          * Spectral centroid: 1200Hz - warmer sound
          * Attack: Gradual (0.1)
          → Result: NOT_CLICK (passed through)
        """
        try:
            # Calculate energy
            energy = np.mean(audio_chunk ** 2)
            
            # Calculate zero-crossing rate
            zcr = self._calculate_zcr(audio_chunk)
            
            # Calculate frequency characteristics
            high_freq_ratio = self._calculate_high_freq_ratio(audio_chunk)
            
            # Calculate spectral centroid (brightness)
            spectral_centroid = self._calculate_spectral_centroid(audio_chunk)
            
            # Calculate attack sharpness (mechanical keyboards have very sharp attacks)
            attack_sharpness = self._calculate_attack_sharpness(audio_chunk)
            
            # Click characteristics (mechanical keyboard example):
            # 1. Very short duration (< 50ms) - "click" happens in ~15-30ms
            # 2. High energy in short burst - mechanical keys are LOUD
            # 3. High zero-crossing rate (sharp transient) - sudden "click" sound
            # 4. High frequency content - the "click" is high-pitched
            # 5. High spectral centroid - bright, sharp sound
            # 6. Very sharp attack - sound starts instantly
            
            is_click = False
            click_score = 0  # Score how "click-like" this is
            
            # Very short duration is a strong indicator
            if duration_ms < 30:
                click_score += 3
                if duration_ms < 20:
                    click_score += 2  # Very short = more likely click
            
            # High energy in short burst
            if energy > self.click_energy_threshold:
                click_score += 2
                if energy > self.click_energy_threshold * 2:
                    click_score += 1  # Very loud = more likely mechanical keyboard
            
            # High zero-crossing rate (sharp transient)
            if zcr > self.click_zcr_threshold:
                click_score += 2
                if zcr > 0.6:
                    click_score += 1  # Very sharp
            
            # High frequency content (mechanical keyboards are "clicky")
            if high_freq_ratio > self.click_high_freq_ratio:
                click_score += 2
                if high_freq_ratio > 0.5:
                    click_score += 1  # Very high frequency = clicky sound
            
            # High spectral centroid (bright sound)
            if spectral_centroid > 2000:
                click_score += 1
                if spectral_centroid > 3000:
                    click_score += 1  # Very bright = mechanical keyboard
            
            # Very sharp attack (characteristic of mechanical keyboards)
            if attack_sharpness > self.mechanical_keyboard_attack_threshold:
                click_score += 2  # Strong indicator of mechanical keyboard
            
            # If it's a sharp transient, that's a strong indicator
            if self._is_sharp_transient(audio_chunk):
                click_score += 3
            
            # Decision: If score is high enough, it's a click
            # Score of 5+ = likely click, 8+ = definitely click
            if click_score >= 5:
                is_click = True
                self.logger.debug(f"Detected click: duration={duration_ms:.1f}ms, energy={energy:.4f}, "
                                f"zcr={zcr:.2f}, high_freq={high_freq_ratio:.2f}, "
                                f"centroid={spectral_centroid:.0f}Hz, attack={attack_sharpness:.2f}, "
                                f"score={click_score}")
            
            return is_click
            
        except Exception as e:
            self.logger.debug(f"Error analyzing click characteristics: {e}")
            return False
    
    def _is_short_burst(self, audio_chunk: np.ndarray, duration_ms: float) -> bool:
        """Check if short audio is a burst (click) or sustained sound"""
        try:
            # Calculate energy over time
            frame_size = int(self.sample_rate * 0.01)  # 10ms frames
            frames = []
            
            for i in range(0, len(audio_chunk) - frame_size, frame_size):
                frame = audio_chunk[i:i + frame_size]
                frames.append(np.mean(frame ** 2))
            
            if len(frames) == 0:
                return False
            
            # Clicks have energy concentrated in one or two frames
            # Speech has more distributed energy
            max_energy = max(frames)
            mean_energy = np.mean(frames)
            
            # If max energy is much higher than mean, it's likely a click
            if max_energy > mean_energy * 3:
                return True
            
            # Check energy decay - clicks decay quickly, speech is more sustained
            if len(frames) >= 3:
                energy_decay = (frames[0] + frames[1]) / (frames[-2] + frames[-1] + 0.0001)
                if energy_decay > 5:  # Rapid decay indicates click
                    return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error checking short burst: {e}")
            return False
    
    def _calculate_zcr(self, audio_chunk: np.ndarray) -> float:
        """Calculate zero-crossing rate"""
        try:
            if len(audio_chunk) < 2:
                return 0.0
            
            # Count sign changes
            sign_changes = np.sum(np.diff(np.sign(audio_chunk)) != 0)
            zcr = sign_changes / len(audio_chunk)
            
            return zcr
            
        except Exception:
            return 0.0
    
    def _calculate_high_freq_ratio(self, audio_chunk: np.ndarray) -> float:
        """Calculate ratio of high-frequency energy to total energy"""
        try:
            if len(audio_chunk) < 64:
                return 0.0
            
            # Compute FFT
            fft = np.fft.rfft(audio_chunk)
            fft_magnitude = np.abs(fft)
            
            # Frequency bins
            freqs = np.fft.rfftfreq(len(audio_chunk), 1.0 / self.sample_rate)
            
            # High frequency range (above 2kHz)
            high_freq_mask = freqs > 2000
            low_freq_mask = freqs <= 2000
            
            high_freq_energy = np.sum(fft_magnitude[high_freq_mask] ** 2)
            total_energy = np.sum(fft_magnitude ** 2)
            
            if total_energy == 0:
                return 0.0
            
            return high_freq_energy / total_energy
            
        except Exception as e:
            self.logger.debug(f"Error calculating high freq ratio: {e}")
            return 0.0
    
    def _calculate_spectral_centroid(self, audio_chunk: np.ndarray) -> float:
        """Calculate spectral centroid (brightness)"""
        try:
            if len(audio_chunk) < 64:
                return 0.0
            
            # Compute FFT
            fft = np.fft.rfft(audio_chunk)
            fft_magnitude = np.abs(fft)
            
            # Frequency bins
            freqs = np.fft.rfftfreq(len(audio_chunk), 1.0 / self.sample_rate)
            
            # Calculate weighted average frequency
            magnitude_sum = np.sum(fft_magnitude)
            if magnitude_sum == 0:
                return 0.0
            
            centroid = np.sum(freqs * fft_magnitude) / magnitude_sum
            
            return centroid
            
        except Exception as e:
            self.logger.debug(f"Error calculating spectral centroid: {e}")
            return 0.0
    
    def _calculate_attack_sharpness(self, audio_chunk: np.ndarray) -> float:
        """Calculate how sharp the attack is (onset of sound)
        
        Example:
        - Mechanical keyboard: Attack happens in first 5-10ms, very sharp (0.4-0.6)
        - Human speech: Attack is gradual over 20-50ms, smooth (0.1-0.2)
        """
        try:
            if len(audio_chunk) < 20:
                return 0.0
            
            # Look at the first 20% of the audio chunk (the attack)
            attack_length = max(10, len(audio_chunk) // 5)
            attack_portion = audio_chunk[:attack_length]
            rest_portion = audio_chunk[attack_length:]
            
            if len(rest_portion) == 0:
                return 0.0
            
            # Calculate energy in attack vs rest
            attack_energy = np.mean(attack_portion ** 2)
            rest_energy = np.mean(rest_portion ** 2) if len(rest_portion) > 0 else 0.001
            
            # Sharp attack = high energy at start relative to rest
            if rest_energy > 0:
                sharpness = attack_energy / (rest_energy + 0.0001)
                # Normalize to 0-1 range
                return min(1.0, sharpness / 10.0)
            
            return 0.0
            
        except Exception as e:
            self.logger.debug(f"Error calculating attack sharpness: {e}")
            return 0.0
    
    def _is_sharp_transient(self, audio_chunk: np.ndarray) -> bool:
        """Detect sharp transients (characteristic of clicks)
        
        Example:
        - Mechanical keyboard: Sudden jump from silence to loud click
          * Derivative ratio: 15-30x (very sharp)
          * Energy spike: 25-50x (sudden burst)
          → Result: IS_SHARP_TRANSIENT
        
        - Human speech: Gradual onset
          * Derivative ratio: 2-5x (smooth)
          * Energy spike: 3-8x (gradual)
          → Result: NOT_SHARP_TRANSIENT
        """
        try:
            if len(audio_chunk) < 10:
                return False
            
            # Calculate first derivative (rate of change)
            derivative = np.diff(audio_chunk)
            
            # Sharp transients have high derivative values
            max_derivative = np.max(np.abs(derivative))
            mean_derivative = np.mean(np.abs(derivative))
            
            # If max derivative is much higher than mean, it's a sharp transient
            # Mechanical keyboards: ratio of 10-30x is common
            if mean_derivative > 0:
                if max_derivative > mean_derivative * 10:
                    return True
            
            # Check for sudden energy spikes
            energy = audio_chunk ** 2
            max_energy = np.max(energy)
            mean_energy = np.mean(energy)
            
            # Mechanical keyboards: sudden energy burst, ratio of 20-50x
            if mean_energy > 0:
                if max_energy > mean_energy * 20:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error detecting sharp transient: {e}")
            return False
    
    def filter_audio(self, audio_chunk: np.ndarray) -> Tuple[np.ndarray, bool]:
        """Filter audio and return (filtered_audio, is_noise)"""
        is_noise = self.is_click_or_noise(audio_chunk)
        
        if is_noise:
            # Return silence or very quiet audio
            return np.zeros_like(audio_chunk), True
        
        return audio_chunk, False

