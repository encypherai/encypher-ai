"""Normalized hashing helpers for C2PA text assets.

This module centralises the NFC normalisation and hash computation rules
mandated by the C2PA text manifest specification. Both the embedding and
verification flows call into these helpers so that offsets, exclusions,
and hash algorithms remain perfectly aligned.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass

# Matches any run of horizontal whitespace (spaces, tabs, NBSP, etc.)
# but NOT newlines — paragraph structure is preserved.
_HORIZONTAL_WS = re.compile(r"[^\S\n]+")


@dataclass(frozen=True)
class NormalizedHashResult:
    """Container returned by :func:`compute_normalized_hash`.

    Attributes
    ----------
    normalized_text:
        NFC-normalised version of the input text.
    normalized_bytes:
        UTF-8 bytes for :attr:`normalized_text` (before exclusions are
        applied).
    filtered_bytes:
        UTF-8 bytes remaining after removing the requested exclusion ranges.
    hexdigest:
        Hex encoded digest of :attr:`filtered_bytes`.
    """

    normalized_text: str
    normalized_bytes: bytes
    filtered_bytes: bytes
    hexdigest: str

    @property
    def filtered_text(self) -> str:
        """Return the post-exclusion text as a Unicode string."""

        return self.filtered_bytes.decode("utf-8")


def normalize_whitespace(text: str) -> str:
    """Canonicalize whitespace so that text from different sources is identical.

    This is a **pre-processing** utility intended to be applied to text
    *before* it is signed.  It is **not** part of the C2PA hash computation
    (which mandates NFC-only normalisation).  By applying the same
    canonicalization when extracting text for signing and when extracting
    text for verification, the NFC hash will match on both sides.

    Transformations applied (in order):

    1. ``\\r\\n`` and ``\\r`` → ``\\n``  (line-ending canonicalization)
    2. ``\\xa0`` (NBSP) and other Unicode spaces → ASCII space
    3. Runs of horizontal whitespace collapsed to a single space
    4. Leading/trailing whitespace on each line stripped
    5. Trailing newlines stripped
    """
    # 1. Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # 2. Replace non-breaking / special Unicode spaces with ASCII space
    text = text.replace("\xa0", " ").replace("\u2009", " ").replace("\u200a", " ")
    # 3. Collapse horizontal whitespace runs (preserving newlines)
    text = _HORIZONTAL_WS.sub(" ", text)
    # 4. Strip leading/trailing whitespace per line
    text = "\n".join(line.strip() for line in text.split("\n"))
    # 5. Strip trailing newlines
    text = text.strip("\n")
    return text


def normalize_text(text: str) -> str:
    """Return the NFC-normalised variant of *text*.

    Per the C2PA text manifest specification, only Unicode Normalization
    Form C (NFC) is applied.  Whitespace is **not** altered here — callers
    that need whitespace canonicalization should use
    :func:`normalize_whitespace` as a pre-processing step before signing.
    """
    return unicodedata.normalize("NFC", text)


def _coerce_ranges(exclusions: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    coerced: list[tuple[int, int]] = []
    for start, length in exclusions:
        coerced_start = int(start)
        coerced_length = int(length)
        if coerced_start < 0 or coerced_length < 0:
            raise ValueError("Exclusion ranges must be non-negative")
        coerced.append((coerced_start, coerced_length))
    return sorted(coerced, key=lambda item: item[0])


def _apply_exclusions(normalized_bytes: bytes, exclusions: Sequence[tuple[int, int]]) -> bytes:
    if not exclusions:
        return normalized_bytes

    filtered = bytearray()
    position = 0
    for start, length in _coerce_ranges(exclusions):
        end = start + length
        if start < position:
            raise ValueError("Exclusion ranges must be non-overlapping and sorted")
        if end > len(normalized_bytes):
            raise ValueError("Exclusion range exceeds the length of the normalised data")
        filtered.extend(normalized_bytes[position:start])
        position = end
    filtered.extend(normalized_bytes[position:])
    return bytes(filtered)


def compute_normalized_hash(
    text: str,
    exclusions: Sequence[tuple[int, int]] | None = None,
    *,
    algorithm: str = "sha256",
) -> NormalizedHashResult:
    """Compute the hash mandated by the text C2PA specification.

    Parameters
    ----------
    text:
        The textual asset to normalise and hash.
    exclusions:
        Iterable of ``(start, length)`` byte ranges within the normalised UTF-8
        representation that must be removed prior to hashing.
    algorithm:
        Name of the hashing algorithm to use. ``sha256`` is the only value the
        specification currently allows but the parameter remains configurable
        for completeness.
    """

    normalized = normalize_text(text)
    normalized_bytes = normalized.encode("utf-8")
    filtered_bytes = _apply_exclusions(normalized_bytes, exclusions or [])
    try:
        digest = hashlib.new(algorithm.replace("-", ""))
    except ValueError as exc:
        raise ValueError(f"Unsupported hash algorithm '{algorithm}' for C2PA") from exc
    digest.update(filtered_bytes)
    return NormalizedHashResult(
        normalized_text=normalized,
        normalized_bytes=normalized_bytes,
        filtered_bytes=filtered_bytes,
        hexdigest=digest.hexdigest(),
    )


__all__ = ["NormalizedHashResult", "compute_normalized_hash", "normalize_text", "normalize_whitespace"]
