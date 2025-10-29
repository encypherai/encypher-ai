"""
Dependencies for FastAPI endpoints (authentication, rate limiting, etc.).
"""
from datetime import datetime
from typing import Dict

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db

security = HTTPBearer()


async def get_current_organization(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Validate API key and return organization details.

    This dependency:
    1. Extracts the API key from the Authorization header
    2. Validates the key against the database
    3. Checks if the key is revoked or expired
    4. Updates last_used_at timestamp
    5. Returns organization details

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        Dictionary containing organization details

    Raises:
        HTTPException: If API key is invalid, revoked, or expired
    """
    api_key = credentials.credentials

    # Demo key bypass for local testing
    if settings.demo_api_key and api_key == settings.demo_api_key:
        return {
            "api_key": api_key,
            "organization_id": settings.demo_organization_id,
            "organization_name": settings.demo_organization_name,
            "organization_type": "demo",
            "tier": "demo",
            "can_sign": True,
            "can_verify": True,
            "can_lookup": True,
            "monthly_quota": 10_000,
            "api_calls_this_month": 0,
            "is_demo": True,
        }

    # Query API key and join with organization
    result = await db.execute(
        text(
            """
            SELECT
                ak.api_key, ak.organization_id, ak.revoked, ak.expires_at,
                ak.can_sign, ak.can_verify, ak.can_lookup,
                o.organization_name, o.organization_type, o.tier,
                o.monthly_quota, o.api_calls_this_month
            FROM api_keys ak
            JOIN organizations o ON ak.organization_id = o.organization_id
            WHERE ak.api_key = :api_key
        """
        ),
        {"api_key": api_key},
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if revoked
    if row.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if expired
    if row.expires_at and row.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check quota (if not on unlimited plan)
    if row.tier != "enterprise" and row.api_calls_this_month >= row.monthly_quota:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Monthly API quota exceeded. Please upgrade your plan.",
        )

    # Update last_used_at timestamp
    await db.execute(
        text("UPDATE api_keys SET last_used_at = :last_used_at WHERE api_key = :api_key"),
        {"api_key": api_key, "last_used_at": datetime.utcnow()},
    )
    await db.commit()

    # Return organization details as dictionary
    return {
        "api_key": row.api_key,
        "organization_id": row.organization_id,
        "organization_name": row.organization_name,
        "organization_type": row.organization_type,
        "tier": row.tier,
        "can_sign": row.can_sign,
        "can_verify": row.can_verify,
        "can_lookup": row.can_lookup,
        "monthly_quota": row.monthly_quota,
        "api_calls_this_month": row.api_calls_this_month,
        "is_demo": False,
    }


async def require_sign_permission(
    organization: Dict = Depends(get_current_organization),
) -> Dict:
    """
    Require that the organization has sign permission.

    Args:
        organization: Organization details from get_current_organization

    Returns:
        Organization details

    Raises:
        HTTPException: If organization doesn't have sign permission
    """
    if not organization["can_sign"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your API key does not have permission to sign content",
        )
    return organization


async def require_verify_permission(
    organization: Dict = Depends(get_current_organization),
) -> Dict:
    """
    Require that the organization has verify permission.

    Args:
        organization: Organization details from get_current_organization

    Returns:
        Organization details

    Raises:
        HTTPException: If organization doesn't have verify permission
    """
    if not organization["can_verify"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your API key does not have permission to verify content",
        )
    return organization


async def require_lookup_permission(
    organization: Dict = Depends(get_current_organization),
) -> Dict:
    """
    Require that the organization has lookup permission.

    Args:
        organization: Organization details from get_current_organization

    Returns:
        Organization details

    Raises:
        HTTPException: If organization doesn't have lookup permission
    """
    if not organization["can_lookup"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your API key does not have permission to lookup sentences",
        )
    return organization
