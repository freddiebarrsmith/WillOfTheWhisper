# WhisperControl

An **extensible** voice dictation tool for macOS that uses OpenAI's Whisper to transcribe speech and automatically paste it into AI coding assistants including VS Code Roo, Cursor IDE, Qwen Code, and any other application.

## Features

- **Dual Activation Modes**: Hotkey-based and voice-activated recording
- **Local Processing**: Uses local Whisper models for privacy and offline operation
- **Smart Integration**: Automatically detects and integrates with AI assistants
- **Extensible Plugin System**: Easy to add support for new AI assistants
- **Voice Commands**: Supports special commands like "new line", "tab", "space"
- **Configurable**: Extensive configuration options for customization
- **Real-time Feedback**: Audio and visual notifications

## Supported AI Assistants

- **VS Code Roo Extension** - Specialized handler with Roo-specific shortcuts
- **Cursor IDE** - Optimized for Cursor's AI features and composer
- **Qwen Code** - Support for Alibaba's Qwen Code assistant
- **Generic Applications** - Fallback handler for any application
- **Custom Handlers** - Easy to add new AI assistants (see [Extensibility Guide](EXTENSIBILITY.md))

## Quick Start

### 1. Setup

```bash
# Clone or download the project
cd whispercontrol

# Run the setup script
./setup.sh
```

### 2. Grant Permissions

Make sure to grant microphone permissions to Terminal/Python in:
**System Preferences > Security & Privacy > Microphone**

### 3. Run

```bash
# Activate virtual environment
source venv/bin/activate

# Start WhisperControl
python src/main.py
```

## Usage

### Hotkey Mode (Default)
- **Press and hold** `Cmd+Shift+Space` to start recording
- **Speak** your text
- **Release** the hotkey to transcribe and paste

### Voice Activation Mode
- **Speak** naturally - recording starts automatically
- **Stop speaking** - recording stops after silence timeout
- Text is automatically transcribed and pasted

### Special Voice Commands
- "new line" or "newline" → Insert newline
- "tab" → Insert tab
- "space" → Insert space
- "backspace" → Delete previous character
- "delete" → Delete next character
- "enter" → Press Enter key

## Configuration

Edit `config.yaml` to customize behavior:

```yaml
# Activation modes: "hotkey", "voice", "both"
activation_mode: "both"

# Hotkey settings
hotkey:
  enabled: true
  key_combination: "cmd+shift+space"
  mode: "push_to_talk"  # "push_to_talk" or "toggle"

# Voice activation settings
voice_activation:
  enabled: true
  sensitivity: 0.5  # 0.0 to 1.0
  silence_timeout: 2.0  # seconds
  min_recording_duration: 0.5  # seconds

# Whisper model settings
whisper:
  model: "base"  # tiny, base, small, medium, large
  language: null  # null for auto-detection

# Output behavior
output:
  auto_paste: true
  copy_to_clipboard: true
  clear_clipboard_first: false

# User feedback
feedback:
  audio_notification: true
  visual_notification: true
  log_level: "INFO"
```

## Whisper Models

Choose the model that balances speed and accuracy for your needs:

- **tiny**: Fastest, least accurate (~39 MB)
- **base**: Good balance (~74 MB) - **Default**
- **small**: Better accuracy (~244 MB)
- **medium**: High accuracy (~769 MB)
- **large**: Best accuracy (~1550 MB)

## Requirements

- macOS 10.14 or later
- Python 3.9 or later
- Microphone access
- ~100 MB free disk space (for base model)

## Dependencies

- `openai-whisper`: Speech-to-text processing
- `sounddevice`: Audio recording
- `soundfile`: Audio file handling
- `pynput`: Hotkey detection and keyboard automation
- `pyperclip`: Clipboard management
- `PyYAML`: Configuration management
- `webrtcvad`: Voice activity detection

## Troubleshooting

### Microphone Not Working
1. Check System Preferences > Security & Privacy > Microphone
2. Ensure Terminal/Python has microphone access
3. Test microphone in other applications

### Hotkey Not Responding
1. Check if hotkey conflicts with other applications
2. Try changing the hotkey combination in config.yaml
3. Ensure no other application is using the same hotkey

### Poor Transcription Quality
1. Speak clearly and at normal volume
2. Reduce background noise
3. Try a larger Whisper model (small, medium, large)
4. Check microphone quality and positioning

### Permission Issues
1. Grant microphone permissions
2. Grant accessibility permissions if needed
3. Run from Terminal with proper permissions

## Advanced Usage

### Custom Hotkeys
Modify `config.yaml` to use different key combinations:
```yaml
hotkey:
  key_combination: "cmd+alt+v"  # Custom combination
```

### Language-Specific Transcription
Set a specific language for better accuracy:
```yaml
whisper:
  language: "en"  # English
  # language: "es"  # Spanish
  # language: "fr"  # French
```

### Voice Sensitivity Tuning
Adjust voice activation sensitivity:
```yaml
voice_activation:
  sensitivity: 0.3  # Less sensitive (quieter environment)
  sensitivity: 0.7  # More sensitive (noisy environment)
```

## Integration with AI Assistants

WhisperControl automatically detects and integrates with AI assistants:

### VS Code Roo Extension
1. Open VS Code with Roo extension
2. Start WhisperControl
3. Click in Roo's input field
4. Use voice dictation to input prompts
5. Transcribed text appears in Roo's input field

### Cursor IDE
1. Open Cursor IDE
2. Start WhisperControl
3. Use Cmd+L to open chat or Cmd+K for composer
4. Voice dictation automatically works in Cursor's AI features

### Qwen Code
1. Open Qwen Code
2. Start WhisperControl
3. Use Cmd+Shift+A to open AI assistant
4. Voice dictation works with Qwen's AI features

### Any Application
- Generic handler works with any application
- Uses standard clipboard and paste functionality
- Automatically falls back when no specific handler is available

## Development

### Project Structure
```
whispercontrol/
├── src/
│   ├── config.py              # Configuration management
│   ├── audio_capture.py       # Audio recording and VAD
│   ├── whisper_transcriber.py # Whisper integration
│   ├── system_integration.py  # Clipboard and paste
│   ├── app_detector.py        # Application detection
│   ├── main.py                # Main application
│   └── plugins/               # Extensible plugin system
│       ├── __init__.py         # Plugin manager
│       └── handlers/           # Output handlers
│           ├── generic_handler.py
│           ├── vscode_roo_handler.py
│           ├── cursor_handler.py
│           └── qwen_code_handler.py
├── config.yaml                # Configuration file
├── requirements.txt           # Dependencies
├── setup.sh                   # Setup script
├── README.md                  # This file
└── EXTENSIBILITY.md          # Extensibility guide
```

### Adding New Features
1. Create new handlers in `src/plugins/handlers/`
2. Add configuration options to `config.yaml`
3. Update the plugin manager to load new handlers
4. Test thoroughly on macOS

### Adding New AI Assistant Support
See the [Extensibility Guide](EXTENSIBILITY.md) for detailed instructions on adding support for new AI assistants.

## License

This project is open source. Feel free to modify and distribute.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `logs/whispercontrol.log`
3. Create an issue with detailed information

## Changelog

### v1.0.0
- Initial release
- Hotkey and voice activation support
- Local Whisper integration
- VS Code Roo compatibility
- Comprehensive configuration options
