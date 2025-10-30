"""Pydantic schemas for Notification Service"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class NotificationCreate(BaseModel):
    """Schema for creating a notification"""
    notification_type: str = Field(pattern="^(email|sms|webhook)$")
    recipient: str
    subject: Optional[str] = None
    content: str
    metadata: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: str
    user_id: str
    notification_type: str
    status: str
    recipient: str
    subject: Optional[str]
    sent_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
