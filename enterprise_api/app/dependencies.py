"""
Dependencies for FastAPI endpoints (authentication, rate limiting, etc.).
"""
from typing import Dict

from fastapi import BackgroundTasks, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.services.key_service_client import key_service_client

security = HTTPBearer()


async def get_current_organization(
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Dict:
    """
    Validate API key and return organization details.
    
    Uses KeyServiceClient to validate against the centralized Key Service.
    Refactored to remove direct DB dependency for auth.

    Args:
        background_tasks: FastAPI background tasks
        credentials: HTTP Bearer credentials

    Returns:
        Dictionary containing organization details
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

    # Validate using Key Service Client (with caching)
    key_data = await key_service_client.validate_key(api_key)
    
    if not key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check quota (if not on unlimited plan)
    # Note: Key Service handles quota checks during validation, but we check here if returned data includes usage
    if key_data.get("tier") != "enterprise" and \
       key_data.get("api_calls_this_month", 0) >= key_data.get("monthly_quota", float('inf')):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Monthly API quota exceeded. Please upgrade your plan.",
        )

    # Update last_used_at timestamp in background (Fire and forget)
    # We still keep this local stat service call if we want local tracking,
    # OR we should move this to call Key Service's stats endpoint.
    # For now, sticking with local stats if we share DB, but since we are decoupling,
    # the Key Service should ideally handle this.
    # However, the KeyServiceClient currently only validates.
    # Let's assume the validation call implicitly tracks usage or we add an async call here.
    # For Option B strict decoupling: we should trust Key Service's validation which likely tracks usage.
    # But to maintain existing behavior of updating 'last_used_at' in OUR local DB (if it exists?),
    # or passing it upstream.
    # Since we are removing local DB dependency for auth, we shouldn't write to it here.
    
    return key_data


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


async def require_read_permission(
    organization: Dict = Depends(get_current_organization),
) -> Dict:
    """
    Require that the organization has read permission (basic authenticated access).
    
    This is a general-purpose dependency for endpoints that only require
    authentication without specific feature permissions.

    Args:
        organization: Organization details from get_current_organization

    Returns:
        Organization details (authenticated)
    """
    # Basic authentication is sufficient - organization is already validated
    return organization
