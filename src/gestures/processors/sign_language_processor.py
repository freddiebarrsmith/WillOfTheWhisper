"""
Sign Language Processor - Recognizes ASL alphabet, numbers, and common signs
"""

from typing import Dict, Any, Optional, List, Tuple
import logging
import time
import sys
import os
import math

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from gestures import GestureProcessor, GestureType


class SignLanguageProcessor(GestureProcessor):
    """Processor for recognizing sign language gestures including ASL alphabet"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.mediapipe_hands = None
        self.camera = None
        self.last_sign_time = {}
        self.sign_cooldown = self._get_config_value("sign_cooldown", 1.0)  # seconds
        self.confidence_threshold = self._get_config_value("confidence_threshold", 0.5)
        self.enable_fingerspelling = self._get_config_value("enable_fingerspelling", True)
        self.enable_numbers = self._get_config_value("enable_numbers", True)
        self.enable_common_signs = self._get_config_value("enable_common_signs", True)
        self.enable_word_signs = self._get_config_value("enable_word_signs", True)  # ASL word signs
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize MediaPipe and camera"""
        try:
            import cv2
            import mediapipe as mp
            
            # Initialize MediaPipe Hands
            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils
            self.mediapipe_hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,  # Support two hands for some signs
                min_detection_confidence=self.confidence_threshold,
                min_tracking_confidence=0.5
            )
            
            # Try to open camera
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.logger.warning("Could not open camera")
                self.camera = None
            else:
                self.logger.info("Camera initialized successfully")
            
        except ImportError as e:
            self.logger.warning(f"MediaPipe or OpenCV not available: {e}")
        except Exception as e:
            self.logger.error(f"Failed to initialize camera: {e}")
    
    def can_process(self) -> bool:
        """Check if camera and MediaPipe are available"""
        return self.mediapipe_hands is not None and self.camera is not None
    
    def process_frame(self, frame: Any) -> Optional[GestureType]:
        """Process a frame and detect sign language gestures"""
        if not self.can_process():
            return None
        
        try:
            import cv2
            
            # Convert BGR to RGB (MediaPipe uses RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.mediapipe_hands.process(rgb_frame)
            
            if not results.multi_hand_landmarks:
                return None
            
            # Get the first hand (primary hand)
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Detect sign
            sign = self._detect_sign(hand_landmarks, results.multi_handedness[0].classification[0].label)
            
            # Apply cooldown to prevent rapid repeated signs
            if sign and sign != GestureType.UNKNOWN:
                current_time = time.time()
                last_time = self.last_sign_time.get(sign, 0)
                
                if current_time - last_time < self.sign_cooldown:
                    return None  # Still in cooldown
                
                self.last_sign_time[sign] = current_time
            
            return sign
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return None
    
    def _detect_sign(self, hand_landmarks, handedness: str) -> GestureType:
        """Detect sign language gesture from hand landmarks"""
        try:
            # Get key landmarks
            landmarks = hand_landmarks.landmark
            
            # Fingers: [thumb, index, middle, ring, pinky]
            # Each finger has 4 points: tip, dip, pip, mcp
            finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
            finger_pips = [3, 6, 10, 14, 18]  # PIP joints
            finger_mcps = [2, 5, 9, 13, 17]   # MCP joints
            
            # Check which fingers are extended
            fingers_extended = self._get_extended_fingers(landmarks, finger_tips, finger_pips, finger_mcps)
            
            # Detect specific signs (order matters - check more specific first)
            # Check ASL word signs FIRST (most specific - whole words)
            if self.enable_word_signs:
                word_sign = self._detect_word_signs(fingers_extended, landmarks, handedness)
                if word_sign and word_sign != GestureType.UNKNOWN:
                    self.logger.debug(f"Detected word sign: {word_sign}")
                    return word_sign
            
            # Check fingerspelling (letters)
            if self.enable_fingerspelling:
                letter = self._detect_letter(fingers_extended, landmarks, handedness)
                if letter:
                    gesture = self._letter_to_gesture_type(letter)
                    if gesture != GestureType.UNKNOWN:
                        self.logger.debug(f"Detected letter: {letter}")
                        return gesture
            
            # Check numbers
            if self.enable_numbers:
                number = self._detect_number(fingers_extended, landmarks)
                if number:
                    gesture = self._number_to_gesture_type(number)
                    if gesture != GestureType.UNKNOWN:
                        self.logger.debug(f"Detected number: {number}")
                        return gesture
            
            # Check common signs last (thumbs up/down)
            if self.enable_common_signs:
                common_sign = self._detect_common_signs(fingers_extended, landmarks, handedness)
                if common_sign and common_sign != GestureType.UNKNOWN:
                    self.logger.debug(f"Detected common sign: {common_sign}")
                    return common_sign
            
            return GestureType.UNKNOWN
            
        except Exception as e:
            self.logger.error(f"Error detecting sign: {e}")
            return GestureType.UNKNOWN
    
    def _get_extended_fingers(self, landmarks, tips, pips, mcps) -> List[bool]:
        """Determine which fingers are extended"""
        fingers = []
        
        for i in range(5):  # 5 fingers
            tip = landmarks[tips[i]]
            pip = landmarks[pips[i]]
            mcp = landmarks[mcps[i]]
            
            if i == 0:  # Thumb - special case (horizontal)
                # Thumb is extended if tip is far from MCP horizontally
                # Check both x and y distance for thumb
                dx = abs(tip.x - mcp.x)
                dy = abs(tip.y - mcp.y)
                extended = (dx > 0.08) or (dy > 0.08)  # More lenient
            else:  # Other fingers - vertical
                # Finger is extended if tip is above PIP (lower y value = higher on screen)
                # Add some tolerance
                extended = tip.y < pip.y - 0.02  # More lenient threshold
            
            fingers.append(extended)
        
        return fingers
    
    def _detect_letter(self, fingers: List[bool], landmarks, handedness: str) -> Optional[str]:
        """Detect ASL alphabet letters based on finger positions"""
        thumb, index, middle, ring, pinky = fingers
        
        # Get hand orientation
        wrist = landmarks[0]
        middle_mcp = landmarks[9]
        hand_angle = math.atan2(middle_mcp.y - wrist.y, middle_mcp.x - wrist.x)
        
        # A: Fist (all fingers down) - check first before other signs
        if not thumb and not index and not middle and not ring and not pinky:
            return 'A'
        
        # B: All fingers extended, thumb in
        if index and middle and ring and pinky and not thumb:
            return 'B'
        
        # C: Curved C shape (thumb and index form C, others down)
        if thumb and index and not middle and not ring and not pinky:
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
            if 0.05 < distance < 0.15:  # Forming C shape
                return 'C'
        
        # D: Index up, others down
        if index and not middle and not ring and not pinky:
            return 'D'
        
        # E: All fingers down, thumb across
        if not index and not middle and not ring and not pinky and thumb:
            return 'E'
        
        # F: Thumb and index touching, others extended
        if middle and ring and pinky and not index:
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
            if distance < 0.05:  # Touching
                return 'F'
        
        # G: Index pointing (extended), thumb in, others down
        if index and not middle and not ring and not pinky and not thumb:
            return 'G'
        
        # H: Index and middle extended side by side, others down
        if index and middle and not ring and not pinky:
            return 'H'
        
        # I: Pinky up, others down
        if pinky and not thumb and not index and not middle and not ring:
            return 'I'
        
        # L: Thumb and index extended at 90 degrees, others down
        if thumb and index and not middle and not ring and not pinky:
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            # Check if they form L shape (perpendicular)
            dx = abs(thumb_tip.x - index_tip.x)
            dy = abs(thumb_tip.y - index_tip.y)
            if dx > 0.1 and dy > 0.1:  # Forming L
                return 'L'
        
        # M: Thumb between ring and pinky, index/middle/ring down
        if not index and not middle and ring and pinky and thumb:
            return 'M'
        
        # N: Thumb between middle and ring, index/middle down
        if not index and not middle and ring and pinky and thumb:
            # Check thumb position more carefully
            return 'N'
        
        # O: Thumb and fingers form O (all touching)
        if thumb and index:
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
            if distance < 0.03:  # Very close, forming O
                return 'O'
        
        # U: Index and middle extended together, others down (check first before V/P/R)
        if index and middle and not ring and not pinky:
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            distance = abs(index_tip.x - middle_tip.x)
            # U: fingers close together
            if distance < 0.05:
                return 'U'
            # V: fingers apart
            elif distance > 0.08:
                return 'V'
            # R: fingers crossed (middle over index)
            elif middle_tip.x < index_tip.x:
                return 'R'
            # P: thumb out with index/middle (simplified)
            elif thumb:
                return 'P'
        
        # Q: Thumb and pinky extended, others down
        if thumb and pinky and not index and not middle and not ring:
            return 'Q'
        
        # S: Fist with thumb across (all fingers down, thumb in)
        if not index and not middle and not ring and not pinky and not thumb:
            return 'S'
        
        # T: Thumb between index and middle, others down
        if not index and not middle and thumb and not ring and not pinky:
            return 'T'
        
        # W: Index, middle, ring extended, others down
        if index and middle and ring and not pinky:
            return 'W'
        
        # X: Index bent, others down
        if not middle and not ring and not pinky:
            index_tip = landmarks[8]
            index_pip = landmarks[6]
            if index_tip.y > index_pip.y:  # Bent
                return 'X'
        
        # Y: Thumb and pinky extended, others down
        if thumb and pinky and not index and not middle and not ring:
            return 'Y'
        
        # Z: Index drawing Z shape (hard to detect statically, simplified)
        if index and not middle and not ring and not pinky:
            # Could be Z, but need motion tracking
            pass
        
        return None
    
    def _detect_number(self, fingers: List[bool], landmarks) -> Optional[int]:
        """Detect ASL numbers 1-10"""
        thumb, index, middle, ring, pinky = fingers
        
        # Count extended fingers
        extended_count = sum(fingers)
        
        # Numbers 1-5: Count extended fingers
        if extended_count >= 1 and extended_count <= 5:
            # Special cases for thumb
            if extended_count == 1 and thumb:
                return 1
            elif extended_count == 2 and index and middle:
                return 2
            elif extended_count == 3 and index and middle and ring:
                return 3
            elif extended_count == 4 and index and middle and ring and pinky:
                return 4
            elif extended_count == 5:
                return 5
        
        # Numbers 6-10: More complex combinations
        # 6: Thumb and pinky
        if thumb and pinky and not index and not middle and not ring:
            return 6
        
        # 7: Thumb, index, middle
        if thumb and index and middle and not ring and not pinky:
            return 7
        
        # 8: Thumb, index, middle, ring
        if thumb and index and middle and ring and not pinky:
            return 8
        
        # 9: Thumb, index, middle, ring, pinky (all but thumb extended differently)
        if index and middle and ring and pinky:
            return 9
        
        # 10: Closed fist or specific gesture
        if not any(fingers):
            return 10
        
        return None
    
    def _detect_word_signs(self, fingers: List[bool], landmarks, handedness: str) -> Optional[GestureType]:
        """Detect ASL word signs (complete words, not letters)"""
        thumb, index, middle, ring, pinky = fingers
        
        # Get key landmarks for position analysis
        wrist = landmarks[0]
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        
        # YES: Nodding motion (hard to detect statically, but can detect hand position)
        # Simplified: Open hand moving up/down - for now, use open hand
        if index and middle and ring and pinky and not thumb:
            # Open hand could be YES (context dependent)
            pass
        
        # NO: Index and middle finger together, moving side to side
        # Static detection: Index and middle extended together
        if index and middle and not ring and not pinky:
            # Could be NO, but also could be U or V - need motion
            distance = abs(index_tip.x - middle_tip.x)
            if distance < 0.03:  # Very close together
                # Check if hand is in NO position (sideways)
                hand_angle = math.atan2(middle_tip.y - wrist.y, middle_tip.x - wrist.x)
                if abs(hand_angle) > 0.5:  # Hand rotated
                    return GestureType.WORD_NO
        
        # THANK YOU: Hand moving from chin forward
        # Static: Open hand near face - hard to detect without face landmarks
        # For now, use open hand (B) as potential THANK YOU
        if index and middle and ring and pinky and not thumb:
            # Check if hand is elevated (could be near face)
            if wrist.y < 0.5:  # Hand in upper half of frame
                return GestureType.WORD_THANK_YOU
        
        # PLEASE: Circular motion with flat hand on chest
        # Static: Flat hand (B) in center
        if index and middle and ring and pinky and not thumb:
            if 0.3 < wrist.y < 0.7:  # Middle of frame
                return GestureType.WORD_PLEASE
        
        # SORRY: Fist rotating on chest
        # Static: Fist (A) in center
        if not thumb and not index and not middle and not ring and not pinky:
            if 0.3 < wrist.y < 0.7:
                return GestureType.WORD_SORRY
        
        # HELP: One hand tapping other (requires two hands, simplified)
        # Static: Open hand (B) could indicate HELP
        if index and middle and ring and pinky and not thumb:
            if wrist.y > 0.6:  # Lower in frame
                return GestureType.WORD_HELP
        
        # WATER: W tapping chin
        # Static: W shape (index, middle, ring extended)
        if index and middle and ring and not pinky:
            if wrist.y < 0.5:  # Upper half (near face)
                return GestureType.WORD_WATER
        
        # FOOD: Fingers to mouth
        # Static: Fingers extended, hand elevated
        if index and middle and ring and pinky:
            if wrist.y < 0.4:  # Very high (near mouth)
                return GestureType.WORD_FOOD
        
        # BATHROOM: T shape shaking
        # Static: T shape (thumb between index and middle)
        if not index and not middle and thumb and not ring and not pinky:
            return GestureType.WORD_BATHROOM
        
        # GOOD: Flat hand moving forward from mouth
        # Static: Open hand (B) elevated
        if index and middle and ring and pinky and not thumb:
            if wrist.y < 0.5:
                return GestureType.WORD_GOOD
        
        # BAD: Flat hand down
        # Static: Open hand (B) lower
        if index and middle and ring and pinky and not thumb:
            if wrist.y > 0.6:
                return GestureType.WORD_BAD
        
        # HAPPY: Hand brushing up face
        # Static: Open hand (B) near face
        if index and middle and ring and pinky and not thumb:
            if wrist.y < 0.4 and wrist.x < 0.6:
                return GestureType.WORD_HAPPY
        
        # SAD: Hand down face
        # Static: Open hand (B) lower on face
        if index and middle and ring and pinky and not thumb:
            if 0.4 < wrist.y < 0.6:
                return GestureType.WORD_SAD
        
        # LOVE: Crossed arms on chest (requires two hands, simplified)
        # Static: X shape or crossed fingers
        if index and middle:
            # Check if fingers are crossed
            if abs(index_tip.x - middle_tip.x) < 0.02:
                return GestureType.WORD_LOVE
        
        # MORE: Fingers tapping together
        # Static: Fingers together (O shape)
        if thumb and index:
            distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
            if distance < 0.03:
                return GestureType.WORD_MORE
        
        # STOP: Flat hand forward
        # Static: Open hand (B) forward
        if index and middle and ring and pinky and not thumb:
            # Hand extended forward
            if 0.4 < wrist.y < 0.7:
                return GestureType.WORD_STOP
        
        # GO: Pointing forward
        # Static: Index pointing (G or D)
        if index and not middle and not ring and not pinky:
            return GestureType.WORD_GO
        
        # COME: Hand motioning toward self (requires motion, simplified)
        # Static: Open hand (B)
        if index and middle and ring and pinky and not thumb:
            if wrist.x < 0.5:  # Left side (toward self)
                return GestureType.WORD_COME
        
        # WHERE: Index moving side to side
        # Static: Index pointing (G)
        if index and not middle and not ring and not pinky:
            if wrist.y < 0.5:
                return GestureType.WORD_WHERE
        
        # WHAT: Open hands moving
        # Static: Open hand (B)
        if index and middle and ring and pinky and not thumb:
            if 0.3 < wrist.y < 0.6:
                return GestureType.WORD_WHAT
        
        # WHEN: Index pointing up
        # Static: Index pointing (G) elevated
        if index and not middle and not ring and not pinky:
            if wrist.y < 0.4:
                return GestureType.WORD_WHEN
        
        # WHY: Y shape moving
        # Static: Y shape (thumb and pinky)
        if thumb and pinky and not index and not middle and not ring:
            return GestureType.WORD_WHY
        
        # HOW: Hands together moving
        # Static: Open hands (B) together
        if index and middle and ring and pinky and not thumb:
            if 0.4 < wrist.y < 0.7:
                return GestureType.WORD_HOW
        
        return None
    
    def _detect_common_signs(self, fingers: List[bool], landmarks, handedness: str) -> Optional[GestureType]:
        """Detect common ASL signs (thumbs up/down, etc.)"""
        thumb, index, middle, ring, pinky = fingers
        
        # Thumbs up (already handled, but keep for compatibility)
        if thumb and not index and not middle and not ring and not pinky:
            thumb_tip = landmarks[4]
            thumb_ip = landmarks[3]
            if thumb_tip.y < thumb_ip.y:  # Thumb pointing up
                return GestureType.THUMBS_UP
        
        # Thumbs down
        if thumb and not index and not middle and not ring and not pinky:
            thumb_tip = landmarks[4]
            thumb_ip = landmarks[3]
            if thumb_tip.y > thumb_ip.y:  # Thumb pointing down
                return GestureType.THUMBS_DOWN
        
        # OK sign (thumb and index form circle)
        if thumb and index and not middle and not ring and not pinky:
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
            if distance < 0.03:
                # Could add OK gesture type
                pass
        
        return None
    
    def _letter_to_gesture_type(self, letter: str) -> GestureType:
        """Convert letter to gesture type"""
        return GestureType.from_letter(letter)
    
    def _number_to_gesture_type(self, number: int) -> GestureType:
        """Convert number to gesture type"""
        return GestureType.from_number(number)
    
    def get_camera_frame(self) -> Optional[Any]:
        """Get a frame from the camera"""
        if not self.camera:
            return None
        
        try:
            if not hasattr(self, 'cv2'):
                import cv2
                self.cv2 = cv2
            
            ret, frame = self.camera.read()
            if ret:
                frame = self.cv2.flip(frame, 1)
                return frame
            return None
        except Exception as e:
            self.logger.error(f"Error reading camera frame: {e}")
            return None
    
    def get_priority(self) -> int:
        """Highest priority for sign language processor (should run first)"""
        return 110  # Higher than thumbs processor (100)
    
    def get_name(self) -> str:
        """Get processor name"""
        return "SignLanguage"
    
    def get_description(self) -> str:
        """Get processor description"""
        return "MediaPipe-based processor for ASL alphabet, numbers, and common signs"
    
    def cleanup(self) -> None:
        """Clean up resources"""
        if self.camera:
            self.camera.release()
        if self.mediapipe_hands:
            self.mediapipe_hands.close()

