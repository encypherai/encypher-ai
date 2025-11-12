"""Per-organization API rate limiting."""
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from app.config import settings


class ApiRateLimiter:
    """Sliding window rate limiter keyed by organization and scope."""

    def __init__(self, default_per_minute: int = 60):
        self.default_per_minute = default_per_minute
        self._requests: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)

    def check(
        self,
        *,
        organization_id: str,
        scope: str,
        per_minute: int | None = None,
    ) -> Tuple[bool, int | None, int, int]:
        """
        Returns tuple (allowed, retry_after_seconds, remaining).
        """

        limit = per_minute or self.default_per_minute
        key = (organization_id, scope)
        now = time.time()
        window_start = now - 60
        dq = self._requests[key]
        while dq and dq[0] < window_start:
            dq.popleft()
        if len(dq) >= limit:
            retry_after = max(1, int(dq[0] + 60 - now))
            return False, retry_after, 0, limit
        dq.append(now)
        remaining = max(0, limit - len(dq))
        return True, None, remaining, limit


api_rate_limiter = ApiRateLimiter(default_per_minute=settings.rate_limit_per_minute)
