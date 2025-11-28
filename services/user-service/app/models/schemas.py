"""Pydantic schemas for User Service"""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    """Schema for updating profile"""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class ProfileResponse(BaseModel):
    """Schema for profile response"""
    id: str
    user_id: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    company: Optional[str]
    location: Optional[str]
    website: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TeamCreate(BaseModel):
    """Schema for creating team"""
    name: str
    description: Optional[str] = None


class TeamResponse(BaseModel):
    """Schema for team response"""
    id: str
    name: str
    owner_id: str
    description: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
