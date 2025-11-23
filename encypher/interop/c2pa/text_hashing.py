"""Normalized hashing helpers for C2PA text assets.

This module centralises the NFC normalisation and hash computation rules
mandated by the C2PA text manifest specification. Both the embedding and
verification flows call into these helpers so that offsets, exclusions,
and hash algorithms remain perfectly aligned.
"""

from __future__ import annotations

import hashlib
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass


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


def normalize_text(text: str) -> str:
    """Return the NFC-normalised variant of *text*."""

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


__all__ = ["NormalizedHashResult", "compute_normalized_hash", "normalize_text"]
