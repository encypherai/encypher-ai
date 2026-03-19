"""Tests for GDPR data management endpoints.

Tests the /api/v1/data/* endpoints for deletion requests, admin purge,
and compliance receipts.
"""

import pytest
from httpx import AsyncClient

from app.dependencies import get_current_organization
from app.main import app
from app.routers.data_management import (
    AUDIT_LOG_RETENTION_YEARS,
    PURGE_WINDOW_DAYS,
    VERIFICATION_RETENTION_YEARS,
    DeletionConfirmResponse,
    DeletionRequestResponse,
    _require_admin,
)


def _mock_org(org_id: str = "org_test", tier: str = "free"):
    """Return a mock organization context."""
    return {
        "organization_id": org_id,
        "organization_name": "Test Organization",
        "tier": tier,
        "user_id": "user_test_123",
        "actor_id": "user_test_123",
        "permissions": ["sign", "verify", "read"],
        "features": {},
    }


def _mock_admin_org(org_id: str = "org_test", tier: str = "free"):
    """Return a mock organization context with admin role (for admin-only endpoints)."""
    ctx = _mock_org(org_id, tier)
    ctx["current_user_role"] = "owner"
    return ctx


@pytest.mark.asyncio
class TestCreateDeletionRequest:
    """Tests for POST /api/v1/data/deletion-request."""

    async def test_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/data/deletion-request",
            json={"confirm": True, "scope": "account"},
        )
        assert response.status_code == 401

    async def test_requires_confirm_true(self, client: AsyncClient):
        app.dependency_overrides[get_current_organization] = lambda: _mock_org()
        response = await client.post(
            "/api/v1/data/deletion-request",
            json={"confirm": False, "scope": "account"},
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 400
        body = response.json()
        msg = body.get("detail", "") or body.get("error", {}).get("message", "")
        assert "confirm" in msg.lower()

    async def test_rejects_invalid_scope(self, client: AsyncClient):
        app.dependency_overrides[get_current_organization] = lambda: _mock_org()
        response = await client.post(
            "/api/v1/data/deletion-request",
            json={"confirm": True, "scope": "invalid_scope"},
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 400

    async def test_creates_deletion_request_account_scope(self, client: AsyncClient):
        app.dependency_overrides[get_current_organization] = lambda: _mock_org()
        response = await client.post(
            "/api/v1/data/deletion-request",
            json={
                "confirm": True,
                "scope": "account",
                "reason": "No longer using the service",
            },
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert data["scope"] == "account"
        assert data["reason"] == "No longer using the service"
        assert data["organization_id"] == "org_test"
        assert data["id"].startswith("del_")
        assert "scheduled_purge_at" in data

    async def test_creates_deletion_request_personal_data_scope(self, client: AsyncClient):
        app.dependency_overrides[get_current_organization] = lambda: _mock_org()
        response = await client.post(
            "/api/v1/data/deletion-request",
            json={"confirm": True, "scope": "personal_data"},
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["scope"] == "personal_data"


@pytest.mark.asyncio
class TestListDeletionRequests:
    """Tests for GET /api/v1/data/deletion-requests."""

    async def test_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/data/deletion-requests")
        assert response.status_code == 401

    async def test_returns_empty_list(self, client: AsyncClient):
        app.dependency_overrides[get_current_organization] = lambda: _mock_org("org_empty_list")
        response = await client.get(
            "/api/v1/data/deletion-requests",
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["requests"] == []

    async def test_lists_created_requests(self, client: AsyncClient):
        org_id = "org_list_test"
        app.dependency_overrides[get_current_organization] = lambda: _mock_org(org_id)

        # Create a request first
        await client.post(
            "/api/v1/data/deletion-request",
            json={"confirm": True, "scope": "account", "reason": "test"},
            headers={"Authorization": "Bearer test"},
        )

        response = await client.get(
            "/api/v1/data/deletion-requests",
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(r["scope"] == "account" for r in data["requests"])

    async def test_filters_by_status(self, client: AsyncClient):
        org_id = "org_filter_test"
        app.dependency_overrides[get_current_organization] = lambda: _mock_org(org_id)

        # Create a pending request
        await client.post(
            "/api/v1/data/deletion-request",
            json={"confirm": True, "scope": "account"},
            headers={"Authorization": "Bearer test"},
        )

        # Filter for completed (should be empty since we only have pending)
        response = await client.get(
            "/api/v1/data/deletion-requests?status=completed",
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 200
        assert response.json()["total"] == 0


@pytest.mark.asyncio
class TestConfirmDeletionRequest:
    """Tests for DELETE /api/v1/data/deletion-request/{id}/confirm."""

    async def test_requires_auth(self, client: AsyncClient):
        response = await client.delete("/api/v1/data/deletion-request/fake_id/confirm")
        assert response.status_code == 401

    async def test_404_for_nonexistent_request(self, client: AsyncClient):
        app.dependency_overrides[get_current_organization] = lambda: _mock_org()
        app.dependency_overrides[_require_admin] = lambda: _mock_admin_org()
        response = await client.delete(
            "/api/v1/data/deletion-request/nonexistent_id/confirm",
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 404

    async def test_confirms_pending_request(self, client: AsyncClient):
        org_id = "org_confirm_test"
        app.dependency_overrides[get_current_organization] = lambda: _mock_org(org_id)
        app.dependency_overrides[_require_admin] = lambda: _mock_admin_org(org_id)

        # Create
        create_resp = await client.post(
            "/api/v1/data/deletion-request",
            json={"confirm": True, "scope": "account"},
            headers={"Authorization": "Bearer test"},
        )
        request_id = create_resp.json()["id"]

        # Confirm
        response = await client.delete(
            f"/api/v1/data/deletion-request/{request_id}/confirm",
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"
        assert str(PURGE_WINDOW_DAYS) in data["message"]

    async def test_cannot_confirm_already_confirmed(self, client: AsyncClient):
        org_id = "org_double_confirm"
        app.dependency_overrides[get_current_organization] = lambda: _mock_org(org_id)
        app.dependency_overrides[_require_admin] = lambda: _mock_admin_org(org_id)

        create_resp = await client.post(
            "/api/v1/data/deletion-request",
            json={"confirm": True, "scope": "account"},
            headers={"Authorization": "Bearer test"},
        )
        request_id = create_resp.json()["id"]

        # Confirm first time
        await client.delete(
            f"/api/v1/data/deletion-request/{request_id}/confirm",
            headers={"Authorization": "Bearer test"},
        )

        # Try to confirm again
        response = await client.delete(
            f"/api/v1/data/deletion-request/{request_id}/confirm",
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 409


@pytest.mark.asyncio
class TestCancelDeletionRequest:
    """Tests for POST /api/v1/data/deletion-request/{id}/cancel."""

    async def test_cancels_pending_request(self, client: AsyncClient):
        org_id = "org_cancel_test"
        app.dependency_overrides[get_current_organization] = lambda: _mock_org(org_id)

        create_resp = await client.post(
            "/api/v1/data/deletion-request",
            json={"confirm": True, "scope": "account"},
            headers={"Authorization": "Bearer test"},
        )
        request_id = create_resp.json()["id"]

        response = await client.post(
            f"/api/v1/data/deletion-request/{request_id}/cancel",
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"


@pytest.mark.asyncio
class TestAdminPurgeUser:
    """Tests for POST /api/v1/data/admin/purge-user."""

    async def test_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/data/admin/purge-user",
            json={
                "user_email": "test@example.com",
                "reason": "GDPR request",
                "confirm": True,
            },
        )
        assert response.status_code == 401

    async def test_requires_confirm(self, client: AsyncClient):
        app.dependency_overrides[get_current_organization] = lambda: _mock_org()
        app.dependency_overrides[_require_admin] = lambda: _mock_admin_org()
        response = await client.post(
            "/api/v1/data/admin/purge-user",
            json={
                "user_email": "test@example.com",
                "reason": "GDPR request",
                "confirm": False,
            },
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 400

    async def test_admin_purge_creates_request(self, client: AsyncClient):
        app.dependency_overrides[get_current_organization] = lambda: _mock_org()
        app.dependency_overrides[_require_admin] = lambda: _mock_admin_org()
        response = await client.post(
            "/api/v1/data/admin/purge-user",
            json={
                "user_email": "departed@example.com",
                "reason": "Employee offboarding",
                "confirm": True,
            },
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_email"] == "departed@example.com"
        assert data["status"] == "confirmed"
        assert data["request_id"].startswith("purge_")
        assert "scheduled_purge_at" in data


@pytest.mark.asyncio
class TestDeletionReceipt:
    """Tests for GET /api/v1/data/deletion-request/{id}/receipt."""

    async def test_returns_receipt_for_account_deletion(self, client: AsyncClient):
        org_id = "org_receipt_test"
        app.dependency_overrides[get_current_organization] = lambda: _mock_org(org_id)

        create_resp = await client.post(
            "/api/v1/data/deletion-request",
            json={"confirm": True, "scope": "account"},
            headers={"Authorization": "Bearer test"},
        )
        request_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/data/deletion-request/{request_id}/receipt",
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"] == request_id
        assert data["scope"] == "account"
        assert "Account information" in data["data_categories_deleted"]
        assert "Verification records" in data["data_categories_retained"]
        assert "Verification records" in data["retention_reasons"]

    async def test_404_for_nonexistent_receipt(self, client: AsyncClient):
        app.dependency_overrides[get_current_organization] = lambda: _mock_org()
        response = await client.get(
            "/api/v1/data/deletion-request/nonexistent/receipt",
            headers={"Authorization": "Bearer test"},
        )
        assert response.status_code == 404


class TestRetentionConstants:
    """Verify retention constants match policy."""

    def test_purge_window(self):
        assert PURGE_WINDOW_DAYS == 90

    def test_verification_retention(self):
        assert VERIFICATION_RETENTION_YEARS == 7

    def test_audit_log_retention(self):
        assert AUDIT_LOG_RETENTION_YEARS == 2
