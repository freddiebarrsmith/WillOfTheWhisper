"""
Gesture recognition system for processing hand gestures (thumbs up/down, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
import logging
from enum import Enum


class GestureType(Enum):
    """Types of gestures that can be recognized"""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    # ASL Letters
    LETTER_A = "letter_a"
    LETTER_B = "letter_b"
    LETTER_C = "letter_c"
    LETTER_D = "letter_d"
    LETTER_E = "letter_e"
    LETTER_F = "letter_f"
    LETTER_G = "letter_g"
    LETTER_H = "letter_h"
    LETTER_I = "letter_i"
    LETTER_L = "letter_l"
    LETTER_M = "letter_m"
    LETTER_N = "letter_n"
    LETTER_O = "letter_o"
    LETTER_P = "letter_p"
    LETTER_Q = "letter_q"
    LETTER_R = "letter_r"
    LETTER_S = "letter_s"
    LETTER_T = "letter_t"
    LETTER_U = "letter_u"
    LETTER_V = "letter_v"
    LETTER_W = "letter_w"
    LETTER_X = "letter_x"
    LETTER_Y = "letter_y"
    # ASL Numbers
    NUMBER_1 = "number_1"
    NUMBER_2 = "number_2"
    NUMBER_3 = "number_3"
    NUMBER_4 = "number_4"
    NUMBER_5 = "number_5"
    NUMBER_6 = "number_6"
    NUMBER_7 = "number_7"
    NUMBER_8 = "number_8"
    NUMBER_9 = "number_9"
    NUMBER_10 = "number_10"
    # ASL Word Signs
    WORD_HELLO = "word_hello"
    WORD_YES = "word_yes"
    WORD_NO = "word_no"
    WORD_THANK_YOU = "word_thank_you"
    WORD_PLEASE = "word_please"
    WORD_SORRY = "word_sorry"
    WORD_HELP = "word_help"
    WORD_WATER = "word_water"
    WORD_FOOD = "word_food"
    WORD_BATHROOM = "word_bathroom"
    WORD_GOOD = "word_good"
    WORD_BAD = "word_bad"
    WORD_HAPPY = "word_happy"
    WORD_SAD = "word_sad"
    WORD_LOVE = "word_love"
    WORD_MORE = "word_more"
    WORD_STOP = "word_stop"
    WORD_GO = "word_go"
    WORD_COME = "word_come"
    WORD_WHERE = "word_where"
    WORD_WHAT = "word_what"
    WORD_WHEN = "word_when"
    WORD_WHY = "word_why"
    WORD_HOW = "word_how"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_letter(cls, letter: str) -> 'GestureType':
        """Convert letter string to GestureType"""
        letter_upper = letter.upper()
        try:
            return cls[f"LETTER_{letter_upper}"]
        except KeyError:
            return cls.UNKNOWN
    
    @classmethod
    def from_number(cls, number: int) -> 'GestureType':
        """Convert number to GestureType"""
        try:
            if 1 <= number <= 10:
                return cls[f"NUMBER_{number}"]
        except KeyError:
            pass
        return cls.UNKNOWN


class GestureProcessor(ABC):
    """Abstract base class for gesture processors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.enabled = self._get_config_value("enabled", True)
        # Initialize callbacks for all gesture types
        self.callbacks: Dict[GestureType, List[Callable]] = {
            gt: [] for gt in GestureType
        }
    
    def _get_config_value(self, key: str, default: Any) -> Any:
        """Get configuration value with dot notation support"""
        gesture_config = self.config.get("gestures", {})
        processor_name = self.get_name().lower().replace(" ", "_")
        processor_config = gesture_config.get(processor_name, {})
        return processor_config.get(key, default)
    
    @abstractmethod
    def can_process(self) -> bool:
        """Check if this processor can run (e.g., camera available)"""
        pass
    
    @abstractmethod
    def process_frame(self, frame: Any) -> Optional[GestureType]:
        """Process a single frame and return detected gesture, or None"""
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """Get processor priority (higher = more preferred)"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get processor name"""
        pass
    
    def get_description(self) -> str:
        """Get processor description"""
        return f"{self.get_name()} gesture processor"
    
    def register_callback(self, gesture_type: GestureType, callback: Callable) -> None:
        """Register a callback function for a specific gesture type"""
        if gesture_type in self.callbacks:
            self.callbacks[gesture_type].append(callback)
            self.logger.info(f"Registered callback for {gesture_type.value}")
    
    def unregister_callback(self, gesture_type: GestureType, callback: Callable) -> None:
        """Unregister a callback function"""
        if gesture_type in self.callbacks:
            if callback in self.callbacks[gesture_type]:
                self.callbacks[gesture_type].remove(callback)
                self.logger.info(f"Unregistered callback for {gesture_type.value}")
    
    def _trigger_callbacks(self, gesture_type: GestureType, data: Dict[str, Any] = None) -> None:
        """Trigger all callbacks for a gesture type"""
        if gesture_type in self.callbacks:
            for callback in self.callbacks[gesture_type]:
                try:
                    if data:
                        callback(gesture_type, data)
                    else:
                        callback(gesture_type)
                except Exception as e:
                    self.logger.error(f"Callback error for {gesture_type.value}: {e}")


class GestureManager:
    """Manages gesture recognition processors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.processors: List[GestureProcessor] = []
        self.active_processor: Optional[GestureProcessor] = None
        self._load_processors()
    
    def _load_processors(self) -> None:
        """Load all available gesture processors"""
        try:
            # Import all processor modules
            from .processors.thumbs_processor import ThumbsProcessor
            from .processors.sign_language_processor import SignLanguageProcessor
            
            # Create processor instances
            processor_classes = [
                SignLanguageProcessor,  # Full sign language support (higher priority)
                ThumbsProcessor,  # Simple thumbs up/down
            ]
            
            for processor_class in processor_classes:
                try:
                    processor = processor_class(self.config)
                    if processor.enabled and processor.can_process():
                        self.processors.append(processor)
                        self.logger.info(f"Loaded processor: {processor.get_name()}")
                    else:
                        self.logger.debug(f"Skipped processor {processor_class.__name__} (disabled or unavailable)")
                except Exception as e:
                    self.logger.warning(f"Failed to load {processor_class.__name__}: {e}")
            
            # Sort by priority (highest first)
            self.processors.sort(key=lambda p: p.get_priority(), reverse=True)
            
            # Set the first available processor as active
            if self.processors:
                self.active_processor = self.processors[0]
                self.logger.info(f"Active processor: {self.active_processor.get_name()}")
            
        except ImportError as e:
            self.logger.error(f"Failed to import processors: {e}")
    
    def get_active_processor(self) -> Optional[GestureProcessor]:
        """Get the currently active processor"""
        return self.active_processor
    
    def set_active_processor(self, processor_name: str) -> bool:
        """Set a specific processor as active"""
        for processor in self.processors:
            if processor.get_name().lower() == processor_name.lower():
                if processor.can_process():
                    self.active_processor = processor
                    self.logger.info(f"Switched to processor: {processor.get_name()}")
                    return True
                else:
                    self.logger.warning(f"Processor {processor_name} is not available")
                    return False
        self.logger.warning(f"Processor {processor_name} not found")
        return False
    
    def register_callback(self, gesture_type: GestureType, callback: Callable, processor_name: Optional[str] = None) -> bool:
        """Register a callback for a gesture type"""
        processor = self.active_processor
        if processor_name:
            processor = next((p for p in self.processors if p.get_name().lower() == processor_name.lower()), None)
        
        if processor:
            processor.register_callback(gesture_type, callback)
            return True
        else:
            self.logger.error("No processor available for callback registration")
            return False
    
    def process_frame(self, frame: Any) -> Optional[GestureType]:
        """Process a frame using the active processor"""
        if not self.active_processor:
            return None
        
        try:
            gesture = self.active_processor.process_frame(frame)
            if gesture and gesture != GestureType.UNKNOWN:
                # Trigger callbacks
                self.active_processor._trigger_callbacks(gesture)
            return gesture
        except Exception as e:
            self.logger.error(f"Processor {self.active_processor.get_name()} failed: {e}")
            return None
    
    def get_available_processors(self) -> List[Dict[str, Any]]:
        """Get list of available processors"""
        return [
            {
                "name": processor.get_name(),
                "description": processor.get_description(),
                "priority": processor.get_priority(),
                "enabled": processor.enabled,
                "available": processor.can_process()
            }
            for processor in self.processors
        ]
    
    def reload_processors(self) -> None:
        """Reload all processors"""
        self.processors.clear()
        self.active_processor = None
        self._load_processors()

