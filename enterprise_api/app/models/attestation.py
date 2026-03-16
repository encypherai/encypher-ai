"""SQLAlchemy models for attestation policies and attestation records.

Maps to tables created by migrations:
- 20260228_100000_add_attestations
- 20260228_200000_add_attestation_policies
- 20260302_100000_add_attestation_original_text
"""

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import Base


class AttestationPolicy(Base):
    """Compliance policy rules governing attestation workflows.

    Per-organization scoping with configurable enforcement (warn/block/audit).
    """

    __tablename__ = "attestation_policies"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    rules = Column(JSONB, nullable=False, default=list)
    enforcement = Column(String(20), nullable=False, default="warn")
    scope = Column(String(30), nullable=False, default="all")
    scope_value = Column(String(255), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AttestationPolicy(id={self.id}, name={self.name}, enforcement={self.enforcement})>"


class Attestation(Base):
    """AI content attestation record linking reviewer/model metadata to provenance."""

    __tablename__ = "attestations"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    document_id = Column(String(255), nullable=False)
    attestation_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    reviewer_identity = Column(String(255), nullable=True)
    reviewer_role = Column(String(100), nullable=True)
    model_name = Column(String(255), nullable=True)
    model_version = Column(String(100), nullable=True)
    model_provider = Column(String(255), nullable=True)
    prompt_hash = Column(String(64), nullable=True)
    human_reviewed = Column(Boolean, nullable=False, default=False)
    generation_timestamp = Column(TIMESTAMP(timezone=True), nullable=True)
    review_timestamp = Column(TIMESTAMP(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    original_instance_id = Column(String(255), nullable=True)
    attested_instance_id = Column(String(255), nullable=True)
    diff_report = Column(JSONB, nullable=True)
    original_text = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    status = Column(String(50), nullable=False, default="active")

    def __repr__(self) -> str:
        return f"<Attestation(id={self.id}, document={self.document_id}, status={self.status})>"
