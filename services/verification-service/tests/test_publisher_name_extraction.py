"""Tests for publisher name extraction from C2PA manifest assertions.

TEAM_210: Verifies that _extract_publisher_name_from_manifest correctly pulls
the human-readable publisher identity from c2pa.metadata assertions, and that
the verify endpoint surfaces it as publisher_name / signer_name in the verdict.
"""

from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata

from app.api.v1.endpoints import _extract_publisher_name_from_manifest
from app.api.v1 import endpoints as verify_endpoints


# ---------------------------------------------------------------------------
# Unit tests for _extract_publisher_name_from_manifest
# ---------------------------------------------------------------------------


def test_extract_publisher_identifier_from_c2pa_metadata() -> None:
    manifest = {
        "assertions": [
            {
                "label": "c2pa.metadata",
                "data": {
                    "publisher": {
                        "identifier": "Erik Svilich at Encypher",
                        "name": "Encypher AI",
                    }
                },
            }
        ]
    }
    assert _extract_publisher_name_from_manifest(manifest) == "Erik Svilich at Encypher"


def test_extract_publisher_name_fallback_when_no_identifier() -> None:
    manifest = {
        "assertions": [
            {
                "label": "c2pa.metadata",
                "data": {
                    "publisher": {"name": "Encypher AI"},
                },
            }
        ]
    }
    assert _extract_publisher_name_from_manifest(manifest) == "Encypher AI"


def test_extract_author_name_fallback_when_no_publisher() -> None:
    manifest = {
        "assertions": [
            {
                "label": "c2pa.metadata",
                "data": {
                    "author": {"name": "Jane Doe"},
                },
            }
        ]
    }
    assert _extract_publisher_name_from_manifest(manifest) == "Jane Doe"


def test_extract_returns_none_when_no_c2pa_metadata_assertion() -> None:
    manifest = {
        "assertions": [
            {"label": "c2pa.actions", "data": {"actions": []}},
        ]
    }
    assert _extract_publisher_name_from_manifest(manifest) is None


def test_extract_returns_none_for_empty_assertions() -> None:
    assert _extract_publisher_name_from_manifest({"assertions": []}) is None


def test_extract_returns_none_for_none_manifest() -> None:
    assert _extract_publisher_name_from_manifest(None) is None


def test_extract_returns_none_for_non_dict_manifest() -> None:
    assert _extract_publisher_name_from_manifest("not a dict") is None  # type: ignore[arg-type]


def test_extract_skips_blank_identifier() -> None:
    manifest = {
        "assertions": [
            {
                "label": "c2pa.metadata",
                "data": {
                    "publisher": {"identifier": "   ", "name": "Encypher AI"},
                },
            }
        ]
    }
    assert _extract_publisher_name_from_manifest(manifest) == "Encypher AI"


def test_extract_ignores_non_c2pa_metadata_labels() -> None:
    manifest = {
        "assertions": [
            {
                "label": "stds.schema-org.CreativeWork",
                "data": {
                    "publisher": {"identifier": "Should Not Be Returned"},
                },
            },
            {
                "label": "c2pa.metadata",
                "data": {
                    "publisher": {"identifier": "Correct Publisher"},
                },
            },
        ]
    }
    assert _extract_publisher_name_from_manifest(manifest) == "Correct Publisher"


# ---------------------------------------------------------------------------
# Integration test: verify endpoint surfaces publisher_name in response
# ---------------------------------------------------------------------------


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

    async def get(self, *args, **kwargs):
        return self._response


def test_verify_endpoint_returns_publisher_name_from_manifest(client, monkeypatch) -> None:
    """When signed content contains c2pa.metadata with publisher.identifier,
    the verify response should include publisher_name and use it as signer_name."""
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "org_test"

    from cryptography.hazmat.primitives import serialization

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")

    signed_text = UnicodeMetadata.embed_metadata(
        text="Hello world",
        private_key=private_key,
        signer_id=signer_id,
        custom_metadata={
            "assertions": [
                {
                    "label": "c2pa.metadata",
                    "data": {
                        "publisher": {"identifier": "Erik Svilich at Encypher"},
                    },
                }
            ]
        },
    )

    dummy = _DummyResponse(
        200,
        {
            "success": True,
            "data": {
                "key_id": "key_123",
                "organization_id": signer_id,
                "organization_name": "Encypher AI",
                "tier": "enterprise",
                "features": {},
                "permissions": ["sign", "verify"],
                "monthly_api_limit": 100000,
                "monthly_api_usage": 0,
                "coalition_member": True,
                "coalition_rev_share": 0.3,
                "certificate_pem": public_key_pem,
            },
        },
    )
    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", lambda: _DummyAsyncClient(dummy))

    response = client.post(
        "/api/v1/verify",
        json={"text": signed_text},
        headers={"Authorization": "Bearer test-key"},
    )
    assert response.status_code == 200
    payload = response.json()
    data = payload["data"]
    assert data["publisher_name"] == "Erik Svilich at Encypher"
    assert data["signer_name"] == "Erik Svilich at Encypher"
