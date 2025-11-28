from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_demo_request(client: TestClient):
    data = {
        "name": "Test User",
        "email": "test@example.com",
        "organization": "Test Corp",
        "role": "Developer",
        "message": "Interested in a demo.",
        "source": "test",
        "consent": True
    }
    response = client.post(f"{settings.API_V1_STR}/demo-requests/", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["email"] == data["email"]
    assert content["name"] == data["name"]
    assert "id" in content
    assert "uuid" in content

def test_create_demo_request_invalid_email(client: TestClient):
    data = {
        "name": "Test User",
        "email": "invalid-email",
        "organization": "Test Corp",
        "role": "Developer",
        "message": "Interested in a demo.",
        "source": "test",
        "consent": True
    }
    response = client.post(f"{settings.API_V1_STR}/demo-requests/", json=data)
    assert response.status_code == 422
