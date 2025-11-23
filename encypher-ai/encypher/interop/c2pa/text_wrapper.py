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


def find_and_decode(text: str) -> tuple[bytes | None, str, tuple[int, int] | None]:
    if hasattr(c2pa_text, "find_wrapper_info"):
        info = c2pa_text.find_wrapper_info(text)
        if info:
            manifest_bytes, start, end = info
            # Reconstruct clean text as per legacy behavior (NFC)
            clean_text = _normalize(text[:start] + text[end:])
            return manifest_bytes, clean_text, (start, end)

    return None, _normalize(text), None

