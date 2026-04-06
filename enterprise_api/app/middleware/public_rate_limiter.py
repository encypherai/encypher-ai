"""
Rate Limiting Middleware for Public Embedding Verification API.

Implements rate limiting for public endpoints that don't require authentication.
Uses in-memory storage with sliding window algorithm.

For production, consider upgrading to Redis-based rate limiting.
"""

import ipaddress
import logging
import time
import uuid
from collections import defaultdict
from typing import Any, Dict, Optional, Set, Tuple

from fastapi import HTTPException, Request, status

from app.config import settings
from app.services.session_service import session_service

logger = logging.getLogger(__name__)


class PublicAPIRateLimiter:
    """
    Rate limiter for public API endpoints.

    Features:
    - IP-based rate limiting
    - Sliding window algorithm
    - Configurable limits per endpoint
    - Automatic cleanup of old entries
    """

    # Rate limits by endpoint type (requests per time window)
    ENDPOINT_LIMITS = {
        "verify_single": {"requests_per_hour": 1000, "window_seconds": 3600},
        "verify_batch": {"requests_per_hour": 100, "window_seconds": 3600},
        "verify_image": {"requests_per_hour": 120, "window_seconds": 3600},
        "verify_rich": {"requests_per_hour": 240, "window_seconds": 3600},
        "c2pa_validate_manifest": {"requests_per_hour": 10, "window_seconds": 60},
        "c2pa_create_manifest": {"requests_per_hour": 10, "window_seconds": 60},
        "trust_anchor_lookup": {"requests_per_hour": 100, "window_seconds": 60},
        "prebid_sign": {"requests_per_hour": 60, "window_seconds": 3600},
        "default": {"requests_per_hour": 500, "window_seconds": 3600},
    }

    def __init__(self, trusted_proxy_ips: Optional[Set[str]] = None):
        """Initialize rate limiter."""
        # Track requests: {(ip, endpoint): [(timestamp, count), ...]}
        self.requests: Dict[Tuple[str, str], list] = defaultdict(list)

        # Track violations for potential blocking
        self.violations: Dict[str, int] = defaultdict(int)

        self.trusted_proxy_ips: Set[str] = set(trusted_proxy_ips or set())
        self.redis_prefix = "encypher:public-rate-limit:"

        logger.info("PublicAPIRateLimiter initialized")

    def _redis_key(self, client_ip: str, endpoint_type: str) -> str:
        return f"{self.redis_prefix}{endpoint_type}:{client_ip}"

    async def _check_rate_limit_redis(self, request: Request, endpoint_type: str) -> Tuple[bool, Optional[str], Optional[int], Dict[str, str]]:
        client_ip = self._get_client_ip(request)
        limits = self.ENDPOINT_LIMITS.get(endpoint_type, self.ENDPOINT_LIMITS["default"])
        max_requests = limits["requests_per_hour"]
        window_seconds = limits["window_seconds"]
        redis_client = session_service.redis_client

        if not settings.public_rate_limit_use_redis or redis_client is None:
            allowed, error_msg, retry_after = self.check_rate_limit(request, endpoint_type)
            headers = self.get_rate_limit_headers(request, endpoint_type)
            return allowed, error_msg, retry_after, headers

        key = self._redis_key(client_ip, endpoint_type)
        now = time.time()
        member = f"{now}:{uuid.uuid4().hex}"
        response = await redis_client.eval(
            """
            local key = KEYS[1]
            local now = tonumber(ARGV[1])
            local window = tonumber(ARGV[2])
            local limit = tonumber(ARGV[3])
            local member = ARGV[4]
            redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window)
            local count = redis.call('ZCARD', key)
            local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
            if count >= limit then
                local retry_after = window
                local reset_at = math.ceil(now + window)
                if oldest[2] ~= nil then
                    retry_after = math.max(1, math.ceil((tonumber(oldest[2]) + window) - now))
                    reset_at = math.ceil(tonumber(oldest[2]) + window)
                end
                return {0, retry_after, 0, limit, reset_at}
            end
            redis.call('ZADD', key, now, member)
            redis.call('EXPIRE', key, math.max(1, math.ceil(window)))
            local remaining = math.max(0, limit - count - 1)
            oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
            local reset_at = math.ceil(now + window)
            if oldest[2] ~= nil then
                reset_at = math.ceil(tonumber(oldest[2]) + window)
            end
            return {1, -1, remaining, limit, reset_at}
            """,
            1,
            key,
            now,
            window_seconds,
            max_requests,
            member,
        )

        allowed = bool(int(response[0]))
        retry_after = None if int(response[1]) < 0 else int(response[1])
        headers = {
            "X-RateLimit-Limit": str(int(response[3])),
            "X-RateLimit-Remaining": str(max(0, int(response[2]))),
            "X-RateLimit-Reset": str(int(response[4])),
        }
        if allowed:
            return True, None, None, headers

        self.violations[client_ip] += 1
        logger.warning(
            f"Rate limit exceeded for IP {client_ip} on {endpoint_type}: "
            f"{max_requests}/{max_requests} in {window_seconds}s "
            f"(violations: {self.violations[client_ip]})"
        )
        return False, f"Rate limit exceeded: {max_requests} requests per hour", retry_after, headers

    def _cleanup_old_entries(self, entries: list, window_seconds: int) -> list:
        """
        Remove entries older than the time window.

        Args:
            entries: List of (timestamp, count) tuples
            window_seconds: Time window in seconds

        Returns:
            Cleaned list of entries
        """
        cutoff = time.time() - window_seconds
        return [(ts, count) for ts, count in entries if ts > cutoff]

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request.

        Args:
            request: FastAPI request

        Returns:
            Client IP address
        """
        client_host = request.client.host if request.client else "unknown"
        if client_host in self.trusted_proxy_ips:
            forwarded_ip = self._parse_forwarded_ip(request.headers.get("X-Forwarded-For"))
            if forwarded_ip:
                return forwarded_ip

            real_ip = self._parse_forwarded_ip(request.headers.get("X-Real-IP"))
            if real_ip:
                return real_ip

        return client_host

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

    def check_rate_limit(self, request: Request, endpoint_type: str = "default") -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Check if request is within rate limits.

        Args:
            request: FastAPI request
            endpoint_type: Type of endpoint (verify_single, verify_batch, default)

        Returns:
            Tuple of (allowed, error_message, retry_after_seconds)
        """
        # Get client IP
        client_ip = self._get_client_ip(request)

        # Get rate limits for endpoint
        limits = self.ENDPOINT_LIMITS.get(endpoint_type, self.ENDPOINT_LIMITS["default"])
        max_requests = limits["requests_per_hour"]
        window_seconds = limits["window_seconds"]

        # Create key
        key = (client_ip, endpoint_type)

        # Cleanup old entries
        self.requests[key] = self._cleanup_old_entries(self.requests[key], window_seconds)

        # Count requests in window
        request_count = sum(count for _, count in self.requests[key])

        if request_count >= max_requests:
            # Calculate retry-after
            if self.requests[key]:
                oldest_timestamp = min(ts for ts, _ in self.requests[key])
                retry_after = int(window_seconds - (time.time() - oldest_timestamp))
            else:
                retry_after = window_seconds

            # Track violation
            self.violations[client_ip] += 1

            logger.warning(
                f"Rate limit exceeded for IP {client_ip} on {endpoint_type}: "
                f"{request_count}/{max_requests} in {window_seconds}s "
                f"(violations: {self.violations[client_ip]})"
            )

            return (False, f"Rate limit exceeded: {max_requests} requests per hour", retry_after)

        # Record this request
        self.requests[key].append((time.time(), 1))

        return True, None, None

    def get_rate_limit_headers(self, request: Request, endpoint_type: str = "default") -> Dict[str, str]:
        """
        Get rate limit headers for a request.

        Args:
            request: FastAPI request
            endpoint_type: Type of endpoint

        Returns:
            Dictionary of rate limit headers
        """
        client_ip = self._get_client_ip(request)
        limits = self.ENDPOINT_LIMITS.get(endpoint_type, self.ENDPOINT_LIMITS["default"])
        max_requests = limits["requests_per_hour"]
        window_seconds = limits["window_seconds"]

        key = (client_ip, endpoint_type)

        # Cleanup and count
        self.requests[key] = self._cleanup_old_entries(self.requests[key], window_seconds)
        request_count = sum(count for _, count in self.requests[key])
        remaining = max(0, max_requests - request_count)

        # Calculate reset time
        reset_at = int(time.time()) + window_seconds

        return {
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_at),
        }

    async def __call__(self, request: Request, endpoint_type: str = "default") -> Dict[str, str]:
        """
        Middleware callable for FastAPI.

        Args:
            request: FastAPI request
            endpoint_type: Type of endpoint

        Returns:
            Rate limit headers dictionary

        Raises:
            HTTPException: If rate limit exceeded
        """
        allowed, error_msg, retry_after, headers = await self._check_rate_limit_redis(request, endpoint_type)

        if not allowed:
            if retry_after:
                headers["Retry-After"] = str(retry_after)

            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=error_msg, headers=headers)

        return headers

    def reset_ip(self, ip_address: str) -> None:
        """
        Reset rate limiting for an IP address.

        Args:
            ip_address: IP address to reset
        """
        # Remove all entries for this IP
        keys_to_remove = [key for key in self.requests if key[0] == ip_address]
        for key in keys_to_remove:
            del self.requests[key]

        # Reset violations
        if ip_address in self.violations:
            del self.violations[ip_address]

        logger.info(f"Reset rate limiting for IP {ip_address}")

    def get_stats(self, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get rate limiting statistics.

        Args:
            ip_address: Optional IP address to get stats for

        Returns:
            Statistics dictionary
        """
        if ip_address:
            endpoints: Dict[str, Dict[str, int]] = {}
            stats: Dict[str, Any] = {
                "ip_address": ip_address,
                "violations": self.violations.get(ip_address, 0),
                "endpoints": endpoints,
            }

            for (ip, endpoint), entries in self.requests.items():
                if ip == ip_address:
                    # Cleanup and count
                    limits = self.ENDPOINT_LIMITS.get(endpoint, self.ENDPOINT_LIMITS["default"])
                    cleaned = self._cleanup_old_entries(entries, limits["window_seconds"])
                    count = sum(c for _, c in cleaned)

                    endpoints[endpoint] = {
                        "requests_in_window": count,
                        "limit": limits["requests_per_hour"],
                        "window_seconds": limits["window_seconds"],
                    }

            return stats
        else:
            # Global stats
            return {
                "total_tracked_ips": len(set(ip for ip, _ in self.requests.keys())),
                "total_violations": sum(self.violations.values()),
                "top_violators": sorted(self.violations.items(), key=lambda x: x[1], reverse=True)[:10],
            }

    def cleanup_all(self) -> None:
        """Cleanup all old entries across all IPs."""
        for key in list(self.requests.keys()):
            endpoint_type = key[1]
            limits = self.ENDPOINT_LIMITS.get(endpoint_type, self.ENDPOINT_LIMITS["default"])
            self.requests[key] = self._cleanup_old_entries(self.requests[key], limits["window_seconds"])

            # Remove empty entries
            if not self.requests[key]:
                del self.requests[key]

        logger.debug("Cleaned up all old rate limit entries")


# Global rate limiter instance
public_rate_limiter = PublicAPIRateLimiter(trusted_proxy_ips=settings.trusted_proxy_ips_set)
