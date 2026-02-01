from fastapi.testclient import TestClient


def test_validate_key_returns_certificate_pem(client) -> None:
    api_key = "ency_" + ("a" * 32)
    response = client.post("/api/v1/keys/validate", json={"key": api_key})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["certificate_pem"].startswith("-----BEGIN PUBLIC KEY-----")


def test_validate_key_missing_certificate_column_returns_none(test_app, mock_db_missing_certificate_column) -> None:
    from app.db.session import get_db

    test_app.dependency_overrides[get_db] = lambda: mock_db_missing_certificate_column
    client = TestClient(test_app)

    api_key = "ency_" + ("a" * 32)
    response = client.post("/api/v1/keys/validate", json={"key": api_key})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["certificate_pem"] is None


def test_validate_key_fetches_certificate_from_auth_service_when_missing_column(
    test_app,
    mock_db_missing_certificate_column,
    monkeypatch,
) -> None:
    from app.db.session import get_db
    from app.core.config import settings

    test_app.dependency_overrides[get_db] = lambda: mock_db_missing_certificate_column
    client = TestClient(test_app)

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
