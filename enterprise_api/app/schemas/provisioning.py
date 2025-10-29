"""
Pydantic schemas for auto-provisioning API keys and user accounts.

Supports provisioning from external services (API, SDK, WordPress plugin, etc.)
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, validator


# ============================================================================
# Auto-Provisioning Schemas
# ============================================================================

class ProvisioningSource(str):
    """Valid provisioning sources."""
    API = "api"
    SDK = "sdk"
    WORDPRESS = "wordpress"
    CLI = "cli"
    DASHBOARD = "dashboard"
    MOBILE_APP = "mobile_app"


class AutoProvisionRequest(BaseModel):
    """Request schema for auto-provisioning an organization and API key."""
    
    email: EmailStr = Field(
        ...,
        description="User email address",
        example="user@example.com"
    )
    organization_name: Optional[str] = Field(
        None,
        description="Organization name (auto-generated if not provided)",
        min_length=1,
        max_length=255,
        example="Acme Corp"
    )
    source: str = Field(
        ...,
        description="Source of the provisioning request",
        example="wordpress"
    )
    source_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata from the source",
        example={
            "plugin_version": "1.2.3",
            "site_url": "https://example.com",
            "wordpress_version": "6.4"
        }
    )
    tier: Optional[str] = Field(
        default="free",
        description="Initial tier (free/professional/enterprise)",
        example="free"
    )
    auto_activate: bool = Field(
        default=True,
        description="Whether to automatically activate the organization"
    )
    
    @validator('source')
    def validate_source(cls, v):
        """Validate provisioning source."""
        valid_sources = [
            ProvisioningSource.API,
            ProvisioningSource.SDK,
            ProvisioningSource.WORDPRESS,
            ProvisioningSource.CLI,
            ProvisioningSource.DASHBOARD,
            ProvisioningSource.MOBILE_APP
        ]
        if v not in valid_sources:
            raise ValueError(f"Invalid source. Must be one of: {', '.join(valid_sources)}")
        return v
    
    @validator('tier')
    def validate_tier(cls, v):
        """Validate tier."""
        valid_tiers = ['free', 'professional', 'enterprise']
        if v and v not in valid_tiers:
            raise ValueError(f"Invalid tier. Must be one of: {', '.join(valid_tiers)}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "developer@example.com",
                "organization_name": "Example Corp",
                "source": "wordpress",
                "source_metadata": {
                    "plugin_version": "1.2.3",
                    "site_url": "https://example.com"
                },
                "tier": "free",
                "auto_activate": True
            }
        }


class APIKeyResponse(BaseModel):
    """Response schema for API key."""
    
    api_key: str = Field(..., description="Generated API key")
    key_id: str = Field(..., description="API key identifier")
    organization_id: str = Field(..., description="Organization identifier")
    tier: str = Field(..., description="Organization tier")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp (if applicable)")
    
    class Config:
        schema_extra = {
            "example": {
                "api_key": "ency_live_1234567890abcdef",
                "key_id": "key_abc123",
                "organization_id": "org_xyz789",
                "tier": "free",
                "created_at": "2024-10-28T12:00:00Z",
                "expires_at": None
            }
        }


class AutoProvisionResponse(BaseModel):
    """Response schema for auto-provisioning."""
    
    success: bool = Field(..., description="Whether provisioning was successful")
    message: str = Field(..., description="Success or error message")
    organization_id: str = Field(..., description="Created organization ID")
    organization_name: str = Field(..., description="Organization name")
    user_id: Optional[str] = Field(None, description="Created user ID")
    api_key: APIKeyResponse = Field(..., description="Generated API key")
    tier: str = Field(..., description="Organization tier")
    features_enabled: Dict[str, bool] = Field(..., description="Enabled features")
    quota_limits: Dict[str, int] = Field(..., description="Quota limits")
    next_steps: Dict[str, str] = Field(..., description="Next steps and documentation links")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Organization and API key created successfully",
                "organization_id": "org_xyz789",
                "organization_name": "Example Corp",
                "user_id": "user_abc123",
                "api_key": {
                    "api_key": "ency_live_1234567890abcdef",
                    "key_id": "key_abc123",
                    "organization_id": "org_xyz789",
                    "tier": "free",
                    "created_at": "2024-10-28T12:00:00Z",
                    "expires_at": None
                },
                "tier": "free",
                "features_enabled": {
                    "merkle_trees": False,
                    "bulk_operations": False,
                    "advanced_analytics": False
                },
                "quota_limits": {
                    "api_calls_per_month": 1000,
                    "merkle_encoding_per_month": 0
                },
                "next_steps": {
                    "documentation": "https://docs.encypher.ai/getting-started",
                    "api_reference": "https://docs.encypher.ai/api",
                    "upgrade": "https://encypher.ai/pricing"
                }
            }
        }


# ============================================================================
# API Key Management Schemas
# ============================================================================

class APIKeyCreateRequest(BaseModel):
    """Request schema for creating an API key."""
    
    name: Optional[str] = Field(
        None,
        description="Friendly name for the API key",
        max_length=255,
        example="Production Key"
    )
    expires_in_days: Optional[int] = Field(
        None,
        description="Number of days until expiration (null for no expiration)",
        ge=1,
        le=365,
        example=90
    )
    scopes: Optional[list[str]] = Field(
        default=None,
        description="API scopes/permissions",
        example=["merkle:read", "merkle:write"]
    )


class APIKeyListResponse(BaseModel):
    """Response schema for listing API keys."""
    
    keys: list[Dict[str, Any]] = Field(..., description="List of API keys")
    total: int = Field(..., description="Total number of keys")


class APIKeyRevokeRequest(BaseModel):
    """Request schema for revoking an API key."""
    
    key_id: str = Field(..., description="API key identifier to revoke")
    reason: Optional[str] = Field(
        None,
        description="Reason for revocation",
        example="Key compromised"
    )


# ============================================================================
# User Account Schemas
# ============================================================================

class UserAccountCreateRequest(BaseModel):
    """Request schema for creating a user account."""
    
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(
        None,
        description="User's full name",
        max_length=255,
        example="John Doe"
    )
    organization_id: Optional[str] = Field(
        None,
        description="Organization to associate with (creates new if not provided)"
    )
    role: Optional[str] = Field(
        default="member",
        description="User role (owner/admin/member)",
        example="member"
    )
    send_welcome_email: bool = Field(
        default=True,
        description="Whether to send welcome email"
    )


class UserAccountResponse(BaseModel):
    """Response schema for user account."""
    
    user_id: str = Field(..., description="User identifier")
    email: str = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="User's full name")
    organization_id: str = Field(..., description="Associated organization")
    role: str = Field(..., description="User role")
    created_at: datetime = Field(..., description="Creation timestamp")
    is_active: bool = Field(..., description="Whether account is active")


# ============================================================================
# Webhook Schemas
# ============================================================================

class WebhookEventType(str):
    """Webhook event types."""
    ORGANIZATION_CREATED = "organization.created"
    API_KEY_CREATED = "api_key.created"
    API_KEY_REVOKED = "api_key.revoked"
    QUOTA_EXCEEDED = "quota.exceeded"
    QUOTA_WARNING = "quota.warning"
    TIER_UPGRADED = "tier.upgraded"


class WebhookPayload(BaseModel):
    """Webhook payload schema."""
    
    event_type: str = Field(..., description="Type of event")
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")
    organization_id: str = Field(..., description="Related organization")
