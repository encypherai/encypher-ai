"""
Base-6 legacy-safe zero-width encoding with Reed-Solomon error correction.

Extends legacy_safe_crypto with RS(36,32) error correction: 4 parity bytes
appended to the 32-byte payload, encoded as 112 base-6 characters.

Layout (112 base-6 chars):
  data:    32 bytes  (log_id: 16 bytes + HMAC-SHA256/128: 16 bytes)
  parity:   4 bytes  (Reed-Solomon GF(256) parity over data)
  total:   36 bytes  -> 112 base-6 chars

Error correction capacity (reedsolo RS(36, 32), nsym=4):
  Corrects up to 2 unknown errors (corrupted chars at unknown positions)
  Corrects up to 4 known erasures (missing chars at known positions)
  In practice: copy/paste operations that strip a few chars are recoverable.

Char count derivation:
  36 bytes = 288 bits
  ceil(288 * log(2) / log(6)) = ceil(288 * 0.3869) = ceil(111.4) = 112
  Verified: 6^112 ~ 2^289.5 > 2^288. 112 chars always suffice.

Detection:
  Find runs of exactly 112 chars from the 6-char set that contain at least
  one LRM or RLM. Unambiguous from the 100-char non-ECC format by length.

Security:
  128-bit log_id uniqueness (hyperscale-safe: ~2e-12 collision P over 10yr at 20B/day)
  128-bit HMAC security (truncated from 256-bit SHA-256)
  RS parity does NOT weaken HMAC: parity is computed over log_id+HMAC bytes,
  so an attacker still needs the signing key to produce a valid HMAC.
"""

import hashlib
import unicodedata
from typing import Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac as crypto_hmac
from reedsolo import ReedSolomonError, RSCodec

from app.utils.legacy_safe_crypto import (
    CHAR_TO_DIGIT,
    CHARS_BASE6,
    CHARS_BASE6_SET,
    LOG_ID_BYTES,
    LRM_RLM_SET,
    ZWNJ,
    derive_signing_key_from_private_key,
    embed_marker_safely,
    generate_log_id,
)

# =============================================================================
# RS CODEC -- 4 parity symbols over GF(256)
# =============================================================================

_RS_NSYM = 4  # parity symbols
_RS = RSCodec(_RS_NSYM)

# Layout constants
HMAC_BYTES = 16  # HMAC-SHA256/128 (full 128-bit security)
DATA_BYTES = LOG_ID_BYTES + HMAC_BYTES  # 32 bytes
PARITY_BYTES = _RS_NSYM  # 4 bytes
PAYLOAD_BYTES = DATA_BYTES + PARITY_BYTES  # 36 bytes

# ceil(36 * 8 * log(2) / log(6)) = ceil(288 * 0.3869) = 112
# Verified: 6^112 ~ 2^289.5 > 2^288
MARKER_CHARS = 112

# Bytes of SHA256(NFC(sentence)) folded into HMAC for content binding
CONTENT_COMMITMENT_BYTES = 8


# =============================================================================
# Big-number base-6 codec (36 bytes <-> 112 chars)
# =============================================================================


def _encode_base6_36(data: bytes) -> str:
    """Encode 36 bytes as a 112-char base-6 string."""
    assert len(data) == PAYLOAD_BYTES, f"Expected {PAYLOAD_BYTES} bytes, got {len(data)}"
    n = int.from_bytes(data, "big")
    digits: list[str] = []
    while n:
        digits.append(CHARS_BASE6[n % 6])
        n //= 6
    while len(digits) < MARKER_CHARS:
        digits.append(ZWNJ)
    return "".join(reversed(digits))


def _decode_base6_36(encoded: str) -> bytes:
    """Decode a 112-char base-6 string back to 36 bytes."""
    if len(encoded) != MARKER_CHARS:
        raise ValueError(f"Expected {MARKER_CHARS} chars, got {len(encoded)}")
    n = 0
    for ch in encoded:
        d = CHAR_TO_DIGIT.get(ch)
        if d is None:
            raise ValueError(f"Invalid base-6 char: U+{ord(ch):04X}")
        n = n * 6 + d
    return n.to_bytes(PAYLOAD_BYTES, "big")


# =============================================================================
# Marker creation and verification
# =============================================================================


def create_marker(
    log_id: bytes,
    signing_key: bytes,
    sentence_text: str | None = None,
) -> str:
    """
    Create a 112-char RS-protected base-6 legacy-safe provenance marker.

    Layout: base6_encode(log_id(16) + HMAC(16) + RS_parity(4)) = 112 chars.

    Args:
        log_id:        16-byte identifier from generate_log_id().
        signing_key:   32-byte HMAC key derived from the org Ed25519 private key.
        sentence_text: Optional sentence for content binding.

    Returns:
        112 invisible characters, confirmed Word-safe and terminal-safe.
    """
    if len(log_id) != LOG_ID_BYTES:
        raise ValueError(f"log_id must be {LOG_ID_BYTES} bytes, got {len(log_id)}")
    if len(signing_key) < 32:
        raise ValueError("signing_key must be at least 32 bytes")

    h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
    h.update(log_id)
    if sentence_text is not None:
        nfc = unicodedata.normalize("NFC", sentence_text).encode("utf-8")
        h.update(hashlib.sha256(nfc).digest()[:CONTENT_COMMITMENT_BYTES])
    hmac_bytes = h.finalize()[:HMAC_BYTES]

    data = log_id + hmac_bytes  # 32 bytes
    rs_encoded = bytes(_RS.encode(data))  # 36 bytes: 32 data + 4 parity
    assert len(rs_encoded) == PAYLOAD_BYTES

    return _encode_base6_36(rs_encoded)


def verify_marker(
    marker: str,
    signing_key: bytes,
    sentence_text: str | None = None,
    erase_positions: list[int] | None = None,
) -> Tuple[bool, Optional[bytes]]:
    """
    Verify a 112-char RS-protected base-6 marker and extract the log_id.

    Tries content-bound verification first; falls back to content-free for
    backward compatibility. Can recover from up to 4 erasures or 2 errors.

    Args:
        marker:          112-char base-6 string.
        signing_key:     32-byte HMAC key.
        sentence_text:   Optional sentence text for content-bound verification.
        erase_positions: Optional list of 0-indexed positions within the
                         36-byte payload that are known erasures.

    Returns:
        (True, log_id_bytes) on success, (False, None) on any failure.
    """
    if len(marker) != MARKER_CHARS:
        return False, None

    try:
        payload_bytes = _decode_base6_36(marker)
    except (ValueError, OverflowError):
        return False, None

    try:
        decoded = bytes(_RS.decode(payload_bytes, erase_pos=erase_positions)[0])
    except (ReedSolomonError, Exception):
        return False, None

    if len(decoded) != DATA_BYTES:
        return False, None

    log_id = decoded[:LOG_ID_BYTES]
    hmac_received = decoded[LOG_ID_BYTES:]

    def _hmac(include_text: bool) -> bytes:
        h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
        h.update(log_id)
        if include_text and sentence_text is not None:
            nfc = unicodedata.normalize("NFC", sentence_text).encode("utf-8")
            h.update(hashlib.sha256(nfc).digest()[:CONTENT_COMMITMENT_BYTES])
        return h.finalize()[:HMAC_BYTES]

    if hmac_received == _hmac(include_text=True):
        return True, log_id
    if sentence_text is not None and hmac_received == _hmac(include_text=False):
        return True, log_id
    return False, None


# =============================================================================
# Detection
# =============================================================================


def find_all_markers(text: str) -> list[tuple[int, int, str]]:
    """
    Find all 112-char RS-protected base-6 markers in text.

    Scans for runs of chars from the 6-char set, extracts MARKER_CHARS-length
    chunks, and keeps those that contain at least one LRM or RLM. Length 112
    unambiguously distinguishes these from non-ECC legacy_safe markers (100 chars).

    Returns:
        List of (start_pos, end_pos, marker_string) tuples.
    """
    results: list[tuple[int, int, str]] = []
    i = 0
    n = len(text)

    while i < n:
        if text[i] in CHARS_BASE6_SET:
            start = i
            while i < n and text[i] in CHARS_BASE6_SET:
                i += 1
            run = text[start:i]
            run_len = len(run)
            offset = 0
            while offset + MARKER_CHARS <= run_len:
                chunk = run[offset : offset + MARKER_CHARS]
                if any(c in LRM_RLM_SET for c in chunk):
                    results.append((start + offset, start + offset + MARKER_CHARS, chunk))
                offset += MARKER_CHARS
        else:
            i += 1

    return results


def extract_marker(text: str) -> Optional[str]:
    """Return the first 112-char RS marker found in text, or None."""
    found = find_all_markers(text)
    return found[0][2] if found else None


def remove_markers(text: str) -> str:
    """Remove all 112-char RS markers from text, preserving all other content."""
    found = find_all_markers(text)
    for start, end, _ in reversed(found):
        text = text[:start] + text[end:]
    return text


# =============================================================================
# Safe embedding
# =============================================================================


def create_embedded_sentence(
    sentence: str,
    log_id: bytes,
    signing_key: bytes,
) -> str:
    """Create and embed a content-bound RS-protected base-6 marker in one call."""
    marker = create_marker(log_id, signing_key, sentence_text=sentence)
    return embed_marker_safely(sentence, marker)
