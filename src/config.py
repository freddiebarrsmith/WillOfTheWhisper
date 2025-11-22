"""
Configuration management for WhisperControl
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for WhisperControl"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from YAML file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = self._get_default_config()
            self.save_config()
    
    def save_config(self) -> None:
        """Save current configuration to YAML file"""
        with open(self.config_path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'whisper.model')"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'activation_mode': 'both',
            'hotkey': {
                'enabled': True,
                'key_combination': 'cmd+shift+space',
                'mode': 'push_to_talk'
            },
            'voice_activation': {
                'enabled': True,
                'sensitivity': 0.5,
                'silence_timeout': 2.0,
                'min_recording_duration': 0.5
            },
            'whisper': {
                'model': 'base',
                'language': None
            },
            'audio': {
                'sample_rate': 16000,
                'channels': 1,
                'chunk_size': 1024
            },
            'output': {
                'auto_paste': True,
                'copy_to_clipboard': True,
                'clear_clipboard_first': False
            },
            'feedback': {
                'audio_notification': True,
                'visual_notification': True,
                'log_level': 'INFO'
            },
            'advanced': {
                'temp_dir': 'temp',
                'log_dir': 'logs',
                'max_recording_duration': 30.0,
                'cleanup_temp_files': True
            }
        }
    
    @property
    def activation_mode(self) -> str:
        return self.get('activation_mode', 'both')
    
    @property
    def hotkey_enabled(self) -> bool:
        return self.get('hotkey.enabled', True)
    
    @property
    def hotkey_combination(self) -> str:
        return self.get('hotkey.key_combination', 'cmd+shift+space')
    
    @property
    def hotkey_mode(self) -> str:
        return self.get('hotkey.mode', 'push_to_talk')
    
    @property
    def voice_enabled(self) -> bool:
        return self.get('voice_activation.enabled', True)
    
    @property
    def voice_sensitivity(self) -> float:
        return self.get('voice_activation.sensitivity', 0.5)
    
    @property
    def voice_silence_timeout(self) -> float:
        return self.get('voice_activation.silence_timeout', 2.0)
    
    @property
    def voice_min_duration(self) -> float:
        return self.get('voice_activation.min_recording_duration', 0.5)
    
    @property
    def whisper_model(self) -> str:
        return self.get('whisper.model', 'base')
    
    @property
    def whisper_language(self) -> Optional[str]:
        return self.get('whisper.language')
    
    @property
    def whisper_accent(self) -> Optional[str]:
        return self.get('whisper.accent')
    
    @property
    def audio_sample_rate(self) -> int:
        return self.get('audio.sample_rate', 16000)
    
    @property
    def audio_channels(self) -> int:
        return self.get('audio.channels', 1)
    
    @property
    def audio_chunk_size(self) -> int:
        return self.get('audio.chunk_size', 1024)

    @property
    def voice_min_speech_frames(self) -> int:
        return self.get('voice_activation.min_speech_frames', 3)
    
    @property
    def auto_paste(self) -> bool:
        return self.get('output.auto_paste', True)
    
    @property
    def copy_to_clipboard(self) -> bool:
        return self.get('output.copy_to_clipboard', True)
    
    @property
    def clear_clipboard_first(self) -> bool:
        return self.get('output.clear_clipboard_first', False)
    
    @property
    def audio_notification(self) -> bool:
        return self.get('feedback.audio_notification', True)
    
    @property
    def visual_notification(self) -> bool:
        return self.get('feedback.visual_notification', True)
    
    @property
    def log_level(self) -> str:
        return self.get('feedback.log_level', 'INFO')
    
    @property
    def temp_dir(self) -> str:
        return self.get('advanced.temp_dir', 'temp')
    
    @property
    def log_dir(self) -> str:
        return self.get('advanced.log_dir', 'logs')
    
    @property
    def max_recording_duration(self) -> float:
        return self.get('advanced.max_recording_duration', 30.0)
    
    @property
    def cleanup_temp_files(self) -> bool:
        return self.get('advanced.cleanup_temp_files', True)
    
    @property
    def use_smart_detection(self) -> bool:
        return self.get('output.use_smart_detection', True)
    
    @property
    def fallback_to_generic(self) -> bool:
        return self.get('output.fallback_to_generic', True)
    
    @property
    def ai_assistants_config(self) -> dict:
        return self.get('ai_assistants', {})
    
    def get_ai_assistant_config(self, assistant_name: str) -> dict:
        """Get configuration for a specific AI assistant"""
        return self.get(f'ai_assistants.{assistant_name}', {})
    
    def is_ai_assistant_enabled(self, assistant_name: str) -> bool:
        """Check if an AI assistant is enabled"""
        config = self.get_ai_assistant_config(assistant_name)
        return config.get('enabled', True)
