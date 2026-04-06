"""Pydantic schemas for CDN Edge Provenance Worker signing endpoints."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Provisioning
# ---------------------------------------------------------------------------


class CdnProvisionRequest(BaseModel):
    """Request body for CDN domain auto-provisioning."""

    domain: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Publisher domain (eTLD+1) detected by the worker.",
    )
    worker_version: Optional[str] = Field(
        default=None,
        max_length=32,
        description="Worker release version for telemetry.",
    )


class CdnProvisionResponse(BaseModel):
    """Response from CDN domain provisioning."""

    success: bool
    org_id: str
    domain_token: str
    dashboard_url: str
    claim_url: str


# ---------------------------------------------------------------------------
# Signing
# ---------------------------------------------------------------------------


class EmbeddingPlanOperation(BaseModel):
    """Single marker insertion operation."""

    insert_after_index: int
    marker: str


class EmbeddingPlanSchema(BaseModel):
    """Index-based marker insertion plan returned to the worker."""

    index_unit: str = "codepoint"
    operations: List[EmbeddingPlanOperation] = Field(default_factory=list)


class CdnSignRequest(BaseModel):
    """Request body for CDN content signing."""

    text: str = Field(
        ...,
        min_length=50,
        max_length=50_000,
        description="Article text extracted from the HTML by the edge worker.",
    )
    page_url: str = Field(
        ...,
        min_length=1,
        max_length=2048,
        description="Canonical URL of the page.",
    )
    org_id: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Organization ID from provisioning. If omitted, domain is used to resolve org.",
    )
    document_title: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Page title from the HTML <title> tag.",
    )
    boundary_selector: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Which content detection method the worker used (for analytics).",
    )


class CdnSignResponse(BaseModel):
    """Response from CDN content signing."""

    success: bool
    embedding_plan: Optional[EmbeddingPlanSchema] = None
    document_id: Optional[str] = None
    verification_url: Optional[str] = None
    content_hash: Optional[str] = None
    org_id: Optional[str] = None
    signer_tier: str = "encypher_free"
    signed_at: Optional[str] = None
    cached: bool = False
    error: Optional[str] = None
    upgrade_url: Optional[str] = None


# ---------------------------------------------------------------------------
# Claiming
# ---------------------------------------------------------------------------


class CdnClaimRequest(BaseModel):
    """Request body for domain claim initiation."""

    org_id: str = Field(
        ...,
        max_length=64,
        description="Organization ID to claim.",
    )
    email: str = Field(
        ...,
        max_length=320,
        description="Email address for account creation.",
    )
