"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


class SignRequest(BaseModel):
    """Request model for signing content."""
    text: str = Field(..., description="Content to sign")
    document_id: Optional[str] = Field(None, description="Optional custom document identifier")
    document_title: Optional[str] = Field(None, description="Optional document title")
    document_url: Optional[str] = Field(None, description="Optional document URL")
    document_type: str = Field(default="article", description="Document type")
    claim_generator: Optional[str] = Field(None, description="Optional claim generator identifier")
    actions: Optional[List[Dict[str, Any]]] = Field(None, description="Optional list of C2PA actions")


class SignResponse(BaseModel):
    """Response model for signing operation."""
    success: bool
    document_id: str
    signed_text: str
    total_sentences: int
    verification_url: str


class VerifyRequest(BaseModel):
    """Request model for verification."""
    text: str = Field(..., description="Signed text to verify")


class ErrorDetail(BaseModel):
    """Standard error payload."""

    code: str
    message: str
    hint: Optional[str] = None


class VerifyVerdict(BaseModel):
    """Verification verdict payload."""

    valid: bool
    tampered: bool
    reason_code: str
    signer_id: Optional[str] = None
    signer_name: Optional[str] = None
    timestamp: Optional[datetime] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class VerifyResponse(BaseModel):
    """Response model for verification operation."""

    success: bool
    data: Optional[VerifyVerdict] = None
    error: Optional[ErrorDetail] = None
    correlation_id: str

    @property
    def is_valid(self) -> bool:
        """Backward compatible access to verdict validity."""

        return bool(self.data and self.data.valid)

    @property
    def tampered(self) -> bool:
        """Backward compatible tamper accessor."""

        return bool(self.data and self.data.tampered)

    @property
    def organization_name(self) -> Optional[str]:
        """Return signer name for legacy callers."""

        return self.data.signer_name if self.data else None

    @property
    def signer_id(self) -> Optional[str]:
        """Expose signer id for legacy callers."""

        return self.data.signer_id if self.data else None

    @property
    def signature_timestamp(self) -> Optional[datetime]:
        """Expose timestamp for legacy callers."""

        return self.data.timestamp if self.data else None

    @property
    def manifest(self) -> Dict[str, Any]:
        """Return manifest details for legacy callers."""

        if self.data and "manifest" in self.data.details:
            return self.data.details["manifest"]
        return {}


class LookupRequest(BaseModel):
    """Request model for sentence lookup."""
    sentence_text: str = Field(..., description="Sentence to look up")


class LookupResponse(BaseModel):
    """Response model for lookup operation."""
    success: bool
    found: bool
    document_title: Optional[str] = None
    organization_name: Optional[str] = None
    publication_date: Optional[datetime] = None
    sentence_index: Optional[int] = None
    document_url: Optional[str] = None


class UsageStats(BaseModel):
    """Usage statistics."""
    documents_signed: int
    sentences_signed: int
    api_calls_this_month: int
    monthly_quota: int
    quota_remaining: int


class StatsResponse(BaseModel):
    """Response model for statistics."""
    success: bool
    organization_id: str
    organization_name: str
    tier: str
    usage: UsageStats


class ErrorResponse(BaseModel):
    """Error response from API."""
    success: bool = False
    error: Dict[str, Any]


class MerkleTreeNode(BaseModel):
    """A single node within a Merkle tree."""

    hash: str = Field(..., description="Node hash")
    depth: Optional[int] = Field(None, description="Depth (root=0)")
    position: Optional[int] = Field(None, description="Position index at depth")
    is_leaf: bool = Field(False, description="Whether this node is a leaf")
    leaf_index: Optional[int] = Field(None, description="Leaf index if leaf")
    left_child_hash: Optional[str] = Field(None, description="Left child hash")
    right_child_hash: Optional[str] = Field(None, description="Right child hash")
    text_content: Optional[str] = Field(None, description="Original text for leaf nodes")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MerkleTreeDetails(BaseModel):
    """Full Merkle tree representation returned by the Enterprise API."""

    model_config = ConfigDict(extra="allow")

    root_id: str = Field(..., description="UUID of the Merkle root")
    root_hash: str = Field(..., description="Root hash")
    tree_depth: Optional[int] = Field(None, description="Depth of the tree")
    leaf_count: Optional[int] = Field(None, description="Number of leaves")
    nodes: List[MerkleTreeNode] = Field(default_factory=list, description="Flattened node list")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")


class MerkleProofStep(BaseModel):
    """Single hop in a Merkle proof."""

    hash: str = Field(..., description="Sibling hash")
    position: Optional[str] = Field(None, description="left/right position relative to target")


class MerkleProof(BaseModel):
    """Merkle proof payload for a sentence-level verification."""

    root_hash: str = Field(..., description="Root hash the proof validates against")
    target_hash: Optional[str] = Field(None, description="Target hash for the proof")
    leaf_index: Optional[int] = Field(None, description="Leaf index being proven")
    verified: bool = Field(False, description="Whether proof verification succeeded")
    proof_path: List[MerkleProofStep] = Field(default_factory=list, description="Proof steps")


class ContentInfo(BaseModel):
    """Content information returned from verification endpoints."""

    text_preview: str = Field(..., description="Preview of verified content")
    leaf_hash: str = Field(..., description="Hash of the verified content")
    leaf_index: int = Field(..., description="Leaf index within the Merkle tree")


class DocumentInfo(BaseModel):
    """Document metadata returned from verification endpoints."""

    document_id: str
    title: Optional[str] = None
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    organization: str


class MerkleProofInfo(BaseModel):
    """Summary of the Merkle proof returned by verification endpoints."""

    root_hash: str
    verified: bool
    proof_url: Optional[str] = None


class C2PAInfo(BaseModel):
    """C2PA manifest verification info."""

    manifest_url: str
    manifest_hash: Optional[str] = None
    verified: bool
    verification_details: Optional[Dict[str, Any]] = None


class LicensingInfo(BaseModel):
    """Licensing metadata associated with verified content."""

    license_type: str
    license_url: Optional[str] = None
    usage_terms: Optional[str] = None
    contact_email: Optional[str] = None


class VerifyEmbeddingResponse(BaseModel):
    """Response payload for `GET /api/v1/public/verify/{ref_id}`."""

    valid: bool
    ref_id: str
    verified_at: Optional[datetime] = None
    content: Optional[ContentInfo] = None
    document: Optional[DocumentInfo] = None
    merkle_proof: Optional[MerkleProofInfo] = None
    c2pa: Optional[C2PAInfo] = None
    licensing: Optional[LicensingInfo] = None
    verification_url: Optional[str] = None
    error: Optional[str] = None


class ExtractAndVerifyResponse(BaseModel):
    """Response payload for `POST /api/v1/public/extract-and-verify`."""

    valid: bool
    verified_at: Optional[datetime] = None
    content: Optional[ContentInfo] = None
    document: Optional[DocumentInfo] = None
    merkle_proof: Optional[MerkleProofInfo] = None
    c2pa: Optional[C2PAInfo] = None
    licensing: Optional[LicensingInfo] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class StreamEvent(BaseModel):
    """Normalized representation of a server-sent event."""

    event: str
    data: Any
    raw: Dict[str, Any] = Field(default_factory=dict)


class EmbeddingOptions(BaseModel):
    """Options for embedding generation."""
    format: str = Field(default="html", description="html, markdown, json, pdf, or plain")
    method: str = Field(default="data-attribute", description="data-attribute, span, or comment")
    include_text: bool = Field(default=True, description="Return text with embedded markers")


class LicenseInfo(BaseModel):
    """License metadata for embeddings."""
    type: str = Field(..., description="License type (e.g., 'All Rights Reserved')")
    url: Optional[str] = Field(None, description="Optional URL with license terms")
    contact_email: Optional[str] = Field(None, description="License contact email")


class EncodeWithEmbeddingsRequest(BaseModel):
    """Request payload for /enterprise/embeddings/encode-with-embeddings."""
    document_id: str
    text: str
    segmentation_level: str = Field(default="sentence")
    action: str = Field(default="c2pa.created")
    previous_instance_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    c2pa_manifest_url: Optional[str] = None
    c2pa_manifest_hash: Optional[str] = None
    custom_assertions: Optional[List[Dict[str, Any]]] = None
    validate_assertions: bool = True
    digital_source_type: Optional[str] = None
    license: Optional[LicenseInfo] = None
    embedding_options: EmbeddingOptions = Field(default_factory=EmbeddingOptions)
    expires_at: Optional[datetime] = None


class EmbeddingInfo(BaseModel):
    """Information about a single embedded segment."""
    leaf_index: int
    leaf_hash: str
    text: Optional[str] = None
    ref_id: Optional[str] = None
    signature: Optional[str] = None
    embedding: Optional[str] = None
    verification_url: Optional[str] = None


class MerkleTreeInfo(BaseModel):
    """Merkle tree metadata attached to embeddings."""
    root_hash: str
    total_leaves: int
    tree_depth: int


class EncodeWithEmbeddingsResponse(BaseModel):
    """Response payload from embedding endpoint."""
    success: bool
    document_id: str
    merkle_tree: Optional[MerkleTreeInfo] = None
    embeddings: List[EmbeddingInfo]
    embedded_content: Optional[str] = None
    statistics: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
