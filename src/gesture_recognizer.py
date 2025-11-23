"""
Main gesture recognition module - runs gesture detection in a loop
"""

import logging
import time
import threading
from typing import Dict, Any, Optional, Callable
import cv2

from gestures import GestureManager, GestureType
from word_recognizer import WordRecognizer


class GestureRecognizer:
    """Main class for running gesture recognition"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.gesture_manager = GestureManager(config)
        self.word_recognizer = WordRecognizer(config)
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.frame_rate = config.get("gestures", {}).get("frame_rate", 30)
        self.show_preview = config.get("gestures", {}).get("show_preview", False)
        
        # Register word callback
        self.word_recognizer.register_word_callback(self._on_word_recognized)
    
    def start(self) -> bool:
        """Start gesture recognition in a background thread"""
        if self.running:
            self.logger.warning("Gesture recognizer already running")
            return False
        
        processor = self.gesture_manager.get_active_processor()
        if not processor:
            self.logger.error("No available gesture processor")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self.logger.info("Gesture recognizer started")
        return True
    
    def stop(self) -> None:
        """Stop gesture recognition"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        self.logger.info("Gesture recognizer stopped")
    
    def _run_loop(self) -> None:
        """Main recognition loop"""
        processor = self.gesture_manager.get_active_processor()
        if not processor or not hasattr(processor, 'get_camera_frame'):
            self.logger.error("Active processor does not support camera frames")
            return
        
        frame_delay = 1.0 / self.frame_rate
        import cv2
        
        self.logger.info("Starting recognition loop...")
        if self.show_preview:
            self.logger.info("Preview window enabled")
        
        while self.running:
            try:
                frame = processor.get_camera_frame()
                if frame is None:
                    self.logger.debug("No frame from camera")
                    time.sleep(0.1)
                    continue
                
                # Process the frame
                gesture = self.gesture_manager.process_frame(frame)
                
                # Handle word recognition for letters
                if gesture and gesture.value.startswith("letter_"):
                    letter = gesture.value.replace("letter_", "").upper()
                    word = self.word_recognizer.add_letter(letter)
                    if word:
                        self.word_recognizer._trigger_word_callbacks(word)
                
                # Show preview if enabled (skip if it fails - GUI may not be available)
                if self.show_preview:
                    try:
                        self._draw_preview(frame, gesture)
                    except Exception as e:
                        # Silently disable preview if it fails (common on headless/macOS)
                        if self.show_preview:  # Only log once
                            self.logger.warning("Preview window unavailable, disabling preview. Gesture detection still works.")
                            self.show_preview = False
                
                time.sleep(frame_delay)
                
            except KeyboardInterrupt:
                self.logger.info("Interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Error in recognition loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(0.1)
        
        # Cleanup
        if self.show_preview:
            try:
                cv2.destroyAllWindows()
            except:
                pass
        if hasattr(processor, 'cleanup'):
            processor.cleanup()
    
    def _draw_preview(self, frame: Any, gesture: Optional[GestureType]) -> None:
        """Draw preview window with gesture information"""
        try:
            import cv2
            
            if frame is None:
                return
            
            # Resize frame if too large (for better performance)
            height, width = frame.shape[:2]
            if width > 1280:
                scale = 1280 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Draw gesture text with larger, more visible font
            if gesture and gesture != GestureType.UNKNOWN:
                text = f"Gesture: {gesture.value.upper()}"
                color = (0, 255, 0)  # Green
                # Draw background rectangle for better visibility
                cv2.rectangle(frame, (5, 5), (450, 70), (0, 0, 0), -1)
                cv2.rectangle(frame, (5, 5), (450, 70), color, 3)
            else:
                text = "Show thumbs up or down"
                color = (0, 165, 255)  # Orange
                cv2.rectangle(frame, (5, 5), (450, 70), (0, 0, 0), -1)
            
            cv2.putText(frame, text, (15, 45), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            
            # Add instruction text at bottom
            h, w = frame.shape[:2]
            cv2.putText(frame, "Hold gesture steady - Press Q to quit", (10, h - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show the frame
            cv2.imshow('Gesture Recognition', frame)
            
            # Check for 'q' key to quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                self.logger.info("Quit key pressed")
                self.running = False
            
        except Exception as e:
            self.logger.error(f"Error drawing preview: {e}")
            import traceback
            traceback.print_exc()
    
    def register_callback(self, gesture_type: GestureType, callback: Callable) -> bool:
        """Register a callback for a gesture type"""
        return self.gesture_manager.register_callback(gesture_type, callback)
    
    def is_running(self) -> bool:
        """Check if recognizer is running"""
        return self.running
    
    def _on_word_recognized(self, word: str) -> None:
        """Callback when a word is recognized"""
        self.logger.info(f"Word recognized: {word}")
    
    def register_word_callback(self, callback: Callable) -> None:
        """Register a callback for when words are recognized"""
        self.word_recognizer.register_word_callback(callback)
    
    def get_current_word(self) -> str:
        """Get the current word being built"""
        return self.word_recognizer.get_current_word()
    
    def force_complete_word(self) -> Optional[str]:
        """Force complete the current word (e.g., on space gesture)"""
        return self.word_recognizer.force_complete_word()


def create_gesture_recognizer(config: Dict[str, Any]) -> Optional[GestureRecognizer]:
    """Factory function to create a gesture recognizer"""
    try:
        recognizer = GestureRecognizer(config)
        return recognizer
    except Exception as e:
        logging.error(f"Failed to create gesture recognizer: {e}")
        return None

