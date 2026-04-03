import pytest
from httpx import AsyncClient

from app.config import settings
from app.main import build_cors_settings, build_trusted_hosts
from app.middleware.security_headers import DEFAULT_CSP, DOCS_CSP, build_security_headers


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

    response = await async_client.get("/docs/assets/design-system.css")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_metrics_endpoint_disabled_by_default(async_client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "enable_public_metrics_endpoint", False)

    response = await async_client.get("/metrics")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_health_endpoint_hides_operational_details_by_default(async_client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "expose_health_details", False)

    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_health_endpoint_can_expose_details_when_enabled(async_client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "expose_health_details", True)

    response = await async_client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert "environment" in payload
    assert "version" in payload


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


def test_trusted_hosts_include_host_docker_internal_outside_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "environment", "development")
    hosts = build_trusted_hosts()
    assert "host.docker.internal" in hosts


@pytest.mark.asyncio
async def test_docs_route_gets_relaxed_csp(async_client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Docs page needs a relaxed CSP so Swagger UI CDN resources can load."""
    monkeypatch.setattr(settings, "enable_public_api_docs", True)

    response = await async_client.get("/docs")
    assert response.status_code == 200
    csp = response.headers["Content-Security-Policy"]

    assert "unpkg.com" in csp
    assert "'unsafe-inline'" in csp
    assert "encypher.com" in csp
    assert "default-src 'none'" not in csp


@pytest.mark.asyncio
async def test_non_docs_route_keeps_strict_csp(async_client: AsyncClient) -> None:
    """Non-docs routes must retain the strict default CSP."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    csp = response.headers["Content-Security-Policy"]

    assert csp == DEFAULT_CSP


def test_docs_csp_allows_swagger_ui_resources() -> None:
    """DOCS_CSP must whitelist all resources needed by the Swagger UI docs page."""
    assert "script-src" in DOCS_CSP
    assert "https://unpkg.com" in DOCS_CSP
    assert "'unsafe-inline'" in DOCS_CSP
    assert "img-src" in DOCS_CSP
    assert "https://encypher.com" in DOCS_CSP
