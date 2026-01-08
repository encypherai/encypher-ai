import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
KEY_SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KEY_SERVICE_ROOT))


class _DummyResult:
    def __init__(self, row):
        self._row = row

    def fetchone(self):
        return self._row


@pytest.fixture
def dummy_org_row():
    return SimpleNamespace(
        key_id="key_123",
        organization_id="org_test",
        user_id="user_123",
        key_permissions=["verify"],
        is_active=True,
        is_revoked=False,
        expires_at=None,
        organization_name="Test Org",
        tier="starter",
        features={},
        monthly_api_limit=10000,
        monthly_api_usage=0,
        coalition_member=False,
        coalition_rev_share=0,
        certificate_pem="-----BEGIN PUBLIC KEY-----\nZm9v\n-----END PUBLIC KEY-----\n",
    )


@pytest.fixture
def mock_db(dummy_org_row):
    class _DB:
        def __init__(self):
            self.execute_calls = 0

        def execute(self, *args, **kwargs):
            self.execute_calls += 1
            if self.execute_calls == 1:
                return _DummyResult(dummy_org_row)
            return _DummyResult(None)

        def commit(self):
            return None

        def rollback(self):
            return None

        def close(self):
            return None

    return _DB()


@pytest.fixture
def test_app(mock_db) -> FastAPI:
    app = FastAPI()

    from app.api.v1.endpoints import router as v1_router
    from app.db.session import get_db

    app.include_router(v1_router, prefix="/api/v1/keys")
    app.dependency_overrides[get_db] = lambda: mock_db
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)
