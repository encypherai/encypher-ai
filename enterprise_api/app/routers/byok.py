"""Customer-facing BYOK (Bring Your Own Key) endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.schemas.admin import PublicKeyListResponse, PublicKeyRegisterRequest, PublicKeyRegisterResponse
from app.services.admin_service import PublicKeyService

router = APIRouter(prefix="/byok", tags=["BYOK"])


def require_byok_business_tier(
    organization: dict = Depends(get_current_organization),
) -> dict:
    features = organization.get("features", {})
    byok_enabled = False
    if isinstance(features, dict):
        byok_enabled = features.get("byok", False)

    byok_enabled = byok_enabled or organization.get("byok_enabled", False)

    tier = (organization.get("tier") or "starter").lower().replace("-", "_")
    allowed_tiers = {"business", "enterprise", "strategic_partner", "demo"}

    if not byok_enabled and tier not in allowed_tiers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="BYOK (Bring Your Own Key) requires Business tier or higher. Please upgrade your plan.",
        )

    return organization


@router.post(
    "/public-keys",
    response_model=PublicKeyRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a public key",
    description="Register a BYOK public key for signature verification.",
)
async def register_public_key(
    request: PublicKeyRegisterRequest,
    organization: dict = Depends(require_byok_business_tier),
    db: AsyncSession = Depends(get_db),
) -> PublicKeyRegisterResponse:
    org_id = organization.get("organization_id")

    result = await PublicKeyService.register_public_key(
        db=db,
        organization_id=org_id,
        public_key_pem=request.public_key_pem,
        key_name=request.key_name,
        key_algorithm=request.key_algorithm,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to register public key"),
        )

    return PublicKeyRegisterResponse(success=True, data=result.get("data"))


@router.get(
    "/public-keys",
    response_model=PublicKeyListResponse,
    summary="List public keys",
    description="List all registered public keys for the organization.",
)
async def list_public_keys(
    include_revoked: bool = Query(False, description="Include revoked keys"),
    organization: dict = Depends(require_byok_business_tier),
    db: AsyncSession = Depends(get_db),
) -> PublicKeyListResponse:
    org_id = organization.get("organization_id")

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
    reason: str | None = Query(None, description="Reason for revocation"),
    organization: dict = Depends(require_byok_business_tier),
    db: AsyncSession = Depends(get_db),
) -> dict:
    org_id = organization.get("organization_id")

    result = await PublicKeyService.revoke_public_key(
        db=db,
        organization_id=org_id,
        key_id=key_id,
        reason=reason,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to revoke public key"),
        )

    return {"success": True, "data": result.get("data")}
