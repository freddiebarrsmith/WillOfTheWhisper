"""
Prompt-focused text processing for natural language optimization
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PromptContext:
    """Context information for prompt processing"""
    intent: str  # question, request, command, explanation
    domain: Optional[str] = None  # coding, general, specific technology
    urgency: str = "normal"  # low, normal, high
    complexity: str = "medium"  # simple, medium, complex


class PromptTextProcessor:
    """Processes transcribed text optimized for AI prompt generation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Prompt optimization patterns
        self.prompt_patterns = self._load_prompt_patterns()
        
        # Natural language improvements
        self.natural_language_map = self._load_natural_language_map()
        
        # Prompt enhancement rules
        self.enhancement_rules = self._load_enhancement_rules()
    
    def _load_prompt_patterns(self) -> Dict[str, str]:
        """Load patterns for prompt optimization"""
        return {
            # Question patterns
            r'\bhow\s+do\s+i\s+(.+)\?': r'How can I \1?',
            r'\bwhat\s+is\s+(.+)\?': r'What is \1 and how does it work?',
            r'\bwhy\s+does\s+(.+)\?': r'Why does \1 happen and how can I fix it?',
            r'\bwhen\s+should\s+i\s+(.+)\?': r'When should I \1 and what are the best practices?',
            r'\bwhere\s+can\s+i\s+(.+)\?': r'Where can I \1 and what are the options?',
            
            # Request patterns
            r'\bcan\s+you\s+(.+)\?': r'Please \1.',
            r'\bcould\s+you\s+(.+)\?': r'Please \1.',
            r'\bwould\s+you\s+(.+)\?': r'Please \1.',
            r'\bi\s+need\s+(.+)': r'I need help with \1.',
            r'\bi\s+want\s+(.+)': r'I would like \1.',
            
            # Command patterns
            r'\bmake\s+(.+)': r'Please create \1.',
            r'\bbuild\s+(.+)': r'Please build \1.',
            r'\bcreate\s+(.+)': r'Please create \1.',
            r'\bfix\s+(.+)': r'Please help me fix \1.',
            r'\bdebug\s+(.+)': r'Please help me debug \1.',
            r'\boptimize\s+(.+)': r'Please optimize \1.',
            
            # Explanation patterns
            r'\bexplain\s+(.+)': r'Please explain \1 in detail.',
            r'\bdescribe\s+(.+)': r'Please describe \1.',
            r'\btell\s+me\s+about\s+(.+)': r'Please tell me about \1.',
            r'\bshow\s+me\s+(.+)': r'Please show me \1.',
        }
    
    def _load_natural_language_map(self) -> Dict[str, str]:
        """Load natural language improvements"""
        return {
            # Common transcription errors
            'um': '',
            'uh': '',
            'like': '',
            'you know': '',
            'i mean': '',
            'actually': '',
            'basically': '',
            'literally': '',
            'obviously': '',
            'clearly': '',
            
            # Coding terminology improvements
            'function': 'function',
            'method': 'method',
            'variable': 'variable',
            'constant': 'constant',
            'class': 'class',
            'object': 'object',
            'array': 'array',
            'string': 'string',
            'number': 'number',
            'boolean': 'boolean',
            'null': 'null',
            'undefined': 'undefined',
            'true': 'true',
            'false': 'false',
            
            # Common abbreviations
            'api': 'API',
            'url': 'URL',
            'http': 'HTTP',
            'https': 'HTTPS',
            'json': 'JSON',
            'xml': 'XML',
            'html': 'HTML',
            'css': 'CSS',
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'react': 'React',
            'vue': 'Vue',
            'angular': 'Angular',
            'node': 'Node.js',
            'python': 'Python',
            'java': 'Java',
            'cpp': 'C++',
            'csharp': 'C#',
            'sql': 'SQL',
            'db': 'database',
            'ui': 'user interface',
            'ux': 'user experience',
            'ui/ux': 'user interface and user experience',
            
            # Technical terms
            'authentication': 'authentication',
            'authorization': 'authorization',
            'encryption': 'encryption',
            'decryption': 'decryption',
            'hashing': 'hashing',
            'caching': 'caching',
            'optimization': 'optimization',
            'performance': 'performance',
            'scalability': 'scalability',
            'maintainability': 'maintainability',
            'readability': 'readability',
            'testability': 'testability',
            'debugging': 'debugging',
            'testing': 'testing',
            'deployment': 'deployment',
            'devops': 'DevOps',
            'ci/cd': 'CI/CD',
            'microservices': 'microservices',
            'rest': 'REST',
            'graphql': 'GraphQL',
            'websocket': 'WebSocket',
            'jwt': 'JWT',
            'oauth': 'OAuth',
            'cors': 'CORS',
            'csrf': 'CSRF',
            'xss': 'XSS',
            'sql injection': 'SQL injection',
        }
    
    def _load_enhancement_rules(self) -> List[Dict[str, str]]:
        """Load prompt enhancement rules"""
        return [
            {
                'pattern': r'\b(help|assist|guide)\s+me\s+with\s+(.+)',
                'enhancement': r'I need help with \2. Please provide step-by-step guidance.',
                'intent': 'help_request'
            },
            {
                'pattern': r'\b(create|make|build)\s+(.+)',
                'enhancement': r'Please create \2 with best practices and proper structure.',
                'intent': 'creation_request'
            },
            {
                'pattern': r'\b(fix|debug|solve)\s+(.+)',
                'enhancement': r'Please help me fix \2. Include the root cause and solution.',
                'intent': 'fix_request'
            },
            {
                'pattern': r'\b(explain|describe)\s+(.+)',
                'enhancement': r'Please explain \2 in detail with examples.',
                'intent': 'explanation_request'
            },
            {
                'pattern': r'\b(optimize|improve|enhance)\s+(.+)',
                'enhancement': r'Please optimize \2 for better performance and maintainability.',
                'intent': 'optimization_request'
            },
            {
                'pattern': r'\b(review|analyze|evaluate)\s+(.+)',
                'enhancement': r'Please review \2 and provide detailed feedback.',
                'intent': 'review_request'
            },
        ]
    
    def process_prompt_text(self, text: str) -> Tuple[str, PromptContext]:
        """Process transcribed text for optimal prompt generation"""
        try:
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Detect prompt context
            context = self._detect_prompt_context(cleaned_text)
            
            # Apply natural language improvements
            improved_text = self._apply_natural_language_improvements(cleaned_text)
            
            # Apply prompt patterns
            optimized_text = self._apply_prompt_patterns(improved_text)
            
            # Apply enhancement rules
            enhanced_text = self._apply_enhancement_rules(optimized_text, context)
            
            # Final cleanup
            final_text = self._final_cleanup(enhanced_text)
            
            self.logger.info(f"Prompt processed: '{text}' -> '{final_text}'")
            
            return final_text, context
            
        except Exception as e:
            self.logger.error(f"Prompt processing failed: {e}")
            return text, PromptContext(intent="unknown")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize input text - minimal processing"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common filler words (but keep it minimal)
        filler_words = ['um', 'uh']
        for word in filler_words:
            text = re.sub(rf'\b{word}\b', '', text, flags=re.IGNORECASE)
        
        # Fix common punctuation issues
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([,.!?;:])\s*([,.!?;:])', r'\1', text)
        
        return text.strip()
    
    def _detect_prompt_context(self, text: str) -> PromptContext:
        """Detect the context of the prompt"""
        text_lower = text.lower()
        
        # Detect intent
        intent = "unknown"
        if any(word in text_lower for word in ['how', 'what', 'why', 'when', 'where', '?']):
            intent = "question"
        elif any(word in text_lower for word in ['help', 'assist', 'guide']):
            intent = "help_request"
        elif any(word in text_lower for word in ['create', 'make', 'build', 'generate']):
            intent = "creation_request"
        elif any(word in text_lower for word in ['fix', 'debug', 'solve', 'resolve']):
            intent = "fix_request"
        elif any(word in text_lower for word in ['explain', 'describe', 'tell me']):
            intent = "explanation_request"
        elif any(word in text_lower for word in ['optimize', 'improve', 'enhance']):
            intent = "optimization_request"
        elif any(word in text_lower for word in ['review', 'analyze', 'evaluate']):
            intent = "review_request"
        
        # Detect domain
        domain = None
        if any(tech in text_lower for tech in ['react', 'vue', 'angular', 'javascript', 'js']):
            domain = "frontend"
        elif any(tech in text_lower for tech in ['node', 'python', 'java', 'php', 'ruby']):
            domain = "backend"
        elif any(tech in text_lower for tech in ['database', 'sql', 'mongodb', 'postgresql']):
            domain = "database"
        elif any(tech in text_lower for tech in ['api', 'rest', 'graphql', 'microservices']):
            domain = "api"
        elif any(word in text_lower for word in ['test', 'testing', 'unit test', 'integration']):
            domain = "testing"
        elif any(word in text_lower for word in ['deploy', 'deployment', 'devops', 'ci/cd']):
            domain = "deployment"
        
        # Detect urgency
        urgency = "normal"
        if any(word in text_lower for word in ['urgent', 'asap', 'immediately', 'quickly']):
            urgency = "high"
        elif any(word in text_lower for word in ['whenever', 'eventually', 'no rush']):
            urgency = "low"
        
        # Detect complexity
        complexity = "medium"
        if any(word in text_lower for word in ['simple', 'basic', 'easy', 'quick']):
            complexity = "simple"
        elif any(word in text_lower for word in ['complex', 'advanced', 'sophisticated', 'detailed']):
            complexity = "complex"
        
        return PromptContext(
            intent=intent,
            domain=domain,
            urgency=urgency,
            complexity=complexity
        )
    
    def _apply_natural_language_improvements(self, text: str) -> str:
        """Apply natural language improvements"""
        words = text.split()
        improved_words = []
        
        for word in words:
            # Check for exact matches
            if word.lower() in self.natural_language_map:
                improved_words.append(self.natural_language_map[word.lower()])
            else:
                improved_words.append(word)
        
        return ' '.join(improved_words)
    
    def _apply_prompt_patterns(self, text: str) -> str:
        """Apply prompt optimization patterns"""
        for pattern, replacement in self.prompt_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _apply_enhancement_rules(self, text: str, context: PromptContext) -> str:
        """Apply enhancement rules based on context"""
        for rule in self.enhancement_rules:
            if re.search(rule['pattern'], text, re.IGNORECASE):
                # Check if the rule matches the detected intent
                if rule['intent'] == context.intent:
                    text = re.sub(rule['pattern'], rule['enhancement'], text, flags=re.IGNORECASE)
                    break
        
        # Add context-specific enhancements
        if context.domain:
            text = self._add_domain_context(text, context.domain)
        
        if context.complexity == "simple":
            text += " Please keep it simple and straightforward."
        elif context.complexity == "complex":
            text += " Please provide detailed explanations and examples."
        
        if context.urgency == "high":
            text += " This is urgent, please prioritize."
        
        return text
    
    def _add_domain_context(self, text: str, domain: str) -> str:
        """Add domain-specific context to prompt"""
        domain_contexts = {
            "frontend": " (focusing on modern frontend best practices)",
            "backend": " (focusing on backend architecture and best practices)",
            "database": " (focusing on database design and optimization)",
            "api": " (focusing on API design and best practices)",
            "testing": " (focusing on testing strategies and best practices)",
            "deployment": " (focusing on deployment strategies and best practices)",
        }
        
        if domain in domain_contexts:
            text += domain_contexts[domain]
        
        return text
    
    def _final_cleanup(self, text: str) -> str:
        """Final cleanup and formatting"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Ensure proper sentence structure
        if not text.endswith(('.', '!', '?')):
            text += '.'
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    def _aggressively_restructure_prompt(self, text: str) -> str:
        """Aggressively restructure casual speech into a proper prompt"""
        text = text.strip()
        text_lower = text.lower()
        
        # Handle incomplete sentences - add context
        if not text.endswith(('.', '!', '?', ':', ';')):
            # Check if it's a question
            if any(word in text_lower for word in ['how', 'what', 'why', 'when', 'where', 'who', 'which']):
                if not text.endswith('?'):
                    text += '?'
            else:
                # It's likely a statement - make it a request
                if not any(word in text_lower for word in ['please', 'help', 'create', 'make', 'build', 'fix', 'explain']):
                    # Add a polite request prefix
                    if text_lower.startswith(('i ', 'i\'m ', 'i\'ve ', 'i\'ll ')):
                        text = text.replace('i ', 'I ', 1).replace('i\'m ', 'I\'m ', 1).replace('i\'ve ', 'I\'ve ', 1).replace('i\'ll ', 'I\'ll ', 1)
                        text = f"Please help me with {text.lower()}"
                    else:
                        text = f"Please {text}"
        
        # Fix common speech patterns
        # "authorization in a system" -> "How to implement authorization in a system"
        if re.match(r'^[a-z][^?]*$', text_lower) and len(text.split()) < 8:
            # Short statement without question - likely needs expansion
            if 'authorization' in text_lower or 'authentication' in text_lower:
                text = f"How to implement {text}?"
            elif any(word in text_lower for word in ['component', 'function', 'class', 'api', 'endpoint']):
                text = f"How to create {text}?"
            elif any(word in text_lower for word in ['error', 'bug', 'issue', 'problem']):
                text = f"How to fix {text}?"
            elif any(word in text_lower for word in ['optimize', 'improve', 'enhance']):
                text = f"How to {text}?"
            else:
                text = f"Please explain {text}."
        
        return text
    
    def _develop_prompt_intelligently(self, text: str, context: PromptContext) -> str:
        """Intelligently develop the prompt with better structure and clarity"""
        text_lower = text.lower()
        
        # Add clarity based on intent
        if context.intent == "question":
            # Ensure questions are clear and actionable
            if not text_lower.startswith(('how', 'what', 'why', 'when', 'where', 'who', 'which', 'can', 'could', 'would', 'should')):
                # Not a proper question - restructure
                if 'how' in text_lower:
                    text = re.sub(r'.*how\s+', 'How ', text, flags=re.IGNORECASE)
                elif 'what' in text_lower:
                    text = re.sub(r'.*what\s+', 'What ', text, flags=re.IGNORECASE)
                else:
                    text = f"How can I {text.lower()}?"
        
        elif context.intent == "creation_request":
            # Ensure creation requests are specific
            if not any(word in text_lower for word in ['create', 'make', 'build', 'generate', 'implement']):
                text = f"Please create {text}."
            else:
                # Add specificity
                if not any(word in text_lower for word in ['with', 'that', 'including', 'using']):
                    text += " with best practices and proper structure."
        
        elif context.intent == "fix_request":
            # Ensure fix requests include context
            if not any(word in text_lower for word in ['fix', 'debug', 'solve', 'resolve', 'repair']):
                text = f"Please help me fix {text}."
            else:
                if 'error' not in text_lower and 'issue' not in text_lower and 'problem' not in text_lower:
                    text += " Please identify the root cause and provide a solution."
        
        elif context.intent == "explanation_request":
            # Ensure explanations are comprehensive
            if not any(word in text_lower for word in ['explain', 'describe', 'tell', 'show', 'clarify']):
                text = f"Please explain {text}."
            else:
                if 'detail' not in text_lower and 'example' not in text_lower:
                    text += " Please provide detailed explanations with examples."
        
        # Add domain-specific context if detected
        if context.domain:
            domain_phrases = {
                "frontend": "following modern frontend best practices",
                "backend": "following backend architecture best practices",
                "database": "following database design best practices",
                "api": "following API design best practices",
                "testing": "following testing best practices",
                "deployment": "following deployment best practices"
            }
            if context.domain in domain_phrases:
                if domain_phrases[context.domain] not in text_lower:
                    text += f" {domain_phrases[context.domain].capitalize()}."
        
        return text
    
    def _polish_for_llm(self, text: str, context: PromptContext) -> str:
        """Final polish to make the prompt optimal for LLM understanding"""
        # Ensure the prompt is clear and actionable
        text = text.strip()
        
        # Remove redundant phrases
        redundant_phrases = [
            (r'\bplease\s+please\b', 'please'),
            (r'\bhelp\s+me\s+help\b', 'help me'),
            (r'\bcan\s+you\s+can\s+you\b', 'can you'),
        ]
        for pattern, replacement in redundant_phrases:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Ensure proper capitalization
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Ensure it ends with proper punctuation
        if not text.endswith(('.', '!', '?')):
            if context.intent == "question":
                text += '?'
            else:
                text += '.'
        
        # Add clarity markers for complex requests
        if context.complexity == "complex":
            if 'detailed' not in text.lower() and 'comprehensive' not in text.lower():
                text = text.rstrip('.!?') + " Please provide a comprehensive solution with detailed explanations."
        
        # Ensure minimum clarity
        if len(text.split()) < 5:
            # Very short prompt - add context
            if context.intent == "question":
                text = text.rstrip('?') + "? Please provide a clear, actionable answer."
            elif context.intent == "creation_request":
                text = text.rstrip('.') + ". Please provide the complete implementation."
            else:
                text = text.rstrip('.') + ". Please provide detailed guidance."
        
        return text
    
    def enhance_for_ai_assistant(self, text: str, assistant_type: str = "general") -> str:
        """Enhance prompt specifically for AI assistant - minimal processing, no aggressive enhancements"""
        try:
            # Just do basic cleanup - no aggressive restructuring or adding phrases
            # Strip out any existing enhancement phrases first
            text = self._strip_enhancement_phrases(text)
            
            # Basic cleanup only
            cleaned_text = self._clean_text(text)
            
            # Ensure proper capitalization and punctuation
            if cleaned_text and cleaned_text[0].islower():
                cleaned_text = cleaned_text[0].upper() + cleaned_text[1:]
            
            if cleaned_text and not cleaned_text.endswith(('.', '!', '?')):
                # Add period if missing, but don't add extra text
                cleaned_text += '.'
            
            return cleaned_text.strip()
            
        except Exception as e:
            self.logger.error(f"AI assistant enhancement failed: {e}")
            return text
    
    def _strip_enhancement_phrases(self, text: str) -> str:
        """Strip out common enhancement phrases that were automatically added"""
        import re
        
        # List of enhancement phrases to remove
        enhancement_phrases = [
            # Best practices and structure
            r'\s+with best practices and proper structure\.?',
            r'\s+with best practices\.?',
            r'\s+following best practices\.?',
            r'\s+following modern frontend best practices\.?',
            r'\s+following backend architecture best practices\.?',
            r'\s+following database design best practices\.?',
            r'\s+following API design best practices\.?',
            r'\s+following testing best practices\.?',
            r'\s+following testing strategies and best practices\.?',
            r'\s+following deployment best practices\.?',
            r'\s+following deployment strategies and best practices\.?',
            r'\s+proper structure\.?',
            
            # Detailed explanations
            r'\s+Please provide detailed explanations with examples\.?',
            r'\s+Please provide detailed explanations\.?',
            r'\s+with detailed explanations\.?',
            r'\s+in detail with examples\.?',
            r'\s+in detail\.?',
            r'\s+with examples\.?',
            
            # Comprehensive solutions
            r'\s+Please provide a comprehensive solution with detailed explanations\.?',
            r'\s+Please provide a comprehensive solution\.?',
            r'\s+comprehensive solution\.?',
            
            # Implementation details
            r'\s+Please provide the complete implementation\.?',
            r'\s+complete implementation\.?',
            r'\s+Please include best practices and error handling\.?',
            r'\s+with error handling\.?',
            
            # Context and guidance
            r'\s+Please consider the existing codebase context\.?',
            r'\s+Please consider the existing code\.?',
            r'\s+Please provide detailed guidance\.?',
            r'\s+Please provide a clear, actionable answer\.?',
            r'\s+clear, actionable answer\.?',
            
            # Root cause and solutions
            r'\s+Please identify the root cause and provide a solution\.?',
            r'\s+root cause and solution\.?',
            
            # Code quality phrases
            r'\s+focusing on modern frontend best practices\.?',
            r'\s+focusing on backend architecture and best practices\.?',
            r'\s+focusing on database design and best practices\.?',
            r'\s+focusing on API design and best practices\.?',
            r'\s+focusing on testing strategies and best practices\.?',
            r'\s+focusing on deployment strategies and best practices\.?',
            
            # Assistant-specific additions
            r'\s+Please explain the issue and provide the fix\.?',
            r'\s+Please provide the complete code with comments\.?',
            r'\s+Please analyze the current code and provide a fix\.?',
        ]
        
        # Remove each enhancement phrase
        for phrase in enhancement_phrases:
            text = re.sub(phrase, '', text, flags=re.IGNORECASE)
        
        # Clean up any double spaces or trailing punctuation issues
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\s+([,.!?])', r'\1', text)  # Space before punctuation
        text = re.sub(r'([,.!?])\s*([,.!?])', r'\1', text)  # Multiple punctuation
        
        return text.strip()
    
    def _enhance_for_roo(self, text: str, context: PromptContext) -> str:
        """Enhance prompt for VS Code Roo"""
        # Roo works well with direct, clear instructions
        if context.intent == "question":
            text = text.replace("?", "? Please provide a clear, actionable answer.")
        elif context.intent == "creation_request":
            text += " Please provide the complete code with comments."
        elif context.intent == "fix_request":
            text += " Please explain the issue and provide the fix."
        
        return text
    
    def _enhance_for_cursor(self, text: str, context: PromptContext) -> str:
        """Enhance prompt for Cursor IDE"""
        # Cursor works well with context-aware instructions
        if context.intent == "creation_request":
            text += " Please consider the existing codebase context."
        elif context.intent == "fix_request":
            text += " Please analyze the current code and provide a fix."
        
        return text
    
    def _enhance_for_qwen(self, text: str, context: PromptContext) -> str:
        """Enhance prompt for Qwen Code"""
        # Qwen works well with detailed explanations
        if context.intent in ["question", "explanation_request"]:
            text += " Please provide detailed explanations and examples."
        elif context.intent == "creation_request":
            text += " Please include best practices and error handling."
        
        return text
    
    def get_prompt_suggestions(self, context: PromptContext) -> List[str]:
        """Get prompt suggestions based on context"""
        suggestions = []
        
        if context.intent == "question":
            suggestions.extend([
                "What are the best practices for this?",
                "How can I implement this efficiently?",
                "What are the common pitfalls to avoid?",
                "How does this compare to alternatives?"
            ])
        elif context.intent == "creation_request":
            suggestions.extend([
                "Please create this with proper error handling",
                "Please include unit tests",
                "Please add documentation",
                "Please follow best practices"
            ])
        elif context.intent == "fix_request":
            suggestions.extend([
                "Please explain the root cause",
                "Please provide a comprehensive fix",
                "Please suggest prevention strategies",
                "Please include testing recommendations"
            ])
        
        return suggestions
