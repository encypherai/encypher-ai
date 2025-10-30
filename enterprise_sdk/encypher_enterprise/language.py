"""
Multi-language support for content signing.

Provides language detection, translation linking, and multi-language metadata.
"""
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass
import langdetect
from langdetect import DetectorFactory

# Set seed for consistent language detection
DetectorFactory.seed = 0


@dataclass
class LanguageInfo:
    """Language information for a document."""
    language: str  # ISO 639-1 code (e.g., 'en', 'es', 'fr')
    confidence: float  # 0.0 to 1.0
    detected: bool  # True if auto-detected, False if manually specified
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "language": self.language,
            "confidence": self.confidence,
            "detected": self.detected
        }


@dataclass
class TranslationLink:
    """Link to a translated version of a document."""
    document_id: str
    language: str
    translator: Optional[str] = None
    translated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "language": self.language,
            "translator": self.translator,
            "translated_at": self.translated_at
        }


class LanguageDetector:
    """
    Detect language of text content.
    
    Example:
        >>> detector = LanguageDetector()
        >>> lang_info = detector.detect("This is English text")
        >>> print(lang_info.language)  # 'en'
    """
    
    # Supported languages (ISO 639-1 codes)
    SUPPORTED_LANGUAGES = {
        'af', 'ar', 'bg', 'bn', 'ca', 'cs', 'cy', 'da', 'de', 'el',
        'en', 'es', 'et', 'fa', 'fi', 'fr', 'gu', 'he', 'hi', 'hr',
        'hu', 'id', 'it', 'ja', 'kn', 'ko', 'lt', 'lv', 'mk', 'ml',
        'mr', 'ne', 'nl', 'no', 'pa', 'pl', 'pt', 'ro', 'ru', 'sk',
        'sl', 'so', 'sq', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr',
        'uk', 'ur', 'vi', 'zh-cn', 'zh-tw'
    }
    
    # Language names for display
    LANGUAGE_NAMES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh-cn': 'Chinese (Simplified)',
        'zh-tw': 'Chinese (Traditional)',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'bn': 'Bengali',
        'pa': 'Punjabi',
        'te': 'Telugu',
        'mr': 'Marathi',
        'ta': 'Tamil',
        'ur': 'Urdu',
        'gu': 'Gujarati',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'tr': 'Turkish',
        'pl': 'Polish',
        'uk': 'Ukrainian',
        'ro': 'Romanian',
        'nl': 'Dutch',
        'el': 'Greek',
        'cs': 'Czech',
        'sv': 'Swedish',
        'hu': 'Hungarian',
        'fi': 'Finnish',
        'no': 'Norwegian',
        'da': 'Danish',
        'he': 'Hebrew',
        'id': 'Indonesian',
        'ms': 'Malay',
        'fa': 'Persian',
    }
    
    def detect(
        self,
        text: str,
        min_length: int = 50
    ) -> LanguageInfo:
        """
        Detect language of text.
        
        Args:
            text: Text to analyze
            min_length: Minimum text length for reliable detection
        
        Returns:
            LanguageInfo with detected language and confidence
        
        Raises:
            ValueError: If text is too short or detection fails
        """
        if len(text) < min_length:
            raise ValueError(f"Text too short for reliable detection (min {min_length} chars)")
        
        try:
            # Detect language
            lang = langdetect.detect(text)
            
            # Get confidence using detect_langs
            langs = langdetect.detect_langs(text)
            confidence = 0.0
            
            for lang_prob in langs:
                if lang_prob.lang == lang:
                    confidence = lang_prob.prob
                    break
            
            return LanguageInfo(
                language=lang,
                confidence=confidence,
                detected=True
            )
        
        except langdetect.LangDetectException as e:
            raise ValueError(f"Language detection failed: {e}")
    
    def detect_multiple(
        self,
        text: str,
        top_n: int = 3
    ) -> List[LanguageInfo]:
        """
        Detect multiple possible languages with probabilities.
        
        Args:
            text: Text to analyze
            top_n: Number of top languages to return
        
        Returns:
            List of LanguageInfo sorted by confidence (highest first)
        """
        try:
            langs = langdetect.detect_langs(text)
            
            results = []
            for lang_prob in langs[:top_n]:
                results.append(LanguageInfo(
                    language=lang_prob.lang,
                    confidence=lang_prob.prob,
                    detected=True
                ))
            
            return results
        
        except langdetect.LangDetectException:
            return []
    
    def is_supported(self, language: str) -> bool:
        """
        Check if language is supported.
        
        Args:
            language: ISO 639-1 language code
        
        Returns:
            True if supported, False otherwise
        """
        return language.lower() in self.SUPPORTED_LANGUAGES
    
    def get_language_name(self, language: str) -> str:
        """
        Get human-readable language name.
        
        Args:
            language: ISO 639-1 language code
        
        Returns:
            Language name or the code if unknown
        """
        return self.LANGUAGE_NAMES.get(language.lower(), language.upper())


class TranslationManager:
    """
    Manage translation links between documents.
    
    Example:
        >>> manager = TranslationManager()
        >>> manager.add_translation("doc_en", "doc_es", "es", "John Doe")
        >>> translations = manager.get_translations("doc_en")
    """
    
    def __init__(self):
        """Initialize translation manager."""
        self.translations: Dict[str, List[TranslationLink]] = {}
    
    def add_translation(
        self,
        source_doc_id: str,
        translation_doc_id: str,
        language: str,
        translator: Optional[str] = None,
        translated_at: Optional[str] = None
    ) -> None:
        """
        Add a translation link.
        
        Args:
            source_doc_id: Original document ID
            translation_doc_id: Translated document ID
            language: Target language code
            translator: Name of translator (optional)
            translated_at: Translation timestamp (optional)
        """
        if source_doc_id not in self.translations:
            self.translations[source_doc_id] = []
        
        link = TranslationLink(
            document_id=translation_doc_id,
            language=language,
            translator=translator,
            translated_at=translated_at
        )
        
        self.translations[source_doc_id].append(link)
    
    def get_translations(
        self,
        document_id: str
    ) -> List[TranslationLink]:
        """
        Get all translations of a document.
        
        Args:
            document_id: Document ID
        
        Returns:
            List of translation links
        """
        return self.translations.get(document_id, [])
    
    def get_translation_by_language(
        self,
        document_id: str,
        language: str
    ) -> Optional[TranslationLink]:
        """
        Get translation in specific language.
        
        Args:
            document_id: Document ID
            language: Target language code
        
        Returns:
            TranslationLink if found, None otherwise
        """
        translations = self.get_translations(document_id)
        
        for trans in translations:
            if trans.language == language:
                return trans
        
        return None
    
    def has_translation(
        self,
        document_id: str,
        language: str
    ) -> bool:
        """
        Check if translation exists for language.
        
        Args:
            document_id: Document ID
            language: Target language code
        
        Returns:
            True if translation exists, False otherwise
        """
        return self.get_translation_by_language(document_id, language) is not None


def detect_language_from_file(
    file_path: Path,
    fallback: Optional[str] = None
) -> LanguageInfo:
    """
    Detect language from file content.
    
    Args:
        file_path: Path to file
        fallback: Fallback language if detection fails
    
    Returns:
        LanguageInfo with detected or fallback language
    """
    detector = LanguageDetector()
    
    try:
        content = file_path.read_text(encoding='utf-8')
        return detector.detect(content)
    except (ValueError, UnicodeDecodeError):
        if fallback:
            return LanguageInfo(
                language=fallback,
                confidence=0.0,
                detected=False
            )
        raise


def create_translation_metadata(
    translations: List[TranslationLink]
) -> Dict:
    """
    Create C2PA custom assertion for translations.
    
    Args:
        translations: List of translation links
    
    Returns:
        Dictionary formatted for C2PA custom assertion
    """
    return {
        "label": "encypher.translations",
        "data": {
            "translations": [t.to_dict() for t in translations]
        }
    }


def extract_language_from_frontmatter(
    frontmatter: Dict
) -> Optional[str]:
    """
    Extract language from frontmatter metadata.
    
    Checks common frontmatter fields: lang, language, locale
    
    Args:
        frontmatter: Frontmatter dictionary
    
    Returns:
        Language code if found, None otherwise
    """
    # Check common field names
    for field in ['lang', 'language', 'locale']:
        if field in frontmatter:
            lang = frontmatter[field]
            # Handle locale format (e.g., 'en-US' -> 'en')
            if isinstance(lang, str):
                return lang.split('-')[0].lower()
    
    return None
