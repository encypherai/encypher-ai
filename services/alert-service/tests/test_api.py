"""Tests for alert service API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Patch DB before importing app
with patch("app.db.session.engine"), patch("app.db.session.SessionLocal"):
    from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "alert-service"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "alert-service"
    assert "docs" in data


def test_alertmanager_webhook_empty_payload():
    """Alertmanager webhook should accept an empty alerts list."""
    with patch("app.api.v1.endpoints.get_db") as mock_get_db:
        from unittest.mock import MagicMock

        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        response = client.post(
            "/api/v1/alerts/alertmanager",
            json={"version": "4", "status": "firing", "receiver": "test", "alerts": []},
        )
        assert response.status_code == 200
        assert response.json()["processed"] == 0
