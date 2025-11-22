"""
Amazon Q Developer and Amazon Q Chat handler
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


class AmazonQHandler(OutputHandler):
    """Handler for Amazon Q Developer and Amazon Q Chat"""
    
    def can_handle(self, app_info: Dict[str, Any]) -> bool:
        """Check if this is Amazon Q Developer or Amazon Q Chat"""
        app_name = app_info.get('name', '').lower()
        window_title = app_info.get('title', '').lower()
        
        # Check for Amazon Q indicators
        is_amazon_q = (
            'amazon q' in app_name or
            'amazonq' in app_name or
            'aws q' in app_name or
            'q developer' in app_name or
            'q chat' in app_name
        )
        
        # Check window title for Amazon Q features
        has_q_features = (
            'amazon q' in window_title or
            'q developer' in window_title or
            'q chat' in window_title or
            'aws q' in window_title or
            'q:' in window_title  # Terminal prompt indicator
        )
        
        return is_amazon_q or has_q_features
    
    def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
        """Send text to Amazon Q Developer or Amazon Q Chat"""
        try:
            # Copy to clipboard
            pyperclip.copy(text)
            
            # Wait for clipboard to update
            time.sleep(0.1)
            
            # Check if it's a terminal-based Q chat
            window_title = app_info.get('title', '').lower()
            is_terminal = (
                'terminal' in window_title or
                'q:' in window_title or
                'aws q' in window_title
            )
            
            if is_terminal:
                # Terminal-based: Use Cmd+V
                self._send_to_terminal(text)
            else:
                # GUI-based: Try to focus input and paste
                self._send_to_gui(text, app_info)
            
            self.logger.info("Text sent to Amazon Q")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send text to Amazon Q: {e}")
            return False
    
    def _send_to_terminal(self, text: str) -> None:
        """Send text to terminal-based Amazon Q Chat - ensure focus"""
        with keyboard.Controller() as controller:
            # Ensure we're at the command prompt
            # Move cursor to end of line
            controller.press(Key.cmd)
            controller.press(Key.right)
            controller.release(Key.right)
            controller.release(Key.cmd)
            time.sleep(0.1)
            
            # Paste with Cmd+V
            controller.press(Key.cmd)
            controller.press('v')
            controller.release('v')
            controller.release(Key.cmd)
            
            time.sleep(0.15)
            
            # Press Enter to submit
            controller.press(Key.enter)
            controller.release(Key.enter)
    
    def _send_to_gui(self, text: str, app_info: Dict[str, Any]) -> None:
        """Send text to GUI-based Amazon Q Developer - ensure input focused"""
        with keyboard.Controller() as controller:
            # Try multiple strategies to focus input
            try:
                # Strategy 1: Try Cmd+L (common for chat focus)
                controller.press(Key.cmd)
                controller.press('l')
                controller.release('l')
                controller.release(Key.cmd)
                time.sleep(0.2)
            except:
                pass
            
            # Strategy 2: Try Tab to focus input field
            controller.press(Key.tab)
            controller.release(Key.tab)
            time.sleep(0.1)
            
            # Paste the text
            controller.press(Key.cmd)
            controller.press('v')
            controller.release('v')
            controller.release(Key.cmd)
            
            time.sleep(0.15)
            
            # Press Enter to submit
            controller.press(Key.enter)
            controller.release(Key.enter)
    
    def get_priority(self) -> int:
        """High priority for Amazon Q"""
        return 88
    
    def get_name(self) -> str:
        """Get handler name"""
        return "Amazon Q"
    
    def get_description(self) -> str:
        """Get handler description"""
        return "Handler for Amazon Q Developer and Amazon Q Chat (terminal and GUI)"

