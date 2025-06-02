"""
Audit log model for storing verification results.
"""
from sqlalchemy import Column, Integer, String, Boolean, JSON, Text, DateTime
from sqlalchemy.sql import func

from app.core.database import Base

class AuditLog(Base):
    """Audit log model for storing verification results."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)  # File path or text source identifier
    is_verified = Column(Boolean, default=False)
    status = Column(String)  # VERIFIED, UNVERIFIED, ERROR
    verification_time = Column(DateTime(timezone=True), server_default=func.now())
    event_data = Column(JSON, nullable=True)  # Extracted metadata or other event-specific data as JSON
    error_message = Column(Text, nullable=True)  # Error message if verification failed
    model_id = Column(String, nullable=True, index=True)  # AI model ID from metadata
    
    # Additional fields for filtering and reporting
    source_type = Column(String, nullable=True)  # File, API, etc.
    department = Column(String, nullable=True, index=True)  # Department from metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
