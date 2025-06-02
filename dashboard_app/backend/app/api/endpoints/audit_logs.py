"""
API endpoints for audit logs.
"""
from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.audit_log import AuditLog, AuditLogCreate, AuditLogStats, AuditLogFilters, AuditLogPage
from app.services.user import get_current_user  # Corrected import
from app.services.audit_log import (
    get_audit_logs,
    get_audit_log_by_id,
    create_audit_log,
    get_audit_log_stats
)

router = APIRouter()

@router.get("/", response_model=AuditLogPage)
async def read_audit_logs(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    status: Optional[str] = Query(None, description="Filter by status"),
    model_id: Optional[str] = Query(None, description="Filter by model ID"),
    department: Optional[str] = Query(None, description="Filter by department"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve audit logs with optional filtering.
    """
    filters = AuditLogFilters(
        start_date=start_date,
        end_date=end_date,
        status=status,
        model_id=model_id,
        department=department,
        source_type=source_type
    )
    logs, total_count = await get_audit_logs(db, filters=filters, skip=skip, limit=limit)
    return AuditLogPage(items=logs, total=total_count)

@router.get("/stats", response_model=AuditLogStats)
async def read_audit_log_stats(
    db: AsyncSession = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get audit log statistics for dashboard.
    """
    filters = AuditLogFilters(
        start_date=start_date,
        end_date=end_date,
        department=department
    )
    return await get_audit_log_stats(db, filters=filters) # Anticipating async service

@router.get("/{audit_log_id}", response_model=AuditLog)
async def read_audit_log(
    audit_log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a specific audit log by ID.
    """
    audit_log = await get_audit_log_by_id(db, audit_log_id) # Anticipating async service
    if not audit_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    return audit_log

@router.post("/", response_model=AuditLog, status_code=status.HTTP_201_CREATED)
async def create_new_audit_log(
    audit_log_in: AuditLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new audit log entry.
    """
    return await create_audit_log(db, audit_log_in) # Anticipating async service


@router.post("/import-csv/", response_model=dict)
async def import_audit_logs_from_csv_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Assuming import is an authenticated action
) -> Any:
    """
    Import audit logs from a CSV file.
    Saves the uploaded file temporarily, then processes it.
    """
    temp_file_path = f"temp_upload_{file.filename}" # Ensure a unique temp name
    try:
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Ensure the service function is imported if not already
        from app.services.audit_log import import_audit_log_from_csv
        imported_count = await import_audit_log_from_csv(db=db, csv_file_path=temp_file_path)
        return {"message": f"Successfully imported {imported_count} audit logs."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import CSV: {str(e)}")
    finally:
        import os
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
