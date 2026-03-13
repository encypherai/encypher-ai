"""Detect and extract log_ids from legacy_safe (base-6 ZWC) embeddings.

Supports both encoding variants:
  - Non-ECC (100 chars): 32 bytes = log_id(16) + HMAC(16)
  - RS ECC  (112 chars): 36 bytes = log_id(16) + HMAC(16) + RS_parity(4)

The presence of LRM (U+200E) or RLM (U+200F) in a run unambiguously
distinguishes legacy_safe markers from base-4 ZW markers, which never
use those characters.

Log_id extraction does not require the HMAC signing key -- it reads the
first 16 bytes of the decoded payload, which is always the log_id.  The
caller then resolves the log_id hex against the content DB.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

# Six-character alphabet (same as legacy_safe_crypto.py)
ZWNJ = "\u200c"  # digit 0
ZWJ = "\u200d"  # digit 1
CGJ = "\u034f"  # digit 2
MVS = "\u180e"  # digit 3
LRM = "\u200e"  # digit 4
RLM = "\u200f"  # digit 5

_CHARS_BASE6_SET = frozenset({ZWNJ, ZWJ, CGJ, MVS, LRM, RLM})
_LRM_RLM_SET = frozenset({LRM, RLM})
_CHAR_TO_DIGIT = {ZWNJ: 0, ZWJ: 1, CGJ: 2, MVS: 3, LRM: 4, RLM: 5}

_MARKER_CHARS_PLAIN = 100  # non-ECC: 32 bytes
_MARKER_CHARS_RS = 112  # RS-ECC:  36 bytes

_DATA_BYTES_PLAIN = 32
_PAYLOAD_BYTES_RS = 36
_LOG_ID_BYTES = 16


def find_legacy_safe_markers(text: str) -> List[Tuple[int, int, str]]:
    """Find all legacy_safe markers (100-char or 112-char) in *text*.

    A valid marker is a contiguous run of base-6 chars whose length is
    exactly 100 or 112 AND contains at least one LRM or RLM character
    (which distinguishes it from base-4 ZW markers).

    Returns list of ``(start, end, marker_string)`` tuples.
    """
    results: List[Tuple[int, int, str]] = []
    i = 0
    n = len(text)

    while i < n:
        if text[i] in _CHARS_BASE6_SET:
            start = i
            while i < n and text[i] in _CHARS_BASE6_SET:
                i += 1
            run = text[start:i]
            run_len = len(run)
            # Extract non-overlapping marker-length chunks
            offset = 0
            while offset < run_len:
                for marker_len in (_MARKER_CHARS_RS, _MARKER_CHARS_PLAIN):
                    if offset + marker_len <= run_len:
                        chunk = run[offset : offset + marker_len]
                        if len(chunk) == marker_len and any(c in _LRM_RLM_SET for c in chunk):
                            results.append((start + offset, start + offset + marker_len, chunk))
                            offset += marker_len
                            break
                else:
                    # No valid marker length fits at this offset -- skip one char
                    offset += 1
        else:
            i += 1

    return results


def _decode_base6(encoded: str, expected_bytes: int) -> Optional[bytes]:
    """Decode a base-6 encoded string to bytes.

    Returns ``None`` if any character is outside the alphabet.
    """
    n = 0
    for ch in encoded:
        d = _CHAR_TO_DIGIT.get(ch)
        if d is None:
            return None
        n = n * 6 + d
    try:
        return n.to_bytes(expected_bytes, "big")
    except OverflowError:
        return None


def extract_log_id_from_marker(marker: str) -> Optional[str]:
    """Extract the log_id hex string from a legacy_safe marker.

    Works for both 100-char (plain) and 112-char (RS) markers.
    Does NOT verify the HMAC -- the caller resolves the log_id against
    the content DB to confirm authenticity.

    Returns a 32-hex-char string (16 bytes) or ``None`` on failure.
    """
    marker_len = len(marker)

    if marker_len == _MARKER_CHARS_PLAIN:
        raw = _decode_base6(marker, _DATA_BYTES_PLAIN)
        if raw is None:
            return None
        return raw[:_LOG_ID_BYTES].hex()

    if marker_len == _MARKER_CHARS_RS:
        raw = _decode_base6(marker, _PAYLOAD_BYTES_RS)
        if raw is None:
            return None
        # Try RS error correction; fall back to raw extraction if unavailable
        try:
            from reedsolo import RSCodec

            _RS = RSCodec(4)
            decoded = bytes(_RS.decode(raw)[0])
            return decoded[:_LOG_ID_BYTES].hex()
        except Exception:
            # RS decode failed or reedsolo unavailable -- read log_id directly
            return raw[:_LOG_ID_BYTES].hex()

    return None
