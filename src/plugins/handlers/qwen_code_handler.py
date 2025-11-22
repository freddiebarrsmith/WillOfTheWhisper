"""
Qwen Code handler
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


class QwenCodeHandler(OutputHandler):
    """Handler specifically for Qwen Code"""
    
    def can_handle(self, app_info: Dict[str, Any]) -> bool:
        """Check if this is Qwen Code"""
        app_name = app_info.get('name', '').lower()
        window_title = app_info.get('title', '').lower()
        
        # Check if it's Qwen Code
        is_qwen = (
            'qwen' in app_name or
            'qwen code' in app_name or
            'tongyi' in app_name
        )
        
        # Check for Qwen-specific indicators
        has_qwen_features = (
            'qwen' in window_title or
            'tongyi' in window_title or
            'alibaba' in window_title or
            'ai assistant' in window_title
        )
        
        return is_qwen or has_qwen_features
    
    def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
        """Send text to Qwen Code"""
        try:
            # Copy to clipboard
            pyperclip.copy(text)
            
            # Small delay
            time.sleep(0.1)
            
            # Try to focus the Qwen input field
            self._focus_qwen_input()
            
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
            
            self.logger.info("Text sent to Qwen Code and submitted")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send text to Qwen: {e}")
            return False
    
    def _focus_qwen_input(self) -> None:
        """Try to focus the Qwen input field"""
        try:
            with keyboard.Controller() as controller:
                # Try common Qwen shortcuts
                # Cmd+Shift+A for AI assistant
                controller.press(Key.cmd)
                controller.press(Key.shift)
                controller.press('a')
                controller.release('a')
                controller.release(Key.shift)
                controller.release(Key.cmd)
                
                time.sleep(0.2)
                
                # Alternative: Try Cmd+J for chat panel
                controller.press(Key.cmd)
                controller.press('j')
                controller.release('j')
                controller.release(Key.cmd)
                
                time.sleep(0.1)
                
        except Exception as e:
            self.logger.debug(f"Could not focus Qwen input: {e}")
    
    def get_priority(self) -> int:
        """High priority for Qwen Code"""
        return 80
    
    def get_name(self) -> str:
        """Get handler name"""
        return "Qwen Code"
    
    def get_description(self) -> str:
        """Get handler description"""
        return "Specialized handler for Qwen Code AI assistant"
