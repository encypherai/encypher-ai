"""
Pydantic schemas for Key Service
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# API Key Schemas
class ApiKeyCreate(BaseModel):
    """Schema for creating an API key"""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    permissions: List[str] = Field(default=["sign", "verify", "read"])
    expires_at: Optional[datetime] = None
    organization_id: Optional[str] = None


class ApiKeyResponse(BaseModel):
    """Schema for API key response (with actual key - only shown once)"""

    id: str
    name: str
    key: str  # Only returned on creation
    fingerprint: str
    permissions: List[str]
    created_at: datetime
    organization_id: Optional[str] = None
    user_id: Optional[str] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class ApiKeyInfo(BaseModel):
    """Schema for API key info (without actual key)"""

    id: str
    name: str
    key_prefix: str  # e.g., "ency_abc..."
    fingerprint: str
    permissions: List[str]
    is_active: bool
    is_revoked: bool
    last_used_at: Optional[datetime]
    usage_count: int
    created_at: datetime
    expires_at: Optional[datetime]
    description: Optional[str]
    organization_id: Optional[str] = None
    user_id: Optional[str] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class ApiKeyUpdate(BaseModel):
    """Schema for updating an API key"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class ApiKeyVerify(BaseModel):
    """Schema for verifying an API key"""

    key: str


class ApiKeyVerifyResponse(BaseModel):
    """Schema for API key verification response"""

    valid: bool
    key_id: Optional[str] = None
    user_id: Optional[str] = None
    permissions: Optional[List[str]] = None
    message: Optional[str] = None


# Key Rotation Schemas
class KeyRotationRequest(BaseModel):
    """Schema for key rotation request"""

    reason: Optional[str] = None


class KeyRotationResponse(BaseModel):
    """Schema for key rotation response"""

    old_key_id: str
    new_key: ApiKeyResponse
    message: str


class RevokeKeysByUserRequest(BaseModel):
    """Schema for revoking all API keys for a user in an organization"""

    organization_id: str
    user_id: str


class RevokeKeysByUserResponse(BaseModel):
    """Schema for revoke-by-user response"""

    revoked_count: int


# Usage Schemas
class KeyUsageStats(BaseModel):
    """Schema for key usage statistics"""

    key_id: str
    total_requests: int
    last_used: Optional[datetime]
    requests_by_endpoint: dict
    requests_by_day: dict


# Response Schemas
class MessageResponse(BaseModel):
    """Generic message response"""

    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""

    detail: str
