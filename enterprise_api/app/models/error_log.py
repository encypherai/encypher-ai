"""
Error Log model for tracking API errors.

Stores error information for admin monitoring and debugging.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class ErrorLog(Base):
    """
    Error log entry for tracking API errors.
    
    Used by admin dashboard to view and analyze errors.
    """
    __tablename__ = "error_logs"
    __table_args__ = {"extend_existing": True}

    id = Column(String(64), primary_key=True)
    
    # User/org context (nullable for unauthenticated requests)
    user_id = Column(String(64), nullable=True, index=True)
    organization_id = Column(String(64), nullable=True, index=True)
    api_key_id = Column(String(64), nullable=True)
    
    # Request info
    endpoint = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)
    
    # Error details
    status_code = Column(Integer, nullable=False, index=True)
    error_code = Column(String(50), nullable=True, index=True)
    error_message = Column(Text, nullable=False)
    error_details = Column(Text, nullable=True)
    
    # Request metadata
    request_id = Column(String(64), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    timestamp = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.utcnow,
        server_default=func.now(),
        index=True
    )

    def __repr__(self) -> str:
        return f"<ErrorLog(id={self.id}, endpoint={self.endpoint}, status={self.status_code})>"
