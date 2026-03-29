"""
Paragraph-level text segmentation.

Segments text into paragraphs based on newline patterns.
"""

import re
from typing import List


def segment_paragraphs(text: str, min_length: int = 1) -> List[str]:
    """
    Segment text into paragraphs.

    Paragraphs are detected by:
    - Double newlines (\\n\\n)
    - Single newlines followed by indentation
    - Markdown paragraph breaks

    Args:
        text: Input text to segment
        min_length: Minimum paragraph length in characters (default: 1)

    Returns:
        List of paragraphs

    Example:
        >>> text = "First paragraph.\\n\\nSecond paragraph."
        >>> segment_paragraphs(text)
        ['First paragraph.', 'Second paragraph.']
    """
    if not text or not text.strip():
        return []

    # Split on double newlines (most common paragraph separator)
    paragraphs = re.split(r"\n\s*\n", text)

    # Clean and filter
    result = []
    for para in paragraphs:
        para = para.strip()
        if para and len(para) >= min_length:
            result.append(para)

    return result


def segment_paragraphs_markdown(text: str) -> List[str]:
    """
    Segment markdown text into paragraphs.

    Handles markdown-specific paragraph breaks including:
    - Headers (# ## ###)
    - Lists (- * +)
    - Code blocks (```)
    - Blockquotes (>)

    Args:
        text: Markdown text

    Returns:
        List of paragraphs
    """
    if not text or not text.strip():
        return []

    # Split on markdown paragraph indicators
    # This includes headers, lists, code blocks, etc.
    lines = text.split("\n")
    paragraphs: List[str] = []
    current_para: List[str] = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Toggle code block state
        if stripped.startswith("```"):
            if current_para:
                paragraphs.append("\n".join(current_para))
                current_para = []
            in_code_block = not in_code_block
            continue

        # If in code block, treat as separate paragraph
        if in_code_block:
            if current_para:
                paragraphs.append("\n".join(current_para))
                current_para = []
            paragraphs.append(line)
            continue

        # Check for paragraph breaks
        is_header = stripped.startswith("#")
        is_list = stripped.startswith(("-", "*", "+", "1.", "2.", "3."))
        is_blockquote = stripped.startswith(">")
        is_empty = not stripped

        if is_empty:
            if current_para:
                paragraphs.append("\n".join(current_para))
                current_para = []
        elif is_header or is_list or is_blockquote:
            if current_para:
                paragraphs.append("\n".join(current_para))
                current_para = []
            paragraphs.append(line)
        else:
            current_para.append(line)

    # Add final paragraph
    if current_para:
        paragraphs.append("\n".join(current_para))

    # Clean and filter
    return [p.strip() for p in paragraphs if p.strip()]


def count_paragraphs(text: str) -> int:
    """
    Count paragraphs in text.

    Args:
        text: Input text

    Returns:
        Number of paragraphs
    """
    return len(segment_paragraphs(text))


def get_paragraph_boundaries(text: str) -> List[tuple[int, int]]:
    """
    Get character positions of paragraph boundaries.

    Args:
        text: Input text

    Returns:
        List of (start, end) tuples for each paragraph
    """
    paragraphs = segment_paragraphs(text)
    boundaries = []
    current_pos = 0

    for paragraph in paragraphs:
        start = text.find(paragraph, current_pos)
        if start != -1:
            end = start + len(paragraph)
            boundaries.append((start, end))
            current_pos = end

    return boundaries
