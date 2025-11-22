"""
System integration module for clipboard and paste functionality
"""

import pyperclip
import logging
import time
from typing import Optional
from pynput import keyboard
from pynput.keyboard import Key, Listener

from config import Config


class SystemIntegration:
    """System integration for clipboard and paste operations"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Store original clipboard content
        self.original_clipboard: Optional[str] = None
    
    def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard"""
        try:
            if self.config.clear_clipboard_first:
                self.original_clipboard = pyperclip.paste()
            
            pyperclip.copy(text)
            self.logger.info(f"Text copied to clipboard: {len(text)} characters")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to copy to clipboard: {e}")
            return False
    
    def paste_to_active_application(self) -> bool:
        """Paste clipboard content to active application using Cmd+V and submit with Enter"""
        try:
            # Small delay to ensure clipboard is ready
            time.sleep(0.1)
            
            # Simulate Cmd+V
            with keyboard.Controller() as controller:
                controller.press(Key.cmd)
                controller.press('v')
                controller.release('v')
                controller.release(Key.cmd)
                
                # Wait a moment for paste to complete
                time.sleep(0.1)
                
                # Press Enter to submit
                controller.press(Key.enter)
                controller.release(Key.enter)
            
            self.logger.info("Pasted text to active application and submitted")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to paste to active application: {e}")
            return False
    
    def copy_and_paste(self, text: str) -> bool:
        """Copy text to clipboard and paste it to active application"""
        try:
            # Copy to clipboard
            if not self.copy_to_clipboard(text):
                return False
            
            # Paste to active application
            if self.config.auto_paste:
                if not self.paste_to_active_application():
                    return False
            
            self.logger.info("Text copied and pasted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to copy and paste: {e}")
            return False
    
    def restore_clipboard(self) -> bool:
        """Restore original clipboard content"""
        if self.original_clipboard is None:
            return True
        
        try:
            pyperclip.copy(self.original_clipboard)
            self.original_clipboard = None
            self.logger.info("Clipboard restored to original content")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore clipboard: {e}")
            return False
    
    def get_clipboard_content(self) -> str:
        """Get current clipboard content"""
        try:
            return pyperclip.paste()
        except Exception as e:
            self.logger.error(f"Failed to get clipboard content: {e}")
            return ""
    
    def clear_clipboard(self) -> bool:
        """Clear clipboard content"""
        try:
            pyperclip.copy("")
            self.logger.info("Clipboard cleared")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear clipboard: {e}")
            return False
    
    def send_text_directly(self, text: str) -> bool:
        """Send text directly to active application without using clipboard"""
        try:
            # Small delay to ensure focus
            time.sleep(0.1)
            
            # Type the text directly
            with keyboard.Controller() as controller:
                controller.type(text)
            
            self.logger.info(f"Text sent directly to active application: {len(text)} characters")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send text directly: {e}")
            return False
    
    def simulate_keystrokes(self, keys: list) -> bool:
        """Simulate a sequence of keystrokes"""
        try:
            with keyboard.Controller() as controller:
                for key in keys:
                    if isinstance(key, str):
                        controller.press(key)
                        controller.release(key)
                    elif isinstance(key, Key):
                        controller.press(key)
                        controller.release(key)
                    else:
                        # Handle key combinations
                        controller.press(key)
                
                # Release any remaining keys
                controller.release(Key.cmd)
                controller.release(Key.ctrl)
                controller.release(Key.alt)
                controller.release(Key.shift)
            
            self.logger.info(f"Simulated {len(keys)} keystrokes")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to simulate keystrokes: {e}")
            return False
    
    def send_special_command(self, command: str) -> bool:
        """Send special commands like 'new line', 'tab', etc."""
        command_map = {
            'new_line': '\n',
            'newline': '\n',
            'tab': '\t',
            'space': ' ',
            'backspace': Key.backspace,
            'delete': Key.delete,
            'enter': Key.enter,
            'escape': Key.esc,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'home': Key.home,
            'end': Key.end,
            'page_up': Key.page_up,
            'page_down': Key.page_down,
        }
        
        if command.lower() in command_map:
            special_key = command_map[command.lower()]
            
            if isinstance(special_key, str):
                return self.send_text_directly(special_key)
            else:
                return self.simulate_keystrokes([special_key])
        
        self.logger.warning(f"Unknown special command: {command}")
        return False
    
    def process_transcribed_text(self, text: str) -> bool:
        """Process transcribed text and handle special commands"""
        if not text.strip():
            self.logger.warning("Empty transcription, nothing to process")
            return False
        
        # Check for special commands
        words = text.strip().lower().split()
        
        # Handle common voice commands
        if len(words) >= 2 and words[0] in ['new', 'line']:
            return self.send_special_command('new_line')
        elif words[0] == 'tab':
            return self.send_special_command('tab')
        elif words[0] == 'space':
            return self.send_special_command('space')
        elif words[0] == 'backspace':
            return self.send_special_command('backspace')
        elif words[0] == 'delete':
            return self.send_special_command('delete')
        elif words[0] == 'enter':
            return self.send_special_command('enter')
        
        # Default: copy and paste the text
        return self.copy_and_paste(text)
