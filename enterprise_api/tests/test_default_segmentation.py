"""
Tests for default spaCy-based segmentation with Unicode normalization.
"""
import pytest

# Check if spaCy is available
try:
    import spacy
    try:
        _nlp = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except OSError:
        SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False

from app.utils.segmentation import (
    DefaultSegmenter,
    HierarchicalSegmenter,
    normalize_for_hashing,
    normalize_unicode,
    segment_sentences_default,
    segment_words_default,
)


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not loaded")
class TestDefaultSegmentation:
    """Test default spaCy-based segmentation."""
    
    def test_sentence_segmentation_with_abbreviations(self):
        """spaCy should handle abbreviations correctly."""
        text = "Dr. Smith works at Inc. Corp. He is great."
        sentences = segment_sentences_default(text)
        
        # spaCy should correctly identify 2 sentences
        assert len(sentences) == 2
        assert "Dr. Smith" in sentences[0]
        assert "He is great." in sentences[1]
    
    def test_word_tokenization(self):
        """spaCy should tokenize words accurately."""
        text = "Hello, world! How are you?"
        words = segment_words_default(text, remove_punctuation=True)
        
        assert "Hello" in words
        assert "world" in words
        assert "How" in words
        assert "," not in words  # Punctuation removed
    
    def test_original_text_preserved(self):
        """Original text should be preserved, not normalized."""
        text = "Hello—World"  # em-dash
        sentences = segment_sentences_default(text, normalize=True)
        
        # Original em-dash should be preserved
        assert "—" in sentences[0]
        assert sentences[0] == "Hello—World"
    
    def test_hierarchical_segmenter_uses_spacy(self):
        """HierarchicalSegmenter should use spaCy by default."""
        text = "Dr. Smith works here. He is great. Another sentence."
        segmenter = HierarchicalSegmenter(text)
        
        # Should get accurate sentence count with spaCy
        assert len(segmenter.sentences) == 3


class TestUnicodeNormalization:
    """Test Unicode normalization."""
    
    def test_dash_normalization(self):
        """Different dash types should normalize to hyphen."""
        # em-dash
        assert normalize_unicode("Hello—world") == "Hello-world"
        # en-dash
        assert normalize_unicode("Hello–world") == "Hello-world"
        # minus sign
        assert normalize_unicode("Hello−world") == "Hello-world"
    
    def test_quote_normalization(self):
        """Curly quotes should normalize to straight quotes."""
        # Left and right double quotes
        assert normalize_unicode("\u201CHello\u201D") == '"Hello"'
        # Left and right single quotes  
        assert normalize_unicode("\u2018Hello\u2019") == "'Hello'"
    
    def test_whitespace_normalization(self):
        """Different whitespace should normalize to regular space."""
        # non-breaking space
        text_with_nbsp = "Hello\u00A0world"
        assert normalize_unicode(text_with_nbsp) == "Hello world"
    
    def test_line_ending_normalization(self):
        """Different line endings should normalize to LF."""
        assert normalize_unicode("Hello\r\nworld") == "Hello\nworld"  # CRLF
        assert normalize_unicode("Hello\rworld") == "Hello\nworld"    # CR
    
    def test_nfc_normalization(self):
        """Unicode should be in NFC form."""
        # é can be represented as single char or e + combining accent
        text1 = "café"  # é as single character
        text2 = "cafe\u0301"  # e + combining acute accent
        
        norm1 = normalize_unicode(text1)
        norm2 = normalize_unicode(text2)
        
        # Both should normalize to same form
        assert norm1 == norm2


class TestHashingNormalization:
    """Test normalization for hashing."""
    
    def test_lowercase_normalization(self):
        """Lowercase normalization for hashing."""
        text = "Hello World"
        normalized = normalize_for_hashing(text, lowercase=True)
        
        assert normalized == "hello world"
    
    def test_combined_normalization(self):
        """Combined Unicode + lowercase normalization."""
        text = "Hello—World"  # em-dash
        normalized = normalize_for_hashing(text, 
                                          lowercase=True,
                                          normalize_unicode_chars=True)
        
        assert normalized == "hello-world"  # hyphen, lowercase
    
    def test_original_unchanged(self):
        """Original text should not be modified."""
        original = "Hello—World"
        normalized = normalize_for_hashing(original)
        
        # Original should still have em-dash
        assert original == "Hello—World"
        # Normalized should have hyphen
        assert normalized == "hello-world"


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not loaded")
class TestDefaultSegmenterClass:
    """Test DefaultSegmenter class."""
    
    def test_initialization(self):
        """Should initialize with default model."""
        segmenter = DefaultSegmenter()
        assert segmenter.nlp is not None
    
    def test_segment_sentences(self):
        """Should segment sentences accurately."""
        segmenter = DefaultSegmenter()
        text = "First sentence. Second sentence! Third sentence?"
        sentences = segmenter.segment_sentences(text)
        
        assert len(sentences) == 3
    
    def test_segment_words(self):
        """Should tokenize words accurately."""
        segmenter = DefaultSegmenter()
        text = "Hello, world!"
        words = segmenter.segment_words(text, remove_punctuation=True)
        
        assert "Hello" in words
        assert "world" in words
        assert "," not in words
    
    def test_normalize_for_hashing(self):
        """Should normalize text for hashing."""
        segmenter = DefaultSegmenter()
        text = "Hello—World"
        normalized = segmenter.normalize_for_hashing(text, lowercase=True)
        
        assert normalized == "hello-world"


class TestRealWorldExamples:
    """Test with real-world text examples."""
    
    def test_mixed_unicode(self):
        """Handle mixed Unicode characters."""
        text = "The caf\u00E9's \u201Cspecial\u201D menu\u2014available today!"
        normalized = normalize_unicode(text)
        
        # Should normalize quotes and dash
        assert '"' in normalized
        assert '-' in normalized
        # Should preserve café
        assert 'caf' in normalized
    
    def test_windows_vs_unix_line_endings(self):
        """Different line endings should normalize consistently."""
        text_windows = "Line 1\r\nLine 2\r\nLine 3"
        text_unix = "Line 1\nLine 2\nLine 3"
        
        norm_windows = normalize_unicode(text_windows)
        norm_unix = normalize_unicode(text_unix)
        
        # Both should normalize to same form
        assert norm_windows == norm_unix
        assert norm_windows == "Line 1\nLine 2\nLine 3"
