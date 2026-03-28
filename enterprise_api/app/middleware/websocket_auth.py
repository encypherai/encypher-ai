"""
WebSocket Authentication Middleware.

Provides authentication for WebSocket connections using API keys or
JWT session tokens (dashboard auth).
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Optional

from fastapi import WebSocket, WebSocketException, status
from sqlalchemy import text

from app.config import settings
from app.database import async_session_factory
from app.dependencies import _get_org_context_from_jwt_access_token, _normalize_permissions

logger = logging.getLogger(__name__)


async def authenticate_websocket(websocket: WebSocket, api_key: Optional[str] = None) -> Dict:
    """
    Authenticate WebSocket connection using API key.

    Args:
        websocket: WebSocket connection
        api_key: API key from query parameter or header

    Returns:
        Organization details dictionary

    Raises:
        WebSocketException: If authentication fails
    """
    if not api_key:
        logger.warning("WebSocket connection attempted without API key")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="API key required")

    # Demo key bypass for local testing
    if settings.demo_api_key and api_key == settings.demo_api_key:
        if settings.is_production and not settings.is_demo_key_allowlisted(api_key):
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid API key")
        logger.info("WebSocket authenticated with demo key")
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
            "private_key_encrypted": settings.demo_private_key_bytes or b"",
        }

    # Query database for API key
    async with async_session_factory() as db:
        try:
            key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
            result = await db.execute(
                text(
                    """
                    SELECT
                        ak.id AS api_key_id,
                        ak.organization_id,
                        ak.scopes,
                        ak.expires_at,
                        ak.is_active,
                        ak.revoked_at,
                        o.name AS organization_name,
                        o.tier,
                        o.monthly_api_limit,
                        o.monthly_api_usage,
                        o.private_key_encrypted,
                        o.features
                    FROM api_keys ak
                    JOIN organizations o ON ak.organization_id = o.id
                    WHERE ak.key_hash = :key_hash
                    """
                ),
                {"key_hash": key_hash},
            )
            row = result.fetchone()

            if not row:
                # API key not found; try JWT session token fallback
                jwt_org = await _authenticate_websocket_jwt(api_key)
                if jwt_org:
                    return jwt_org
                logger.warning("WebSocket authentication failed: Invalid API key or JWT")
                raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid API key")

            # Check if revoked
            if row.revoked_at is not None or row.is_active is False:
                logger.warning("WebSocket authentication failed: Revoked API key")
                raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="API key has been revoked")

            # Check if expired
            if row.expires_at and row.expires_at < datetime.utcnow():
                logger.warning("WebSocket authentication failed: Expired API key")
                raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="API key has expired")

            # Check quota (if not on unlimited plan)
            if row.monthly_api_limit not in (-1, None) and row.monthly_api_usage >= row.monthly_api_limit:
                logger.warning(f"WebSocket authentication failed: Quota exceeded for org {row.organization_id}")
                raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Monthly API quota exceeded")

            # Check streaming permission (Professional+ tier)
            if row.tier not in ("professional", "business", "enterprise", "demo"):
                logger.warning(f"WebSocket authentication failed: Insufficient tier for org {row.organization_id}")
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="Streaming requires Professional or Enterprise tier",
                )

            # Update last_used_at timestamp
            await db.execute(
                text("UPDATE api_keys SET last_used_at = :last_used_at WHERE id = :api_key_id"),
                {"api_key_id": row.api_key_id, "last_used_at": datetime.utcnow()},
            )
            await db.commit()

            scopes = row.scopes or []
            if isinstance(scopes, str):
                scopes = json.loads(scopes)
            scopes = _normalize_permissions(scopes)

            logger.info(f"WebSocket authenticated for org {row.organization_id}")

            # Return organization details
            return {
                "api_key": api_key,
                "api_key_id": row.api_key_id,
                "organization_id": row.organization_id,
                "organization_name": row.organization_name,
                "tier": row.tier,
                "can_sign": "sign" in scopes,
                "can_verify": "verify" in scopes,
                "can_lookup": "lookup" in scopes,
                "monthly_quota": row.monthly_api_limit,
                "api_calls_this_month": row.monthly_api_usage,
                "is_demo": False,
                "private_key_encrypted": row.private_key_encrypted,
                "features": row.features if isinstance(row.features, dict) else {},
            }

        except WebSocketException:
            raise
        except Exception as e:
            logger.error(f"WebSocket authentication error: {e}", exc_info=True)
            raise WebSocketException(code=status.WS_1011_INTERNAL_ERROR, reason="Authentication error")


async def _authenticate_websocket_jwt(token: str) -> Optional[Dict]:
    """Try to authenticate a WebSocket connection via JWT session token.

    Reuses the same auth-service verification as HTTP endpoints so that
    dashboard session tokens work for WebSocket streaming.
    """
    org_context = await _get_org_context_from_jwt_access_token(token)
    if not org_context:
        return None

    org_id = org_context.get("organization_id")
    permissions = org_context.get("permissions", [])
    if isinstance(permissions, str):
        permissions = json.loads(permissions)
    permissions = _normalize_permissions(permissions)

    # Load private_key_encrypted from the org record
    private_key_encrypted = None
    try:
        async with async_session_factory() as db:
            result = await db.execute(
                text("SELECT private_key_encrypted FROM organizations WHERE id = :org_id"),
                {"org_id": org_id},
            )
            row = result.fetchone()
            if row:
                private_key_encrypted = row.private_key_encrypted
    except Exception as exc:
        logger.warning("Failed to load private key for JWT-authed org %s: %s", org_id, exc)

    logger.info("WebSocket authenticated via JWT for org %s", org_id)

    return {
        "api_key": None,
        "organization_id": org_id,
        "organization_name": org_context.get("organization_name"),
        "tier": org_context.get("tier", "free"),
        "can_sign": "sign" in permissions,
        "can_verify": "verify" in permissions,
        "can_lookup": "lookup" in permissions,
        "monthly_quota": org_context.get("monthly_api_limit"),
        "api_calls_this_month": org_context.get("monthly_api_usage", 0),
        "is_demo": False,
        "private_key_encrypted": private_key_encrypted,
        "features": org_context.get("features", {}),
    }


async def require_streaming_permission(organization: Dict) -> Dict:
    """
    Verify organization has streaming permission.

    Args:
        organization: Organization details

    Returns:
        Organization details

    Raises:
        WebSocketException: If organization lacks streaming permission
    """
    # Check tier
    if organization["tier"] not in ("professional", "enterprise", "demo"):
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Streaming requires Professional or Enterprise tier",
        )

    # Check sign permission
    if not organization["can_sign"]:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="API key does not have permission to sign content",
        )

    return organization
