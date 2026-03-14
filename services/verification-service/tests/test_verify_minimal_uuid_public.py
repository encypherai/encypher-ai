from __future__ import annotations

from cryptography.hazmat.primitives import serialization
from sqlalchemy.exc import ProgrammingError

from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata

from app.api.v1 import endpoints as verify_endpoints


class _DummyResponse:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload


class _DummyAsyncClient:
    def __init__(self, get_response: _DummyResponse):
        self._get_response = get_response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, *args, **kwargs):
        return self._get_response

    async def post(self, *args, **kwargs):
        raise AssertionError("unexpected POST")


def _pem_from_public_key(public_key) -> str:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")


def test_verify_minimal_uuid_public_fetches_trust_anchor_and_validates(client, mock_db, monkeypatch) -> None:
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "org_a18f662bf1287480"
    manifest_uuid = "7d6b04d7-7e7e-4f59-86b1-9b59211c6d8a"

    signed_text = UnicodeMetadata.embed_metadata(
        text="hello world",
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="basic",
        target=MetadataTarget.WHITESPACE,
        custom_metadata={"manifest_uuid": manifest_uuid},
        add_hard_binding=False,
    )

    mock_result = mock_db.execute.return_value
    mock_result.fetchone.return_value = (1,)

    dummy_response = _DummyResponse(
        200,
        {
            "signer_id": signer_id,
            "signer_name": "Test Org",
            "public_key": _pem_from_public_key(public_key),
            "public_key_algorithm": "Ed25519",
        },
    )

    monkeypatch.setattr(
        verify_endpoints.httpx,
        "AsyncClient",
        lambda: _DummyAsyncClient(dummy_response),
    )

    response = client.post("/api/v1/verify", json={"text": signed_text})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["valid"] is True
    assert payload["data"]["reason_code"] == "OK"
    assert payload["data"]["signer_id"] == signer_id


def test_verify_minimal_uuid_public_missing_record_falls_through_to_trust_anchor(client, mock_db, monkeypatch) -> None:
    """TEAM_156: When manifest_uuid is not in content_references (lightweight UUID
    mode), verification falls through to trust anchor resolution and succeeds."""
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "org_a18f662bf1287480"
    manifest_uuid = "7d6b04d7-7e7e-4f59-86b1-9b59211c6d8a"

    signed_text = UnicodeMetadata.embed_metadata(
        text="hello world",
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="basic",
        target=MetadataTarget.WHITESPACE,
        custom_metadata={"manifest_uuid": manifest_uuid},
        add_hard_binding=False,
    )

    mock_result = mock_db.execute.return_value
    mock_result.fetchone.return_value = None

    dummy_response = _DummyResponse(
        200,
        {
            "signer_id": signer_id,
            "signer_name": "Test Org",
            "public_key": _pem_from_public_key(public_key),
            "public_key_algorithm": "Ed25519",
        },
    )

    monkeypatch.setattr(
        verify_endpoints.httpx,
        "AsyncClient",
        lambda: _DummyAsyncClient(dummy_response),
    )

    response = client.post("/api/v1/verify", json={"text": signed_text})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["valid"] is True
    assert payload["data"]["reason_code"] == "OK"
    assert payload["data"]["signer_id"] == signer_id


def test_verify_minimal_uuid_public_missing_table_falls_through_to_trust_anchor(client, mock_db, monkeypatch) -> None:
    """TEAM_156: When content_references table doesn't exist (lightweight UUID
    mode, dev env), verification falls through to trust anchor resolution."""
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "org_a18f662bf1287480"
    manifest_uuid = "7d6b04d7-7e7e-4f59-86b1-9b59211c6d8a"

    signed_text = UnicodeMetadata.embed_metadata(
        text="hello world",
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="basic",
        target=MetadataTarget.WHITESPACE,
        custom_metadata={"manifest_uuid": manifest_uuid},
        add_hard_binding=False,
    )

    mock_db.execute.side_effect = ProgrammingError(
        "SELECT 1 FROM content_references",
        {"manifest_uuid": manifest_uuid},
        Exception('relation "content_references" does not exist'),
    )

    dummy_response = _DummyResponse(
        200,
        {
            "signer_id": signer_id,
            "signer_name": "Test Org",
            "public_key": _pem_from_public_key(public_key),
            "public_key_algorithm": "Ed25519",
        },
    )

    monkeypatch.setattr(
        verify_endpoints.httpx,
        "AsyncClient",
        lambda: _DummyAsyncClient(dummy_response),
    )

    response = client.post("/api/v1/verify", json={"text": signed_text})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    # TEAM_156: Falls through to trust anchor, verification succeeds
    assert payload["data"]["valid"] is True
    assert payload["data"]["reason_code"] == "OK"
    assert payload["data"]["signer_id"] == signer_id
    # Confirm rollback was called after ProgrammingError
    mock_db.rollback.assert_called_once()
