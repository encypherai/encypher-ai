"""
Word-level text segmentation.

Provides the finest-grained segmentation for Merkle trees.
"""

import re
from typing import List


def segment_words_simple(text: str, include_punctuation: bool = False, min_length: int = 1) -> List[str]:
    """
    Segment text into words using simple regex.

    Args:
        text: Input text
        include_punctuation: Include punctuation as separate tokens
        min_length: Minimum word length

    Returns:
        List of words

    Example:
        >>> segment_words_simple("Hello, world!")
        ['Hello', 'world']
        >>> segment_words_simple("Hello, world!", include_punctuation=True)
        ['Hello', ',', 'world', '!']
    """
    if not text or not text.strip():
        return []

    if include_punctuation:
        # Split on whitespace but keep punctuation
        # This regex splits on spaces but keeps punctuation attached or separate
        words = re.findall(r"\w+|[^\w\s]", text)
    else:
        # Split on non-word characters
        words = re.findall(r"\b\w+\b", text)

    # Filter by minimum length
    return [w for w in words if len(w) >= min_length]


def segment_words_with_positions(text: str, include_punctuation: bool = False) -> List[tuple[str, int, int]]:
    """
    Segment text into words with character positions.

    Args:
        text: Input text
        include_punctuation: Include punctuation tokens

    Returns:
        List of (word, start_pos, end_pos) tuples

    Example:
        >>> segment_words_with_positions("Hello world")
        [('Hello', 0, 5), ('world', 6, 11)]
    """
    if not text or not text.strip():
        return []

    results = []

    if include_punctuation:
        pattern = r"\w+|[^\w\s]"
    else:
        pattern = r"\b\w+\b"

    for match in re.finditer(pattern, text):
        word = match.group()
        start = match.start()
        end = match.end()
        results.append((word, start, end))

    return results


def count_words(text: str, include_punctuation: bool = False) -> int:
    """
    Count words in text.

    Args:
        text: Input text
        include_punctuation: Count punctuation as words

    Returns:
        Number of words
    """
    return len(segment_words_simple(text, include_punctuation=include_punctuation))


def segment_words_normalized(text: str, lowercase: bool = True, remove_numbers: bool = False, min_length: int = 1) -> List[str]:
    """
    Segment text into normalized words.

    Args:
        text: Input text
        lowercase: Convert to lowercase
        remove_numbers: Exclude numeric tokens
        min_length: Minimum word length

    Returns:
        List of normalized words
    """
    words = segment_words_simple(text, include_punctuation=False, min_length=min_length)

    normalized = []
    for word in words:
        if remove_numbers and word.isdigit():
            continue

        if lowercase:
            word = word.lower()

        normalized.append(word)

    return normalized
