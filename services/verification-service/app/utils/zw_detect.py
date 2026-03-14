# TEAM_156: Lightweight ZW embedding detection and UUID extraction.
#
# This module detects zero-width (ZW) embeddings in text and extracts
# the embedded UUIDs without requiring the HMAC signing key.
# ZW format: 128 contiguous base-4 chars = 32 bytes (16 UUID + 16 HMAC).
"""Detect and extract UUIDs from ZW (zero-width) embeddings."""

from __future__ import annotations

from typing import List, Optional, Tuple
from uuid import UUID

# Word-safe invisible characters used by ZW base-4 encoding
ZWNJ = "\u200c"  # 0
ZWJ = "\u200d"  # 1
CGJ = "\u034f"  # 2
MVS = "\u180e"  # 3

_CHARS_BASE4_SET = frozenset({ZWNJ, ZWJ, CGJ, MVS})
_CHAR_TO_DIGIT = {ZWNJ: 0, ZWJ: 1, CGJ: 2, MVS: 3}

_SIG_LEN = 128  # 32 bytes × 4 chars/byte
_UUID_CHARS = 64  # 16 bytes × 4 chars/byte


def find_zw_signatures(text: str) -> List[Tuple[int, int, str]]:
    """Find all 128-char contiguous base-4 sequences in *text*.

    Returns list of ``(start, end, signature_string)`` tuples.
    """
    signatures: List[Tuple[int, int, str]] = []
    i = 0
    n = len(text)

    while i < n:
        if text[i] in _CHARS_BASE4_SET:
            start = i
            while i < n and text[i] in _CHARS_BASE4_SET:
                i += 1
            length = i - start
            pos = start
            while length >= _SIG_LEN:
                sig = text[pos : pos + _SIG_LEN]
                signatures.append((pos, pos + _SIG_LEN, sig))
                pos += _SIG_LEN
                length -= _SIG_LEN
        else:
            i += 1

    return signatures


def _decode_byte(encoded: str) -> int:
    """Decode 4 base-4 chars into a single byte."""
    value = 0
    multiplier = 1
    for ch in encoded:
        value += _CHAR_TO_DIGIT[ch] * multiplier
        multiplier *= 4
    return value


def extract_uuid_from_signature(sig: str) -> Optional[UUID]:
    """Extract the UUID from a 128-char ZW signature (first 64 chars).

    Returns ``None`` if the signature is malformed.
    """
    if len(sig) != _SIG_LEN:
        return None
    try:
        uuid_bytes = bytes(_decode_byte(sig[i : i + 4]) for i in range(0, _UUID_CHARS, 4))
        return UUID(bytes=uuid_bytes)
    except Exception:
        return None
