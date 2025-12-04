"""
Pydantic schemas for embedding API endpoints.

Defines request/response models for minimal signed embeddings.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

# ============================================================================
# Embedding Creation Schemas
# ============================================================================

class EmbeddingOptions(BaseModel):
    """Options for embedding generation."""
    format: str = Field(
        default="html",
        description="Output format: html, markdown, json, pdf, plain"
    )
    method: str = Field(
        default="data-attribute",
        description="Embedding method: data-attribute, span, comment"
    )
    include_text: bool = Field(
        default=True,
        description="Whether to return text with embeddings"
    )
    
    @validator('format')
    def validate_format(cls, v):
        allowed = ['html', 'markdown', 'json', 'pdf', 'plain']
        if v not in allowed:
            raise ValueError(f"Format must be one of: {', '.join(allowed)}")
        return v
    
    @validator('method')
    def validate_method(cls, v):
        allowed = ['data-attribute', 'span', 'comment']
        if v not in allowed:
            raise ValueError(f"Method must be one of: {', '.join(allowed)}")
        return v


class LicenseInfo(BaseModel):
    """License information for content."""
    type: str = Field(..., description="License type (e.g., 'All Rights Reserved', 'CC-BY-4.0')")
    url: Optional[str] = Field(None, description="License URL")
    contact_email: Optional[str] = Field(None, description="Contact email for licensing")


class EncodeWithEmbeddingsRequest(BaseModel):
    """Request to encode document with minimal signed embeddings."""
    document_id: str = Field(..., description="Unique document identifier")
    text: str = Field(..., description="Full document text to encode")
    segmentation_level: str = Field(
        default="sentence",
        description="Segmentation level: document (free tier, no segmentation), sentence, paragraph, section, word"
    )
    action: str = Field(
        default="c2pa.created",
        description="C2PA action type: c2pa.created (new content) or c2pa.edited (modified content)"
    )
    previous_instance_id: Optional[str] = Field(
        None,
        description="Previous manifest instance_id for edit provenance chain (required if action=c2pa.edited)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional document metadata (title, author, etc.)"
    )
    c2pa_manifest_url: Optional[str] = Field(
        None,
        description="Optional C2PA manifest URL"
    )
    c2pa_manifest_hash: Optional[str] = Field(
        None,
        description="Optional C2PA manifest hash"
    )
    custom_assertions: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Custom C2PA assertions to include in manifest"
    )
    validate_assertions: bool = Field(
        True,
        description="Whether to validate custom assertions against registered schemas"
    )
    digital_source_type: Optional[str] = Field(
        None,
        description="IPTC digital source type URI (e.g., 'http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia' for AI-generated content)"
    )
    license: Optional[LicenseInfo] = Field(
        None,
        description="Optional license information"
    )
    embedding_options: EmbeddingOptions = Field(
        default_factory=EmbeddingOptions,
        description="Embedding generation options"
    )
    expires_at: Optional[datetime] = Field(
        None,
        description="Optional expiration datetime for embeddings"
    )
    
    @validator('segmentation_level')
    def validate_segmentation_level(cls, v):
        allowed = ['document', 'word', 'sentence', 'paragraph', 'section']
        if v not in allowed:
            raise ValueError(f"Segmentation level must be one of: {', '.join(allowed)}")
        return v


class EmbeddingInfo(BaseModel):
    """
    Information about a single invisible embedding.
    
    Uses encypher-ai package for invisible Unicode variation selector embeddings.
    No visible ref_id, signature, or embedding string - all embedded invisibly.
    """
    leaf_index: int = Field(..., description="Position in document (0-indexed)")
    text: Optional[str] = Field(None, description="Text with invisible embedding (if include_text=true)")
    ref_id: Optional[str] = Field(None, description="Deprecated: No visible ref_id with invisible embeddings")
    signature: Optional[str] = Field(None, description="Deprecated: No visible signature with invisible embeddings")
    embedding: Optional[str] = Field(None, description="Deprecated: No visible embedding string with invisible embeddings")
    verification_url: Optional[str] = Field(None, description="Deprecated: Verification by extracting from text")
    leaf_hash: str = Field(..., description="SHA-256 hash of text segment")


class MerkleTreeInfo(BaseModel):
    """Merkle tree information."""
    root_hash: str = Field(..., description="Merkle tree root hash")
    total_leaves: int = Field(..., description="Number of leaf nodes")
    tree_depth: int = Field(..., description="Height of the tree")


class EncodeWithEmbeddingsResponse(BaseModel):
    """Response from encoding document with embeddings."""
    success: bool = Field(True, description="Whether encoding succeeded")
    document_id: str = Field(..., description="Document identifier")
    merkle_tree: Optional[MerkleTreeInfo] = Field(None, description="Merkle tree information (None for free tier)")
    embeddings: List[EmbeddingInfo] = Field(..., description="List of generated embeddings")
    embedded_content: Optional[str] = Field(
        None,
        description="Content with embeddings injected (if format specified)"
    )
    statistics: Dict[str, Any] = Field(..., description="Processing statistics")
    metadata: Optional[Dict[str, Any]] = Field(None, description="C2PA manifest metadata including instance_id")


# ============================================================================
# Verification Schemas
# ============================================================================

class VerifyEmbeddingRequest(BaseModel):
    """Request to verify an embedding (for batch operations)."""
    ref_id: str = Field(..., description="Reference ID (8 hex characters)")
    signature: str = Field(..., description="Signature (8+ hex characters)")


class ContentInfo(BaseModel):
    """Content information from verification."""
    text_preview: str = Field(..., description="First 200 characters of content")
    leaf_hash: str = Field(..., description="SHA-256 hash of full content")
    leaf_index: int = Field(..., description="Position in document")


class DocumentInfo(BaseModel):
    """Document information from verification."""
    document_id: str = Field(..., description="Document identifier")
    title: Optional[str] = Field(None, description="Document title")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    author: Optional[str] = Field(None, description="Author name")
    organization: str = Field(..., description="Organization name")


class MerkleProofInfo(BaseModel):
    """Merkle proof information."""
    root_hash: str = Field(..., description="Merkle tree root hash")
    verified: bool = Field(..., description="Whether proof is valid")
    proof_url: Optional[str] = Field(None, description="URL to full proof")


class C2PAInfo(BaseModel):
    """C2PA manifest information with verification details."""
    manifest_url: str = Field(..., description="C2PA manifest URL")
    manifest_hash: Optional[str] = Field(None, description="Manifest hash")
    verified: bool = Field(..., description="Whether manifest is verified")
    verification_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed verification results (assertions, signatures, errors)"
    )


class LicensingInfo(BaseModel):
    """Licensing information."""
    license_type: str = Field(..., description="License type")
    license_url: Optional[str] = Field(None, description="License URL")
    usage_terms: Optional[str] = Field(None, description="Usage terms summary")
    contact_email: Optional[str] = Field(None, description="Contact for licensing")


class VerifyEmbeddingResponse(BaseModel):
    """Response from verifying an embedding."""
    valid: bool = Field(..., description="Whether embedding is valid")
    ref_id: str = Field(..., description="Reference ID")
    verified_at: Optional[datetime] = Field(None, description="Verification timestamp")
    content: Optional[ContentInfo] = Field(None, description="Content information")
    document: Optional[DocumentInfo] = Field(None, description="Document information")
    merkle_proof: Optional[MerkleProofInfo] = Field(None, description="Merkle proof information")
    c2pa: Optional[C2PAInfo] = Field(None, description="C2PA information")
    licensing: Optional[LicensingInfo] = Field(None, description="Licensing information")
    verification_url: Optional[str] = Field(None, description="Verification URL")
    error: Optional[str] = Field(None, description="Error message if invalid")


class BatchVerifyRequest(BaseModel):
    """Request to verify multiple embeddings."""
    references: List[VerifyEmbeddingRequest] = Field(
        ...,
        description="List of embeddings to verify"
    )


class BatchVerifyResult(BaseModel):
    """Result for a single embedding in batch verification."""
    ref_id: str = Field(..., description="Reference ID")
    valid: bool = Field(..., description="Whether embedding is valid")
    document_id: Optional[str] = Field(None, description="Document ID if valid")
    text_preview: Optional[str] = Field(None, description="Text preview if valid")
    error: Optional[str] = Field(None, description="Error message if invalid")


class BatchVerifyResponse(BaseModel):
    """Response from batch verification."""
    results: List[BatchVerifyResult] = Field(..., description="Verification results")
    total: int = Field(..., description="Total number of embeddings checked")
    valid_count: int = Field(..., description="Number of valid embeddings")
    invalid_count: int = Field(..., description="Number of invalid embeddings")


# ============================================================================
# Partner Integration Schemas
# ============================================================================

class Finding(BaseModel):
    """A single finding from web scraping partner."""
    ref_id: str = Field(..., description="Reference ID found")
    found_url: str = Field(..., description="URL where content was found")
    found_at: datetime = Field(..., description="When content was found")
    context: Optional[str] = Field(None, description="Context about the finding")
    screenshot_url: Optional[str] = Field(None, description="Screenshot URL")


class ReportFindingsRequest(BaseModel):
    """Request from partner to report findings."""
    partner_id: str = Field(..., description="Partner identifier")
    scan_date: datetime = Field(..., description="Date of scan")
    findings: List[Finding] = Field(..., description="List of findings")


class ReportFindingsResponse(BaseModel):
    """Response to partner findings report."""
    success: bool = Field(True, description="Whether report was processed")
    findings_processed: int = Field(..., description="Number of findings processed")
    notifications_sent: int = Field(..., description="Number of notifications sent")
    summary: Dict[str, int] = Field(..., description="Summary statistics")


# ============================================================================
# Organization Dashboard Schemas
# ============================================================================

class FindingInfo(BaseModel):
    """Information about a finding for organization dashboard."""
    ref_id: str = Field(..., description="Reference ID")
    document_id: str = Field(..., description="Document ID")
    text_preview: str = Field(..., description="Text preview")
    found_url: str = Field(..., description="URL where found")
    found_at: datetime = Field(..., description="When found")
    status: str = Field(..., description="Status: authorized, unauthorized, pending_review")
    actions_available: List[str] = Field(..., description="Available actions")
    screenshot_url: Optional[str] = Field(None, description="Screenshot URL")


class FindingsSummary(BaseModel):
    """Summary of findings."""
    total_findings: int = Field(..., description="Total number of findings")
    unauthorized: int = Field(..., description="Number of unauthorized uses")
    authorized: int = Field(..., description="Number of authorized uses")
    pending_review: int = Field(..., description="Number pending review")


class GetFindingsResponse(BaseModel):
    """Response with organization's findings."""
    findings: List[FindingInfo] = Field(..., description="List of findings")
    summary: FindingsSummary = Field(..., description="Summary statistics")


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response."""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    error_code: Optional[str] = Field(None, description="Error code for programmatic handling")
