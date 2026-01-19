"""
Unit tests for Public API Rate Limiter.
"""

import time
from unittest.mock import Mock

import pytest
from fastapi import HTTPException, Request

from app.middleware.public_rate_limiter import PublicAPIRateLimiter


class TestPublicAPIRateLimiter:
    """Test public API rate limiter."""

    def test_rate_limiter_initialization(self):
        """Test rate limiter initializes correctly."""
        limiter = PublicAPIRateLimiter()

        assert limiter.requests == {}
        assert limiter.violations == {}

    def test_get_client_ip_direct(self):
        """Test getting client IP from direct connection."""
        limiter = PublicAPIRateLimiter()

        # Mock request
        request = Mock(spec=Request)
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        ip = limiter._get_client_ip(request)

        assert ip == "192.168.1.1"

    def test_get_client_ip_forwarded(self):
        """Test getting client IP from X-Forwarded-For header."""
        limiter = PublicAPIRateLimiter(trusted_proxy_ips={"192.168.1.1"})

        # Mock request
        request = Mock(spec=Request)
        request.headers = {"X-Forwarded-For": "10.0.0.1, 192.168.1.1"}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        ip = limiter._get_client_ip(request)

        assert ip == "10.0.0.1"

    def test_get_client_ip_real_ip(self):
        """Test getting client IP from X-Real-IP header."""
        limiter = PublicAPIRateLimiter(trusted_proxy_ips={"192.168.1.1"})

        # Mock request
        request = Mock(spec=Request)
        request.headers = {"X-Real-IP": "10.0.0.2"}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        ip = limiter._get_client_ip(request)

        assert ip == "10.0.0.2"

    def test_check_rate_limit_within_limit(self):
        """Test rate limit check when within limits."""
        limiter = PublicAPIRateLimiter()

        # Mock request
        request = Mock(spec=Request)
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        # Should allow first request
        allowed, error, retry_after = limiter.check_rate_limit(request, "verify_single")

        assert allowed is True
        assert error is None
        assert retry_after is None

    def test_check_rate_limit_exceeded(self):
        """Test rate limit check when limit exceeded."""
        limiter = PublicAPIRateLimiter()

        # Override limits for testing
        limiter.ENDPOINT_LIMITS["test"] = {"requests_per_hour": 2, "window_seconds": 10}

        # Mock request
        request = Mock(spec=Request)
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        # Make requests up to limit
        for _ in range(2):
            allowed, _, _ = limiter.check_rate_limit(request, "test")
            assert allowed is True

        # Next request should be denied
        allowed, error, retry_after = limiter.check_rate_limit(request, "test")

        assert allowed is False
        assert "Rate limit exceeded" in error
        assert retry_after is not None
        assert retry_after <= 10

    def test_check_rate_limit_different_ips(self):
        """Test that different IPs have separate limits."""
        limiter = PublicAPIRateLimiter()

        # Override limits for testing
        limiter.ENDPOINT_LIMITS["test"] = {"requests_per_hour": 1, "window_seconds": 10}

        # Mock requests from different IPs
        request1 = Mock(spec=Request)
        request1.headers = {}
        request1.client = Mock()
        request1.client.host = "192.168.1.1"

        request2 = Mock(spec=Request)
        request2.headers = {}
        request2.client = Mock()
        request2.client.host = "192.168.1.2"

        # Both should be allowed
        allowed1, _, _ = limiter.check_rate_limit(request1, "test")
        allowed2, _, _ = limiter.check_rate_limit(request2, "test")

        assert allowed1 is True
        assert allowed2 is True

    def test_check_rate_limit_different_endpoints(self):
        """Test that different endpoints have separate limits."""
        limiter = PublicAPIRateLimiter()

        # Override limits for testing
        limiter.ENDPOINT_LIMITS["test1"] = {"requests_per_hour": 1, "window_seconds": 10}
        limiter.ENDPOINT_LIMITS["test2"] = {"requests_per_hour": 1, "window_seconds": 10}

        # Mock request
        request = Mock(spec=Request)
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        # Both should be allowed (different endpoints)
        allowed1, _, _ = limiter.check_rate_limit(request, "test1")
        allowed2, _, _ = limiter.check_rate_limit(request, "test2")

        assert allowed1 is True
        assert allowed2 is True

    def test_cleanup_old_entries(self):
        """Test that old entries are cleaned up."""
        limiter = PublicAPIRateLimiter()

        # Create entries with old timestamps
        entries = [
            (time.time() - 100, 1),  # Old
            (time.time() - 5, 1),  # Recent
            (time.time(), 1),  # Current
        ]

        cleaned = limiter._cleanup_old_entries(entries, window_seconds=10)

        # Should only keep recent entries
        assert len(cleaned) == 2

    def test_reset_ip(self):
        """Test resetting rate limit for an IP."""
        limiter = PublicAPIRateLimiter()

        # Mock request
        request = Mock(spec=Request)
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        # Make a request
        limiter.check_rate_limit(request, "verify_single")

        # Verify entry exists
        assert len(limiter.requests) > 0

        # Reset
        limiter.reset_ip("192.168.1.1")

        # Verify entries cleared
        assert len(limiter.requests) == 0

    def test_get_stats_for_ip(self):
        """Test getting stats for a specific IP."""
        limiter = PublicAPIRateLimiter()

        # Mock request
        request = Mock(spec=Request)
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        # Make requests
        for _ in range(3):
            limiter.check_rate_limit(request, "verify_single")

        # Get stats
        stats = limiter.get_stats("192.168.1.1")

        assert stats["ip_address"] == "192.168.1.1"
        assert "endpoints" in stats
        assert "verify_single" in stats["endpoints"]
        assert stats["endpoints"]["verify_single"]["requests_in_window"] == 3

    def test_get_stats_global(self):
        """Test getting global stats."""
        limiter = PublicAPIRateLimiter()

        # Mock requests from different IPs
        for i in range(3):
            request = Mock(spec=Request)
            request.headers = {}
            request.client = Mock()
            request.client.host = f"192.168.1.{i}"
            limiter.check_rate_limit(request, "verify_single")

        # Get global stats
        stats = limiter.get_stats()

        assert stats["total_tracked_ips"] == 3

    @pytest.mark.asyncio
    async def test_middleware_callable_allowed(self):
        """Test middleware callable when request is allowed."""
        limiter = PublicAPIRateLimiter()

        # Mock request
        request = Mock(spec=Request)
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        # Should not raise exception
        await limiter(request, "verify_single")

    @pytest.mark.asyncio
    async def test_middleware_callable_denied(self):
        """Test middleware callable when request is denied."""
        limiter = PublicAPIRateLimiter()

        # Override limits for testing
        limiter.ENDPOINT_LIMITS["test"] = {"requests_per_hour": 1, "window_seconds": 10}

        # Mock request
        request = Mock(spec=Request)
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        # First request should succeed
        await limiter(request, "test")

        # Second request should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await limiter(request, "test")

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
