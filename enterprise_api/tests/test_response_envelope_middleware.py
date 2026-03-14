"""Tests for ResponseEnvelopeMiddleware.

Verifies Unix Agent Design criterion 4 (metadata footer) and criterion 8
(two-layer separation): every ApiResponse-shaped JSON response gets a
consistent ``meta`` block with processing_time_ms, status, api_version,
and correlation_id.
"""

import json

from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.testclient import TestClient
from starlette.requests import Request

from app.middleware.request_id_middleware import RequestIDMiddleware
from app.middleware.response_envelope import ResponseEnvelopeMiddleware


def _make_app() -> FastAPI:
    """Build a minimal FastAPI app with RequestID + ResponseEnvelope middleware."""
    app = FastAPI()
    # ResponseEnvelope is inner to RequestID (added first = innermost)
    app.add_middleware(ResponseEnvelopeMiddleware)
    app.add_middleware(RequestIDMiddleware)

    @app.get("/success")
    async def success_route():
        return JSONResponse({"success": True, "data": {"msg": "hello"}, "error": None})

    @app.get("/error")
    async def error_route():
        return JSONResponse(
            {"success": False, "data": None, "error": {"code": "E_TEST", "message": "oops"}},
            status_code=400,
        )

    @app.get("/with-meta")
    async def with_meta_route():
        return JSONResponse(
            {
                "success": True,
                "data": {},
                "error": None,
                "meta": {"tier": "enterprise", "features_used": ["basic_signing"]},
            }
        )

    @app.get("/non-api")
    async def non_api_route():
        return JSONResponse({"items": [1, 2, 3]})

    @app.get("/plain")
    async def plain_route():
        return PlainTextResponse("OK")

    @app.get("/health")
    async def health_route():
        return JSONResponse({"status": "healthy"})

    @app.get("/with-correlation")
    async def with_correlation(request: Request):
        rid = getattr(request.state, "request_id", "missing")
        return JSONResponse({"success": True, "data": {"rid": rid}, "error": None, "correlation_id": rid})

    return app


class TestResponseEnvelopeMiddleware:
    """Verify that meta footer is injected on all ApiResponse-shaped responses."""

    def setup_method(self):
        self.client = TestClient(_make_app())

    # -- Criterion 4: metadata footer on success --

    def test_success_response_gets_meta(self):
        resp = self.client.get("/success")
        body = resp.json()
        assert "meta" in body
        meta = body["meta"]
        assert "processing_time_ms" in meta
        assert isinstance(meta["processing_time_ms"], int)
        assert meta["processing_time_ms"] >= 0
        assert meta["status"] == "ok"
        assert meta["api_version"] == "v1"

    def test_success_response_has_correlation_id(self):
        resp = self.client.get("/success")
        body = resp.json()
        assert "correlation_id" in body
        assert body["correlation_id"].startswith("req-")
        assert body["meta"]["correlation_id"] == body["correlation_id"]

    # -- Criterion 4: metadata footer on error --

    def test_error_response_gets_meta(self):
        resp = self.client.get("/error")
        assert resp.status_code == 400
        body = resp.json()
        meta = body["meta"]
        assert meta["status"] == "error"
        assert "processing_time_ms" in meta
        assert meta["api_version"] == "v1"

    def test_error_response_preserves_error_payload(self):
        resp = self.client.get("/error")
        body = resp.json()
        assert body["error"]["code"] == "E_TEST"
        assert body["error"]["message"] == "oops"

    # -- Existing meta fields are preserved --

    def test_existing_meta_fields_preserved(self):
        resp = self.client.get("/with-meta")
        body = resp.json()
        meta = body["meta"]
        # Original fields preserved
        assert meta["tier"] == "enterprise"
        assert meta["features_used"] == ["basic_signing"]
        # Footer fields injected
        assert "processing_time_ms" in meta
        assert meta["status"] == "ok"
        assert meta["api_version"] == "v1"

    # -- Non-ApiResponse JSON passes through untouched --

    def test_non_api_response_untouched(self):
        resp = self.client.get("/non-api")
        body = resp.json()
        assert body == {"items": [1, 2, 3]}
        assert "meta" not in body

    # -- Non-JSON responses pass through --

    def test_plain_text_response_untouched(self):
        resp = self.client.get("/plain")
        assert resp.text == "OK"

    # -- Excluded paths pass through --

    def test_health_endpoint_untouched(self):
        resp = self.client.get("/health")
        body = resp.json()
        assert body == {"status": "healthy"}
        assert "meta" not in body

    # -- Correlation ID from RequestIDMiddleware --

    def test_correlation_id_from_request_id_middleware(self):
        resp = self.client.get("/with-correlation")
        body = resp.json()
        # The correlation_id should match the request_id set by middleware
        assert body["correlation_id"].startswith("req-")
        assert body["meta"]["correlation_id"] == body["correlation_id"]

    def test_caller_supplied_request_id_preserved(self):
        resp = self.client.get("/with-correlation", headers={"x-request-id": "caller-trace-123"})
        body = resp.json()
        assert body["correlation_id"] == "caller-trace-123"
        assert body["meta"]["correlation_id"] == "caller-trace-123"

    # -- Status code preserved --

    def test_status_code_preserved(self):
        resp = self.client.get("/error")
        assert resp.status_code == 400

    def test_success_status_code_preserved(self):
        resp = self.client.get("/success")
        assert resp.status_code == 200
