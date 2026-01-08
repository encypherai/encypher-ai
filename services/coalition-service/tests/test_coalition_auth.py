from app.api.v1 import endpoints as coalition_endpoints


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


def test_coalition_missing_api_key_returns_401(client) -> None:
    user_id = "00000000-0000-0000-0000-000000000001"
    response = client.get(f"/api/v1/coalition/status/{user_id}")
    assert response.status_code == 401


def test_coalition_cross_user_access_returns_403(client, monkeypatch) -> None:
    dummy_response = _DummyResponse(
        200,
        {
            "success": True,
            "data": {
                "key_id": "key_123",
                "user_id": "00000000-0000-0000-0000-000000000002",
                "organization_id": "org_test",
                "organization_name": "Test Org",
                "tier": "starter",
                "features": {},
                "permissions": ["coalition"],
                "monthly_api_limit": 10000,
                "monthly_api_usage": 0,
                "coalition_member": True,
                "coalition_rev_share": 65,
            },
        },
    )

    monkeypatch.setattr(
        coalition_endpoints.httpx,
        "AsyncClient",
        lambda: _DummyAsyncClient(dummy_response),
    )

    target_user_id = "00000000-0000-0000-0000-000000000001"
    response = client.get(
        f"/api/v1/coalition/status/{target_user_id}",
        headers={"Authorization": "Bearer valid-api-key"},
    )
    assert response.status_code == 403
