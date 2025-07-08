"""Utility functions for generating tamper reports."""

from difflib import SequenceMatcher


def generate_diff_report(original: str, modified: str) -> str:
    """Generate a short diff summary between two strings.

    This compares both the visible text and embedded metadata bytes.

    Args:
        original: The reference string believed to be untampered.
        modified: The string under verification.

    Returns:
        A human-friendly summary describing the differences.
    """
    text_matcher = SequenceMatcher(None, original, modified)
    added_chars = 0
    removed_chars = 0
    for tag, i1, i2, j1, j2 in text_matcher.get_opcodes():
        if tag == "insert":
            added_chars += j2 - j1
        elif tag == "delete":
            removed_chars += i2 - i1
        elif tag == "replace":
            removed_chars += i2 - i1
            added_chars += j2 - j1
    from encypher.core.unicode_metadata import UnicodeMetadata

    orig_bytes = UnicodeMetadata.extract_bytes(original)
    mod_bytes = UnicodeMetadata.extract_bytes(modified)

    byte_matcher = SequenceMatcher(None, orig_bytes, mod_bytes)
    added_bytes = 0
    removed_bytes = 0
    for tag, i1, i2, j1, j2 in byte_matcher.get_opcodes():
        if tag == "insert":
            added_bytes += j2 - j1
        elif tag == "delete":
            removed_bytes += i2 - i1
        elif tag == "replace":
            removed_bytes += i2 - i1
            added_bytes += j2 - j1

    parts = []
    if added_chars or removed_chars:
        char_parts = []
        if removed_chars:
            char_parts.append(f"{removed_chars} characters removed")
        if added_chars:
            char_parts.append(f"{added_chars} characters added")
        parts.append("Text changes: " + ", ".join(char_parts))
    if added_bytes or removed_bytes:
        byte_parts = []
        if removed_bytes:
            byte_parts.append(f"{removed_bytes} metadata bytes removed")
        if added_bytes:
            byte_parts.append(f"{added_bytes} metadata bytes added")
        parts.append("Metadata changes: " + ", ".join(byte_parts))
    if not parts:
        return "No changes detected"
    return "; ".join(parts)
