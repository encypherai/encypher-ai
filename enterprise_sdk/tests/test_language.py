"""
Tests for language detection and translation management.
"""
import pytest
from pathlib import Path
from encypher_enterprise.language import (
    LanguageDetector,
    TranslationManager,
    LanguageInfo,
    TranslationLink,
    detect_language_from_file,
    create_translation_metadata,
    extract_language_from_frontmatter
)


class TestLanguageDetector:
    """Test language detection functionality."""
    
    def test_detect_english(self):
        """Test detecting English text."""
        detector = LanguageDetector()
        text = "This is a sample English text that should be detected correctly."
        
        lang_info = detector.detect(text)
        
        assert lang_info.language == "en"
        assert lang_info.confidence > 0.9
        assert lang_info.detected is True
    
    def test_detect_spanish(self):
        """Test detecting Spanish text."""
        detector = LanguageDetector()
        text = "Este es un texto de ejemplo en español que debería ser detectado correctamente."
        
        lang_info = detector.detect(text)
        
        assert lang_info.language == "es"
        assert lang_info.confidence > 0.9
    
    def test_detect_french(self):
        """Test detecting French text."""
        detector = LanguageDetector()
        text = "Ceci est un exemple de texte en français qui devrait être détecté correctement."
        
        lang_info = detector.detect(text)
        
        assert lang_info.language == "fr"
        assert lang_info.confidence > 0.9
    
    def test_detect_german(self):
        """Test detecting German text."""
        detector = LanguageDetector()
        text = "Dies ist ein Beispieltext auf Deutsch, der korrekt erkannt werden sollte."
        
        lang_info = detector.detect(text)
        
        assert lang_info.language == "de"
        assert lang_info.confidence > 0.9
    
    def test_detect_short_text_fails(self):
        """Test that short text raises error."""
        detector = LanguageDetector()
        text = "Short"
        
        with pytest.raises(ValueError, match="too short"):
            detector.detect(text)
    
    def test_detect_with_custom_min_length(self):
        """Test detection with custom minimum length."""
        detector = LanguageDetector()
        text = "This is a medium length text for testing."
        
        lang_info = detector.detect(text, min_length=20)
        
        assert lang_info.language == "en"
    
    def test_detect_multiple(self):
        """Test detecting multiple possible languages."""
        detector = LanguageDetector()
        text = "This is English text with some français mixed in for testing purposes."
        
        langs = detector.detect_multiple(text, top_n=3)
        
        assert len(langs) <= 3
        assert all(isinstance(lang, LanguageInfo) for lang in langs)
        assert langs[0].confidence >= langs[1].confidence if len(langs) > 1 else True
    
    def test_is_supported(self):
        """Test checking if language is supported."""
        detector = LanguageDetector()
        
        assert detector.is_supported("en") is True
        assert detector.is_supported("es") is True
        assert detector.is_supported("fr") is True
        assert detector.is_supported("xyz") is False
    
    def test_get_language_name(self):
        """Test getting language names."""
        detector = LanguageDetector()
        
        assert detector.get_language_name("en") == "English"
        assert detector.get_language_name("es") == "Spanish"
        assert detector.get_language_name("fr") == "French"
        assert detector.get_language_name("de") == "German"
        # Unknown language returns the code
        assert detector.get_language_name("xyz") == "XYZ"


class TestLanguageInfo:
    """Test LanguageInfo dataclass."""
    
    def test_language_info_creation(self):
        """Test creating LanguageInfo."""
        lang_info = LanguageInfo(
            language="en",
            confidence=0.95,
            detected=True
        )
        
        assert lang_info.language == "en"
        assert lang_info.confidence == 0.95
        assert lang_info.detected is True
    
    def test_language_info_to_dict(self):
        """Test LanguageInfo serialization."""
        lang_info = LanguageInfo(
            language="es",
            confidence=0.88,
            detected=False
        )
        
        data = lang_info.to_dict()
        
        assert data["language"] == "es"
        assert data["confidence"] == 0.88
        assert data["detected"] is False


class TestTranslationManager:
    """Test translation management functionality."""
    
    def test_add_translation(self):
        """Test adding a translation link."""
        manager = TranslationManager()
        
        manager.add_translation(
            source_doc_id="doc_en_123",
            translation_doc_id="doc_es_456",
            language="es",
            translator="John Doe"
        )
        
        translations = manager.get_translations("doc_en_123")
        assert len(translations) == 1
        assert translations[0].document_id == "doc_es_456"
        assert translations[0].language == "es"
        assert translations[0].translator == "John Doe"
    
    def test_add_multiple_translations(self):
        """Test adding multiple translations."""
        manager = TranslationManager()
        
        manager.add_translation("doc_en", "doc_es", "es")
        manager.add_translation("doc_en", "doc_fr", "fr")
        manager.add_translation("doc_en", "doc_de", "de")
        
        translations = manager.get_translations("doc_en")
        assert len(translations) == 3
        languages = [t.language for t in translations]
        assert "es" in languages
        assert "fr" in languages
        assert "de" in languages
    
    def test_get_translation_by_language(self):
        """Test getting translation by language."""
        manager = TranslationManager()
        
        manager.add_translation("doc_en", "doc_es", "es")
        manager.add_translation("doc_en", "doc_fr", "fr")
        
        spanish = manager.get_translation_by_language("doc_en", "es")
        assert spanish is not None
        assert spanish.language == "es"
        assert spanish.document_id == "doc_es"
        
        german = manager.get_translation_by_language("doc_en", "de")
        assert german is None
    
    def test_has_translation(self):
        """Test checking if translation exists."""
        manager = TranslationManager()
        
        manager.add_translation("doc_en", "doc_es", "es")
        
        assert manager.has_translation("doc_en", "es") is True
        assert manager.has_translation("doc_en", "fr") is False
        assert manager.has_translation("doc_xyz", "es") is False
    
    def test_get_translations_empty(self):
        """Test getting translations for non-existent document."""
        manager = TranslationManager()
        
        translations = manager.get_translations("doc_nonexistent")
        assert translations == []


class TestTranslationLink:
    """Test TranslationLink dataclass."""
    
    def test_translation_link_creation(self):
        """Test creating TranslationLink."""
        link = TranslationLink(
            document_id="doc_es_456",
            language="es",
            translator="Jane Doe",
            translated_at="2025-10-29T12:00:00Z"
        )
        
        assert link.document_id == "doc_es_456"
        assert link.language == "es"
        assert link.translator == "Jane Doe"
        assert link.translated_at == "2025-10-29T12:00:00Z"
    
    def test_translation_link_to_dict(self):
        """Test TranslationLink serialization."""
        link = TranslationLink(
            document_id="doc_fr_789",
            language="fr",
            translator="Bob Smith"
        )
        
        data = link.to_dict()
        
        assert data["document_id"] == "doc_fr_789"
        assert data["language"] == "fr"
        assert data["translator"] == "Bob Smith"
        assert data["translated_at"] is None


class TestCreateTranslationMetadata:
    """Test translation metadata creation."""
    
    def test_create_translation_metadata(self):
        """Test creating C2PA translation metadata."""
        translations = [
            TranslationLink("doc_es", "es", "Translator 1"),
            TranslationLink("doc_fr", "fr", "Translator 2")
        ]
        
        metadata = create_translation_metadata(translations)
        
        assert metadata["label"] == "encypher.translations"
        assert "translations" in metadata["data"]
        assert len(metadata["data"]["translations"]) == 2
    
    def test_create_translation_metadata_empty(self):
        """Test creating metadata with no translations."""
        metadata = create_translation_metadata([])
        
        assert metadata["label"] == "encypher.translations"
        assert metadata["data"]["translations"] == []


class TestExtractLanguageFromFrontmatter:
    """Test extracting language from frontmatter."""
    
    def test_extract_from_lang_field(self):
        """Test extracting from 'lang' field."""
        frontmatter = {"lang": "en"}
        
        language = extract_language_from_frontmatter(frontmatter)
        
        assert language == "en"
    
    def test_extract_from_language_field(self):
        """Test extracting from 'language' field."""
        frontmatter = {"language": "es"}
        
        language = extract_language_from_frontmatter(frontmatter)
        
        assert language == "es"
    
    def test_extract_from_locale_field(self):
        """Test extracting from 'locale' field."""
        frontmatter = {"locale": "fr"}
        
        language = extract_language_from_frontmatter(frontmatter)
        
        assert language == "fr"
    
    def test_extract_with_locale_format(self):
        """Test extracting from locale format (e.g., en-US)."""
        frontmatter = {"lang": "en-US"}
        
        language = extract_language_from_frontmatter(frontmatter)
        
        assert language == "en"
    
    def test_extract_missing(self):
        """Test extracting when no language field exists."""
        frontmatter = {"title": "Test", "author": "John"}
        
        language = extract_language_from_frontmatter(frontmatter)
        
        assert language is None
    
    def test_extract_priority(self):
        """Test that 'lang' takes priority over 'language'."""
        frontmatter = {"lang": "en", "language": "es"}
        
        language = extract_language_from_frontmatter(frontmatter)
        
        # Should use 'lang' first
        assert language == "en"


class TestDetectLanguageFromFile:
    """Test detecting language from file."""
    
    def test_detect_from_file(self, tmp_path):
        """Test detecting language from file content."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("This is English text for testing language detection from files.")
        
        lang_info = detect_language_from_file(file_path)
        
        assert lang_info.language == "en"
        assert lang_info.detected is True
    
    def test_detect_from_file_with_fallback(self, tmp_path):
        """Test fallback when detection fails."""
        file_path = tmp_path / "short.txt"
        file_path.write_text("Hi")  # Too short
        
        lang_info = detect_language_from_file(file_path, fallback="en")
        
        assert lang_info.language == "en"
        assert lang_info.confidence == 0.0
        assert lang_info.detected is False
    
    def test_detect_from_file_no_fallback_fails(self, tmp_path):
        """Test that detection fails without fallback."""
        file_path = tmp_path / "short.txt"
        file_path.write_text("Hi")
        
        with pytest.raises(ValueError):
            detect_language_from_file(file_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
