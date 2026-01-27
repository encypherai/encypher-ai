from fastapi.testclient import TestClient


def test_validate_key_returns_certificate_pem(client) -> None:
    api_key = "ency_" + ("a" * 32)
    response = client.post("/api/v1/keys/validate", json={"key": api_key})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["certificate_pem"].startswith("-----BEGIN PUBLIC KEY-----")


def test_validate_key_missing_certificate_column_returns_none(test_app, mock_db_missing_certificate_column) -> None:
    from app.db.session import get_db

    test_app.dependency_overrides[get_db] = lambda: mock_db_missing_certificate_column
    client = TestClient(test_app)

    api_key = "ency_" + ("a" * 32)
    response = client.post("/api/v1/keys/validate", json={"key": api_key})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["certificate_pem"] is None
