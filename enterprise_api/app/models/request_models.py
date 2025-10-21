"""
Pydantic request models for API validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class SignRequest(BaseModel):
    """Request model for signing content."""

    text: str = Field(
        ...,
        description="Content to sign",
        min_length=1,
        max_length=1000000
    )
    document_title: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional document title"
    )
    document_url: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional document URL"
    )
    document_type: str = Field(
        default="article",
        description="Document type: article | legal_brief | contract | ai_output"
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
                    "document_type": "article"
                }
            ]
        }
    }


class VerifyRequest(BaseModel):
    """Request model for verifying signed content."""

    text: str = Field(
        ...,
        description="Text with embedded C2PA manifest",
        min_length=1
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Signed content with invisible C2PA manifest..."
                }
            ]
        }
    }


class LookupRequest(BaseModel):
    """Request model for sentence lookup."""

    sentence_text: str = Field(
        ...,
        description="Sentence to look up",
        min_length=1
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sentence_text": "The Senate passed a landmark bill today."
                }
            ]
        }
    }
