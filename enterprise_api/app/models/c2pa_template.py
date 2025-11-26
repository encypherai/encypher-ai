"""
C2PA Assertion Template Model

Stores reusable C2PA assertion templates.
"""
from sqlalchemy import Column, String, Text, Boolean, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator
import uuid

from app.database import Base


# Database-agnostic JSON type
class JSONType(TypeDecorator):
    """
    JSON type that uses JSONB for PostgreSQL and JSON for other databases.
    """
    impl = JSON
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())



class C2PAAssertionTemplate(Base):
    """
    Pre-built C2PA assertion template.
    
    Templates provide pre-configured sets of assertions
    for common use cases (news, legal, academic, etc.).
    
    Updated to match unified schema in 002_enterprise_api_schema.sql.
    """
    __tablename__ = "c2pa_assertion_templates"
    
    # Primary key - matches migration
    id = Column(String(64), primary_key=True, default=lambda: f"tmpl_{uuid.uuid4().hex[:12]}")
    
    # Foreign keys - matches migration
    organization_id = Column(String(64), nullable=False, index=True)
    schema_id = Column(String(64), nullable=False, index=True)
    
    # Template data - matches migration
    name = Column(String(255), nullable=False)
    template_data = Column(JSONType, nullable=False)
    category = Column(String(100), nullable=True)  # news, legal, academic, publisher
    
    # Status flags - matches migration
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Metadata - matches migration
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'schema_id': self.schema_id,
            'template_data': self.template_data,
            'category': self.category,
            'organization_id': self.organization_id,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
