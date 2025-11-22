"""
Generic output handler for any application
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


class GenericHandler(OutputHandler):
    """Generic handler that works with any application"""
    
    def can_handle(self, app_info: Dict[str, Any]) -> bool:
        """Generic handler can handle any application"""
        return True
    
    def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
        """Send text using clipboard and paste - ensure correct focus"""
        try:
            # Copy text to clipboard
            pyperclip.copy(text)
            
            # Wait a moment for clipboard to update
            time.sleep(0.15)
            
            # IMPORTANT: Ensure we're pasting into the correct field
            # First, try to focus the input field by clicking or using Tab
            self._ensure_input_focus()
            
            # Small delay to ensure focus is set
            time.sleep(0.1)
            
            # Simulate Cmd+V to paste
            with keyboard.Controller() as controller:
                controller.press(Key.cmd)
                controller.press('v')
                controller.release('v')
                controller.release(Key.cmd)
                
                # Wait a moment for paste to complete
                time.sleep(0.15)
                
                # Press Enter to submit
                controller.press(Key.enter)
                controller.release(Key.enter)
            
            self.logger.info(f"Sent text via clipboard and submitted: '{text[:50]}...'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send text: {e}")
            return False
    
    def _ensure_input_focus(self) -> None:
        """Try to ensure the input field is focused before pasting"""
        try:
            with keyboard.Controller() as controller:
                # Try Tab to move to input field (common pattern)
                # This works in many applications
                controller.press(Key.tab)
                controller.release(Key.tab)
                time.sleep(0.1)
                
                # Alternative: Try Shift+Tab to go back if we went too far
                # But for now, just Tab should work for most cases
                
        except Exception as e:
            self.logger.debug(f"Could not ensure input focus: {e}")
    
    def get_priority(self) -> int:
        """Generic handler has lowest priority"""
        return 1
    
    def get_name(self) -> str:
        """Get handler name"""
        return "Generic"
    
    def get_description(self) -> str:
        """Get handler description"""
        return "Generic clipboard-based handler for any application"
