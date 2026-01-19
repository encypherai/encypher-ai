"""
Sentence parsing and hashing utilities.
"""

import hashlib
import re
import unicodedata
from typing import List


def parse_sentences(text: str) -> List[str]:
    """
    Parse text into sentences.

    Uses simple regex for v1. Can be upgraded to spaCy/nltk for better accuracy later.

    Args:
        text: Input text to parse

    Returns:
        List of sentences
    """
    # Split on sentence terminators followed by whitespace
    # This handles periods, exclamation marks, and question marks
    sentences = re.split(r"(?<=[.!?])\s+", text)

    # Clean and filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences


def compute_sentence_hash(sentence: str) -> str:
    """
    Compute SHA-256 hash of sentence for lookup.

    Args:
        sentence: Sentence text

    Returns:
        Hexadecimal hash string
    """
    normalized = unicodedata.normalize("NFC", sentence)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_text_hash(text: str) -> str:
    """
    Compute SHA-256 hash of full text for tamper detection.

    Args:
        text: Full text content

    Returns:
        Hexadecimal hash string
    """
    normalized = unicodedata.normalize("NFC", text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
