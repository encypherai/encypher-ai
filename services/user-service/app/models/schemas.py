"""Pydantic schemas for User Service"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class _OrmBase(BaseModel):
    """Shared base for ORM-backed response schemas."""

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list response envelope."""

    items: List[T]
    total: int
    page: int
    page_size: int
    next_page: Optional[int] = None


class ProfileUpdate(BaseModel):
    """Schema for updating profile"""

    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class ProfileResponse(_OrmBase):
    """Schema for profile response"""

    id: str
    user_id: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime


class TeamCreate(BaseModel):
    """Schema for creating team"""

    name: str
    description: Optional[str] = None


class TeamResponse(_OrmBase):
    """Schema for team response"""

    id: str
    name: str
    owner_id: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
