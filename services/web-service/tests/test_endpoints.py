"""
Integration tests for web-service endpoints.
Tests all demo request and analytics endpoints.
"""

import pytest
from fastapi.testclient import TestClient

# Test data
AI_DEMO_REQUEST = {
    "name": "Test User AI",
    "email": "test.ai@example.com",
    "organization": "AI Test Corp",
    "role": "ML Engineer",
    "message": "Testing AI demo request endpoint",
    "consent": True,
    "source": "ai-demo-test",
}

PUBLISHER_DEMO_REQUEST = {
    "name": "Test User Publisher",
    "email": "test.publisher@example.com",
    "organization": "Publisher Test Inc",
    "role": "Content Manager",
    "message": "Testing publisher demo request endpoint",
    "consent": True,
    "source": "publisher-demo-test",
}

ENTERPRISE_SALES_REQUEST = {
    "name": "Enterprise Test User",
    "email": "enterprise@example.com",
    "organization": "Enterprise Corp",
    "role": "CTO",
    "message": "Testing enterprise sales endpoint",
    "consent": True,
    "source": "enterprise-sales-test",
}

GENERAL_SALES_REQUEST = {
    "name": "General Test User",
    "email": "general@example.com",
    "organization": "General Corp",
    "role": "Product Manager",
    "message": "Testing general sales endpoint",
    "consent": True,
    "source": "general-sales-test",
}

ANALYTICS_EVENT = {
    "event_name": "test_event",
    "event_type": "custom",
    "session_id": "test-session-123",
    "page_url": "http://localhost:3000/test",
    "page_title": "Test Page",
    "properties": {"test_property": "test_value", "source": "integration_test"},
}


@pytest.fixture()
def publisher_demo_request_id(client: TestClient) -> str:
    response = client.post(
        "/api/v1/publisher-demo/demo-requests",
        json=PUBLISHER_DEMO_REQUEST,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True
    assert "id" in data
    return data["id"]


def test_health(client: TestClient):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_ai_demo_request(client: TestClient):
    """Test AI demo request endpoint"""
    response = client.post(
        "/api/v1/ai-demo/demo-requests",
        json=AI_DEMO_REQUEST,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True
    assert "id" in data


def test_ai_demo_analytics(client: TestClient):
    """Test AI demo analytics endpoint"""
    response = client.post(
        "/api/v1/ai-demo/analytics/events",
        json=ANALYTICS_EVENT,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True


def test_publisher_demo_analytics(client: TestClient):
    """Test Publisher demo analytics endpoint"""
    event = ANALYTICS_EVENT.copy()
    event["event_name"] = "publisher_demo_loaded"
    response = client.post(
        "/api/v1/publisher-demo/analytics/events",
        json=event,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True


def test_publisher_demo_get_request(client: TestClient, publisher_demo_request_id: str):
    """Test getting a publisher demo request by ID"""
    response = client.get(f"/api/v1/publisher-demo/demo-requests/{publisher_demo_request_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == publisher_demo_request_id
    assert data["email"] == PUBLISHER_DEMO_REQUEST["email"]


def test_enterprise_sales(client: TestClient):
    """Test Enterprise sales endpoint"""
    response = client.post(
        "/api/v1/sales/enterprise-requests",
        json=ENTERPRISE_SALES_REQUEST,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True
    assert "id" in data


def test_general_sales(client: TestClient):
    """Test General sales endpoint"""
    response = client.post(
        "/api/v1/sales/general-requests",
        json=GENERAL_SALES_REQUEST,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True
    assert "id" in data


def test_legacy_demo_request(client: TestClient):
    """Test legacy generic demo request endpoint"""
    legacy_request = {
        "name": "Legacy Test User",
        "email": "legacy@example.com",
        "organization": "Legacy Corp",
        "role": "Developer",
        "message": "Testing legacy endpoint",
        "consent": True,
        "source": "legacy-test",
    }
    response = client.post(
        "/api/v1/demo-requests/",
        json=legacy_request,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert "uuid" in data


def test_marketing_analytics(client: TestClient):
    """Test marketing analytics endpoint"""
    event = {
        "event_type": "page_view",
        "event_name": "legacy_test_event",
        "session_id": "legacy-session-123",
        "page_url": "http://localhost:3000/legacy",
    }
    response = client.post(
        "/api/v1/marketing-analytics/",
        json=event,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["success"] is True


def test_tools_encode_is_deprecated(client: TestClient):
    response = client.post(
        "/api/v1/tools/encode",
        json={"original_text": "payload"},
    )
    assert response.status_code == 410
    assert response.json()["detail"] == "Deprecated endpoint. Use /api/v1/sign instead."


def test_tools_decode_is_deprecated(client: TestClient):
    response = client.post(
        "/api/v1/tools/decode",
        json={"encoded_text": "payload"},
    )
    assert response.status_code == 410
    assert response.json()["detail"] == "Deprecated endpoint. Use /api/v1/verify instead."


def test_newsletter_subscribers_internal_requires_token(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("app.api.v1.endpoints.newsletter.settings.INTERNAL_SERVICE_TOKEN", "internal-secret")

    response = client.get("/api/v1/newsletter/subscribers")

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


def test_newsletter_subscribers_internal_returns_rows(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("app.api.v1.endpoints.newsletter.settings.INTERNAL_SERVICE_TOKEN", "internal-secret")

    subscribe_response = client.post(
        "/api/v1/newsletter/subscribe",
        json={"email": "subscriber@example.com", "source": "blog"},
    )
    assert subscribe_response.status_code == 200

    response = client.get(
        "/api/v1/newsletter/subscribers",
        headers={"X-Internal-Token": "internal-secret"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["total"] >= 1
    assert payload["data"]["subscribers"][0]["email"] == "subscriber@example.com"
    assert payload["data"]["subscribers"][0]["status"] == "active"


def test_newsletter_subscriber_status_update_internal(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("app.api.v1.endpoints.newsletter.settings.INTERNAL_SERVICE_TOKEN", "internal-secret")

    subscribe_response = client.post(
        "/api/v1/newsletter/subscribe",
        json={"email": "invalid@example.com", "source": "blog"},
    )
    assert subscribe_response.status_code == 200

    rows_response = client.get(
        "/api/v1/newsletter/subscribers",
        headers={"X-Internal-Token": "internal-secret"},
    )
    subscriber_id = rows_response.json()["data"]["subscribers"][0]["id"]

    response = client.post(
        f"/api/v1/newsletter/subscribers/{subscriber_id}/status",
        json={"status": "invalid", "reason": "Mailbox rejected by provider"},
        headers={"X-Internal-Token": "internal-secret"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "invalid"
    assert payload["data"]["active"] is False


def test_newsletter_subscriber_delete_internal(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("app.api.v1.endpoints.newsletter.settings.INTERNAL_SERVICE_TOKEN", "internal-secret")

    subscribe_response = client.post(
        "/api/v1/newsletter/subscribe",
        json={"email": "delete-me@example.com", "source": "blog"},
    )
    assert subscribe_response.status_code == 200

    rows_response = client.get(
        "/api/v1/newsletter/subscribers",
        headers={"X-Internal-Token": "internal-secret"},
    )
    subscriber_id = rows_response.json()["data"]["subscribers"][0]["id"]

    response = client.delete(
        f"/api/v1/newsletter/subscribers/{subscriber_id}",
        headers={"X-Internal-Token": "internal-secret"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["deleted"] is True
