"""
Tests for Admin API endpoints.

Tests cover:
- Platform stats (super admin only)
- User listing with filtering
- Tier upgrades/downgrades
- Error logs viewing
- BYOK public key registration
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.admin import UserTier, UserStatus


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def super_admin_org():
    """Super admin organization context."""
    return {
        "organization_id": "org_super_admin",
        "organization_name": "Super Admin Org",
        "tier": "enterprise",
        "features": {"is_super_admin": True},
        "permissions": ["sign", "verify", "lookup", "admin"],
        "can_sign": True,
        "can_verify": True,
        "can_lookup": True,
    }


@pytest.fixture
def enterprise_org():
    """Enterprise organization context (not super admin)."""
    return {
        "organization_id": "org_enterprise_test",
        "organization_name": "Enterprise Test Org",
        "tier": "enterprise",
        "features": {
            "byok": True,
            "is_super_admin": False,
        },
        "byok_enabled": True,
        "permissions": ["sign", "verify", "lookup"],
        "can_sign": True,
        "can_verify": True,
        "can_lookup": True,
    }


@pytest.fixture
def starter_org():
    """Starter tier organization context."""
    return {
        "organization_id": "org_starter_test",
        "organization_name": "Starter Test Org",
        "tier": "starter",
        "features": {"byok": False},
        "byok_enabled": False,
        "permissions": ["sign", "verify"],
        "can_sign": True,
        "can_verify": True,
        "can_lookup": False,
    }


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock()


# =============================================================================
# Platform Stats Tests
# =============================================================================

@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


class TestPlatformStats:
    """Tests for GET /api/v1/admin/stats endpoint."""

    def test_get_stats_requires_super_admin(self, client, starter_org):
        """Non-super-admin should be forbidden."""
        with patch("app.dependencies.get_current_organization", return_value=starter_org):
            response = client.get(
                "/api/v1/admin/stats",
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_stats_success(self, client, super_admin_org, mock_db):
        """Super admin should get platform stats."""
        mock_stats = {
            "total_users": 100,
            "active_users": 85,
            "paying_customers": 20,
            "mrr": 5000,
            "total_api_calls": 150000,
            "users_by_tier": {"starter": 60, "professional": 25, "business": 10, "enterprise": 5},
        }
        
        with patch("app.dependencies.get_current_organization", return_value=super_admin_org), \
             patch("app.routers.admin.AdminService.get_platform_stats", return_value=mock_stats):
            response = client.get(
                "/api/v1/admin/stats",
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["data"]["total_users"] == 100


# =============================================================================
# User List Tests
# =============================================================================

class TestUserList:
    """Tests for GET /api/v1/admin/users endpoint."""

    def test_list_users_requires_super_admin(self, client, enterprise_org):
        """Non-super-admin should be forbidden."""
        with patch("app.dependencies.get_current_organization", return_value=enterprise_org):
            response = client.get(
                "/api/v1/admin/users",
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_users_with_search(self, client, super_admin_org, mock_db):
        """Should filter users by search term."""
        mock_result = {
            "users": [{"id": "user_1", "email": "test@example.com", "name": "Test User", "tier": "starter"}],
            "total": 1,
            "page": 1,
            "page_size": 50,
        }
        
        with patch("app.dependencies.get_current_organization", return_value=super_admin_org), \
             patch("app.routers.admin.AdminService.list_users", return_value=mock_result):
            response = client.get(
                "/api/v1/admin/users?search=test",
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["users"]) == 1


# =============================================================================
# Tier Update Tests
# =============================================================================

class TestTierUpdate:
    """Tests for POST /api/v1/admin/users/update-tier endpoint."""

    def test_update_tier_requires_super_admin(self, client, enterprise_org):
        """Non-super-admin should be forbidden."""
        with patch("app.dependencies.get_current_organization", return_value=enterprise_org):
            response = client.post(
                "/api/v1/admin/users/update-tier",
                headers={"Authorization": "Bearer test-token"},
                json={"user_id": "user_123", "new_tier": "enterprise"}
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_tier_success(self, client, super_admin_org, mock_db):
        """Super admin should be able to update user tier."""
        mock_result = {
            "success": True,
            "user_id": "user_123",
            "previous_tier": "starter",
            "new_tier": "enterprise",
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        with patch("app.dependencies.get_current_organization", return_value=super_admin_org), \
             patch("app.routers.admin.AdminService.update_user_tier", return_value=mock_result):
            response = client.post(
                "/api/v1/admin/users/update-tier",
                headers={"Authorization": "Bearer test-token"},
                json={"user_id": "user_123", "new_tier": "enterprise", "reason": "Sales upgrade"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["data"]["new_tier"] == "enterprise"

    def test_update_tier_invalid_tier(self, client, super_admin_org):
        """Should reject invalid tier values."""
        with patch("app.dependencies.get_current_organization", return_value=super_admin_org):
            response = client.post(
                "/api/v1/admin/users/update-tier",
                headers={"Authorization": "Bearer test-token"},
                json={"user_id": "user_123", "new_tier": "invalid_tier"}
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# =============================================================================
# Error Logs Tests
# =============================================================================

class TestErrorLogs:
    """Tests for GET /api/v1/admin/error-logs endpoint."""

    def test_get_error_logs_requires_super_admin(self, client, enterprise_org):
        """Non-super-admin should be forbidden."""
        with patch("app.dependencies.get_current_organization", return_value=enterprise_org):
            response = client.get(
                "/api/v1/admin/error-logs",
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_error_logs_success(self, client, super_admin_org, mock_db):
        """Super admin should get error logs."""
        mock_result = {
            "logs": [
                {
                    "id": "err_123",
                    "endpoint": "/api/v1/sign",
                    "method": "POST",
                    "status_code": 500,
                    "error_message": "Internal error",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 50,
        }
        
        with patch("app.dependencies.get_current_organization", return_value=super_admin_org), \
             patch("app.routers.admin.AdminService.get_error_logs", return_value=mock_result):
            response = client.get(
                "/api/v1/admin/error-logs",
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["logs"]) == 1


# =============================================================================
# BYOK Public Key Tests
# =============================================================================

class TestPublicKeyRegistration:
    """Tests for BYOK public key management endpoints."""

    SAMPLE_ED25519_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAGb9F2CMCwPz5K8VdBkPbVkPJPvPZMhLGpIRvXe5Rnvs=
-----END PUBLIC KEY-----"""

    def test_register_key_requires_byok_feature(self, client, starter_org):
        """Non-super-admin should be forbidden."""
        with patch("app.dependencies.get_current_organization", return_value=starter_org):
            response = client.post(
                "/api/v1/admin/public-keys",
                headers={"Authorization": "Bearer test-token"},
                json={
                    "public_key_pem": self.SAMPLE_ED25519_PUBLIC_KEY,
                    "key_name": "Test Key",
                }
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_register_key_requires_super_admin(self, client, enterprise_org):
        """Enterprise tier without super-admin should be forbidden."""
        with patch("app.dependencies.get_current_organization", return_value=enterprise_org):
            response = client.post(
                "/api/v1/admin/public-keys",
                headers={"Authorization": "Bearer test-token"},
                json={
                    "public_key_pem": self.SAMPLE_ED25519_PUBLIC_KEY,
                    "key_name": "Test Key",
                },
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_register_key_success(self, client, super_admin_org, mock_db):
        """Super admin should be able to register public keys."""
        mock_result = {
            "success": True,
            "data": {
                "id": "pk_123",
                "organization_id": "org_enterprise_test",
                "key_name": "Test Key",
                "key_algorithm": "Ed25519",
                "key_fingerprint": "SHA256:abc123...",
                "public_key_pem": self.SAMPLE_ED25519_PUBLIC_KEY,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
            }
        }
        
        with patch("app.dependencies.get_current_organization", return_value=super_admin_org), \
             patch("app.routers.admin.PublicKeyService.register_public_key", return_value=mock_result):
            response = client.post(
                "/api/v1/admin/public-keys",
                headers={"Authorization": "Bearer test-token"},
                json={
                    "public_key_pem": self.SAMPLE_ED25519_PUBLIC_KEY,
                    "key_name": "Test Key",
                    "key_algorithm": "Ed25519",
                }
            )
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["success"] is True
            assert data["data"]["key_name"] == "Test Key"

    def test_register_key_invalid_pem(self, client, super_admin_org):
        """Should reject invalid PEM format."""
        with patch("app.dependencies.get_current_organization", return_value=super_admin_org):
            response = client.post(
                "/api/v1/admin/public-keys",
                headers={"Authorization": "Bearer test-token"},
                json={
                    "public_key_pem": "not a valid pem",
                    "key_name": "Test Key",
                }
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_public_keys_requires_super_admin(self, client, enterprise_org):
        """Enterprise tier without super-admin should be forbidden."""
        with patch("app.dependencies.get_current_organization", return_value=enterprise_org):
            response = client.get(
                "/api/v1/admin/public-keys",
                headers={"Authorization": "Bearer test-token"},
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_public_keys(self, client, super_admin_org, mock_db):
        """Super admin should be able to list organization's public keys."""
        mock_result = {
            "success": True,
            "data": {
                "keys": [
                    {
                        "id": "pk_123",
                        "key_name": "Test Key",
                        "key_fingerprint": "SHA256:abc123...",
                        "is_active": True,
                    }
                ],
                "total": 1,
            }
        }
        
        with patch("app.dependencies.get_current_organization", return_value=super_admin_org), \
             patch("app.routers.admin.PublicKeyService.list_public_keys", return_value=mock_result):
            response = client.get(
                "/api/v1/admin/public-keys",
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["keys"]) == 1

    def test_revoke_public_key(self, client, super_admin_org, mock_db):
        """Super admin should be able to revoke a public key."""
        mock_result = {
            "success": True,
            "data": {
                "key_id": "pk_123",
                "revoked_at": datetime.utcnow().isoformat(),
            }
        }
        
        with patch("app.dependencies.get_current_organization", return_value=super_admin_org), \
             patch("app.routers.admin.PublicKeyService.revoke_public_key", return_value=mock_result):
            response = client.delete(
                "/api/v1/admin/public-keys/pk_123?reason=Key%20compromised",
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True


# =============================================================================
# Admin Service Unit Tests
# =============================================================================

class TestAdminService:
    """Unit tests for AdminService."""

    def test_compute_key_fingerprint(self):
        """Should compute consistent fingerprint for public key."""
        from app.services.admin_service import PublicKeyService
        
        pem = """-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAGb9F2CMCwPz5K8VdBkPbVkPJPvPZMhLGpIRvXe5Rnvs=
-----END PUBLIC KEY-----"""
        
        fingerprint1 = PublicKeyService.compute_key_fingerprint(pem)
        fingerprint2 = PublicKeyService.compute_key_fingerprint(pem)
        
        assert fingerprint1 == fingerprint2
        assert fingerprint1.startswith("SHA256:")
        assert len(fingerprint1) > 10
