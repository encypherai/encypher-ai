from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID, uuid4
from enum import Enum

class AnalyticsEventType(str, Enum):
    PAGE_VIEW = "page_view"
    BUTTON_CLICK = "button_click"
    FORM_SUBMISSION = "form_submission"
    DEMO_REQUEST = "demo_request"
    DOWNLOAD = "download"
    EXTERNAL_LINK = "external_link"
    SCROLL = "scroll"
    CUSTOM = "custom"

class DeviceType(str, Enum):
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"

# Shared properties
class AnalyticsEventBase(BaseModel):
    event_type: AnalyticsEventType = Field(..., description="Type of the event")
    event_name: str = Field(..., max_length=255, description="Human-readable name of the event")
    session_id: str = Field(..., description="Client-side session ID")
    
    # Page context
    page_url: str = Field(..., description="URL of the page where the event occurred")
    page_title: Optional[str] = Field(None, max_length=512, description="Title of the page")
    
    # User context
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    
    # Device and browser info (can be auto-detected on the client side)
    user_agent: Optional[str] = Field(None, description="User agent string")
    ip_address: Optional[str] = Field(None, description="IP address of the user")
    device_type: Optional[DeviceType] = Field(None, description="Type of device")
    browser: Optional[str] = Field(None, description="Browser name and version")
    os: Optional[str] = Field(None, description="Operating system")
    
    # Referrer information
    referrer: Optional[str] = Field(None, description="Referrer URL")
    
    # Custom properties
    properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional properties specific to this event"
    )

# Properties to receive on creation
class AnalyticsEventCreate(AnalyticsEventBase):
    # Override event_type to be optional in the create schema
    # as it will be set by the endpoint based on the route
    event_type: Optional[AnalyticsEventType] = None

# Properties to receive on update
class AnalyticsEventUpdate(BaseModel):
    pass

# Properties to return to client
class AnalyticsEventResponse(BaseModel):
    event_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the event")
    received_at: datetime = Field(default_factory=datetime.utcnow, description="Server timestamp when event was received")
    
    class Config:
        from_attributes = True

# Properties stored in DB
class AnalyticsEventInDB(AnalyticsEventBase):
    id: int
    event_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True
