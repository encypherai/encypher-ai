"""Tests for WS2: content spread ungating and enforcement gating.

Uses httpx.ASGITransport to avoid app lifespan (no DB migration needed).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from httpx import ASGITransport

from app.database import get_db
from app.dependencies import get_current_organization_dep
from app.main import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TEST_ORG_ID = "org_ws2_test"
NOTICE_ID = "00000000-0000-0000-0000-000000000001"


def _make_org_dep(tier: str):
    """Return an org context override for the given tier."""

    def _dep():
        return {
            "organization_id": TEST_ORG_ID,
            "name": "WS2 Test Org",
            "tier": tier,
            "add_ons": {},
        }

    return _dep


async def _override_db():
    yield AsyncMock()


def _make_notice(org_id=TEST_ORG_ID, status="created"):
    notice = MagicMock()
    notice.id = NOTICE_ID
    notice.organization_id = org_id
    notice.status = status
    notice.delivered_at = None
    notice.delivery_method = None
    notice.delivery_receipt = None
    notice.delivery_receipt_hash = None
    return notice


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Content Spread -- ungated (all tiers allowed)
# ---------------------------------------------------------------------------


class TestContentSpreadUngated:
    """Content spread analytics should be accessible to all tiers."""

    @pytest.mark.anyio
    async def test_free_tier_can_access_content_spread(self):
        """Free tier should NOT get 403 on /analytics/content-spread."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_result.scalar_one.return_value = 0
        mock_db.execute = AsyncMock(return_value=mock_result)

        async def override_db():
            yield mock_db

        app.dependency_overrides[get_current_organization_dep] = _make_org_dep("free")
        app.dependency_overrides[get_db] = override_db

        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/analytics/content-spread?days=30")
            # Should NOT be 403 -- the gate was removed
            assert (
                response.status_code != 403
            ), f"Free tier got 403 on content-spread; gate should be removed. Got {response.status_code}: {response.text}"

    @pytest.mark.anyio
    async def test_enterprise_tier_can_access_content_spread(self):
        """Enterprise tier should still access content spread."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_result.scalar_one.return_value = 0
        mock_db.execute = AsyncMock(return_value=mock_result)

        async def override_db():
            yield mock_db

        app.dependency_overrides[get_current_organization_dep] = _make_org_dep("enterprise")
        app.dependency_overrides[get_db] = override_db

        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/analytics/content-spread?days=30")
            assert response.status_code != 403


# ---------------------------------------------------------------------------
# Notice creation -- enterprise-only
# ---------------------------------------------------------------------------


class TestNoticeCreationGate:
    """Notice creation should be gated to enterprise/strategic_partner/demo."""

    @pytest.mark.anyio
    async def test_free_tier_cannot_create_notice(self):
        """Free tier should get 403 on POST /notices/create."""
        app.dependency_overrides[get_current_organization_dep] = _make_org_dep("free")
        app.dependency_overrides[get_db] = _override_db

        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/notices/create",
                json={
                    "recipient_entity": "Test Corp",
                    "notice_text": "Test notice text",
                    "violation_type": "unauthorized_training",
                },
            )
            assert response.status_code == 403
            body = response.json()
            # detail may be nested under "detail" key or at top level
            detail = body.get("detail", body)
            if isinstance(detail, dict):
                assert detail.get("code") == "FEATURE_NOT_AVAILABLE" or "Enterprise" in str(detail)

    @pytest.mark.anyio
    async def test_enterprise_tier_can_create_notice(self):
        """Enterprise tier should pass the tier gate on notice creation."""
        app.dependency_overrides[get_current_organization_dep] = _make_org_dep("enterprise")
        app.dependency_overrides[get_db] = _override_db

        with patch("app.routers.notices._notice_service") as mock_svc_factory:
            mock_notice = _make_notice()
            mock_notice.created_at = None
            mock_notice.target_entity_name = "Test Corp"
            mock_notice.target_entity_domain = None
            mock_notice.target_contact_email = None
            mock_notice.target_entity_type = None
            mock_notice.scope_type = "all_content"
            mock_notice.scope_document_ids = []
            mock_notice.notice_type = "cease_and_desist"
            mock_notice.notice_hash = "abc123"
            mock_notice.demands = None
            mock_notice.delivery_method = None
            mock_notice.delivery_receipt_hash = None
            mock_notice.acknowledged_at = None
            mock_notice.notice_text = "Test notice"

            svc = MagicMock()
            svc.create_notice = AsyncMock(return_value=mock_notice)
            mock_svc_factory.return_value = svc

            transport = ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/notices/create",
                    json={
                        "recipient_entity": "Test Corp",
                        "notice_text": "Test notice text",
                        "violation_type": "unauthorized_training",
                    },
                )
                # Should NOT be 403
                assert response.status_code != 403, f"Enterprise tier got 403 on notice creation. Got {response.status_code}: {response.text}"


# ---------------------------------------------------------------------------
# Notice delivery -- enterprise-only
# ---------------------------------------------------------------------------


class TestNoticeDeliveryGate:
    """Notice delivery should be gated to enterprise/strategic_partner/demo."""

    @pytest.mark.anyio
    async def test_free_tier_cannot_deliver_notice(self):
        """Free tier should get 403 on POST /notices/{id}/deliver."""
        app.dependency_overrides[get_current_organization_dep] = _make_org_dep("free")
        app.dependency_overrides[get_db] = _override_db

        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/v1/notices/{NOTICE_ID}/deliver",
                json={"delivery_method": "api"},
            )
            assert response.status_code == 403


# ---------------------------------------------------------------------------
# Evidence package -- enterprise-only
# ---------------------------------------------------------------------------


class TestEvidencePackageGate:
    """Evidence package endpoints should be gated to enterprise tiers."""

    @pytest.mark.anyio
    async def test_free_tier_cannot_get_evidence(self):
        """Free tier should get 403 on GET /notices/{id}/evidence."""
        app.dependency_overrides[get_current_organization_dep] = _make_org_dep("free")
        app.dependency_overrides[get_db] = _override_db

        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/notices/{NOTICE_ID}/evidence")
            assert response.status_code == 403

    @pytest.mark.anyio
    async def test_free_tier_cannot_get_evidence_pdf(self):
        """Free tier should get 403 on GET /notices/{id}/evidence/pdf."""
        app.dependency_overrides[get_current_organization_dep] = _make_org_dep("free")
        app.dependency_overrides[get_db] = _override_db

        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/notices/{NOTICE_ID}/evidence/pdf")
            assert response.status_code == 403

    @pytest.mark.anyio
    async def test_demo_tier_passes_evidence_gate(self):
        """Demo tier should pass the tier gate (same access as enterprise)."""
        app.dependency_overrides[get_current_organization_dep] = _make_org_dep("demo")
        app.dependency_overrides[get_db] = _override_db

        with patch("app.routers.notices._notice_service") as mock_svc_factory:
            svc = MagicMock()
            svc.get_notice = AsyncMock(return_value=None)
            mock_svc_factory.return_value = svc

            transport = ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(f"/api/v1/notices/{NOTICE_ID}/evidence")
                # Should NOT be 403 -- demo passes the gate; will be 404 since notice not found
                assert response.status_code != 403


# ---------------------------------------------------------------------------
# Tier config sanity checks
# ---------------------------------------------------------------------------


class TestTierConfig:
    """Verify tier_config.py has the correct feature flags."""

    def test_free_features_content_spread_enabled(self):
        from app.core.tier_config import FREE_FEATURES

        assert FREE_FEATURES["content_spread_analytics"] is True

    def test_free_features_notices_disabled(self):
        from app.core.tier_config import FREE_FEATURES

        assert FREE_FEATURES["formal_notice_creation"] is False
        assert FREE_FEATURES["evidence_generation"] is False

    def test_enterprise_features_all_enabled(self):
        from app.core.tier_config import ENTERPRISE_FEATURES

        assert ENTERPRISE_FEATURES["content_spread_analytics"] is True
        assert ENTERPRISE_FEATURES["formal_notice_creation"] is True
        assert ENTERPRISE_FEATURES["evidence_generation"] is True

    def test_strategic_partner_inherits_enterprise(self):
        from app.core.tier_config import STRATEGIC_PARTNER_FEATURES

        assert STRATEGIC_PARTNER_FEATURES["formal_notice_creation"] is True
        assert STRATEGIC_PARTNER_FEATURES["evidence_generation"] is True
