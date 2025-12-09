"""
Pydantic schemas for Auth Service
"""

from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime


# TEAM_006: API Access Gating - Status enum (mirrors db model)
class ApiAccessStatus(str, Enum):
    """Status of a user's API access request"""

    NOT_REQUESTED = "not_requested"
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation"""

    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response - matches core_db schema"""

    id: str
    created_at: datetime
    is_active: bool = True
    email_verified: bool = False
    is_super_admin: bool = False  # TEAM_006: Super admin flag

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
    new_password: str = Field(..., min_length=8)


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
