"""Unified verification request/response schemas.

TEAM_273: Single schema set for POST /api/v1/verify, replacing the
fragmented per-media-type schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.batch import SegmentationLevel

# Valid search scopes for verification
SearchScope = Literal["organization", "public", "all"]


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class VerifyOptions(BaseModel):
    """Feature flags for verification -- tier-gated like SignOptions."""

    # Tamper detection
    include_tamper_localization: bool = False
    segmentation_level: SegmentationLevel = "sentence"

    # Attribution & plagiarism
    include_attribution: bool = False
    detect_plagiarism: bool = False
    include_heat_map: bool = False
    min_match_percentage: float = 0.0

    # Fuzzy search (Enterprise)
    fuzzy_search: bool = False
    fuzzy_similarity_threshold: float = 0.82
    fuzzy_max_candidates: int = 20
    fuzzy_fallback_when_no_binding: bool = True

    # Search scope (Enterprise)
    search_scope: SearchScope = "organization"

    # Print leak detection (cheap, on by default)
    detect_print_fingerprint: bool = True

    # Print micro ECC detection (cheap, on by default)
    detect_print_micro_ecc: bool = True


class VerifyDocument(BaseModel):
    """One item in a batch verify request."""

    text: str
    document_id: Optional[str] = None


class UnifiedVerifyRequest(BaseModel):
    """JSON body for POST /api/v1/verify.

    Exactly one of ``text`` or ``documents`` must be provided.
    Binary media uses the multipart/form-data route instead.
    """

    text: Optional[str] = None
    document_id: Optional[str] = None
    documents: Optional[List[VerifyDocument]] = None
    options: VerifyOptions = Field(default_factory=VerifyOptions)

    @model_validator(mode="after")
    def _exactly_one_input(self) -> "UnifiedVerifyRequest":
        has_text = self.text is not None
        has_docs = self.documents is not None and len(self.documents) > 0
        if has_text == has_docs:
            raise ValueError("Provide exactly one of 'text' (single) or 'documents' (batch).")
        return self

    def get_documents(self) -> List[VerifyDocument]:
        """Normalize single/batch into a list."""
        if self.documents:
            return self.documents
        return [VerifyDocument(text=self.text, document_id=self.document_id)]  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class SignerInfo(BaseModel):
    """Unified signer identity -- replaces the two incompatible
    SignerIdentity classes in embeddings.py and rich_verify_schemas.py."""

    organization_id: str
    organization_name: Optional[str] = None
    trust_level: Optional[str] = None
    certificate_status: Optional[str] = None
    ca_backed: Optional[bool] = None


class ContentInfo(BaseModel):
    """Content verification details (fields populated vary by media type)."""

    # Common
    hash_verified: Optional[bool] = None
    c2pa_manifest_valid: Optional[bool] = None
    c2pa_instance_id: Optional[str] = None

    # Text-specific
    manifest_mode: Optional[str] = None
    embeddings_found: Optional[int] = None
    leaf_hash_verified: Optional[bool] = None

    # Media-specific
    db_matched: Optional[bool] = None
    document_id: Optional[str] = None

    # C2PA manifest (all types)
    manifest_data: Optional[Dict[str, Any]] = None


class UnifiedVerifyResponse(BaseModel):
    """Standard envelope for all verification results."""

    success: bool
    valid: bool
    tampered: bool = False
    reason_code: str
    media_type: str  # text, image, audio, video
    verified_at: datetime

    signer: Optional[SignerInfo] = None
    content: Optional[ContentInfo] = None
    details: Dict[str, Any] = Field(default_factory=dict)

    error: Optional[str] = None
    correlation_id: str
