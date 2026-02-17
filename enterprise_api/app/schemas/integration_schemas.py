"""
Pydantic schemas for CMS integration endpoints (Ghost, WordPress, etc.).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Ghost Integration CRUD
# =============================================================================


class GhostIntegrationCreate(BaseModel):
    """Request body for creating/updating a Ghost integration."""

    ghost_url: str = Field(
        ...,
        description="URL of the Ghost instance (e.g. https://myblog.ghost.io)",
        min_length=1,
        max_length=1000,
    )
    ghost_admin_api_key: str = Field(
        ...,
        description="Ghost Admin API key (format: {id}:{secret})",
        min_length=10,
        max_length=500,
    )
    auto_sign_on_publish: bool = Field(
        default=True,
        description="Automatically sign posts when published",
    )
    auto_sign_on_update: bool = Field(
        default=True,
        description="Automatically re-sign posts when updated",
    )
    manifest_mode: str = Field(
        default="micro",
        description="C2PA manifest mode for signing",
    )
    segmentation_level: str = Field(
        default="sentence",
        description="Text segmentation level for signing",
    )
    badge_enabled: bool = Field(
        default=True,
        description="Inject verification badge into posts",
    )

    @field_validator("ghost_url")
    @classmethod
    def validate_ghost_url(cls, v: str) -> str:
        v = v.rstrip("/")
        if not v.startswith(("http://", "https://")):
            raise ValueError("ghost_url must start with http:// or https://")
        return v

    @field_validator("ghost_admin_api_key")
    @classmethod
    def validate_admin_api_key(cls, v: str) -> str:
        if ":" not in v:
            raise ValueError("ghost_admin_api_key must be in format {id}:{secret}")
        parts = v.split(":")
        if len(parts) != 2 or len(parts[0]) < 10:
            raise ValueError("ghost_admin_api_key must be in format {id}:{secret} with valid id")
        return v

    @field_validator("manifest_mode")
    @classmethod
    def validate_manifest_mode(cls, v: str) -> str:
        valid = {
            "full", "lightweight_uuid", "minimal_uuid", "hybrid",
            "zw_embedding", "micro",
        }
        if v not in valid:
            raise ValueError(f"manifest_mode must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("segmentation_level")
    @classmethod
    def validate_segmentation_level(cls, v: str) -> str:
        valid = {"document", "sentence", "paragraph", "section"}
        if v not in valid:
            raise ValueError(f"segmentation_level must be one of: {', '.join(sorted(valid))}")
        return v


class GhostIntegrationResponse(BaseModel):
    """Response for Ghost integration config (key masked)."""

    id: str
    organization_id: str
    ghost_url: str
    ghost_admin_api_key_masked: str = Field(
        description="Masked Admin API key (only last 4 chars visible)",
    )
    auto_sign_on_publish: bool
    auto_sign_on_update: bool
    manifest_mode: str
    segmentation_level: str
    badge_enabled: bool
    is_active: bool
    webhook_url: str = Field(
        description="The ready-to-paste URL to configure in Ghost webhooks. Contains a scoped token (not your API key).",
    )
    webhook_token: Optional[str] = Field(
        default=None,
        description="Webhook token (ghwh_...). Only returned on creation or regeneration — store it now, it won't be shown again.",
    )
    last_webhook_at: Optional[datetime] = None
    last_sign_at: Optional[datetime] = None
    sign_count: str = "0"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GhostTokenRegenerateResponse(BaseModel):
    """Response after regenerating the webhook token."""

    webhook_url: str = Field(
        description="New webhook URL with the regenerated token. Update this in Ghost.",
    )
    webhook_token: str = Field(
        description="New webhook token (ghwh_...). Store it now — it won't be shown again.",
    )


# =============================================================================
# Ghost Webhook Payloads
# =============================================================================


class GhostWebhookPostCurrent(BaseModel):
    """The 'current' post object inside a Ghost webhook payload."""

    id: str
    title: Optional[str] = None
    status: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"extra": "allow"}


class GhostWebhookPayload(BaseModel):
    """
    Ghost webhook payload structure.

    Ghost sends: {"post": {"current": {...}, "previous": {...}}}
    or:          {"page": {"current": {...}, "previous": {...}}}
    """

    post: Optional[Dict[str, Any]] = None
    page: Optional[Dict[str, Any]] = None

    def get_resource_type(self) -> Optional[str]:
        if self.post is not None:
            return "post"
        if self.page is not None:
            return "page"
        return None

    def get_current(self) -> Optional[Dict[str, Any]]:
        resource = self.post or self.page
        if resource and isinstance(resource, dict):
            return resource.get("current")
        return None


class GhostManualSignRequest(BaseModel):
    """Request body for manually triggering signing of a Ghost post."""

    post_type: str = Field(
        default="post",
        description="Type of Ghost resource: 'post' or 'page'",
    )

    @field_validator("post_type")
    @classmethod
    def validate_post_type(cls, v: str) -> str:
        if v not in ("post", "page"):
            raise ValueError("post_type must be 'post' or 'page'")
        return v
