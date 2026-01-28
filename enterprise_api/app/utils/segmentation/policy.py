"""Segmentation and canonicalization version metadata."""

from typing import Any, Dict, List, Optional

from .default import SPACY_AVAILABLE


def build_processing_metadata(
    *,
    segmentation_level: Optional[str],
    segmentation_levels: Optional[List[str]] = None,
    include_words: bool = False,
) -> Dict[str, Any]:
    levels = segmentation_levels or ([segmentation_level] if segmentation_level else [])
    sentence_boundary = "spacy_default" if SPACY_AVAILABLE else "regex_fallback"

    return {
        "canonicalization_version": "v1",
        "canonicalization": {
            "unicode_normalization": "NFC",
            "segmentation_boundary_normalization": "normalize_unicode_v1",
        },
        "hashing": {
            "algorithm": "sha256",
            "leaf": {
                "unicode_normalization": "NFC",
            },
        },
        "segmentation": {
            "strategy": "hierarchical",
            "levels": levels,
            "primary_level": segmentation_level,
            "include_words": include_words,
            "sentence_boundary": sentence_boundary,
        },
    }
