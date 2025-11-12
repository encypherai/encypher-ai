"""
Pydantic response models for API responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class SignResponse(BaseModel):
    """Response model for signing operation."""

    success: bool = Field(..., description="Whether the operation was successful")
    document_id: str = Field(..., description="Unique document identifier")
    signed_text: str = Field(..., description="Text with embedded C2PA manifest")
    total_sentences: int = Field(..., description="Number of sentences signed")
    verification_url: str = Field(..., description="URL for public verification")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "document_id": "doc_abc123xyz",
                    "signed_text": "The Senate passed... [with invisible C2PA manifest]",
                    "total_sentences": 2,
                    "verification_url": "https://verify.encypherai.com/doc_abc123xyz"
                }
            ]
        }
    }


class ErrorDetail(BaseModel):
    """Standard API error object."""

    code: str = Field(..., description="Stable machine-readable error code")
    message: str = Field(..., description="Human readable error description")
    hint: Optional[str] = Field(None, description="Optional remediation hint")


class VerifyVerdict(BaseModel):
    """Detailed verification verdict data."""

    valid: bool = Field(..., description="Whether the signature is valid")
    tampered: bool = Field(..., description="Whether the payload was tampered")
    reason_code: str = Field(..., description="Reason code describing the verdict")
    signer_id: Optional[str] = Field(None, description="Resolved signer/organization ID")
    signer_name: Optional[str] = Field(None, description="Human readable signer name")
    timestamp: Optional[datetime] = Field(None, description="Signature timestamp, if present")
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured details (manifest, benchmarking stats, etc.)",
    )


class VerifyResponse(BaseModel):
    """Envelope returned by the verification endpoint."""

    success: bool = Field(..., description="Indicates if the request was processed successfully")
    data: Optional[VerifyVerdict] = Field(
        None,
        description="Verification verdict payload when success is true",
    )
    error: Optional[ErrorDetail] = Field(
        None,
        description="Error payload when success is false",
    )
    correlation_id: str = Field(..., description="Request correlation identifier for tracing")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "correlation_id": "req-123",
                    "data": {
                        "valid": True,
                        "tampered": False,
                        "reason_code": "OK",
                        "signer_id": "org_demo",
                        "signer_name": "Demo Org",
                        "timestamp": "2025-01-15T10:30:00Z",
                        "details": {"manifest": {"document_id": "doc-1"}},
                    },
                    "error": None,
                }
            ]
        }
    }


class LookupResponse(BaseModel):
    """Response model for sentence lookup operation."""

    success: bool = Field(..., description="Whether the operation was successful")
    found: bool = Field(..., description="Whether the sentence was found")
    document_title: Optional[str] = Field(None, description="Title of the document")
    organization_name: Optional[str] = Field(None, description="Name of the organization")
    publication_date: Optional[datetime] = Field(None, description="When the document was published")
    sentence_index: Optional[int] = Field(None, description="Index of the sentence in the document")
    document_url: Optional[str] = Field(None, description="URL of the original document")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "found": True,
                    "document_title": "Senate Passes Bill",
                    "organization_name": "Example Publisher",
                    "publication_date": "2025-01-15T10:00:00Z",
                    "sentence_index": 0,
                    "document_url": "https://example.com/article"
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Response model for API errors."""

    success: bool = Field(False, description="Always false for errors")
    error: Dict[str, Any] = Field(
        ...,
        description="Error details including code and message"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": False,
                    "error": {
                        "code": "INVALID_API_KEY",
                        "message": "The provided API key is invalid or expired"
                    }
                }
            ]
        }
    }
