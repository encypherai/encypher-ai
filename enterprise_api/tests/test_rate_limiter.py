"""
Tests for tier-aware rate limiting.

TEAM_002: Tests for rate limit headers and tier-based limits.
"""
import time
import pytest

from app.middleware.api_rate_limiter import (
    ApiRateLimiter,
    RateLimitResult,
    TIER_RATE_LIMITS_PER_SECOND,
)


class TestTierRateLimits:
    """Tests for tier-based rate limit configuration."""
    
    def test_tier_limits_match_pricing_strategy(self):
        """Verify tier limits match docs/pricing/PRICING_STRATEGY.md."""
        assert TIER_RATE_LIMITS_PER_SECOND["starter"] == 10
        assert TIER_RATE_LIMITS_PER_SECOND["professional"] == 50
        assert TIER_RATE_LIMITS_PER_SECOND["business"] == 200
        assert TIER_RATE_LIMITS_PER_SECOND["enterprise"] == -1  # Unlimited
        assert TIER_RATE_LIMITS_PER_SECOND["strategic_partner"] == -1  # Unlimited
    
    def test_get_tier_limit_per_minute(self):
        """Test conversion from per-second to per-minute limits."""
        limiter = ApiRateLimiter()
        
        assert limiter.get_tier_limit_per_minute("starter") == 600  # 10 * 60
        assert limiter.get_tier_limit_per_minute("professional") == 3000  # 50 * 60
        assert limiter.get_tier_limit_per_minute("business") == 12000  # 200 * 60
        assert limiter.get_tier_limit_per_minute("enterprise") == -1  # Unlimited
        assert limiter.get_tier_limit_per_minute("strategic_partner") == -1  # Unlimited
    
    def test_get_tier_limit_case_insensitive(self):
        """Test tier names are case-insensitive."""
        limiter = ApiRateLimiter()
        
        assert limiter.get_tier_limit_per_minute("STARTER") == 600
        assert limiter.get_tier_limit_per_minute("Starter") == 600
        assert limiter.get_tier_limit_per_minute("starter") == 600
    
    def test_get_tier_limit_unknown_tier_defaults(self):
        """Unknown tier should default to starter limits."""
        limiter = ApiRateLimiter()
        
        # Unknown tier defaults to 10 req/s = 600/min
        assert limiter.get_tier_limit_per_minute("unknown_tier") == 600


class TestRateLimitCheck:
    """Tests for rate limit checking."""
    
    def test_check_allows_within_limit(self):
        """Requests within limit should be allowed."""
        limiter = ApiRateLimiter()
        
        allowed, retry_after, remaining, limit = limiter.check(
            organization_id="org_test",
            scope="sign",
            tier="starter",
        )
        
        assert allowed is True
        assert retry_after is None
        assert remaining == 599  # 600 - 1
        assert limit == 600
    
    def test_check_denies_over_limit(self):
        """Requests over limit should be denied."""
        limiter = ApiRateLimiter()
        
        # Exhaust the limit (use a small limit for testing)
        for _ in range(5):
            limiter.check(
                organization_id="org_test",
                scope="sign",
                per_minute=5,  # Override to small limit
            )
        
        # Next request should be denied
        allowed, retry_after, remaining, limit = limiter.check(
            organization_id="org_test",
            scope="sign",
            per_minute=5,
        )
        
        assert allowed is False
        assert retry_after is not None
        assert retry_after > 0
        assert remaining == 0
        assert limit == 5
    
    def test_check_unlimited_tier(self):
        """Enterprise tier should have unlimited requests."""
        limiter = ApiRateLimiter()
        
        # Make many requests
        for _ in range(1000):
            allowed, retry_after, remaining, limit = limiter.check(
                organization_id="org_enterprise",
                scope="sign",
                tier="enterprise",
            )
            assert allowed is True
            assert limit == -1
            assert remaining == -1
    
    def test_check_scopes_are_independent(self):
        """Different scopes should have independent limits."""
        limiter = ApiRateLimiter()
        
        # Exhaust "sign" scope
        for _ in range(5):
            limiter.check(
                organization_id="org_test",
                scope="sign",
                per_minute=5,
            )
        
        # "verify" scope should still be available
        allowed, _, _, _ = limiter.check(
            organization_id="org_test",
            scope="verify",
            per_minute=5,
        )
        
        assert allowed is True
    
    def test_check_organizations_are_independent(self):
        """Different organizations should have independent limits."""
        limiter = ApiRateLimiter()
        
        # Exhaust org_a's limit
        for _ in range(5):
            limiter.check(
                organization_id="org_a",
                scope="sign",
                per_minute=5,
            )
        
        # org_b should still be available
        allowed, _, _, _ = limiter.check(
            organization_id="org_b",
            scope="sign",
            per_minute=5,
        )
        
        assert allowed is True


class TestRateLimitResult:
    """Tests for RateLimitResult dataclass."""
    
    def test_check_with_reset_returns_result(self):
        """check_with_reset should return RateLimitResult."""
        limiter = ApiRateLimiter()
        
        result = limiter.check_with_reset(
            organization_id="org_test",
            scope="sign",
            tier="starter",
        )
        
        assert isinstance(result, RateLimitResult)
        assert result.allowed is True
        assert result.retry_after is None
        assert result.remaining == 599
        assert result.limit == 600
        assert result.reset_at > 0
    
    def test_reset_at_is_future_timestamp(self):
        """reset_at should be a future Unix timestamp."""
        limiter = ApiRateLimiter()
        
        result = limiter.check_with_reset(
            organization_id="org_test",
            scope="sign",
            tier="starter",
        )
        
        now = int(time.time())
        assert result.reset_at >= now
        assert result.reset_at <= now + 60  # Within 60 seconds


class TestRateLimitHeaders:
    """Tests for rate limit HTTP headers."""
    
    def test_get_headers_includes_all_headers(self):
        """get_headers should include all standard rate limit headers."""
        limiter = ApiRateLimiter()
        
        result = limiter.check_with_reset(
            organization_id="org_test",
            scope="sign",
            tier="starter",
        )
        
        headers = limiter.get_headers(result)
        
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers
        assert headers["X-RateLimit-Limit"] == "600"
        assert int(headers["X-RateLimit-Remaining"]) >= 0
        assert int(headers["X-RateLimit-Reset"]) > 0
    
    def test_get_headers_includes_retry_after_on_deny(self):
        """Retry-After header should be included when rate limited."""
        limiter = ApiRateLimiter()
        
        # Exhaust limit
        for _ in range(5):
            limiter.check_with_reset(
                organization_id="org_test",
                scope="sign",
                per_minute=5,
            )
        
        # Get denied result
        result = limiter.check_with_reset(
            organization_id="org_test",
            scope="sign",
            per_minute=5,
        )
        
        headers = limiter.get_headers(result)
        
        assert "Retry-After" in headers
        assert int(headers["Retry-After"]) > 0
    
    def test_get_headers_unlimited_tier_no_headers(self):
        """Unlimited tiers should not include rate limit headers."""
        limiter = ApiRateLimiter()
        
        result = limiter.check_with_reset(
            organization_id="org_enterprise",
            scope="sign",
            tier="enterprise",
        )
        
        headers = limiter.get_headers(result)
        
        # Unlimited tier should have empty headers
        assert "X-RateLimit-Limit" not in headers
        assert "X-RateLimit-Remaining" not in headers
