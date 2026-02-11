"""
Pydantic schemas for Auth Service
"""

import re
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.config import settings


HTML_TAG_RE = re.compile(r"<[^>]+>")
URL_LIKE_RE = re.compile(r"(https?://|www\.)", re.IGNORECASE)


def canonicalize_email(value: str) -> str:
    cleaned = value.strip()
    if "@" not in cleaned:
        return cleaned.lower()
    local_part, domain_part = cleaned.split("@", 1)
    domain_part = domain_part.lower().strip()
    local_part = local_part.strip()
    if "+" in local_part:
        local_part = local_part.split("+", 1)[0]
    if domain_part in {"gmail.com", "googlemail.com"}:
        local_part = local_part.replace(".", "")
    return f"{local_part.lower()}@{domain_part}"


def sanitize_name(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = HTML_TAG_RE.sub("", value).strip()
    if URL_LIKE_RE.search(cleaned):
        raise ValueError("Name must not contain URLs")
    return cleaned


# TEAM_006: API Access Gating - Status enum (mirrors db model)
class ApiAccessStatus(str, Enum):
    """Status of a user's API access request"""

    NOT_REQUESTED = "not_requested"
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    SUSPENDED = "suspended"  # TEAM_164: Admin suspended - blocks all API access


class UserTier(str, Enum):
    """Available user tiers for admin updates.

    TEAM_145: Consolidated to free/enterprise/strategic_partner.
    """

    FREE = "free"
    ENTERPRISE = "enterprise"
    STRATEGIC_PARTNER = "strategic_partner"


class UserStatus(str, Enum):
    """User account status for admin updates."""

    ACTIVE = "active"
    SUSPENDED = "suspended"


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    name: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def canonicalize_email_field(cls, value: str) -> str:
        return canonicalize_email(value)

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name_field(cls, value: Optional[str]) -> Optional[str]:
        return sanitize_name(value)


class UserCreate(UserBase):
    """Schema for user creation"""

    password: str = Field(..., min_length=8, max_length=settings.AUTH_MAX_PASSWORD_LENGTH)


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr
    password: str = Field(..., max_length=settings.AUTH_MAX_PASSWORD_LENGTH)

    @field_validator("email", mode="before")
    @classmethod
    def canonicalize_email_field(cls, value: str) -> str:
        return canonicalize_email(value)


class UserResponse(UserBase):
    """Schema for user response - matches core_db schema"""

    id: str
    created_at: datetime
    is_active: bool = True
    email_verified: bool = False
    is_super_admin: bool = False  # TEAM_006: Super admin flag
    default_organization_id: Optional[str] = None  # TEAM_128: For billing service tier sync

    class Config:
        from_attributes = True


# Token Schemas
class Token(BaseModel):
    """Token response schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105 - OAuth2 token type, not a password


class TokenPayload(BaseModel):
    """Token payload schema"""

    sub: str  # user_id
    email: str
    exp: int
    type: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""

    refresh_token: str


# OAuth Schemas
class OAuthProvider(BaseModel):
    """OAuth provider schema"""

    provider: str = Field(..., pattern="^(google|github)$")
    code: str


class OAuthCallback(BaseModel):
    """OAuth callback schema"""

    provider: str
    code: str
    state: Optional[str] = None


class OAuthExchangeRequest(BaseModel):
    """Request body for OAuth token exchange from frontend"""

    provider: str = Field(..., pattern="^(google|github)$")
    id_token: Optional[str] = None  # For Google
    access_token: Optional[str] = None  # For Google/GitHub


# Email Verification Schemas
class EmailVerifyRequest(BaseModel):
    """Email verification request schema"""

    token: str


class ResendVerificationRequest(BaseModel):
    """Resend verification email request schema"""

    email: EmailStr


# Password Reset Schemas
class PasswordResetRequest(BaseModel):
    """Password reset request schema"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""

    token: str
    new_password: str = Field(..., min_length=8, max_length=settings.AUTH_MAX_PASSWORD_LENGTH)


# Response Schemas
class MessageResponse(BaseModel):
    """Generic message response"""

    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""

    detail: str


# ============================================
# TEAM_006: API Access Gating Schemas
# ============================================


class ApiAccessRequestCreate(BaseModel):
    """Request to gain API access - requires use case description"""

    use_case: str = Field(..., min_length=20, max_length=2000, description="Describe how you plan to use the API (min 20 characters)")

    @field_validator("use_case")
    @classmethod
    def validate_use_case(cls, v: str) -> str:
        """Ensure use case is meaningful"""
        if len(v.strip()) < 20:
            raise ValueError("Use case must be at least 20 characters")
        return v.strip()


class ApiAccessStatusResponse(BaseModel):
    """Response with current API access status"""

    status: ApiAccessStatus
    requested_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    use_case: Optional[str] = None
    denial_reason: Optional[str] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True


class ApiAccessApproval(BaseModel):
    """Admin request to approve API access"""

    user_id: str = Field(..., description="ID of the user to approve")


class ApiAccessDenial(BaseModel):
    """Admin request to deny API access"""

    user_id: str = Field(..., description="ID of the user to deny")
    reason: str = Field(..., min_length=10, max_length=500, description="Reason for denial")


class PendingAccessRequest(BaseModel):
    """A pending API access request for admin review"""

    user_id: str
    email: str
    name: Optional[str] = None
    use_case: str
    requested_at: datetime

    class Config:
        from_attributes = True


class PendingAccessRequestList(BaseModel):
    """List of pending API access requests"""

    requests: List[PendingAccessRequest]
    total: int


# ============================================
# Admin User Updates
# ============================================


class TierUpdateRequest(BaseModel):
    """Request to update a user's tier."""

    user_id: str = Field(..., description="User ID to update")
    new_tier: UserTier = Field(..., description="New tier to assign")
    reason: Optional[str] = Field(None, description="Reason for tier change")


class TierUpdateResponse(BaseModel):
    """Response for tier update."""

    success: bool = True
    data: dict = Field(default_factory=dict)


class UserStatusUpdateRequest(BaseModel):
    """Request to update a user's status."""

    user_id: str = Field(..., description="User ID to update")
    status: UserStatus = Field(..., description="New account status")
    reason: Optional[str] = Field(None, description="Reason for status change")


class UserStatusUpdateResponse(BaseModel):
    """Response for status update."""

    success: bool = True
    data: dict = Field(default_factory=dict)


# TEAM_164: Admin API Access Status Management
class ApiAccessStatusSetRequest(BaseModel):
    """Admin request to directly set a user's API access status."""

    user_id: str = Field(..., description="ID of the user to update")
    status: ApiAccessStatus = Field(..., description="New API access status")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")


class ApiAccessStatusSetResponse(BaseModel):
    """Response for API access status set."""

    success: bool = True
    data: dict = Field(default_factory=dict)


class RoleUpdateRequest(BaseModel):
    """Request to update a user's role within an organization."""

    user_id: str = Field(..., description="User ID to update")
    new_role: str = Field(..., description="New role to assign (member, manager, admin)")


class RoleUpdateResponse(BaseModel):
    """Response for role update."""

    success: bool = True
    data: dict = Field(default_factory=dict)
