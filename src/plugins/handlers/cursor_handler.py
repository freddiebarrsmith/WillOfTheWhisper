"""
Cursor IDE handler
"""

from typing import Dict, Any
import logging
import time
from pynput import keyboard
from pynput.keyboard import Key
import pyperclip

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from plugins import OutputHandler


class CursorHandler(OutputHandler):
    """Handler specifically for Cursor IDE"""
    
    def can_handle(self, app_info: Dict[str, Any]) -> bool:
        """Check if this is Cursor IDE"""
        app_name = app_info.get('name', '').lower()
        window_title = app_info.get('title', '').lower()
        
        # Check if it's Cursor
        is_cursor = 'cursor' in app_name
        
        # Check for Cursor-specific indicators
        has_cursor_features = (
            'cursor' in window_title or
            'ai' in window_title or
            'chat' in window_title or
            'composer' in window_title
        )
        
        return is_cursor or has_cursor_features
    
    def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
        """Send text to Cursor IDE"""
        try:
            # Copy to clipboard
            pyperclip.copy(text)
            
            # Small delay
            time.sleep(0.1)
            
            # Try to focus the Cursor chat/composer
            self._focus_cursor_input()
            
            # Paste the text
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
            
            self.logger.info("Text sent to Cursor IDE and submitted")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send text to Cursor: {e}")
            return False
    
    def _focus_cursor_input(self) -> None:
        """Try to focus the Cursor input field"""
        try:
            with keyboard.Controller() as controller:
                # Try Cmd+L to open chat (common Cursor shortcut)
                controller.press(Key.cmd)
                controller.press('l')
                controller.release('l')
                controller.release(Key.cmd)
                
                time.sleep(0.2)
                
                # Alternative: Try Cmd+K for composer
                controller.press(Key.cmd)
                controller.press('k')
                controller.release('k')
                controller.release(Key.cmd)
                
                time.sleep(0.1)
                
        except Exception as e:
            self.logger.debug(f"Could not focus Cursor input: {e}")
    
    def get_priority(self) -> int:
        """High priority for Cursor"""
        return 85
    
    def get_name(self) -> str:
        """Get handler name"""
        return "Cursor IDE"
    
    def get_description(self) -> str:
        """Get handler description"""
        return "Specialized handler for Cursor IDE with AI features"
