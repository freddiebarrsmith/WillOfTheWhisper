"""
Prompt-focused voice command system for AI assistants
"""

import logging
import time
import threading
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re


class PromptCommandType(Enum):
    """Types of prompt-focused voice commands"""
    PROMPT_INPUT = "prompt_input"
    PROMPT_MODIFICATION = "prompt_modification"
    PROMPT_TEMPLATE = "prompt_template"
    PROMPT_ACTION = "prompt_action"
    CONTEXT_MANAGEMENT = "context_management"


@dataclass
class PromptCommand:
    """Represents a prompt-focused voice command"""
    pattern: str
    command_type: PromptCommandType
    handler: Callable
    description: str
    examples: List[str]
    requires_confirmation: bool = False
    priority: int = 1


class PromptVoiceProcessor:
    """Voice command processor optimized for AI prompt dictation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.commands: List[PromptCommand] = []
        self.prompt_history: List[str] = []
        self.current_prompt: str = ""
        
        # Initialize prompt-focused command registry
        self._register_prompt_commands()
    
    def _register_prompt_commands(self) -> None:
        """Register prompt-focused voice commands"""
        
        # Prompt input commands
        self._register_prompt_input_commands()
        
        # Prompt modification commands
        self._register_prompt_modification_commands()
        
        # Prompt template commands
        self._register_prompt_template_commands()
        
        # Prompt action commands
        self._register_prompt_action_commands()
        
        # Context management commands
        self._register_context_commands()
    
    def _register_prompt_input_commands(self) -> None:
        """Register prompt input commands"""
        commands = [
            PromptCommand(
                pattern=r"^(ask|question|query)\s+(.+)$",
                command_type=PromptCommandType.PROMPT_INPUT,
                handler=self._handle_ask_question,
                description="Ask a question or make a query",
                examples=["ask how to implement authentication", "question about React hooks", "query database optimization"]
            ),
            PromptCommand(
                pattern=r"^(explain|describe|tell me about)\s+(.+)$",
                command_type=PromptCommandType.PROMPT_INPUT,
                handler=self._handle_explain_request,
                description="Request explanation or description",
                examples=["explain async await", "describe React lifecycle", "tell me about TypeScript"]
            ),
            PromptCommand(
                pattern=r"^(help me|assist me|guide me)\s+(.+)$",
                command_type=PromptCommandType.PROMPT_INPUT,
                handler=self._handle_help_request,
                description="Request help or assistance",
                examples=["help me debug this error", "assist me with API integration", "guide me through deployment"]
            ),
            PromptCommand(
                pattern=r"^(create|make|build|generate)\s+(.+)$",
                command_type=PromptCommandType.PROMPT_INPUT,
                handler=self._handle_create_request,
                description="Request creation or generation",
                examples=["create a login form", "make a REST API", "build a React component", "generate test cases"]
            ),
            PromptCommand(
                pattern=r"^(fix|debug|solve|resolve)\s+(.+)$",
                command_type=PromptCommandType.PROMPT_INPUT,
                handler=self._handle_fix_request,
                description="Request fixing or debugging",
                examples=["fix this error", "debug the authentication issue", "solve the performance problem"]
            ),
            PromptCommand(
                pattern=r"^(optimize|improve|enhance)\s+(.+)$",
                command_type=PromptCommandType.PROMPT_INPUT,
                handler=self._handle_optimize_request,
                description="Request optimization or improvement",
                examples=["optimize this function", "improve the database query", "enhance the user interface"]
            ),
            PromptCommand(
                pattern=r"^(review|analyze|evaluate)\s+(.+)$",
                command_type=PromptCommandType.PROMPT_INPUT,
                handler=self._handle_review_request,
                description="Request review or analysis",
                examples=["review this code", "analyze the performance", "evaluate the security"]
            ),
        ]
        self.commands.extend(commands)
    
    def _register_prompt_modification_commands(self) -> None:
        """Register prompt modification commands"""
        commands = [
            PromptCommand(
                pattern=r"^(add|include|also)\s+(.+)$",
                command_type=PromptCommandType.PROMPT_MODIFICATION,
                handler=self._handle_add_to_prompt,
                description="Add to current prompt",
                examples=["add error handling", "include unit tests", "also add documentation"]
            ),
            PromptCommand(
                pattern=r"^(remove|exclude|don't include)\s+(.+)$",
                command_type=PromptCommandType.PROMPT_MODIFICATION,
                handler=self._handle_remove_from_prompt,
                description="Remove from current prompt",
                examples=["remove comments", "exclude error handling", "don't include tests"]
            ),
            PromptCommand(
                pattern=r"^(change|modify|update)\s+(.+)\s+to\s+(.+)$",
                command_type=PromptCommandType.PROMPT_MODIFICATION,
                handler=self._handle_change_prompt,
                description="Change part of prompt",
                examples=["change function name to calculateSum", "modify the API to use GraphQL", "update the styling to use Tailwind"]
            ),
            PromptCommand(
                pattern=r"^(make it|make this)\s+(.+)$",
                command_type=PromptCommandType.PROMPT_MODIFICATION,
                handler=self._handle_modify_prompt,
                description="Modify current prompt",
                examples=["make it more efficient", "make this responsive", "make it async"]
            ),
            PromptCommand(
                pattern=r"^(simplify|make simpler|reduce complexity)$",
                command_type=PromptCommandType.PROMPT_MODIFICATION,
                handler=self._handle_simplify_prompt,
                description="Simplify the prompt",
                examples=["simplify", "make simpler", "reduce complexity"]
            ),
            PromptCommand(
                pattern=r"^(expand|elaborate|add more detail)$",
                command_type=PromptCommandType.PROMPT_MODIFICATION,
                handler=self._handle_expand_prompt,
                description="Expand the prompt with more detail",
                examples=["expand", "elaborate", "add more detail"]
            ),
        ]
        self.commands.extend(commands)
    
    def _register_prompt_template_commands(self) -> None:
        """Register prompt template commands"""
        commands = [
            PromptCommand(
                pattern=r"^(code review|review code)$",
                command_type=PromptCommandType.PROMPT_TEMPLATE,
                handler=self._handle_code_review_template,
                description="Code review template",
                examples=["code review", "review code"]
            ),
            PromptCommand(
                pattern=r"^(explain code|explain this)$",
                command_type=PromptCommandType.PROMPT_TEMPLATE,
                handler=self._handle_explain_code_template,
                description="Code explanation template",
                examples=["explain code", "explain this"]
            ),
            PromptCommand(
                pattern=r"^(refactor|refactor this)$",
                command_type=PromptCommandType.PROMPT_TEMPLATE,
                handler=self._handle_refactor_template,
                description="Code refactoring template",
                examples=["refactor", "refactor this"]
            ),
            PromptCommand(
                pattern=r"^(write tests|create tests|add tests)$",
                command_type=PromptCommandType.PROMPT_TEMPLATE,
                handler=self._handle_write_tests_template,
                description="Test writing template",
                examples=["write tests", "create tests", "add tests"]
            ),
            PromptCommand(
                pattern=r"^(documentation|add docs|write docs)$",
                command_type=PromptCommandType.PROMPT_TEMPLATE,
                handler=self._handle_documentation_template,
                description="Documentation template",
                examples=["documentation", "add docs", "write docs"]
            ),
            PromptCommand(
                pattern=r"^(optimize|optimize this)$",
                command_type=PromptCommandType.PROMPT_TEMPLATE,
                handler=self._handle_optimize_template,
                description="Optimization template",
                examples=["optimize", "optimize this"]
            ),
            PromptCommand(
                pattern=r"^(debug|debug this)$",
                command_type=PromptCommandType.PROMPT_TEMPLATE,
                handler=self._handle_debug_template,
                description="Debugging template",
                examples=["debug", "debug this"]
            ),
        ]
        self.commands.extend(commands)
    
    def _register_prompt_action_commands(self) -> None:
        """Register prompt action commands"""
        commands = [
            PromptCommand(
                pattern=r"^(send|submit|go)$",
                command_type=PromptCommandType.PROMPT_ACTION,
                handler=self._handle_send_prompt,
                description="Send the current prompt",
                examples=["send", "submit", "go"]
            ),
            PromptCommand(
                pattern=r"^(clear|reset|start over)$",
                command_type=PromptCommandType.PROMPT_ACTION,
                handler=self._handle_clear_prompt,
                description="Clear current prompt",
                examples=["clear", "reset", "start over"]
            ),
            PromptCommand(
                pattern=r"^(undo|go back)$",
                command_type=PromptCommandType.PROMPT_ACTION,
                handler=self._handle_undo_prompt,
                description="Undo last prompt modification",
                examples=["undo", "go back"]
            ),
            PromptCommand(
                pattern=r"^(repeat|say again)$",
                command_type=PromptCommandType.PROMPT_ACTION,
                handler=self._handle_repeat_prompt,
                description="Repeat the current prompt",
                examples=["repeat", "say again"]
            ),
            PromptCommand(
                pattern=r"^(save prompt|save this)$",
                command_type=PromptCommandType.PROMPT_ACTION,
                handler=self._handle_save_prompt,
                description="Save current prompt",
                examples=["save prompt", "save this"]
            ),
            PromptCommand(
                pattern=r"^(load prompt|load saved)$",
                command_type=PromptCommandType.PROMPT_ACTION,
                handler=self._handle_load_prompt,
                description="Load saved prompt",
                examples=["load prompt", "load saved"]
            ),
        ]
        self.commands.extend(commands)
    
    def _register_context_commands(self) -> None:
        """Register context management commands"""
        commands = [
            PromptCommand(
                pattern=r"^(for|in|using)\s+(.+)$",
                command_type=PromptCommandType.CONTEXT_MANAGEMENT,
                handler=self._handle_add_context,
                description="Add context to prompt",
                examples=["for React", "in Python", "using TypeScript", "for mobile app"]
            ),
            PromptCommand(
                pattern=r"^(with|including|that has)\s+(.+)$",
                command_type=PromptCommandType.CONTEXT_MANAGEMENT,
                handler=self._handle_add_requirements,
                description="Add requirements to prompt",
                examples=["with error handling", "including tests", "that has authentication"]
            ),
            PromptCommand(
                pattern=r"^(without|excluding|not including)\s+(.+)$",
                command_type=PromptCommandType.CONTEXT_MANAGEMENT,
                handler=self._handle_exclude_requirements,
                description="Exclude requirements from prompt",
                examples=["without tests", "excluding comments", "not including error handling"]
            ),
            PromptCommand(
                pattern=r"^(as a|like a|similar to)\s+(.+)$",
                command_type=PromptCommandType.CONTEXT_MANAGEMENT,
                handler=self._handle_add_style_context,
                description="Add style or approach context",
                examples=["as a beginner", "like a senior developer", "similar to existing code"]
            ),
        ]
        self.commands.extend(commands)
    
    def process_command(self, text: str) -> Optional[str]:
        """Process voice command and return result - minimal processing, no enhancements"""
        try:
            # Clean and normalize text (keep original case)
            text = text.strip()
            
            # Add to prompt history
            self.prompt_history.append(text)
            if len(self.prompt_history) > 20:
                self.prompt_history.pop(0)
            
            # Find matching command (but don't add enhancements)
            for command in sorted(self.commands, key=lambda c: c.priority, reverse=True):
                match = re.match(command.pattern, text.lower())
                if match:
                    self.logger.info(f"Matched prompt command: {command.description}")
                    
                    # Execute command
                    result = command.handler(match.groups())
                    
                    if result:
                        # Update current prompt
                        self.current_prompt = result
                        return result
            
            # No command matched, treat as regular prompt text (return as-is)
            self.current_prompt = text
            return text
            
        except Exception as e:
            self.logger.error(f"Prompt command processing failed: {e}")
            return text
    
    # Command handlers - simplified, no enhancements
    def _handle_ask_question(self, groups: tuple) -> str:
        """Handle ask question command"""
        question = groups[1] if len(groups) > 1 else ""
        return question if question else ""
    
    def _handle_explain_request(self, groups: tuple) -> str:
        """Handle explain request command"""
        topic = groups[1] if len(groups) > 1 else ""
        return f"Explain {topic}" if topic else ""
    
    def _handle_help_request(self, groups: tuple) -> str:
        """Handle help request command"""
        task = groups[1] if len(groups) > 1 else ""
        return f"Help with {task}" if task else ""
    
    def _handle_create_request(self, groups: tuple) -> str:
        """Handle create request command"""
        item = groups[1] if len(groups) > 1 else ""
        return f"Create {item}" if item else ""
    
    def _handle_fix_request(self, groups: tuple) -> str:
        """Handle fix request command"""
        issue = groups[1] if len(groups) > 1 else ""
        return f"Fix {issue}" if issue else ""
    
    def _handle_optimize_request(self, groups: tuple) -> str:
        """Handle optimize request command"""
        target = groups[1] if len(groups) > 1 else ""
        return f"Optimize {target}" if target else ""
    
    def _handle_review_request(self, groups: tuple) -> str:
        """Handle review request command"""
        target = groups[1] if len(groups) > 1 else ""
        return f"Review {target}" if target else ""
    
    def _handle_add_to_prompt(self, groups: tuple) -> str:
        """Handle add to prompt command"""
        addition = groups[1] if len(groups) > 1 else ""
        if self.current_prompt:
            return f"{self.current_prompt}. Also {addition}."
        return f"Please {addition}."
    
    def _handle_remove_from_prompt(self, groups: tuple) -> str:
        """Handle remove from prompt command"""
        removal = groups[1] if len(groups) > 1 else ""
        if self.current_prompt:
            return f"{self.current_prompt}. But don't include {removal}."
        return f"Please help me, but don't include {removal}."
    
    def _handle_change_prompt(self, groups: tuple) -> str:
        """Handle change prompt command"""
        old_part = groups[1] if len(groups) > 1 else ""
        new_part = groups[2] if len(groups) > 2 else ""
        if self.current_prompt:
            return self.current_prompt.replace(old_part, new_part)
        return f"Please help me with {new_part}."
    
    def _handle_modify_prompt(self, groups: tuple) -> str:
        """Handle modify prompt command"""
        modification = groups[1] if len(groups) > 1 else ""
        if self.current_prompt:
            return f"{self.current_prompt}. Make it {modification}."
        return f"Please help me make it {modification}."
    
    def _handle_simplify_prompt(self, groups: tuple) -> str:
        """Handle simplify prompt command"""
        if self.current_prompt:
            return f"{self.current_prompt}. Please keep it simple and straightforward."
        return "Please help me with a simple solution."
    
    def _handle_expand_prompt(self, groups: tuple) -> str:
        """Handle expand prompt command"""
        if self.current_prompt:
            return f"{self.current_prompt}. Please provide detailed explanations and examples."
        return "Please provide a detailed solution with examples."
    
    def _handle_code_review_template(self, groups: tuple) -> str:
        """Handle code review template"""
        return "Please review the selected code and provide feedback on:\n- Code quality and best practices\n- Potential bugs or issues\n- Performance considerations\n- Suggestions for improvement"
    
    def _handle_explain_code_template(self, groups: tuple) -> str:
        """Handle explain code template"""
        return "Please explain the selected code:\n- What does it do?\n- How does it work?\n- What are the key concepts?\n- Any potential issues or improvements?"
    
    def _handle_refactor_template(self, groups: tuple) -> str:
        """Handle refactor template"""
        return "Please refactor the selected code to:\n- Improve readability and maintainability\n- Follow best practices\n- Optimize performance\n- Add proper error handling"
    
    def _handle_write_tests_template(self, groups: tuple) -> str:
        """Handle write tests template"""
        return "Please write comprehensive tests for the selected code:\n- Unit tests for all functions\n- Edge cases and error conditions\n- Integration tests if applicable\n- Mock external dependencies"
    
    def _handle_documentation_template(self, groups: tuple) -> str:
        """Handle documentation template"""
        return "Please add comprehensive documentation:\n- Function/class descriptions\n- Parameter and return value documentation\n- Usage examples\n- Any important notes or warnings"
    
    def _handle_optimize_template(self, groups: tuple) -> str:
        """Handle optimize template"""
        return "Please optimize the selected code for:\n- Performance improvements\n- Memory usage reduction\n- Better algorithm efficiency\n- Maintainability"
    
    def _handle_debug_template(self, groups: tuple) -> str:
        """Handle debug template"""
        return "Please help debug the selected code:\n- Identify potential issues\n- Suggest debugging strategies\n- Provide fixes for any bugs\n- Explain the root cause"
    
    def _handle_send_prompt(self, groups: tuple) -> str:
        """Handle send prompt command"""
        return "SEND_PROMPT"
    
    def _handle_clear_prompt(self, groups: tuple) -> str:
        """Handle clear prompt command"""
        self.current_prompt = ""
        return "CLEAR_PROMPT"
    
    def _handle_undo_prompt(self, groups: tuple) -> str:
        """Handle undo prompt command"""
        if len(self.prompt_history) > 1:
            self.current_prompt = self.prompt_history[-2]
            return self.current_prompt
        return "UNDO_PROMPT"
    
    def _handle_repeat_prompt(self, groups: tuple) -> str:
        """Handle repeat prompt command"""
        return self.current_prompt or "No prompt to repeat"
    
    def _handle_save_prompt(self, groups: tuple) -> str:
        """Handle save prompt command"""
        return "SAVE_PROMPT"
    
    def _handle_load_prompt(self, groups: tuple) -> str:
        """Handle load prompt command"""
        return "LOAD_PROMPT"
    
    def _handle_add_context(self, groups: tuple) -> str:
        """Handle add context command"""
        context = groups[1] if len(groups) > 1 else ""
        if self.current_prompt:
            return f"{self.current_prompt} (for {context})"
        return f"Please help me with {context}"
    
    def _handle_add_requirements(self, groups: tuple) -> str:
        """Handle add requirements command"""
        requirements = groups[1] if len(groups) > 1 else ""
        if self.current_prompt:
            return f"{self.current_prompt} with {requirements}"
        return f"Please help me with {requirements}"
    
    def _handle_exclude_requirements(self, groups: tuple) -> str:
        """Handle exclude requirements command"""
        exclusions = groups[1] if len(groups) > 1 else ""
        if self.current_prompt:
            return f"{self.current_prompt} without {exclusions}"
        return f"Please help me without {exclusions}"
    
    def _handle_add_style_context(self, groups: tuple) -> str:
        """Handle add style context command"""
        style = groups[1] if len(groups) > 1 else ""
        if self.current_prompt:
            return f"{self.current_prompt} (as a {style})"
        return f"Please help me as a {style}"
    
    def get_current_prompt(self) -> str:
        """Get current prompt"""
        return self.current_prompt
    
    def get_prompt_history(self) -> List[str]:
        """Get prompt history"""
        return self.prompt_history.copy()
    
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
    
    def get_commands_by_type(self, command_type: PromptCommandType) -> List[PromptCommand]:
        """Get commands by type"""
        return [cmd for cmd in self.commands if cmd.command_type == command_type]
    
    def add_custom_command(self, command: PromptCommand) -> None:
        """Add a custom command"""
        self.commands.append(command)
        self.logger.info(f"Added custom prompt command: {command.description}")
    
    def reset_prompt(self) -> None:
        """Reset current prompt"""
        self.current_prompt = ""
        self.logger.info("Prompt reset")
