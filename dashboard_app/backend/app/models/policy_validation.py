"""
Policy validation model for storing validation results.
"""
from sqlalchemy import Column, Integer, String, Boolean, JSON, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class PolicySchema(Base):
    """Policy schema model for storing policy definitions."""
    __tablename__ = "policy_schemas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    schema = Column(JSON)  # The full policy schema as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to validation results
    validation_results = relationship("PolicyValidationResult", back_populates="policy_schema")


class PolicyValidationResult(Base):
    """Policy validation result model for storing validation results."""
    __tablename__ = "policy_validation_results"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)  # File path or text source identifier
    policy_schema_id = Column(Integer, ForeignKey("policy_schemas.id"))
    is_valid = Column(Boolean, default=False)
    validation_time = Column(DateTime(timezone=True), server_default=func.now())
    validated_data = Column(JSON, nullable=True)  # The data that was validated against the policy
    errors = Column(JSON, nullable=True)  # List of validation errors
    
    # Additional fields for filtering and reporting
    source_type = Column(String, nullable=True)  # File, API, etc.
    department = Column(String, nullable=True, index=True)  # Department from metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to policy schema
    policy_schema = relationship("PolicySchema", back_populates="validation_results")
