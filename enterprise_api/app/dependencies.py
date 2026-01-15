"""
Dependencies for FastAPI endpoints (authentication, rate limiting, etc.).

Unified Authentication Architecture:
- All API key validation goes through Key Service /validate endpoint
- Key Service returns organization context with tier and features
- Features are used for tier-gating (team_management, audit_logs, etc.)
- Demo keys are supported for local development when Key Service is unavailable
"""

import inspect
import logging
from typing import Dict

from fastapi import BackgroundTasks, Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.services.key_service_client import key_service_client

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


async def get_current_organization_dep(
    request: Request,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> Dict:
    maybe_org = get_current_organization(
        request=request,
        background_tasks=background_tasks,
        credentials=credentials,
    )
    return await maybe_org if inspect.isawaitable(maybe_org) else maybe_org

# Demo key configurations for local testing (when Key Service unavailable)
# These match the seeded test organizations
DEMO_KEYS = {
    "demo-api-key-for-testing": {
        "organization_id": "org_demo",
        "organization_name": "Demo Organization",
        "tier": "enterprise",  # Demo has all features
        "is_demo": True,
        "features": {
            "team_management": True,
            "audit_logs": True,
            "merkle_enabled": True,
            "bulk_operations": True,
            "sentence_tracking": True,
            "streaming": True,
            "byok": True,
            "sso": True,
            "custom_assertions": True,
            "max_team_members": -1,
        },
        "permissions": ["sign", "verify", "lookup"],
        "monthly_api_limit": 100000,
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": 65,
    },
    "starter-api-key-for-testing": {
        "organization_id": "org_starter",
        "organization_name": "Starter Test Organization",
        "tier": "starter",
        "is_demo": True,
        "features": {
            "team_management": False,
            "audit_logs": False,
            "merkle_enabled": False,
            "bulk_operations": False,
            "sentence_tracking": False,
            "streaming": False,
            "byok": False,
            "sso": False,
            "custom_assertions": False,
            "max_team_members": 1,
        },
        "permissions": ["sign", "verify"],
        "monthly_api_limit": 10000,
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": 65,
    },
    "professional-api-key-for-testing": {
        "organization_id": "org_professional",
        "organization_name": "Professional Test Organization",
        "tier": "professional",
        "is_demo": True,
        "features": {
            "team_management": False,
            "audit_logs": False,
            "merkle_enabled": False,
            "bulk_operations": False,
            "sentence_tracking": True,
            "streaming": True,
            "byok": False,
            "sso": False,
            "custom_assertions": False,
            "max_team_members": 5,
        },
        "permissions": ["sign", "verify", "lookup"],
        "monthly_api_limit": 100000,
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": 70,
    },
    "business-api-key-for-testing": {
        "organization_id": "org_business",
        "organization_name": "Business Test Organization",
        "tier": "business",
        "is_demo": True,
        "user_id": "usr_business_owner",
        "api_key_owner_id": "usr_business_owner",
        "features": {
            "team_management": True,
            "audit_logs": True,
            "merkle_enabled": True,
            "bulk_operations": True,
            "sentence_tracking": True,
            "streaming": True,
            "byok": True,
            "sso": False,
            "custom_assertions": True,
            "max_team_members": 10,
        },
        "permissions": ["sign", "verify", "lookup"],
        "monthly_api_limit": 500000,
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": 80,
    },
    "enterprise-api-key-for-testing": {
        "organization_id": "org_enterprise",
        "organization_name": "Enterprise Test Organization",
        "tier": "enterprise",
        "is_demo": True,
        "user_id": "usr_enterprise_owner",
        "api_key_owner_id": "usr_enterprise_owner",
        "features": {
            "team_management": True,
            "audit_logs": True,
            "merkle_enabled": True,
            "bulk_operations": True,
            "sentence_tracking": True,
            "streaming": True,
            "byok": True,
            "sso": True,
            "custom_assertions": True,
            "max_team_members": -1,
        },
        "permissions": ["sign", "verify", "lookup"],
        "monthly_api_limit": -1,  # Unlimited
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": 85,
    },
    # Marketing site production key - starter tier for public tools
    "ency_marketing_site_prod_2026": {
        "organization_id": "org_encypher_marketing",
        "organization_name": "Encypher Corporation - Marketing Site",
        "tier": "starter",
        "is_demo": True,  # Uses shared demo key (no database record needed)
        "user_id": "usr_encypher_marketing",
        "api_key_owner_id": "usr_encypher_marketing",
        "features": {
            "team_management": False,
            "audit_logs": False,
            "merkle_enabled": False,
            "bulk_operations": False,
            "sentence_tracking": False,
            "streaming": False,
            "byok": False,
            "sso": False,
            "custom_assertions": False,
            "max_team_members": 1,
        },
        "permissions": ["sign", "verify"],  # Basic permissions only
        "monthly_api_limit": 50000,  # Reasonable limit for public tools
        "monthly_api_usage": 0,
        "coalition_member": False,
        "coalition_rev_share": 0,
    },
}


async def get_current_organization(
    request: Request,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> Dict:
    """
    Validate API key and return organization context.
    
    Uses Key Service /validate endpoint for unified authentication.
    Falls back to demo keys for local development.
    
    Also sets request.state for metrics middleware.

    Returns:
        Dictionary containing:
        - organization_id, organization_name
        - tier (starter, professional, business, enterprise)
        - features (dict of enabled features for tier-gating)
        - permissions (list of key permissions)
        - usage limits
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = credentials.credentials
    org_context = None

    # 1. Try Key Service first (production path)
    org_context = await key_service_client.validate_key(api_key)
    
    if org_context:
        # Normalize the response to ensure consistent structure
        org_context = _normalize_org_context(org_context)
    elif api_key in DEMO_KEYS:
        # 2. Fall back to demo keys (development/testing)
        logger.debug(f"Using demo key: {api_key[:20]}...")
        org_context = _normalize_org_context(DEMO_KEYS[api_key].copy())
    elif settings.demo_api_key and api_key == settings.demo_api_key:
        # 3. Legacy demo key support (from settings)
        logger.debug("Using legacy demo key from settings")
        org_context = _normalize_org_context(DEMO_KEYS.get("demo-api-key-for-testing", {}).copy())
    else:
        # 4. Invalid key
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Set request.state for metrics middleware
    request.state.organization_id = org_context.get("organization_id")
    request.state.user_id = org_context.get("user_id") or org_context.get("api_key_owner_id")
    request.state.api_key_id = org_context.get("api_key_id")
    request.state.tier = org_context.get("tier")
    
    return org_context


def _normalize_org_context(org_context: Dict) -> Dict:
    """Normalize organization context to ensure consistent structure."""
    # Ensure features is a dict
    features = org_context.get("features", {})
    if not isinstance(features, dict):
        features = {}
    
    # Ensure permissions is a list
    permissions = org_context.get("permissions", [])
    if not isinstance(permissions, list):
        permissions = ["sign", "verify", "lookup"]
    
    # Map permissions to can_* for backward compatibility
    result = {
        **org_context,
        "features": features,
        "permissions": permissions,
        "can_sign": "sign" in permissions,
        "can_verify": "verify" in permissions,
        "can_lookup": "lookup" in permissions,
        # Ensure quota fields exist
        "monthly_quota": org_context.get("monthly_api_limit", 10000),
        "api_calls_this_month": org_context.get("monthly_api_usage", 0),
        # Flatten feature flags for backward compatibility with routers
        # that check organization.get("feature_name_enabled")
        "team_management_enabled": features.get("team_management", False),
        "audit_logs_enabled": features.get("audit_logs", False),
        "merkle_enabled": features.get("merkle_enabled", False),
        "bulk_operations_enabled": features.get("bulk_operations", False),
        "sentence_tracking_enabled": features.get("sentence_tracking", False),
        "streaming_enabled": features.get("streaming", False),
        "byok_enabled": features.get("byok", False),
        "sso_enabled": features.get("sso", False),
        "custom_assertions_enabled": features.get("custom_assertions", False),
        "max_team_members": features.get("max_team_members", 1),
    }
    return result


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


async def require_embedding_permission(
    organization: Dict = Depends(get_current_organization),
) -> Dict:
    features = organization.get("features", {})
    is_super_admin = isinstance(features, dict) and features.get("is_super_admin", False)

    tier = (organization.get("tier") or "starter").lower().replace("-", "_")
    if not is_super_admin and tier not in {"professional", "business", "enterprise", "demo"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Embeddings require Professional or Enterprise tier. Please upgrade your plan.",
        )

    if not organization.get("can_sign"):
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


async def require_super_admin(
    organization: Dict,
) -> Dict:
    features = organization.get("features", {})
    if not isinstance(features, dict) or not features.get("is_super_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )
    return organization


async def require_super_admin_dep(
    organization: Dict = Depends(get_current_organization_dep),
) -> Dict:
    return await require_super_admin(organization)
