"""
Admin API Schemas

Pydantic models for admin endpoints:
- User management (list, stats, tier changes)
- Error logs viewing
- BYOK public key registration
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


# =============================================================================
# Enums
# =============================================================================


class UserTier(str, Enum):
    """Available user tiers."""

    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    STRATEGIC_PARTNER = "strategic_partner"


class UserStatus(str, Enum):
    """User account status."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"


# =============================================================================
# User Management Schemas
# =============================================================================


class AdminUserInfo(BaseModel):
    """User information for admin view."""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: Optional[str] = Field(None, description="User display name")
    tier: str = Field(..., description="Current tier (starter, professional, business, enterprise)")
    status: str = Field(default="active", description="Account status")
    organization_id: Optional[str] = Field(None, description="Organization ID if part of org")
    organization_name: Optional[str] = Field(None, description="Organization name")

    # Usage stats
    api_calls_this_month: int = Field(default=0, description="API calls this billing period")
    documents_signed: int = Field(default=0, description="Total documents signed")
    monthly_quota: int = Field(default=10000, description="Monthly API quota")

    # Key info
    api_key_count: int = Field(default=0, description="Number of active API keys")

    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Account creation date")
    last_active_at: Optional[datetime] = Field(None, description="Last API activity")

    # Features
    features: Dict[str, Any] = Field(default_factory=dict, description="Enabled features")

    class Config:
        from_attributes = True


class AdminUserListResponse(BaseModel):
    """Response for admin user list endpoint."""

    success: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {"example": {"success": True, "data": {"users": [], "total": 0, "page": 1, "page_size": 50}}}


class AdminStatsResponse(BaseModel):
    """Response for admin platform stats endpoint."""

    success: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "total_users": 100,
                    "active_users": 85,
                    "paying_customers": 20,
                    "mrr": 5000,
                    "total_api_calls": 150000,
                    "users_by_tier": {"starter": 60, "professional": 25, "business": 10, "enterprise": 5},
                },
            }
        }


# =============================================================================
# Tier Management Schemas
# =============================================================================


class TierUpdateRequest(BaseModel):
    """Request to update a user's tier."""

    user_id: str = Field(..., description="User ID to update")
    new_tier: UserTier = Field(..., description="New tier to assign")
    reason: Optional[str] = Field(None, description="Reason for tier change (for audit log)")

    class Config:
        json_schema_extra = {"example": {"user_id": "user_abc123", "new_tier": "enterprise", "reason": "Upgraded per sales agreement"}}


class TierUpdateResponse(BaseModel):
    """Response for tier update."""

    success: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"user_id": "user_abc123", "previous_tier": "professional", "new_tier": "enterprise", "updated_at": "2024-12-23T22:00:00Z"},
            }
        }


# =============================================================================
# Error Logs Schemas
# =============================================================================


class ErrorLogEntry(BaseModel):
    """Single error log entry."""

    id: str = Field(..., description="Error log ID")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    endpoint: str = Field(..., description="API endpoint that errored")
    method: str = Field(..., description="HTTP method")
    status_code: int = Field(..., description="HTTP status code returned")
    error_code: Optional[str] = Field(None, description="Application error code")
    error_message: str = Field(..., description="Error message")
    request_id: Optional[str] = Field(None, description="Correlation/request ID")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    timestamp: datetime = Field(..., description="When the error occurred")

    class Config:
        from_attributes = True


class ErrorLogsResponse(BaseModel):
    """Response for error logs endpoint."""

    success: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {"example": {"success": True, "data": {"logs": [], "total": 0, "page": 1, "page_size": 50}}}


# =============================================================================
# BYOK Public Key Registration Schemas
# =============================================================================


class PublicKeyRegisterRequest(BaseModel):
    """Request to register a BYOK public key."""

    public_key_pem: str = Field(..., description="PEM-encoded public key (Ed25519 or RSA)", min_length=50)
    key_name: Optional[str] = Field(None, description="Friendly name for the key")
    key_algorithm: str = Field(default="Ed25519", description="Key algorithm (Ed25519, RSA-2048, RSA-4096)")

    @validator("public_key_pem")
    def validate_pem_format(cls, v):
        if not v.strip().startswith("-----BEGIN"):
            raise ValueError("Public key must be in PEM format")
        return v.strip()

    @validator("key_algorithm")
    def validate_algorithm(cls, v):
        allowed = ["Ed25519", "RSA-2048", "RSA-4096"]
        if v not in allowed:
            raise ValueError(f"Algorithm must be one of: {', '.join(allowed)}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEA...\n-----END PUBLIC KEY-----",
                "key_name": "Production Signing Key",
                "key_algorithm": "Ed25519",
            }
        }


class PublicKeyInfo(BaseModel):
    """Information about a registered public key."""

    id: str = Field(..., description="Key ID")
    organization_id: str = Field(..., description="Organization that owns this key")
    key_name: Optional[str] = Field(None, description="Friendly name")
    key_algorithm: str = Field(..., description="Key algorithm")
    key_fingerprint: str = Field(..., description="SHA-256 fingerprint of the public key")
    public_key_pem: str = Field(..., description="PEM-encoded public key")
    is_active: bool = Field(default=True, description="Whether key is active for verification")
    created_at: datetime = Field(..., description="When key was registered")
    last_used_at: Optional[datetime] = Field(None, description="Last verification using this key")

    class Config:
        from_attributes = True


class PublicKeyRegisterResponse(BaseModel):
    """Response for public key registration."""

    success: bool = True
    data: Optional[PublicKeyInfo] = None
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "id": "pk_abc123",
                    "organization_id": "org_xyz789",
                    "key_name": "Production Signing Key",
                    "key_algorithm": "Ed25519",
                    "key_fingerprint": "SHA256:abc123...",
                    "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
                    "is_active": True,
                    "created_at": "2024-12-23T22:00:00Z",
                },
            }
        }


class PublicKeyListResponse(BaseModel):
    """Response for listing organization's public keys."""

    success: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {"example": {"success": True, "data": {"keys": [], "total": 0}}}


# =============================================================================
# User Status Update Schemas
# =============================================================================


class UserStatusUpdateRequest(BaseModel):
    """Request to update user status (suspend/activate)."""

    user_id: str = Field(..., description="User ID to update")
    status: UserStatus = Field(..., description="New status")
    reason: Optional[str] = Field(None, description="Reason for status change")

    class Config:
        json_schema_extra = {"example": {"user_id": "user_abc123", "status": "suspended", "reason": "Terms of service violation"}}


class UserStatusUpdateResponse(BaseModel):
    """Response for user status update."""

    success: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)
