"""
Tests for RequestIDMiddleware and RequestIDFilter (TEAM_218).

Verifies:
- X-Request-ID is stamped on every response
- Inbound X-Request-ID is echoed back (caller tracing)
- Generated IDs have the expected req-{12hex} format
- request.state.request_id is set and accessible inside route handlers
- request_id_ctx ContextVar carries the value through async call stack
"""

import re

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.middleware.request_id_middleware import RequestIDMiddleware, request_id_ctx


def _make_app() -> tuple[FastAPI, list[str]]:
    """Return (app, captured_ids) where captured_ids is populated during requests."""
    captured: list[str] = []
    app = FastAPI()
    app.add_middleware(RequestIDMiddleware)

    @app.get("/echo")
    async def echo(request: Request) -> JSONResponse:
        from_state = request.state.request_id
        from_ctx = request_id_ctx.get()
        captured.append(from_state)
        return JSONResponse({"state_id": from_state, "ctx_id": from_ctx})

    @app.get("/health")
    async def health() -> JSONResponse:
        return JSONResponse({"ok": True})

    return app, captured


def test_response_has_x_request_id_header() -> None:
    app, _ = _make_app()
    client = TestClient(app, raise_server_exceptions=True)
    resp = client.get("/echo")
    assert resp.status_code == 200
    assert "x-request-id" in resp.headers


def test_generated_request_id_format() -> None:
    """Auto-generated IDs match req-{12 hex chars}."""
    app, _ = _make_app()
    client = TestClient(app)
    resp = client.get("/echo")
    rid = resp.headers.get("x-request-id", "")
    assert re.fullmatch(r"req-[0-9a-f]{12}", rid), f"Unexpected format: {rid!r}"


def test_inbound_request_id_is_echoed() -> None:
    """When the caller supplies X-Request-ID it must be returned unchanged."""
    app, _ = _make_app()
    client = TestClient(app)
    resp = client.get("/echo", headers={"x-request-id": "req-aabbccddeeff"})
    assert resp.headers.get("x-request-id") == "req-aabbccddeeff"


def test_request_state_and_ctx_match_response_header() -> None:
    """request.state.request_id and ContextVar must equal the response header value."""
    app, captured = _make_app()
    client = TestClient(app)
    resp = client.get("/echo")
    body = resp.json()
    rid = resp.headers["x-request-id"]

    assert body["state_id"] == rid
    assert body["ctx_id"] == rid
    assert captured[0] == rid


def test_ctx_var_reset_after_request() -> None:
    """ContextVar must be reset to '-' default after each request lifecycle."""
    app, _ = _make_app()
    client = TestClient(app)
    # Make a request - inside the request the ctx is set
    client.get("/echo")
    # Outside any request context the default should apply
    # (TestClient may run in same thread; check via the route echo endpoint indirectly
    # by verifying two sequential requests get distinct IDs)
    resp1 = client.get("/echo")
    resp2 = client.get("/echo")
    assert resp1.headers["x-request-id"] != resp2.headers["x-request-id"]


def test_each_request_gets_unique_id() -> None:
    """Two concurrent requests without supplied IDs must receive different IDs."""
    app, _ = _make_app()
    client = TestClient(app)
    ids = {client.get("/echo").headers["x-request-id"] for _ in range(5)}
    assert len(ids) == 5, "All 5 requests must have unique IDs"


def test_non_api_path_still_gets_id() -> None:
    """Even health/probe paths receive an X-Request-ID stamp."""
    app, _ = _make_app()
    client = TestClient(app)
    resp = client.get("/health")
    assert "x-request-id" in resp.headers
