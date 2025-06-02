"""
Pydantic schemas for policy validation-related API requests and responses.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class PolicySchemaBase(BaseModel):
    """Base policy schema with common attributes."""
    name: str
    description: Optional[str] = None
    schema_definition: Dict[str, Any]  # The actual JSON schema definition


class PolicySchemaCreate(PolicySchemaBase):
    """Schema for creating a new policy schema."""
    pass


class PolicySchemaUpdate(BaseModel):
    """Schema for updating a policy schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    schema_definition: Optional[Dict[str, Any]] = None  # Renamed from schema


class PolicySchemaInDB(PolicySchemaBase):
    """Schema for policy schema stored in the database."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True


class PolicySchema(PolicySchemaInDB):
    """Schema for policy schema response."""
    pass


class PolicyValidationResultBase(BaseModel):
    """Base policy validation result schema with common attributes."""
    source: str
    policy_schema_id: int
    is_valid: bool
    validated_data: Optional[Dict[str, Any]] = None  # The data that was validated
    errors: Optional[List[str]] = None
    source_type: Optional[str] = None
    department: Optional[str] = None


class PolicyValidationResultCreate(PolicyValidationResultBase):
    """Schema for creating a new policy validation result."""
    pass


class PolicyValidationResultUpdate(BaseModel):
    """Schema for updating a policy validation result."""
    is_valid: Optional[bool] = None
    validated_data: Optional[Dict[str, Any]] = None  # The data that was validated
    errors: Optional[List[str]] = None
    source_type: Optional[str] = None
    department: Optional[str] = None


class PolicyValidationResultInDB(PolicyValidationResultBase):
    """Schema for policy validation result stored in the database."""
    id: int
    validation_time: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True


class PolicyValidationResult(PolicyValidationResultInDB):
    """Schema for policy validation result response."""
    policy_schema: PolicySchema


class PolicyValidationStats(BaseModel):
    """Schema for policy validation statistics."""
    total_documents: int
    valid_count: int
    invalid_count: int
    validation_rate: float  # Percentage of valid documents
    error_types: Dict[str, int]  # Count of documents by error type
    department_stats: Dict[str, int]  # Count of documents by department


class PolicyValidationFilters(BaseModel):
    """Schema for filtering policy validation results."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    policy_schema_id: Optional[int] = None
    is_valid: Optional[bool] = None
    department: Optional[str] = None
    source_type: Optional[str] = None
