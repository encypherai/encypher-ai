"""Tests for Prebid auto-provenance signing endpoints and service.

Covers:
- Service utilities (extract_domain, hash_content, org ID generation)
- POST /api/v1/public/prebid/sign (happy path, dedup, validation, rate limit)
- GET /api/v1/public/prebid/manifest/{id}
- GET /api/v1/public/prebid/status/{domain}
"""

import uuid
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.public_rate_limiter import public_rate_limiter


@pytest_asyncio.fixture(autouse=True)
async def _prebid_test_isolation(db: AsyncSession):
    """Clean Prebid data and mock C2PA signing for each test.

    The signing executor's content_session_factory() opens connections on
    the module-level engine, which conflicts with the test ASGI transport's
    event loop. We mock execute_unified_signing here; the real signing
    pipeline is tested in test_managed_signing_mode.py and signing tests.
    """
    await db.execute(sa_text("DELETE FROM prebid_content_records"))
    await db.execute(sa_text("DELETE FROM organizations WHERE id LIKE 'org_prebid_%%'"))
    await db.commit()

    async def _mock_sign(**kwargs):
        doc_id = f"doc_test_{uuid.uuid4().hex[:8]}"
        return {
            "success": True,
            "data": {
                "document": {
                    "document_id": doc_id,
                    "signed_text": "signed content with embedded C2PA manifest",
                    "verification_url": f"http://test/verify/{doc_id}",
                    "total_segments": 1,
                    "merkle_root": None,
                    "instance_id": None,
                    "metadata": None,
                    "publisher_attribution": None,
                    "embedding_plan": None,
                },
                "documents": None,
                "total_documents": 1,
                "total_segments": 1,
                "processing_time_ms": 10,
            },
            "error": None,
            "correlation_id": "test-correlation-id",
            "meta": {
                "tier": "free",
                "features_used": ["basic_signing"],
                "processing_time_ms": 10,
                "correlation_id": "test-correlation-id",
            },
        }

    with patch(
        "app.services.prebid_signing_service.execute_unified_signing",
        side_effect=_mock_sign,
    ):
        yield


# ============================================================================
# Unit tests: service utilities
# ============================================================================


class TestServiceUtilities:
    """Pure unit tests for prebid_signing_service helpers."""

    def test_extract_domain_strips_www(self):
        from app.services.prebid_signing_service import extract_domain

        assert extract_domain("https://www.nytimes.com/2026/article") == "nytimes.com"

    def test_extract_domain_preserves_subdomain(self):
        from app.services.prebid_signing_service import extract_domain

        assert extract_domain("https://blog.example.com/post") == "blog.example.com"

    def test_extract_domain_lowercase(self):
        from app.services.prebid_signing_service import extract_domain

        assert extract_domain("https://WWW.EXAMPLE.COM/page") == "example.com"

    def test_extract_domain_no_scheme(self):
        from app.services.prebid_signing_service import extract_domain

        # urlparse treats schemeless URLs oddly, but our function handles it
        result = extract_domain("example.com/page")
        # Without scheme, urlparse puts it all in path; hostname is None
        assert result == ""

    def test_hash_content_deterministic(self):
        from app.services.prebid_signing_service import hash_content

        h1 = hash_content("Hello world")
        h2 = hash_content("Hello world")
        assert h1 == h2
        assert h1.startswith("sha256:")
        assert len(h1) == 71  # "sha256:" (7) + 64 hex chars

    def test_hash_content_different_for_different_text(self):
        from app.services.prebid_signing_service import hash_content

        h1 = hash_content("Article one")
        h2 = hash_content("Article two")
        assert h1 != h2

    def test_generate_prebid_org_id(self):
        from app.services.prebid_signing_service import _generate_prebid_org_id

        org_id = _generate_prebid_org_id("example.com")
        assert org_id.startswith("org_prebid_")
        assert len(org_id) == len("org_prebid_") + 12

    def test_generate_prebid_org_id_deterministic(self):
        from app.services.prebid_signing_service import _generate_prebid_org_id

        id1 = _generate_prebid_org_id("nytimes.com")
        id2 = _generate_prebid_org_id("nytimes.com")
        assert id1 == id2

    def test_generate_prebid_org_id_different_domains(self):
        from app.services.prebid_signing_service import _generate_prebid_org_id

        id1 = _generate_prebid_org_id("nytimes.com")
        id2 = _generate_prebid_org_id("washingtonpost.com")
        assert id1 != id2


# ============================================================================
# Integration tests: sign endpoint
# ============================================================================


LONG_ARTICLE = "A" * 100  # meets 50-char minimum


class TestPrebidSignEndpoint:
    """Integration tests for POST /api/v1/public/prebid/sign."""

    async def test_sign_new_content(self, client: AsyncClient):
        """First request for a domain+content: provisions org, signs, returns manifest."""
        resp = await client.post(
            "/api/v1/public/prebid/sign",
            json={
                "text": LONG_ARTICLE,
                "page_url": "https://www.testpublisher.com/article/1",
                "document_title": "Test Article",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["cached"] is False
        assert data["signer_tier"] == "encypher_free"
        assert data["manifest_url"] is not None
        assert data["content_hash"].startswith("sha256:")
        assert data["org_id"].startswith("org_prebid_")
        assert data["signed_at"] is not None

    async def test_sign_dedup_returns_cached(self, client: AsyncClient):
        """Second request for same domain+content returns cached manifest."""
        payload = {
            "text": "Unique dedup test content that is long enough to pass validation " * 2,
            "page_url": "https://dedup-test.com/article/42",
        }
        resp1 = await client.post("/api/v1/public/prebid/sign", json=payload)
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["success"] is True
        assert data1["cached"] is False

        resp2 = await client.post("/api/v1/public/prebid/sign", json=payload)
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["success"] is True
        assert data2["cached"] is True
        assert data2["manifest_url"] == data1["manifest_url"]
        assert data2["content_hash"] == data1["content_hash"]

    async def test_sign_different_content_same_domain(self, client: AsyncClient):
        """Different content on the same domain gets separate manifests."""
        base = {
            "page_url": "https://multi-content.com/page",
        }
        resp1 = await client.post(
            "/api/v1/public/prebid/sign",
            json={**base, "text": "First article content that is long enough for extraction " * 2},
        )
        resp2 = await client.post(
            "/api/v1/public/prebid/sign",
            json={**base, "text": "Second article content that is completely different from the first " * 2},
        )
        assert resp1.json()["manifest_url"] != resp2.json()["manifest_url"]

    async def test_sign_rejects_short_text(self, client: AsyncClient):
        """Text shorter than 50 characters is rejected by Pydantic validation."""
        resp = await client.post(
            "/api/v1/public/prebid/sign",
            json={
                "text": "Too short",
                "page_url": "https://example.com/short",
            },
        )
        assert resp.status_code == 422

    async def test_sign_rejects_missing_page_url(self, client: AsyncClient):
        """Missing page_url is rejected."""
        resp = await client.post(
            "/api/v1/public/prebid/sign",
            json={"text": LONG_ARTICLE},
        )
        assert resp.status_code == 422

    async def test_sign_rate_limit(self, client: AsyncClient):
        """Rate limiting kicks in after exceeding requests_per_hour."""
        # Temporarily lower the limit for testing
        original_limit = public_rate_limiter.ENDPOINT_LIMITS["prebid_sign"]["requests_per_hour"]
        public_rate_limiter.ENDPOINT_LIMITS["prebid_sign"]["requests_per_hour"] = 2

        try:
            payload = {
                "text": "Rate limit test content that needs to be long enough for the minimum " * 2,
                "page_url": "https://rate-limit-test.com/page",
            }
            # First two should succeed
            r1 = await client.post("/api/v1/public/prebid/sign", json=payload)
            assert r1.status_code == 200
            r2 = await client.post(
                "/api/v1/public/prebid/sign",
                json={
                    "text": "Different content for rate limit test two that needs to be long enough " * 2,
                    "page_url": "https://rate-limit-test.com/page2",
                },
            )
            assert r2.status_code == 200

            # Third should be rate limited
            r3 = await client.post(
                "/api/v1/public/prebid/sign",
                json={
                    "text": "Third content for rate limit test three that needs to be long enough " * 2,
                    "page_url": "https://rate-limit-test.com/page3",
                },
            )
            assert r3.status_code == 429
        finally:
            public_rate_limiter.ENDPOINT_LIMITS["prebid_sign"]["requests_per_hour"] = original_limit

    async def test_sign_cors_headers(self, client: AsyncClient):
        """Sign endpoint should not block CORS (handled at app level)."""
        resp = await client.post(
            "/api/v1/public/prebid/sign",
            json={
                "text": LONG_ARTICLE,
                "page_url": "https://cors-test.com/page",
            },
        )
        assert resp.status_code == 200


# ============================================================================
# Integration tests: manifest endpoint
# ============================================================================


class TestPrebidManifestEndpoint:
    """Integration tests for GET /api/v1/public/prebid/manifest/{record_id}."""

    async def test_manifest_returns_signed_record(self, client: AsyncClient):
        """After signing, the manifest endpoint returns valid data."""
        sign_resp = await client.post(
            "/api/v1/public/prebid/sign",
            json={
                "text": "Manifest retrieval test content that is long enough to pass the minimum " * 2,
                "page_url": "https://manifest-test.com/article/99",
                "document_title": "Manifest Test Article",
            },
        )
        assert sign_resp.status_code == 200
        manifest_url = sign_resp.json()["manifest_url"]

        # Extract the path from the manifest_url
        # manifest_url format: http://test/api/v1/public/prebid/manifest/{uuid}
        path = manifest_url.replace("http://test", "")
        # If manifest_url starts with the real API base, extract path part
        if "/api/v1/public/prebid/manifest/" in manifest_url:
            path = "/api/v1/public/prebid/manifest/" + manifest_url.split("/api/v1/public/prebid/manifest/")[1]

        manifest_resp = await client.get(path)
        assert manifest_resp.status_code == 200

        data = manifest_resp.json()
        assert data["status"] == "ok"
        assert data["signerTier"] == "encypher_free"
        assert data["domain"] == "manifest-test.com"
        assert data["action"] == "c2pa.created"
        assert data["signedAt"] is not None

        # C2PA signing result fields
        assert data["document_id"] is not None
        assert data["document_id"].startswith("doc_test_")
        assert data["verification_url"] is not None

        # CORS header
        assert manifest_resp.headers.get("access-control-allow-origin") == "*"

    async def test_manifest_404_for_unknown_id(self, client: AsyncClient):
        """Unknown record ID returns 404."""
        resp = await client.get("/api/v1/public/prebid/manifest/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404


# ============================================================================
# Integration tests: status endpoint
# ============================================================================


class TestPrebidStatusEndpoint:
    """Integration tests for GET /api/v1/public/prebid/status/{domain}."""

    async def test_status_provisioned_domain(self, client: AsyncClient):
        """After signing, status returns provisioned=True with stats."""
        # First, sign something to provision the domain
        await client.post(
            "/api/v1/public/prebid/sign",
            json={
                "text": "Status test content for a provisioned domain that should be long enough " * 2,
                "page_url": "https://status-test.com/article/1",
            },
        )

        resp = await client.get("/api/v1/public/prebid/status/status-test.com")
        assert resp.status_code == 200
        data = resp.json()
        assert data["provisioned"] is True
        assert data["domain"] == "status-test.com"
        assert data["total_signed"] >= 1
        assert data["quota_remaining"] >= 0
        assert "upgrade_url" in data

    async def test_status_unprovisioned_domain(self, client: AsyncClient):
        """Unknown domain returns provisioned=False."""
        resp = await client.get("/api/v1/public/prebid/status/never-seen-before.com")
        assert resp.status_code == 200
        data = resp.json()
        assert data["provisioned"] is False
        assert data["total_signed"] == 0


# ============================================================================
# Service-level integration tests (direct function calls)
# ============================================================================


class TestPrebidSigningService:
    """Integration tests calling the service layer directly."""

    async def test_sign_or_retrieve_new_content(self, db: AsyncSession):
        """sign_or_retrieve provisions org and returns success for new content."""
        from app.services.prebid_signing_service import sign_or_retrieve

        result = await sign_or_retrieve(
            db=db,
            page_url="https://direct-service-test.com/article/1",
            text_content="Direct service test content that is long enough to pass the minimum threshold " * 2,
            document_title="Direct Test",
        )
        assert result["success"] is True
        assert result["cached"] is False
        assert result["org_id"].startswith("org_prebid_")
        assert result["manifest_url"] is not None
        assert result["content_hash"].startswith("sha256:")

    async def test_sign_or_retrieve_dedup(self, db: AsyncSession):
        """Same content+domain returns cached result on second call."""
        from app.services.prebid_signing_service import sign_or_retrieve

        args = {
            "db": db,
            "page_url": "https://dedup-service.com/page",
            "text_content": "Content for dedup service test that is long enough to pass minimum " * 2,
        }
        r1 = await sign_or_retrieve(**args)
        r2 = await sign_or_retrieve(**args)
        assert r1["cached"] is False
        assert r2["cached"] is True
        assert r1["manifest_url"] == r2["manifest_url"]

    async def test_sign_or_retrieve_invalid_url(self, db: AsyncSession):
        """Invalid URL (no hostname) returns error."""
        from app.services.prebid_signing_service import sign_or_retrieve

        result = await sign_or_retrieve(
            db=db,
            page_url="not-a-url",
            text_content=LONG_ARTICLE,
        )
        assert result["success"] is False
        assert result["error"] == "invalid_url"

    async def test_org_auto_provisioning_idempotent(self, db: AsyncSession):
        """Calling _ensure_prebid_org twice returns same org_id."""
        from app.services.prebid_signing_service import _ensure_prebid_org

        org_id_1, is_new_1 = await _ensure_prebid_org(db, "idempotent-test.com")
        org_id_2, is_new_2 = await _ensure_prebid_org(db, "idempotent-test.com")
        assert org_id_1 == org_id_2
        assert is_new_1 is True
        assert is_new_2 is False

    async def test_quota_check(self, db: AsyncSession):
        """Freshly provisioned org has quota available."""
        from app.services.prebid_signing_service import _check_prebid_quota, _ensure_prebid_org

        org_id, _ = await _ensure_prebid_org(db, "quota-check.com")
        allowed, usage = await _check_prebid_quota(db, org_id)
        assert allowed is True
        assert usage == 0
