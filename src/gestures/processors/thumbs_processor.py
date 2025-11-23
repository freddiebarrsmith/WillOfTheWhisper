"""
Thumbs up/down gesture processor using MediaPipe
"""

from typing import Dict, Any, Optional
import logging
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from gestures import GestureProcessor, GestureType


class ThumbsProcessor(GestureProcessor):
    """Processor for detecting thumbs up and thumbs down gestures"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.mediapipe_hands = None
        self.camera = None
        self.last_gesture_time = {}
        self.gesture_cooldown = self._get_config_value("gesture_cooldown", 0.5)  # seconds
        self.confidence_threshold = self._get_config_value("confidence_threshold", 0.7)
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize MediaPipe and camera"""
        try:
            import cv2
            import mediapipe as mp
            self.cv2 = cv2  # Store for later use
            
            # Initialize MediaPipe Hands
            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils
            self.mediapipe_hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
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
            self.logger.warning("Install with: pip install opencv-python mediapipe")
        except Exception as e:
            self.logger.error(f"Failed to initialize camera: {e}")
    
    def can_process(self) -> bool:
        """Check if camera and MediaPipe are available"""
        return self.mediapipe_hands is not None and self.camera is not None
    
    def process_frame(self, frame: Any) -> Optional[GestureType]:
        """Process a frame and detect thumbs up/down gesture"""
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
            
            # Get the first hand
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Detect gesture
            gesture = self._detect_thumbs_gesture(hand_landmarks)
            
            # Apply cooldown to prevent rapid repeated gestures
            if gesture and gesture != GestureType.UNKNOWN:
                current_time = time.time()
                last_time = self.last_gesture_time.get(gesture, 0)
                
                if current_time - last_time < self.gesture_cooldown:
                    return None  # Still in cooldown
                
                self.last_gesture_time[gesture] = current_time
            
            return gesture
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return None
    
    def _detect_thumbs_gesture(self, hand_landmarks) -> GestureType:
        """Detect thumbs up or thumbs down from hand landmarks"""
        try:
            # MediaPipe hand landmarks indices:
            # Thumb: 4 (tip), 3 (IP), 2 (MP), 1 (CMC)
            # Index finger: 8 (tip), 6 (PIP), 5 (MCP)
            
            thumb_tip = hand_landmarks.landmark[4]
            thumb_ip = hand_landmarks.landmark[3]
            thumb_mcp = hand_landmarks.landmark[2]
            index_tip = hand_landmarks.landmark[8]
            index_pip = hand_landmarks.landmark[6]
            wrist = hand_landmarks.landmark[0]
            
            # Check if thumb is extended (thumbs up/down)
            # For thumbs up: thumb tip is above thumb IP and above wrist
            # For thumbs down: thumb tip is below thumb IP and below wrist
            
            # Calculate thumb direction
            thumb_vertical = thumb_tip.y - thumb_ip.y
            thumb_wrist_vertical = thumb_tip.y - wrist.y
            
            # Calculate thumb extension (how far thumb is from base)
            thumb_extension_x = abs(thumb_tip.x - thumb_mcp.x)
            thumb_extension_y = abs(thumb_tip.y - thumb_mcp.y)
            thumb_extension = thumb_extension_x + thumb_extension_y
            
            # Thumb must be extended (not curled)
            if thumb_extension < 0.12:
                return GestureType.UNKNOWN
            
            # Thumbs up: thumb tip is above IP joint and above wrist
            # More lenient thresholds
            if thumb_vertical < -0.03:  # Thumb tip above IP
                if thumb_wrist_vertical < -0.05:  # Thumb tip above wrist
                    return GestureType.THUMBS_UP
            
            # Thumbs down: thumb tip is below IP joint and below wrist
            elif thumb_vertical > 0.03:  # Thumb tip below IP
                if thumb_wrist_vertical > 0.05:  # Thumb tip below wrist
                    return GestureType.THUMBS_DOWN
            
            return GestureType.UNKNOWN
            
        except Exception as e:
            self.logger.error(f"Error detecting gesture: {e}")
            return GestureType.UNKNOWN
    
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
                # Flip frame horizontally for mirror effect (more natural)
                frame = self.cv2.flip(frame, 1)
                return frame
            return None
        except Exception as e:
            self.logger.error(f"Error reading camera frame: {e}")
            return None
    
    def get_priority(self) -> int:
        """High priority for thumbs processor"""
        return 100
    
    def get_name(self) -> str:
        """Get processor name"""
        return "Thumbs"
    
    def get_description(self) -> str:
        """Get processor description"""
        return "MediaPipe-based processor for thumbs up/down gestures"
    
    def cleanup(self) -> None:
        """Clean up resources"""
        if self.camera:
            self.camera.release()
        if self.mediapipe_hands:
            self.mediapipe_hands.close()

