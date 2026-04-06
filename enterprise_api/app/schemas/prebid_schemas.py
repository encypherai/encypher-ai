"""Pydantic schemas for Prebid auto-provenance signing endpoints."""

from typing import Optional

from pydantic import BaseModel, Field


class PrebidSignRequest(BaseModel):
    """Request body for Prebid auto-sign endpoint."""

    text: str = Field(
        ...,
        min_length=50,
        max_length=50_000,
        description="Article text extracted from the DOM by the RTD module.",
    )
    page_url: str = Field(
        ...,
        min_length=1,
        max_length=2048,
        description="Canonical URL of the page.",
    )
    document_title: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Page title from document.title.",
    )


class PrebidSignResponse(BaseModel):
    """Response from Prebid auto-sign endpoint."""

    success: bool
    manifest_url: Optional[str] = None
    signer_tier: str = "encypher_free"
    signed_at: Optional[str] = None
    content_hash: Optional[str] = None
    org_id: Optional[str] = None
    cached: bool = False
    error: Optional[str] = None
    upgrade_url: Optional[str] = None
