from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from uuid import UUID

class DemoRequestStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    REJECTED = "rejected"

# Shared properties
class DemoRequestBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Full name of the requester")
    email: EmailStr = Field(..., description="Email address of the requester")
    organization: Optional[str] = Field(None, max_length=255, description="Company or organization name")
    role: Optional[str] = Field(None, max_length=100, description="Professional role or title")
    message: Optional[str] = Field(None, description="Additional message from the requester")
    source: Optional[str] = Field(None, max_length=100, description="Source of the demo request")
    consent: bool = Field(False, description="Whether the user consented to be contacted")

# Properties to receive on creation
class DemoRequestCreate(DemoRequestBase):
    pass

# Properties to receive on update (admin only)
class DemoRequestUpdate(BaseModel):
    status: Optional[DemoRequestStatus] = None
    notes: Optional[str] = Field(None, description="Internal notes about the demo request")

# Properties shared by models stored in DB
class DemoRequestInDBBase(DemoRequestBase):
    id: int
    uuid: UUID
    status: DemoRequestStatus = DemoRequestStatus.NEW
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Properties to return to client
class DemoRequest(DemoRequestInDBBase):
    pass

# Properties stored in DB
class DemoRequestInDB(DemoRequestInDBBase):
    pass
