"""
Text segmentation utilities for hierarchical content attribution.

This package provides:
- Default segmentation (spaCy-based with Unicode normalization) - RECOMMENDED
- Word-level segmentation (finest granularity)
- Sentence-level segmentation
- Paragraph-level segmentation
- Section-level segmentation
- Hierarchical structure building

By default, spaCy is used for accurate boundary detection and tokenization.
"""
from .sentence import segment_sentences
from .paragraph import segment_paragraphs
from .section import segment_sections
from .word import segment_words_simple, segment_words_normalized
from .hierarchical import HierarchicalSegmenter, build_hierarchical_structure

# Default segmenter (spaCy-based with Unicode normalization) - RECOMMENDED
try:
    from .default import (
        DefaultSegmenter,
        segment_sentences_default,
        segment_words_default,
        normalize_for_hashing,
        normalize_unicode,
        SPACY_AVAILABLE
    )
    DEFAULT_AVAILABLE = True
except ImportError:
    DEFAULT_AVAILABLE = False
    DefaultSegmenter = None
    segment_sentences_default = None
    segment_words_default = None
    normalize_for_hashing = None
    normalize_unicode = None
    SPACY_AVAILABLE = False

# Advanced segmentation (for special use cases)
try:
    from .advanced import AdvancedSegmenter, segment_sentences_advanced, segment_words, normalize_text_advanced
    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False
    AdvancedSegmenter = None
    segment_sentences_advanced = None
    segment_words = None
    normalize_text_advanced = None

__all__ = [
    # Default (recommended)
    "DefaultSegmenter",
    "segment_sentences_default",
    "segment_words_default",
    "normalize_for_hashing",
    "normalize_unicode",
    "DEFAULT_AVAILABLE",
    "SPACY_AVAILABLE",
    # Basic segmentation
    "segment_sentences",
    "segment_paragraphs",
    "segment_sections",
    "segment_words_simple",
    "segment_words_normalized",
    # Hierarchical
    "HierarchicalSegmenter",
    "build_hierarchical_structure",
    # Advanced (special use cases)
    "AdvancedSegmenter",
    "segment_sentences_advanced",
    "segment_words",
    "normalize_text_advanced",
    "ADVANCED_AVAILABLE",
]
