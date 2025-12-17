from app.api.v1 import endpoints as verify_endpoints


class _DummyResponse:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload


class _DummyAsyncClient:
    def __init__(self, response: _DummyResponse):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        return self._response


def test_verify_missing_api_key_returns_401(client) -> None:
    response = client.post("/api/v1/verify", json={"text": "hello"})
    assert response.status_code == 401


def test_verify_invalid_api_key_returns_401(client, monkeypatch) -> None:
    dummy_response = _DummyResponse(401, {"detail": "Invalid or expired API key"})

    monkeypatch.setattr(
        verify_endpoints.httpx,
        "AsyncClient",
        lambda: _DummyAsyncClient(dummy_response),
    )

    response = client.post(
        "/api/v1/verify",
        json={"text": "hello"},
        headers={"Authorization": "Bearer invalid-api-key"},
    )
    assert response.status_code == 401
