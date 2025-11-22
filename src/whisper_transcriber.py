"""
Whisper transcription module
"""

import whisper
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any
import torch

from config import Config


class WhisperTranscriber:
    """Whisper-based speech-to-text transcription"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Whisper model
        self.model: Optional[whisper.Whisper] = None
        self.model_name = config.whisper_model
        self.language = config.whisper_language
        
        # Load model on initialization
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the Whisper model"""
        try:
            self.logger.info(f"Loading Whisper model: {self.model_name}")
            
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.logger.info(f"Using device: {device}")
            
            # Load the model
            self.model = whisper.load_model(self.model_name, device=device)
            
            self.logger.info(f"Whisper model {self.model_name} loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe_file(self, audio_file_path: str) -> str:
        """Transcribe audio from file with British English accent optimization"""
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        if not Path(audio_file_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            self.logger.info(f"Transcribing audio file: {audio_file_path}")
            
            # Determine language - use "en" for British English if not specified
            language = self.language or "en"
            
            # Transcribe the audio with British English optimization
            # Note: No initial_prompt to avoid it appearing in output
            result = self.model.transcribe(
                audio_file_path,
                language=language,
                fp16=False,  # Disable fp16 for better compatibility
                condition_on_previous_text=True,  # Better context understanding
                temperature=0.0,  # More deterministic, better for accents
                best_of=2,  # Try 2 candidates for better accuracy
                beam_size=5,  # Good balance for accent recognition
                word_timestamps=False,  # Word timestamps (can improve accuracy but slower)
                no_speech_threshold=0.6,  # Lower threshold = better at detecting speech
                logprob_threshold=-1.0,  # Lower threshold = more words detected
                compression_ratio_threshold=2.4  # Better compression detection
            )
            
            # Extract text from result
            text = result["text"].strip()
            
            # Post-process for British English corrections
            if language == "en":
                text = self._correct_british_accent_errors(text)
            
            self.logger.info(f"Transcription completed: {len(text)} characters")
            self.logger.debug(f"Transcribed text: {text}")
            
            return text
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            raise
    
    def _correct_british_accent_errors(self, text: str) -> str:
        """Correct common transcription errors for British accents
        
        Examples of corrections:
        - "program" → "programme" (British spelling)
        - "color" → "colour" (British spelling)
        - "center" → "centre" (British spelling)
        - "realize" → "realise" (British spelling)
        - "optimize" → "optimise" (British spelling)
        - "authorize" → "authorise" (British spelling)
        - "analyze" → "analyse" (British spelling)
        - "organize" → "organise" (British spelling)
        - "recognize" → "recognise" (British spelling)
        - "specialize" → "specialise" (British spelling)
        - "defense" → "defence" (British spelling)
        - "offense" → "offence" (British spelling)
        - "license" (verb) → "licence" (noun, British)
        - "practice" (verb) → "practise" (verb, British)
        """
        # British spelling corrections
        british_corrections = {
            # -ize → -ise
            r'\boptimize\b': 'optimise',
            r'\boptimizes\b': 'optimises',
            r'\boptimized\b': 'optimised',
            r'\boptimizing\b': 'optimising',
            r'\borganize\b': 'organise',
            r'\borganizes\b': 'organises',
            r'\borganized\b': 'organised',
            r'\borganizing\b': 'organising',
            r'\brealize\b': 'realise',
            r'\brealizes\b': 'realises',
            r'\brealized\b': 'realised',
            r'\brealizing\b': 'realising',
            r'\brecognize\b': 'recognise',
            r'\brecognizes\b': 'recognises',
            r'\brecognized\b': 'recognised',
            r'\brecognizing\b': 'recognising',
            r'\bauthorize\b': 'authorise',
            r'\bauthorizes\b': 'authorises',
            r'\bauthorized\b': 'authorised',
            r'\bauthorizing\b': 'authorising',
            r'\banalyze\b': 'analyse',
            r'\banalyzes\b': 'analyses',
            r'\banalyzed\b': 'analysed',
            r'\banalyzing\b': 'analysing',
            r'\bspecialize\b': 'specialise',
            r'\bspecializes\b': 'specialises',
            r'\bspecialized\b': 'specialised',
            r'\bspecializing\b': 'specialising',
            
            # -or → -our
            r'\bcolor\b': 'colour',
            r'\bcolors\b': 'colours',
            r'\bcolored\b': 'coloured',
            r'\bcoloring\b': 'colouring',
            r'\bhonor\b': 'honour',
            r'\bhonors\b': 'honours',
            r'\bhonored\b': 'honoured',
            r'\bhonoring\b': 'honouring',
            r'\blabor\b': 'labour',
            r'\blabors\b': 'labours',
            r'\blabored\b': 'laboured',
            r'\blaboring\b': 'labouring',
            r'\bneighbor\b': 'neighbour',
            r'\bneighbors\b': 'neighbours',
            r'\bneighbored\b': 'neighboured',
            r'\bneighboring\b': 'neighbouring',
            r'\bhumor\b': 'humour',
            r'\bhumors\b': 'humours',
            r'\bhumored\b': 'humoured',
            r'\bhumoring\b': 'humouring',
            r'\bbehavior\b': 'behaviour',
            r'\bbehaviors\b': 'behaviours',
            r'\bfavor\b': 'favour',
            r'\bfavors\b': 'favours',
            r'\bfavored\b': 'favoured',
            r'\bfavoring\b': 'favouring',
            
            # -er → -re
            r'\bcenter\b': 'centre',
            r'\bcenters\b': 'centres',
            r'\bcentered\b': 'centred',
            r'\bcentering\b': 'centring',
            r'\btheater\b': 'theatre',
            r'\btheaters\b': 'theatres',
            r'\bfiber\b': 'fibre',
            r'\bfibers\b': 'fibres',
            r'\bcaliber\b': 'calibre',
            r'\bcalibers\b': 'calibres',
            
            # -og → -ogue
            r'\bdialog\b': 'dialogue',
            r'\bdialogs\b': 'dialogues',
            r'\bcatalog\b': 'catalogue',
            r'\bcatalogs\b': 'catalogues',
            r'\banalog\b': 'analogue',
            r'\banalogs\b': 'analogues',
            
            # -ense → -ence
            r'\bdefense\b': 'defence',
            r'\boffense\b': 'offence',
            r'\bpretense\b': 'pretence',
            
            # Other common differences
            r'\bprogram\b': 'programme',  # When meaning TV/radio programme
            r'\bprograms\b': 'programmes',
            r'\btraveled\b': 'travelled',
            r'\btraveling\b': 'travelling',
            r'\btraveler\b': 'traveller',
            r'\btravelers\b': 'travellers',
            r'\blabeled\b': 'labelled',
            r'\blabeling\b': 'labelling',
            r'\bmodeled\b': 'modelled',
            r'\bmodeling\b': 'modelling',
            r'\bmodeler\b': 'modeller',
            r'\bmodelers\b': 'modellers',
        }
        
        import re
        corrected_text = text
        for pattern, replacement in british_corrections.items():
            corrected_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
        
        return corrected_text
    
    def transcribe_audio_data(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        """Transcribe audio from raw data with British English accent optimization"""
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            self.logger.info("Transcribing audio data")
            
            # Determine language - use "en" for British English if not specified
            language = self.language or "en"
            
            # Transcribe the audio data with British English optimization
            # Note: No initial_prompt to avoid it appearing in output
            result = self.model.transcribe(
                audio_data,
                language=language,
                fp16=False,
                condition_on_previous_text=True,
                temperature=0.0,
                best_of=2,  # Try 2 candidates for better accuracy
                beam_size=5,
                word_timestamps=False,  # Word timestamps (can improve accuracy but slower)
                no_speech_threshold=0.6,  # Lower threshold = better at detecting speech
                logprob_threshold=-1.0,  # Lower threshold = more words detected
                compression_ratio_threshold=2.4  # Better compression detection
            )
            
            # Extract text from result
            text = result["text"].strip()
            
            # Post-process for British English corrections
            if language == "en":
                text = self._correct_british_accent_errors(text)
            
            self.logger.info(f"Transcription completed: {len(text)} characters")
            self.logger.debug(f"Transcribed text: {text}")
            
            return text
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.model:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "model_name": self.model_name,
            "language": self.language,
            "device": str(next(self.model.parameters()).device),
            "parameters": sum(p.numel() for p in self.model.parameters())
        }
    
    def reload_model(self, model_name: Optional[str] = None) -> None:
        """Reload the Whisper model"""
        if model_name:
            self.model_name = model_name
        
        self.logger.info(f"Reloading Whisper model: {self.model_name}")
        self._load_model()
    
    def set_language(self, language: Optional[str]) -> None:
        """Set the language for transcription"""
        self.language = language
        self.logger.info(f"Language set to: {language or 'auto-detect'}")
    
    def cleanup(self) -> None:
        """Clean up resources"""
        if self.model:
            # Clear model from memory
            del self.model
            self.model = None
            
            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            self.logger.info("Whisper model cleaned up")
