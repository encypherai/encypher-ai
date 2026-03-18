"""Tests for JobQueue (D6)."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import AsyncMock

import pytest

from app.services.job_queue import JobQueue


class FakeRedisStream:
    """Minimal Redis stand-in supporting xadd / xreadgroup / xack / xgroup_create."""

    def __init__(self) -> None:
        self._stream: List[Tuple[str, Dict[str, str]]] = []
        self._acked: set = set()
        self._counter = 0

    async def xgroup_create(self, stream: str, group: str, id: str = "0", mkstream: bool = True) -> None:
        pass

    async def xadd(self, stream: str, fields: Dict[str, str], maxlen: int = 0) -> str:
        self._counter += 1
        entry_id = f"1-{self._counter}"
        self._stream.append((entry_id, fields))
        return entry_id

    async def xreadgroup(
        self,
        group: str,
        consumer: str,
        streams: Dict[str, str],
        count: int = 10,
        block: int = 0,
    ) -> Optional[List[Tuple[str, List[Tuple[str, Dict[str, str]]]]]]:
        unacked = [(eid, f) for eid, f in self._stream if eid not in self._acked]
        if not unacked:
            return None
        return [("encypher:jobs", unacked[:count])]

    async def xack(self, stream: str, group: str, msg_id: str) -> None:
        self._acked.add(msg_id)


@pytest.mark.asyncio
async def test_enqueue_returns_entry_id() -> None:
    q = JobQueue()
    await q.connect(FakeRedisStream())
    entry_id = await q.enqueue("test_job", {"key": "val"})
    assert entry_id is not None
    assert entry_id.startswith("1-")


@pytest.mark.asyncio
async def test_enqueue_without_redis_fires_asyncio_task() -> None:
    q = JobQueue()
    results: list = []

    async def handler(payload: Dict[str, Any]) -> None:
        results.append(payload)

    q.register_handler("test_job", handler)
    entry_id = await q.enqueue("test_job", {"x": 1})
    assert entry_id is None

    # Let the fire-and-forget task run
    await asyncio.sleep(0.05)
    assert results == [{"x": 1}]


@pytest.mark.asyncio
async def test_process_pending_calls_handler() -> None:
    q = JobQueue()
    redis = FakeRedisStream()
    await q.connect(redis)

    processed_payloads: list = []

    async def handler(payload: Dict[str, Any]) -> None:
        processed_payloads.append(payload)

    q.register_handler("webhook", handler)
    await q.enqueue("webhook", {"url": "https://example.com"})
    count = await q.process_pending("worker-1")
    assert count == 1
    assert processed_payloads == [{"url": "https://example.com"}]


@pytest.mark.asyncio
async def test_process_pending_skips_unknown_type() -> None:
    q = JobQueue()
    redis = FakeRedisStream()
    await q.connect(redis)

    await q.enqueue("unknown_type", {"data": "x"})
    count = await q.process_pending("worker-1")
    # Unknown types are acked but not counted as processed
    assert count == 0


@pytest.mark.asyncio
async def test_process_pending_without_redis() -> None:
    q = JobQueue()
    count = await q.process_pending("worker-1")
    assert count == 0


@pytest.mark.asyncio
async def test_handler_error_does_not_ack() -> None:
    q = JobQueue()
    redis = FakeRedisStream()
    await q.connect(redis)

    async def failing_handler(payload: Dict[str, Any]) -> None:
        raise RuntimeError("boom")

    q.register_handler("fail_job", failing_handler)
    await q.enqueue("fail_job", {"x": 1})
    count = await q.process_pending("worker-1")
    # Failed handler means not acked, not counted
    assert count == 0
    assert len(redis._acked) == 0
