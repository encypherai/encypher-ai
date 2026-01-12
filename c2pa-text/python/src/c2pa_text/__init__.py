"""
C2PA Text Manifest Wrapper Reference Implementation.

This module implements the C2PA Text Embedding Standard, allowing binary data
(typically a C2PA JUMBF Manifest) to be embedded into valid UTF-8 strings using
invisible Unicode Variation Selectors.

Validation:
    Use validate_manifest() to check manifest structure before embedding.
    This helps catch issues early and provides detailed diagnostics.
"""

import re
import struct
import unicodedata
from typing import Optional, Tuple

# Import validation utilities
from .validator import (
    ValidationCode,
    ValidationIssue,
    ValidationResult,
    validate_jumbf_structure,
    validate_manifest,
    validate_wrapper_bytes,
)

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


def _byte_offset_to_char_index(value: str, byte_offset: int) -> int:
    if byte_offset <= 0:
        return 0
    consumed = 0
    for idx, ch in enumerate(value):
        ch_len = len(ch.encode("utf-8"))
        if consumed + ch_len > byte_offset:
            return idx
        consumed += ch_len
    return len(value)


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


def find_wrapper_info(text: str) -> Optional[Tuple[bytes, int, int]]:
    """
    Locate and decode the C2PA wrapper in the text.

    Args:
        text: The text to search.

    Returns:
        Tuple(manifest_bytes, start_index, end_index) or None if not found/valid.
        start_index and end_index allow extracting or excluding the wrapper.
    """
    # Search for first wrapper
    m = _WRAPPER_RE.search(text)
    if not m:
        return None

    # Ensure there is no second wrapper occurrence (spec requirement)
    second = _WRAPPER_RE.search(text, pos=m.end())
    if second:
        raise ValueError("Multiple C2PA text wrappers detected – must embed exactly one per asset")

    seq = m.group(1)
    try:
        raw = decode_wrapper_sequence(seq)
    except ValueError:
        # Invalid VS sequence
        return None

    if len(raw) < _HEADER_SIZE:
        # Too short
        return None

    magic, version, length = _HEADER_STRUCT.unpack(raw[:_HEADER_SIZE])

    if magic != MAGIC:
        # Wrong magic
        return None

    if version != VERSION:
        # Unsupported version
        return None

    if len(raw) < _HEADER_SIZE + length:
        # Truncated
        return None

    manifest_bytes = raw[_HEADER_SIZE : _HEADER_SIZE + length]
    wrapper_start_byte = len(text[: m.start()].encode("utf-8"))
    wrapper_length_byte = len(text[m.start() : m.end()].encode("utf-8"))
    return manifest_bytes, wrapper_start_byte, wrapper_length_byte


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
    info = find_wrapper_info(text)
    if not info:
        return None, unicodedata.normalize("NFC", text)

    manifest_bytes, wrapper_start_byte, wrapper_length_byte = info
    wrapper_end_byte = wrapper_start_byte + wrapper_length_byte
    start_char = _byte_offset_to_char_index(text, wrapper_start_byte)
    end_char = _byte_offset_to_char_index(text, wrapper_end_byte)
    clean_text = text[:start_char] + text[end_char:]

    return manifest_bytes, unicodedata.normalize("NFC", clean_text)


__all__ = [
    # Core embedding functions
    "embed_manifest",
    "extract_manifest",
    "find_wrapper_info",
    "encode_wrapper",
    "decode_wrapper_sequence",
    # Validation
    "validate_manifest",
    "validate_jumbf_structure",
    "validate_wrapper_bytes",
    "ValidationCode",
    "ValidationIssue",
    "ValidationResult",
    # Constants
    "MAGIC",
    "VERSION",
    "ZWNBSP",
]
