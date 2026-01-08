def test_validate_key_returns_certificate_pem(client) -> None:
    api_key = "ency_" + ("a" * 32)
    response = client.post("/api/v1/keys/validate", json={"key": api_key})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["certificate_pem"].startswith("-----BEGIN PUBLIC KEY-----")
