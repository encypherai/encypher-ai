"""
C2PA Schema Model

Stores custom C2PA assertion schemas for validation.
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.database import Base


class C2PASchema(Base):
    """
    Custom C2PA assertion schema for validation.
    
    Allows organizations to register custom assertion types
    with JSON Schema validation rules.
    """
    __tablename__ = "c2pa_schemas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    namespace = Column(String(255), nullable=False, index=True)
    label = Column(String(255), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    schema = Column(JSONB, nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(String(255), nullable=True, index=True)
    is_public = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('uq_schema_namespace_label_version', 'namespace', 'label', 'version', unique=True),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': str(self.id),
            'namespace': self.namespace,
            'label': self.label,
            'version': self.version,
            'schema': self.schema,
            'description': self.description,
            'organization_id': self.organization_id,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
