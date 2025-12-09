"""
Service for audit log operations.
"""
import csv
import json
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate, AuditLogFilters, AuditLogStats
from app.utils.caching import cached_async, invalidate_cache


async def get_audit_logs(
    db: AsyncSession,
    filters: Optional[AuditLogFilters] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[AuditLog], int]:
    """
    Get audit logs with optional filtering and total count.
    
    Args:
        db: Database session
        filters: Optional filters
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        A tuple containing a list of audit logs and the total count of matching records.
    """
    query = select(AuditLog)
    count_query = select(func.count()).select_from(AuditLog)

    if filters:
        if filters.start_date:
            query = query.where(AuditLog.verification_time >= filters.start_date)
            count_query = count_query.where(AuditLog.verification_time >= filters.start_date)
        if filters.end_date:
            query = query.where(AuditLog.verification_time <= filters.end_date)
            count_query = count_query.where(AuditLog.verification_time <= filters.end_date)
        if filters.status:
            query = query.where(AuditLog.status == filters.status)
            count_query = count_query.where(AuditLog.status == filters.status)
        if filters.model_id:
            query = query.where(AuditLog.model_id == filters.model_id)
            count_query = count_query.where(AuditLog.model_id == filters.model_id)
        if filters.department:
            query = query.where(AuditLog.department == filters.department)
            count_query = count_query.where(AuditLog.department == filters.department)
        if filters.source_type:
            query = query.where(AuditLog.source_type == filters.source_type)
            count_query = count_query.where(AuditLog.source_type == filters.source_type)

    total_count_result = await db.execute(count_query)
    total_count = total_count_result.scalar_one_or_none() or 0

    result = await db.execute(
        query.order_by(AuditLog.verification_time.desc()).offset(skip).limit(limit)
    )
    logs = result.scalars().all()
    return logs, total_count

async def get_audit_log_by_id(db: AsyncSession, audit_log_id: int) -> Optional[AuditLog]:
    """
    Get an audit log by ID.
    
    Args:
        db: Database session
        audit_log_id: Audit log ID
        
    Returns:
        Audit log if found, None otherwise
    """
    return await db.get(AuditLog, audit_log_id)

async def create_audit_log(db: AsyncSession, audit_log_in: AuditLogCreate) -> AuditLog:
    """
    Create a new audit log entry.
    """
    db_audit_log = AuditLog(**audit_log_in.model_dump())
    db.add(db_audit_log)
    await db.commit()
    await db.refresh(db_audit_log)  # Refresh to load server-set defaults
    
    # Invalidate stats cache when new data is added
    await invalidate_cache("audit_log_stats")
    
    return db_audit_log

@cached_async(key_prefix="audit_log_stats", ttl_seconds=300)
async def get_audit_log_stats(db: AsyncSession, filters: AuditLogFilters) -> AuditLogStats:
    """
    Get audit log statistics for dashboard.
    
    Args:
        db: Database session
        filters: Optional filters
        
    Returns:
        Audit log statistics
    """
    filter_conditions = []
    if filters:
        if filters.start_date:
            filter_conditions.append(AuditLog.verification_time >= filters.start_date)
        if filters.end_date:
            filter_conditions.append(AuditLog.verification_time <= filters.end_date)
        if filters.status:
            filter_conditions.append(AuditLog.status == filters.status)
        if filters.model_id:
            filter_conditions.append(AuditLog.model_id == filters.model_id)
        if filters.department:
            filter_conditions.append(AuditLog.department == filters.department)
        if filters.source_type:
            filter_conditions.append(AuditLog.source_type == filters.source_type)

    # Base query selecting all columns from AuditLog, with initial filters applied
    base_select_stmt = select(AuditLog)
    if filter_conditions:
        base_select_stmt = base_select_stmt.where(and_(*filter_conditions))

    # Create a named subquery from the base select statement
    log_sq = base_select_stmt.subquery('log_sq')

    # Total documents
    total_documents_stmt = select(func.count()).select_from(log_sq)
    total_documents = (await db.execute(total_documents_stmt)).scalar_one_or_none() or 0
    
    # Verified count
    verified_stmt = select(func.count()).select_from(log_sq).where(log_sq.c.is_verified == True)
    verified_count = (await db.execute(verified_stmt)).scalar_one_or_none() or 0
    
    # Unverified count (meaning is_verified is False AND status is UNVERIFIED)
    unverified_stmt = select(func.count()).select_from(log_sq).where(
        and_(log_sq.c.is_verified == False, log_sq.c.status == "UNVERIFIED")
    )
    unverified_count = (await db.execute(unverified_stmt)).scalar_one_or_none() or 0
    
    # Error count
    error_stmt = select(func.count()).select_from(log_sq).where(log_sq.c.status == "ERROR")
    error_count = (await db.execute(error_stmt)).scalar_one_or_none() or 0
    
    # Verification rate
    verification_rate = (verified_count / total_documents) * 100 if total_documents > 0 else 0.0
    
    # Model usage (count of logs per model_id, from the filtered subquery)
    model_usage_query = select(
        log_sq.c.model_id, func.count(log_sq.c.id).label('count')
    ).select_from(log_sq).where(
        log_sq.c.model_id.isnot(None)
    ).group_by(
        log_sq.c.model_id
    )
    model_usage_result = await db.execute(model_usage_query)
    model_usage = dict(model_usage_result.all())
    
    # Department stats (count of logs per department, from the filtered subquery)
    department_stats_query = select(
        log_sq.c.department, func.count(log_sq.c.id).label('count')
    ).select_from(log_sq).where(
        log_sq.c.department.isnot(None)
    ).group_by(
        log_sq.c.department
    )
    department_stats_result = await db.execute(department_stats_query)
    department_stats = dict(department_stats_result.all())
    
    return AuditLogStats(
        total_documents=total_documents,
        verified_count=verified_count,
        unverified_count=unverified_count,
        error_count=error_count,
        verification_rate=verification_rate,
        model_usage=model_usage,
        department_stats=department_stats
    )

async def import_audit_log_from_csv(db: AsyncSession, csv_file_path: str) -> int:
    """
    Import audit logs from a CSV file generated by the audit_log_cli tool.
    
    Args:
        db: Database session
        csv_file_path: Path to CSV file
        
    Returns:
        Number of imported records
    """
    count = 0
    logs_to_add = []
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            metadata = {}
            # Standardize keys by lowercasing and replacing spaces with underscores
            standardized_row = {k.lower().replace(' ', '_'): v for k, v in row.items()}

            for key, value in standardized_row.items():
                if key not in ['source', 'is_verified', 'status', 'error_message', 'verification_time', 'model_id', 'department']:
                    try:
                        metadata[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        metadata[key] = value
            
            model_id = standardized_row.get('model_id')
            department = standardized_row.get('department')
            
            verification_time_str = standardized_row.get('verification_time')
            try:
                verification_time = datetime.fromisoformat(verification_time_str) if verification_time_str else datetime.now()
            except ValueError:
                verification_time = datetime.now() # Fallback if parsing fails

            audit_log = AuditLog(
                source=standardized_row.get('source', ''),
                is_verified=standardized_row.get('is_verified', 'false').lower() == 'true',
                status=standardized_row.get('status', ''),
                error_message=standardized_row.get('error_message'),
                event_data=metadata, # Changed from metadata
                model_id=model_id,
                department=department,
                verification_time=verification_time
            )
            logs_to_add.append(audit_log)
            count += 1
        
    if logs_to_add:
        db.add_all(logs_to_add)
        await db.commit()
    
    return count
