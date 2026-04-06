"""
Tests for the Evidence PDF endpoint.

Covers: auth required, 404, 403, and successful PDF generation.
Uses httpx TestClient with dependency overrides (same pattern as
test_cdn_integrations_router.py).
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.dependencies import get_current_organization_dep
from app.main import app

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TEST_ORG_ID = "test-org-pdf-001"
OTHER_ORG_ID = "other-org-pdf-002"
NOTICE_ID = str(uuid4())

_NOW = datetime.now(timezone.utc)


def _make_notice(org_id: str = TEST_ORG_ID) -> MagicMock:
    n = MagicMock()
    n.id = NOTICE_ID
    n.organization_id = org_id
    n.status = "delivered"
    n.target_entity_name = "Acme AI Corp"
    n.target_entity_domain = "acme.ai"
    n.target_contact_email = "legal@acme.ai"
    n.target_entity_type = "ai_company"
    n.notice_type = "cease_and_desist"
    n.scope_type = "all_content"
    n.scope_document_ids = []
    n.notice_text = "You are hereby notified that your use of our content is unauthorized."
    n.notice_hash = "abc123deadbeef" * 4
    n.delivery_method = "email"
    n.delivery_receipt = {"sent_at": _NOW.isoformat()}
    n.delivery_receipt_hash = "receipt_hash_xyz"
    n.demands = []
    n.response = None
    n.created_at = _NOW
    n.delivered_at = _NOW
    n.acknowledged_at = None
    n.evidence_chain = []
    return n


def _make_evidence_package() -> dict:
    return {
        "notice_id": NOTICE_ID,
        "generated_at": _NOW.isoformat(),
        "organization_id": TEST_ORG_ID,
        "notice": {
            "status": "delivered",
            "target_entity_name": "Acme AI Corp",
            "target_entity_domain": "acme.ai",
            "target_contact_email": "legal@acme.ai",
            "target_entity_type": "ai_company",
            "notice_type": "cease_and_desist",
            "scope_type": "all_content",
            "scope_document_ids": [],
            "notice_text": "You are hereby notified that your use of our content is unauthorized.",
            "created_at": _NOW.isoformat(),
            "delivered_at": _NOW.isoformat(),
            "delivery_method": "email",
        },
        "notice_hash": "abc123deadbeef" * 4,
        "notice_hash_verified": True,
        "evidence_chain": [
            {
                "event_type": "notice_created",
                "created_at": _NOW.isoformat(),
                "event_hash": "evthash001" * 6,
                "previous_hash": "0" * 64,
            },
            {
                "event_type": "notice_delivered",
                "created_at": _NOW.isoformat(),
                "event_hash": "evthash002" * 6,
                "previous_hash": "evthash001" * 6,
            },
        ],
        "chain_integrity_verified": True,
        "package_hash": "pkghash" * 9,
    }


def mock_org_dep():
    return {"organization_id": TEST_ORG_ID, "name": "Test Publisher", "tier": "enterprise"}


@pytest.fixture
def client():
    """Client with auth dep overridden to return TEST_ORG_ID."""
    app.dependency_overrides[get_current_organization_dep] = mock_org_dep
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def raw_client():
    """Client WITHOUT auth override — used to test 401/403."""
    app.dependency_overrides.clear()
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_evidence_pdf_requires_auth(raw_client):
    """No auth token -> 401 or 403 (depends on auth middleware)."""
    response = raw_client.get(f"/api/v1/notices/{NOTICE_ID}/evidence/pdf")
    assert response.status_code in (401, 403), f"Expected 401 or 403 without auth, got {response.status_code}"


def test_evidence_pdf_not_found(client):
    """Unknown notice_id -> 404."""
    unknown_id = str(uuid4())

    async def fake_get_notice(db, notice_id):
        return None

    with patch("app.routers.notices._notice_service") as mock_svc_factory:
        svc = MagicMock()
        svc.get_notice = AsyncMock(return_value=None)
        mock_svc_factory.return_value = svc

        async def override_db():
            yield AsyncMock()

        app.dependency_overrides[get_db] = override_db
        try:
            response = client.get(f"/api/v1/notices/{unknown_id}/evidence/pdf")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.pop(get_db, None)


def test_evidence_pdf_wrong_org(client):
    """Notice belongs to another org -> 403."""
    notice = _make_notice(org_id=OTHER_ORG_ID)

    with patch("app.routers.notices._notice_service") as mock_svc_factory:
        svc = MagicMock()
        svc.get_notice = AsyncMock(return_value=notice)
        mock_svc_factory.return_value = svc

        async def override_db():
            yield AsyncMock()

        app.dependency_overrides[get_db] = override_db
        try:
            response = client.get(f"/api/v1/notices/{NOTICE_ID}/evidence/pdf")
            assert response.status_code == 403
        finally:
            app.dependency_overrides.pop(get_db, None)


def test_evidence_pdf_returns_pdf(client):
    """Valid notice for the authed org -> 200, application/pdf, non-empty body."""
    notice = _make_notice()
    package = _make_evidence_package()

    with patch("app.routers.notices._notice_service") as mock_svc_factory:
        svc = MagicMock()
        svc.get_notice = AsyncMock(return_value=notice)
        svc.generate_evidence_package = AsyncMock(return_value=package)
        mock_svc_factory.return_value = svc

        async def override_db():
            yield AsyncMock()

        app.dependency_overrides[get_db] = override_db
        try:
            response = client.get(f"/api/v1/notices/{NOTICE_ID}/evidence/pdf")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            assert "application/pdf" in response.headers.get("content-type", "")
            assert len(response.content) > 0, "PDF body should not be empty"
            # PDF magic bytes
            assert response.content[:4] == b"%PDF", "Response should start with PDF magic bytes"
        finally:
            app.dependency_overrides.pop(get_db, None)
