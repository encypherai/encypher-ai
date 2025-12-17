import pytest
import os
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock(spec=Session)


@pytest.fixture
def test_app(mock_db: MagicMock) -> FastAPI:
    app = FastAPI()

    from app.api.v1.endpoints import router as v1_router
    from app.db.session import get_db

    app.include_router(v1_router, prefix="/api/v1/verify")
    app.dependency_overrides[get_db] = lambda: mock_db
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)
