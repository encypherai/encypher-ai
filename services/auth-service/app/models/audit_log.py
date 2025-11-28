"""
Audit log model for tracking security-critical operations.
"""
from sqlalchemy import Column, String, DateTime, JSON, Integer, Index
from datetime import datetime
from .base import Base


class AuditLog(Base):
    """
    Audit log for tracking all security-critical operations.
    
    This table records:
    - Who performed the action (user_id, organization_id)
    - What action was performed (action, resource_type, resource_id)
    - When it was performed (timestamp)
    - Where it came from (ip_address, user_agent)
    - How it went (result, error_message)
    - Additional context (details, request_id)
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Who
    user_id = Column(String, nullable=True, index=True)
    organization_id = Column(String, nullable=True, index=True)

    # What
    action = Column(String, nullable=False, index=True)  # e.g., "user.login", "document.sign"
    resource_type = Column(String, nullable=False, index=True)  # e.g., "user", "document", "api_key"
    resource_id = Column(String, nullable=True)

    # Where
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # Context
    request_id = Column(String, nullable=True, index=True)
    details = Column(JSON, nullable=True)  # Additional context as JSON

    # Result
    result = Column(String, nullable=False, index=True)  # "success" or "failure"
    error_message = Column(String, nullable=True)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_org_action', 'organization_id', 'action'),
        Index('idx_audit_timestamp_result', 'timestamp', 'result'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, result={self.result})>"
