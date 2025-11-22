# WhisperControl Extensibility Guide

This guide explains how to extend WhisperControl with new AI assistant integrations and custom output handlers.

## Plugin System Architecture

WhisperControl uses a plugin-based architecture that allows you to add support for new AI assistants and applications without modifying the core code.

### Core Components

1. **OutputHandler**: Abstract base class for all output handlers
2. **PluginManager**: Manages and coordinates all handlers
3. **AppDetector**: Detects the currently active application
4. **Configuration**: YAML-based configuration for each handler

## Creating a New Output Handler

### Step 1: Create Handler Class

Create a new file in `src/plugins/handlers/` (e.g., `my_assistant_handler.py`):

```python
"""
Custom AI Assistant Handler
"""

from typing import Dict, Any
import logging
from pynput import keyboard
from pynput.keyboard import Key
import pyperclip
import time

from ..plugins import OutputHandler


class MyAssistantHandler(OutputHandler):
    """Handler for My AI Assistant"""
    
    def can_handle(self, app_info: Dict[str, Any]) -> bool:
        """Check if this handler can handle the current application"""
        app_name = app_info.get('name', '').lower()
        window_title = app_info.get('title', '').lower()
        
        # Define detection criteria
        is_my_assistant = (
            'my assistant' in app_name or
            'myai' in app_name or
            'my-assistant' in app_name
        )
        
        has_ai_features = (
            'ai' in window_title or
            'chat' in window_title or
            'assistant' in window_title
        )
        
        return is_my_assistant or has_ai_features
    
    def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
        """Send text to My AI Assistant"""
        try:
            # Copy to clipboard
            pyperclip.copy(text)
            
            # Small delay
            time.sleep(0.1)
            
            # Try to focus the input field
            self._focus_input_field()
            
            # Paste the text
            with keyboard.Controller() as controller:
                controller.press(Key.cmd)
                controller.press('v')
                controller.release('v')
                controller.release(Key.cmd)
            
            self.logger.info("Text sent to My AI Assistant")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send text to My Assistant: {e}")
            return False
    
    def _focus_input_field(self) -> None:
        """Try to focus the input field"""
        try:
            with keyboard.Controller() as controller:
                # Define custom shortcuts for your assistant
                controller.press(Key.cmd)
                controller.press('j')  # Example: Cmd+J to open chat
                controller.release('j')
                controller.release(Key.cmd)
                
                time.sleep(0.2)
                
        except Exception as e:
            self.logger.debug(f"Could not focus input field: {e}")
    
    def get_priority(self) -> int:
        """Get handler priority (higher = more preferred)"""
        return 75  # Set appropriate priority
    
    def get_name(self) -> str:
        """Get handler name"""
        return "My AI Assistant"
    
    def get_description(self) -> str:
        """Get handler description"""
        return "Custom handler for My AI Assistant"
```

### Step 2: Register Handler

Update `src/plugins/__init__.py` to include your new handler:

```python
def _load_handlers(self) -> None:
    """Load all available output handlers"""
    try:
        # Import all handler modules
        from .handlers.generic_handler import GenericHandler
        from .handlers.vscode_roo_handler import VSCodeRooHandler
        from .handlers.cursor_handler import CursorHandler
        from .handlers.qwen_code_handler import QwenCodeHandler
        from .handlers.my_assistant_handler import MyAssistantHandler  # Add this line
        
        # Create handler instances
        handler_classes = [
            GenericHandler,
            VSCodeRooHandler,
            CursorHandler,
            QwenCodeHandler,
            MyAssistantHandler  # Add this line
        ]
        
        # ... rest of the method
```

### Step 3: Add Configuration

Update `config.yaml` to include configuration for your handler:

```yaml
# AI Assistant Integration Settings
ai_assistants:
  # ... existing handlers ...
  
  # My AI Assistant
  my_assistant:
    enabled: true
    priority: 75
    shortcuts:
      open_chat: "cmd+j"           # Command to open chat
      focus_input: "cmd+i"         # Command to focus input
    detection:
      app_names: ["My Assistant", "MyAI", "My-Assistant"]
      window_keywords: ["ai", "chat", "assistant", "prompt"]
```

## Advanced Handler Features

### Custom Detection Logic

You can implement sophisticated detection logic:

```python
def can_handle(self, app_info: Dict[str, Any]) -> bool:
    """Advanced detection logic"""
    app_name = app_info.get('name', '').lower()
    window_title = app_info.get('title', '').lower()
    bundle_id = app_info.get('bundle_id', '').lower()
    
    # Check bundle ID for exact match
    if bundle_id == 'com.mycompany.myassistant':
        return True
    
    # Check app name patterns
    app_patterns = ['my assistant', 'myai', 'my-assistant']
    if any(pattern in app_name for pattern in app_patterns):
        return True
    
    # Check window title for specific features
    title_indicators = ['ai chat', 'assistant panel', 'prompt input']
    if any(indicator in window_title for indicator in title_indicators):
        return True
    
    return False
```

### Custom Text Processing

Implement custom text processing before sending:

```python
def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
    """Send text with custom processing"""
    try:
        # Custom text processing
        processed_text = self._process_text(text)
        
        # Custom sending logic
        return self._send_to_assistant(processed_text)
        
    except Exception as e:
        self.logger.error(f"Failed to send text: {e}")
        return False

def _process_text(self, text: str) -> str:
    """Custom text processing"""
    # Example: Add prefix for your assistant
    if not text.startswith('/'):
        return f"/prompt {text}"
    return text

def _send_to_assistant(self, text: str) -> bool:
    """Custom sending implementation"""
    # Implement custom sending logic here
    # Could use APIs, special shortcuts, etc.
    pass
```

### Multiple Input Methods

Support different ways to send text:

```python
def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
    """Try multiple methods to send text"""
    methods = [
        self._send_via_clipboard,
        self._send_via_api,
        self._send_via_shortcuts,
        self._send_via_typing
    ]
    
    for method in methods:
        try:
            if method(text):
                return True
        except Exception as e:
            self.logger.debug(f"Method {method.__name__} failed: {e}")
            continue
    
    return False
```

## Configuration Options

### Handler Configuration

Each handler can have custom configuration:

```yaml
ai_assistants:
  my_assistant:
    enabled: true
    priority: 75
    shortcuts:
      open_chat: "cmd+j"
      focus_input: "cmd+i"
      send_message: "cmd+enter"
    detection:
      app_names: ["My Assistant"]
      window_keywords: ["ai", "chat"]
      bundle_ids: ["com.mycompany.myassistant"]
    custom_settings:
      api_endpoint: "http://localhost:8080/api"
      timeout: 5.0
      retry_attempts: 3
```

### Accessing Configuration

In your handler, access configuration:

```python
def __init__(self, config: Dict[str, Any]):
    super().__init__(config)
    self.custom_config = config.get('my_assistant', {})
    self.api_endpoint = self.custom_config.get('custom_settings', {}).get('api_endpoint')
```

## Testing Your Handler

### Unit Testing

Create tests for your handler:

```python
import unittest
from unittest.mock import Mock, patch
from my_assistant_handler import MyAssistantHandler

class TestMyAssistantHandler(unittest.TestCase):
    def setUp(self):
        self.config = {'my_assistant': {'enabled': True}}
        self.handler = MyAssistantHandler(self.config)
    
    def test_can_handle(self):
        app_info = {'name': 'My Assistant', 'title': 'AI Chat'}
        self.assertTrue(self.handler.can_handle(app_info))
    
    def test_cannot_handle(self):
        app_info = {'name': 'Other App', 'title': 'Regular Window'}
        self.assertFalse(self.handler.can_handle(app_info))
    
    @patch('pyperclip.copy')
    @patch('keyboard.Controller')
    def test_send_text(self, mock_controller, mock_copy):
        app_info = {'name': 'My Assistant'}
        result = self.handler.send_text("test message", app_info)
        self.assertTrue(result)
```

### Integration Testing

Test with the actual application:

```python
def test_integration():
    """Test handler with real application"""
    # Start your AI assistant
    # Run WhisperControl
    # Test voice input
    # Verify text appears in assistant
```

## Debugging Handlers

### Enable Debug Logging

Set log level to DEBUG in config:

```yaml
feedback:
  log_level: "DEBUG"
```

### Handler-Specific Logging

Add detailed logging to your handler:

```python
def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
    """Send text with detailed logging"""
    self.logger.debug(f"Sending text to {app_info['name']}: {text}")
    
    try:
        # Your implementation
        self.logger.debug("Text sent successfully")
        return True
    except Exception as e:
        self.logger.error(f"Failed to send text: {e}")
        return False
```

## Best Practices

### 1. Graceful Degradation

Always provide fallback behavior:

```python
def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
    """Send text with fallback"""
    try:
        # Try primary method
        if self._send_via_api(text):
            return True
    except Exception as e:
        self.logger.warning(f"Primary method failed: {e}")
    
    # Fallback to clipboard
    try:
        return self._send_via_clipboard(text)
    except Exception as e:
        self.logger.error(f"All methods failed: {e}")
        return False
```

### 2. Error Handling

Implement comprehensive error handling:

```python
def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
    """Send text with error handling"""
    if not text or not text.strip():
        self.logger.warning("Empty text provided")
        return False
    
    if not app_info or not app_info.get('name'):
        self.logger.error("Invalid app info provided")
        return False
    
    try:
        # Your implementation
        return True
    except PermissionError:
        self.logger.error("Permission denied - check accessibility settings")
        return False
    except TimeoutError:
        self.logger.error("Operation timed out")
        return False
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        return False
```

### 3. Performance Considerations

Optimize for performance:

```python
class MyAssistantHandler(OutputHandler):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Cache expensive operations
        self._cached_app_info = None
        self._last_check_time = 0
    
    def can_handle(self, app_info: Dict[str, Any]) -> bool:
        """Cached detection for performance"""
        current_time = time.time()
        
        # Cache detection results for 1 second
        if (self._cached_app_info == app_info and 
            current_time - self._last_check_time < 1.0):
            return self._cached_result
        
        result = self._do_detection(app_info)
        self._cached_app_info = app_info
        self._cached_result = result
        self._last_check_time = current_time
        
        return result
```

## Contributing Handlers

### Submitting New Handlers

1. Create your handler following the guidelines above
2. Add comprehensive tests
3. Update documentation
4. Submit a pull request

### Handler Requirements

- Must inherit from `OutputHandler`
- Must implement all abstract methods
- Must include error handling
- Must include logging
- Must include tests
- Must include documentation

## Examples

### GitHub Copilot Handler

```python
class GitHubCopilotHandler(OutputHandler):
    def can_handle(self, app_info: Dict[str, Any]) -> bool:
        return 'github copilot' in app_info.get('name', '').lower()
    
    def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
        # GitHub Copilot specific implementation
        pass
```

### ChatGPT Handler

```python
class ChatGPTHandler(OutputHandler):
    def can_handle(self, app_info: Dict[str, Any]) -> bool:
        return 'chatgpt' in app_info.get('name', '').lower()
    
    def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
        # ChatGPT specific implementation
        pass
```

This extensibility system allows WhisperControl to work with any AI assistant or application, making it a truly universal voice dictation tool.
