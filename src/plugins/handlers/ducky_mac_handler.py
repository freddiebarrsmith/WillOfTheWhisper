"""
Ducky One 2 Mac Handler - Specialized for Mac Ultra 3 compatibility
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
from mac_keyboard_utils import MacKeyboardDetector, MacKeyMapper


class DuckyMacHandler(OutputHandler):
    """Handler specifically for Ducky One 2 keyboards on Mac Ultra 3"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.detector = MacKeyboardDetector()
        self.key_mapper = MacKeyMapper(self.detector)
        self.optimizations = self.detector.optimize_for_ducky()
        
    def can_handle(self, app_info: Dict[str, Any]) -> bool:
        """Check if this is a Mac system that can benefit from Ducky optimization"""
        # This handler is always available on Mac systems
        return self.detector.is_ducky_compatible()
    
    def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
        """Send text optimized for Ducky One 2 on Mac Ultra 3"""
        try:
            # Copy to clipboard first
            pyperclip.copy(text)
            
            # Get optimal timing for Mac Ultra 3
            timing = self.detector.get_optimal_timing()
            time.sleep(timing["paste_delay"])
            
            # Use Ducky-optimized key combinations
            self._send_with_ducky_optimization(text, app_info)
            
            self.logger.info("Text sent via Ducky Mac handler")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send text with Ducky handler: {e}")
            return False
    
    def _send_with_ducky_optimization(self, text: str, app_info: Dict[str, Any]) -> None:
        """Send text using Ducky One 2 optimized key combinations"""
        try:
            timing = self.detector.get_optimal_timing()
            controller = keyboard.Controller()
            
            # Try multiple paste methods for Ducky One 2 compatibility
            success = False
            
            # Method 1: Standard Mac Command+V
            try:
                controller.press(Key.cmd)
                time.sleep(timing["key_press_delay"])
                controller.press('v')
                controller.release('v')
                time.sleep(timing["key_release_delay"])
                controller.release(Key.cmd)
                success = True
                self.logger.info("Used Command+V paste method")
            except Exception as e:
                self.logger.debug(f"Command+V failed: {e}")
            
            # Method 2: Try Ctrl+V (Windows key on Ducky)
            if not success:
                try:
                    controller.press(Key.ctrl)
                    time.sleep(timing["key_press_delay"])
                    controller.press('v')
                    controller.release('v')
                    time.sleep(timing["key_release_delay"])
                    controller.release(Key.ctrl)
                    success = True
                    self.logger.info("Used Ctrl+V paste method")
                except Exception as e:
                    self.logger.debug(f"Ctrl+V failed: {e}")
            
            # Method 3: Try Windows key if available
            if not success:
                try:
                    # Map Windows key to Command key
                    controller.press(Key.cmd)  # Use Command as Windows key equivalent
                    time.sleep(timing["key_press_delay"])
                    controller.press('v')
                    controller.release('v')
                    time.sleep(timing["key_release_delay"])
                    controller.release(Key.cmd)
                    success = True
                    self.logger.info("Used Windows key equivalent paste method")
                except Exception as e:
                    self.logger.debug(f"Windows key equivalent failed: {e}")
            
            # Additional optimization for Apple Silicon
            if self.detector.is_apple_silicon and success:
                time.sleep(timing["command_delay"])
            
            # Press Enter to submit after paste
            if success:
                time.sleep(0.1)  # Wait for paste to complete
                controller.press(Key.enter)
                controller.release(Key.enter)
                self.logger.info("Pressed Enter to submit")
                    
        except Exception as e:
            self.logger.debug(f"Ducky optimization failed: {e}")
            # Fallback to standard paste
            self._standard_paste()
    
    def _standard_paste(self) -> None:
        """Standard paste as fallback"""
        try:
            controller = keyboard.Controller()
            controller.press(Key.cmd)
            controller.press('v')
            controller.release('v')
            controller.release(Key.cmd)
            
            # Press Enter to submit
            time.sleep(0.1)
            controller.press(Key.enter)
            controller.release(Key.enter)
        except Exception as e:
            self.logger.error(f"Standard paste failed: {e}")
    
    def send_special_command(self, command: str, app_info: Dict[str, Any]) -> bool:
        """Send special commands optimized for Ducky One 2"""
        try:
            timing = self.detector.get_optimal_timing()
            
            with keyboard.Controller() as controller:
                if command == "new_line":
                    # Ducky One 2 Enter key optimization
                    controller.press(Key.enter)
                    controller.release(Key.enter)
                    
                elif command == "tab":
                    # Ducky One 2 Tab key optimization
                    controller.press(Key.tab)
                    controller.release(Key.tab)
                    
                elif command == "space":
                    controller.press(Key.space)
                    controller.release(Key.space)
                    
                elif command == "backspace":
                    controller.press(Key.backspace)
                    controller.release(Key.backspace)
                    
                elif command == "delete":
                    controller.press(Key.delete)
                    controller.release(Key.delete)
                    
                elif command == "enter":
                    controller.press(Key.enter)
                    controller.release(Key.enter)
                    
                else:
                    return False
                
                # Use optimal timing for Mac Ultra 3
                time.sleep(timing["key_press_delay"])
                    
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to send special command: {e}")
            return False
    
    def get_priority(self) -> int:
        """High priority for Mac systems with Ducky keyboards"""
        return 95 if self.optimizations["enabled"] else 50
    
    def get_name(self) -> str:
        """Get handler name"""
        return "Ducky Mac Handler"
    
    def get_description(self) -> str:
        """Get handler description"""
        system_info = self.detector.get_system_info()
        return f"Ducky One 2 optimized handler for Mac Ultra 3 (macOS {system_info['mac_version']}, {'Apple Silicon' if system_info['is_apple_silicon'] else 'Intel'})"
    
    def get_keyboard_info(self) -> Dict[str, Any]:
        """Get keyboard and system information"""
        return self.detector.get_system_info()
