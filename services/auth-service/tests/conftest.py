"""
Pytest configuration for auth-service tests
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

# Add the auth-service root to the path so we can import app modules
auth_service_root = Path(__file__).parent.parent
sys.path.insert(0, str(auth_service_root))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.db.session import get_db


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def test_app(mock_db):
    app = FastAPI()

    try:
        from app.api.v1.saml import router as saml_router

        app.include_router(saml_router, prefix="/api/v1/auth")
    except ImportError:
        pass

    try:
        from app.api.scim import router as scim_router

        app.include_router(scim_router)
    except ImportError:
        pass

    app.dependency_overrides[get_db] = lambda: mock_db
    return app


@pytest.fixture
def client(test_app):
    return TestClient(test_app)
