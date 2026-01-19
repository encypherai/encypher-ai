import structlog
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.middleware.logging import RequestLoggingMiddleware


def _build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/api/v1/auth/saml/login")
    async def saml_login():
        return {"ok": True}

    @app.get("/scim/v2/Users")
    async def scim_users():
        return {"ok": True}

    return app


def _request_started_kwargs(logger: MagicMock):
    for call in logger.info.call_args_list:
        if call.args and call.args[0] == "request_started":
            return call.kwargs
    return None


def test_request_logging_redacts_saml_query_params(monkeypatch):
    logger = MagicMock()
    monkeypatch.setattr(structlog, "get_logger", lambda: logger)

    client = TestClient(_build_app())
    client.get("/api/v1/auth/saml/login?org_id=org_test&return_to=https://example.com/callback")

    kwargs = _request_started_kwargs(logger)
    assert kwargs is not None
    assert kwargs["query_params"]["org_id"] == "[REDACTED]"
    assert kwargs["query_params"]["return_to"] == "[REDACTED]"


def test_request_logging_redacts_scim_query_params(monkeypatch):
    logger = MagicMock()
    monkeypatch.setattr(structlog, "get_logger", lambda: logger)

    client = TestClient(_build_app())
    client.get("/scim/v2/Users?filter=userName%20eq%20%22user%40example.com%22")

    kwargs = _request_started_kwargs(logger)
    assert kwargs is not None
    assert kwargs["query_params"]["filter"] == "[REDACTED]"
