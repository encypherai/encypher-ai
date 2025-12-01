"""
Rate Limiting Middleware for Public Embedding Verification API.

Implements rate limiting for public endpoints that don't require authentication.
Uses in-memory storage with sliding window algorithm.

For production, consider upgrading to Redis-based rate limiting.
"""
import logging
import time
from typing import Dict, Optional, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status

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
        "verify_single": {
            "requests_per_hour": 1000,
            "window_seconds": 3600
        },
        "verify_batch": {
            "requests_per_hour": 100,
            "window_seconds": 3600
        },
        "default": {
            "requests_per_hour": 500,
            "window_seconds": 3600
        }
    }
    
    def __init__(self):
        """Initialize rate limiter."""
        # Track requests: {(ip, endpoint): [(timestamp, count), ...]}
        self.requests: Dict[Tuple[str, str], list] = defaultdict(list)
        
        # Track violations for potential blocking
        self.violations: Dict[str, int] = defaultdict(int)
        
        logger.info("PublicAPIRateLimiter initialized")
    
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
        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection IP
        return request.client.host if request.client else "unknown"
    
    def check_rate_limit(
        self,
        request: Request,
        endpoint_type: str = "default"
    ) -> Tuple[bool, Optional[str], Optional[int]]:
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
        limits = self.ENDPOINT_LIMITS.get(
            endpoint_type,
            self.ENDPOINT_LIMITS["default"]
        )
        max_requests = limits["requests_per_hour"]
        window_seconds = limits["window_seconds"]
        
        # Create key
        key = (client_ip, endpoint_type)
        
        # Cleanup old entries
        self.requests[key] = self._cleanup_old_entries(
            self.requests[key],
            window_seconds
        )
        
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
            
            return (
                False,
                f"Rate limit exceeded: {max_requests} requests per hour",
                retry_after
            )
        
        # Record this request
        self.requests[key].append((time.time(), 1))
        
        return True, None, None
    
    def get_rate_limit_headers(
        self,
        request: Request,
        endpoint_type: str = "default"
    ) -> Dict[str, str]:
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

    async def __call__(
        self,
        request: Request,
        endpoint_type: str = "default"
    ) -> Dict[str, str]:
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
        allowed, error_msg, retry_after = self.check_rate_limit(request, endpoint_type)
        headers = self.get_rate_limit_headers(request, endpoint_type)
        
        if not allowed:
            if retry_after:
                headers["Retry-After"] = str(retry_after)
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_msg,
                headers=headers
            )
        
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
    
    def get_stats(self, ip_address: Optional[str] = None) -> Dict:
        """
        Get rate limiting statistics.
        
        Args:
            ip_address: Optional IP address to get stats for
            
        Returns:
            Statistics dictionary
        """
        if ip_address:
            stats = {
                "ip_address": ip_address,
                "violations": self.violations.get(ip_address, 0),
                "endpoints": {}
            }
            
            for (ip, endpoint), entries in self.requests.items():
                if ip == ip_address:
                    # Cleanup and count
                    limits = self.ENDPOINT_LIMITS.get(endpoint, self.ENDPOINT_LIMITS["default"])
                    cleaned = self._cleanup_old_entries(entries, limits["window_seconds"])
                    count = sum(c for _, c in cleaned)
                    
                    stats["endpoints"][endpoint] = {
                        "requests_in_window": count,
                        "limit": limits["requests_per_hour"],
                        "window_seconds": limits["window_seconds"]
                    }
            
            return stats
        else:
            # Global stats
            return {
                "total_tracked_ips": len(set(ip for ip, _ in self.requests.keys())),
                "total_violations": sum(self.violations.values()),
                "top_violators": sorted(
                    self.violations.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }
    
    def cleanup_all(self) -> None:
        """Cleanup all old entries across all IPs."""
        for key in list(self.requests.keys()):
            endpoint_type = key[1]
            limits = self.ENDPOINT_LIMITS.get(endpoint_type, self.ENDPOINT_LIMITS["default"])
            self.requests[key] = self._cleanup_old_entries(
                self.requests[key],
                limits["window_seconds"]
            )
            
            # Remove empty entries
            if not self.requests[key]:
                del self.requests[key]
        
        logger.debug("Cleaned up all old rate limit entries")


# Global rate limiter instance
public_rate_limiter = PublicAPIRateLimiter()
