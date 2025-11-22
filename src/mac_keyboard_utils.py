"""
Mac-specific keyboard detection and mapping utilities
Optimized for Mac Ultra 3 and Ducky One 2 compatibility
"""

import subprocess
import platform
import logging
from typing import Dict, Any, Optional, List
import time


class MacKeyboardDetector:
    """Detects and manages Mac keyboard configurations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mac_version = self._get_mac_version()
        self.is_apple_silicon = self._is_apple_silicon()
        self.keyboard_info = self._detect_keyboard_info()
        
    def _get_mac_version(self) -> str:
        """Get macOS version"""
        try:
            result = subprocess.run(['sw_vers', '-productVersion'], 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            self.logger.warning(f"Could not get macOS version: {e}")
            return "Unknown"
    
    def _is_apple_silicon(self) -> bool:
        """Check if running on Apple Silicon"""
        try:
            result = subprocess.run(['uname', '-m'], 
                                  capture_output=True, text=True)
            return 'arm64' in result.stdout
        except Exception as e:
            self.logger.warning(f"Could not detect CPU architecture: {e}")
            return False
    
    def _detect_keyboard_info(self) -> Dict[str, Any]:
        """Detect connected keyboard information"""
        keyboard_info = {
            "connected_keyboards": [],
            "primary_keyboard": None,
            "ducky_detected": False,
            "mac_mode": True
        }
        
        try:
            # Get connected USB devices
            result = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                usb_output = result.stdout.lower()
                
                # Look for Ducky keyboards
                if 'ducky' in usb_output or 'one' in usb_output:
                    keyboard_info["ducky_detected"] = True
                    keyboard_info["primary_keyboard"] = "Ducky One 2"
                    
                    # Check if in Mac mode (this is a best guess)
                    keyboard_info["mac_mode"] = True
                    
                    self.logger.info("Ducky One 2 keyboard detected")
                
                # Extract all keyboard devices
                lines = result.stdout.split('\n')
                current_device = None
                
                for line in lines:
                    line = line.strip()
                    if 'keyboard' in line.lower() or 'ducky' in line.lower():
                        if current_device:
                            keyboard_info["connected_keyboards"].append(current_device)
                        current_device = line
                    elif current_device and line.startswith('Product ID:'):
                        keyboard_info["connected_keyboards"].append(current_device)
                        current_device = None
                
                if current_device:
                    keyboard_info["connected_keyboards"].append(current_device)
                    
        except Exception as e:
            self.logger.warning(f"Could not detect keyboard info: {e}")
        
        return keyboard_info
    
    def get_optimal_timing(self) -> Dict[str, float]:
        """Get optimal timing settings for Mac Ultra 3"""
        base_timing = {
            "key_press_delay": 0.01,
            "key_release_delay": 0.01,
            "paste_delay": 0.05,
            "command_delay": 0.02
        }
        
        # Apple Silicon optimizations
        if self.is_apple_silicon:
            base_timing.update({
                "key_press_delay": 0.005,
                "key_release_delay": 0.005,
                "paste_delay": 0.03,
                "command_delay": 0.01
            })
        
        # Mac Ultra 3 specific optimizations
        if "Ultra" in self.mac_version or self.is_apple_silicon:
            base_timing.update({
                "ultra_optimization": True,
                "enhanced_timing": True
            })
        
        return base_timing
    
    def get_ducky_mappings(self) -> Dict[str, str]:
        """Get Ducky One 2 key mappings for Mac"""
        return {
            # Function keys
            "f1": "f1",
            "f2": "f2",
            "f3": "f3",
            "f4": "f4",
            "f5": "f5",
            "f6": "f6",
            "f7": "f7",
            "f8": "f8",
            "f9": "f9",
            "f10": "f10",
            "f11": "f11",
            "f12": "f12",
            
            # Special Mac keys - Ducky One 2 specific mappings
            "cmd": "cmd",           # Command key (⌘)
            "windows": "cmd",       # Windows key maps to Command on Mac
            "option": "alt",        # Option key (⌥)
            "control": "ctrl",      # Control key (⌃)
            "shift": "shift",       # Shift key (⇧)
            
            # Navigation
            "home": "home",
            "end": "end",
            "page_up": "page_up",
            "page_down": "page_down",
            
            # Editing
            "insert": "insert",
            "delete": "delete",
            "backspace": "backspace",
            "enter": "enter",
            "tab": "tab",
            "space": "space",
            "escape": "esc",
            
            # Ducky One 2 specific keys
            "win": "cmd",           # Windows key → Command
            "alt": "alt",           # Alt key → Option
            "ctrl": "ctrl",         # Ctrl key → Control
            "meta": "cmd"           # Meta key → Command
        }
    
    def is_ducky_compatible(self) -> bool:
        """Check if Ducky One 2 is compatible with current Mac setup"""
        return (
            platform.system() == "Darwin" and
            self.keyboard_info.get("ducky_detected", False) and
            self.keyboard_info.get("mac_mode", True)
        )
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            "mac_version": self.mac_version,
            "is_apple_silicon": self.is_apple_silicon,
            "keyboard_info": self.keyboard_info,
            "optimal_timing": self.get_optimal_timing(),
            "ducky_mappings": self.get_ducky_mappings(),
            "is_ducky_compatible": self.is_ducky_compatible(),
            "platform": platform.system(),
            "architecture": platform.machine()
        }
    
    def optimize_for_ducky(self) -> Dict[str, Any]:
        """Get optimization settings specifically for Ducky One 2"""
        optimizations = {
            "enabled": self.is_ducky_compatible(),
            "timing": self.get_optimal_timing(),
            "key_mappings": self.get_ducky_mappings(),
            "mac_mode": True,
            "apple_silicon_optimized": self.is_apple_silicon,
            "ultra_3_optimized": "Ultra" in self.mac_version or self.is_apple_silicon
        }
        
        if optimizations["enabled"]:
            self.logger.info("Ducky One 2 optimizations enabled")
        else:
            self.logger.warning("Ducky One 2 optimizations disabled - compatibility issues detected")
        
        return optimizations


class MacKeyMapper:
    """Maps keys for Mac Ultra 3 and Ducky One 2 compatibility"""
    
    def __init__(self, detector: MacKeyboardDetector):
        self.detector = detector
        self.logger = logging.getLogger(__name__)
        self.mappings = detector.get_ducky_mappings()
        self.timing = detector.get_optimal_timing()
    
    def map_key(self, key: str) -> str:
        """Map a key to its Mac equivalent"""
        return self.mappings.get(key.lower(), key)
    
    def get_key_timing(self, key_type: str) -> float:
        """Get optimal timing for key type"""
        return self.timing.get(key_type, 0.01)
    
    def is_mac_key(self, key: str) -> bool:
        """Check if key is Mac-specific"""
        mac_keys = ['cmd', 'option', 'control', 'shift']
        return key.lower() in mac_keys
    
    def get_ducky_optimized_sequence(self, keys: List[str]) -> List[Dict[str, Any]]:
        """Get optimized key sequence for Ducky One 2"""
        sequence = []
        
        for key in keys:
            mapped_key = self.map_key(key)
            timing = self.get_key_timing("key_press_delay")
            
            sequence.append({
                "key": mapped_key,
                "timing": timing,
                "is_mac_key": self.is_mac_key(key),
                "ducky_optimized": True
            })
        
        return sequence
