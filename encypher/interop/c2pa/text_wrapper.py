"""C2PA Text Manifest Wrapper utilities (moved from core)."""

from __future__ import annotations

import re
import struct
import unicodedata
from typing import Optional, Tuple

# ---------------------- Constants -------------------------------------------

MAGIC = b"C2PATXT\0"  # 8-byte magic sequence
VERSION = 1  # Current wrapper version we emit / accept
ALGORITHM_IDS = {
    "sha256": 1,
    "sha384": 2,
    "sha512": 3,
    "sha3-256": 4,
    "sha3-384": 5,
    "sha3-512": 6,
}

ZWNBSP = "\ufeff"
_VS_CHAR_CLASS = "[\ufe00-\ufe0f\U000e0100-\U000e01ef]"
_WRAPPER_RE = re.compile(ZWNBSP + f"({_VS_CHAR_CLASS}{{15,}})")


def _byte_to_vs(byte: int) -> str:
    if 0 <= byte <= 15:
        return chr(0xFE00 + byte)
    elif 16 <= byte <= 255:
        return chr(0xE0100 + (byte - 16))
    raise ValueError("byte out of range 0-255")


def _vs_to_byte(codepoint: int) -> Optional[int]:
    if 0xFE00 <= codepoint <= 0xFE0F:
        return codepoint - 0xFE00
    if 0xE0100 <= codepoint <= 0xE01EF:
        return (codepoint - 0xE0100) + 16
    return None


def encode_wrapper(manifest_bytes: bytes, alg: str = "sha256") -> str:
    if alg not in ALGORITHM_IDS:
        raise ValueError(f"Unsupported algorithm '{alg}'.")

    header = b"".join(
        [
            MAGIC,
            struct.pack("!B", VERSION),
            struct.pack("!H", ALGORITHM_IDS[alg]),
            struct.pack("!I", len(manifest_bytes)),
        ]
    )
    payload = header + manifest_bytes
    vs = [_byte_to_vs(b) for b in payload]
    return ZWNBSP + "".join(vs)


def _decode_vs_sequence(seq: str) -> bytes:
    out = bytearray()
    for ch in seq:
        b = _vs_to_byte(ord(ch))
        if b is None:
            raise ValueError("Invalid variation selector")
        out.append(b)
    return bytes(out)


def attach_wrapper_to_text(text: str, manifest_bytes: bytes, alg: str = "sha256", *, at_end: bool = True) -> str:
    """Return *text* with a wrapped manifest attached.

    If *at_end* is True (default) the wrapper is appended; otherwise it is
    prepended before the first line break.
    """
    wrapper = encode_wrapper(manifest_bytes, alg)
    return text + wrapper if at_end else wrapper + text


def extract_from_text(text: str) -> Tuple[Optional[bytes], Optional[str], str, Optional[Tuple[int, int]]]:
    """Extract wrapper from text.

    Returns (manifest_bytes, alg_name, clean_text, span) where *clean_text* is NFC normalised text with wrapper removed.
    If wrapper not found returns (None, None, normalised_text, None).
    """
    """Alias for find_and_decode for external callers."""
    return find_and_decode(text)


def _normalize(text: str) -> str:
    """Return NFC-normalized *text* as required by C2PA spec."""
    return unicodedata.normalize("NFC", text)


def find_and_decode(text: str) -> Tuple[Optional[bytes], Optional[str], str, Optional[Tuple[int, int]]]:
    # Search for first wrapper
    m = _WRAPPER_RE.search(text)
    if not m:
        return None, None, _normalize(text), None

    # Ensure there is no second wrapper occurrence (spec §4.2)
    second = _WRAPPER_RE.search(text, pos=m.end())
    if second:
        raise ValueError("Multiple C2PA text wrappers detected – must embed exactly one per asset")
    seq = m.group(1)
    try:
        raw = _decode_vs_sequence(seq)
    except ValueError:
        return None, None, _normalize(text), None
    if len(raw) < 15:
        return None, None, _normalize(text), None
    magic, version, alg_id, length = struct.unpack("!8sBHI", raw[:15])
    if magic != MAGIC or version != VERSION or len(raw) < 15 + length:
        raise ValueError("Invalid C2PA text wrapper header or length")
    # Map algorithm id
    alg_name = None
    for name, _id in ALGORITHM_IDS.items():
        if _id == alg_id:
            alg_name = name
            break
    if alg_name is None:
        raise ValueError(f"Unknown hash algorithm id {alg_id}")
    manifest_bytes = raw[15 : 15 + length]
    start, end = m.span()
    clean_text = _normalize(text[:start] + text[end:])
    return manifest_bytes, alg_name, clean_text, (start, end)
