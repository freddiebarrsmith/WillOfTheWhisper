"""
Generic output handler for any application
"""

from typing import Dict, Any
import logging
from pynput import keyboard
from pynput.keyboard import Key
import pyperclip
import time

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
        """Send text using clipboard and paste"""
        try:
            # Copy to clipboard
            pyperclip.copy(text)
            
            # Small delay to ensure clipboard is ready
            time.sleep(0.1)
            
            # Paste using Cmd+V
            with keyboard.Controller() as controller:
                controller.press(Key.cmd)
                controller.press('v')
                controller.release('v')
                controller.release(Key.cmd)
            
            self.logger.info(f"Text pasted to {app_info.get('name', 'unknown app')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to paste text: {e}")
            return False
    
    def get_priority(self) -> int:
        """Lowest priority - fallback handler"""
        return 1
    
    def get_name(self) -> str:
        """Get handler name"""
        return "Generic"
    
    def get_description(self) -> str:
        """Get handler description"""
        return "Generic clipboard-based handler for any application"
