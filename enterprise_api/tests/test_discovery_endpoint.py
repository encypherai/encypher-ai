"""Tests for the API discovery endpoint.

Verifies Unix Agent Design criterion 6 (progressive help L0): the API
provides a public, unauthenticated endpoint that enumerates all available
operations with summaries, while filtering out internal/admin routes.
"""

import app.routers.discovery as discovery_mod
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.discovery import router as discovery_router


def _make_app() -> FastAPI:
    """Build a minimal app with discovery + sample public/internal routes."""
    app = FastAPI()
    app.include_router(discovery_router)

    @app.get("/api/v1/sign", summary="Sign content", tags=["Signing"])
    async def sign():
        return {}

    @app.post("/api/v1/verify", summary="Verify content", tags=["Verification"])
    async def verify():
        return {}

    # Internal routes that should be filtered out
    @app.get("/api/v1/admin/stats", summary="Platform stats", tags=["Admin"])
    async def admin_stats():
        return {}

    @app.post("/api/v1/provisioning/auto", summary="Auto provision", tags=["Provisioning"])
    async def provision():
        return {}

    @app.get("/api/v1/audit-logs", summary="Audit logs", tags=["Audit"])
    async def audit():
        return {}

    @app.get("/api/v1/licensing/plans", summary="Plans", tags=["Licensing"])
    async def licensing():
        return {}

    # Hidden route (include_in_schema=False)
    @app.get("/api/v1/internal/debug", summary="Debug", include_in_schema=False)
    async def debug():
        return {}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


class TestDiscoveryEndpoint:
    def setup_method(self):
        # Clear the cache so each test gets a fresh build
        discovery_mod._cached_payload = None
        self.client = TestClient(_make_app())

    def teardown_method(self):
        discovery_mod._cached_payload = None

    def test_returns_200(self):
        resp = self.client.get("/api/v1/")
        assert resp.status_code == 200

    def test_returns_api_response_envelope(self):
        body = self.client.get("/api/v1/").json()
        assert body["success"] is True
        assert "data" in body
        assert body["error"] is None

    def test_lists_registered_endpoints(self):
        body = self.client.get("/api/v1/").json()
        endpoints = body["data"]["endpoints"]
        paths = [(e["method"], e["path"]) for e in endpoints]
        assert ("GET", "/api/v1/sign") in paths
        assert ("POST", "/api/v1/verify") in paths

    def test_includes_summaries(self):
        body = self.client.get("/api/v1/").json()
        endpoints = body["data"]["endpoints"]
        sign_ep = next(e for e in endpoints if e["path"] == "/api/v1/sign")
        assert sign_ep["summary"] == "Sign content"

    def test_includes_tags(self):
        body = self.client.get("/api/v1/").json()
        endpoints = body["data"]["endpoints"]
        sign_ep = next(e for e in endpoints if e["path"] == "/api/v1/sign")
        assert "Signing" in sign_ep.get("tags", [])

    def test_excludes_health_endpoint(self):
        body = self.client.get("/api/v1/").json()
        paths = [e["path"] for e in body["data"]["endpoints"]]
        assert "/health" not in paths

    def test_includes_endpoint_count(self):
        body = self.client.get("/api/v1/").json()
        count = body["data"]["endpoint_count"]
        endpoints = body["data"]["endpoints"]
        assert count == len(endpoints)
        assert count > 0

    def test_includes_docs_url_in_meta(self):
        body = self.client.get("/api/v1/").json()
        assert body["meta"]["docs_url"] == "/docs"

    def test_excludes_head_and_options(self):
        body = self.client.get("/api/v1/").json()
        methods = [e["method"] for e in body["data"]["endpoints"]]
        assert "HEAD" not in methods
        assert "OPTIONS" not in methods

    def test_endpoints_sorted_by_path(self):
        body = self.client.get("/api/v1/").json()
        paths = [e["path"] for e in body["data"]["endpoints"]]
        assert paths == sorted(paths)

    # -- Security: internal routes are filtered out --

    def test_excludes_admin_routes(self):
        body = self.client.get("/api/v1/").json()
        paths = [e["path"] for e in body["data"]["endpoints"]]
        assert "/api/v1/admin/stats" not in paths

    def test_excludes_provisioning_routes(self):
        body = self.client.get("/api/v1/").json()
        paths = [e["path"] for e in body["data"]["endpoints"]]
        assert "/api/v1/provisioning/auto" not in paths

    def test_excludes_audit_routes(self):
        body = self.client.get("/api/v1/").json()
        paths = [e["path"] for e in body["data"]["endpoints"]]
        assert "/api/v1/audit-logs" not in paths

    def test_excludes_licensing_routes(self):
        body = self.client.get("/api/v1/").json()
        paths = [e["path"] for e in body["data"]["endpoints"]]
        assert "/api/v1/licensing/plans" not in paths

    def test_excludes_hidden_routes(self):
        body = self.client.get("/api/v1/").json()
        paths = [e["path"] for e in body["data"]["endpoints"]]
        assert "/api/v1/internal/debug" not in paths

    def test_caches_after_first_request(self):
        self.client.get("/api/v1/")
        assert discovery_mod._cached_payload is not None
        # Second call uses cache (same object identity)
        payload_ref = discovery_mod._cached_payload
        self.client.get("/api/v1/")
        assert discovery_mod._cached_payload is payload_ref
