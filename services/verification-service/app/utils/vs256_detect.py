# TEAM_158: Lightweight VS256 embedding detection and UUID extraction.
#
# This module detects VS256 (base-256 variation selector) embeddings in text
# and extracts the embedded UUIDs without requiring the HMAC signing key.
#
# Supports three formats (same magic prefix, different lengths):
# - vs256_embedding:        4 magic + 16 UUID + 16 HMAC       = 36 chars
# - vs256_rs_embedding:     4 magic + 16 UUID + 8 HMAC-64 + 8 RS parity = 36 chars
#   (legacy 36-char RS variant, RS(8) over 32 bytes -> 24 bytes data)
# - vs256_rs_ecc_embedding: 4 magic + 40 payload (RS(8) over 40 bytes -> 32 bytes data)
#   = 44 chars total (current ECC mode used by micro+ecc signing)
#
# Detection priority: check for 44-char ECC signature first (it has a longer
# payload), then fall back to 36-char.  Both share the same MAGIC_PREFIX.
"""Detect and extract log IDs from VS256 (variation selector) embeddings."""

from __future__ import annotations

from typing import List, Optional, Tuple
from uuid import UUID

# VS256 alphabet ranges
VS_BMP_START = 0xFE00  # VS1
VS_BMP_END = 0xFE0F  # VS16
VS_SUPP_START = 0xE0100  # VS17
VS_SUPP_END = 0xE01EF  # VS256

# Build lookup tables
_VS_TO_BYTE: dict[str, int] = {}
for _i in range(16):
    _VS_TO_BYTE[chr(VS_BMP_START + _i)] = _i
for _i in range(240):
    _VS_TO_BYTE[chr(VS_SUPP_START + _i)] = _i + 16

_VS_CHAR_SET = frozenset(_VS_TO_BYTE.keys())

# Magic prefix: VS240-VS243 (byte values 239-242)
_BYTE_TO_VS = [chr(VS_BMP_START + i) for i in range(16)] + [chr(VS_SUPP_START + i) for i in range(240)]
MAGIC_PREFIX = _BYTE_TO_VS[239] + _BYTE_TO_VS[240] + _BYTE_TO_VS[241] + _BYTE_TO_VS[242]
MAGIC_PREFIX_LEN = 4

# Signature lengths
SIGNATURE_CHARS = 36  # Legacy: 4 prefix + 32 payload
ECC_SIGNATURE_CHARS = 44  # Current ECC: 4 prefix + 40 payload (RS-protected)

# RS constants for legacy 36-char format: RS(8) over 32 bytes -> 24 bytes data
_RS_NSYM = 8
_RS_DATA_BYTES = 24  # 16 log_id + 8 HMAC-64

# RS constants for 44-char ECC format: RS(8) over 40 bytes -> 32 bytes data
_ECC_RS_NSYM = 8
_ECC_RS_DATA_BYTES = 32  # 16 log_id + 16 HMAC-128


def find_vs256_signatures(text: str) -> List[Tuple[int, int, str]]:
    """Find all VS256 signatures in *text* (36-char and 44-char ECC formats).

    For each magic-prefix match, tries to claim the longer 44-char ECC format
    first; falls back to 36-char.

    Returns list of ``(start, end, signature_string)`` tuples.
    """
    signatures: List[Tuple[int, int, str]] = []
    i = 0
    text_len = len(text)

    while i < text_len:
        if text[i] != MAGIC_PREFIX[0]:
            i += 1
            continue
        if text[i : i + MAGIC_PREFIX_LEN] != MAGIC_PREFIX:
            i += 1
            continue

        # Try 44-char ECC format first (larger payload)
        if i + ECC_SIGNATURE_CHARS <= text_len:
            candidate = text[i : i + ECC_SIGNATURE_CHARS]
            if all(ch in _VS_CHAR_SET for ch in candidate[MAGIC_PREFIX_LEN:]):
                signatures.append((i, i + ECC_SIGNATURE_CHARS, candidate))
                i += ECC_SIGNATURE_CHARS
                continue

        # Try 36-char legacy format
        if i + SIGNATURE_CHARS <= text_len:
            candidate = text[i : i + SIGNATURE_CHARS]
            if all(ch in _VS_CHAR_SET for ch in candidate[MAGIC_PREFIX_LEN:]):
                signatures.append((i, i + SIGNATURE_CHARS, candidate))
                i += SIGNATURE_CHARS
                continue

        i += 1

    return signatures


def extract_uuid_from_vs256_signature(sig: str) -> Optional[UUID]:
    """Extract the log ID (as UUID) from a VS256 signature (36 or 44 chars).

    For 44-char ECC signatures: RS decode 40-byte payload -> 32 bytes; first
    16 bytes are the log_id.

    For 36-char signatures: RS decode 32-byte payload -> 24 bytes OR raw
    extraction; first 16 bytes are the log_id.

    Returns ``None`` if the signature is malformed or unsupported.
    """
    sig_len = len(sig)
    if sig_len not in (SIGNATURE_CHARS, ECC_SIGNATURE_CHARS):
        return None
    if sig[:MAGIC_PREFIX_LEN] != MAGIC_PREFIX:
        return None

    try:
        payload_chars = sig[MAGIC_PREFIX_LEN:]
        payload_bytes = bytes(_VS_TO_BYTE[ch] for ch in payload_chars)
    except (KeyError, Exception):
        return None

    if sig_len == ECC_SIGNATURE_CHARS:
        # 44-char ECC: RS(8) over 40 bytes -> 32 bytes; log_id = first 16
        try:
            from reedsolo import RSCodec

            rs = RSCodec(_ECC_RS_NSYM)
            decoded = bytes(rs.decode(payload_bytes)[0])
            if len(decoded) == _ECC_RS_DATA_BYTES:
                return UUID(bytes=decoded[:16])
        except Exception:
            pass
        # Fallback: raw extraction (no ECC correction)
        try:
            return UUID(bytes=payload_bytes[:16])
        except Exception:
            return None

    # 36-char legacy format
    try:
        from reedsolo import RSCodec

        rs = RSCodec(_RS_NSYM)
        decoded = bytes(rs.decode(payload_bytes)[0])
        if len(decoded) == _RS_DATA_BYTES:
            return UUID(bytes=decoded[:16])
    except Exception:
        pass

    # Fallback: raw extraction (vs256_embedding - log_id at bytes 0-15)
    try:
        return UUID(bytes=payload_bytes[:16])
    except Exception:
        return None


def collect_distributed_vs_chars(text: str) -> List[str]:
    """Collect all VS chars from text in reading order.

    After redistribution, VS chars are scattered across visible text
    (1 per base glyph). This function collects them in order for
    signature reassembly.
    """
    return [ch for ch in text if ch in _VS_CHAR_SET]


def reassemble_signature_from_distributed(
    vs_chars: List[str],
) -> Optional[str]:
    """Attempt to reassemble a VS256 signature from distributed VS chars.

    Scans the collected VS chars for the magic prefix and extracts the
    following payload chars.  Tries the longer ECC format (44 chars) first
    so that ECC signatures are not accidentally truncated to 36.

    Returns the signature string (36 or 44 chars) or None.
    """
    n = len(vs_chars)

    # Try 44-char ECC format first
    for i in range(n - ECC_SIGNATURE_CHARS + 1):
        candidate = "".join(vs_chars[i : i + ECC_SIGNATURE_CHARS])
        if candidate[:MAGIC_PREFIX_LEN] == MAGIC_PREFIX:
            return candidate

    # Fall back to 36-char legacy format
    for i in range(n - SIGNATURE_CHARS + 1):
        candidate = "".join(vs_chars[i : i + SIGNATURE_CHARS])
        if candidate[:MAGIC_PREFIX_LEN] == MAGIC_PREFIX:
            return candidate

    return None
