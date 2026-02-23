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
