"""Tests for auth-service admin dashboard data endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.v1.endpoints import router as auth_router
from app.db.session import get_db


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def client(mock_db):
    app = FastAPI()
    app.include_router(auth_router, prefix="/api/v1/auth")
    app.dependency_overrides[get_db] = lambda: mock_db
    return TestClient(app)


class TestAdminDashboardStats:
    def test_admin_stats_requires_super_admin(self, client):
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_1"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=False),
        ):
            response = client.get(
                "/api/v1/auth/admin/stats",
                headers={"Authorization": "Bearer test-token"},
            )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_stats_success(self, client):
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_admin"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=True),
            patch("app.api.v1.endpoints.AdminService.get_platform_stats", return_value={"total_users": 1}),
        ):
            response = client.get(
                "/api/v1/auth/admin/stats",
                headers={"Authorization": "Bearer test-token"},
            )
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert payload["data"]["total_users"] == 1


class TestAdminDashboardUsers:
    def test_admin_users_requires_super_admin(self, client):
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_1"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=False),
        ):
            response = client.get(
                "/api/v1/auth/admin/users",
                headers={"Authorization": "Bearer test-token"},
            )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_users_success(self, client):
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_admin"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=True),
            patch("app.api.v1.endpoints.AdminService.list_users", return_value={"users": [], "total": 0, "page": 1, "page_size": 50}),
        ):
            response = client.get(
                "/api/v1/auth/admin/users",
                headers={"Authorization": "Bearer test-token"},
            )
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert payload["data"]["total"] == 0


class TestAdminOrganizationSearch:
    def test_admin_org_search_requires_super_admin(self, client):
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_1"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=False),
        ):
            response = client.get(
                "/api/v1/auth/admin/organizations/search?query=encypher",
                headers={"Authorization": "Bearer test-token"},
            )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_org_search_success(self, client):
        orgs = [{"id": "org_1", "name": "Encypher", "email": "billing@encypher.ai", "tier": "business", "slug": "encypher"}]
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_admin"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=True),
            patch("app.api.v1.endpoints.AdminService.search_organizations", return_value=orgs),
        ):
            response = client.get(
                "/api/v1/auth/admin/organizations/search?query=encypher",
                headers={"Authorization": "Bearer test-token"},
            )
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert payload["data"][0]["id"] == "org_1"


class TestAdminNewsletterSubscribers:
    def test_admin_newsletter_subscribers_requires_super_admin(self, client):
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_1"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=False),
        ):
            response = client.get(
                "/api/v1/auth/admin/newsletter-subscribers",
                headers={"Authorization": "Bearer test-token"},
            )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_newsletter_subscribers_success(self, client):
        payload = {
            "subscribers": [
                {
                    "id": 1,
                    "email": "subscriber@example.com",
                    "active": True,
                    "source": "blog",
                    "subscribed_at": "2026-02-24T00:00:00",
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 50,
            "total_pages": 1,
        }
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_admin"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=True),
            patch("app.api.v1.endpoints.AdminService.get_newsletter_subscribers", new=AsyncMock(return_value=payload)),
        ):
            response = client.get(
                "/api/v1/auth/admin/newsletter-subscribers",
                headers={"Authorization": "Bearer test-token"},
            )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert body["data"]["total"] == 1
        assert body["data"]["subscribers"][0]["email"] == "subscriber@example.com"

    def test_update_newsletter_subscriber_status_success(self, client):
        payload = {
            "id": 1,
            "email": "subscriber@example.com",
            "active": False,
            "status": "invalid",
            "status_reason": "Mailbox rejected by provider",
        }
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_admin"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=True),
            patch("app.api.v1.endpoints.AdminService.update_newsletter_subscriber_status", new=AsyncMock(return_value=payload)),
        ):
            response = client.post(
                "/api/v1/auth/admin/newsletter-subscribers/1/status",
                headers={"Authorization": "Bearer test-token"},
                json={"status": "invalid", "reason": "Mailbox rejected by provider"},
            )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert body["data"]["status"] == "invalid"
        assert body["data"]["active"] is False

    def test_delete_newsletter_subscriber_success(self, client):
        payload = {"deleted": True, "id": 1}
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_admin"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=True),
            patch("app.api.v1.endpoints.AdminService.delete_newsletter_subscriber", new=AsyncMock(return_value=payload)),
        ):
            response = client.delete(
                "/api/v1/auth/admin/newsletter-subscribers/1",
                headers={"Authorization": "Bearer test-token"},
            )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert body["data"]["deleted"] is True


class TestAdminTierUpdates:
    def test_update_tier_requires_super_admin(self, client):
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_1"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=False),
        ):
            response = client.post(
                "/api/v1/auth/admin/users/update-tier",
                headers={"Authorization": "Bearer test-token"},
                json={"user_id": "user_123", "new_tier": "enterprise"},
            )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_tier_success(self, client):
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_admin"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=True),
            patch(
                "app.api.v1.endpoints.AdminService.update_user_tier",
                return_value={"success": True, "user_id": "user_123", "new_tier": "enterprise"},
            ),
        ):
            response = client.post(
                "/api/v1/auth/admin/users/update-tier",
                headers={"Authorization": "Bearer test-token"},
                json={"user_id": "user_123", "new_tier": "enterprise", "reason": "Upgrade"},
            )
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert payload["data"]["new_tier"] == "enterprise"

    def test_update_tier_rejects_invalid_tier(self, client):
        response = client.post(
            "/api/v1/auth/admin/users/update-tier",
            headers={"Authorization": "Bearer test-token"},
            json={"user_id": "user_123", "new_tier": "invalid"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAdminStatusUpdates:
    def test_update_status_requires_super_admin(self, client):
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_1"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=False),
        ):
            response = client.post(
                "/api/v1/auth/admin/users/update-status",
                headers={"Authorization": "Bearer test-token"},
                json={"user_id": "user_123", "status": "suspended"},
            )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_status_success(self, client):
        with (
            patch("app.api.v1.endpoints.AuthService.verify_access_token", return_value={"sub": "user_admin"}),
            patch("app.api.v1.endpoints.verify_super_admin", return_value=True),
            patch(
                "app.api.v1.endpoints.AdminService.update_user_status",
                return_value={"success": True, "user_id": "user_123", "new_status": "suspended"},
            ),
        ):
            response = client.post(
                "/api/v1/auth/admin/users/update-status",
                headers={"Authorization": "Bearer test-token"},
                json={"user_id": "user_123", "status": "suspended", "reason": "Abuse"},
            )
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert payload["data"]["new_status"] == "suspended"

    def test_update_status_rejects_invalid_status(self, client):
        response = client.post(
            "/api/v1/auth/admin/users/update-status",
            headers={"Authorization": "Bearer test-token"},
            json={"user_id": "user_123", "status": "invalid"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
