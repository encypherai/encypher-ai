"""SAML configuration model for SSO."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, JSON

from .models import Base


class SamlConfig(Base):
    __tablename__ = "saml_configs"

    id = Column(String(64), primary_key=True)
    organization_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    idp_entity_id = Column(String(512), nullable=False)
    idp_sso_url = Column(String(1024), nullable=False)
    idp_certificate = Column(Text, nullable=False)
    attribute_mapping = Column(JSON, nullable=True, default=dict)
    enabled = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
