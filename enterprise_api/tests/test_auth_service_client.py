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
