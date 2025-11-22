"""
Context-aware text processing for coding terminology
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CodeContext:
    """Context information for code processing"""
    language: str
    framework: Optional[str] = None
    ide: Optional[str] = None
    project_type: Optional[str] = None


class CodeTerminologyProcessor:
    """Processes transcribed text with coding context awareness"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Coding terminology mappings
        self.code_terms = self._load_code_terminology()
        
        # Common coding patterns
        self.coding_patterns = self._load_coding_patterns()
        
        # IDE-specific patterns
        self.ide_patterns = self._load_ide_patterns()
    
    def _load_code_terminology(self) -> Dict[str, str]:
        """Load coding terminology mappings"""
        return {
            # Common abbreviations
            'def': 'def ',
            'func': 'function ',
            'var': 'variable ',
            'const': 'const ',
            'let': 'let ',
            'async': 'async ',
            'await': 'await ',
            'import': 'import ',
            'export': 'export ',
            'return': 'return ',
            'if': 'if ',
            'else': 'else ',
            'elif': 'elif ',
            'for': 'for ',
            'while': 'while ',
            'try': 'try ',
            'catch': 'catch ',
            'finally': 'finally ',
            'class': 'class ',
            'interface': 'interface ',
            'type': 'type ',
            'enum': 'enum ',
            
            # Common coding phrases
            'create a function': 'function ',
            'create a class': 'class ',
            'create a variable': 'let ',
            'create a constant': 'const ',
            'add a comment': '// ',
            'add documentation': '/** */',
            'add error handling': 'try { } catch (error) { }',
            'add async function': 'async function ',
            'add promise': 'Promise',
            'add callback': 'callback',
            'add event listener': 'addEventListener',
            'add click handler': 'onClick',
            'add submit handler': 'onSubmit',
            
            # Framework-specific terms
            'react component': 'React.Component',
            'vue component': 'Vue.component',
            'angular component': '@Component',
            'express route': 'app.get',
            'mongoose model': 'mongoose.model',
            'sequelize model': 'sequelize.define',
            'redux action': 'action',
            'redux reducer': 'reducer',
            'mobx store': 'mobx.store',
            'jest test': 'describe',
            'cypress test': 'cy.',
            'pytest test': 'def test_',
            
            # Common symbols and operators
            'equals': '=',
            'not equals': '!=',
            'greater than': '>',
            'less than': '<',
            'greater or equal': '>=',
            'less or equal': '<=',
            'and': '&&',
            'or': '||',
            'not': '!',
            'arrow function': '=>',
            'spread operator': '...',
            'optional chaining': '?.',
            'nullish coalescing': '??',
            
            # Brackets and parentheses
            'open parenthesis': '(',
            'close parenthesis': ')',
            'open bracket': '[',
            'close bracket': ']',
            'open brace': '{',
            'close brace': '}',
            'open angle': '<',
            'close angle': '>',
            
            # Common coding actions
            'new line': '\n',
            'indent': '    ',
            'tab': '\t',
            'space': ' ',
            'comma': ',',
            'semicolon': ';',
            'colon': ':',
            'dot': '.',
            'quote': '"',
            'single quote': "'",
            'backtick': '`',
            'pipe': '|',
            'ampersand': '&',
            'at symbol': '@',
            'hash': '#',
            'dollar': '$',
            'percent': '%',
            'caret': '^',
            'tilde': '~',
            'underscore': '_',
            'dash': '-',
            'plus': '+',
            'asterisk': '*',
            'slash': '/',
            'backslash': '\\',
        }
    
    def _load_coding_patterns(self) -> Dict[str, str]:
        """Load common coding patterns"""
        return {
            # Function patterns
            r'\bfunction\s+(\w+)\s*\(([^)]*)\)': r'function \1(\2)',
            r'\bdef\s+(\w+)\s*\(([^)]*)\)': r'def \1(\2)',
            r'\bclass\s+(\w+)': r'class \1',
            r'\binterface\s+(\w+)': r'interface \1',
            r'\btype\s+(\w+)': r'type \1',
            r'\benum\s+(\w+)': r'enum \1',
            
            # Variable patterns
            r'\blet\s+(\w+)\s*=\s*([^;]+)': r'let \1 = \2;',
            r'\bconst\s+(\w+)\s*=\s*([^;]+)': r'const \1 = \2;',
            r'\bvar\s+(\w+)\s*=\s*([^;]+)': r'var \1 = \2;',
            
            # Control flow patterns
            r'\bif\s*\(([^)]+)\)': r'if (\1)',
            r'\belse\s+if\s*\(([^)]+)\)': r'else if (\1)',
            r'\bfor\s*\(([^)]+)\)': r'for (\1)',
            r'\bwhile\s*\(([^)]+)\)': r'while (\1)',
            r'\btry\s*\{([^}]*)\}\s*catch\s*\(([^)]+)\)': r'try {\1} catch (\2)',
            
            # Import/export patterns
            r'\bimport\s+([^;]+)': r'import \1;',
            r'\bexport\s+([^;]+)': r'export \1;',
            r'\bfrom\s+([^;]+)': r'from \1',
            
            # Method calls
            r'\b(\w+)\s*\.\s*(\w+)\s*\(([^)]*)\)': r'\1.\2(\3)',
            r'\b(\w+)\s*\(([^)]*)\)': r'\1(\2)',
        }
    
    def _load_ide_patterns(self) -> Dict[str, Dict[str, str]]:
        """Load IDE-specific patterns"""
        return {
            'vscode': {
                'open command palette': 'Cmd+Shift+P',
                'open terminal': 'Ctrl+`',
                'open file': 'Cmd+P',
                'go to definition': 'F12',
                'find references': 'Shift+F12',
                'rename symbol': 'F2',
                'format document': 'Shift+Alt+F',
                'toggle comment': 'Cmd+/',
                'duplicate line': 'Shift+Alt+Down',
                'move line up': 'Alt+Up',
                'move line down': 'Alt+Down',
            },
            'cursor': {
                'open chat': 'Cmd+L',
                'open composer': 'Cmd+K',
                'accept suggestion': 'Tab',
                'reject suggestion': 'Esc',
                'next suggestion': 'Alt+]',
                'previous suggestion': 'Alt+[',
            },
            'qwen': {
                'open assistant': 'Cmd+Shift+A',
                'open chat': 'Cmd+J',
                'generate code': 'Cmd+G',
                'explain code': 'Cmd+E',
            }
        }
    
    def process_text(self, text: str, context: Optional[CodeContext] = None) -> str:
        """Process transcribed text with coding context awareness"""
        try:
            # Clean and normalize text
            processed_text = self._clean_text(text)
            
            # Apply terminology mappings
            processed_text = self._apply_terminology_mappings(processed_text)
            
            # Apply coding patterns
            processed_text = self._apply_coding_patterns(processed_text)
            
            # Apply context-specific processing
            if context:
                processed_text = self._apply_context_processing(processed_text, context)
            
            # Apply IDE-specific patterns
            if context and context.ide:
                processed_text = self._apply_ide_patterns(processed_text, context.ide)
            
            # Final cleanup
            processed_text = self._final_cleanup(processed_text)
            
            return processed_text
            
        except Exception as e:
            self.logger.error(f"Text processing failed: {e}")
            return text
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize input text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common transcription errors
        text = text.replace('equals sign', '=')
        text = text.replace('plus sign', '+')
        text = text.replace('minus sign', '-')
        text = text.replace('asterisk', '*')
        text = text.replace('forward slash', '/')
        text = text.replace('backslash', '\\')
        
        return text
    
    def _apply_terminology_mappings(self, text: str) -> str:
        """Apply coding terminology mappings"""
        words = text.split()
        processed_words = []
        
        for word in words:
            # Check for exact matches
            if word.lower() in self.code_terms:
                processed_words.append(self.code_terms[word.lower()])
            else:
                processed_words.append(word)
        
        return ' '.join(processed_words)
    
    def _apply_coding_patterns(self, text: str) -> str:
        """Apply common coding patterns"""
        for pattern, replacement in self.coding_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _apply_context_processing(self, text: str, context: CodeContext) -> str:
        """Apply context-specific processing"""
        if context.language == 'python':
            text = self._process_python_context(text)
        elif context.language == 'javascript':
            text = self._process_javascript_context(text)
        elif context.language == 'typescript':
            text = self._process_typescript_context(text)
        elif context.language == 'java':
            text = self._process_java_context(text)
        elif context.language == 'cpp':
            text = self._process_cpp_context(text)
        
        return text
    
    def _process_python_context(self, text: str) -> str:
        """Process text for Python context"""
        python_patterns = {
            r'\bdef\s+(\w+)\s*\(([^)]*)\)': r'def \1(\2):',
            r'\bclass\s+(\w+)': r'class \1:',
            r'\bif\s+([^:]+)': r'if \1:',
            r'\belse\s*:': r'else:',
            r'\belif\s+([^:]+)': r'elif \1:',
            r'\bfor\s+(\w+)\s+in\s+([^:]+)': r'for \1 in \2:',
            r'\bwhile\s+([^:]+)': r'while \1:',
            r'\btry\s*:': r'try:',
            r'\bexcept\s+([^:]+)': r'except \1:',
            r'\bfinally\s*:': r'finally:',
            r'\bwith\s+([^:]+)': r'with \1:',
        }
        
        for pattern, replacement in python_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _process_javascript_context(self, text: str) -> str:
        """Process text for JavaScript context"""
        js_patterns = {
            r'\bfunction\s+(\w+)\s*\(([^)]*)\)': r'function \1(\2) {',
            r'\bconst\s+(\w+)\s*=\s*([^;]+)': r'const \1 = \2;',
            r'\blet\s+(\w+)\s*=\s*([^;]+)': r'let \1 = \2;',
            r'\bvar\s+(\w+)\s*=\s*([^;]+)': r'var \1 = \2;',
            r'\bif\s*\(([^)]+)\)': r'if (\1) {',
            r'\belse\s*\{': r'} else {',
            r'\bfor\s*\(([^)]+)\)': r'for (\1) {',
            r'\bwhile\s*\(([^)]+)\)': r'while (\1) {',
        }
        
        for pattern, replacement in js_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _process_typescript_context(self, text: str) -> str:
        """Process text for TypeScript context"""
        ts_patterns = {
            r'\binterface\s+(\w+)': r'interface \1 {',
            r'\btype\s+(\w+)': r'type \1 = ',
            r'\benum\s+(\w+)': r'enum \1 {',
            r'\bclass\s+(\w+)': r'class \1 {',
            r'\bpublic\s+(\w+)': r'public \1',
            r'\bprivate\s+(\w+)': r'private \1',
            r'\bprotected\s+(\w+)': r'protected \1',
            r'\bstatic\s+(\w+)': r'static \1',
            r'\basync\s+(\w+)': r'async \1',
            r'\bawait\s+(\w+)': r'await \1',
        }
        
        for pattern, replacement in ts_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _process_java_context(self, text: str) -> str:
        """Process text for Java context"""
        java_patterns = {
            r'\bpublic\s+class\s+(\w+)': r'public class \1 {',
            r'\bprivate\s+(\w+)': r'private \1',
            r'\bprotected\s+(\w+)': r'protected \1',
            r'\bstatic\s+(\w+)': r'static \1',
            r'\bfinal\s+(\w+)': r'final \1',
            r'\babstract\s+(\w+)': r'abstract \1',
            r'\binterface\s+(\w+)': r'interface \1 {',
            r'\benum\s+(\w+)': r'enum \1 {',
        }
        
        for pattern, replacement in java_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _process_cpp_context(self, text: str) -> str:
        """Process text for C++ context"""
        cpp_patterns = {
            r'\bclass\s+(\w+)': r'class \1 {',
            r'\bstruct\s+(\w+)': r'struct \1 {',
            r'\bnamespace\s+(\w+)': r'namespace \1 {',
            r'\btemplate\s*<([^>]+)>': r'template<\1>',
            r'\bpublic\s*:': r'public:',
            r'\bprivate\s*:': r'private:',
            r'\bprotected\s*:': r'protected:',
            r'\bvirtual\s+(\w+)': r'virtual \1',
            r'\bconst\s+(\w+)': r'const \1',
            r'\bstatic\s+(\w+)': r'static \1',
        }
        
        for pattern, replacement in cpp_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _apply_ide_patterns(self, text: str, ide: str) -> str:
        """Apply IDE-specific patterns"""
        if ide.lower() in self.ide_patterns:
            patterns = self.ide_patterns[ide.lower()]
            for phrase, shortcut in patterns.items():
                if phrase in text.lower():
                    text = text.replace(phrase, shortcut)
        
        return text
    
    def _final_cleanup(self, text: str) -> str:
        """Final cleanup and formatting"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common punctuation issues
        text = text.replace(' ,', ',')
        text = text.replace(' .', '.')
        text = text.replace(' ;', ';')
        text = text.replace(' :', ':')
        text = text.replace(' (', '(')
        text = text.replace('( ', '(')
        text = text.replace(' )', ')')
        text = text.replace(') ', ')')
        text = text.replace(' {', '{')
        text = text.replace('{ ', '{')
        text = text.replace(' }', '}')
        text = text.replace('} ', '}')
        
        return text
    
    def detect_code_context(self, text: str) -> CodeContext:
        """Detect coding context from text"""
        text_lower = text.lower()
        
        # Detect programming language
        language = 'unknown'
        if any(keyword in text_lower for keyword in ['python', 'def ', 'import ', 'from ']):
            language = 'python'
        elif any(keyword in text_lower for keyword in ['javascript', 'function', 'const ', 'let ']):
            language = 'javascript'
        elif any(keyword in text_lower for keyword in ['typescript', 'interface', 'type ', 'enum ']):
            language = 'typescript'
        elif any(keyword in text_lower for keyword in ['java', 'class ', 'public ', 'private ']):
            language = 'java'
        elif any(keyword in text_lower for keyword in ['cpp', 'c++', 'template', 'namespace']):
            language = 'cpp'
        
        # Detect framework
        framework = None
        if any(keyword in text_lower for keyword in ['react', 'jsx', 'component']):
            framework = 'react'
        elif any(keyword in text_lower for keyword in ['vue', 'vue.js']):
            framework = 'vue'
        elif any(keyword in text_lower for keyword in ['angular', 'ng-']):
            framework = 'angular'
        elif any(keyword in text_lower for keyword in ['express', 'node.js']):
            framework = 'express'
        
        # Detect IDE
        ide = None
        if any(keyword in text_lower for keyword in ['vscode', 'visual studio code']):
            ide = 'vscode'
        elif any(keyword in text_lower for keyword in ['cursor']):
            ide = 'cursor'
        elif any(keyword in text_lower for keyword in ['qwen', 'tongyi']):
            ide = 'qwen'
        
        return CodeContext(language=language, framework=framework, ide=ide)
