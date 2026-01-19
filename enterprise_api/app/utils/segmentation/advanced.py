"""
Advanced text segmentation using NLP (spaCy).

Provides more accurate segmentation than regex-based approaches.
Requires: spacy and a language model (e.g., en_core_web_sm)

Install with: uv add spacy
Then: python -m spacy download en_core_web_sm
"""

import logging
from functools import lru_cache
from typing import List

logger = logging.getLogger(__name__)

# Try to import spaCy (optional dependency)
try:
    import spacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available. Advanced segmentation disabled. Install with: uv add spacy")


@lru_cache(maxsize=4)
def get_spacy_model(model_name: str):
    """
    Get cached spaCy model to avoid reloading.
    """
    if not SPACY_AVAILABLE:
        raise ImportError("spaCy is required for advanced segmentation. Install with: uv add spacy && python -m spacy download en_core_web_sm")

    try:
        logger.info(f"Loading spaCy model: {model_name}")
        return spacy.load(model_name)
    except OSError:
        raise OSError(f"spaCy model '{model_name}' not found. Download with: python -m spacy download {model_name}")


class AdvancedSegmenter:
    """
    Advanced text segmentation using spaCy NLP.

    Provides:
    - Accurate sentence boundary detection
    - Word tokenization
    - Lemmatization for normalization
    - Part-of-speech tagging
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize advanced segmenter.

        Args:
            model_name: spaCy model to use (default: en_core_web_sm)

        Raises:
            ImportError: If spaCy is not installed
            OSError: If spaCy model is not downloaded
        """
        self.nlp = get_spacy_model(model_name)

    def segment_sentences(self, text: str) -> List[str]:
        """
        Segment text into sentences using spaCy.

        This is much more accurate than regex-based segmentation,
        properly handling abbreviations, numbers, etc.

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        doc = self.nlp(text)
        return [sent.text.strip() for sent in doc.sents]

    def segment_words(self, text: str, remove_punctuation: bool = False) -> List[str]:
        """
        Segment text into words (tokens).

        Args:
            text: Input text
            remove_punctuation: If True, exclude punctuation tokens

        Returns:
            List of words
        """
        doc = self.nlp(text)

        if remove_punctuation:
            return [token.text for token in doc if not token.is_punct and not token.is_space]
        else:
            return [token.text for token in doc if not token.is_space]

    def normalize_text(
        self, text: str, lowercase: bool = True, lemmatize: bool = True, remove_stopwords: bool = False, remove_punctuation: bool = False
    ) -> str:
        """
        Normalize text for better matching.

        Args:
            text: Input text
            lowercase: Convert to lowercase
            lemmatize: Convert words to base form (run -> run, running -> run)
            remove_stopwords: Remove common words (the, a, is, etc.)
            remove_punctuation: Remove punctuation

        Returns:
            Normalized text
        """
        doc = self.nlp(text)
        tokens = []

        for token in doc:
            # Skip based on filters
            if token.is_space:
                continue
            if remove_punctuation and token.is_punct:
                continue
            if remove_stopwords and token.is_stop:
                continue

            # Get token text
            if lemmatize:
                word = token.lemma_
            else:
                word = token.text

            if lowercase:
                word = word.lower()

            tokens.append(word)

        return " ".join(tokens)

    def segment_sentences_normalized(self, text: str, **normalize_kwargs) -> List[str]:
        """
        Segment into sentences and normalize each.

        Args:
            text: Input text
            **normalize_kwargs: Arguments for normalize_text()

        Returns:
            List of normalized sentences
        """
        sentences = self.segment_sentences(text)
        return [self.normalize_text(sent, **normalize_kwargs) for sent in sentences]

    def get_sentence_boundaries(self, text: str) -> List[tuple[int, int]]:
        """
        Get character positions of sentence boundaries.

        Args:
            text: Input text

        Returns:
            List of (start, end) character positions
        """
        doc = self.nlp(text)
        return [(sent.start_char, sent.end_char) for sent in doc.sents]


def segment_sentences_advanced(text: str, model: str = "en_core_web_sm") -> List[str]:
    """
    Segment sentences using spaCy (convenience function).

    Args:
        text: Input text
        model: spaCy model name

    Returns:
        List of sentences
    """
    segmenter = AdvancedSegmenter(model)
    return segmenter.segment_sentences(text)


def segment_words(text: str, model: str = "en_core_web_sm", remove_punctuation: bool = False) -> List[str]:
    """
    Segment text into words (convenience function).

    Args:
        text: Input text
        model: spaCy model name
        remove_punctuation: Remove punctuation tokens

    Returns:
        List of words
    """
    segmenter = AdvancedSegmenter(model)
    return segmenter.segment_words(text, remove_punctuation=remove_punctuation)


def normalize_text_advanced(text: str, model: str = "en_core_web_sm", **kwargs) -> str:
    """
    Normalize text using spaCy (convenience function).

    Args:
        text: Input text
        model: spaCy model name
        **kwargs: Arguments for normalize_text()

    Returns:
        Normalized text
    """
    segmenter = AdvancedSegmenter(model)
    return segmenter.normalize_text(text, **kwargs)
