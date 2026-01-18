"""
Pydantic request models for API validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class RightsMetadata(BaseModel):
    copyright_holder: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Copyright holder / publisher name",
    )
    license_url: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="URL to license terms",
    )
    usage_terms: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Human-readable usage terms",
    )
    syndication_allowed: Optional[bool] = Field(
        default=None,
        description="Whether downstream syndication is permitted",
    )
    embargo_until: Optional[datetime] = Field(
        default=None,
        description="Optional embargo end timestamp",
    )
    contact_email: Optional[str] = Field(
        default=None,
        max_length=320,
        description="Contact email for licensing",
    )


class SignRequest(BaseModel):
    """Request model for signing content."""

    text: str = Field(..., description="Content to sign", min_length=1, max_length=1000000)
    document_id: Optional[str] = Field(
        None,
        description="Optional custom document identifier",
        min_length=1,
        max_length=255,
    )
    document_title: Optional[str] = Field(None, max_length=500, description="Optional document title")
    document_url: Optional[str] = Field(None, max_length=1000, description="Optional document URL")
    document_type: str = Field(default="article", description="Document type: article | legal_brief | contract | ai_output")
    claim_generator: Optional[str] = Field(default=None, description="Optional claim generator identifier for C2PA manifests.")
    actions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional list of C2PA action assertions to include.")

    template_id: Optional[str] = Field(
        None,
        description="Optional assertion template to apply (Business+).",
    )

    validate_assertions: bool = Field(
        True,
        description="Whether to validate template-based assertions (Business+).",
    )

    rights: Optional[RightsMetadata] = Field(
        None,
        description="Optional rights metadata to embed (Business+).",
    )

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, v: str) -> str:
        """Validate document type."""
        allowed = ["article", "legal_brief", "contract", "ai_output"]
        if v not in allowed:
            raise ValueError(f"document_type must be one of: {', '.join(allowed)}")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "The Senate passed a landmark bill today. The vote was 67-33.",
                    "document_title": "Senate Passes Bill",
                    "document_type": "article",
                }
            ]
        }
    }


class VerifyRequest(BaseModel):
    """Request model for verifying signed content."""

    text: str = Field(..., description="Text with embedded C2PA manifest", min_length=1)

    model_config = {"json_schema_extra": {"examples": [{"text": "Signed content with invisible C2PA manifest..."}]}}


class LookupRequest(BaseModel):
    """Request model for sentence lookup."""

    sentence_text: str = Field(..., description="Sentence to look up", min_length=1)

    model_config = {"json_schema_extra": {"examples": [{"sentence_text": "The Senate passed a landmark bill today."}]}}
