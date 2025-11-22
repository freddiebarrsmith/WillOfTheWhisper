"""
Plugin system for extensible output handlers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path


class OutputHandler(ABC):
    """Abstract base class for output handlers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def can_handle(self, app_info: Dict[str, Any]) -> bool:
        """Check if this handler can handle the current application"""
        pass
    
    @abstractmethod
    def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
        """Send text to the target application"""
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """Get handler priority (higher = more preferred)"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get handler name"""
        pass
    
    def get_description(self) -> str:
        """Get handler description"""
        return f"{self.get_name()} output handler"


class PluginManager:
    """Manages output handler plugins"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.handlers: List[OutputHandler] = []
        self._load_handlers()
    
    def _load_handlers(self) -> None:
        """Load all available output handlers"""
        try:
            # Import all handler modules
            from .handlers.generic_handler import GenericHandler
            from .handlers.vscode_roo_handler import VSCodeRooHandler
            from .handlers.cursor_handler import CursorHandler
            from .handlers.qwen_code_handler import QwenCodeHandler
            from .handlers.ducky_mac_handler import DuckyMacHandler
            from .handlers.terminal_handler import TerminalHandler
            from .handlers.amazon_q_handler import AmazonQHandler
            from .handlers.openwebui_handler import OpenWebUIHandler
            
            # Create handler instances
            handler_classes = [
                DuckyMacHandler,  # Highest priority for Mac systems
                AmazonQHandler,   # High priority for Amazon Q
                OpenWebUIHandler, # High priority for OpenWebUI
                TerminalHandler,  # Medium-high priority for terminals
                VSCodeRooHandler,
                CursorHandler,
                QwenCodeHandler,
                GenericHandler   # Lowest priority - fallback
            ]
            
            for handler_class in handler_classes:
                try:
                    handler = handler_class(self.config)
                    self.handlers.append(handler)
                    self.logger.info(f"Loaded handler: {handler.get_name()}")
                except Exception as e:
                    self.logger.warning(f"Failed to load {handler_class.__name__}: {e}")
            
            # Sort by priority (highest first)
            self.handlers.sort(key=lambda h: h.get_priority(), reverse=True)
            
        except ImportError as e:
            self.logger.error(f"Failed to import handlers: {e}")
    
    def get_handler_for_app(self, app_info: Dict[str, Any]) -> Optional[OutputHandler]:
        """Get the best handler for the current application"""
        for handler in self.handlers:
            if handler.can_handle(app_info):
                self.logger.info(f"Selected handler: {handler.get_name()}")
                return handler
        
        self.logger.warning("No suitable handler found")
        return None
    
    def send_text(self, text: str, app_info: Dict[str, Any]) -> bool:
        """Send text using the appropriate handler"""
        handler = self.get_handler_for_app(app_info)
        
        if not handler:
            self.logger.error("No handler available for current application")
            return False
        
        try:
            return handler.send_text(text, app_info)
        except Exception as e:
            self.logger.error(f"Handler {handler.get_name()} failed: {e}")
            return False
    
    def get_available_handlers(self) -> List[Dict[str, Any]]:
        """Get list of available handlers"""
        return [
            {
                "name": handler.get_name(),
                "description": handler.get_description(),
                "priority": handler.get_priority()
            }
            for handler in self.handlers
        ]
    
    def reload_handlers(self) -> None:
        """Reload all handlers"""
        self.handlers.clear()
        self._load_handlers()
