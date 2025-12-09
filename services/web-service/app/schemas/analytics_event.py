from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# Properties to receive on creation - flexible to match marketing site
class AnalyticsEventCreate(BaseModel):
    """Schema for creating an analytics event from the marketing site."""
    event_name: str = Field(..., max_length=255, description="Event name")
    event_type: str | None = Field(None, max_length=100, description="Event type")
    session_id: str | None = Field(None, max_length=128, description="Session ID")
    page_url: str | None = Field(None, description="Page URL")
    page_title: str | None = Field(None, max_length=512, description="Page title")
    user_id: str | None = Field(None, description="User ID if authenticated")
    user_agent: str | None = Field(None, description="User agent string")
    referrer: str | None = Field(None, description="Referrer URL")
    properties: dict[str, Any] | None = Field(
        default_factory=dict,
        description="Additional event properties"
    )


# Response schema
class AnalyticsEventResponse(BaseModel):
    """Schema for analytics event response."""
    success: bool
    message: str = "Event tracked successfully"
    event_id: UUID | None = Field(default_factory=uuid4)

    class Config:
        from_attributes = True


# Properties stored in DB
class AnalyticsEventInDB(BaseModel):
    id: int
    event_id: UUID
    event_type: str
    event_name: str
    session_id: str | None
    page_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True
