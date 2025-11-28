import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class DemoRequest(Base):
    """Model for tracking demo requests from the marketing site."""
    __tablename__ = "demo_requests"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    organization = Column(String(255))
    role = Column(String(100))
    message = Column(Text)
    source = Column(String(100))  # e.g., 'website', 'landing-page', etc.

    # Contact consent
    consent = Column(Boolean, default=False)

    # Status tracking
    status = Column(String(50), default="new")  # new, contacted, scheduled, completed, rejected
    notes = Column(Text)

    # Analytics
    ip_address = Column(String(45))  # IPv6 requires 45 chars
    user_agent = Column(Text)
    referrer = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<DemoRequest {self.email} - {self.status}>"
