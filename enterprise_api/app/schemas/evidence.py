"""
Evidence Generation & Attribution API Schemas (TEAM_044 - Patent FIG. 11).

These schemas define request/response models for generating court-ready
evidence packages that prove content provenance and attribution.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class EvidenceGenerateRequest(BaseModel):
    """
    Request to generate an evidence package for content attribution.
    
    Patent Reference: FIG. 11 - Evidence Generation & Attribution Flow
    """
    
    target_text: str = Field(
        ...,
        description="Text content to generate evidence for",
        min_length=1,
    )
    document_id: Optional[str] = Field(
        default=None,
        description="Optional known document ID to verify against"
    )
    include_merkle_proof: bool = Field(
        default=True,
        description="Include Merkle proof in evidence package"
    )
    include_signature_chain: bool = Field(
        default=True,
        description="Include full signature verification chain"
    )
    include_timestamp_proof: bool = Field(
        default=True,
        description="Include timestamp verification"
    )
    export_format: str = Field(
        default="json",
        description="Export format: json, pdf, or both"
    )
    
    @validator('export_format')
    def validate_export_format(cls, v):
        allowed = ['json', 'pdf', 'both']
        if v not in allowed:
            raise ValueError(f"Export format must be one of: {', '.join(allowed)}")
        return v


class MerkleProofItem(BaseModel):
    """A single item in a Merkle proof path."""
    
    hash: str = Field(..., description="Hash value at this node")
    position: str = Field(..., description="Position: 'left' or 'right'")
    level: int = Field(..., description="Tree level (0 = leaf)")


class SignatureVerification(BaseModel):
    """Signature verification details."""
    
    signer_id: str = Field(..., description="Signer identifier")
    signer_name: Optional[str] = Field(None, description="Human-readable signer name")
    algorithm: str = Field(..., description="Signature algorithm used")
    public_key_fingerprint: str = Field(..., description="Public key fingerprint")
    signature_valid: bool = Field(..., description="Whether signature is valid")
    signed_at: Optional[datetime] = Field(None, description="Timestamp when signed")


class ContentMatch(BaseModel):
    """Details of matched content."""
    
    segment_text: str = Field(..., description="Matched text segment")
    segment_hash: str = Field(..., description="Hash of the segment")
    leaf_index: int = Field(..., description="Index in Merkle tree")
    confidence: float = Field(..., description="Match confidence (0-1)", ge=0, le=1)
    source_document_id: str = Field(..., description="Source document ID")
    source_organization_id: str = Field(..., description="Source organization ID")


class EvidencePackage(BaseModel):
    """
    Complete evidence package for content attribution.
    
    This package contains all cryptographic proofs needed to verify
    content provenance in legal or compliance contexts.
    """
    
    evidence_id: UUID = Field(..., description="Unique evidence package ID")
    generated_at: datetime = Field(..., description="When evidence was generated")
    
    # Target content info
    target_text_hash: str = Field(..., description="Hash of target text")
    target_text_preview: str = Field(..., description="Preview of target text (first 200 chars)")
    
    # Attribution results
    attribution_found: bool = Field(..., description="Whether attribution was found")
    attribution_confidence: float = Field(..., description="Overall confidence score", ge=0, le=1)
    
    # Source information
    source_document_id: Optional[str] = Field(None, description="Source document ID")
    source_organization_id: Optional[str] = Field(None, description="Source organization ID")
    source_organization_name: Optional[str] = Field(None, description="Source organization name")
    
    # Merkle proof
    merkle_root_hash: Optional[str] = Field(None, description="Merkle root hash")
    merkle_proof: Optional[List[MerkleProofItem]] = Field(None, description="Merkle proof path")
    merkle_proof_valid: Optional[bool] = Field(None, description="Whether Merkle proof is valid")
    
    # Signature verification
    signature_verification: Optional[SignatureVerification] = Field(
        None, description="Signature verification details"
    )
    
    # Content matches
    content_matches: List[ContentMatch] = Field(
        default_factory=list,
        description="List of matched content segments"
    )
    
    # Timestamps
    original_timestamp: Optional[datetime] = Field(None, description="Original signing timestamp")
    timestamp_verified: Optional[bool] = Field(None, description="Whether timestamp is verified")
    
    # Export URLs
    json_export_url: Optional[str] = Field(None, description="URL to download JSON export")
    pdf_export_url: Optional[str] = Field(None, description="URL to download PDF export")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class EvidenceGenerateResponse(BaseModel):
    """Response containing the generated evidence package."""
    
    success: bool = Field(..., description="Whether evidence generation succeeded")
    evidence: Optional[EvidencePackage] = Field(None, description="The evidence package")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    message: str = Field(..., description="Status message")


class EvidenceListRequest(BaseModel):
    """Request to list evidence packages."""
    
    document_id: Optional[str] = Field(None, description="Filter by document ID")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    limit: int = Field(default=50, description="Maximum results to return", ge=1, le=100)
    offset: int = Field(default=0, description="Offset for pagination", ge=0)


class EvidenceListResponse(BaseModel):
    """Response containing list of evidence packages."""
    
    success: bool = Field(..., description="Whether list retrieval succeeded")
    total_count: int = Field(..., description="Total number of evidence packages")
    evidence_packages: List[EvidencePackage] = Field(
        default_factory=list,
        description="List of evidence packages"
    )
    has_more: bool = Field(..., description="Whether more results are available")
