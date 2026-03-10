"""Tests for CDN analytics endpoints and image attribution helper.

Covers:
- GET /api/v1/cdn/analytics/summary returns 200 with zero counts when no records exist
- GET /api/v1/cdn/analytics/timeline?days=7 returns correct structure
- _maybe_record_image_attribution correctly identifies image URIs
- _maybe_record_image_attribution skips non-image URIs

Uses httpx TestClient with dependency overrides for router tests and direct
async invocation for service unit tests.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Path + env setup (must happen before any app imports)
# ---------------------------------------------------------------------------

_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

os.environ.setdefault("KEY_ENCRYPTION_KEY", "0" * 64)
os.environ.setdefault("ENCRYPTION_NONCE", "0" * 24)
os.environ.setdefault("IMAGE_SIGNING_PASSTHROUGH", "true")
os.environ.setdefault(
    "CORE_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:15432/encypher_content",  # pragma: allowlist secret
)
os.environ.setdefault(
    "CONTENT_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:15432/encypher_content",  # pragma: allowlist secret
)
os.environ.setdefault("DATABASE_URL", os.environ["CORE_DATABASE_URL"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TEST_ORG_ID = "test-org-analytics-001"


def _mock_org_dep():
    return {"organization_id": TEST_ORG_ID}


def _make_zero_count_db():
    """Return an AsyncSession mock whose execute() always yields count=0."""
    scalar_result = MagicMock()
    scalar_result.scalar_one.return_value = 0
    scalar_result.scalars.return_value.all.return_value = []

    db = AsyncMock()
    db.execute = AsyncMock(return_value=scalar_result)
    return db


# ---------------------------------------------------------------------------
# Router fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    from app.database import get_db
    from app.dependencies import get_current_organization_dep
    from app.main import app
    from fastapi.testclient import TestClient

    async def _override_db():
        yield _make_zero_count_db()

    app.dependency_overrides[get_current_organization_dep] = _mock_org_dep
    app.dependency_overrides[get_db] = _override_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Router: summary
# ---------------------------------------------------------------------------


class TestAnalyticsSummaryEndpoint:
    def test_summary_returns_200_zero_counts(self, client):
        """GET /cdn/analytics/summary returns 200 with all zeros for empty DB."""
        response = client.get("/api/v1/cdn/analytics/summary")
        assert response.status_code == 200
        body = response.json()
        assert body["organization_id"] == TEST_ORG_ID
        assert body["assets_protected"] == 0
        assert body["variants_registered"] == 0
        assert body["image_requests_tracked"] == 0
        assert body["recoverable_percent"] == 0.0

    def test_summary_response_has_required_fields(self, client):
        """GET /cdn/analytics/summary response includes all schema fields."""
        response = client.get("/api/v1/cdn/analytics/summary")
        assert response.status_code == 200
        body = response.json()
        required_fields = {
            "organization_id",
            "assets_protected",
            "variants_registered",
            "image_requests_tracked",
            "recoverable_percent",
        }
        assert required_fields.issubset(body.keys())

    def test_summary_requires_auth(self):
        """GET /cdn/analytics/summary returns 401/403 without auth."""
        from app.main import app
        from fastapi.testclient import TestClient

        # Use a client with no overrides so the real auth dependency runs
        with TestClient(app, raise_server_exceptions=False) as c:
            response = c.get("/api/v1/cdn/analytics/summary")
        assert response.status_code in (401, 403, 422)


# ---------------------------------------------------------------------------
# Router: timeline
# ---------------------------------------------------------------------------


class TestAnalyticsTimelineEndpoint:
    def test_timeline_returns_200_correct_structure(self, client):
        """GET /cdn/analytics/timeline?days=7 returns 200 with correct structure."""
        response = client.get("/api/v1/cdn/analytics/timeline?days=7")
        assert response.status_code == 200
        body = response.json()
        assert body["days"] == 7
        assert "data" in body
        assert isinstance(body["data"], list)
        assert len(body["data"]) == 7

    def test_timeline_default_days(self, client):
        """GET /cdn/analytics/timeline without days param defaults to 30."""
        response = client.get("/api/v1/cdn/analytics/timeline")
        assert response.status_code == 200
        body = response.json()
        assert body["days"] == 30
        assert len(body["data"]) == 30

    def test_timeline_day_entry_structure(self, client):
        """Each timeline day entry has date, images_signed, and image_requests."""
        response = client.get("/api/v1/cdn/analytics/timeline?days=3")
        assert response.status_code == 200
        body = response.json()
        for entry in body["data"]:
            assert "date" in entry
            assert "images_signed" in entry
            assert "image_requests" in entry
            # date must be YYYY-MM-DD
            assert len(entry["date"]) == 10
            assert entry["date"][4] == "-"
            assert entry["date"][7] == "-"
            # counts must be non-negative integers
            assert isinstance(entry["images_signed"], int)
            assert entry["images_signed"] >= 0
            assert isinstance(entry["image_requests"], int)
            assert entry["image_requests"] >= 0

    def test_timeline_zero_counts_for_empty_db(self, client):
        """When DB has no records, all timeline entries should have zero counts."""
        response = client.get("/api/v1/cdn/analytics/timeline?days=5")
        assert response.status_code == 200
        body = response.json()
        for entry in body["data"]:
            assert entry["images_signed"] == 0
            assert entry["image_requests"] == 0


# ---------------------------------------------------------------------------
# Service: _maybe_record_image_attribution
# ---------------------------------------------------------------------------


class TestMaybeRecordImageAttribution:
    """Unit tests for the image URI detection logic in logpush_service."""

    @pytest.mark.asyncio
    async def test_identifies_jpg_uri(self):
        """URIs ending in .jpg should trigger attribution recording."""
        from app.services.logpush_service import _maybe_record_image_attribution

        db = AsyncMock()
        db.add = MagicMock()

        await _maybe_record_image_attribution(
            db=db,
            organization_id=TEST_ORG_ID,
            host="example.com",
            uri="/photos/hero.jpg",
            status=200,
            client_ip="1.2.3.4",
        )

        db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_identifies_png_uri(self):
        """URIs ending in .png should trigger attribution recording."""
        from app.services.logpush_service import _maybe_record_image_attribution

        db = AsyncMock()
        db.add = MagicMock()

        await _maybe_record_image_attribution(
            db=db,
            organization_id=TEST_ORG_ID,
            host="example.com",
            uri="/static/logo.png",
            status=200,
            client_ip=None,
        )

        db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_identifies_webp_uri(self):
        """URIs ending in .webp should trigger attribution recording."""
        from app.services.logpush_service import _maybe_record_image_attribution

        db = AsyncMock()
        db.add = MagicMock()

        await _maybe_record_image_attribution(
            db=db,
            organization_id=TEST_ORG_ID,
            host="cdn.example.com",
            uri="/images/thumbnail.webp",
            status=200,
            client_ip="10.0.0.1",
        )

        db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_identifies_cdn_cgi_image_uri(self):
        """URIs containing /cdn-cgi/image/ should trigger attribution recording."""
        from app.services.logpush_service import _maybe_record_image_attribution

        db = AsyncMock()
        db.add = MagicMock()

        await _maybe_record_image_attribution(
            db=db,
            organization_id=TEST_ORG_ID,
            host="example.com",
            uri="/cdn-cgi/image/width=800,format=webp/images/hero.jpg",
            status=200,
            client_ip="5.5.5.5",
        )

        db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_identifies_images_path_hint(self):
        """URIs containing /images/ should trigger attribution recording."""
        from app.services.logpush_service import _maybe_record_image_attribution

        db = AsyncMock()
        db.add = MagicMock()

        await _maybe_record_image_attribution(
            db=db,
            organization_id=TEST_ORG_ID,
            host="example.com",
            uri="/images/background",
            status=200,
            client_ip=None,
        )

        db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_html_uri(self):
        """URIs ending in .html should NOT trigger attribution recording."""
        from app.services.logpush_service import _maybe_record_image_attribution

        db = AsyncMock()
        db.add = MagicMock()

        await _maybe_record_image_attribution(
            db=db,
            organization_id=TEST_ORG_ID,
            host="example.com",
            uri="/articles/my-post.html",
            status=200,
            client_ip="1.2.3.4",
        )

        db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_skips_api_uri(self):
        """API-style URIs should NOT trigger attribution recording."""
        from app.services.logpush_service import _maybe_record_image_attribution

        db = AsyncMock()
        db.add = MagicMock()

        await _maybe_record_image_attribution(
            db=db,
            organization_id=TEST_ORG_ID,
            host="example.com",
            uri="/api/v1/users",
            status=200,
            client_ip=None,
        )

        db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_skips_js_uri(self):
        """URIs ending in .js should NOT trigger attribution recording."""
        from app.services.logpush_service import _maybe_record_image_attribution

        db = AsyncMock()
        db.add = MagicMock()

        await _maybe_record_image_attribution(
            db=db,
            organization_id=TEST_ORG_ID,
            host="example.com",
            uri="/static/bundle.js",
            status=200,
            client_ip=None,
        )

        db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_cdn_cgi_prefix_stripped_in_canonical_url(self):
        """The /cdn-cgi/image/{opts}/ prefix should be stripped in canonical_url."""
        from app.models.cdn_attribution_event import CdnAttributionEvent
        from app.services.logpush_service import _maybe_record_image_attribution

        db = AsyncMock()
        captured = []

        def _capture_add(obj):
            captured.append(obj)

        db.add = _capture_add

        await _maybe_record_image_attribution(
            db=db,
            organization_id=TEST_ORG_ID,
            host="example.com",
            uri="/cdn-cgi/image/width=400,format=webp/images/hero.jpg",
            status=200,
            client_ip=None,
        )

        assert len(captured) == 1
        event = captured[0]
        assert isinstance(event, CdnAttributionEvent)
        assert "/cdn-cgi/image/" not in event.canonical_url
        assert "images/hero.jpg" in event.canonical_url
        assert "/cdn-cgi/image/" in event.image_url

    @pytest.mark.asyncio
    async def test_identifies_avif_uri(self):
        """URIs ending in .avif should trigger attribution recording."""
        from app.services.logpush_service import _maybe_record_image_attribution

        db = AsyncMock()
        db.add = MagicMock()

        await _maybe_record_image_attribution(
            db=db,
            organization_id=TEST_ORG_ID,
            host="cdn.example.com",
            uri="/media/photo.avif",
            status=200,
            client_ip=None,
        )

        db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_identifies_gif_uri(self):
        """URIs ending in .gif should trigger attribution recording."""
        from app.services.logpush_service import _maybe_record_image_attribution

        db = AsyncMock()
        db.add = MagicMock()

        await _maybe_record_image_attribution(
            db=db,
            organization_id=TEST_ORG_ID,
            host="example.com",
            uri="/animations/loading.gif",
            status=200,
            client_ip=None,
        )

        db.add.assert_called_once()
