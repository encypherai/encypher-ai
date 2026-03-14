"""Tests for navigation-rich error responses and custom validation handler.

Verifies Unix Agent Design criteria 1 (navigation errors) and 5 (progressive
help L1): every error response includes actionable next_action guidance, and
validation errors are grouped by field with docs links.
"""

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.bootstrap.errors import register_exception_handlers
from app.middleware.request_id_middleware import RequestIDMiddleware
from app.middleware.response_envelope import ResponseEnvelopeMiddleware


def _make_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)
    app.add_middleware(ResponseEnvelopeMiddleware)
    app.add_middleware(RequestIDMiddleware)

    @app.get("/raise-401")
    async def raise_401():
        raise HTTPException(
            status_code=401,
            detail={"code": "E_UNAUTHORIZED", "message": "Missing API key"},
        )

    @app.get("/raise-403-tier")
    async def raise_403_tier():
        raise HTTPException(
            status_code=403,
            detail={"code": "E_TIER_REQUIRED", "message": "Requires Enterprise"},
        )

    @app.get("/raise-429")
    async def raise_429():
        raise HTTPException(
            status_code=429,
            detail={"code": "E_RATE_LIMIT", "message": "Rate limit exceeded"},
        )

    @app.get("/raise-500-string")
    async def raise_500_string():
        raise HTTPException(status_code=500, detail="Something broke")

    @app.get("/raise-unhandled")
    async def raise_unhandled():
        raise RuntimeError("kaboom")

    @app.get("/raise-410")
    async def raise_410():
        raise HTTPException(
            status_code=410,
            detail={"code": "E_DEPRECATED", "message": "Use /api/v1/sign instead"},
        )

    @app.get("/raise-401-string")
    async def raise_401_string():
        # Simulates auth dependency that raises with plain string detail
        raise HTTPException(status_code=401, detail="API key required")

    @app.get("/raise-with-existing-nav")
    async def raise_with_existing_nav():
        raise HTTPException(
            status_code=401,
            detail={
                "code": "E_UNAUTHORIZED",
                "message": "Missing API key",
                "next_action": "Custom next action provided by handler",
            },
        )

    class TestBody(BaseModel):
        name: str = Field(..., min_length=1)
        count: int = Field(..., ge=1, le=100)

    @app.post("/validate")
    async def validate_body(body: TestBody):
        return {"success": True, "data": body.model_dump()}

    return app


class TestNavigationErrors:
    """Criterion 1: every error has a concrete next_action."""

    def setup_method(self):
        self.client = TestClient(_make_app(), raise_server_exceptions=False)

    def test_401_has_next_action(self):
        resp = self.client.get("/raise-401")
        assert resp.status_code == 401
        error = resp.json()["error"]
        assert error["next_action"] is not None
        assert "Authorization" in error["next_action"]
        assert "docs_url" in error

    def test_403_tier_has_next_action(self):
        resp = self.client.get("/raise-403-tier")
        assert resp.status_code == 403
        error = resp.json()["error"]
        assert "next_action" in error
        assert "pricing" in error["next_action"].lower()

    def test_429_has_next_action(self):
        resp = self.client.get("/raise-429")
        assert resp.status_code == 429
        error = resp.json()["error"]
        assert "next_action" in error
        assert "Retry-After" in error["next_action"]

    def test_string_detail_gets_fallback_code(self):
        resp = self.client.get("/raise-500-string")
        assert resp.status_code == 500
        body = resp.json()
        assert body["error"]["code"] == "E_HTTP"
        assert body["error"]["message"] == "Something broke"

    def test_unhandled_exception_has_next_action(self):
        resp = self.client.get("/raise-unhandled")
        assert resp.status_code == 500
        error = resp.json()["error"]
        assert error["code"] == "E_INTERNAL"
        assert "next_action" in error
        assert "correlation_id" in error["next_action"]

    def test_deprecated_has_next_action(self):
        resp = self.client.get("/raise-410")
        assert resp.status_code == 410
        error = resp.json()["error"]
        assert "next_action" in error
        assert "deprecated" in error["next_action"].lower()

    def test_401_string_detail_promoted_to_unauthorized(self):
        """Plain-string 401s get promoted to E_UNAUTHORIZED with navigation."""
        resp = self.client.get("/raise-401-string")
        assert resp.status_code == 401
        error = resp.json()["error"]
        assert error["code"] == "E_UNAUTHORIZED"
        assert "Authorization" in error["next_action"]

    def test_existing_next_action_not_overwritten(self):
        resp = self.client.get("/raise-with-existing-nav")
        error = resp.json()["error"]
        assert error["next_action"] == "Custom next action provided by handler"

    def test_all_errors_have_correlation_id(self):
        for path in ["/raise-401", "/raise-403-tier", "/raise-429", "/raise-unhandled"]:
            resp = self.client.get(path)
            body = resp.json()
            assert "correlation_id" in body, f"Missing correlation_id for {path}"


class TestValidationErrorHandler:
    """Criterion 5: validation errors are grouped, readable, with docs link."""

    def setup_method(self):
        self.client = TestClient(_make_app(), raise_server_exceptions=False)

    def test_missing_required_fields(self):
        resp = self.client.post("/validate", json={})
        assert resp.status_code == 422
        body = resp.json()
        assert body["success"] is False
        error = body["error"]
        assert error["code"] == "E_VALIDATION"
        assert "field_errors" in error["details"]
        assert "name" in error["details"]["field_errors"]
        assert "count" in error["details"]["field_errors"]

    def test_validation_error_has_next_action(self):
        resp = self.client.post("/validate", json={})
        error = resp.json()["error"]
        assert "next_action" in error
        assert "schema" in error["next_action"].lower()

    def test_validation_error_has_docs_url(self):
        resp = self.client.post("/validate", json={})
        error = resp.json()["error"]
        assert "docs_url" in error
        assert error["docs_url"] == "/docs"

    def test_invalid_type(self):
        resp = self.client.post("/validate", json={"name": "ok", "count": "not_a_number"})
        assert resp.status_code == 422
        error = resp.json()["error"]
        assert "count" in error["details"]["field_errors"]

    def test_constraint_violation(self):
        resp = self.client.post("/validate", json={"name": "ok", "count": 999})
        assert resp.status_code == 422
        error = resp.json()["error"]
        assert "count" in error["details"]["field_errors"]

    def test_validation_has_correlation_id(self):
        resp = self.client.post("/validate", json={})
        body = resp.json()
        assert "correlation_id" in body
