"""
Schemas for fuzzy fingerprint indexing and search configuration.
"""

from typing import List

from pydantic import BaseModel, Field, validator


class FuzzyFingerprintConfig(BaseModel):
    """Configuration for fuzzy fingerprint indexing at encode time."""

    enabled: bool = Field(
        default=False,
        description="Whether to generate fuzzy fingerprints during encoding.",
    )
    algorithm: str = Field(default="simhash", description="Fingerprint algorithm (currently simhash).")
    levels: List[str] = Field(
        default_factory=lambda: ["sentence", "paragraph"],
        description="Segmentation levels to fingerprint.",
    )
    include_document_fingerprint: bool = Field(
        default=False,
        description="Whether to include a document-level fingerprint.",
    )
    fingerprint_bits: int = Field(
        default=64,
        ge=32,
        le=256,
        description="Number of bits in the fingerprint.",
    )
    bucket_bits: int = Field(
        default=16,
        ge=8,
        le=32,
        description="Number of high-order bits used for bucket indexing.",
    )

    @validator("levels")
    def validate_levels(cls, value: List[str]) -> List[str]:
        valid_levels = {"sentence", "paragraph", "document"}
        invalid = [level for level in value if level not in valid_levels]
        if invalid:
            raise ValueError(f"Invalid fuzzy fingerprint levels: {invalid}. Must be one of {sorted(valid_levels)}.")
        return value


class FuzzySearchConfig(BaseModel):
    """Configuration for fuzzy fingerprint search during verification."""

    enabled: bool = Field(
        default=False,
        description="Whether to run fuzzy fingerprint search.",
    )
    algorithm: str = Field(
        default="simhash",
        description="Fingerprint algorithm (currently simhash).",
    )
    levels: List[str] = Field(
        default_factory=lambda: ["sentence", "paragraph"],
        description="Segmentation levels to search.",
    )
    similarity_threshold: float = Field(
        default=0.82,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for matches (0-1).",
    )
    max_candidates: int = Field(
        default=20,
        ge=1,
        le=200,
        description="Maximum number of candidate matches to return.",
    )
    include_merkle_proof: bool = Field(
        default=True,
        description="Whether to include Merkle proofs for matches.",
    )
    fallback_when_no_binding: bool = Field(
        default=True,
        description="Only run fuzzy search when no embeddings are found.",
    )

    @validator("levels")
    def validate_search_levels(cls, value: List[str]) -> List[str]:
        valid_levels = {"sentence", "paragraph", "document"}
        invalid = [level for level in value if level not in valid_levels]
        if invalid:
            raise ValueError(f"Invalid fuzzy search levels: {invalid}. Must be one of {sorted(valid_levels)}.")
        return value
