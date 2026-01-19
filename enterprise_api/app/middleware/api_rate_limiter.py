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

import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque, Dict, Optional, Tuple

from app.config import settings

# Rate limits by tier (requests per second)
# These align with docs/pricing/PRICING_STRATEGY.md
TIER_RATE_LIMITS_PER_SECOND: Dict[str, int] = {
    "starter": 10,
    "professional": 50,
    "business": 200,
    "enterprise": -1,  # Unlimited
    "strategic_partner": -1,  # Unlimited
}


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

    def check(
        self,
        *,
        organization_id: str,
        scope: str,
        tier: Optional[str] = None,
        per_minute: Optional[int] = None,
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

        # Unlimited tier
        if limit == -1:
            return True, None, -1, -1

        key = (organization_id, scope)
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
