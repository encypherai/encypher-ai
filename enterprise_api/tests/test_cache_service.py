"""Tests for OrgCacheService (D5)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.services.cache_service import OrgCacheService

from .conftest import FakeRedis


@pytest.mark.asyncio
async def test_no_redis_returns_none() -> None:
    svc = OrgCacheService()
    assert await svc.get_org_tier("org_1") is None
    assert await svc.get_org_data("org_1") is None
    # Should not raise
    await svc.set_org_tier("org_1", "enterprise")
    await svc.set_org_data("org_1", {"name": "Acme"})
    await svc.invalidate_org("org_1")


@pytest.mark.asyncio
async def test_tier_round_trip() -> None:
    svc = OrgCacheService()
    await svc.connect(FakeRedis())

    assert await svc.get_org_tier("org_1") is None
    await svc.set_org_tier("org_1", "enterprise")
    assert await svc.get_org_tier("org_1") == "enterprise"


@pytest.mark.asyncio
async def test_org_data_round_trip() -> None:
    svc = OrgCacheService()
    await svc.connect(FakeRedis())

    data = {"name": "Acme", "tier": "business"}
    await svc.set_org_data("org_2", data)
    cached = await svc.get_org_data("org_2")
    assert cached == data


@pytest.mark.asyncio
async def test_invalidate_removes_both_keys() -> None:
    svc = OrgCacheService()
    await svc.connect(FakeRedis())

    await svc.set_org_tier("org_3", "free")
    await svc.set_org_data("org_3", {"name": "Test"})
    await svc.invalidate_org("org_3")
    assert await svc.get_org_tier("org_3") is None
    assert await svc.get_org_data("org_3") is None


@pytest.mark.asyncio
async def test_redis_error_is_swallowed() -> None:
    svc = OrgCacheService()
    failing_redis = AsyncMock()
    failing_redis.get = AsyncMock(side_effect=ConnectionError("gone"))
    failing_redis.setex = AsyncMock(side_effect=ConnectionError("gone"))
    failing_redis.delete = AsyncMock(side_effect=ConnectionError("gone"))
    await svc.connect(failing_redis)

    # All operations should return gracefully instead of raising
    assert await svc.get_org_tier("org_x") is None
    assert await svc.get_org_data("org_x") is None
    await svc.set_org_tier("org_x", "free")
    await svc.set_org_data("org_x", {})
    await svc.invalidate_org("org_x")
