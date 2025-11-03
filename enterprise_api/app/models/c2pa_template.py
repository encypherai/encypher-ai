"""
C2PA Assertion Template Model

Stores pre-built assertion templates for common use cases.
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.database import Base


class C2PAAssertionTemplate(Base):
    """
    Pre-built C2PA assertion template.
    
    Templates provide pre-configured sets of assertions
    for common use cases (news, legal, academic, etc.).
    """
    __tablename__ = "c2pa_assertion_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    assertions = Column(JSONB, nullable=False)
    organization_id = Column(String(255), nullable=True, index=True)
    is_public = Column(Boolean, default=False, nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)  # news, legal, academic, publisher
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'assertions': self.assertions,
            'organization_id': self.organization_id,
            'is_public': self.is_public,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
