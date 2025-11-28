"""SQLAlchemy database models for Notification Service"""
import uuid

from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Notification(Base):
    """Notification model"""
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)

    notification_type = Column(String, nullable=False, index=True)  # email, sms, webhook
    status = Column(String, nullable=False, index=True)  # pending, sent, failed

    recipient = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    content = Column(String, nullable=False)

    sent_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)

    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type}, status={self.status})>"
