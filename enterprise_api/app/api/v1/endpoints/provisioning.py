"""
API endpoints for auto-provisioning organizations and API keys.

Allows external services (SDK, WordPress, CLI) to automatically
create organizations and obtain API keys.
"""

import logging
import time
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.config import settings
from app.database import get_db
from app.models.organization import OrganizationTier
from app.schemas.provisioning import (
    APIKeyCreateRequest,
    APIKeyListResponse,
    APIKeyResponse,
    APIKeyRevokeRequest,
    AutoProvisionRequest,
    AutoProvisionResponse,
    UserAccountCreateRequest,
    UserAccountResponse,
)
from app.services.provisioning_service import ProvisioningService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/provisioning", tags=["Provisioning"])


def _require_provisioning_token(x_provisioning_token: str | None) -> None:
    if not settings.is_production:
        return

    expected = (settings.provisioning_token or "").strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Provisioning is not configured for production",
        )

    token = (x_provisioning_token or "").strip()
    if token != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid provisioning token",
        )


# ============================================================================
# Auto-Provisioning Endpoint
# ============================================================================


@router.post(
    "/auto-provision",
    response_model=AutoProvisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Auto-provision Organization and API Key",
    description="""
    Automatically provision an organization, user account, and API key.
    
    This endpoint is designed for external services to automatically create
    accounts without manual intervention:
    
    **Use Cases:**
    - SDK initialization (auto-create account on first use)
    - WordPress plugin activation (auto-provision on install)
    - CLI tool setup (auto-create account on login)
    - Mobile app onboarding (auto-provision on signup)
    
    **What Gets Created:**
    1. Organization (with specified tier)
    2. User account (associated with email)
    3. API key (for authentication)
    
    **Idempotent:** If organization already exists for email, returns existing
    organization with a new API key.
    
    **Rate Limits:**
    - 10 requests per minute per IP
    - 100 requests per hour per email
    
    **Security:**
    - Requires valid provisioning token (for production)
    - Validates email format
    - Logs all provisioning events
    """,
    responses={
        201: {"description": "Organization and API key created successfully"},
        400: {"description": "Invalid request"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error"},
    },
)
async def auto_provision(
    request: AutoProvisionRequest,
    db: AsyncSession = Depends(get_db),
    x_provisioning_token: str = Header(None, description="Provisioning token (optional)"),
) -> AutoProvisionResponse:
    """
    Auto-provision an organization and API key.

    Args:
        request: Provisioning request
        db: Database session
        x_provisioning_token: Optional provisioning token for security

    Returns:
        AutoProvisionResponse with organization and API key details
    """
    start_time = time.time()

    try:
        logger.info(f"Auto-provisioning request from {request.source} for {request.email}")

        _require_provisioning_token(x_provisioning_token)

        # Auto-provision organization, user, and API key
        org, api_key, user_id = await ProvisioningService.auto_provision(
            db=db,
            email=request.email,
            organization_name=request.organization_name,
            source=request.source,
            source_metadata=request.source_metadata,
            tier=request.tier or "free",
            auto_activate=request.auto_activate,
        )

        # Get tier enum
        tier_map = {"free": OrganizationTier.FREE, "professional": OrganizationTier.PROFESSIONAL, "enterprise": OrganizationTier.ENTERPRISE}
        tier_enum = tier_map.get(request.tier or "free", OrganizationTier.FREE)

        # Build response
        api_key_response = APIKeyResponse(
            api_key=api_key,
            key_id=f"key_{api_key[-12:]}",
            organization_id=org.organization_id,
            tier=str(org.tier),
            created_at=org.created_at,
            expires_at=None,
        )

        features_enabled = ProvisioningService.get_features_for_tier(tier_enum)
        quota_limits = ProvisioningService.get_quota_limits_for_tier(tier_enum)
        next_steps = ProvisioningService.get_next_steps()

        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(f"Successfully provisioned {org.organization_id} in {processing_time_ms:.2f}ms")

        return AutoProvisionResponse(
            success=True,
            message="Organization and API key created successfully",
            organization_id=org.organization_id,
            organization_name=org.name,
            user_id=user_id,
            api_key=api_key_response,
            tier=str(org.tier),
            features_enabled=features_enabled,
            quota_limits=quota_limits,
            next_steps=next_steps,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error auto-provisioning: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to provision organization")


# ============================================================================
# API Key Management Endpoints
# ============================================================================


@router.post(
    "/api-keys",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create API Key",
    description="Create a new API key for an organization",
)
async def create_api_key(
    request: APIKeyCreateRequest,
    db: AsyncSession = Depends(get_db),
    x_provisioning_token: str = Header(None, description="Provisioning token (optional)"),
    # TODO: Add authentication dependency
    # current_org: Organization = Depends(get_current_organization)
) -> APIKeyResponse:
    """
    Create a new API key.

    Args:
        request: API key creation request
        db: Database session

    Returns:
        Created API key details
    """
    _require_provisioning_token(x_provisioning_token)

    org_row = await db.execute(text("SELECT id, tier FROM organizations WHERE id = :org_id"), {"org_id": request.organization_id})
    org = org_row.fetchone()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    key_data = await ProvisioningService.create_api_key(
        db=db,
        organization_id=request.organization_id,
        name=request.name,
        scopes=request.scopes,
        expires_in_days=request.expires_in_days,
    )

    return APIKeyResponse(
        api_key=key_data["api_key"],
        key_id=key_data["key_id"],
        organization_id=key_data["organization_id"],
        tier=str(org.tier),
        created_at=key_data["created_at"],
        expires_at=key_data["expires_at"],
    )


@router.get("/api-keys", response_model=APIKeyListResponse, summary="List API Keys", description="List all API keys for an organization")
async def list_api_keys(
    organization_id: str = Query(..., description="Organization identifier"),
    db: AsyncSession = Depends(get_db),
    x_provisioning_token: str = Header(None, description="Provisioning token (optional)"),
    # TODO: Add authentication dependency
) -> APIKeyListResponse:
    """
    List API keys for an organization.

    Args:
        db: Database session

    Returns:
        List of API keys
    """
    _require_provisioning_token(x_provisioning_token)

    org_row = await db.execute(text("SELECT id FROM organizations WHERE id = :org_id"), {"org_id": organization_id})
    if not org_row.fetchone():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    keys = await ProvisioningService.list_api_keys(db, organization_id)

    return APIKeyListResponse(keys=keys, total=len(keys))


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Revoke API Key", description="Revoke an API key")
async def revoke_api_key(
    key_id: str,
    request: APIKeyRevokeRequest,
    db: AsyncSession = Depends(get_db),
    x_provisioning_token: str = Header(None, description="Provisioning token (optional)"),
    # TODO: Add authentication dependency
):
    """
    Revoke an API key.

    Args:
        key_id: API key identifier
        request: Revocation request
        db: Database session
    """
    _require_provisioning_token(x_provisioning_token)

    org_row = await db.execute(text("SELECT id FROM organizations WHERE id = :org_id"), {"org_id": request.organization_id})
    if not org_row.fetchone():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    success = await ProvisioningService.revoke_api_key(
        db=db,
        key_id=key_id,
        organization_id=request.organization_id,
        reason=request.reason,
    )

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")


# ============================================================================
# User Account Management Endpoints
# ============================================================================


@router.post(
    "/users",
    response_model=UserAccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User Account",
    description="Create a new user account",
)
async def create_user_account(
    request: UserAccountCreateRequest,
    db: AsyncSession = Depends(get_db),
    x_provisioning_token: str = Header(None, description="Provisioning token (optional)"),
) -> UserAccountResponse:
    """
    Create a new user account.

    Args:
        request: User account creation request
        db: Database session

    Returns:
        Created user account details
    """
    _require_provisioning_token(x_provisioning_token)

    # Generate user ID
    user_id = ProvisioningService.generate_user_id(request.email)

    # If no organization provided, create one
    if not request.organization_id:
        org, _, _ = await ProvisioningService.auto_provision(
            db=db, email=request.email, organization_name=None, source="api", source_metadata=None, tier="free", auto_activate=True
        )
        organization_id = org.organization_id
    else:
        organization_id = request.organization_id

    # TODO: Create user in database
    # TODO: Send welcome email if requested

    return UserAccountResponse(
        user_id=user_id,
        email=request.email,
        full_name=request.full_name,
        organization_id=organization_id,
        role=request.role or "member",
        created_at=datetime.utcnow(),
        is_active=True,
    )


# ============================================================================
# Health Check for External Services
# ============================================================================


@router.get("/health", summary="Provisioning Service Health", description="Check if provisioning service is available")
async def provisioning_health():
    """
    Health check for provisioning service.

    Returns:
        Service status
    """
    return {
        "status": "healthy",
        "service": "provisioning",
        "version": "1.0.0",
        "endpoints": {
            "auto_provision": "/api/v1/provisioning/auto-provision",
            "api_keys": "/api/v1/provisioning/api-keys",
            "users": "/api/v1/provisioning/users",
        },
    }
