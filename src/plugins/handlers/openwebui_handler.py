"""
OpenWebUI handler for browser-based OpenWebUI chat
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


class OpenWebUIHandler(OutputHandler):
    """Handler for OpenWebUI in browser"""
    
    def can_handle(self, app_info: Dict[str, Any]) -> bool:
        """Check if this is OpenWebUI in a browser"""
        app_name = app_info.get('name', '').lower()
        window_title = app_info.get('title', '').lower()
        
        # Check for browser applications
        browsers = ['safari', 'chrome', 'firefox', 'edge', 'brave', 'arc', 'opera']
        is_browser = any(browser in app_name for browser in browsers)
        
        # Check for OpenWebUI indicators in window title
        has_openwebui = (
            'openwebui' in window_title or
            'open webui' in window_title or
            'webui' in window_title
        )
        
        # Also check URL patterns if available
        # OpenWebUI typically has specific URL patterns
        
        return is_browser and has_openwebui
    
    def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
        """Send text to OpenWebUI in browser - ensure input field is focused"""
        try:
            # Copy to clipboard
            pyperclip.copy(text)
            
            # Wait for clipboard to update
            time.sleep(0.15)
            
            # IMPORTANT: Ensure OpenWebUI input field is focused
            # OpenWebUI typically has a textarea for input
            self._focus_openwebui_input()
            
            # Small delay to ensure focus is set
            time.sleep(0.15)
            
            # Paste the text
            with keyboard.Controller() as controller:
                controller.press(Key.cmd)
                controller.press('v')
                controller.release('v')
                controller.release(Key.cmd)
                
                # Wait for paste to complete
                time.sleep(0.15)
                
                # Press Enter to submit
                controller.press(Key.enter)
                controller.release(Key.enter)
            
            self.logger.info("Text sent to OpenWebUI and submitted")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send text to OpenWebUI: {e}")
            return False
    
    def _focus_openwebui_input(self) -> None:
        """Try to focus the OpenWebUI input field - multiple strategies"""
        try:
            with keyboard.Controller() as controller:
                # Strategy 1: Try Tab multiple times to reach input field
                # OpenWebUI input is usually the last focusable element
                for _ in range(3):
                    controller.press(Key.tab)
                    controller.release(Key.tab)
                    time.sleep(0.1)
                
                # Strategy 2: If Tab didn't work, try clicking in the page
                # But we can't click with keyboard, so try Escape to clear any modals
                controller.press(Key.esc)
                controller.release(Key.esc)
                time.sleep(0.1)
                
                # Strategy 3: Try Tab again after Escape
                controller.press(Key.tab)
                controller.release(Key.tab)
                time.sleep(0.1)
                
        except Exception as e:
            self.logger.debug(f"Could not focus OpenWebUI input: {e}")
    
    def get_priority(self) -> int:
        """High priority for OpenWebUI"""
        return 87
    
    def get_name(self) -> str:
        """Get handler name"""
        return "OpenWebUI"
    
    def get_description(self) -> str:
        """Get handler description"""
        return "Handler for OpenWebUI in browser windows"

