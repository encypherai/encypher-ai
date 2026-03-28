"""SQLAlchemy models for alert-service."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def _generate_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(64), primary_key=True, default=lambda: _generate_id("inc_"))
    fingerprint = Column(String(128), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="open", index=True)
    severity = Column(String(20), nullable=False, default="warning", index=True)
    title = Column(String(500), nullable=False)
    service_name = Column(String(100), index=True)
    endpoint = Column(String(500))
    error_code = Column(String(50))
    first_seen_at = Column(DateTime, nullable=False, server_default=func.now())
    last_seen_at = Column(DateTime, nullable=False, server_default=func.now())
    occurrence_count = Column(Integer, default=1)
    sample_error = Column(Text)
    sample_stack = Column(Text)
    sample_request_id = Column(String(64))
    sample_organization_id = Column(String(64))
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    events = relationship("AlertEvent", back_populates="incident", lazy="dynamic")
    notifications = relationship("NotificationLog", back_populates="incident", lazy="dynamic")


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id = Column(String(64), primary_key=True, default=lambda: _generate_id("evt_"))
    incident_id = Column(String(64), ForeignKey("incidents.id"), index=True)
    source = Column(String(50), nullable=False)
    raw_payload = Column(JSONB, nullable=False)
    status_code = Column(Integer)
    endpoint = Column(String(500))
    error_code = Column(String(50))
    error_message = Column(Text)
    service_name = Column(String(100), index=True)
    organization_id = Column(String(64))
    user_id = Column(String(64))
    request_id = Column(String(64))
    created_at = Column(DateTime, server_default=func.now(), index=True)

    incident = relationship("Incident", back_populates="events")


class NotificationLog(Base):
    __tablename__ = "notification_log"

    id = Column(String(64), primary_key=True, default=lambda: _generate_id("ntf_"))
    incident_id = Column(String(64), ForeignKey("incidents.id"), index=True)
    channel = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    payload = Column(JSONB)
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    incident = relationship("Incident", back_populates="notifications")
