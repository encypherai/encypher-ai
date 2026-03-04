"""Audit logging router for Business+ tier organizations."""

import json
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory, get_db
from app.dependencies import require_read_permission

logger = logging.getLogger(__name__)

router = APIRouter()


async def write_api_audit_log(
    organization_id: str,
    action: str,
    resource_type: str,
    actor_id: str,
    actor_type: str = "api_key",
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """Write an audit log entry using a standalone session (best-effort, errors swallowed).

    Opens its own DB session so callers can fire-and-forget via asyncio.create_task
    without worrying about session lifecycle.
    """
    try:
        async with async_session_factory() as db:
            await db.execute(
                text(
                    """
                    INSERT INTO audit_logs
                      (id, organization_id, action, actor_id, actor_type,
                       resource_type, resource_id, details, ip_address, user_agent)
                    VALUES
                      (:id, :organization_id, :action, :actor_id, :actor_type,
                       :resource_type, :resource_id, :details, :ip_address, :user_agent)
                    """
                ),
                {
                    "id": uuid4().hex,
                    "organization_id": organization_id,
                    "action": action,
                    "actor_id": actor_id,
                    "actor_type": actor_type,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "details": json.dumps(details) if details is not None else None,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                },
            )
            await db.commit()
    except Exception as exc:
        logger.warning(
            "audit_log_write_failed",
            extra={"action": action, "org_id": organization_id, "error": str(exc)},
        )


class AuditAction(str, Enum):
    """Types of auditable actions."""

    # API Key operations
    API_KEY_CREATED = "api_key.created"
    API_KEY_REVOKED = "api_key.revoked"
    API_KEY_ROTATED = "api_key.rotated"

    # Signing operations
    DOCUMENT_SIGNED = "document.signed"
    BATCH_SIGN_STARTED = "batch.sign.started"
    BATCH_SIGN_COMPLETED = "batch.sign.completed"

    # Verification operations
    DOCUMENT_VERIFIED = "document.verified"
    VERIFICATION_FAILED = "verification.failed"

    # Organization operations
    ORG_SETTINGS_UPDATED = "org.settings.updated"
    ORG_TIER_CHANGED = "org.tier.changed"
    ORG_MEMBER_ADDED = "org.member.added"
    ORG_MEMBER_REMOVED = "org.member.removed"
    ORG_MEMBER_ROLE_CHANGED = "org.member.role.changed"

    # Certificate operations
    CERTIFICATE_UPLOADED = "certificate.uploaded"
    CERTIFICATE_ROTATED = "certificate.rotated"

    # Coalition operations
    COALITION_OPTED_IN = "coalition.opted_in"
    COALITION_OPTED_OUT = "coalition.opted_out"

    # Billing operations
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPGRADED = "subscription.upgraded"
    SUBSCRIPTION_DOWNGRADED = "subscription.downgraded"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"


class AuditLogEntry(BaseModel):
    """Single audit log entry."""

    id: str
    timestamp: str
    action: str
    actor_id: str
    actor_type: str  # user, api_key, system
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogResponse(BaseModel):
    """Paginated audit log response."""

    organization_id: str
    logs: List[AuditLogEntry]
    total: int
    page: int
    page_size: int
    has_more: bool


class AuditLogCreateRequest(BaseModel):
    """Request to create an audit log entry."""

    action: AuditAction
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


async def check_audit_logs_enabled(
    organization: dict = Depends(require_read_permission),
) -> dict:
    """Check if audit logs are enabled for the organization."""
    if not organization.get("audit_logs_enabled", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Audit logs are only available on Business and Enterprise tiers",
                "upgrade_url": "/billing/upgrade",
            },
        )
    return organization


@router.get("/audit-logs", response_model=AuditLogResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    action: Optional[str] = Query(None, description="Filter by action type"),
    actor_id: Optional[str] = Query(None, description="Filter by actor ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    organization: dict = Depends(check_audit_logs_enabled),
    db: AsyncSession = Depends(get_db),
) -> AuditLogResponse:
    """
    Get audit logs for the organization.

    Supports filtering by:
    - action: Type of action (e.g., "document.signed")
    - actor_id: ID of the user or API key that performed the action
    - resource_type: Type of resource affected
    - start_date/end_date: Date range

    Results are paginated and sorted by timestamp (newest first).
    """
    org_id = organization["organization_id"]
    offset = (page - 1) * page_size

    # Build query with filters
    where_clauses = ["organization_id = :org_id"]
    params = {"org_id": org_id, "limit": page_size, "offset": offset}

    if action:
        where_clauses.append("action = :action")
        params["action"] = action

    if actor_id:
        where_clauses.append("actor_id = :actor_id")
        params["actor_id"] = actor_id

    if resource_type:
        where_clauses.append("resource_type = :resource_type")
        params["resource_type"] = resource_type

    if start_date:
        where_clauses.append("created_at >= :start_date")
        # Parse ISO string to datetime for PostgreSQL
        params["start_date"] = datetime.fromisoformat(start_date.replace("Z", "+00:00"))

    if end_date:
        where_clauses.append("created_at <= :end_date")
        params["end_date"] = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

    where_sql = " AND ".join(where_clauses)

    # Get total count
    # Note: where_sql contains only hardcoded column names and :param placeholders, not user input
    count_result = await db.execute(
        text(f"SELECT COUNT(*) FROM audit_logs WHERE {where_sql}"),  # noqa: S608
        params,
    )
    total = count_result.scalar() or 0

    # Get paginated results
    # Note: where_sql is built from hardcoded strings, user values are parameterized
    result = await db.execute(
        text(f"""
            SELECT 
                id, created_at, action, actor_id, actor_type,
                resource_type, resource_id, details, ip_address, user_agent
            FROM audit_logs
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """),  # noqa: S608
        params,
    )
    rows = result.fetchall()

    logs = [
        AuditLogEntry(
            id=row.id,
            timestamp=row.created_at.isoformat() if row.created_at else "",
            action=row.action,
            actor_id=row.actor_id,
            actor_type=row.actor_type,
            resource_type=row.resource_type,
            resource_id=row.resource_id,
            details=row.details,
            ip_address=row.ip_address,
            user_agent=row.user_agent,
        )
        for row in rows
    ]

    return AuditLogResponse(
        organization_id=org_id,
        logs=logs,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + len(logs)) < total,
    )


@router.get("/audit-logs/export")
async def export_audit_logs(
    format: str = Query("json", pattern="^(json|csv)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    organization: dict = Depends(check_audit_logs_enabled),
    db: AsyncSession = Depends(get_db),
):
    """
    Export audit logs in JSON or CSV format.

    Returns all logs within the specified date range.
    Default is last 30 days if no dates specified.
    """
    org_id = organization["organization_id"]

    # Default to last 30 days
    end_dt = datetime.now(timezone.utc)
    if end_date:
        end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

    if start_date:
        start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    else:
        start_dt = end_dt - timedelta(days=30)

    result = await db.execute(
        text("""
            SELECT 
                id, created_at, action, actor_id, actor_type,
                resource_type, resource_id, details, ip_address, user_agent
            FROM audit_logs
            WHERE organization_id = :org_id
              AND created_at >= :start_date
              AND created_at <= :end_date
            ORDER BY created_at DESC
        """),
        {"org_id": org_id, "start_date": start_dt, "end_date": end_dt},
    )
    rows = result.fetchall()

    if format == "csv":
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "timestamp", "action", "actor_id", "actor_type", "resource_type", "resource_id", "ip_address", "user_agent"])

        for row in rows:
            writer.writerow(
                [
                    row.id,
                    row.created_at.isoformat() if row.created_at else "",
                    row.action,
                    row.actor_id,
                    row.actor_type,
                    row.resource_type,
                    row.resource_id,
                    row.ip_address,
                    row.user_agent,
                ]
            )

        from fastapi.responses import Response

        return Response(
            content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=audit_logs_{org_id}.csv"}
        )

    # JSON format
    logs = [
        {
            "id": row.id,
            "timestamp": row.created_at.isoformat() if row.created_at else "",
            "action": row.action,
            "actor_id": row.actor_id,
            "actor_type": row.actor_type,
            "resource_type": row.resource_type,
            "resource_id": row.resource_id,
            "details": row.details,
            "ip_address": row.ip_address,
            "user_agent": row.user_agent,
        }
        for row in rows
    ]

    return {
        "organization_id": org_id,
        "export_date": datetime.now(timezone.utc).isoformat(),
        "start_date": start_dt.isoformat(),
        "end_date": end_dt.isoformat(),
        "total_records": len(logs),
        "logs": logs,
    }


async def log_audit_event(
    db: AsyncSession,
    organization_id: str,
    action: AuditAction,
    actor_id: str,
    actor_type: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> str:
    """
    Create an audit log entry.

    This is a helper function to be called from other parts of the application.
    Returns the ID of the created log entry.
    """
    import json

    log_id = f"audit_{uuid4().hex[:16]}"
    now = datetime.now(timezone.utc)

    # Serialize details dict to JSON string for PostgreSQL JSONB column
    details_json = json.dumps(details) if details else None

    await db.execute(
        text("""
            INSERT INTO audit_logs (
                id, organization_id, created_at, action, actor_id, actor_type,
                resource_type, resource_id, details, ip_address, user_agent
            )
            VALUES (
                :id, :org_id, :created_at, :action, :actor_id, :actor_type,
                :resource_type, :resource_id, CAST(:details AS jsonb), :ip_address, :user_agent
            )
        """),
        {
            "id": log_id,
            "org_id": organization_id,
            "created_at": now,
            "action": action.value,
            "actor_id": actor_id,
            "actor_type": actor_type,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details_json,
            "ip_address": ip_address,
            "user_agent": user_agent,
        },
    )

    return log_id
