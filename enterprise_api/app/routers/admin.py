"""
Admin API Router

Admin-only endpoints for:
- User management (list, stats, tier changes)
- Error log viewing
- BYOK public key management

IMPORTANT: These endpoints are tagged with "Admin" which is in _INTERNAL_DOC_TAGS
in main.py, so they will NOT appear in the public /docs endpoint.
They are only visible in /internal/docs (requires super_admin).
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_super_admin_dep
from app.schemas.admin import (
    AdminStatsResponse,
    AdminUserListResponse,
    ErrorLogsResponse,
    PublicKeyListResponse,
    PublicKeyRegisterRequest,
    PublicKeyRegisterResponse,
    TierUpdateRequest,
    TierUpdateResponse,
    UserStatusUpdateRequest,
    UserStatusUpdateResponse,
)
from app.services.admin_service import AdminService, PublicKeyService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


# =============================================================================
# Platform Stats (Super Admin Only)
# =============================================================================


@router.get(
    "/stats",
    response_model=AdminStatsResponse,
    summary="Get platform statistics",
    description="Get platform-wide statistics including user counts, revenue, and usage metrics.",
)
async def get_platform_stats(
    organization: dict = Depends(require_super_admin_dep),
    db: AsyncSession = Depends(get_db),
) -> AdminStatsResponse:
    """Get platform statistics for admin dashboard."""
    stats = await AdminService.get_platform_stats(db)
    return AdminStatsResponse(success=True, data=stats)


# =============================================================================
# User Management (Super Admin Only)
# =============================================================================


@router.get(
    "/users",
    response_model=AdminUserListResponse,
    summary="List all users",
    description="List all users/organizations with optional filtering and pagination.",
)
async def list_users(
    search: Optional[str] = Query(None, description="Search by name, email, or ID"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    organization: dict = Depends(require_super_admin_dep),
    db: AsyncSession = Depends(get_db),
) -> AdminUserListResponse:
    """List users with optional filtering."""
    result = await AdminService.list_users(
        db=db,
        search=search,
        tier=tier,
        page=page,
        page_size=page_size,
    )
    return AdminUserListResponse(success=True, data=result)


@router.post(
    "/users/update-tier",
    response_model=TierUpdateResponse,
    summary="Update user tier",
    description="Upgrade or downgrade a user's subscription tier.",
)
async def update_user_tier(
    request: TierUpdateRequest,
    organization: dict = Depends(require_super_admin_dep),
    db: AsyncSession = Depends(get_db),
) -> TierUpdateResponse:
    """Update a user's tier."""
    admin_id = organization.get("organization_id") or organization.get("user_id")

    result = await AdminService.update_user_tier(
        db=db,
        user_id=request.user_id,
        new_tier=request.new_tier.value,
        reason=request.reason,
        admin_id=admin_id,
    )

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "Failed to update tier"))

    return TierUpdateResponse(success=True, data=result)


@router.post(
    "/users/update-status",
    response_model=UserStatusUpdateResponse,
    summary="Update user status",
    description="Suspend or activate a user account.",
)
async def update_user_status(
    request: UserStatusUpdateRequest,
    organization: dict = Depends(require_super_admin_dep),
    db: AsyncSession = Depends(get_db),
) -> UserStatusUpdateResponse:
    """Update a user's status (suspend/activate)."""
    admin_id = organization.get("organization_id") or organization.get("user_id")

    result = await AdminService.update_user_status(
        db=db,
        user_id=request.user_id,
        status=request.status.value,
        reason=request.reason,
        admin_id=admin_id,
    )

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "Failed to update status"))

    return UserStatusUpdateResponse(success=True, data=result)


# =============================================================================
# Error Logs (Super Admin Only)
# =============================================================================


@router.get(
    "/error-logs",
    response_model=ErrorLogsResponse,
    summary="Get error logs",
    description="View API error logs with optional filtering.",
)
async def get_error_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status_code: Optional[int] = Query(None, description="Filter by HTTP status code"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    organization: dict = Depends(require_super_admin_dep),
    db: AsyncSession = Depends(get_db),
) -> ErrorLogsResponse:
    """Get error logs with optional filtering."""
    result = await AdminService.get_error_logs(
        db=db,
        user_id=user_id,
        status_code=status_code,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    return ErrorLogsResponse(success=True, data=result)


# =============================================================================
# BYOK Public Key Management (Enterprise Users)
# =============================================================================


@router.post(
    "/public-keys",
    response_model=PublicKeyRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a public key",
    description="Register a BYOK public key for signature verification. Requires enterprise tier with BYOK enabled.",
)
async def register_public_key(
    request: PublicKeyRegisterRequest,
    organization: dict = Depends(require_super_admin_dep),
    db: AsyncSession = Depends(get_db),
) -> PublicKeyRegisterResponse:
    """
    Register a public key for BYOK verification.

    Enterprise tier customers can register their own signing keys.
    When content signed with their private key is verified, we use
    the registered public key to validate the signature.
    """
    # Check BYOK feature is enabled
    features = organization.get("features", {})
    byok_enabled = features.get("byok", False) or organization.get("byok_enabled", False)
    tier = organization.get("tier", "free")

    if not byok_enabled and tier not in ("enterprise", "strategic_partner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="BYOK (Bring Your Own Key) requires Enterprise tier. Please upgrade your plan."
        )

    org_id = organization.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID missing")

    result = await PublicKeyService.register_public_key(
        db=db,
        organization_id=org_id,
        public_key_pem=request.public_key_pem,
        key_name=request.key_name,
        key_algorithm=request.key_algorithm,
    )

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "Failed to register public key"))

    return PublicKeyRegisterResponse(success=True, data=result.get("data"))


@router.get(
    "/public-keys",
    response_model=PublicKeyListResponse,
    summary="List public keys",
    description="List all registered public keys for the organization.",
)
async def list_public_keys(
    include_revoked: bool = Query(False, description="Include revoked keys"),
    organization: dict = Depends(require_super_admin_dep),
    db: AsyncSession = Depends(get_db),
) -> PublicKeyListResponse:
    """List public keys for the organization."""
    org_id = organization.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID missing")

    result = await PublicKeyService.list_public_keys(
        db=db,
        organization_id=org_id,
        include_revoked=include_revoked,
    )

    return PublicKeyListResponse(success=True, data=result.get("data", {}))


@router.delete(
    "/public-keys/{key_id}",
    summary="Revoke a public key",
    description="Revoke a registered public key. Revoked keys cannot be used for verification.",
)
async def revoke_public_key(
    key_id: str,
    reason: Optional[str] = Query(None, description="Reason for revocation"),
    organization: dict = Depends(require_super_admin_dep),
    db: AsyncSession = Depends(get_db),
):
    """Revoke a public key."""
    org_id = organization.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID missing")

    result = await PublicKeyService.revoke_public_key(
        db=db,
        organization_id=org_id,
        key_id=key_id,
        reason=reason,
    )

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error", "Failed to revoke public key"))

    return {"success": True, "data": result.get("data")}
