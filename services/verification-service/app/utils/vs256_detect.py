# TEAM_158: Lightweight VS256 embedding detection and UUID extraction.
#
# This module detects VS256 (base-256 variation selector) embeddings in text
# and extracts the embedded UUIDs without requiring the HMAC signing key.
#
# Supports two formats (same magic prefix, same 36-char length):
# - vs256_embedding:    4 magic + 16 UUID + 16 HMAC = 36 chars
# - vs256_rs_embedding: 4 magic + 16 UUID + 8 HMAC-64 + 8 RS parity = 36 chars
#
# Both formats use the same detection logic; RS decode is attempted first
# for error recovery, falling back to raw byte extraction.
"""Detect and extract UUIDs from VS256 (variation selector) embeddings."""

from __future__ import annotations

from typing import List, Optional, Tuple
from uuid import UUID

# VS256 alphabet ranges
VS_BMP_START = 0xFE00    # VS1
VS_BMP_END = 0xFE0F      # VS16
VS_SUPP_START = 0xE0100  # VS17
VS_SUPP_END = 0xE01EF    # VS256

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
SIGNATURE_CHARS = 36  # 4 prefix + 32 payload

# RS constants (must match vs256_rs_crypto)
_RS_NSYM = 8
_RS_DATA_BYTES = 24  # 16 UUID + 8 HMAC-64


def find_vs256_signatures(text: str) -> List[Tuple[int, int, str]]:
    """Find all VS256 signatures (magic prefix + 32 VS payload) in *text*.

    Returns list of ``(start, end, signature_string)`` tuples.
    """
    signatures: List[Tuple[int, int, str]] = []
    i = 0
    text_len = len(text)

    while i <= text_len - SIGNATURE_CHARS:
        if text[i] == MAGIC_PREFIX[0]:
            if text[i : i + MAGIC_PREFIX_LEN] == MAGIC_PREFIX:
                candidate = text[i : i + SIGNATURE_CHARS]
                if len(candidate) == SIGNATURE_CHARS and all(
                    ch in _VS_CHAR_SET for ch in candidate[MAGIC_PREFIX_LEN:]
                ):
                    signatures.append((i, i + SIGNATURE_CHARS, candidate))
                    i += SIGNATURE_CHARS
                    continue
        i += 1

    return signatures


def extract_uuid_from_vs256_signature(sig: str) -> Optional[UUID]:
    """Extract the UUID from a 36-char VS256 signature.

    Attempts RS decode first (handles vs256_rs_embedding with error
    correction). Falls back to raw byte extraction (vs256_embedding).
    Returns ``None`` if the signature is malformed.
    """
    if len(sig) != SIGNATURE_CHARS:
        return None

    try:
        payload_chars = sig[MAGIC_PREFIX_LEN:]
        payload_bytes = bytes(_VS_TO_BYTE[ch] for ch in payload_chars)
    except (KeyError, Exception):
        return None

    # Try RS decode first (works for vs256_rs_embedding, harmless for plain)
    try:
        from reedsolo import RSCodec

        rs = RSCodec(_RS_NSYM)
        decoded = bytes(rs.decode(payload_bytes)[0])
        if len(decoded) == _RS_DATA_BYTES:
            return UUID(bytes=decoded[:16])
    except Exception:
        pass

    # Fallback: raw extraction (vs256_embedding — UUID at bytes 0-15)
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
    following 32 chars as the payload.

    Returns the 36-char signature string or None.
    """
    n = len(vs_chars)
    for i in range(n - SIGNATURE_CHARS + 1):
        candidate = "".join(vs_chars[i : i + SIGNATURE_CHARS])
        if candidate[:MAGIC_PREFIX_LEN] == MAGIC_PREFIX:
            return candidate
    return None
