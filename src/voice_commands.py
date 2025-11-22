"""
Advanced voice command system for complex operations
"""

import logging
import time
import threading
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re


class CommandType(Enum):
    """Types of voice commands"""
    TEXT_INPUT = "text_input"
    SYSTEM_ACTION = "system_action"
    CODE_GENERATION = "code_generation"
    FILE_OPERATION = "file_operation"
    NAVIGATION = "navigation"
    EDITING = "editing"
    DEBUGGING = "debugging"


@dataclass
class VoiceCommand:
    """Represents a voice command"""
    pattern: str
    command_type: CommandType
    handler: Callable
    description: str
    examples: List[str]
    requires_confirmation: bool = False
    priority: int = 1


class VoiceCommandProcessor:
    """Advanced voice command processing system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.commands: List[VoiceCommand] = []
        self.context_history: List[str] = []
        self.active_context: Optional[Dict[str, Any]] = None
        
        # Initialize command registry
        self._register_commands()
    
    def _register_commands(self) -> None:
        """Register all available voice commands"""
        
        # Text input commands
        self._register_text_commands()
        
        # System action commands
        self._register_system_commands()
        
        # Code generation commands
        self._register_code_commands()
        
        # File operation commands
        self._register_file_commands()
        
        # Navigation commands
        self._register_navigation_commands()
        
        # Editing commands
        self._register_editing_commands()
        
        # Debugging commands
        self._register_debugging_commands()
    
    def _register_text_commands(self) -> None:
        """Register text input commands"""
        commands = [
            VoiceCommand(
                pattern=r"^(type|write|say)\s+(.+)$",
                command_type=CommandType.TEXT_INPUT,
                handler=self._handle_type_text,
                description="Type or write text",
                examples=["type hello world", "write function name", "say variable name"]
            ),
            VoiceCommand(
                pattern=r"^(new line|line break|enter)$",
                command_type=CommandType.TEXT_INPUT,
                handler=self._handle_new_line,
                description="Insert new line",
                examples=["new line", "line break", "enter"]
            ),
            VoiceCommand(
                pattern=r"^(tab|indent)$",
                command_type=CommandType.TEXT_INPUT,
                handler=self._handle_tab,
                description="Insert tab or indent",
                examples=["tab", "indent"]
            ),
            VoiceCommand(
                pattern=r"^(space|spaces?)$",
                command_type=CommandType.TEXT_INPUT,
                handler=self._handle_space,
                description="Insert space(s)",
                examples=["space", "spaces"]
            ),
        ]
        self.commands.extend(commands)
    
    def _register_system_commands(self) -> None:
        """Register system action commands"""
        commands = [
            VoiceCommand(
                pattern=r"^(save|save file)$",
                command_type=CommandType.SYSTEM_ACTION,
                handler=self._handle_save,
                description="Save current file",
                examples=["save", "save file"]
            ),
            VoiceCommand(
                pattern=r"^(undo|go back)$",
                command_type=CommandType.SYSTEM_ACTION,
                handler=self._handle_undo,
                description="Undo last action",
                examples=["undo", "go back"]
            ),
            VoiceCommand(
                pattern=r"^(redo|repeat)$",
                command_type=CommandType.SYSTEM_ACTION,
                handler=self._handle_redo,
                description="Redo last undone action",
                examples=["redo", "repeat"]
            ),
            VoiceCommand(
                pattern=r"^(copy|copy text)$",
                command_type=CommandType.SYSTEM_ACTION,
                handler=self._handle_copy,
                description="Copy selected text",
                examples=["copy", "copy text"]
            ),
            VoiceCommand(
                pattern=r"^(paste|paste text)$",
                command_type=CommandType.SYSTEM_ACTION,
                handler=self._handle_paste,
                description="Paste from clipboard",
                examples=["paste", "paste text"]
            ),
            VoiceCommand(
                pattern=r"^(cut|cut text)$",
                command_type=CommandType.SYSTEM_ACTION,
                handler=self._handle_cut,
                description="Cut selected text",
                examples=["cut", "cut text"]
            ),
            VoiceCommand(
                pattern=r"^(select all|select everything)$",
                command_type=CommandType.SYSTEM_ACTION,
                handler=self._handle_select_all,
                description="Select all text",
                examples=["select all", "select everything"]
            ),
        ]
        self.commands.extend(commands)
    
    def _register_code_commands(self) -> None:
        """Register code generation commands"""
        commands = [
            VoiceCommand(
                pattern=r"^(create|make|add)\s+(?:a\s+)?function\s+(.+)$",
                command_type=CommandType.CODE_GENERATION,
                handler=self._handle_create_function,
                description="Create a function",
                examples=["create function calculateSum", "make function getUserData", "add function validateInput"]
            ),
            VoiceCommand(
                pattern=r"^(create|make|add)\s+(?:a\s+)?class\s+(.+)$",
                command_type=CommandType.CODE_GENERATION,
                handler=self._handle_create_class,
                description="Create a class",
                examples=["create class User", "make class DatabaseConnection", "add class ApiClient"]
            ),
            VoiceCommand(
                pattern=r"^(create|make|add)\s+(?:a\s+)?variable\s+(.+)$",
                command_type=CommandType.CODE_GENERATION,
                handler=self._handle_create_variable,
                description="Create a variable",
                examples=["create variable userName", "make variable config", "add variable result"]
            ),
            VoiceCommand(
                pattern=r"^(create|make|add)\s+(?:a\s+)?constant\s+(.+)$",
                command_type=CommandType.CODE_GENERATION,
                handler=self._handle_create_constant,
                description="Create a constant",
                examples=["create constant API_URL", "make constant MAX_RETRIES", "add constant DEFAULT_TIMEOUT"]
            ),
            VoiceCommand(
                pattern=r"^(add|insert)\s+(?:a\s+)?comment\s+(.+)$",
                command_type=CommandType.CODE_GENERATION,
                handler=self._handle_add_comment,
                description="Add a comment",
                examples=["add comment this function calculates the sum", "insert comment TODO: implement error handling"]
            ),
            VoiceCommand(
                pattern=r"^(add|insert)\s+(?:a\s+)?if\s+statement\s+(.+)$",
                command_type=CommandType.CODE_GENERATION,
                handler=self._handle_add_if_statement,
                description="Add an if statement",
                examples=["add if statement user is logged in", "insert if statement data is not null"]
            ),
            VoiceCommand(
                pattern=r"^(add|insert)\s+(?:a\s+)?for\s+loop\s+(.+)$",
                command_type=CommandType.CODE_GENERATION,
                handler=self._handle_add_for_loop,
                description="Add a for loop",
                examples=["add for loop iterate through items", "insert for loop process each user"]
            ),
            VoiceCommand(
                pattern=r"^(add|insert)\s+(?:a\s+)?try\s+catch\s+(.+)$",
                command_type=CommandType.CODE_GENERATION,
                handler=self._handle_add_try_catch,
                description="Add try-catch block",
                examples=["add try catch handle API errors", "insert try catch validate input"]
            ),
        ]
        self.commands.extend(commands)
    
    def _register_file_commands(self) -> None:
        """Register file operation commands"""
        commands = [
            VoiceCommand(
                pattern=r"^(open|open file)\s+(.+)$",
                command_type=CommandType.FILE_OPERATION,
                handler=self._handle_open_file,
                description="Open a file",
                examples=["open file main.js", "open file index.html", "open file package.json"]
            ),
            VoiceCommand(
                pattern=r"^(create|new|make)\s+(?:a\s+)?file\s+(.+)$",
                command_type=CommandType.FILE_OPERATION,
                handler=self._handle_create_file,
                description="Create a new file",
                examples=["create file utils.js", "new file config.py", "make file README.md"]
            ),
            VoiceCommand(
                pattern=r"^(close|close file)$",
                command_type=CommandType.FILE_OPERATION,
                handler=self._handle_close_file,
                description="Close current file",
                examples=["close", "close file"]
            ),
            VoiceCommand(
                pattern=r"^(rename|rename file)\s+(.+)$",
                command_type=CommandType.FILE_OPERATION,
                handler=self._handle_rename_file,
                description="Rename current file",
                examples=["rename file new_name.js", "rename file updated_config.py"]
            ),
        ]
        self.commands.extend(commands)
    
    def _register_navigation_commands(self) -> None:
        """Register navigation commands"""
        commands = [
            VoiceCommand(
                pattern=r"^(go to|navigate to|jump to)\s+(.+)$",
                command_type=CommandType.NAVIGATION,
                handler=self._handle_navigate_to,
                description="Navigate to a location",
                examples=["go to line 50", "navigate to function calculateSum", "jump to class User"]
            ),
            VoiceCommand(
                pattern=r"^(find|search for|look for)\s+(.+)$",
                command_type=CommandType.NAVIGATION,
                handler=self._handle_find_text,
                description="Find text in file",
                examples=["find variable name", "search for function call", "look for error message"]
            ),
            VoiceCommand(
                pattern=r"^(go back|previous|back)$",
                command_type=CommandType.NAVIGATION,
                handler=self._handle_go_back,
                description="Go back to previous location",
                examples=["go back", "previous", "back"]
            ),
            VoiceCommand(
                pattern=r"^(go forward|next|forward)$",
                command_type=CommandType.NAVIGATION,
                handler=self._handle_go_forward,
                description="Go forward to next location",
                examples=["go forward", "next", "forward"]
            ),
        ]
        self.commands.extend(commands)
    
    def _register_editing_commands(self) -> None:
        """Register editing commands"""
        commands = [
            VoiceCommand(
                pattern=r"^(delete|remove)\s+(.+)$",
                command_type=CommandType.EDITING,
                handler=self._handle_delete_text,
                description="Delete specified text",
                examples=["delete variable name", "remove function call", "delete comment"]
            ),
            VoiceCommand(
                pattern=r"^(replace|change)\s+(.+)\s+with\s+(.+)$",
                command_type=CommandType.EDITING,
                handler=self._handle_replace_text,
                description="Replace text with new text",
                examples=["replace old name with new name", "change function name with updated name"]
            ),
            VoiceCommand(
                pattern=r"^(move|move line)\s+(up|down|left|right)$",
                command_type=CommandType.EDITING,
                handler=self._handle_move_line,
                description="Move current line",
                examples=["move line up", "move line down", "move line left", "move line right"]
            ),
            VoiceCommand(
                pattern=r"^(duplicate|copy line)$",
                command_type=CommandType.EDITING,
                handler=self._handle_duplicate_line,
                description="Duplicate current line",
                examples=["duplicate", "copy line"]
            ),
            VoiceCommand(
                pattern=r"^(format|format code|beautify)$",
                command_type=CommandType.EDITING,
                handler=self._handle_format_code,
                description="Format code",
                examples=["format", "format code", "beautify"]
            ),
        ]
        self.commands.extend(commands)
    
    def _register_debugging_commands(self) -> None:
        """Register debugging commands"""
        commands = [
            VoiceCommand(
                pattern=r"^(add|insert|set)\s+(?:a\s+)?breakpoint$",
                command_type=CommandType.DEBUGGING,
                handler=self._handle_add_breakpoint,
                description="Add a breakpoint",
                examples=["add breakpoint", "insert breakpoint", "set breakpoint"]
            ),
            VoiceCommand(
                pattern=r"^(remove|delete|clear)\s+(?:a\s+)?breakpoint$",
                command_type=CommandType.DEBUGGING,
                handler=self._handle_remove_breakpoint,
                description="Remove breakpoint",
                examples=["remove breakpoint", "delete breakpoint", "clear breakpoint"]
            ),
            VoiceCommand(
                pattern=r"^(debug|start debugging|run debugger)$",
                command_type=CommandType.DEBUGGING,
                handler=self._handle_start_debugging,
                description="Start debugging",
                examples=["debug", "start debugging", "run debugger"]
            ),
            VoiceCommand(
                pattern=r"^(stop|stop debugging|end debugging)$",
                command_type=CommandType.DEBUGGING,
                handler=self._handle_stop_debugging,
                description="Stop debugging",
                examples=["stop", "stop debugging", "end debugging"]
            ),
            VoiceCommand(
                pattern=r"^(step|step over|next step)$",
                command_type=CommandType.DEBUGGING,
                handler=self._handle_step_over,
                description="Step over in debugger",
                examples=["step", "step over", "next step"]
            ),
            VoiceCommand(
                pattern=r"^(step into|step in)$",
                command_type=CommandType.DEBUGGING,
                handler=self._handle_step_into,
                description="Step into in debugger",
                examples=["step into", "step in"]
            ),
            VoiceCommand(
                pattern=r"^(step out|step return)$",
                command_type=CommandType.DEBUGGING,
                handler=self._handle_step_out,
                description="Step out in debugger",
                examples=["step out", "step return"]
            ),
        ]
        self.commands.extend(commands)
    
    def process_command(self, text: str) -> Optional[str]:
        """Process voice command and return result"""
        try:
            # Clean and normalize text
            text = text.strip().lower()
            
            # Add to context history
            self.context_history.append(text)
            if len(self.context_history) > 10:
                self.context_history.pop(0)
            
            # Find matching command
            for command in sorted(self.commands, key=lambda c: c.priority, reverse=True):
                match = re.match(command.pattern, text)
                if match:
                    self.logger.info(f"Matched command: {command.description}")
                    
                    # Execute command
                    result = command.handler(match.groups())
                    
                    if result:
                        return result
            
            # No command matched, return as regular text
            return text
            
        except Exception as e:
            self.logger.error(f"Command processing failed: {e}")
            return text
    
    # Command handlers
    def _handle_type_text(self, groups: tuple) -> str:
        """Handle type text command"""
        return groups[1] if len(groups) > 1 else ""
    
    def _handle_new_line(self, groups: tuple) -> str:
        """Handle new line command"""
        return "\n"
    
    def _handle_tab(self, groups: tuple) -> str:
        """Handle tab command"""
        return "\t"
    
    def _handle_space(self, groups: tuple) -> str:
        """Handle space command"""
        return " "
    
    def _handle_save(self, groups: tuple) -> str:
        """Handle save command"""
        # This would trigger a system action
        return "SAVE_FILE"
    
    def _handle_undo(self, groups: tuple) -> str:
        """Handle undo command"""
        return "UNDO"
    
    def _handle_redo(self, groups: tuple) -> str:
        """Handle redo command"""
        return "REDO"
    
    def _handle_copy(self, groups: tuple) -> str:
        """Handle copy command"""
        return "COPY"
    
    def _handle_paste(self, groups: tuple) -> str:
        """Handle paste command"""
        return "PASTE"
    
    def _handle_cut(self, groups: tuple) -> str:
        """Handle cut command"""
        return "CUT"
    
    def _handle_select_all(self, groups: tuple) -> str:
        """Handle select all command"""
        return "SELECT_ALL"
    
    def _handle_create_function(self, groups: tuple) -> str:
        """Handle create function command"""
        func_name = groups[1] if len(groups) > 1 else "newFunction"
        return f"function {func_name}() {{\n    // TODO: implement function\n}}"
    
    def _handle_create_class(self, groups: tuple) -> str:
        """Handle create class command"""
        class_name = groups[1] if len(groups) > 1 else "NewClass"
        return f"class {class_name} {{\n    constructor() {{\n        // TODO: implement constructor\n    }}\n}}"
    
    def _handle_create_variable(self, groups: tuple) -> str:
        """Handle create variable command"""
        var_name = groups[1] if len(groups) > 1 else "newVariable"
        return f"let {var_name} = null;"
    
    def _handle_create_constant(self, groups: tuple) -> str:
        """Handle create constant command"""
        const_name = groups[1] if len(groups) > 1 else "NEW_CONSTANT"
        return f"const {const_name} = null;"
    
    def _handle_add_comment(self, groups: tuple) -> str:
        """Handle add comment command"""
        comment_text = groups[1] if len(groups) > 1 else "TODO"
        return f"// {comment_text}"
    
    def _handle_add_if_statement(self, groups: tuple) -> str:
        """Handle add if statement command"""
        condition = groups[1] if len(groups) > 1 else "condition"
        return f"if ({condition}) {{\n    // TODO: implement logic\n}}"
    
    def _handle_add_for_loop(self, groups: tuple) -> str:
        """Handle add for loop command"""
        loop_desc = groups[1] if len(groups) > 1 else "items"
        return f"for (let i = 0; i < {loop_desc}.length; i++) {{\n    // TODO: implement loop logic\n}}"
    
    def _handle_add_try_catch(self, groups: tuple) -> str:
        """Handle add try-catch command"""
        error_desc = groups[1] if len(groups) > 1 else "error"
        return f"try {{\n    // TODO: implement try block\n}} catch ({error_desc}) {{\n    // TODO: handle error\n}}"
    
    def _handle_open_file(self, groups: tuple) -> str:
        """Handle open file command"""
        filename = groups[1] if len(groups) > 1 else ""
        return f"OPEN_FILE:{filename}"
    
    def _handle_create_file(self, groups: tuple) -> str:
        """Handle create file command"""
        filename = groups[1] if len(groups) > 1 else "new_file"
        return f"CREATE_FILE:{filename}"
    
    def _handle_close_file(self, groups: tuple) -> str:
        """Handle close file command"""
        return "CLOSE_FILE"
    
    def _handle_rename_file(self, groups: tuple) -> str:
        """Handle rename file command"""
        new_name = groups[1] if len(groups) > 1 else ""
        return f"RENAME_FILE:{new_name}"
    
    def _handle_navigate_to(self, groups: tuple) -> str:
        """Handle navigate to command"""
        target = groups[1] if len(groups) > 1 else ""
        return f"NAVIGATE_TO:{target}"
    
    def _handle_find_text(self, groups: tuple) -> str:
        """Handle find text command"""
        search_text = groups[1] if len(groups) > 1 else ""
        return f"FIND_TEXT:{search_text}"
    
    def _handle_go_back(self, groups: tuple) -> str:
        """Handle go back command"""
        return "GO_BACK"
    
    def _handle_go_forward(self, groups: tuple) -> str:
        """Handle go forward command"""
        return "GO_FORWARD"
    
    def _handle_delete_text(self, groups: tuple) -> str:
        """Handle delete text command"""
        text_to_delete = groups[1] if len(groups) > 1 else ""
        return f"DELETE_TEXT:{text_to_delete}"
    
    def _handle_replace_text(self, groups: tuple) -> str:
        """Handle replace text command"""
        old_text = groups[1] if len(groups) > 1 else ""
        new_text = groups[2] if len(groups) > 2 else ""
        return f"REPLACE_TEXT:{old_text}:{new_text}"
    
    def _handle_move_line(self, groups: tuple) -> str:
        """Handle move line command"""
        direction = groups[1] if len(groups) > 1 else "up"
        return f"MOVE_LINE:{direction}"
    
    def _handle_duplicate_line(self, groups: tuple) -> str:
        """Handle duplicate line command"""
        return "DUPLICATE_LINE"
    
    def _handle_format_code(self, groups: tuple) -> str:
        """Handle format code command"""
        return "FORMAT_CODE"
    
    def _handle_add_breakpoint(self, groups: tuple) -> str:
        """Handle add breakpoint command"""
        return "ADD_BREAKPOINT"
    
    def _handle_remove_breakpoint(self, groups: tuple) -> str:
        """Handle remove breakpoint command"""
        return "REMOVE_BREAKPOINT"
    
    def _handle_start_debugging(self, groups: tuple) -> str:
        """Handle start debugging command"""
        return "START_DEBUGGING"
    
    def _handle_stop_debugging(self, groups: tuple) -> str:
        """Handle stop debugging command"""
        return "STOP_DEBUGGING"
    
    def _handle_step_over(self, groups: tuple) -> str:
        """Handle step over command"""
        return "STEP_OVER"
    
    def _handle_step_into(self, groups: tuple) -> str:
        """Handle step into command"""
        return "STEP_INTO"
    
    def _handle_step_out(self, groups: tuple) -> str:
        """Handle step out command"""
        return "STEP_OUT"
    
    def get_available_commands(self) -> List[Dict[str, Any]]:
        """Get list of available commands"""
        return [
            {
                "pattern": cmd.pattern,
                "type": cmd.command_type.value,
                "description": cmd.description,
                "examples": cmd.examples,
                "priority": cmd.priority
            }
            for cmd in self.commands
        ]
    
    def get_commands_by_type(self, command_type: CommandType) -> List[VoiceCommand]:
        """Get commands by type"""
        return [cmd for cmd in self.commands if cmd.command_type == command_type]
    
    def add_custom_command(self, command: VoiceCommand) -> None:
        """Add a custom command"""
        self.commands.append(command)
        self.logger.info(f"Added custom command: {command.description}")
    
    def remove_command(self, pattern: str) -> bool:
        """Remove a command by pattern"""
        for i, cmd in enumerate(self.commands):
            if cmd.pattern == pattern:
                removed = self.commands.pop(i)
                self.logger.info(f"Removed command: {removed.description}")
                return True
        return False
