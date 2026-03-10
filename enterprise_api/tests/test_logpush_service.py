"""
Tests for the Cloudflare Logpush ingestion service.

Covers: line parsing, bot classification, bypass detection logic,
and full batch ingestion.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.logpush_service import (
    _parse_timestamp,
    ingest_logpush_batch,
    parse_logpush_line,
)

# ---------------------------------------------------------------------------
# _parse_timestamp
# ---------------------------------------------------------------------------


def test_parse_timestamp_nanoseconds():
    # 2026-01-01 00:00:00 UTC in nanoseconds
    ns = 1_767_225_600 * 1_000_000_000
    result = _parse_timestamp(ns)
    assert result is not None
    assert result.tzinfo is not None
    assert result.year == 2026


def test_parse_timestamp_iso_string():
    result = _parse_timestamp("2026-01-15T12:00:00Z")
    assert result is not None
    assert result.year == 2026
    assert result.month == 1
    assert result.day == 15


def test_parse_timestamp_none():
    assert _parse_timestamp(None) is None


def test_parse_timestamp_invalid():
    assert _parse_timestamp("not-a-date") is None


# ---------------------------------------------------------------------------
# parse_logpush_line
# ---------------------------------------------------------------------------


def _make_line(**overrides) -> str:
    base = {
        "ClientIP": "1.2.3.4",
        "ClientRequestHost": "example.com",
        "ClientRequestURI": "/article/hello-world",
        "ClientRequestMethod": "GET",
        "ClientRequestUserAgent": "GPTBot/1.0",
        "EdgeStartTimestamp": "2026-01-15T12:00:00Z",
        "EdgeResponseStatus": 200,
        "ZoneName": "example.com",
    }
    base.update(overrides)
    return json.dumps(base)


def test_parse_logpush_line_valid():
    result = parse_logpush_line(_make_line())
    assert result is not None
    assert result["user_agent"] == "GPTBot/1.0"
    assert result["domain"] == "example.com"
    assert result["uri"] == "/article/hello-world"
    assert result["client_ip"] == "1.2.3.4"


def test_parse_logpush_line_empty():
    assert parse_logpush_line("") is None
    assert parse_logpush_line("   ") is None


def test_parse_logpush_line_malformed_json():
    assert parse_logpush_line("{not valid json}") is None


def test_parse_logpush_line_skips_post_method():
    result = parse_logpush_line(_make_line(ClientRequestMethod="POST"))
    assert result is None


def test_parse_logpush_line_skips_robots_txt():
    result = parse_logpush_line(_make_line(ClientRequestURI="/robots.txt"))
    assert result is None


def test_parse_logpush_line_skips_api_path():
    result = parse_logpush_line(_make_line(ClientRequestURI="/api/v1/something"))
    assert result is None


def test_parse_logpush_line_skips_static_assets():
    result = parse_logpush_line(_make_line(ClientRequestURI="/static/app.js"))
    assert result is None


def test_parse_logpush_line_skips_next_assets():
    result = parse_logpush_line(_make_line(ClientRequestURI="/_next/chunks/main.js"))
    assert result is None


def test_parse_logpush_line_head_method_allowed():
    result = parse_logpush_line(_make_line(ClientRequestMethod="HEAD"))
    assert result is not None


# ---------------------------------------------------------------------------
# ingest_logpush_batch (mocked DB)
# ---------------------------------------------------------------------------


def _make_db_mock(rsl_check_count: int = 0, rsl_respecting_types: list[str] | None = None):
    """Build a minimal AsyncSession mock for ingest tests."""
    if rsl_respecting_types is None:
        rsl_respecting_types = ["gptbot"]

    db = AsyncMock()

    # Mock for _get_rsl_respecting_categories (SELECT crawler_type WHERE respects_rsl=True)
    rsl_types_result = MagicMock()
    rsl_types_result.all.return_value = [(t,) for t in rsl_respecting_types]

    # Mock for _has_recent_rsl_check (SELECT count WHERE detection_source=rsl_olp_check)
    rsl_count_result = MagicMock()
    rsl_count_result.scalar_one.return_value = rsl_check_count

    db.execute = AsyncMock(side_effect=[rsl_types_result, rsl_count_result])
    db.add = MagicMock()
    db.flush = AsyncMock()

    return db


@pytest.mark.asyncio
async def test_ingest_empty_body():
    db = _make_db_mock()
    result = await ingest_logpush_batch(
        organization_id="org-1",
        body=b"",
        db=db,
    )
    assert result.lines_received == 0
    assert result.bots_detected == 0
    assert result.bypass_flags == 0
    assert result.events_created == 0
    assert result.errors == 0


@pytest.mark.asyncio
async def test_ingest_non_bot_lines():
    """Lines with human browser UA should not produce events."""
    line = _make_line(ClientRequestUserAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0")
    db = _make_db_mock(rsl_respecting_types=[])
    result = await ingest_logpush_batch(
        organization_id="org-1",
        body=line.encode(),
        db=db,
    )
    assert result.bots_detected == 0
    assert result.events_created == 0


@pytest.mark.asyncio
async def test_ingest_bot_line_no_bypass():
    """Known bot with a recent RSL check should NOT be flagged as bypass."""
    line = _make_line(ClientRequestUserAgent="GPTBot/1.0")
    db = _make_db_mock(rsl_check_count=5, rsl_respecting_types=["gptbot"])
    result = await ingest_logpush_batch(
        organization_id="org-1",
        body=line.encode(),
        db=db,
    )
    assert result.bots_detected == 1
    assert result.events_created == 1
    assert result.bypass_flags == 0


@pytest.mark.asyncio
async def test_ingest_bot_line_bypass_flagged():
    """Known bot claiming RSL compliance but no prior RSL check = bypass."""
    line = _make_line(ClientRequestUserAgent="GPTBot/1.0")
    db = _make_db_mock(rsl_check_count=0, rsl_respecting_types=["gptbot"])
    result = await ingest_logpush_batch(
        organization_id="org-1",
        body=line.encode(),
        db=db,
    )
    assert result.bots_detected == 1
    assert result.events_created == 1
    assert result.bypass_flags == 1


@pytest.mark.asyncio
async def test_ingest_unknown_bot_no_bypass():
    """Unknown bot category should not get bypass flag even with no RSL check."""
    line = _make_line(ClientRequestUserAgent="SomeObscureBot/2.0 (+http://obscure.example)")
    db = _make_db_mock(rsl_check_count=0, rsl_respecting_types=["gptbot"])
    result = await ingest_logpush_batch(
        organization_id="org-1",
        body=line.encode(),
        db=db,
    )
    # "SomeObscureBot" doesn't match any _BOT_PATTERNS -> classify_bot returns "unknown" -> skipped
    assert result.bots_detected == 0
    assert result.events_created == 0
    assert result.bypass_flags == 0


@pytest.mark.asyncio
async def test_ingest_multiple_lines():
    """Multiple lines with different bots should each produce events."""
    lines = "\n".join(
        [
            _make_line(ClientRequestUserAgent="GPTBot/1.0", ClientRequestURI="/article/a"),
            _make_line(ClientRequestUserAgent="ClaudeBot/1.0", ClientRequestURI="/article/b"),
            _make_line(ClientRequestUserAgent="Mozilla/5.0 Chrome/121", ClientRequestURI="/article/c"),
        ]
    )
    # Two separate RSL check lookups needed (one per bot category)
    from unittest.mock import AsyncMock, MagicMock

    db = AsyncMock()

    rsl_types_result = MagicMock()
    rsl_types_result.all.return_value = [("gptbot",), ("claudebot",)]

    rsl_count_result_1 = MagicMock()
    rsl_count_result_1.scalar_one.return_value = 1  # gptbot has RSL check

    rsl_count_result_2 = MagicMock()
    rsl_count_result_2.scalar_one.return_value = 0  # claudebot has no RSL check

    db.execute = AsyncMock(side_effect=[rsl_types_result, rsl_count_result_1, rsl_count_result_2])
    db.add = MagicMock()
    db.flush = AsyncMock()

    result = await ingest_logpush_batch(
        organization_id="org-1",
        body=lines.encode(),
        db=db,
    )
    assert result.bots_detected == 2
    assert result.events_created == 2
    assert result.bypass_flags == 1  # only claudebot bypassed
