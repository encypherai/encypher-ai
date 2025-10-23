"""C2PA Text Manifest Wrapper utilities (moved from core)."""

from __future__ import annotations

import re
import struct
import unicodedata
from typing import Optional, Tuple

# ---------------------- Constants -------------------------------------------

MAGIC = b"C2PATXT\0"  # 8-byte magic sequence
VERSION = 1  # Current wrapper version we emit / accept
_HEADER_STRUCT = struct.Struct("!8sBI")
_HEADER_SIZE = _HEADER_STRUCT.size

ZWNBSP = "\ufeff"
_VS_CHAR_CLASS = "[\ufe00-\ufe0f\U000e0100-\U000e01ef]"
_WRAPPER_RE = re.compile(ZWNBSP + f"({_VS_CHAR_CLASS}{{{_HEADER_SIZE},}})")


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


def encode_wrapper(manifest_bytes: bytes) -> str:
    header = _HEADER_STRUCT.pack(MAGIC, VERSION, len(manifest_bytes))
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
    # The ``alg`` parameter is retained for backwards compatibility with
    # earlier APIs that allowed selecting a hash algorithm, but the updated
    # wrapper format encodes only the manifest bytes.
    wrapper = encode_wrapper(manifest_bytes)
    return text + wrapper if at_end else wrapper + text


def extract_from_text(text: str) -> Tuple[Optional[bytes], str, Optional[Tuple[int, int]]]:
    """Extract wrapper from text.

    Returns ``(manifest_bytes, clean_text, span)`` where ``clean_text`` is NFC
    normalised text with the wrapper removed. If no wrapper is present the
    function returns ``(None, normalised_text, None)``.
    """

    return find_and_decode(text)


def _normalize(text: str) -> str:
    """Return NFC-normalized *text* as required by C2PA spec."""
    return unicodedata.normalize("NFC", text)


def find_and_decode(text: str) -> Tuple[Optional[bytes], str, Optional[Tuple[int, int]]]:
    # Search for first wrapper
    m = _WRAPPER_RE.search(text)
    if not m:
        return None, _normalize(text), None

    # Ensure there is no second wrapper occurrence (spec §4.2)
    second = _WRAPPER_RE.search(text, pos=m.end())
    if second:
        raise ValueError("Multiple C2PA text wrappers detected – must embed exactly one per asset")
    seq = m.group(1)
    try:
        raw = _decode_vs_sequence(seq)
    except ValueError:
        raise ValueError("Invalid variation selector sequence in wrapper")
    if len(raw) < _HEADER_SIZE:
        raise ValueError("C2PA text wrapper shorter than required header length")
    magic, version, length = _HEADER_STRUCT.unpack(raw[:_HEADER_SIZE])
    if magic != MAGIC or version != VERSION:
        raise ValueError("Invalid C2PA text wrapper header values")
    if len(raw) < _HEADER_SIZE + length:
        raise ValueError("C2PA text wrapper truncated before manifest bytes")
    manifest_bytes = raw[_HEADER_SIZE : _HEADER_SIZE + length]
    start, end = m.span()
    clean_text = _normalize(text[:start] + text[end:])
    return manifest_bytes, clean_text, (start, end)
