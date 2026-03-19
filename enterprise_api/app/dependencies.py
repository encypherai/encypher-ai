"""
Dependencies for FastAPI endpoints (authentication, rate limiting, etc.).

Unified Authentication Architecture:
- All API key validation goes through Key Service /validate endpoint
- Key Service returns organization context with tier and features
- Features are used for tier-gating (team_management, audit_logs, etc.)
- Demo keys are supported for local development when Key Service is unavailable
"""

import inspect
import ipaddress
import logging
from typing import Dict, Optional

import httpx
from fastapi import BackgroundTasks, Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.services.auth_service_client import auth_service_client
from app.services.key_service_client import key_service_client

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


def _unauthorized_http_exception(detail: str = "Invalid API key") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _build_api_key_prefix(raw_key: str) -> str:
    """Return a safe, human-readable key prefix for telemetry."""
    trimmed = (raw_key or "").strip()
    if not trimmed:
        return ""
    return trimmed[:12]


def check_ip_allowlist(allowlist: list[str], client_ip: str) -> bool:
    """Check if a client IP is within any of the CIDR ranges in the allowlist.

    Returns True if the allowlist is empty (no restriction) or if the IP
    matches at least one entry. Returns False otherwise.

    Handles IPv4-mapped IPv6 addresses (e.g. ::ffff:10.0.0.1) by normalizing
    them to plain IPv4 before comparison.
    """
    if not allowlist:
        return True

    try:
        addr = ipaddress.ip_address(client_ip)
        # Normalize IPv4-mapped IPv6 to plain IPv4 for consistent matching
        if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:
            addr = addr.ipv4_mapped
    except ValueError:
        return False

    for cidr in allowlist:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            if addr in network:
                return True
        except ValueError:
            continue

    return False


def _get_client_ip(request: Request) -> str:
    """Extract the real client IP using rightmost-untrusted-IP from X-Forwarded-For.

    Walks the X-Forwarded-For chain from right to left, skipping trusted proxies,
    and returns the first untrusted IP. This prevents spoofing via prepended headers.
    Falls back to the direct peer IP.
    """
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for and settings.trusted_proxy_ips_set:
        peer = request.client.host if request.client else ""
        if peer in settings.trusted_proxy_ips_set:
            # Walk from right to left, skip trusted proxies
            ips = [ip.strip() for ip in forwarded_for.split(",")]
            for ip in reversed(ips):
                if ip and ip not in settings.trusted_proxy_ips_set:
                    return ip
            # All IPs in chain are trusted; use the leftmost
            if ips:
                return ips[0]
    return request.client.host if request.client else ""


def _normalize_permissions(raw_permissions: object) -> list[str]:
    if not isinstance(raw_permissions, list):
        raw_permissions = ["sign", "verify", "lookup"]

    normalized: set[str] = set()
    for permission in raw_permissions:
        if not isinstance(permission, str):
            continue

        token = permission.strip().lower().replace("-", "_")
        if not token:
            continue
        if token == "admin":
            normalized.update({"admin", "sign", "verify", "lookup", "read"})
            continue
        if token in {"lookup", "read"}:
            normalized.update({"lookup", "read"})
            continue
        normalized.add(token)

    return sorted(normalized)


async def _get_org_context_from_jwt_access_token(token: str) -> Optional[Dict]:
    """Resolve organization context from an auth-service JWT access token.

    Dashboard requests use auth-service JWTs (not API keys). For org-scoped
    enterprise API endpoints, derive org context from the user's default org.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.auth_service_url}/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0,
            )
    except httpx.RequestError:
        logger.warning("Auth service unavailable while resolving JWT org context")
        return None

    if response.status_code != status.HTTP_200_OK:
        return None

    payload = response.json()
    user = payload.get("data") if isinstance(payload, dict) and payload.get("success") else None
    if not isinstance(user, dict):
        return None

    org_id = user.get("default_organization_id")
    if not org_id:
        return None

    org_data = await auth_service_client.get_organization_context(str(org_id))
    if not org_data:
        return None

    return _normalize_org_context(
        {
            "organization_id": org_id,
            "organization_name": org_data.get("name"),
            "tier": org_data.get("tier", "free"),
            "features": org_data.get("features", {}),
            # JWT auth does not include API key scopes; use baseline app permissions.
            "permissions": ["sign", "verify", "lookup", "read"],
            "monthly_api_limit": org_data.get("monthly_api_limit"),
            "monthly_api_usage": org_data.get("monthly_api_usage"),
            "coalition_member": org_data.get("coalition_member", True),
            "coalition_rev_share": org_data.get("coalition_rev_share", DEFAULT_COALITION_PUBLISHER_PERCENT),
            "certificate_pem": org_data.get("certificate_pem"),
            "user_id": user.get("id"),
            "account_type": org_data.get("account_type"),
            "display_name": org_data.get("display_name"),
            "anonymous_publisher": org_data.get("anonymous_publisher", False),
            "add_ons": org_data.get("add_ons", {}),
            "verification_domain": org_data.get("verification_domain"),
            "status": org_data.get("status", "active"),
        }
    )


def _build_composed_org_context(key_context: Dict, org_data: Dict) -> Dict:
    return {
        "api_key_id": key_context.get("key_id"),
        "organization_id": key_context.get("organization_id"),
        "organization_name": org_data.get("name"),
        "tier": key_context.get("tier", "free"),
        "features": org_data.get("features", {}),
        "permissions": key_context.get("permissions", []),
        "monthly_api_limit": org_data.get("monthly_api_limit"),
        "monthly_api_usage": org_data.get("monthly_api_usage"),
        "coalition_member": org_data.get("coalition_member", True),
        "coalition_rev_share": org_data.get("coalition_rev_share", DEFAULT_COALITION_PUBLISHER_PERCENT),
        "certificate_pem": org_data.get("certificate_pem"),
        "user_id": key_context.get("user_id"),
        "account_type": org_data.get("account_type"),
        "display_name": org_data.get("display_name"),
        "anonymous_publisher": org_data.get("anonymous_publisher", False),
        "add_ons": org_data.get("add_ons", {}),
        "verification_domain": org_data.get("verification_domain"),
        "status": org_data.get("status", "active"),
    }


async def _resolve_org_context_via_composed_auth_service(api_key: str) -> Optional[Dict]:
    if not settings.compose_org_context_via_auth_service:
        return None

    key_context = await key_service_client.validate_key_minimal(api_key)
    if not key_context or not key_context.get("organization_id"):
        return None

    org_data = await auth_service_client.get_organization_context(str(key_context["organization_id"]))
    if not org_data:
        return None

    return _build_composed_org_context(key_context, org_data)


def _resolve_demo_org_context(api_key: str) -> Optional[Dict]:
    is_demo_candidate = api_key in DEMO_KEYS or (settings.demo_api_key and api_key == settings.demo_api_key)
    if settings.is_production and is_demo_candidate and not settings.is_demo_key_allowlisted(api_key):
        raise _unauthorized_http_exception()

    if api_key in DEMO_KEYS:
        logger.debug(f"Using demo key: {api_key[:20]}...")
        return _normalize_org_context(DEMO_KEYS[api_key].copy())

    if settings.demo_api_key and api_key == settings.demo_api_key:
        logger.debug("Using legacy demo key from settings")
        return _normalize_org_context(DEMO_KEYS.get("demo-api-key-for-testing", {}).copy())

    return None


def _set_request_auth_state(request: Request, org_context: Dict, api_key: str) -> None:
    request.state.organization_id = org_context.get("organization_id")
    request.state.user_id = org_context.get("user_id") or org_context.get("api_key_owner_id")
    request.state.api_key_id = org_context.get("api_key_id")
    request.state.api_key_prefix = _build_api_key_prefix(api_key)
    request.state.tier = org_context.get("tier")


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


# TEAM_166: Demo key features derived from tier_config SSOT
from app.core.pricing_constants import DEFAULT_COALITION_PUBLISHER_PERCENT
from app.core.tier_config import get_tier_features, get_tier_limits, get_tier_rev_share

_free_features = get_tier_features("free")
_enterprise_features = get_tier_features("enterprise")
_free_limits = get_tier_limits("free")
_enterprise_limits = get_tier_limits("enterprise")

# Demo key configurations for local testing (when Key Service unavailable)
# These match the seeded test organizations
DEMO_KEYS = {
    "demo-api-key-for-testing": {
        "organization_id": "org_demo",
        "organization_name": "Demo Organization",
        "tier": "enterprise",  # Demo has all features
        "is_demo": True,
        "features": {**_enterprise_features},
        "permissions": ["sign", "verify", "lookup"],
        "monthly_api_limit": 100000,
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": get_tier_rev_share("enterprise")["publisher"],
    },
    "starter-api-key-for-testing": {
        "organization_id": "org_free",
        "organization_name": "Free Test Organization",
        "tier": "free",
        "is_demo": True,
        "features": {**_free_features},
        "permissions": ["sign", "verify"],
        "monthly_api_limit": _free_limits["api_calls"],
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": get_tier_rev_share("free")["publisher"],
        "nma_member": False,
    },
    # NMA (News Media Alliance) member - free tier with NMA flag
    "nma-starter-api-key-for-testing": {
        "organization_id": "org_nma_free",
        "organization_name": "NMA Member Test Organization",
        "tier": "free",
        "is_demo": True,
        "features": {**_free_features},
        "permissions": ["sign", "verify"],
        "monthly_api_limit": _free_limits["api_calls"],
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": get_tier_rev_share("free")["publisher"],
        "nma_member": True,  # NMA membership flag
    },
    # Legacy key names kept for backward compat; all map to free tier
    "professional-api-key-for-testing": {
        "organization_id": "org_free_legacy_pro",
        "organization_name": "Free Test Organization (legacy pro)",
        "tier": "free",
        "is_demo": True,
        "features": {**_free_features},
        "permissions": ["sign", "verify", "lookup"],
        "monthly_api_limit": _free_limits["api_calls"],
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": get_tier_rev_share("free")["publisher"],
    },
    "business-api-key-for-testing": {
        "organization_id": "org_free_legacy_biz",
        "organization_name": "Free Test Organization (legacy biz)",
        "tier": "free",
        "is_demo": True,
        "user_id": "usr_free_legacy_biz_owner",
        "api_key_owner_id": "usr_free_legacy_biz_owner",
        "features": {**_free_features},
        "permissions": ["sign", "verify", "lookup"],
        "monthly_api_limit": _free_limits["api_calls"],
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": get_tier_rev_share("free")["publisher"],
    },
    "enterprise-api-key-for-testing": {
        "organization_id": "org_enterprise",
        "organization_name": "Enterprise Test Organization",
        "tier": "enterprise",
        "is_demo": True,
        "user_id": "usr_enterprise_owner",
        "api_key_owner_id": "usr_enterprise_owner",
        "features": {**_enterprise_features},
        "permissions": ["sign", "verify", "lookup"],
        "monthly_api_limit": -1,  # Unlimited
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": get_tier_rev_share("enterprise")["publisher"],
    },
    # Strategic partner key for testing (TEAM_222)
    "strategic-partner-api-key-for-testing": {
        "organization_id": "org_strategic_partner",
        "organization_name": "Strategic Partner Test Organization",
        "tier": "strategic_partner",
        "is_demo": True,
        "features": {**_enterprise_features},
        "permissions": ["sign", "verify", "lookup"],
        "monthly_api_limit": -1,
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": get_tier_rev_share("enterprise")["publisher"],
    },
    # Marketing site production key - free tier for public tools
    "ency_marketing_site_prod_2026": {
        "organization_id": "org_encypher_marketing",
        "organization_name": "Encypher Corporation - Marketing Site",
        "tier": "free",
        "is_demo": True,
        "user_id": "usr_encypher_marketing",
        "api_key_owner_id": "usr_encypher_marketing",
        "features": {**_free_features},
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
        raise _unauthorized_http_exception("API key required")

    api_key = credentials.credentials
    org_context = await _resolve_org_context_via_composed_auth_service(api_key)

    if org_context is None:
        org_context = await key_service_client.validate_key(api_key)

    if org_context is None:
        org_context = await _get_org_context_from_jwt_access_token(api_key)

    if org_context is not None:
        org_context = _normalize_org_context(org_context)
    else:
        org_context = _resolve_demo_org_context(api_key)
        if org_context is None:
            raise _unauthorized_http_exception()

    # Enforce organization suspension
    org_status = org_context.get("status", "active")
    if org_status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ORGANIZATION_SUSPENDED",
                "message": "This organization has been suspended. Contact support for assistance.",
            },
        )

    # Enforce IP allowlist (if set on the API key context)
    ip_allowlist = org_context.get("ip_allowlist")
    if ip_allowlist:
        client_ip = _get_client_ip(request)
        if not check_ip_allowlist(ip_allowlist, client_ip):
            logger.warning(
                "IP allowlist denied: ip=%s key_id=%s org=%s",
                client_ip,
                org_context.get("api_key_id", "unknown"),
                org_context.get("organization_id", "unknown"),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "IP_NOT_ALLOWED",
                    "message": "Request denied: your IP address is not in this key's allowlist.",
                },
            )

    _set_request_auth_state(request, org_context, api_key)

    return org_context


def _normalize_org_context(org_context: Dict) -> Dict:
    """Normalize organization context to ensure consistent structure."""
    # Ensure features is a dict
    features = org_context.get("features", {})
    if not isinstance(features, dict):
        features = {}

    # Ensure permissions is a list
    permissions = _normalize_permissions(org_context.get("permissions", []))

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
        "fuzzy_fingerprint_enabled": features.get("fuzzy_fingerprint", False),
        "max_team_members": features.get("max_team_members", 1),
        # NMA (News Media Alliance) membership - extends starter tier with sentence-level embeddings
        "nma_member": org_context.get("nma_member", False),
        # TEAM_191: Publisher identity for attribution
        "account_type": org_context.get("account_type"),
        "display_name": org_context.get("display_name"),
        "anonymous_publisher": org_context.get("anonymous_publisher", False),
        # IP allowlist for key-level restriction
        "ip_allowlist": org_context.get("ip_allowlist", []),
    }
    # TEAM_191: Build publisher identity + attribution strings
    from app.utils.publisher_attribution import build_publisher_attribution_from_org_context, build_publisher_identity_base_from_org_context

    result["publisher_identity_base"] = build_publisher_identity_base_from_org_context(result)
    result["publisher_attribution"] = build_publisher_attribution_from_org_context(result)
    return result


async def require_sign_permission(
    organization: Dict = Depends(get_current_organization),
) -> Dict:
    return await _require_permission_flag(organization, "can_sign", "Your API key does not have permission to sign content")


async def require_embedding_permission(
    organization: Dict = Depends(get_current_organization),
) -> Dict:
    return await _require_permission_flag(organization, "can_sign", "Your API key does not have permission to sign content")


async def require_verify_permission(
    organization: Dict = Depends(get_current_organization),
) -> Dict:
    return await _require_permission_flag(organization, "can_verify", "Your API key does not have permission to verify content")


async def require_lookup_permission(
    organization: Dict = Depends(get_current_organization),
) -> Dict:
    return await _require_permission_flag(organization, "can_lookup", "Your API key does not have permission to lookup sentences")


async def require_read_permission(
    organization: Dict = Depends(get_current_organization),
) -> Dict:
    return organization


async def _require_permission_flag(organization: Dict, permission_flag: str, error_detail: str) -> Dict:
    if not organization.get(permission_flag):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_detail,
        )
    return organization


async def require_super_admin(
    organization: Dict,
) -> Dict:
    features = organization.get("features", {})
    permissions = organization.get("permissions", [])
    if not isinstance(permissions, list):
        permissions = []

    is_super_admin = isinstance(features, dict) and features.get("is_super_admin", False)
    has_admin_scope = "admin" in permissions

    if not is_super_admin and not has_admin_scope:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )
    return organization


async def require_super_admin_dep(
    request: Request,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> Dict:
    if credentials is None or not credentials.credentials:
        raise _unauthorized_http_exception("API key required")

    try:
        organization = await get_current_organization_dep(
            request=request,
            background_tasks=background_tasks,
            credentials=credentials,
        )
        return await require_super_admin(organization)
    except HTTPException as exc:
        if exc.status_code != status.HTTP_401_UNAUTHORIZED:
            raise

    admin_context = await _get_super_admin_from_jwt(credentials.credentials)
    if not admin_context:
        raise

    request.state.organization_id = admin_context.get("organization_id")
    request.state.user_id = admin_context.get("user_id")
    request.state.api_key_id = admin_context.get("api_key_id")
    request.state.api_key_prefix = ""
    request.state.tier = admin_context.get("tier")
    return await require_super_admin(admin_context)


async def _get_super_admin_from_jwt(token: str) -> Optional[Dict]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.auth_service_url}/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0,
            )
    except httpx.RequestError:
        logger.warning("Auth service unavailable while verifying admin JWT")
        return None

    if response.status_code != status.HTTP_200_OK:
        return None

    payload = response.json()
    user = payload.get("data") if isinstance(payload, dict) and payload.get("success") else None
    if not isinstance(user, dict) or not user.get("is_super_admin"):
        return None

    user_id = user.get("id")
    return {
        "organization_id": f"user_{user_id}" if user_id else "user_admin",
        "organization_name": user.get("email") or "Admin",
        "tier": "enterprise",
        "features": {"is_super_admin": True},
        "permissions": ["admin", "sign", "verify", "lookup"],
        "can_sign": True,
        "can_verify": True,
        "can_lookup": True,
        "user_id": user_id,
    }
