from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base

class AnalyticsEvent(Base):
    """Model for tracking user interactions and events on the marketing site."""
    __tablename__ = "analytics_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Event identification
    event_type = Column(String(100), nullable=False, index=True)  # e.g., 'page_view', 'form_submission', 'button_click'
    event_name = Column(String(255), nullable=False)  # Human-readable name
    
    # Session and user tracking
    session_id = Column(String(100), index=True)  # Client-side session ID
    user_id = Column(String(100), index=True)     # If user is authenticated
    
    # Page context
    page_url = Column(Text, nullable=False)
    page_title = Column(String(512))
    referrer = Column(Text)
    
    # Device and browser info
    user_agent = Column(Text)
    ip_address = Column(String(45))  # IPv6 requires 45 chars
    device_type = Column(String(50))  # mobile, tablet, desktop
    browser = Column(String(50))
    os = Column(String(50))
    
    # Custom properties
    properties = Column(JSON)  # Flexible JSON field for additional event data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<AnalyticsEvent {self.event_type} - {self.session_id}>"
