"""
Base-6 legacy-safe zero-width encoding.

Six confirmed Word-safe and terminal-safe invisible characters (empirically
tested, no visual artifacts in desktop Microsoft Word or standard terminals):

  ZWNJ  U+200C  = 0   Zero-Width Non-Joiner     (original)
  ZWJ   U+200D  = 1   Zero-Width Joiner          (original)
  CGJ   U+034F  = 2   Combining Grapheme Joiner  (original)
  MVS   U+180E  = 3   Mongolian Vowel Separator  (original)
  LRM   U+200E  = 4   Left-to-Right Mark         (new, March 2026)
  RLM   U+200F  = 5   Right-to-Left Mark         (new, March 2026)

Encoding strategy: big-number base-6
  Treat the full 32-byte payload as one 256-bit integer, encode in base-6.
  Byte-by-byte base-6 is inefficient (6^3=216 < 256, requires 4 chars/byte =
  same as base-4). Big-number encoding achieves ~99.5% Shannon efficiency.

Payload format: 32 bytes -> 100 chars  (vs base-4: 32 bytes -> 128 chars)
  log_id   16 bytes   random identifier referencing the transparency log entry
  HMAC     16 bytes   HMAC-SHA256 truncated to 128 bits

  log_id is 128-bit random (os.urandom(16)), chosen to handle global AI
  ecosystem scale: birthday collision probability is ~2e-12 over 10 years at
  20B messages/day across all providers. Not sequential -- avoids disclosing
  signing volume.

Detection:
  Find runs of exactly 100 chars from the 6-char set that contain at least one
  LRM or RLM. Base-4 markers use 128 chars and never contain LRM/RLM -- the
  lengths and alphabets are distinct, so there is no ambiguity.
  Probability of a base-4 run of 100 chars having LRM/RLM is (4/6)^100 ~ 2e-18.

Size comparison (per sentence):
  base-4 legacy       32 bytes payload   128 chars
  base-6 legacy_safe  32 bytes payload   100 chars   (-22%)
"""

import hashlib
import os
import unicodedata
from typing import Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac as crypto_hmac
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# ---------------------------------------------------------------------------
# Alphabet
# ---------------------------------------------------------------------------

ZWNJ = "\u200c"  # 0
ZWJ = "\u200d"  # 1
CGJ = "\u034f"  # 2
MVS = "\u180e"  # 3
LRM = "\u200e"  # 4  -- confirmed Word-safe, no visual artifact
RLM = "\u200f"  # 5  -- confirmed Word-safe, no visual artifact

CHARS_BASE6: list[str] = [ZWNJ, ZWJ, CGJ, MVS, LRM, RLM]
CHAR_TO_DIGIT: dict[str, int] = {c: i for i, c in enumerate(CHARS_BASE6)}
CHARS_BASE6_SET: frozenset = frozenset(CHARS_BASE6)

# LRM/RLM are absent from the base-4 alphabet, making them reliable markers
# that a 100-char run is base-6 rather than a stray base-4 fragment.
LRM_RLM_SET: frozenset = frozenset({LRM, RLM})


# ---------------------------------------------------------------------------
# Payload layout
# ---------------------------------------------------------------------------

LOG_ID_BYTES = 16  # 128-bit random log reference (hyperscale-safe)
HMAC_BYTES = 16  # 128-bit HMAC-SHA256
PAYLOAD_BYTES = LOG_ID_BYTES + HMAC_BYTES  # 32 bytes

# ceil(256 * log(2) / log(6)) = ceil(99.03) = 100
# Verified: 6^100 > 2^256 (6^100 ~ 6.5e77 > 2^256 ~ 1.16e77)
MARKER_CHARS = 100

# Bytes of SHA256(NFC(sentence)) folded into HMAC for content binding
CONTENT_COMMITMENT_BYTES = 8


# ---------------------------------------------------------------------------
# Big-number base-6 codec
# ---------------------------------------------------------------------------


def _encode_base6(data: bytes) -> str:
    """
    Encode bytes as a MARKER_CHARS-length base-6 string.

    Treats the payload as one large big-endian integer.  Leading "zero" digits
    are encoded as ZWNJ (digit 0) to maintain fixed length.
    """
    n = int.from_bytes(data, "big")
    digits: list[str] = []
    while n:
        digits.append(CHARS_BASE6[n % 6])
        n //= 6
    while len(digits) < MARKER_CHARS:
        digits.append(ZWNJ)
    return "".join(reversed(digits))


def _decode_base6(encoded: str) -> bytes:
    """Decode a MARKER_CHARS-length base-6 string back to PAYLOAD_BYTES bytes."""
    n = 0
    for ch in encoded:
        d = CHAR_TO_DIGIT.get(ch)
        if d is None:
            raise ValueError(f"Invalid base-6 char: U+{ord(ch):04X}")
        n = n * 6 + d
    return n.to_bytes(PAYLOAD_BYTES, "big")


# ---------------------------------------------------------------------------
# Marker creation and verification
# ---------------------------------------------------------------------------


def generate_log_id() -> bytes:
    """
    Generate a random 16-byte log ID.

    Random rather than sequential to avoid disclosing signing volume via
    enumeration.  2^128 space; birthday collision probability is ~2e-12 over
    10 years at 20B messages/day across the global AI ecosystem -- safe at
    any realistic deployment scale indefinitely.
    """
    return os.urandom(LOG_ID_BYTES)


def create_marker(
    log_id: bytes,
    signing_key: bytes,
    sentence_text: str | None = None,
) -> str:
    """
    Create a 100-char base-6 legacy-safe provenance marker.

    Args:
        log_id:        16-byte identifier returned by generate_log_id().
        signing_key:   32-byte HMAC key derived from the org Ed25519 private key.
        sentence_text: Optional sentence for content binding.  When provided,
                       SHA256(NFC(text))[:8] is folded into the HMAC input,
                       tying the marker to this exact sentence content.

    Returns:
        100 invisible characters, confirmed Word-safe and terminal-safe.
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

    payload = log_id + hmac_bytes  # 32 bytes
    return _encode_base6(payload)


def verify_marker(
    marker: str,
    signing_key: bytes,
    sentence_text: str | None = None,
) -> Tuple[bool, Optional[bytes]]:
    """
    Verify a 100-char base-6 marker and extract the log_id.

    Tries content-bound verification first; falls back to content-free
    verification for backward compatibility with markers created without
    sentence_text.

    Returns:
        (True, log_id_bytes) on success, (False, None) on any failure.
    """
    if len(marker) != MARKER_CHARS:
        return False, None

    try:
        payload = _decode_base6(marker)
    except (ValueError, OverflowError):
        return False, None

    log_id = payload[:LOG_ID_BYTES]
    hmac_received = payload[LOG_ID_BYTES:]

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


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def find_all_markers(text: str) -> list[tuple[int, int, str]]:
    """
    Find all base-6 markers in text.

    Scans for runs of chars from the 6-char set, extracts MARKER_CHARS-length
    chunks, and keeps those that contain at least one LRM or RLM (distinguishing
    them from any accidental base-4 content of the same length).

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
    """Return the first base-6 marker found in text, or None."""
    found = find_all_markers(text)
    return found[0][2] if found else None


def remove_markers(text: str) -> str:
    """Remove all base-6 markers from text, preserving all other content."""
    found = find_all_markers(text)
    for start, end, _ in reversed(found):
        text = text[:start] + text[end:]
    return text


# ---------------------------------------------------------------------------
# Safe embedding
# ---------------------------------------------------------------------------

TRAILING_PUNCTUATION = ".!?\"')]}»\u201d"


def embed_marker_safely(text: str, marker: str) -> str:
    """
    Embed marker before terminal punctuation to reduce accidental deletion.
    """
    if not text:
        return marker
    trailing = 0
    for ch in reversed(text):
        if ch in TRAILING_PUNCTUATION:
            trailing += 1
        else:
            break
    pos = len(text) - trailing
    return text[:pos] + marker + text[pos:]


def create_embedded_sentence(
    sentence: str,
    log_id: bytes,
    signing_key: bytes,
) -> str:
    """Create and embed a content-bound base-6 marker in one call."""
    marker = create_marker(log_id, signing_key, sentence_text=sentence)
    return embed_marker_safely(sentence, marker)


# ---------------------------------------------------------------------------
# Key derivation
# ---------------------------------------------------------------------------


def derive_signing_key_from_private_key(private_key: Ed25519PrivateKey) -> bytes:
    """Derive a 32-byte HMAC signing key from an Ed25519 private key."""
    return hashlib.sha256(b"encypher-hmac-key:" + private_key.private_bytes_raw()).digest()
