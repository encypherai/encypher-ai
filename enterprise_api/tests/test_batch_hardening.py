"""Tests for batch service hardening (D7) -- Redis state persistence and recovery."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from app.services.batch_service import BatchService

from .conftest import FakeRedis


@pytest.mark.asyncio
async def test_persist_and_clear_batch_state() -> None:
    svc = BatchService()
    redis = FakeRedis()
    svc._redis = redis

    await svc._persist_batch_state("batch-1", {"batch_id": "batch-1", "status": "processing"})
    key = f"{svc.BATCH_STATE_PREFIX}batch-1"
    assert key in redis._store
    stored = json.loads(redis._store[key])
    assert stored["status"] == "processing"

    await svc._clear_batch_state("batch-1")
    assert key not in redis._store


@pytest.mark.asyncio
async def test_persist_without_redis_is_noop() -> None:
    svc = BatchService()
    # No redis attached -- should not raise
    await svc._persist_batch_state("batch-x", {"status": "processing"})
    await svc._clear_batch_state("batch-x")


@pytest.mark.asyncio
async def test_recover_incomplete_batches() -> None:
    svc = BatchService()
    redis = FakeRedis()

    # Pre-seed two incomplete batch states
    key1 = f"{svc.BATCH_STATE_PREFIX}batch-a"
    key2 = f"{svc.BATCH_STATE_PREFIX}batch-b"
    redis._store[key1] = json.dumps({"batch_id": "batch-a", "status": "processing"})
    redis._store[key2] = json.dumps({"batch_id": "batch-b", "status": "processing"})

    recovered = await svc.recover_incomplete_batches(redis)
    assert recovered == 2
    # Keys should be cleaned up after recovery
    assert key1 not in redis._store
    assert key2 not in redis._store


@pytest.mark.asyncio
async def test_recover_no_redis() -> None:
    svc = BatchService()
    recovered = await svc.recover_incomplete_batches(None)
    assert recovered == 0


@pytest.mark.asyncio
async def test_recover_empty_redis() -> None:
    svc = BatchService()
    redis = FakeRedis()
    recovered = await svc.recover_incomplete_batches(redis)
    assert recovered == 0


@pytest.mark.asyncio
async def test_redis_error_in_persist_is_swallowed() -> None:
    svc = BatchService()
    failing_redis = AsyncMock()
    failing_redis.setex = AsyncMock(side_effect=ConnectionError("gone"))
    failing_redis.delete = AsyncMock(side_effect=ConnectionError("gone"))
    svc._redis = failing_redis

    # Should not raise
    await svc._persist_batch_state("batch-err", {"status": "processing"})
    await svc._clear_batch_state("batch-err")
