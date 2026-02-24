"""
Default text segmentation using spaCy with Unicode normalization.

This module provides the default segmentation strategy:
- spaCy for accurate boundary detection and tokenization
- Unicode normalization for consistent hashing (without modifying original content)
- Preserves original text while normalizing for comparison

IMPORTANT: We NEVER modify the original content stored in the tree.
Normalization is only applied to hash computation for matching.
"""

import logging
import unicodedata
from typing import List, Optional

logger = logging.getLogger(__name__)

# Try to import spaCy
try:
    import spacy

    SPACY_AVAILABLE = True

    # Load default model
    try:
        _default_nlp: Optional["spacy.language.Language"] = spacy.load("en_core_web_sm")
        logger.info("Loaded spaCy model: en_core_web_sm")
    except OSError as e:
        logger.warning(f"spaCy model not found: {e}")
        logger.warning(
            "Install with: uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
        )
        _default_nlp = None
        SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False
    _default_nlp = None
    logger.warning("spaCy not available. Install with: uv add spacy")


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode characters for consistent hashing.

    This handles:
    - Different dash types (em-dash, en-dash, hyphen)
    - Different quote types (curly vs straight)
    - Different whitespace (non-breaking space, etc.)
    - Different line endings (CRLF vs LF)
    - Combining characters (é vs e + ́)

    Args:
        text: Input text

    Returns:
        Unicode-normalized text

    Example:
        >>> normalize_unicode("Hello—world")  # em-dash
        'Hello-world'  # hyphen
        >>> normalize_unicode("café")  # é as single char
        'café'  # é as e + combining accent (or vice versa, normalized)
    """
    # Apply NFC normalization (canonical composition)
    # This ensures characters are represented consistently
    text = unicodedata.normalize("NFC", text)

    # Normalize different dash types to standard hyphen
    dash_variants = [
        "\u2013",  # en-dash
        "\u2014",  # em-dash
        "\u2015",  # horizontal bar
        "\u2212",  # minus sign
    ]
    for dash in dash_variants:
        text = text.replace(dash, "-")

    # Normalize different quote types
    quote_pairs = [
        ("\u2018", "'"),  # left single quote
        ("\u2019", "'"),  # right single quote
        ("\u201c", '"'),  # left double quote
        ("\u201d", '"'),  # right double quote
    ]
    for fancy, simple in quote_pairs:
        text = text.replace(fancy, simple)

    # Normalize whitespace
    whitespace_variants = [
        "\u00a0",  # non-breaking space
        "\u2003",  # em space
        "\u2009",  # thin space
    ]
    for ws in whitespace_variants:
        text = text.replace(ws, " ")

    # Normalize line endings to LF
    text = text.replace("\r\n", "\n")  # Windows CRLF
    text = text.replace("\r", "\n")  # Old Mac CR

    return text


def segment_sentences_default(text: str, normalize: bool = True) -> List[str]:
    """
    Segment text into sentences using best available method.

    Uses spaCy if available, falls back to regex.
    Optionally applies Unicode normalization for consistent hashing.

    Args:
        text: Input text
        normalize: Apply Unicode normalization

    Returns:
        List of sentences (original text preserved)

    Note:
        Normalization is applied to a COPY for boundary detection.
        Original text is preserved in the returned segments.
    """
    if not text or not text.strip():
        return []

    # Normalize for boundary detection (but preserve original)
    text_for_detection = normalize_unicode(text) if normalize else text

    if SPACY_AVAILABLE and _default_nlp:
        # Use spaCy for accurate sentence boundary detection
        doc = _default_nlp(text_for_detection)

        # Extract sentences, but map back to original text positions.
        # Do NOT strip the original slice — stripping removes leading \n\n that precede
        # block-level elements like ATX headings (## Heading), which breaks markdown
        # rendering and causes build_embedding_plan to return None (text mismatch).
        sentences = []
        for sent in doc.sents:
            # Get the original text for this sentence
            start = sent.start_char
            end = sent.end_char
            original_sent = text[start:end]
            if original_sent.strip():  # filter visibly-empty spans, keep whitespace in non-empty ones
                sentences.append(original_sent)

        return sentences
    else:
        # Fallback to regex-based segmentation
        from .sentence import segment_sentences

        return segment_sentences(text)


def segment_words_default(text: str, normalize: bool = True, remove_punctuation: bool = False) -> List[str]:
    """
    Segment text into words using best available method.

    Uses spaCy if available, falls back to regex.

    Args:
        text: Input text
        normalize: Apply Unicode normalization
        remove_punctuation: Exclude punctuation tokens

    Returns:
        List of words (original text preserved)
    """
    if not text or not text.strip():
        return []

    # Normalize for tokenization
    text_for_tokenization = normalize_unicode(text) if normalize else text

    if SPACY_AVAILABLE and _default_nlp:
        # Use spaCy for accurate word tokenization
        doc = _default_nlp(text_for_tokenization)

        words = []
        for token in doc:
            if token.is_space:
                continue
            if remove_punctuation and token.is_punct:
                continue

            # Get original text for this token
            start = token.idx
            end = token.idx + len(token.text)
            original_word = text[start:end]
            words.append(original_word)

        return words
    else:
        # Fallback to regex-based segmentation
        from .word import segment_words_simple

        return segment_words_simple(text, include_punctuation=not remove_punctuation)


def normalize_for_hashing(text: str, lowercase: bool = True, normalize_unicode_chars: bool = True) -> str:
    """
    Normalize text for hash computation (NOT for storage).

    This is used to create consistent hashes for matching,
    while the original text is preserved in the Merkle tree.

    Args:
        text: Input text
        lowercase: Convert to lowercase
        normalize_unicode_chars: Apply Unicode normalization

    Returns:
        Normalized text (for hashing only)

    Example:
        >>> original = "Hello—World"
        >>> normalized = normalize_for_hashing(original)
        >>> # Store original in tree, use normalized for hash
    """
    result = text

    if normalize_unicode_chars:
        result = normalize_unicode(result)

    if lowercase:
        result = result.lower()

    return result


class DefaultSegmenter:
    """
    Default segmenter using spaCy with Unicode normalization.

    This is the recommended segmenter for production use.
    It provides:
    - Accurate sentence boundary detection
    - Proper word tokenization
    - Unicode normalization for consistent hashing
    - Original text preservation
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize default segmenter.

        Args:
            model_name: spaCy model to use
        """
        if not SPACY_AVAILABLE:
            raise ImportError("spaCy is required for default segmenter. Install with: uv add spacy && python -m spacy download en_core_web_sm")

        if model_name == "en_core_web_sm" and _default_nlp:
            self.nlp = _default_nlp
        else:
            self.nlp = spacy.load(model_name)

        logger.info(f"Initialized DefaultSegmenter with model: {model_name}")

    def segment_sentences(self, text: str, normalize: bool = True) -> List[str]:
        """Segment into sentences."""
        return segment_sentences_default(text, normalize=normalize)

    def segment_words(self, text: str, normalize: bool = True, remove_punctuation: bool = False) -> List[str]:
        """Segment into words."""
        return segment_words_default(text, normalize=normalize, remove_punctuation=remove_punctuation)

    def normalize_for_hashing(self, text: str, lowercase: bool = True) -> str:
        """Normalize text for hash computation."""
        return normalize_for_hashing(text, lowercase=lowercase)
