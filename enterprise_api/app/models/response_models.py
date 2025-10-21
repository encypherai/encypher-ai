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


class VerifyResponse(BaseModel):
    """Response model for verification operation."""

    success: bool = Field(..., description="Whether the operation was successful")
    is_valid: bool = Field(..., description="Whether the signature is valid")
    signer_id: str = Field(..., description="Organization ID of the signer")
    organization_name: str = Field(..., description="Name of the signing organization")
    signature_timestamp: Optional[datetime] = Field(None, description="When the content was signed")
    manifest: Dict[str, Any] = Field(..., description="Full C2PA manifest details")
    tampered: bool = Field(..., description="Whether the content has been tampered with")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "is_valid": True,
                    "signer_id": "org_123",
                    "organization_name": "Example Publisher",
                    "signature_timestamp": "2025-01-15T10:30:00Z",
                    "manifest": {"version": "1.0", "signer": "org_123"},
                    "tampered": False
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
