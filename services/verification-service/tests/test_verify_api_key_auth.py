from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography import x509
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta

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


def _pem_from_certificate(private_key, public_key) -> str:
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Org"),
            x509.NameAttribute(NameOID.COMMON_NAME, "org_test"),
        ]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=3650))
        .sign(private_key, algorithm=None)
    )
    return cert.public_bytes(serialization.Encoding.PEM).decode("ascii")


def test_verify_missing_api_key_allows_public_verification(client) -> None:
    demo_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(b"\x00" * 32)
    signer_id = "user_123"
    signed_text = UnicodeMetadata.embed_metadata(
        text="hello world",
        private_key=demo_private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        target=MetadataTarget.WHITESPACE,
    )

    response = client.post("/api/v1/verify", json={"text": signed_text})
    assert response.status_code == 200


def test_verify_org_encypher_marketing_uses_secret_key_for_demo_verification(client, monkeypatch) -> None:
    secret_key_hex = "11" * 32
    monkeypatch.setenv("SECRET_KEY", secret_key_hex)

    demo_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(secret_key_hex))
    signer_id = "org_encypher_marketing"
    signed_text = UnicodeMetadata.embed_metadata(
        text="hello world",
        private_key=demo_private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        target=MetadataTarget.WHITESPACE,
    )

    response = client.post("/api/v1/verify", json={"text": signed_text})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["valid"] is True
    assert payload["data"]["reason_code"] == "OK"
    assert payload["data"]["signer_id"] == signer_id


def test_verify_valid_signed_text_with_certificate_pem_returns_200(client, monkeypatch) -> None:
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "org_test"
    signed_text = UnicodeMetadata.embed_metadata(
        text="hello world",
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        target=MetadataTarget.WHITESPACE,
    )

    dummy_response = _DummyResponse(
        200,
        {
            "success": True,
            "data": {
                "key_id": "key_123",
                "organization_id": "org_test",
                "organization_name": "Test Org",
                "tier": "starter",
                "features": {},
                "permissions": ["verify"],
                "monthly_api_limit": 10000,
                "monthly_api_usage": 0,
                "coalition_member": False,
                "coalition_rev_share": 0,
                "certificate_pem": _pem_from_certificate(private_key, public_key),
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
        json={"text": signed_text},
        headers={"Authorization": "Bearer valid-api-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["valid"] is True
    assert payload["data"]["reason_code"] == "OK"
    assert payload["data"]["signer_id"] == signer_id


def test_verify_payload_too_large_returns_413(client, monkeypatch) -> None:
    dummy_response = _DummyResponse(
        200,
        {
            "success": True,
            "data": {
                "key_id": "key_123",
                "organization_id": "org_test",
                "organization_name": "Test Org",
                "tier": "starter",
                "features": {},
                "permissions": ["verify"],
                "monthly_api_limit": 10000,
                "monthly_api_usage": 0,
                "coalition_member": False,
                "coalition_rev_share": 0,
                "certificate_pem": "-----BEGIN PUBLIC KEY-----\nZm9v\n-----END PUBLIC KEY-----\n",
            },
        },
    )

    monkeypatch.setattr(
        verify_endpoints.httpx,
        "AsyncClient",
        lambda: _DummyAsyncClient(dummy_response),
    )

    too_large_text = "a" * (2 * 1024 * 1024 + 1)
    response = client.post(
        "/api/v1/verify",
        json={"text": too_large_text},
        headers={"Authorization": "Bearer valid-api-key"},
    )

    assert response.status_code == 413


def test_verify_valid_signed_text_returns_200(client, monkeypatch) -> None:
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "org_test"
    signed_text = UnicodeMetadata.embed_metadata(
        text="hello world",
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        target=MetadataTarget.WHITESPACE,
    )

    dummy_response = _DummyResponse(
        200,
        {
            "success": True,
            "data": {
                "key_id": "key_123",
                "organization_id": "org_test",
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
        json={"text": signed_text},
        headers={"Authorization": "Bearer valid-api-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["valid"] is True
    assert payload["data"]["reason_code"] == "OK"
    assert payload["data"]["signer_id"] == signer_id


def test_verify_invalid_token_falls_back_to_public(client, monkeypatch) -> None:
    """Invalid auth token should fall back to unauthenticated public verification."""
    dummy_response = _DummyResponse(401, {"detail": "Invalid or expired API key"})

    monkeypatch.setattr(
        verify_endpoints.httpx,
        "AsyncClient",
        lambda: _DummyAsyncClient(dummy_response),
    )

    response = client.post(
        "/api/v1/verify",
        json={"text": "hello"},
        headers={"Authorization": "Bearer invalid-api-key"},
    )
    # Verify is public; invalid auth falls back to unauthenticated access
    assert response.status_code == 200


def test_verify_untrusted_signer_returns_warning_code(client, monkeypatch) -> None:
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "third_party"
    signed_text = UnicodeMetadata.embed_metadata(
        text="hello world",
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        target=MetadataTarget.WHITESPACE,
    )

    # Provide an "embedded" public key for the verifier to use.
    monkeypatch.setattr(
        verify_endpoints,
        "_extract_embedded_c2pa_public_key",
        lambda _text: public_key,
        raising=False,
    )

    # Force trust list validation to fail so we return a distinct warning.
    async def _always_untrusted(*_args, **_kwargs) -> bool:
        return False

    monkeypatch.setattr(
        verify_endpoints,
        "_is_embedded_c2pa_key_trusted",
        _always_untrusted,
        raising=False,
    )

    response = client.post("/api/v1/verify", json={"text": signed_text})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["valid"] is True
    assert payload["data"]["reason_code"] == "UNTRUSTED_SIGNER"
