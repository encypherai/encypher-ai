"""
Pydantic schemas for Auth Service
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


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
