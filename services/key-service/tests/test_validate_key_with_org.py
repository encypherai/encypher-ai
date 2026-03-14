import pytest


def test_validate_key_returns_certificate_pem(client, monkeypatch) -> None:
    from app.services.key_service import KeyService

    monkeypatch.setattr(
        KeyService,
        "_fetch_org_certificate_pem",
        lambda _org_id: "-----BEGIN PUBLIC KEY-----\nZm9v\n-----END PUBLIC KEY-----\n",
    )

    api_key = "ency_" + ("a" * 32)  # pragma: allowlist secret
    response = client.post("/api/v1/keys/validate", json={"key": api_key})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["certificate_pem"].startswith("-----BEGIN PUBLIC KEY-----")


def test_validate_key_returns_none_when_no_certificate(client, monkeypatch) -> None:
    from app.services.key_service import KeyService

    monkeypatch.setattr(KeyService, "_fetch_org_certificate_pem", lambda _org_id: None)

    api_key = "ency_" + ("a" * 32)  # pragma: allowlist secret
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

    api_key = "ency_" + ("a" * 32)  # pragma: allowlist secret
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


def test_user_level_super_admin_key_uses_configured_publisher_identity(monkeypatch) -> None:
    from types import SimpleNamespace

    from app.core.config import settings
    from app.services.key_service import KeyService

    class _DummyResult:
        def __init__(self, row):
            self._row = row

        def fetchone(self):
            return self._row

    class _DummyDB:
        def __init__(self):
            self.execute_calls = 0
            self.row = SimpleNamespace(
                key_id="key_superadmin",
                organization_id=None,
                user_id="a1621dd6-3298-473f-b2ad-232ca72c3df5",
                key_permissions=["sign", "verify", "super_admin"],
                is_active=True,
                is_revoked=False,
                expires_at=None,
            )

        def execute(self, *args, **kwargs):
            self.execute_calls += 1
            if self.execute_calls == 1:
                return _DummyResult(self.row)
            return _DummyResult(None)

        def commit(self):
            return None

        def rollback(self):
            return None

    monkeypatch.setattr(settings, "SUPERADMIN_PUBLISHER_DISPLAY_NAME", "Encypher Publisher", raising=False)
    monkeypatch.setattr(settings, "SUPERADMIN_USER_IDS", "a1621dd6-3298-473f-b2ad-232ca72c3df5", raising=False)
    result = KeyService.verify_key_with_org(_DummyDB(), "ency_" + ("a" * 32))

    assert result is not None
    assert result["organization_name"] == "Encypher Publisher"
    assert result["display_name"] == "Encypher Publisher"
    assert result["account_type"] == "organization"


def test_create_key_enforces_free_tier_active_key_cap(monkeypatch) -> None:
    from types import SimpleNamespace

    from app.models.schemas import ApiKeyCreate
    from app.services.key_service import ApiKey, KeyService, Organization

    class _OrgQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return SimpleNamespace(id="org_test", name="Test Org", tier="free")

    class _KeyQuery:
        def filter(self, *args, **kwargs):
            return self

        def count(self):
            return 2

    class _DummyDB:
        def query(self, model):
            if model is Organization:
                return _OrgQuery()
            if model is ApiKey:
                return _KeyQuery()
            raise AssertionError("Unexpected model")

        def add(self, _obj):
            raise AssertionError("Should not add key when limit reached")

        def commit(self):
            raise AssertionError("Should not commit when limit reached")

        def refresh(self, _obj):
            raise AssertionError("Should not refresh when limit reached")

    monkeypatch.setattr(KeyService, "_ensure_organization_exists", lambda db, org_id, authorization: True)
    monkeypatch.setattr(KeyService, "_ensure_organization_certificate", lambda **kwargs: True)

    with pytest.raises(ValueError) as exc_info:
        KeyService.create_key(
            db=_DummyDB(),
            user_id="user_123",
            key_data=ApiKeyCreate(name="Test Key", organization_id="org_test"),
            organization_id="org_test",
            authorization="Bearer test",
        )

    assert "2 active API keys" in str(exc_info.value)
