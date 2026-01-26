"""
Integration tests for authentication flow.
"""

from datetime import datetime
import secrets

import httpx
import pytest


BASE_URL = "http://localhost:8001"


def _forwarded_for() -> str:
    return f"10.0.{secrets.randbelow(255)}.{secrets.randbelow(255)}"


async def _service_available(client: httpx.AsyncClient) -> bool:
    try:
        response = await client.get(f"{BASE_URL}/health", timeout=5.0)
        return response.status_code == 200
    except httpx.RequestError:
        return False


pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_complete_auth_flow():
    """Test complete authentication flow: signup -> login -> verify -> refresh -> logout."""
    async with httpx.AsyncClient() as client:
        if not await _service_available(client):
            pytest.skip("Auth service not running")
        base_headers = {"x-forwarded-for": _forwarded_for()}
        # 1. Register user
        email = f"test_{datetime.now().timestamp()}@example.com"
        register_response = await client.post(
            f"{BASE_URL}/api/v1/auth/signup",
            headers=base_headers,
            json={"email": email, "password": "SecurePass123!", "name": "Test User"},
        )
        assert register_response.status_code == 201
        response_json = register_response.json()
        # TEAM_006: API uses standardized response format { success, data, error }
        assert response_json["success"] is True
        user_data = response_json["data"]
        assert "id" in user_data
        assert user_data["email"] == email

        # 2. Login
        login_response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            headers=base_headers,
            json={"email": email, "password": "SecurePass123!"},
        )
        assert login_response.status_code == 200
        login_json = login_response.json()
        assert login_json["success"] is True
        tokens = login_json["data"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens

        # 3. Verify token
        verify_response = await client.post(
            f"{BASE_URL}/api/v1/auth/verify",
            headers={**base_headers, "Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert verify_response.status_code == 200

        # 4. Refresh token
        refresh_response = await client.post(
            f"{BASE_URL}/api/v1/auth/refresh",
            headers=base_headers,
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert refresh_response.status_code == 200
        refresh_json = refresh_response.json()
        assert refresh_json["success"] is True
        new_tokens = refresh_json["data"]
        assert "access_token" in new_tokens

        # 5. Logout
        logout_response = await client.post(
            f"{BASE_URL}/api/v1/auth/logout",
            headers={**base_headers, "Authorization": f"Bearer {new_tokens['access_token']}"},
        )
        assert logout_response.status_code == 200


@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Test that metrics endpoint returns Prometheus format."""
    async with httpx.AsyncClient() as client:
        if not await _service_available(client):
            pytest.skip("Auth service not running")
        response = await client.get(f"{BASE_URL}/metrics")
        assert response.status_code == 200

        metrics_text = response.text
        assert "auth_attempts_total" in metrics_text
        assert "http_requests_total" in metrics_text
        assert "http_request_duration_seconds" in metrics_text


@pytest.mark.asyncio
async def test_signup_rejects_url_like_name():
    async with httpx.AsyncClient() as client:
        if not await _service_available(client):
            pytest.skip("Auth service not running")
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/signup",
            headers={"x-forwarded-for": _forwarded_for()},
            json={
                "email": f"url_name_{datetime.now().timestamp()}@example.com",
                "password": "SecurePass123!",
                "name": "Visit https://evil.test now",
            },
        )

        assert response.status_code == 422
        detail = response.json().get("detail", [])
        assert detail
        assert "Name must not contain URLs" in detail[0].get("msg", "")


@pytest.mark.asyncio
async def test_signup_sanitizes_name_and_canonicalizes_email():
    async with httpx.AsyncClient() as client:
        if not await _service_available(client):
            pytest.skip("Auth service not running")
        timestamp = int(datetime.now().timestamp())
        raw_email = f"TestUser{timestamp}+tag@Example.com"
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/signup",
            headers={"x-forwarded-for": _forwarded_for()},
            json={"email": raw_email, "password": "SecurePass123!", "name": "<b>Jane Doe</b>"},
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["success"] is True
        data = payload["data"]
        assert data["email"] == f"testuser{timestamp}@example.com"
        assert data["name"] == "Jane Doe"


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with httpx.AsyncClient() as client:
        if not await _service_available(client):
            pytest.skip("Auth service not running")
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data


@pytest.mark.asyncio
async def test_request_id_header():
    """Test that X-Request-ID header is returned."""
    async with httpx.AsyncClient() as client:
        if not await _service_available(client):
            pytest.skip("Auth service not running")
        response = await client.get(f"{BASE_URL}/health")
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) == 36  # UUID length


@pytest.mark.asyncio
async def test_failed_login_attempt():
    """Test failed login attempt is tracked."""
    async with httpx.AsyncClient() as client:
        if not await _service_available(client):
            pytest.skip("Auth service not running")
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            headers={"x-forwarded-for": _forwarded_for()},
            json={"email": "nonexistent@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

        # Check that metrics recorded the failure
        metrics_response = await client.get(f"{BASE_URL}/metrics")
        assert "auth_attempts_total" in metrics_response.text
