"""
Multi-Source Hash Table Lookup Schemas (TEAM_044 - Patent FIG. 8).

These schemas define request/response models for looking up content
across multiple sources with chronological and authority ranking.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class MultiSourceLookupRequest(BaseModel):
    """
    Request to look up content across multiple sources.

    Patent Reference: FIG. 8 - Multi-Source Hash Table Lookup
    """

    text_segment: str = Field(
        ...,
        description="Text segment to search for",
        min_length=1,
    )
    include_all_sources: bool = Field(default=True, description="Return all matching sources (not just first)")
    order_by: str = Field(default="chronological", description="Ordering: chronological (earliest first), authority, or confidence")
    include_authority_score: bool = Field(default=False, description="Include authority ranking scores (Enterprise feature)")
    max_results: int = Field(
        default=10,
        description="Maximum number of sources to return",
        ge=1,
        le=100,
    )

    @validator("order_by")
    def validate_order_by(cls, v):
        allowed = ["chronological", "authority", "confidence"]
        if v not in allowed:
            raise ValueError(f"order_by must be one of: {', '.join(allowed)}")
        return v


class SourceRecord(BaseModel):
    """A single source record in the lookup results."""

    document_id: str = Field(..., description="Source document ID")
    organization_id: str = Field(..., description="Source organization ID")
    organization_name: Optional[str] = Field(None, description="Organization name")
    segment_hash: str = Field(..., description="Hash of the matched segment")
    leaf_index: int = Field(..., description="Index in source Merkle tree")
    merkle_root_hash: Optional[str] = Field(None, description="Merkle root hash")

    # Timestamps
    created_at: datetime = Field(..., description="When content was first registered")
    signed_at: Optional[datetime] = Field(None, description="When content was signed")

    # Scores
    confidence: float = Field(..., description="Match confidence (0-1)", ge=0, le=1)
    authority_score: Optional[float] = Field(
        None,
        description="Authority ranking score (0-1)",
        ge=0,
        le=1,
    )

    # Linked list info
    is_original: bool = Field(..., description="Whether this is the original source")
    previous_source_id: Optional[str] = Field(None, description="Previous source in chain")
    next_source_id: Optional[str] = Field(None, description="Next source in chain")

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MultiSourceLookupResponse(BaseModel):
    """Response containing multi-source lookup results."""

    success: bool = Field(..., description="Whether lookup succeeded")
    query_hash: str = Field(..., description="Hash of the queried text")
    total_sources: int = Field(..., description="Total number of matching sources")

    # Results
    sources: List[SourceRecord] = Field(default_factory=list, description="List of matching sources")
    original_source: Optional[SourceRecord] = Field(None, description="The original/earliest source")

    # Chain info
    has_chain: bool = Field(..., description="Whether sources form a linked chain")
    chain_length: int = Field(default=0, description="Length of the source chain")

    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    message: str = Field(..., description="Status message")


class AuthorityConfig(BaseModel):
    """Configuration for authority ranking."""

    organization_weights: Dict[str, float] = Field(default_factory=dict, description="Custom weights for specific organizations (0-1)")
    prefer_verified: bool = Field(default=True, description="Prefer verified/trusted organizations")
    age_decay_factor: float = Field(
        default=0.1,
        description="How much to decay authority by age (0-1)",
        ge=0,
        le=1,
    )
