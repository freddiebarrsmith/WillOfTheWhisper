# Gesture Recognition System

A modular gesture recognition system for WhisperControl that processes hand gestures (thumbs up/down) using a plugin architecture similar to the output handlers.

## Architecture

The gesture recognition system follows the same plugin architecture as the output handlers:

```
src/gestures/
├── __init__.py              # Base classes and GestureManager
├── processors/
│   ├── __init__.py
│   └── thumbs_processor.py  # Thumbs up/down processor
└── gesture_recognizer.py    # Main recognition runner
```

### Components

1. **GestureProcessor** (ABC): Abstract base class for gesture processors
   - `can_process()`: Check if processor can run
   - `process_frame()`: Process a frame and return detected gesture
   - `register_callback()`: Register callbacks for gesture events

2. **GestureManager**: Manages all gesture processors
   - Loads available processors
   - Selects active processor based on priority
   - Handles callback registration

3. **GestureRecognizer**: Main runner that processes frames in a loop
   - Runs in background thread
   - Handles camera capture
   - Triggers callbacks on gesture detection

## Usage

### Basic Example

```python
from gesture_recognizer import GestureRecognizer, create_gesture_recognizer
from gestures import GestureType

# Load config
config = {...}  # Your config dict

# Create recognizer
recognizer = create_gesture_recognizer(config)

# Register callbacks
def on_thumbs_up(gesture_type, data=None):
    print("Thumbs up detected!")

def on_thumbs_down(gesture_type, data=None):
    print("Thumbs down detected!")

recognizer.register_callback(GestureType.THUMBS_UP, on_thumbs_up)
recognizer.register_callback(GestureType.THUMBS_DOWN, on_thumbs_down)

# Start recognition
recognizer.start()

# ... your code ...

# Stop when done
recognizer.stop()
```

### Running the Test Script

```bash
python test_gestures.py
```

## Configuration

Add to `config.yaml`:

```yaml
gestures:
  enabled: true
  frame_rate: 30  # FPS for gesture recognition
  show_preview: false  # Show camera preview window
  thumbs:
    enabled: true
    gesture_cooldown: 0.5  # seconds between gesture detections
    confidence_threshold: 0.7  # 0.0 to 1.0, higher = more strict
```

## Adding New Gesture Processors

To add a new gesture processor:

1. Create a new processor class in `src/gestures/processors/`:

```python
from gestures import GestureProcessor, GestureType

class MyGestureProcessor(GestureProcessor):
    def can_process(self) -> bool:
        # Check if processor can run
        return True
    
    def process_frame(self, frame: Any) -> Optional[GestureType]:
        # Process frame and return gesture
        return GestureType.UNKNOWN
    
    def get_priority(self) -> int:
        return 50
    
    def get_name(self) -> str:
        return "MyGesture"
```

2. Register it in `src/gestures/__init__.py`:

```python
from .processors.my_gesture_processor import MyGestureProcessor

processor_classes = [
    ThumbsProcessor,
    MyGestureProcessor,  # Add here
]
```

## Dependencies

- `opencv-python>=4.8.0`: Camera access and image processing
- `mediapipe>=0.10.0`: Hand tracking and gesture recognition

Install with:
```bash
pip install opencv-python mediapipe
```

## Gesture Types

Currently supported:
- `THUMBS_UP`: Thumb extended upward
- `THUMBS_DOWN`: Thumb extended downward
- `UNKNOWN`: No gesture detected

## Features

- **Modular Architecture**: Easy to add new gesture processors
- **Callback System**: Register callbacks for specific gestures
- **Configurable**: All settings in config.yaml
- **Cooldown System**: Prevents rapid repeated gesture detection
- **Preview Window**: Optional camera preview for debugging
- **Thread-Safe**: Runs in background thread

## Integration with WhisperControl

The gesture recognition system can be integrated with WhisperControl to:
- Approve/reject transcriptions (thumbs up/down)
- Control recording (thumbs up to start, thumbs down to stop)
- Navigate through options
- Any custom action based on gestures

