"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class SignRequest(BaseModel):
    """Request model for signing content."""
    text: str = Field(..., description="Content to sign")
    document_title: Optional[str] = Field(None, description="Optional document title")
    document_url: Optional[str] = Field(None, description="Optional document URL")
    document_type: str = Field(default="article", description="Document type")
    custom_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata payload to persist alongside the manifest",
    )


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
