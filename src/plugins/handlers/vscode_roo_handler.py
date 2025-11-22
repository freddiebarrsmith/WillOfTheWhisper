"""
VS Code Roo extension handler
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


class VSCodeRooHandler(OutputHandler):
    """Handler specifically for VS Code Roo extension"""
    
    def can_handle(self, app_info: Dict[str, Any]) -> bool:
        """Check if this is VS Code with Roo extension"""
        app_name = app_info.get('name', '').lower()
        window_title = app_info.get('title', '').lower()
        
        # Check if it's VS Code
        is_vscode = 'visual studio code' in app_name or 'code' in app_name
        
        # Check for Roo-specific indicators
        has_roo = (
            'roo' in window_title or
            'ai assistant' in window_title or
            'chat' in window_title or
            'prompt' in window_title
        )
        
        return is_vscode and has_roo
    
    def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
        """Send text to VS Code Roo extension"""
        try:
            # Copy to clipboard
            pyperclip.copy(text)
            
            # Small delay
            time.sleep(0.1)
            
            # Try to focus the Roo input field first
            # Look for common Roo input field selectors
            self._focus_roo_input()
            
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
            
            self.logger.info("Text sent to VS Code Roo extension and submitted")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send text to Roo: {e}")
            return False
    
    def _focus_roo_input(self) -> None:
        """Try to focus the Roo input field - simplified to avoid triggering Electron errors"""
        try:
            with keyboard.Controller() as controller:
                # Don't try to open command palette - just use Tab to focus input
                # This is safer and won't trigger VS Code development mode issues
                controller.press(Key.tab)
                controller.release(Key.tab)
                time.sleep(0.1)
                
                # Try Tab again if needed (Roo input might be deeper in focus order)
                controller.press(Key.tab)
                controller.release(Key.tab)
                time.sleep(0.1)
                
        except Exception as e:
            self.logger.debug(f"Could not focus Roo input: {e}")
    
    def get_priority(self) -> int:
        """High priority for VS Code Roo"""
        return 90
    
    def get_name(self) -> str:
        """Get handler name"""
        return "VS Code Roo"
    
    def get_description(self) -> str:
        """Get handler description"""
        return "Specialized handler for VS Code Roo AI assistant extension"
