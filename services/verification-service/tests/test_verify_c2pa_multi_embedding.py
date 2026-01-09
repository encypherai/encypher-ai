from __future__ import annotations

from cryptography.hazmat.primitives import serialization

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
    def __init__(self, response: _DummyResponse):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        return self._response


def _pem_from_public_key(public_key) -> str:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")


def test_verify_multi_embedding_c2pa_wrapper_returns_ok(client, monkeypatch) -> None:
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "org_test"

    embedded_one = UnicodeMetadata.embed_metadata(
        text="Hello world.",
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="basic",
        target=MetadataTarget.WHITESPACE,
        custom_metadata={"leaf_index": 0, "leaf_hash": "deadbeef"},
        add_hard_binding=False,
    )
    embedded_two = UnicodeMetadata.embed_metadata(
        text="Second sentence.",
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="basic",
        target=MetadataTarget.WHITESPACE,
        custom_metadata={"leaf_index": 1, "leaf_hash": "cafebabe"},
        add_hard_binding=False,
    )

    full_doc = f"{embedded_one} {embedded_two}"
    signed_doc = UnicodeMetadata.embed_metadata(
        text=full_doc,
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        target=MetadataTarget.WHITESPACE,
        add_hard_binding=True,
    )

    dummy_response = _DummyResponse(
        200,
        {
            "success": True,
            "data": {
                "key_id": "key_123",
                "organization_id": signer_id,
                "organization_name": "Test Org",
                "tier": "starter",
                "features": {},
                "permissions": ["verify"],
                "monthly_api_limit": 10000,
                "monthly_api_usage": 0,
                "coalition_member": False,
                "coalition_rev_share": 0,
                "certificate_pem": _pem_from_public_key(public_key),
            },
        },
    )

    monkeypatch.setattr(
        verify_endpoints.httpx,
        "AsyncClient",
        lambda: _DummyAsyncClient(dummy_response),
    )

    response = client.post(
        "/api/v1/verify",
        json={"text": signed_doc},
        headers={"Authorization": "Bearer valid-api-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["valid"] is True
    assert payload["data"]["reason_code"] == "OK"
    assert payload["data"]["signer_id"] == signer_id
