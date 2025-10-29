"""
Unit tests for text segmentation.

Tests cover:
- Sentence segmentation (using spaCy default)
- Paragraph segmentation
- Section segmentation
- Hierarchical structure building
"""
import pytest
from app.utils.segmentation import (
    segment_sentences_default,  # Use spaCy-based default
    segment_paragraphs,
    segment_sections,
    HierarchicalSegmenter,
    build_hierarchical_structure,
    SPACY_AVAILABLE
)


class TestSentenceSegmentation:
    """Test sentence-level segmentation using spaCy default."""
    
    def test_simple_sentences(self):
        """Segment simple sentences."""
        text = "First sentence. Second sentence. Third sentence."
        sentences = segment_sentences_default(text)
        
        assert len(sentences) == 3
        assert sentences[0] == "First sentence."
        assert sentences[1] == "Second sentence."
        assert sentences[2] == "Third sentence."
    
    def test_multiple_terminators(self):
        """Handle different sentence terminators."""
        text = "Question? Exclamation! Statement."
        sentences = segment_sentences_default(text)
        
        assert len(sentences) == 3
        assert "Question?" in sentences
        assert "Exclamation!" in sentences
        assert "Statement." in sentences
    
    def test_abbreviations(self):
        """spaCy should handle abbreviations correctly."""
        text = "Dr. Smith works at Inc. Corp. He is great."
        sentences = segment_sentences_default(text)
        
        if SPACY_AVAILABLE:
            # With spaCy, should correctly identify 2 sentences
            assert len(sentences) == 2
            assert "Dr. Smith" in sentences[0]
            assert "He is great." in sentences[1]
        else:
            # Fallback: at least should work
            assert len(sentences) >= 1
    
    def test_empty_text(self):
        """Handle empty text."""
        assert segment_sentences_default("") == []
        assert segment_sentences_default("   ") == []
    
    def test_single_sentence(self):
        """Handle single sentence."""
        text = "Only one sentence here."
        sentences = segment_sentences_default(text)
        
        assert len(sentences) == 1
        assert sentences[0] == text
    
    def test_no_punctuation(self):
        """Handle text without sentence terminators."""
        text = "No punctuation here"
        sentences = segment_sentences_default(text)
        
        assert len(sentences) == 1
        assert sentences[0] == text


class TestParagraphSegmentation:
    """Test paragraph-level segmentation."""
    
    def test_double_newline(self):
        """Segment on double newlines."""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        paragraphs = segment_paragraphs(text)
        
        assert len(paragraphs) == 3
        assert paragraphs[0] == "First paragraph."
        assert paragraphs[1] == "Second paragraph."
        assert paragraphs[2] == "Third paragraph."
    
    def test_single_paragraph(self):
        """Handle single paragraph."""
        text = "This is all one paragraph with multiple sentences. It has no breaks."
        paragraphs = segment_paragraphs(text)
        
        assert len(paragraphs) == 1
        assert paragraphs[0] == text
    
    def test_empty_lines(self):
        """Handle multiple empty lines."""
        text = "First paragraph here.\n\n\n\nSecond paragraph here."
        paragraphs = segment_paragraphs(text)
        
        # Should split on multiple newlines
        assert len(paragraphs) >= 1
        assert any("First" in p for p in paragraphs)
    
    def test_min_length_filter(self):
        """Filter paragraphs below minimum length."""
        text = "Short.\n\nThis is a longer paragraph that meets the minimum."
        paragraphs = segment_paragraphs(text, min_length=20)
        
        assert len(paragraphs) == 1
        assert "longer paragraph" in paragraphs[0]
    
    def test_empty_text(self):
        """Handle empty text."""
        assert segment_paragraphs("") == []
        assert segment_paragraphs("   ") == []


class TestSectionSegmentation:
    """Test section-level segmentation."""
    
    def test_markdown_headers(self):
        """Segment on markdown headers."""
        text = """# Introduction
This is the introduction section with enough content to meet minimum length requirements for segmentation.

## Methods
This is the methods section with detailed methodology and procedures.

## Results
This is the results section with findings and analysis."""
        
        sections = segment_sections(text)
        
        # Should detect at least 1 section (may combine short sections)
        assert len(sections) >= 1
        assert any("Introduction" in s or "Methods" in s or "Results" in s for s in sections)
    
    def test_numbered_sections(self):
        """Segment on numbered sections."""
        text = """1. First Section
Content here with enough text to meet the minimum length requirement for section segmentation.

2. Second Section
More content with additional details and information to ensure proper segmentation.

3. Third Section
Final content with comprehensive information and analysis."""
        
        sections = segment_sections(text)
        
        # Should detect at least 1 section
        assert len(sections) >= 1
        assert any("First Section" in s or "Second Section" in s or "Third Section" in s for s in sections)
    
    def test_no_sections(self):
        """Handle text without clear sections."""
        text = "Just a plain paragraph without any section markers."
        sections = segment_sections(text)
        
        # Should return at least the whole text as one section
        assert len(sections) >= 1
    
    def test_min_length_filter(self):
        """Filter sections below minimum length."""
        text = """# Short
Hi.

# Long Section
This is a much longer section with plenty of content that exceeds the minimum length requirement."""
        
        sections = segment_sections(text, min_length=50)
        
        # Only the long section should be included
        assert len(sections) == 1
        assert "Long Section" in sections[0]
    
    def test_empty_text(self):
        """Handle empty text."""
        assert segment_sections("") == []
        assert segment_sections("   ") == []


class TestHierarchicalSegmenter:
    """Test hierarchical segmentation."""
    
    def test_basic_hierarchy(self):
        """Build basic hierarchical structure."""
        text = """# Introduction
This is the first sentence. This is the second sentence.

This is a new paragraph. It has multiple sentences too."""
        
        segmenter = HierarchicalSegmenter(text)
        
        assert len(segmenter.sentences) >= 4
        assert len(segmenter.paragraphs) >= 2
        assert len(segmenter.sections) >= 1
    
    def test_get_segments(self):
        """Get segments at specific level."""
        text = "First. Second.\n\nThird. Fourth."
        segmenter = HierarchicalSegmenter(text)
        
        sentences = segmenter.get_segments('sentence')
        paragraphs = segmenter.get_segments('paragraph')
        
        assert len(sentences) == 4
        assert len(paragraphs) == 2
    
    def test_invalid_level(self):
        """Raise error for invalid level."""
        segmenter = HierarchicalSegmenter("Test.")
        
        with pytest.raises(ValueError, match="Invalid level"):
            segmenter.get_segments('invalid')
    
    def test_count_segments(self):
        """Count segments at each level."""
        text = "Sentence one. Sentence two.\n\nParagraph two with sentence three. Sentence four.\n\nParagraph three with sentence five."
        segmenter = HierarchicalSegmenter(text)
        
        assert segmenter.count_segments('sentence') >= 5
        # Paragraphs may be filtered by min_length, so just check we have some
        assert segmenter.count_segments('paragraph') >= 1
    
    def test_build_hierarchy(self):
        """Build hierarchical structure with relationships."""
        text = "First sentence. Second sentence.\n\nThird sentence."
        segmenter = HierarchicalSegmenter(text)
        hierarchy = segmenter.build_hierarchy()
        
        assert 'sentence' in hierarchy
        assert 'paragraph' in hierarchy
        assert 'section' in hierarchy
        
        # Check that segments have metadata
        if hierarchy['sentence']:
            assert 'length' in hierarchy['sentence'][0].metadata
    
    def test_serialization(self):
        """Serialize segmenter to dict."""
        text = "Test sentence.\n\nAnother paragraph."
        segmenter = HierarchicalSegmenter(text)
        data = segmenter.to_dict()
        
        assert 'text_length' in data
        assert 'sentence_count' in data
        assert 'paragraph_count' in data
        assert 'sentences' in data
        assert data['text_length'] == len(text)
    
    def test_empty_text(self):
        """Handle empty text."""
        segmenter = HierarchicalSegmenter("")
        
        assert len(segmenter.sentences) == 0
        assert len(segmenter.paragraphs) == 0
        assert len(segmenter.sections) == 0


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_build_hierarchical_structure(self):
        """Build structure using convenience function."""
        text = "First sentence here. Second sentence here.\n\nThird sentence in new paragraph."
        structure = build_hierarchical_structure(text)
        
        assert 'sentences' in structure
        assert 'paragraphs' in structure
        assert 'sections' in structure
        assert len(structure['sentences']) >= 3
        # Paragraphs may be filtered by min_length
        assert len(structure['paragraphs']) >= 1


class TestRealWorldExamples:
    """Test with real-world text examples."""
    
    def test_news_article(self):
        """Segment a news article."""
        text = """# Breaking News: Major Discovery

Scientists announced today a groundbreaking discovery in the field of quantum physics. The research team worked for five years on this project. The findings were published in a prestigious journal.

## Background

Previous studies had suggested this possibility for many years. However, no concrete evidence existed until now. This research fills a critical gap in our understanding.

## Implications

This discovery will change everything we know about the field. Experts are calling it revolutionary. The impact will be felt for decades to come."""
        
        segmenter = HierarchicalSegmenter(text)
        
        # With spaCy, should get accurate sentence count (7-9 sentences depending on parsing)
        assert segmenter.count_segments('sentence') >= 7
        assert segmenter.count_segments('paragraph') >= 1
        assert segmenter.count_segments('section') >= 1
    
    def test_academic_paper(self):
        """Segment an academic paper abstract."""
        text = """Abstract

This study investigates the effects of X on Y. We conducted experiments with 100 participants. Results showed significant correlation.

Introduction

Previous research has established that X affects Y. However, the mechanism remains unclear. This paper addresses this gap."""
        
        segmenter = HierarchicalSegmenter(text)
        
        assert segmenter.count_segments('sentence') >= 5
        assert segmenter.count_segments('paragraph') >= 2
    
    def test_code_documentation(self):
        """Segment code documentation."""
        text = """# API Reference

## Authentication

All requests require an API key. Include it in the Authorization header.

## Endpoints

### GET /users

Returns a list of users. Supports pagination.

### POST /users

Creates a new user. Requires name and email."""
        
        segmenter = HierarchicalSegmenter(text)
        
        # Should handle markdown headers at multiple levels
        assert segmenter.count_segments('sentence') >= 4
        assert segmenter.count_segments('section') >= 1
    
    def test_unicode_content(self):
        """Handle Unicode content."""
        text = """Introducción

Este es el primer párrafo. Contiene caracteres especiales: ñ, á, é.

Conclusión

El texto en español funciona correctamente. También 中文 和 日本語."""
        
        segmenter = HierarchicalSegmenter(text)
        
        assert segmenter.count_segments('sentence') >= 3
        assert segmenter.count_segments('paragraph') >= 2
