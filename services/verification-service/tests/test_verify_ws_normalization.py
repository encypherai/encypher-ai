"""Tests for whitespace-normalization retry in verify_text.

When a user copies a multi-paragraph signed article from a browser, rendered
<p> tags produce \\n\\n between paragraphs.  The original signed text was built
with single spaces between paragraphs (WordPress extract_text joins via
implode(' ', ...)).  COSE passes (signer_id set) but the content hash fails
(is_valid=False) because the pasted text differs only in whitespace.

The fix: when COSE verifies but content hash fails, retry with whitespace-
collapsed text before returning SIGNATURE_INVALID.
"""

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


def _make_dummy_client(public_key, signer_id: str) -> _DummyAsyncClient:
    return _DummyAsyncClient(
        _DummyResponse(
            200,
            {
                "success": True,
                "data": {
                    "key_id": "key_test",
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
    )


def test_verify_browser_paste_whitespace_normalization(client, monkeypatch) -> None:
    """Browser copy-paste adds \\n\\n between paragraphs; verify must still pass."""
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "org_ws_test"

    # Sign text where paragraphs are joined by single spaces (as WordPress does)
    signed_text = UnicodeMetadata.embed_metadata(
        text="First paragraph. Second sentence. Third sentence. Second paragraph. More content here. Final sentence.",
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        target=MetadataTarget.WHITESPACE,
        add_hard_binding=True,
    )

    # Simulate browser paste: replace the space between the two "paragraphs"
    # with \n\n (what a browser produces from rendered <p> tags).
    # We need to find where the mid-point space is (after the visible dot+space).
    # Replace the first occurrence of ". " in the clean (visible) portion:
    browser_pasted = signed_text.replace(
        "Third sentence. Second paragraph",
        "Third sentence.\n\nSecond paragraph",
        1,
    )
    # Confirm the text actually changed (the replacement found a match)
    assert browser_pasted != signed_text, "Test setup: replacement must alter text"

    monkeypatch.setattr(
        verify_endpoints.httpx,
        "AsyncClient",
        lambda: _make_dummy_client(public_key, signer_id),
    )

    response = client.post(
        "/api/v1/verify",
        json={"text": browser_pasted},
        headers={"Authorization": "Bearer valid-api-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["valid"] is True, (
        f"Expected valid=True after ws-normalization retry, got reason_code={data.get('reason_code')}"
    )
    assert data["reason_code"] == "OK"
    assert data["signer_id"] == signer_id


def test_verify_no_regression_non_whitespace_tamper(client, monkeypatch) -> None:
    """Content changes (not just whitespace) must still be rejected as SIGNATURE_INVALID."""
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "org_tamper_test"

    signed_text = UnicodeMetadata.embed_metadata(
        text="Original article content. This is important. Final line.",
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        target=MetadataTarget.WHITESPACE,
        add_hard_binding=True,
    )

    # Tamper with actual content (not whitespace)
    tampered = signed_text.replace("Original article", "Modified article", 1)
    assert tampered != signed_text, "Test setup: tamper must alter text"

    monkeypatch.setattr(
        verify_endpoints.httpx,
        "AsyncClient",
        lambda: _make_dummy_client(public_key, signer_id),
    )

    response = client.post(
        "/api/v1/verify",
        json={"text": tampered},
        headers={"Authorization": "Bearer valid-api-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["valid"] is False
    assert data["tampered"] is True
    assert data["reason_code"] == "SIGNATURE_INVALID"
