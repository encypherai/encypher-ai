"""
Tests for detection analytics endpoints and detection service module.

Covers:
- Analytics detections endpoint auth and data
- Analytics crawlers endpoint auth and data
- Known crawlers seeded data
- ZW resolve endpoint smoke test
- Detection service module import
"""

import pytest
from httpx import AsyncClient

# ─────────────────────────────────────────────────────────────────────────────
# Analytics Detections
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_analytics_detections_requires_auth(client: AsyncClient):
    """GET /api/v1/rights/analytics/detections without auth returns 401/403."""
    response = await client.get("/api/v1/rights/analytics/detections")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_analytics_detections_returns_list(client: AsyncClient, auth_headers: dict):
    """GET /api/v1/rights/analytics/detections with auth returns 200 with detection data."""
    response = await client.get("/api/v1/rights/analytics/detections", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "organization_id" in data
    assert "total_events" in data
    assert "by_source" in data
    assert "by_category" in data


# ─────────────────────────────────────────────────────────────────────────────
# Analytics Crawlers
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_analytics_crawlers_requires_auth(client: AsyncClient):
    """GET /api/v1/rights/analytics/crawlers without auth returns 401/403."""
    response = await client.get("/api/v1/rights/analytics/crawlers")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_analytics_crawlers_returns_data(client: AsyncClient, auth_headers: dict):
    """GET /api/v1/rights/analytics/crawlers with auth returns 200."""
    response = await client.get("/api/v1/rights/analytics/crawlers", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "organization_id" in data
    assert "known_crawlers" in data
    assert "crawlers" in data


# ─────────────────────────────────────────────────────────────────────────────
# Known Crawlers Seeded
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_known_crawlers_seeded(client: AsyncClient, auth_headers: dict):
    """Verify known_crawlers has GPTBot, ClaudeBot etc. via the crawlers endpoint."""
    response = await client.get("/api/v1/rights/analytics/crawlers", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    known = data.get("known_crawlers", [])
    crawler_names = [c["crawler_name"] for c in known]
    assert "GPTBot" in crawler_names, f"GPTBot not found in known_crawlers: {crawler_names}"
    assert "ClaudeBot" in crawler_names, f"ClaudeBot not found in known_crawlers: {crawler_names}"


# ─────────────────────────────────────────────────────────────────────────────
# ZW Resolve Endpoint
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_zw_resolve_endpoint_works(client: AsyncClient):
    """GET /api/v1/public/c2pa/zw/resolve/{uuid} with fake UUID returns 404 (not 500)."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/public/c2pa/zw/resolve/{fake_uuid}")
    assert response.status_code == 404
    data = response.json()
    # Middleware flattens detail dict to top-level keys
    assert "SEGMENT_NOT_FOUND" in str(data)


# ─────────────────────────────────────────────────────────────────────────────
# Detection Service Module
# ─────────────────────────────────────────────────────────────────────────────


def test_detection_service_module_exists():
    """Verify that detection_service can be imported."""
    from app.services.detection_service import detection_service

    assert detection_service is not None
    assert callable(detection_service)
