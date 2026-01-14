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

    from app.api.v1 import endpoints as v1_endpoints
    from app.db.session import get_db

    app.include_router(v1_endpoints.router, prefix="/api/v1/verify")

    @app.get("/{document_id}")
    async def _verify_portal_document_id(document_id: str):
        return await v1_endpoints.verify_by_document_id(document_id=document_id, db=mock_db)

    @app.get("/demo/{document_id}")
    async def _verify_portal_demo_document_id(document_id: str):
        return await v1_endpoints.verify_by_document_id(document_id=document_id, db=mock_db)

    app.dependency_overrides[get_db] = lambda: mock_db
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)
