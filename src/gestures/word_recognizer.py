"""
Word recognition system for sign language - combines letters into words
"""

from typing import List, Optional, Dict, Set
import time
import logging
from collections import deque


class WordRecognizer:
    """Recognizes words from sequences of letters"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Word recognition settings
        word_config = config.get("gestures", {}).get("word_recognition", {})
        self.enabled = word_config.get("enabled", True)
        self.letter_timeout = word_config.get("letter_timeout", 2.0)  # seconds to wait for next letter
        self.min_word_length = word_config.get("min_word_length", 2)  # minimum letters for a word
        self.max_word_length = word_config.get("max_word_length", 20)  # maximum letters
        self.enable_dictionary = word_config.get("enable_dictionary", True)
        self.auto_complete = word_config.get("auto_complete", True)  # Auto-complete words on timeout
        
        # Current word being built
        self.current_letters: deque = deque(maxlen=self.max_word_length)
        self.last_letter_time: Optional[float] = None
        self.word_callbacks: List[callable] = []
        
        # Dictionary for word suggestions/corrections
        self.dictionary: Set[str] = self._load_dictionary()
    
    def _load_dictionary(self) -> Set[str]:
        """Load a dictionary of common words"""
        # Common English words for suggestions
        common_words = {
            'hello', 'world', 'yes', 'no', 'please', 'thank', 'you', 'help',
            'water', 'food', 'bathroom', 'good', 'bad', 'happy', 'sad',
            'name', 'my', 'your', 'what', 'where', 'when', 'why', 'how',
            'the', 'and', 'or', 'but', 'if', 'then', 'now', 'later',
            'today', 'tomorrow', 'yesterday', 'morning', 'afternoon', 'night',
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'
        }
        return common_words
    
    def add_letter(self, letter: str) -> Optional[str]:
        """Add a letter to the current word and return word if complete"""
        if not self.enabled:
            return None
        
        current_time = time.time()
        
        # Check if too much time has passed since last letter (word complete)
        if self.last_letter_time is not None:
            time_since_last = current_time - self.last_letter_time
            if time_since_last > self.letter_timeout:
                # Word is complete, process it
                word = self._complete_word()
                if word:
                    return word
                # Start new word
                self.current_letters.clear()
        
        # Add new letter
        self.current_letters.append(letter.upper())
        self.last_letter_time = current_time
        
        # Check if word is complete (auto-complete if enabled)
        if self.auto_complete and len(self.current_letters) >= self.min_word_length:
            # Could check for word completion signals here
            pass
        
        return None
    
    def _complete_word(self) -> Optional[str]:
        """Complete the current word and return it"""
        if len(self.current_letters) < self.min_word_length:
            return None
        
        word = ''.join(self.current_letters)
        
        # Check dictionary for suggestions
        if self.enable_dictionary:
            word_lower = word.lower()
            if word_lower in self.dictionary:
                self.logger.info(f"Recognized word from dictionary: {word}")
            else:
                # Find similar words
                suggestions = self._find_similar_words(word_lower)
                if suggestions:
                    self.logger.debug(f"Suggestions for '{word}': {suggestions}")
        
        return word
    
    def _find_similar_words(self, word: str, max_distance: int = 2) -> List[str]:
        """Find similar words in dictionary using simple edit distance"""
        suggestions = []
        for dict_word in self.dictionary:
            distance = self._edit_distance(word, dict_word)
            if distance <= max_distance and distance < len(word):
                suggestions.append(dict_word)
        return sorted(suggestions, key=lambda w: self._edit_distance(word, w))[:5]
    
    def _edit_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance"""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def force_complete_word(self) -> Optional[str]:
        """Force complete the current word (e.g., on space gesture)"""
        word = self._complete_word()
        self.current_letters.clear()
        self.last_letter_time = None
        return word
    
    def clear_word(self) -> None:
        """Clear the current word being built"""
        self.current_letters.clear()
        self.last_letter_time = None
    
    def get_current_word(self) -> str:
        """Get the current word being built"""
        return ''.join(self.current_letters)
    
    def register_word_callback(self, callback: callable) -> None:
        """Register a callback for when a word is recognized"""
        self.word_callbacks.append(callback)
    
    def _trigger_word_callbacks(self, word: str) -> None:
        """Trigger all word callbacks"""
        for callback in self.word_callbacks:
            try:
                callback(word)
            except Exception as e:
                self.logger.error(f"Word callback error: {e}")

