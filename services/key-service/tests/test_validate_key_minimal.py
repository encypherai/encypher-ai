from fastapi.testclient import TestClient


def test_validate_key_minimal_returns_key_identity_only(test_app, mock_db) -> None:
    from app.db.session import get_db

    test_app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(test_app)

    api_key = "ency_" + ("a" * 32)
    response = client.post("/api/v1/keys/validate-minimal", json={"key": api_key})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["key_id"] == "key_123"
    assert data["organization_id"] == "org_test"
    assert data["user_id"] == "user_123"
    assert data["permissions"] == ["verify"]

    assert "tier" not in data
    assert "features" not in data
    assert "certificate_pem" not in data
