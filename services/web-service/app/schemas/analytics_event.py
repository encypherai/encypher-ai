from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# Properties to receive on creation - flexible to match marketing site
class AnalyticsEventCreate(BaseModel):
    """Schema for creating an analytics event from the marketing site."""
    event_name: str = Field(..., max_length=255, description="Event name")
    event_type: Optional[str] = Field(None, max_length=100, description="Event type")
    session_id: Optional[str] = Field(None, max_length=128, description="Session ID")
    page_url: Optional[str] = Field(None, description="Page URL")
    page_title: Optional[str] = Field(None, max_length=512, description="Page title")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    user_agent: Optional[str] = Field(None, description="User agent string")
    referrer: Optional[str] = Field(None, description="Referrer URL")
    properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional event properties"
    )


# Response schema
class AnalyticsEventResponse(BaseModel):
    """Schema for analytics event response."""
    success: bool
    message: str = "Event tracked successfully"
    event_id: Optional[UUID] = Field(default_factory=uuid4)

    class Config:
        from_attributes = True


# Properties stored in DB
class AnalyticsEventInDB(BaseModel):
    id: int
    event_id: UUID
    event_type: str
    event_name: str
    session_id: Optional[str]
    page_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
