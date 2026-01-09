"""C2PA Text Manifest Wrapper utilities (moved from core)."""

from __future__ import annotations

import unicodedata

import c2pa_text

# ---------------------- Constants -------------------------------------------

MAGIC = c2pa_text.MAGIC
VERSION = c2pa_text.VERSION


def encode_wrapper(manifest_bytes: bytes) -> str:
    return c2pa_text.encode_wrapper(manifest_bytes)


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


def extract_from_text(text: str) -> tuple[bytes | None, str, tuple[int, int] | None]:
    """Extract wrapper from text.

    Returns ``(manifest_bytes, clean_text, span)`` where ``clean_text`` is NFC
    normalised text with the wrapper removed. If no wrapper is present the
    function returns ``(None, normalised_text, None)``.
    """

    return find_and_decode(text)


def _normalize(text: str) -> str:
    """Return NFC-normalized *text* as required by C2PA spec."""
    return unicodedata.normalize("NFC", text)


def _byte_offset_to_char_index(value: str, byte_offset: int) -> int:
    """Convert a UTF-8 byte offset into a Python string character index."""
    if byte_offset <= 0:
        return 0
    consumed = 0
    for idx, ch in enumerate(value):
        ch_len = len(ch.encode("utf-8"))
        if consumed + ch_len > byte_offset:
            return idx
        consumed += ch_len
    return len(value)


def find_wrapper_info_bytes(text: str) -> tuple[bytes, int, int] | None:
    """Return wrapper info using c2pa-text byte offsets.

    c2pa-text reports wrapper offsets as UTF-8 byte offsets (start byte + length).
    Downstream callers that need to verify hard-binding exclusions should use
    this function rather than importing c2pa_text directly.
    """

    normalized_text = _normalize(text)
    if hasattr(c2pa_text, "find_wrapper_info"):
        info = c2pa_text.find_wrapper_info(normalized_text)
        if info:
            manifest_bytes, wrapper_start_byte, wrapper_length_byte = info
            return manifest_bytes, wrapper_start_byte, wrapper_length_byte
    return None


def find_and_decode(text: str) -> tuple[bytes | None, str, tuple[int, int] | None]:
    normalized_text = _normalize(text)
    if hasattr(c2pa_text, "find_wrapper_info"):
        info = c2pa_text.find_wrapper_info(normalized_text)
        if info:
            manifest_bytes, wrapper_start_byte, wrapper_length_byte = info
            wrapper_end_byte = wrapper_start_byte + wrapper_length_byte

            start_char = _byte_offset_to_char_index(normalized_text, wrapper_start_byte)
            end_char = _byte_offset_to_char_index(normalized_text, wrapper_end_byte)

            clean_text = normalized_text[:start_char] + normalized_text[end_char:]
            return manifest_bytes, clean_text, (start_char, end_char)

    return None, normalized_text, None

