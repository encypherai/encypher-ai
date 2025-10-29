"""
Sentence-level text segmentation.

Enhanced version of the existing sentence parser with better edge case handling.
"""
import re
from typing import List


def segment_sentences(text: str, min_length: int = 3) -> List[str]:
    """
    Segment text into sentences.
    
    Uses regex-based sentence boundary detection with support for:
    - Standard sentence terminators (. ! ?)
    - Abbreviations (Dr., Mr., etc.)
    - Decimal numbers (3.14)
    - Ellipsis (...)
    
    Args:
        text: Input text to segment
        min_length: Minimum sentence length in characters (default: 3)
    
    Returns:
        List of sentences
    
    Example:
        >>> segment_sentences("Hello world. How are you?")
        ['Hello world.', 'How are you?']
    """
    if not text or not text.strip():
        return []
    
    # Common abbreviations that shouldn't trigger sentence breaks
    abbreviations = {
        'Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Sr.', 'Jr.',
        'vs.', 'etc.', 'i.e.', 'e.g.', 'cf.', 'Inc.', 'Ltd.',
        'Co.', 'Corp.', 'Ave.', 'St.', 'Rd.', 'Blvd.',
        'Jan.', 'Feb.', 'Mar.', 'Apr.', 'Jun.', 'Jul.', 'Aug.', 
        'Sep.', 'Sept.', 'Oct.', 'Nov.', 'Dec.',
        'U.S.', 'U.K.', 'E.U.', 'Ph.D.', 'M.D.', 'B.A.', 'M.A.'
    }
    
    # Temporarily replace abbreviations with placeholders
    protected_text = text
    abbrev_map = {}
    for i, abbrev in enumerate(abbreviations):
        if abbrev in protected_text:
            placeholder = f"__ABBREV_{i}__"
            abbrev_map[placeholder] = abbrev
            protected_text = protected_text.replace(abbrev, placeholder)
    
    # Split on sentence terminators followed by whitespace and capital letter
    # or end of string
    pattern = r'(?<=[.!?])\s+(?=[A-Z])'
    segments = re.split(pattern, protected_text)
    
    # Also handle end of string
    if not segments:
        segments = [protected_text]
    
    # Restore abbreviations
    for i, segment in enumerate(segments):
        for placeholder, abbrev in abbrev_map.items():
            segment = segment.replace(placeholder, abbrev)
        segments[i] = segment
    
    # Clean and filter
    sentences = []
    for segment in segments:
        segment = segment.strip()
        if segment and len(segment) >= min_length:
            sentences.append(segment)
    
    return sentences


def segment_sentences_simple(text: str) -> List[str]:
    """
    Simple sentence segmentation (backward compatible).
    
    Uses basic regex splitting on sentence terminators.
    
    Args:
        text: Input text
    
    Returns:
        List of sentences
    """
    # Split on sentence terminators followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Clean and filter
    return [s.strip() for s in sentences if s.strip()]


def count_sentences(text: str) -> int:
    """
    Count sentences in text.
    
    Args:
        text: Input text
    
    Returns:
        Number of sentences
    """
    return len(segment_sentences(text))


def get_sentence_boundaries(text: str) -> List[tuple[int, int]]:
    """
    Get character positions of sentence boundaries.
    
    Args:
        text: Input text
    
    Returns:
        List of (start, end) tuples for each sentence
    """
    sentences = segment_sentences(text)
    boundaries = []
    current_pos = 0
    
    for sentence in sentences:
        start = text.find(sentence, current_pos)
        if start != -1:
            end = start + len(sentence)
            boundaries.append((start, end))
            current_pos = end
    
    return boundaries
