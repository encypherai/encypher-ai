def test_validate_key_returns_certificate_pem(client, monkeypatch) -> None:
    from app.services.key_service import KeyService

    monkeypatch.setattr(
        KeyService,
        "_fetch_org_certificate_pem",
        lambda _org_id: "-----BEGIN PUBLIC KEY-----\nZm9v\n-----END PUBLIC KEY-----\n",
    )

    api_key = "ency_" + ("a" * 32)
    response = client.post("/api/v1/keys/validate", json={"key": api_key})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["certificate_pem"].startswith("-----BEGIN PUBLIC KEY-----")


def test_validate_key_returns_none_when_no_certificate(client, monkeypatch) -> None:
    from app.services.key_service import KeyService

    monkeypatch.setattr(KeyService, "_fetch_org_certificate_pem", lambda _org_id: None)

    api_key = "ency_" + ("a" * 32)
    response = client.post("/api/v1/keys/validate", json={"key": api_key})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["certificate_pem"] is None


def test_validate_key_fetches_certificate_from_auth_service(monkeypatch, client) -> None:
    from app.core.config import settings

    monkeypatch.setattr(settings, "INTERNAL_SERVICE_TOKEN", "internal-token", raising=False)

    class _DummyResponse:
        status_code = 200

        def json(self):
            return {
                "success": True,
                "data": {
                    "certificate_pem": "-----BEGIN PUBLIC KEY-----\nZm9v\n-----END PUBLIC KEY-----\n",
                },
            }

    class _DummyClient:
        def __init__(self, *args, **kwargs):
            self.headers_seen = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def get(self, url, headers=None, timeout=None):
            self.headers_seen = headers
            return _DummyResponse()

    dummy_client = _DummyClient()

    def _dummy_client_factory(*args, **kwargs):
        return dummy_client

    monkeypatch.setattr("app.services.key_service.httpx.Client", _dummy_client_factory)

    api_key = "ency_" + ("a" * 32)
    response = client.post("/api/v1/keys/validate", json={"key": api_key})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["certificate_pem"].startswith("-----BEGIN PUBLIC KEY-----")
    assert dummy_client.headers_seen["X-Internal-Token"] == "internal-token"


def test_ensure_organization_certificate_calls_enterprise_api(monkeypatch) -> None:
    from app.services.key_service import KeyService
    from app.core.config import settings

    monkeypatch.setattr(settings, "ENTERPRISE_API_URL", "http://enterprise-api", raising=False)
    monkeypatch.setattr(settings, "INTERNAL_SERVICE_TOKEN", "internal-token", raising=False)

    class _DummyResponse:
        status_code = 200
        text = "ok"

    class _DummyClient:
        def __init__(self, *args, **kwargs):
            self.post_calls = []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def post(self, url, json=None, headers=None):
            self.post_calls.append((url, json, headers))
            return _DummyResponse()

    dummy_client = _DummyClient()

    monkeypatch.setattr("app.services.key_service.httpx.Client", lambda *args, **kwargs: dummy_client)

    result = KeyService._ensure_organization_certificate(
        organization_id="org_test",
        organization_name="Test Org",
        authorization="Bearer test",
    )

    assert result is True
    assert dummy_client.post_calls
    url, payload, headers = dummy_client.post_calls[0]
    assert url.endswith("/api/v1/provisioning/internal/ensure-certificate")
    assert payload["organization_id"] == "org_test"
    assert payload["organization_name"] == "Test Org"
    assert headers["Authorization"] == "Bearer test"
    assert headers["X-Internal-Token"] == "internal-token"
