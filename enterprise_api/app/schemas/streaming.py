"""Schemas for streaming endpoints."""
from typing import Optional

from pydantic import BaseModel, Field


class StreamSignRequest(BaseModel):
    """Request payload for streaming signing run."""

    text: str = Field(..., description="Content to sign while streaming progress")
    document_id: Optional[str] = Field(None, description="Optional document identifier")
    document_title: Optional[str] = Field(None, description="Optional title")
    document_type: str = Field("article", description="Document type metadata")
    run_id: Optional[str] = Field(None, description="Client-supplied run identifier for retries")
