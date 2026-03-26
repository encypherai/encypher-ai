from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.config import settings
from app.middleware.request_id_middleware import request_id_ctx
from app.services.auth_service_client import AuthServiceClient


def test_build_internal_headers_includes_scoped_metadata(monkeypatch):
    monkeypatch.setattr(settings, "internal_service_token", "internal-token")
    token = request_id_ctx.set("req-test123456")
    try:
        headers = AuthServiceClient._build_internal_headers(audience="auth_service.organization_context")
    finally:
        request_id_ctx.reset(token)

    assert headers["X-Internal-Token"] == "internal-token"
    assert headers["X-Internal-Service"] == "enterprise_api"
    assert headers["X-Internal-Audience"] == "auth_service.organization_context"
    assert headers["x-request-id"] == "req-test123456"
    assert headers["X-Internal-Timestamp"]


def test_build_internal_headers_omits_token_when_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "internal_service_token", None)
    token = request_id_ctx.set("req-test654321")
    try:
        headers = AuthServiceClient._build_internal_headers(audience="auth_service.bulk_provision")
    finally:
        request_id_ctx.reset(token)

    assert "X-Internal-Token" not in headers
    assert headers["X-Internal-Service"] == "enterprise_api"
    assert headers["X-Internal-Audience"] == "auth_service.bulk_provision"
    assert headers["x-request-id"] == "req-test654321"


@pytest.mark.asyncio
async def test_set_default_organization_skips_when_no_token(monkeypatch, caplog):
    """set_default_organization logs a warning and returns when no internal token is configured."""
    monkeypatch.setattr(settings, "internal_service_token", "")
    client = AuthServiceClient()
    await client.set_default_organization(user_id="usr_1", organization_id="org_1")
    assert "internal_service_token_missing" in caplog.text


@pytest.mark.asyncio
async def test_set_default_organization_calls_auth_service(monkeypatch):
    """set_default_organization POSTs to the correct auth-service internal endpoint."""
    monkeypatch.setattr(settings, "internal_service_token", "test-token")
    monkeypatch.setattr(settings, "auth_service_url", "http://auth-test:8080")
    ctx_token = request_id_ctx.set("req-setdeforg")

    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    try:
        with patch("app.services.auth_service_client.httpx.AsyncClient", return_value=mock_client):
            client = AuthServiceClient()
            await client.set_default_organization(user_id="usr_abc", organization_id="org_xyz")
    finally:
        request_id_ctx.reset(ctx_token)

    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert call_args[0][0] == "http://auth-test:8080/api/v1/auth/internal/users/set-default-org"
    assert call_args[1]["json"] == {"user_id": "usr_abc", "organization_id": "org_xyz"}
    assert call_args[1]["headers"]["X-Internal-Token"] == "test-token"
