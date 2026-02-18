from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class VerifyOptions(BaseModel):
    """Optional parameters for verification request."""
    include_merkle_proof: bool = Field(default=False, description="Include Merkle proof details (requires API key)")
    include_raw_manifest: bool = Field(default=False, description="Include raw C2PA manifest data")


class VerifyRequest(BaseModel):
    text: str = Field(..., min_length=1)
    options: Optional[VerifyOptions] = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    hint: Optional[str] = None


class DocumentInfo(BaseModel):
    """Document metadata from the embedding."""
    document_id: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    document_type: Optional[str] = None


class C2PAInfo(BaseModel):
    """C2PA manifest information."""
    manifest_url: Optional[str] = None
    manifest_hash: Optional[str] = None
    validated: bool = False
    validation_type: Optional[str] = None  # "cryptographic" or "structural"
    assertions: Optional[List[Dict[str, Any]]] = None
    certificate_chain: Optional[List[str]] = None


class SegmentLocationInfo(BaseModel):
    """Location of a segment within the original document."""
    paragraph_index: int = Field(..., description="0-indexed paragraph number")
    sentence_in_paragraph: int = Field(..., description="0-indexed sentence within the paragraph")


class EmbeddingDetail(BaseModel):
    """Details for a single detected embedding/signature."""
    segment_uuid: str
    leaf_index: Optional[int] = None
    segment_location: Optional[SegmentLocationInfo] = None
    manifest_mode: Optional[str] = None


class MerkleProofInfo(BaseModel):
    """Merkle tree proof information (paid feature)."""
    root_hash: Optional[str] = None
    leaf_hash: Optional[str] = None
    leaf_index: Optional[int] = None
    proof_path: Optional[List[str]] = None
    verified: bool = False


class LicensingInfo(BaseModel):
    """Content licensing information."""
    license_type: Optional[str] = None
    license_url: Optional[str] = None
    usage_terms: Optional[str] = None
    attribution_required: bool = False


class VerifyVerdict(BaseModel):
    """Core verification result."""
    valid: bool
    tampered: bool
    reason_code: str
    signer_id: Optional[str] = None
    signer_name: Optional[str] = None
    publisher_name: Optional[str] = None
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None
    timestamp: Optional[datetime] = None
    # Rich metadata - all free
    document: Optional[DocumentInfo] = None
    c2pa: Optional[C2PAInfo] = None
    licensing: Optional[LicensingInfo] = None
    # Embedding details (segment locations for all detected signatures)
    embeddings: Optional[List[EmbeddingDetail]] = None
    total_embeddings: Optional[int] = None
    total_segments_in_document: Optional[int] = None
    # Paid features
    merkle_proof: Optional[MerkleProofInfo] = None
    # Legacy details field for backward compat
    details: Dict[str, Any] = Field(default_factory=dict)


class VerifyResponse(BaseModel):
    success: bool
    data: Optional[VerifyVerdict] = None
    error: Optional[ErrorDetail] = None
    correlation_id: str
