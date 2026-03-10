"""
Per-organization API rate limiting with tier-aware limits.

Rate limits per tier (requests per second):
- Starter: 10 req/s (600/min)
- Professional: 50 req/s (3000/min)
- Business: 200 req/s (12000/min)
- Enterprise: Unlimited
- Strategic Partner: Unlimited

Headers returned:
- X-RateLimit-Limit: Maximum requests per window
- X-RateLimit-Remaining: Requests remaining in current window
- X-RateLimit-Reset: Unix timestamp when window resets
- Retry-After: Seconds until rate limit resets (on 429 only)
"""

import ipaddress
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque, Dict, Optional, Tuple

from fastapi import Request

from app.config import settings
from app.core.tier_config import TIER_RATE_LIMITS_PER_SECOND  # SSOT


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""

    allowed: bool
    retry_after: Optional[int]
    remaining: int
    limit: int
    reset_at: int  # Unix timestamp


class ApiRateLimiter:
    """
    Sliding window rate limiter keyed by organization and scope.

    Supports tier-aware rate limiting with proper HTTP headers.
    """

    DIMENSION_LIMIT_FACTORS = {
        "organization": 1.0,
        "api_key": 0.5,
        "ip": 0.25,
    }

    def __init__(self, default_per_minute: int = 60):
        self.default_per_minute = default_per_minute
        self._requests: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)

    def get_tier_limit_per_minute(self, tier: Optional[str] = None) -> int:
        """
        Get rate limit per minute for a tier.

        Args:
            tier: Organization tier (starter, professional, business, enterprise, strategic_partner)

        Returns:
            Rate limit per minute (-1 for unlimited)
        """
        if not tier:
            return self.default_per_minute

        tier_lower = tier.lower().replace("-", "_")
        per_second = TIER_RATE_LIMITS_PER_SECOND.get(tier_lower, 10)

        if per_second == -1:
            return -1  # Unlimited

        return per_second * 60  # Convert to per minute

    def get_dimension_limit_per_minute(self, base_limit: int, identity_type: str) -> int:
        if base_limit == -1:
            return -1

        factor = self.DIMENSION_LIMIT_FACTORS.get(identity_type, 1.0)
        return max(1, int(base_limit * factor))

    @staticmethod
    def _parse_forwarded_ip(raw_value: Optional[str]) -> Optional[str]:
        if not raw_value:
            return None

        candidate = raw_value.split(",")[0].strip()
        if not candidate:
            return None

        try:
            ipaddress.ip_address(candidate)
        except ValueError:
            return None
        return candidate

    def resolve_client_ip(self, request: Request) -> str:
        client_host = request.client.host if request.client else "unknown"
        if client_host in settings.trusted_proxy_ips_set:
            forwarded_ip = self._parse_forwarded_ip(request.headers.get("X-Forwarded-For"))
            if forwarded_ip:
                return forwarded_ip

            real_ip = self._parse_forwarded_ip(request.headers.get("X-Real-IP"))
            if real_ip:
                return real_ip

        return client_host

    def check(
        self,
        *,
        organization_id: str,
        scope: str,
        tier: Optional[str] = None,
        per_minute: Optional[int] = None,
        identity_type: str = "organization",
        identity_value: Optional[str] = None,
    ) -> Tuple[bool, Optional[int], int, int]:
        """
        Check if request is within rate limits.

        Args:
            organization_id: Organization identifier
            scope: Rate limit scope (e.g., "sign", "verify", "batch_sign")
            tier: Organization tier for tier-aware limits
            per_minute: Override rate limit (optional)

        Returns:
            Tuple of (allowed, retry_after_seconds, remaining, limit)
        """
        # Determine limit: explicit override > tier-based > default
        if per_minute is not None:
            limit = per_minute
        elif tier:
            limit = self.get_tier_limit_per_minute(tier)
        else:
            limit = self.default_per_minute

        limit = self.get_dimension_limit_per_minute(limit, identity_type)

        # Unlimited tier
        if limit == -1:
            return True, None, -1, -1

        limiter_identity = identity_value or organization_id
        key = (f"{identity_type}:{limiter_identity}", scope)
        now = time.time()
        window_start = now - 60
        dq = self._requests[key]

        # Clean old entries
        while dq and dq[0] < window_start:
            dq.popleft()

        if len(dq) >= limit:
            retry_after = max(1, int(dq[0] + 60 - now))
            return False, retry_after, 0, limit

        dq.append(now)
        remaining = max(0, limit - len(dq))
        return True, None, remaining, limit

    def check_with_reset(
        self,
        *,
        organization_id: str,
        scope: str,
        tier: Optional[str] = None,
        per_minute: Optional[int] = None,
        identity_type: str = "organization",
        identity_value: Optional[str] = None,
    ) -> RateLimitResult:
        """
        Check rate limit and return full result with reset timestamp.

        Args:
            organization_id: Organization identifier
            scope: Rate limit scope
            tier: Organization tier
            per_minute: Override rate limit

        Returns:
            RateLimitResult with all rate limit info
        """
        allowed, retry_after, remaining, limit = self.check(
            organization_id=organization_id,
            scope=scope,
            tier=tier,
            per_minute=per_minute,
            identity_type=identity_type,
            identity_value=identity_value,
        )

        # Calculate reset timestamp (end of current 60-second window)
        now = time.time()
        reset_at = int(now) + 60 - (int(now) % 60)

        return RateLimitResult(
            allowed=allowed,
            retry_after=retry_after,
            remaining=remaining,
            limit=limit,
            reset_at=reset_at,
        )

    def check_request_limits(
        self,
        *,
        request: Request,
        organization_id: str,
        scope: str,
        tier: Optional[str] = None,
        per_minute: Optional[int] = None,
        api_key_prefix: Optional[str] = None,
    ) -> Tuple[RateLimitResult, str]:
        primary_result: Optional[RateLimitResult] = None
        dimensions = [
            ("organization", organization_id),
            ("api_key", api_key_prefix),
            ("ip", self.resolve_client_ip(request)),
        ]

        for identity_type, identity_value in dimensions:
            if not identity_value:
                continue

            result = self.check_with_reset(
                organization_id=organization_id,
                scope=scope,
                tier=tier,
                per_minute=per_minute,
                identity_type=identity_type,
                identity_value=identity_value,
            )

            if identity_type == "organization":
                primary_result = result

            if not result.allowed:
                return result, identity_type

        if primary_result is None:
            primary_result = self.check_with_reset(
                organization_id=organization_id,
                scope=scope,
                tier=tier,
                per_minute=per_minute,
            )

        return primary_result, "organization"

    def get_headers(self, result: RateLimitResult) -> Dict[str, str]:
        """
        Get HTTP headers for rate limit response.

        Args:
            result: Rate limit check result

        Returns:
            Dictionary of HTTP headers
        """
        headers = {}

        if result.limit != -1:  # Not unlimited
            headers["X-RateLimit-Limit"] = str(result.limit)
            headers["X-RateLimit-Remaining"] = str(max(0, result.remaining))
            headers["X-RateLimit-Reset"] = str(result.reset_at)

        if not result.allowed and result.retry_after:
            headers["Retry-After"] = str(result.retry_after)

        return headers


api_rate_limiter = ApiRateLimiter(default_per_minute=settings.rate_limit_per_minute)
