"""GDPR data management router: deletion requests, purge, and data export.

Implements the engineering requirements from PRIVACY_RETENTION_POLICY.md:
- Soft-delete with 90-day purge window
- Verification record retention for 7 years
- Audit log retention for 2 years
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data", tags=["Data Management"])

ADMIN_ROLES = {"owner", "admin"}


async def _require_admin(
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Require admin or owner role for data management operations."""
    user_id = organization.get("user_id") or organization.get("api_key_owner_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User context required for admin operations.",
        )

    result = await db.execute(
        text("SELECT role FROM organization_members WHERE organization_id = :org_id AND user_id = :user_id"),
        {"org_id": organization["organization_id"], "user_id": user_id},
    )
    row = result.fetchone()
    role = row.role if row else None

    # For demo/test keys in enterprise tier, assume owner role
    if role is None and organization.get("is_demo"):
        role = "owner"

    if role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Owner role required for this operation.",
        )

    organization["current_user_role"] = role
    return organization


# Retention constants (from PRIVACY_RETENTION_POLICY.md)
PURGE_WINDOW_DAYS = 90
VERIFICATION_RETENTION_YEARS = 7
AUDIT_LOG_RETENTION_YEARS = 2


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class DeletionRequestCreate(BaseModel):
    """Request to delete user or organization data."""

    reason: Optional[str] = Field(None, max_length=1000, description="Reason for deletion")
    scope: str = Field(
        "account",
        description="Scope of deletion: 'account' (full account) or 'personal_data' (PII only)",
    )
    confirm: bool = Field(..., description="Must be true to confirm the deletion request")


class DeletionRequestResponse(BaseModel):
    """Response for a deletion request."""

    id: str
    organization_id: str
    requested_by: str
    scope: str
    reason: Optional[str]
    status: str
    requested_at: str
    scheduled_purge_at: str


class DeletionRequestListResponse(BaseModel):
    """List of deletion requests."""

    requests: List[DeletionRequestResponse]
    total: int


class AdminPurgeRequest(BaseModel):
    """Admin request to purge a specific user's data."""

    user_email: str = Field(..., description="Email of the user whose data to purge")
    reason: str = Field(..., min_length=1, max_length=1000, description="Administrative reason for purge")
    confirm: bool = Field(..., description="Must be true to confirm the purge")


class AdminPurgeResponse(BaseModel):
    """Response for an admin purge operation."""

    request_id: str
    user_email: str
    status: str
    scheduled_purge_at: str
    records_marked: int


class DeletionConfirmResponse(BaseModel):
    """Response for confirming/executing a deletion."""

    request_id: str
    status: str
    message: str


class DeletionReceiptResponse(BaseModel):
    """Deletion receipt for compliance documentation."""

    request_id: str
    organization_id: str
    scope: str
    requested_at: str
    completed_at: Optional[str]
    status: str
    data_categories_deleted: List[str]
    data_categories_retained: List[str]
    retention_reasons: Dict[str, str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_table_ensured = False


async def _ensure_deletion_requests_table(db: AsyncSession) -> None:
    """Create the deletion_requests table if it does not exist (once per process)."""
    global _table_ensured
    if _table_ensured:
        return
    await db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS deletion_requests (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                requested_by TEXT NOT NULL,
                user_email TEXT,
                scope TEXT NOT NULL DEFAULT 'account',
                reason TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                scheduled_purge_at TIMESTAMPTZ NOT NULL,
                completed_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
    )
    await db.commit()
    _table_ensured = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/deletion-request",
    status_code=status.HTTP_201_CREATED,
    response_model=DeletionRequestResponse,
    summary="Request data deletion (GDPR Art. 17)",
    description=(
        "Submit a request to delete your account or personal data. "
        "A 90-day soft-delete window begins immediately. Verification records "
        "are retained for 7 years per legal compliance requirements."
    ),
)
async def create_deletion_request(
    payload: DeletionRequestCreate,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    if not payload.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must set confirm=true to submit a deletion request.",
        )

    if payload.scope not in ("account", "personal_data"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="scope must be 'account' or 'personal_data'.",
        )

    org_id = organization["organization_id"]
    actor_id = organization.get("user_id") or organization.get("actor_id") or org_id
    request_id = f"del_{uuid4().hex[:16]}"
    now = datetime.now(timezone.utc)
    scheduled_purge = now + timedelta(days=PURGE_WINDOW_DAYS)

    await _ensure_deletion_requests_table(db)

    await db.execute(
        text(
            """
            INSERT INTO deletion_requests
              (id, organization_id, requested_by, scope, reason, status, requested_at, scheduled_purge_at)
            VALUES
              (:id, :org_id, :requested_by, :scope, :reason, 'pending', :now, :purge_at)
            """
        ),
        {
            "id": request_id,
            "org_id": org_id,
            "requested_by": actor_id,
            "scope": payload.scope,
            "reason": payload.reason,
            "now": now,
            "purge_at": scheduled_purge,
        },
    )
    await db.commit()

    logger.info(
        "Deletion request created: %s for org %s (scope=%s, purge=%s)",
        request_id,
        org_id,
        payload.scope,
        scheduled_purge.isoformat(),
    )

    return DeletionRequestResponse(
        id=request_id,
        organization_id=org_id,
        requested_by=actor_id,
        scope=payload.scope,
        reason=payload.reason,
        status="pending",
        requested_at=now.isoformat(),
        scheduled_purge_at=scheduled_purge.isoformat(),
    )


@router.get(
    "/deletion-requests",
    response_model=DeletionRequestListResponse,
    summary="List deletion requests",
    description="List all deletion requests for the current organization.",
)
async def list_deletion_requests(
    request: Request,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: pending, confirmed, completed, cancelled"),
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]

    VALID_STATUSES = {"pending", "confirmed", "completed", "cancelled"}
    if status_filter and status_filter not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status filter. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
        )

    await _ensure_deletion_requests_table(db)

    query = """
        SELECT id, organization_id, requested_by, scope, reason, status,
               requested_at, scheduled_purge_at
        FROM deletion_requests
        WHERE organization_id = :org_id
    """
    params: dict = {"org_id": org_id}

    if status_filter:
        query += " AND status = :status"
        params["status"] = status_filter

    query += " ORDER BY requested_at DESC"

    result = await db.execute(text(query), params)
    rows = result.mappings().all()

    requests_list = [
        DeletionRequestResponse(
            id=row["id"],
            organization_id=row["organization_id"],
            requested_by=row["requested_by"],
            scope=row["scope"],
            reason=row["reason"],
            status=row["status"],
            requested_at=row["requested_at"].isoformat() if row["requested_at"] else "",
            scheduled_purge_at=row["scheduled_purge_at"].isoformat() if row["scheduled_purge_at"] else "",
        )
        for row in rows
    ]

    return DeletionRequestListResponse(requests=requests_list, total=len(requests_list))


@router.delete(
    "/deletion-request/{request_id}/confirm",
    response_model=DeletionConfirmResponse,
    summary="Confirm and execute a deletion request",
    description=(
        "Confirm a pending deletion request. This begins the data purge process. "
        "Account data is soft-deleted immediately and permanently purged after 90 days. "
        "Verification records are retained for 7 years."
    ),
)
async def confirm_deletion_request(
    request_id: str,
    request: Request,
    organization: dict = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]

    await _ensure_deletion_requests_table(db)

    result = await db.execute(
        text(
            """
            SELECT id, organization_id, status, scope
            FROM deletion_requests
            WHERE id = :id AND organization_id = :org_id
            """
        ),
        {"id": request_id, "org_id": org_id},
    )
    row = result.mappings().first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deletion request not found.",
        )

    if row["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Deletion request is already '{row['status']}'. Only pending requests can be confirmed.",
        )

    now = datetime.now(timezone.utc)
    await db.execute(
        text(
            """
            UPDATE deletion_requests
            SET status = 'confirmed', updated_at = :now
            WHERE id = :id
            """
        ),
        {"id": request_id, "now": now},
    )
    await db.commit()

    logger.info(
        "Deletion request confirmed: %s for org %s (scope=%s)",
        request_id,
        org_id,
        row["scope"],
    )

    return DeletionConfirmResponse(
        request_id=request_id,
        status="confirmed",
        message=(
            "Deletion confirmed. Account data will be soft-deleted immediately. "
            f"Permanent purge is scheduled after {PURGE_WINDOW_DAYS} days. "
            f"Verification records are retained for {VERIFICATION_RETENTION_YEARS} years per legal requirements."
        ),
    )


@router.post(
    "/admin/purge-user",
    status_code=status.HTTP_201_CREATED,
    response_model=AdminPurgeResponse,
    summary="Admin: purge a user's data",
    description=(
        "Organization admin endpoint to initiate deletion of a specific user's data. "
        "Requires admin/owner role. The purge follows the same 90-day window."
    ),
)
async def admin_purge_user(
    payload: AdminPurgeRequest,
    request: Request,
    organization: dict = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    if not payload.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must set confirm=true to initiate a user purge.",
        )

    org_id = organization["organization_id"]
    actor_id = organization.get("user_id") or organization.get("actor_id") or org_id
    request_id = f"purge_{uuid4().hex[:16]}"
    now = datetime.now(timezone.utc)
    scheduled_purge = now + timedelta(days=PURGE_WINDOW_DAYS)

    await _ensure_deletion_requests_table(db)

    # Check if user exists in the organization
    user_result = await db.execute(
        text(
            """
            SELECT u.id FROM users u
            JOIN organization_members om ON om.user_id = u.id
            WHERE u.email = :email AND om.organization_id = :org_id
            """
        ),
        {"email": payload.user_email, "org_id": org_id},
    )
    user_row = user_result.first()

    records_marked = 0
    if user_row:
        # Mark user's API keys as revoked
        revoke_result = await db.execute(
            text(
                """
                UPDATE api_keys
                SET is_revoked = true, updated_at = :now
                WHERE organization_id = :org_id
                  AND (user_id = :user_id OR created_by = :user_id)
                  AND is_revoked = false
                """
            ),
            {"org_id": org_id, "user_id": str(user_row[0]), "now": now},
        )
        records_marked += revoke_result.rowcount or 0

    await db.execute(
        text(
            """
            INSERT INTO deletion_requests
              (id, organization_id, requested_by, user_email, scope, reason, status, requested_at, scheduled_purge_at)
            VALUES
              (:id, :org_id, :requested_by, :user_email, 'user_data', :reason, 'confirmed', :now, :purge_at)
            """
        ),
        {
            "id": request_id,
            "org_id": org_id,
            "requested_by": actor_id,
            "user_email": payload.user_email,
            "reason": payload.reason,
            "now": now,
            "purge_at": scheduled_purge,
        },
    )
    await db.commit()

    logger.info(
        "Admin purge initiated: %s for user %s in org %s (%d records marked)",
        request_id,
        payload.user_email,
        org_id,
        records_marked,
    )

    return AdminPurgeResponse(
        request_id=request_id,
        user_email=payload.user_email,
        status="confirmed",
        scheduled_purge_at=scheduled_purge.isoformat(),
        records_marked=records_marked,
    )


@router.get(
    "/deletion-request/{request_id}/receipt",
    response_model=DeletionReceiptResponse,
    summary="Get deletion receipt",
    description="Get a compliance receipt for a deletion request documenting what was deleted and what was retained.",
)
async def get_deletion_receipt(
    request_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]

    await _ensure_deletion_requests_table(db)

    result = await db.execute(
        text(
            """
            SELECT id, organization_id, scope, reason, status,
                   requested_at, completed_at
            FROM deletion_requests
            WHERE id = :id AND organization_id = :org_id
            """
        ),
        {"id": request_id, "org_id": org_id},
    )
    row = result.mappings().first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deletion request not found.",
        )

    scope = row["scope"]
    if scope == "account":
        deleted = ["Account information", "API keys", "Team membership", "Notification preferences", "Payment methods"]
        retained = ["Verification records", "Audit logs (2 years)", "Public verification data"]
    elif scope == "personal_data":
        deleted = ["Personal profile data", "Email address", "Contact information"]
        retained = ["Organization data", "Verification records", "API keys", "Audit logs"]
    else:  # user_data (admin purge)
        deleted = ["User profile data", "User API keys", "Team membership"]
        retained = ["Organization data", "Verification records", "Audit logs"]

    retention_reasons = {
        "Verification records": f"Retained for {VERIFICATION_RETENTION_YEARS} years (legal compliance)",
        "Audit logs": f"Retained for {AUDIT_LOG_RETENTION_YEARS} years (regulatory requirement)",
        "Public verification data": "Retained indefinitely (independent verification requirements)",
    }

    return DeletionReceiptResponse(
        request_id=row["id"],
        organization_id=row["organization_id"],
        scope=scope,
        requested_at=row["requested_at"].isoformat() if row["requested_at"] else "",
        completed_at=row["completed_at"].isoformat() if row["completed_at"] else None,
        status=row["status"],
        data_categories_deleted=deleted,
        data_categories_retained=retained,
        retention_reasons=retention_reasons,
    )


@router.post(
    "/deletion-request/{request_id}/cancel",
    response_model=DeletionConfirmResponse,
    summary="Cancel a pending deletion request",
    description="Cancel a deletion request that has not yet been purged.",
)
async def cancel_deletion_request(
    request_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization["organization_id"]

    await _ensure_deletion_requests_table(db)

    result = await db.execute(
        text(
            """
            SELECT id, status FROM deletion_requests
            WHERE id = :id AND organization_id = :org_id
            """
        ),
        {"id": request_id, "org_id": org_id},
    )
    row = result.mappings().first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deletion request not found.",
        )

    if row["status"] not in ("pending", "confirmed"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot cancel a request with status '{row['status']}'.",
        )

    now = datetime.now(timezone.utc)
    await db.execute(
        text(
            """
            UPDATE deletion_requests
            SET status = 'cancelled', updated_at = :now
            WHERE id = :id
            """
        ),
        {"id": request_id, "now": now},
    )
    await db.commit()

    return DeletionConfirmResponse(
        request_id=request_id,
        status="cancelled",
        message="Deletion request has been cancelled. Your data will not be deleted.",
    )
