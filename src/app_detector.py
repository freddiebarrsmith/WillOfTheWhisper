"""
Application detection system for macOS
"""

import subprocess
import logging
from typing import Dict, Any, Optional
import json


class AppDetector:
    """Detects the currently active application on macOS"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_active_app_info(self) -> Dict[str, Any]:
        """Get information about the currently active application"""
        try:
            # Use AppleScript to get active application info
            # First get the app name using a simpler method
            script = '''
            tell application "System Events"
                try
                    set frontApp to first application process whose frontmost is true
                    set appName to name of frontApp
                    set windowTitle to ""
                    
                    try
                        set windowTitle to name of first window of frontApp
                    on error
                        set windowTitle to ""
                    end try
                    
                    return appName & "|" & windowTitle
                on error errMsg
                    return "Unknown|" & errMsg
                end try
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split('|')
                app_name = parts[0] if len(parts) > 0 and parts[0] != "Unknown" else "Unknown"
                window_title = parts[1] if len(parts) > 1 else ""
                
                # Try to get app path separately using a different method
                app_path = self._get_app_path_by_name(app_name)
                
                return {
                    'name': app_name,
                    'path': app_path,
                    'title': window_title,
                    'bundle_id': self._get_bundle_id(app_path) if app_path else "",
                    'is_ai_assistant': self._is_ai_assistant(app_name, window_title)
                }
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.logger.warning(f"Failed to get app info: {error_msg}")
                return self._get_fallback_info()
                
        except subprocess.TimeoutExpired:
            self.logger.warning("Timeout getting app info")
            return self._get_fallback_info()
        except Exception as e:
            self.logger.error(f"Error getting app info: {e}")
            return self._get_fallback_info()
    
    def _get_app_path_by_name(self, app_name: str) -> str:
        """Get app path by name using a safer method"""
        try:
            if not app_name or app_name == "Unknown":
                return ""
            
            # Use mdfind to find the app
            script = f'''
            tell application "System Events"
                try
                    set appPath to POSIX path of (path to application "{app_name}")
                    return appPath
                on error
                    return ""
                end try
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            
        except Exception as e:
            self.logger.debug(f"Could not get app path for {app_name}: {e}")
        
        return ""
    
    def _get_bundle_id(self, app_path: str) -> str:
        """Get bundle ID from app path"""
        try:
            if not app_path:
                return ""
            
            # Extract bundle ID from app path
            script = f'''
            tell application "System Events"
                set bundleID to bundle identifier of application file "{app_path}"
                return bundleID
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            
        except Exception as e:
            self.logger.debug(f"Could not get bundle ID: {e}")
        
        return ""
    
    def _is_ai_assistant(self, app_name: str, window_title: str) -> bool:
        """Check if the app appears to be an AI assistant"""
        ai_indicators = [
            'cursor', 'roo', 'qwen', 'tongyi', 'copilot', 'chatgpt',
            'claude', 'bard', 'ai', 'assistant', 'chat', 'prompt'
        ]
        
        text_to_check = f"{app_name} {window_title}".lower()
        
        return any(indicator in text_to_check for indicator in ai_indicators)
    
    def _get_fallback_info(self) -> Dict[str, Any]:
        """Get fallback app info when detection fails"""
        return {
            'name': 'Unknown',
            'path': '',
            'title': '',
            'bundle_id': '',
            'is_ai_assistant': False
        }
    
    def get_app_list(self) -> list:
        """Get list of running applications"""
        try:
            script = '''
            tell application "System Events"
                set appList to {}
                repeat with appProcess in (every application process)
                    set appName to name of appProcess
                    set appPath to POSIX path of (path to appProcess)
                    set end of appList to appName & "|" & appPath
                end repeat
                return appList as string
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                apps = []
                for line in result.stdout.strip().split('\n'):
                    if '|' in line:
                        name, path = line.split('|', 1)
                        apps.append({'name': name.strip(), 'path': path.strip()})
                return apps
            
        except Exception as e:
            self.logger.error(f"Error getting app list: {e}")
        
        return []
    
    def is_app_running(self, app_name: str) -> bool:
        """Check if a specific app is running"""
        try:
            script = f'''
            tell application "System Events"
                return exists (processes whose name is "{app_name}")
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            return result.returncode == 0 and 'true' in result.stdout.lower()
            
        except Exception as e:
            self.logger.debug(f"Error checking if {app_name} is running: {e}")
            return False
    
    def get_window_info(self) -> Dict[str, Any]:
        """Get detailed window information"""
        try:
            script = '''
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set appName to name of frontApp
                set windowList to {}
                repeat with win in windows of frontApp
                    set winTitle to name of win
                    set winPosition to position of win
                    set winSize to size of win
                    set end of windowList to winTitle & "|" & (item 1 of winPosition) & "," & (item 2 of winPosition) & "|" & (item 1 of winSize) & "," & (item 2 of winSize)
                end repeat
                return appName & "||" & (windowList as string)
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                parts = result.stdout.strip().split('||')
                app_name = parts[0] if len(parts) > 0 else "Unknown"
                windows_info = parts[1] if len(parts) > 1 else ""
                
                windows = []
                for win_info in windows_info.split('\n'):
                    if '|' in win_info:
                        title, position, size = win_info.split('|')
                        windows.append({
                            'title': title,
                            'position': position,
                            'size': size
                        })
                
                return {
                    'app_name': app_name,
                    'windows': windows,
                    'active_window': windows[0] if windows else None
                }
            
        except Exception as e:
            self.logger.debug(f"Error getting window info: {e}")
        
        return {'app_name': 'Unknown', 'windows': [], 'active_window': None}
