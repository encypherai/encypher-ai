"""
Pydantic schemas for embedding API endpoints.

Defines request/response models for minimal signed embeddings.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from app.schemas.signing_constants import (
    DISTRIBUTION_TARGETS,
    EMBEDDING_STRATEGIES,
    MANIFEST_MODES,
    MERKLE_SEGMENTATION_LEVELS,
    SEGMENTATION_LEVELS,
)

# ============================================================================
# Embedding Creation Schemas
# ============================================================================


class EmbeddingOptions(BaseModel):
    """Options for embedding generation."""

    format: str = Field(default="html", description="Output format: html, markdown, json, pdf, plain")
    method: str = Field(default="data-attribute", description="Embedding method: data-attribute, span, comment")
    include_text: bool = Field(default=True, description="Whether to return text with embeddings")

    @validator("format")
    def validate_format(cls, v):
        allowed = ["html", "markdown", "json", "pdf", "plain"]
        if v not in allowed:
            raise ValueError(f"Format must be one of: {', '.join(allowed)}")
        return v

    @validator("method")
    def validate_method(cls, v):
        allowed = ["data-attribute", "span", "comment"]
        if v not in allowed:
            raise ValueError(f"Method must be one of: {', '.join(allowed)}")
        return v


class LicenseInfo(BaseModel):
    """License information for content."""

    type: str = Field(..., description="License type (e.g., 'All Rights Reserved', 'CC-BY-4.0')")
    url: Optional[str] = Field(None, description="License URL")
    contact_email: Optional[str] = Field(None, description="Contact email for licensing")


class RightsMetadata(BaseModel):
    copyright_holder: Optional[str] = Field(None, description="Copyright holder / publisher name")
    license_url: Optional[str] = Field(None, description="URL to license terms")
    usage_terms: Optional[str] = Field(None, description="Human-readable usage terms")
    syndication_allowed: Optional[bool] = Field(None, description="Whether downstream syndication is permitted")
    embargo_until: Optional[datetime] = Field(None, description="Optional embargo end timestamp")
    contact_email: Optional[str] = Field(None, description="Contact email for licensing")


class EncodeWithEmbeddingsRequest(BaseModel):
    """Request to encode document with minimal signed embeddings."""

    document_id: str = Field(..., description="Unique document identifier")
    text: str = Field(..., description="Full document text to encode")
    segmentation_level: str = Field(
        default="sentence", description="Segmentation level: document (free tier, no segmentation), sentence, paragraph, section, word"
    )
    segmentation_levels: Optional[List[str]] = Field(
        default=None,
        description="Optional list of Merkle segmentation levels to build/index (sentence, paragraph, section). Defaults to [segmentation_level].",
    )
    index_for_attribution: Optional[bool] = Field(
        default=None,
        description="Whether to enforce Merkle indexing quotas for attribution workflows. Defaults to true for paid tiers.",
    )
    action: str = Field(default="c2pa.created", description="C2PA action type: c2pa.created (new content) or c2pa.edited (modified content)")
    # === API Feature Augmentation (TEAM_044) ===
    manifest_mode: str = Field(
        default="full",
        description="Controls manifest detail level. Options: full, lightweight_uuid, minimal_uuid, hybrid, zw_embedding, micro. micro uses ultra-compact per-sentence markers; behaviour controlled by ecc and embed_c2pa flags. Availability depends on plan tier.",
    )
    ecc: bool = Field(
        default=True,
        description="Enable Reed-Solomon error correction for micro mode (44 chars/segment vs 36). Ignored for non-micro modes.",
    )
    embed_c2pa: bool = Field(
        default=True,
        description="Embed full C2PA document manifest into signed content for micro mode. When false, per-sentence markers only; C2PA manifest is still generated and stored in DB. Ignored for non-micro modes.",
    )
    embedding_strategy: str = Field(
        default="single_point",
        description="Controls embedding placement strategy. Options: single_point, distributed, distributed_redundant. Availability depends on plan tier.",
    )
    distribution_target: Optional[str] = Field(
        default=None,
        description="Target characters for distributed embedding: whitespace, punctuation, all_chars. Only used when embedding_strategy is distributed or distributed_redundant.",
    )
    add_dual_binding: bool = Field(default=False, description="Enable additional integrity binding. Availability depends on plan tier.")
    disable_c2pa: bool = Field(default=False, description="Opt-out of C2PA embedding. When true, only basic metadata is embedded.")
    store_c2pa_manifest: bool = Field(
        default=True,
        description="Store extracted C2PA manifest in content DB for DB-backed verification features.",
    )
    previous_instance_id: Optional[str] = Field(
        None, description="Previous manifest instance_id for edit provenance chain (required if action=c2pa.edited)"
    )
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional document metadata (title, author, etc.)")
    c2pa_manifest_url: Optional[str] = Field(None, description="Optional C2PA manifest URL")
    c2pa_manifest_hash: Optional[str] = Field(None, description="Optional C2PA manifest hash")
    custom_assertions: Optional[List[Dict[str, Any]]] = Field(None, description="Custom C2PA assertions to include in manifest")
    template_id: Optional[str] = Field(None, description="Template ID to use for assertions")
    validate_assertions: bool = Field(True, description="Whether to validate custom assertions against registered schemas")
    digital_source_type: Optional[str] = Field(
        None,
        description="IPTC digital source type URI (e.g., 'http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia' for AI-generated content)",
    )
    license: Optional[LicenseInfo] = Field(None, description="Optional license information")
    rights: Optional[RightsMetadata] = Field(
        None,
        description="Optional rights metadata to embed (Business+).",
    )
    embedding_options: EmbeddingOptions = Field(default_factory=EmbeddingOptions, description="Embedding generation options")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration datetime for embeddings")

    @validator("segmentation_level")
    def validate_segmentation_level(cls, v):
        if v not in SEGMENTATION_LEVELS:
            raise ValueError(f"Segmentation level must be one of: {', '.join(SEGMENTATION_LEVELS)}")
        return v

    @validator("segmentation_levels")
    def validate_segmentation_levels(cls, v):
        if v is None:
            return v
        for level in v:
            if level not in MERKLE_SEGMENTATION_LEVELS:
                raise ValueError(f"segmentation_levels entries must be one of: {', '.join(sorted(MERKLE_SEGMENTATION_LEVELS))}")
        return v

    @validator("manifest_mode")
    def validate_manifest_mode(cls, v):
        if v not in MANIFEST_MODES:
            raise ValueError(f"Manifest mode must be one of: {', '.join(MANIFEST_MODES)}")
        return v

    @validator("embedding_strategy")
    def validate_embedding_strategy(cls, v):
        if v not in EMBEDDING_STRATEGIES:
            raise ValueError(f"Embedding strategy must be one of: {', '.join(EMBEDDING_STRATEGIES)}")
        return v

    @validator("distribution_target")
    def validate_distribution_target(cls, v):
        if v is None:
            return v
        if v not in DISTRIBUTION_TARGETS:
            raise ValueError(f"Distribution target must be one of: {', '.join(DISTRIBUTION_TARGETS)}")
        return v


class EmbeddingInfo(BaseModel):
    """
    Information about a single embedding.
    """

    leaf_index: int = Field(..., description="Position in document (0-indexed)")
    text: Optional[str] = Field(None, description="Text containing the embedding (if include_text=true)")
    ref_id: Optional[str] = Field(None, description="Deprecated")
    signature: Optional[str] = Field(None, description="Deprecated")
    embedding: Optional[str] = Field(None, description="Deprecated")
    verification_url: Optional[str] = Field(None, description="Deprecated")
    leaf_hash: str = Field(..., description="Cryptographic hash of the signed text segment")


class MerkleTreeInfo(BaseModel):
    """Merkle tree information."""

    root_hash: str = Field(..., description="Root hash for the integrity proof")
    total_leaves: int = Field(..., description="Number of leaf nodes")
    tree_depth: int = Field(..., description="Height of the tree")


class MerkleTreeLevelInfo(MerkleTreeInfo):
    indexed: bool = Field(..., description="Whether the Merkle tree was indexed for attribution workflows")


class EncodeWithEmbeddingsResponse(BaseModel):
    """Response from encoding document with embeddings."""

    success: bool = Field(True, description="Whether encoding succeeded")
    document_id: str = Field(..., description="Document identifier")
    merkle_tree: Optional[MerkleTreeInfo] = Field(None, description="Merkle tree information (None for free tier)")
    merkle_trees: Optional[Dict[str, MerkleTreeLevelInfo]] = Field(
        None,
        description="Optional mapping of segmentation level to Merkle tree metadata.",
    )
    embeddings: List[EmbeddingInfo] = Field(..., description="List of generated embeddings")
    embedded_content: Optional[str] = Field(None, description="Content with embeddings injected (if format specified)")
    statistics: Dict[str, Any] = Field(..., description="Processing statistics")
    metadata: Optional[Dict[str, Any]] = Field(None, description="C2PA manifest metadata including instance_id")


# ============================================================================
# Verification Schemas
# ============================================================================


class VerifyEmbeddingRequest(BaseModel):
    """Request to verify an embedding (for batch operations)."""

    ref_id: str = Field(..., description="Reference ID (8 hex characters)")
    signature: str = Field(..., description="Signature (8+ hex characters)")


class SegmentLocation(BaseModel):
    """Location of a segment within the document hierarchy."""

    paragraph_index: int = Field(..., description="0-indexed paragraph number")
    sentence_in_paragraph: int = Field(..., description="0-indexed sentence position within the paragraph")
    total_segments: Optional[int] = Field(None, description="Total number of segments in the document")


class ContentInfo(BaseModel):
    """Content information from verification."""

    text_preview: Optional[str] = Field(None, description="Optional preview derived from submitted text")
    leaf_hash: str = Field(..., description="Cryptographic hash of full content")
    leaf_index: int = Field(..., description="Position in document")
    segment_location: Optional[SegmentLocation] = Field(None, description="Hierarchical location of this segment (paragraph, sentence)")


class SignerIdentity(BaseModel):
    """Signer identity and trust chain information.

    TEAM_165: When an org starts with a self-signed key managed by Encypher,
    micro markers are already cryptographically bound to that key. If the org
    later obtains a CA-signed certificate (via /byok/certificates), the trust
    chain upgrades automatically — no re-signing needed.
    """

    organization_id: str = Field(..., description="Organization identifier")
    organization_name: Optional[str] = Field(None, description="Organization display name")
    certificate_status: str = Field(..., description="Certificate lifecycle: none, pending, active, expired, revoked")
    ca_backed: bool = Field(False, description="True if the org certificate chains to a trusted CA (not self-signed)")
    issuer: Optional[str] = Field(None, description="Certificate issuer (CA name) if CA-backed, or 'self-signed'")
    certificate_expiry: Optional[datetime] = Field(None, description="Certificate expiry timestamp")
    trust_level: str = Field(
        "self_signed",
        description="Trust level: 'ca_verified' (chains to C2PA-trusted CA), 'self_signed' (Encypher-managed key), 'none' (no certificate)",
    )


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

    manifest_url: Optional[str] = Field(None, description="C2PA manifest URL")
    manifest_hash: Optional[str] = Field(None, description="Manifest hash")
    validated: bool = Field(..., description="Whether the manifest passed validation")
    validation_type: str = Field(..., description="Validation semantics.")
    validation_details: Optional[Dict[str, Any]] = Field(None, description="Detailed validation results (assertions, signatures, errors)")
    manifest_data: Optional[Dict[str, Any]] = Field(None, description="Full C2PA manifest data (available for micro mode)")


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
    signer_identity: Optional[SignerIdentity] = Field(None, description="Signer identity and trust chain (CA-backed or self-signed)")
    licensing: Optional[LicensingInfo] = Field(None, description="Licensing information")
    verification_url: Optional[str] = Field(None, description="Verification URL")
    error: Optional[str] = Field(None, description="Error message if invalid")


class BatchVerifyRequest(BaseModel):
    """Request to verify multiple embeddings."""

    references: List[VerifyEmbeddingRequest] = Field(..., description="List of embeddings to verify")


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
