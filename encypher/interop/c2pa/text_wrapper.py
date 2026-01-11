"""C2PA Text Manifest Wrapper utilities (moved from core)."""

from __future__ import annotations

import struct
import unicodedata
import warnings
from typing import cast

import c2pa_text

# ---------------------- Constants -------------------------------------------

MAGIC = c2pa_text.MAGIC
VERSION = c2pa_text.VERSION

_HEADER_STRUCT = struct.Struct("!8sBI")
_HEADER_SIZE = _HEADER_STRUCT.size


def _is_variation_selector(ch: str) -> bool:
    cp = ord(ch)
    if 0xFE00 <= cp <= 0xFE0F:
        return True
    return 0xE0100 <= cp <= 0xE01EF


def _find_valid_wrappers(normalized_text: str) -> list[tuple[bytes, int, int, int, int]]:
    wrappers: list[tuple[bytes, int, int, int, int]] = []
    i = 0
    while i < len(normalized_text):
        if normalized_text[i] != "\ufeff":
            i += 1
            continue

        j = i + 1
        while j < len(normalized_text) and _is_variation_selector(normalized_text[j]):
            j += 1

        if j <= i + 1:
            i += 1
            continue

        seq = normalized_text[i + 1 : j]
        try:
            raw = c2pa_text.decode_wrapper_sequence(seq)
        except ValueError:
            i = j
            continue

        if len(raw) < _HEADER_SIZE:
            i = j
            continue

        magic, version, length = _HEADER_STRUCT.unpack(raw[:_HEADER_SIZE])
        if magic != MAGIC or version != VERSION:
            i = j
            continue

        total = _HEADER_SIZE + length
        if len(raw) != total:
            i = j
            continue

        manifest_bytes = raw[_HEADER_SIZE:total]
        wrapper_start_byte = len(normalized_text[:i].encode("utf-8"))
        wrapper_length_byte = len(normalized_text[i:j].encode("utf-8"))
        wrappers.append((manifest_bytes, i, j, wrapper_start_byte, wrapper_length_byte))
        i = j

    return wrappers


def encode_wrapper(manifest_bytes: bytes) -> str:
    return cast(str, c2pa_text.encode_wrapper(manifest_bytes))


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


def find_wrapper_info_bytes(text: str) -> tuple[bytes, int, int] | None:
    """Return wrapper info using c2pa-text byte offsets.

    c2pa-text reports wrapper offsets as UTF-8 byte offsets (start byte + length).
    Downstream callers that need to verify hard-binding exclusions should use
    this function rather than importing c2pa_text directly.
    """

    normalized_text = _normalize(text)
    wrappers = _find_valid_wrappers(normalized_text)
    if not wrappers:
        return None
    if len(wrappers) > 1:
        warnings.warn(
            "Multiple C2PA text wrappers detected (multiple FEFF + C2PA magic blocks)",
            UserWarning,
            stacklevel=2,
        )
    manifest_bytes, _start_char, _end_char, start_byte, length_byte = wrappers[-1]
    return manifest_bytes, start_byte, length_byte


def find_and_decode(text: str) -> tuple[bytes | None, str, tuple[int, int] | None]:
    normalized_text = _normalize(text)
    wrappers = _find_valid_wrappers(normalized_text)
    if not wrappers:
        return None, normalized_text, None
    if len(wrappers) > 1:
        warnings.warn(
            "Multiple C2PA text wrappers detected (multiple FEFF + C2PA magic blocks)",
            UserWarning,
            stacklevel=2,
        )

    manifest_bytes, _selected_start_char, _selected_end_char, start_byte, length_byte = wrappers[-1]
    clean_text = normalized_text
    for _manifest_bytes, start_char, end_char, _start_byte, _length_byte in reversed(wrappers):
        clean_text = clean_text[:start_char] + clean_text[end_char:]
    return manifest_bytes, clean_text, (start_byte, length_byte)


def count_valid_wrappers(text: str) -> int:
    normalized_text = _normalize(text)
    return len(_find_valid_wrappers(normalized_text))
