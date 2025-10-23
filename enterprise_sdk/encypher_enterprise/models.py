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


class VerifyResponse(BaseModel):
    """Response model for verification operation."""
    success: bool
    is_valid: bool
    signer_id: str
    organization_name: str
    signature_timestamp: Optional[datetime] = None
    manifest: Dict[str, Any]
    tampered: bool


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
