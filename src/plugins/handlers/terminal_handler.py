"""
Terminal handler for terminal applications (iTerm, Terminal.app, etc.)
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


class TerminalHandler(OutputHandler):
    """Handler for terminal applications"""
    
    def can_handle(self, app_info: Dict[str, Any]) -> bool:
        """Check if this is a terminal application"""
        app_name = app_info.get('name', '').lower()
        window_title = app_info.get('title', '').lower()
        
        # Common terminal applications
        terminal_apps = [
            'terminal',
            'iterm',
            'iterm2',
            'warp',
            'alacritty',
            'kitty',
            'hyper',
            'wezterm',
            'rio',
            'tabby'
        ]
        
        # Check if it's a terminal app
        is_terminal = any(term in app_name for term in terminal_apps)
        
        # Also check window title for terminal indicators
        has_terminal_features = (
            'terminal' in window_title or
            'shell' in window_title or
            'bash' in window_title or
            'zsh' in window_title or
            'fish' in window_title or
            'ssh' in window_title
        )
        
        return is_terminal or has_terminal_features
    
    def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
        """Send text to terminal application - ensure terminal is focused"""
        try:
            # Copy to clipboard
            pyperclip.copy(text)
            
            # Wait for clipboard to update
            time.sleep(0.15)  # Slightly longer for terminals
            
            # IMPORTANT: Ensure terminal input is focused
            # In terminals, we need to make sure we're at the command prompt
            self._ensure_terminal_focus()
            
            # Small delay to ensure focus
            time.sleep(0.1)
            
            # Terminals use Cmd+V for paste
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
            
            self.logger.info("Text sent to terminal and submitted")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send text to terminal: {e}")
            return False
    
    def _ensure_terminal_focus(self) -> None:
        """Ensure terminal input is focused before pasting"""
        try:
            with keyboard.Controller() as controller:
                # In terminals, we want to be at the end of the current line
                # Press Ctrl+E (end of line) or Cmd+Right to ensure we're at prompt
                # Actually, better to just ensure the terminal window is active
                # The user should already have clicked in the terminal
                # But we can try to move cursor to end of line
                controller.press(Key.cmd)
                controller.press(Key.right)
                controller.release(Key.right)
                controller.release(Key.cmd)
                time.sleep(0.05)
                
        except Exception as e:
            self.logger.debug(f"Could not ensure terminal focus: {e}")
    
    def get_priority(self) -> int:
        """Medium-high priority for terminals"""
        return 70
    
    def get_name(self) -> str:
        """Get handler name"""
        return "Terminal"
    
    def get_description(self) -> str:
        """Get handler description"""
        return "Handler for terminal applications (iTerm, Terminal.app, etc.)"

