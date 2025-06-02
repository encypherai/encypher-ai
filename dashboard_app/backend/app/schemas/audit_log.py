"""
Pydantic schemas for audit log-related API requests and responses.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class AuditLogBase(BaseModel):
    """Base audit log schema with common attributes."""
    source: str
    is_verified: bool
    status: str
    event_data: Optional[Dict[str, Any]] = None  # Extracted metadata or other event-specific data
    error_message: Optional[str] = None
    model_id: Optional[str] = None
    source_type: Optional[str] = None
    department: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating a new audit log entry."""
    pass


class AuditLogUpdate(BaseModel):
    """Schema for updating an audit log entry."""
    is_verified: Optional[bool] = None
    status: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None  # Extracted metadata or other event-specific data
    error_message: Optional[str] = None
    model_id: Optional[str] = None
    source_type: Optional[str] = None
    department: Optional[str] = None


class AuditLogInDB(AuditLogBase):
    """Schema for audit log stored in the database."""
    id: int
    verification_time: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True


class AuditLog(AuditLogInDB):
    """Schema for audit log response."""
    pass


class AuditLogStats(BaseModel):
    """Schema for audit log statistics."""
    total_documents: int
    verified_count: int
    unverified_count: int
    error_count: int
    verification_rate: float  # Percentage of verified documents
    model_usage: Dict[str, int]  # Count of documents by model_id
    department_stats: Dict[str, int]  # Count of documents by department


class AuditLogPage(BaseModel):
    items: List[AuditLog]
    total: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [
                        {
                            "id": 1,
                            "source": "user_action",
                            "is_verified": True,
                            "status": "VERIFIED",
                            "error_message": None,
                            "event_data": {"action": "login", "user_id": 123},
                            "verification_time": "2023-10-26T10:00:00Z",
                            "model_id": "model_xyz",
                            "department": "Security",
                            "source_type": "API",
                            "created_at": "2023-10-26T10:00:00Z",
                            "updated_at": "2023-10-26T10:00:00Z"
                        }
                    ],
                    "total": 100
                }
            ]
        }
    }


class AuditLogFilters(BaseModel):
    """Schema for filtering audit logs."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    model_id: Optional[str] = None
    department: Optional[str] = None
    source_type: Optional[str] = None
