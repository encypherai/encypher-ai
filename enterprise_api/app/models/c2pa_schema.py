"""
C2PA Schema Model

Stores custom C2PA assertion schemas for validation.
"""

import uuid

from sqlalchemy import JSON, TIMESTAMP, Boolean, Column, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator

from app.database import Base


# Database-agnostic JSON type
class JSONType(TypeDecorator):
    """
    JSON type that uses JSONB for PostgreSQL and JSON for other databases.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())


class C2PASchema(Base):
    """
    Custom C2PA assertion schema for validation.

    Allows organizations to register custom assertion types
    with JSON Schema validation rules.

    Updated to match unified schema in 002_enterprise_api_schema.sql.
    """

    __tablename__ = "c2pa_assertion_schemas"

    # Primary key - matches migration
    id = Column(String(64), primary_key=True, default=lambda: f"schema_{uuid.uuid4().hex[:12]}")

    # Foreign key - matches migration
    organization_id = Column(String(64), nullable=False, index=True)

    # Schema definition - matches migration
    name = Column(String(255), nullable=False)
    label = Column(String(255), nullable=False)
    version = Column(String(20), nullable=False, default="1.0")
    json_schema = Column(JSONType, nullable=False)

    # Status - matches migration
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)

    # Metadata - matches migration
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (Index("uq_c2pa_schema_org_label_version", "organization_id", "label", "version", unique=True),)

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "name": self.name,
            "label": self.label,
            "version": self.version,
            "json_schema": self.json_schema,
            "description": self.description,
            "organization_id": self.organization_id,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
