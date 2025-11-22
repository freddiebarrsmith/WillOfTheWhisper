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
        
        # Get terminal config for custom app names
        terminal_config = self.config.get('ai_assistants', {}).get('terminal', {})
        detection_config = terminal_config.get('detection', {})
        config_app_names = [name.lower() for name in detection_config.get('app_names', [])]
        config_keywords = [kw.lower() for kw in detection_config.get('window_keywords', [])]
        
        # Common terminal applications (merge with config)
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
            'tabby',
            'gnome-terminal',
            'konsole',
            'xterm',
            'urxvt',
            'st',
            'tilix',
            'terminator'
        ] + config_app_names
        
        # Check if it's a terminal app
        is_terminal = any(term in app_name for term in terminal_apps)
        
        # Also check window title for terminal indicators
        terminal_keywords = [
            'terminal', 'shell', 'bash', 'zsh', 'fish', 'ssh', 'powershell',
            'cmd', 'command', 'prompt', 'tty', 'pts', 'console'
        ] + config_keywords
        
        has_terminal_features = any(kw in window_title for kw in terminal_keywords)
        
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
            
            # Get config for terminal handler
            terminal_config = self.config.get('ai_assistants', {}).get('terminal', {})
            auto_submit = terminal_config.get('auto_submit', True)  # Default to True for convenience
            
            # Terminals use Cmd+V for paste
            with keyboard.Controller() as controller:
                controller.press(Key.cmd)
                controller.press('v')
                controller.release('v')
                controller.release(Key.cmd)
                
                # Wait for paste to complete
                time.sleep(0.15)
                
                # Press Enter to submit if auto_submit is enabled
                if auto_submit:
                    controller.press(Key.enter)
                    controller.release(Key.enter)
                    self.logger.info("Text sent to terminal and submitted")
                else:
                    self.logger.info("Text pasted to terminal (not auto-submitted)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send text to terminal: {e}")
            return False
    
    def _ensure_terminal_focus(self) -> None:
        """Ensure terminal input is focused before pasting"""
        try:
            with keyboard.Controller() as controller:
                # In terminals, we want to be at the end of the current line
                # Try multiple methods to ensure we're at the prompt
                
                # Method 1: Move cursor to end of line (Cmd+Right on Mac)
                controller.press(Key.cmd)
                controller.press(Key.right)
                controller.release(Key.right)
                controller.release(Key.cmd)
                time.sleep(0.05)
                
                # Method 2: Alternative - Ctrl+E (end of line) for some terminals
                # This works in bash/zsh
                try:
                    controller.press(Key.ctrl)
                    controller.press('e')
                    controller.release('e')
                    controller.release(Key.ctrl)
                    time.sleep(0.05)
                except:
                    pass  # Some terminals might not support this
                
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

