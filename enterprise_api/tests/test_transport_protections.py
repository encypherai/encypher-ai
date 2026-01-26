import pytest
from httpx import AsyncClient

from app.config import settings
from app.main import build_cors_settings
from app.middleware.security_headers import build_security_headers


@pytest.mark.asyncio
async def test_security_headers_attached(async_client: AsyncClient) -> None:
    response = await async_client.get("/")
    assert response.status_code == 200
    headers = response.headers

    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert headers["Permissions-Policy"].startswith("geolocation=")
    assert "default-src" in headers["Content-Security-Policy"]
    if "Strict-Transport-Security" in headers:
        assert headers["Strict-Transport-Security"]


def test_security_headers_include_hsts_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "environment", "production")

    headers = build_security_headers()

    assert "Strict-Transport-Security" in headers


@pytest.mark.asyncio
async def test_trusted_host_blocks_unlisted(async_client: AsyncClient) -> None:
    response = await async_client.get("/", headers={"host": "evil.example"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_public_docs_disabled_by_default(async_client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "enable_public_api_docs", False)

    response = await async_client.get("/docs")
    assert response.status_code == 404

    response = await async_client.get("/docs/openapi.json")
    assert response.status_code == 404


def test_cors_production_settings_do_not_include_localhost(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "allowed_origins", "https://example.com")

    cors_settings = build_cors_settings()

    assert cors_settings["allow_origins"] == ["https://example.com"]
    assert "http://localhost:3000" not in cors_settings["allow_origins"]


def test_cors_wildcard_disables_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "allowed_origins", "*")

    cors_settings = build_cors_settings()

    assert cors_settings["allow_origins"] == ["*"]
    assert cors_settings["allow_credentials"] is False
