"""
Pydantic schemas for CDN integration endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CdnIntegrationCreate(BaseModel):
    """Request body for creating or updating a CDN integration."""

    provider: str = Field(default="cloudflare", description="CDN provider slug (cloudflare | fastly | cloudfront)")
    zone_id: Optional[str] = Field(default=None, description="Cloudflare Zone ID (optional; used for setup hints)")
    webhook_secret: str = Field(
        min_length=16,
        max_length=256,
        description="Shared secret to authenticate Logpush requests (stored hashed)",
    )
    enabled: bool = Field(default=True)


class CdnIntegrationResponse(BaseModel):
    """Response schema for CDN integration config."""

    id: str
    provider: str
    zone_id: Optional[str]
    enabled: bool
    created_at: datetime
    updated_at: datetime
    # Webhook URL hint shown in the dashboard so publisher can paste into Cloudflare
    webhook_url: str


class LogpushIngestResult(BaseModel):
    """Result of a Logpush batch ingestion."""

    lines_received: int
    bots_detected: int
    bypass_flags: int
    events_created: int
    errors: int


# ---------------------------------------------------------------------------
# CDN Provenance schemas
# ---------------------------------------------------------------------------


class CdnImageSignResponse(BaseModel):
    """Response for POST /cdn/images/sign."""

    record_id: str
    manifest_url: str
    image_id: str
    phash: Optional[int] = None
    sha256: Optional[str] = None
    signed_image_b64: str
    mime_type: str


class CdnImageRegisterResponse(BaseModel):
    """Response for POST /cdn/images/register."""

    record_id: str
    phash: Optional[int] = None
    sha256: Optional[str] = None


class CdnManifestResponse(BaseModel):
    """Response for GET /cdn/manifests/{record_id}."""

    record_id: str
    manifest: Optional[dict] = None
    manifest_url: str


class CdnManifestLookupResponse(BaseModel):
    """Response for GET /cdn/manifests/lookup?url=..."""

    record_id: str
    manifest_url: str
    original_url: Optional[str] = None


class CdnVariantsRequest(BaseModel):
    """Request body for POST /cdn/images/{record_id}/variants."""

    transforms: list[str]


class CdnVariantsResponse(BaseModel):
    """Response for POST /cdn/images/{record_id}/variants."""

    parent_record_id: str
    variant_count: int
    variant_ids: list[str]


class CdnVerifyResponse(BaseModel):
    """Response for POST /cdn/verify and POST /cdn/verify/url."""

    verdict: str  # ORIGINAL_SIGNED | VERIFIED_DERIVATIVE | PROVENANCE_LOST
    verification_path: str  # EMBEDDED | PHASH_SIDECAR | URL_LOOKUP | NONE
    record_id: Optional[str] = None
    manifest: Optional[dict] = None
    hamming_distance: Optional[int] = None
    confidence: Optional[float] = None


class CdnWorkerConfigResponse(BaseModel):
    """Response for POST /cdn/integrations/{id}/generate-worker-config."""

    worker_script: str
    wrangler_toml: str
    integration_id: str


# ---------------------------------------------------------------------------
# CDN Analytics schemas
# ---------------------------------------------------------------------------


class CdnAnalyticsSummary(BaseModel):
    organization_id: str
    assets_protected: int
    variants_registered: int
    image_requests_tracked: int
    recoverable_percent: float  # 0-100


class CdnAnalyticsTimelineDay(BaseModel):
    date: str  # YYYY-MM-DD
    images_signed: int
    image_requests: int


class CdnAnalyticsTimeline(BaseModel):
    days: int
    data: list[CdnAnalyticsTimelineDay]
