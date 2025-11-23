# Sign Language Recognition

Full sign language recognition system supporting ASL (American Sign Language) alphabet, numbers, and common signs.

## Features

### ASL Alphabet (Fingerspelling)
Recognizes all 26 letters of the ASL alphabet:
- **A-Z**: Complete fingerspelling support
- Hand tracking using MediaPipe
- Real-time letter detection

### ASL Numbers
Recognizes numbers 1-10:
- **1-5**: Standard finger counting
- **6-10**: ASL number signs

### Common Signs
- Thumbs up/down
- OK sign
- And more (extensible)

## Usage

### Basic Test

```bash
./venv/bin/python test_sign_language.py
```

### In Your Code

```python
from gesture_recognizer import create_gesture_recognizer
from gestures import GestureType
import yaml

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create recognizer
recognizer = create_gesture_recognizer(config)

# Register callbacks for letters
def letter_callback(gesture_type, data=None):
    letter = gesture_type.value.replace("letter_", "").upper()
    print(f"Detected letter: {letter}")

# Register for all letters
for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    gesture_type = GestureType.from_letter(letter)
    recognizer.register_callback(gesture_type, letter_callback)

# Register for numbers
def number_callback(gesture_type, data=None):
    number = gesture_type.value.replace("number_", "")
    print(f"Detected number: {number}")

for num in range(1, 11):
    gesture_type = GestureType.from_number(num)
    recognizer.register_callback(gesture_type, number_callback)

# Start recognition
recognizer.start()
```

## Configuration

In `config.yaml`:

```yaml
gestures:
  sign_language:
    enabled: true
    sign_cooldown: 1.0  # seconds between detections
    confidence_threshold: 0.5  # 0.0 to 1.0
    enable_fingerspelling: true  # ASL alphabet
    enable_numbers: true  # ASL numbers 1-10
    enable_common_signs: true  # Common signs
```

## Supported Gestures

### Letters
- **A**: Fist (all fingers down)
- **B**: All fingers extended, thumb in
- **C**: Curved C shape
- **D**: Index up
- **E**: All fingers down, thumb across
- **F**: Thumb and index touching, others extended
- **G**: Index pointing
- **H**: Index and middle side by side
- **I**: Pinky up
- **L**: Thumb and index at 90 degrees
- **M**: Thumb between ring and pinky
- **N**: Thumb between middle and ring
- **O**: Thumb and fingers form O
- **P**: Index and middle up, thumb out
- **Q**: Thumb and pinky extended
- **R**: Index and middle crossed
- **S**: Fist
- **T**: Thumb between index and middle
- **U**: Index and middle together
- **V**: Index and middle apart
- **W**: Index, middle, ring extended
- **X**: Index bent
- **Y**: Thumb and pinky extended
- **Z**: Index drawing Z (requires motion tracking)

### Numbers
- **1-5**: Standard finger counting
- **6**: Thumb and pinky
- **7**: Thumb, index, middle
- **8**: Thumb, index, middle, ring
- **9**: Index, middle, ring, pinky
- **10**: Closed fist or specific gesture

## Tips for Best Results

1. **Lighting**: Ensure good lighting so hand is clearly visible
2. **Background**: Use a contrasting background
3. **Distance**: Keep hand at comfortable distance from camera
4. **Steadiness**: Hold each sign steady for 1-2 seconds
5. **Clarity**: Make sure fingers are clearly extended/bent as needed
6. **Cooldown**: There's a 1-second cooldown between detections

## Architecture

The sign language processor uses:
- **MediaPipe Hands**: For hand landmark detection
- **Finger State Analysis**: Determines which fingers are extended
- **Geometric Analysis**: Calculates distances and angles between landmarks
- **Pattern Matching**: Matches finger patterns to known signs

## Extending

To add new signs:

1. Add gesture type to `GestureType` enum in `src/gestures/__init__.py`
2. Add detection logic in `_detect_letter()` or `_detect_common_signs()`
3. Update callbacks in your application

## Limitations

- Static signs only (no motion tracking yet)
- Single hand recognition (two-hand signs coming soon)
- Some letters (like Z) require motion and may not work perfectly
- Accuracy depends on lighting, camera quality, and hand positioning

## Future Enhancements

- Motion tracking for dynamic signs
- Two-hand sign recognition
- Word recognition (combining letters)
- Custom sign training
- Multiple sign language support (BSL, etc.)

