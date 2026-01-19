"""
Tier-based access control middleware.

Validates organization tier and feature access for enterprise endpoints.
"""

import logging
from typing import Callable, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.models.organization import OrganizationTier

logger = logging.getLogger(__name__)


class TierCheckMiddleware:
    """
    Middleware to check organization tier and feature access.

    This middleware:
    1. Identifies the organization from the request
    2. Checks if the organization has access to the requested feature
    3. Returns 403 Forbidden if access is denied
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        """Process the request through tier checking."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Check if this is an enterprise endpoint
        if self._is_enterprise_endpoint(request.url.path):
            # Get organization from request (would come from auth)
            org_tier = self._get_organization_tier(request)

            # Check if tier has access
            if not self._has_feature_access(request.url.path, org_tier):
                response = JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "success": False,
                        "error": "FeatureNotAvailable",
                        "message": f"This feature requires {self._get_required_tier(request.url.path)} tier or higher",
                        "details": {
                            "current_tier": org_tier.value if org_tier else "unknown",
                            "required_tier": self._get_required_tier(request.url.path),
                            "upgrade_url": "/api/v1/onboarding/upgrade",
                        },
                    },
                )
                await response(scope, receive, send)
                return

        # Continue to next middleware/endpoint
        await self.app(scope, receive, send)

    def _is_enterprise_endpoint(self, path: str) -> bool:
        """Check if the path is an enterprise endpoint."""
        enterprise_prefixes = [
            "/api/v1/enterprise/merkle",
            "/api/v1/enterprise/advanced",
        ]
        return any(path.startswith(prefix) for prefix in enterprise_prefixes)

    def _get_organization_tier(self, request: Request) -> Optional[OrganizationTier]:
        """
        Get organization tier from request.

        In production, this would extract the organization from:
        - JWT token
        - API key
        - Session

        For now, returns a default for testing.
        """
        tier_value = getattr(request.state, "tier", None)
        if not tier_value:
            return None

        if isinstance(tier_value, OrganizationTier):
            return tier_value

        try:
            return OrganizationTier(str(tier_value))
        except ValueError:
            return None

    def _has_feature_access(self, path: str, tier: Optional[OrganizationTier]) -> bool:
        """Check if the tier has access to the feature."""
        if tier is None:
            return False

        required_tier = self._get_required_tier(path)

        # Tier hierarchy: STARTER < PROFESSIONAL < ENTERPRISE
        tier_levels = {"starter": 0, "professional": 1, "enterprise": 2}

        current_level = tier_levels.get(tier.value, -1)
        required_level = tier_levels.get(required_tier, 999)

        return current_level >= required_level

    def _get_required_tier(self, path: str) -> str:
        """Get the required tier for a path."""
        # Merkle tree features require enterprise tier
        if "/enterprise/merkle" in path:
            return "enterprise"

        # Default to professional for other enterprise endpoints
        if "/enterprise/" in path:
            return "professional"

        return "starter"


def check_tier_access(required_tier: OrganizationTier, feature_name: str) -> Callable:
    """
    Dependency to check tier access for specific endpoints.

    Usage:
        @router.post("/endpoint", dependencies=[Depends(check_tier_access(OrganizationTier.ENTERPRISE, "merkle_trees"))])
        async def endpoint():
            ...

    Args:
        required_tier: Minimum tier required
        feature_name: Name of the feature for error messages

    Returns:
        Dependency function
    """

    async def dependency(request: Request):
        """Check if organization has required tier."""
        tier_value = getattr(request.state, "tier", None)
        if not tier_value:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")

        current_tier = tier_value if isinstance(tier_value, OrganizationTier) else OrganizationTier(str(tier_value))

        tier_levels = {OrganizationTier.FREE: 0, OrganizationTier.PROFESSIONAL: 1, OrganizationTier.ENTERPRISE: 2}

        if tier_levels.get(current_tier, -1) < tier_levels.get(required_tier, 999):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FeatureNotAvailable",
                    "message": f"{feature_name} requires {required_tier.value} tier or higher",
                    "current_tier": current_tier.value,
                    "required_tier": required_tier.value,
                },
            )

        return True

    return dependency
