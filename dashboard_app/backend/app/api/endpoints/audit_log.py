from typing import Any, List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.audit_log import AuditLog as AuditLogSchema
from app.schemas.audit_log import AuditLogCreate, AuditLogFilters, AuditLogStats
from app.services import audit_log as audit_log_service

router = APIRouter()


@router.post("/", response_model=AuditLogSchema, status_code=201)
async def create_audit_log_entry(
    audit_log_in: AuditLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),  # Assuming logs are created by authenticated users
) -> Any:
    """
    Create new audit log.
    """
    return await audit_log_service.create_audit_log(db=db, audit_log_in=audit_log_in)


@router.get("/", response_model=List[AuditLogSchema])
async def read_audit_logs(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    filters: AuditLogFilters = Depends(),  # Use Depends for query parameters in Pydantic model
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve audit logs with filtering and pagination.
    """
    logs = await audit_log_service.get_audit_logs(db=db, filters=filters, skip=skip, limit=limit)
    return logs


@router.get("/stats/", response_model=AuditLogStats)
async def read_audit_log_stats(
    db: AsyncSession = Depends(get_db), filters: AuditLogFilters = Depends(), current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve audit log statistics.
    """
    stats = await audit_log_service.get_audit_log_stats(db=db, filters=filters)
    return stats


@router.get("/{audit_log_id}", response_model=AuditLogSchema)
async def read_audit_log(audit_log_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Get audit log by ID.
    """
    db_audit_log = await audit_log_service.get_audit_log_by_id(db=db, audit_log_id=audit_log_id)
    if db_audit_log is None:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return db_audit_log


@router.post("/import-csv/", response_model=dict)
async def import_audit_logs_from_csv_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),  # Assuming import is an authenticated action
) -> Any:
    """
    Import audit logs from a CSV file.
    Saves the uploaded file temporarily, then processes it.
    """
    # Securely save the uploaded file temporarily
    # Note: In a production environment, consider using a more robust temporary file handling
    # or streaming the file content directly if the service layer supports it.
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        imported_count = await audit_log_service.import_audit_log_from_csv(db=db, csv_file_path=temp_file_path)
        return {"message": f"Successfully imported {imported_count} audit logs."}
    except Exception as e:
        # Basic error handling, consider more specific exceptions
        raise HTTPException(status_code=500, detail=f"Failed to import CSV: {str(e)}")
    finally:
        # Clean up the temporary file
        import os

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
