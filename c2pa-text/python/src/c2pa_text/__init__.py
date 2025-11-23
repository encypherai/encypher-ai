"""
C2PA Text Manifest Wrapper Reference Implementation.

This module implements the C2PA Text Embedding Standard, allowing binary data
(typically a C2PA JUMBF Manifest) to be embedded into valid UTF-8 strings using
invisible Unicode Variation Selectors.
"""

import re
import struct
import unicodedata
from typing import Optional, Tuple

# ---------------------- Constants -------------------------------------------

MAGIC = b"C2PATXT\0"  # 8-byte magic sequence (0x4332504154585400)
VERSION = 1  # Current wrapper version
_HEADER_STRUCT = struct.Struct("!8sBI")  # Big-endian: Magic(8), Version(1), Length(4)
_HEADER_SIZE = _HEADER_STRUCT.size

ZWNBSP = "\ufeff"  # Zero-Width No-Break Space (Prefix)
_VS_CHAR_CLASS = "[\ufe00-\ufe0f\U000e0100-\U000e01ef]"
_WRAPPER_RE = re.compile(ZWNBSP + f"({_VS_CHAR_CLASS}{{{_HEADER_SIZE},}})")


def _byte_to_vs(byte: int) -> str:
    """Convert a single byte (0-255) to a Unicode Variation Selector."""
    if 0 <= byte <= 15:
        return chr(0xFE00 + byte)
    elif 16 <= byte <= 255:
        return chr(0xE0100 + (byte - 16))
    raise ValueError("Byte out of range 0-255")


def _vs_to_byte(codepoint: int) -> Optional[int]:
    """Convert a Unicode Variation Selector codepoint back to a byte."""
    if 0xFE00 <= codepoint <= 0xFE0F:
        return codepoint - 0xFE00
    if 0xE0100 <= codepoint <= 0xE01EF:
        return (codepoint - 0xE0100) + 16
    return None


def encode_wrapper(manifest_bytes: bytes) -> str:
    """
    Encode raw bytes into a C2PA Text Manifest Wrapper string.

    Args:
        manifest_bytes: The binary data to embed (typically C2PA JUMBF).

    Returns:
        A string consisting of the ZWNBSP prefix and the encoded variation selectors.
    """
    header = _HEADER_STRUCT.pack(MAGIC, VERSION, len(manifest_bytes))
    payload = header + manifest_bytes
    vs = [_byte_to_vs(b) for b in payload]
    return ZWNBSP + "".join(vs)


def decode_wrapper_sequence(seq: str) -> bytes:
    """Decode a sequence of variation selector characters into bytes."""
    out = bytearray()
    for ch in seq:
        b = _vs_to_byte(ord(ch))
        if b is None:
            raise ValueError("Invalid variation selector in sequence")
        out.append(b)
    return bytes(out)


def embed_manifest(text: str, manifest_bytes: bytes) -> str:
    """
    Embed a C2PA manifest into text.

    Normalizes the text to NFC and appends the invisible wrapper to the end.

    Args:
        text: The host text.
        manifest_bytes: The binary manifest data.

    Returns:
        The NFC-normalized text with the wrapper appended.
    """
    normalized_text = unicodedata.normalize("NFC", text)
    wrapper = encode_wrapper(manifest_bytes)
    return normalized_text + wrapper


def extract_manifest(text: str) -> Tuple[Optional[bytes], str]:
    """
    Extract a C2PA manifest from text.

    Searches for the standard C2PA wrapper, decodes it, and returns the manifest
    and the clean text (NFC normalized).

    Args:
        text: The text containing the embedding.

    Returns:
        Tuple(manifest_bytes, clean_text).
        manifest_bytes is None if no valid wrapper is found.
    """
    # Search for first wrapper
    m = _WRAPPER_RE.search(text)
    if not m:
        return None, unicodedata.normalize("NFC", text)

    # Ensure there is no second wrapper occurrence (spec requirement)
    second = _WRAPPER_RE.search(text, pos=m.end())
    if second:
        raise ValueError("Multiple C2PA text wrappers detected – must embed exactly one per asset")

    seq = m.group(1)
    try:
        raw = decode_wrapper_sequence(seq)
    except ValueError:
        # Invalid VS sequence
        return None, unicodedata.normalize("NFC", text)

    if len(raw) < _HEADER_SIZE:
        # Too short
        return None, unicodedata.normalize("NFC", text)

    magic, version, length = _HEADER_STRUCT.unpack(raw[:_HEADER_SIZE])

    if magic != MAGIC:
        # Wrong magic
        return None, unicodedata.normalize("NFC", text)

    if version != VERSION:
        # Unsupported version
        return None, unicodedata.normalize("NFC", text)

    if len(raw) < _HEADER_SIZE + length:
        # Truncated
        return None, unicodedata.normalize("NFC", text)

    manifest_bytes = raw[_HEADER_SIZE : _HEADER_SIZE + length]

    # Remove wrapper from text
    start, end = m.span()
    clean_text = text[:start] + text[end:]

    return manifest_bytes, unicodedata.normalize("NFC", clean_text)
