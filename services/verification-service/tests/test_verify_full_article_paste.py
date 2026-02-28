"""Regression test: full article paste (with browser chrome) resolves via ZWC fallback.

Production bug: When a user copies the whole article page from a browser (including
the page title, author metadata, and the Encypher provenance badge appended by
maybe_add_c2pa_badge()), the extra content makes the C2PA content hash fail even
though the C2PA COSE signature verifies (signer_id is extracted).

Old behaviour (bug): ZWC fallback was guarded by ``if not signer_id:`` -- when
C2PA extracted a signer_id from COSE but the hash failed, ZWC was BLOCKED, and
the endpoint returned SIGNATURE_INVALID.

Fix: change guard to ``if not signer_id or not is_valid:`` so that ZWC (and VS256)
fallbacks run whenever verification has not yet succeeded, regardless of whether a
signer_id was found by the C2PA path.

Individual paragraphs already worked because they carry no C2PA wrapper, so
signer_id=None and ZWC ran normally.  Full article now works for the same reason.
"""

from __future__ import annotations

from uuid import uuid4

from cryptography.hazmat.primitives import serialization

from encypher.core.keys import generate_ed25519_key_pair

from app.api.v1 import endpoints as verify_endpoints
from app.utils.zw_detect import ZWNJ, ZWJ, CGJ, MVS


# ---------------------------------------------------------------------------
# ZWC signature builder (inline; avoids cross-test import)
# ---------------------------------------------------------------------------

_ZW_CHARS = [ZWNJ, ZWJ, CGJ, MVS]


def _encode_byte(b: int) -> str:
    result = []
    v = b
    for _ in range(4):
        result.append(_ZW_CHARS[v % 4])
        v //= 4
    return "".join(result)


def _make_zw_signature(sentence_uuid) -> str:
    """Return 128-char ZW signature (16-byte UUID + 16-byte fake HMAC)."""
    uuid_bytes = sentence_uuid.bytes
    fake_hmac = b"\xab" * 16
    return "".join(_encode_byte(b) for b in (uuid_bytes + fake_hmac))


# ---------------------------------------------------------------------------
# HTTP mock helpers
# ---------------------------------------------------------------------------


class _DummyResponse:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload


def _pem_from_public_key(public_key) -> str:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")


def _make_routing_client(zw_uuids: list[str], org_id: str, public_key=None):
    """Async client that routes:

    - POST .../keys/validate       -> cert lookup (404 if public_key is None)
    - GET  .../zw/resolve/<uuid>   -> 404 (single-resolve fallback)
    - POST .../c2pa/zw/resolve     -> ZWC bulk resolve response
    """
    zw_results = [
        {
            "segment_uuid": uid,
            "organization_id": org_id,
            "document_id": "doc_full_article_test",
            "manifest_mode": "zw_embedding",
        }
        for uid in zw_uuids
    ]
    cert_payload = None
    if public_key is not None:
        cert_payload = {
            "success": True,
            "data": {
                "key_id": "key_test",
                "organization_id": org_id,
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
        }

    class _RoutingClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return False

        async def get(self, url: str, *args, **kwargs):
            return _DummyResponse(404)

        async def post(self, url: str, *args, **kwargs):
            if "/api/v1/keys/validate" in url:
                if cert_payload is not None:
                    return _DummyResponse(200, cert_payload)
                return _DummyResponse(404)
            if "/c2pa/zw/resolve" in url:
                return _DummyResponse(200, {"results": zw_results, "not_found": []})
            return _DummyResponse(404)

    return _RoutingClient


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_zwc_fallback_runs_when_c2pa_signer_id_set_but_hash_fails(
    client, monkeypatch
) -> None:
    """When C2PA extracts a signer_id from COSE but the content hash fails
    (because extra browser content surrounds the signed article), the ZWC fallback
    must still run and resolve the sentence-level embeddings.

    Before the fix: ``if not signer_id:`` blocked ZWC when C2PA set signer_id.
    After the fix: ``if not signer_id or not is_valid:`` allows ZWC to run.
    """
    c2pa_signer_id = "org_c2pa_cose_signed"
    zw_org_id = "org_c2pa_cose_signed"  # same org, consistent
    seg_uuid = uuid4()
    sig = _make_zw_signature(seg_uuid)

    # Text that contains ZWC markers (sentence-level embeddings from WP plugin)
    # plus extra surrounding content that would break a C2PA document hash.
    browser_pasted = (
        "My Article Title\n\n"
        f"First paragraph of the article.{sig} Second sentence. Third sentence.\n\n"
        "Second paragraph here. More content. Final sentence.\n\n"
        "Verified by Encypher."
    )

    # Simulate C2PA path: COSE verifies (signer_id is set) but content hash fails.
    # This is what happens when extra browser content surrounds the signed region.
    def _mock_verify_metadata(text, public_key_resolver=None):
        return (False, c2pa_signer_id, {"assertions": []})

    monkeypatch.setattr(
        verify_endpoints.UnicodeMetadata,
        "verify_metadata",
        staticmethod(_mock_verify_metadata),
    )

    monkeypatch.setattr(
        verify_endpoints.httpx,
        "AsyncClient",
        _make_routing_client([str(seg_uuid)], zw_org_id),
    )

    response = client.post(
        "/api/v1/verify",
        json={"text": browser_pasted},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["valid"] is True, (
        "Expected valid=True after ZWC fallback for full-article paste, "
        f"got reason_code={data.get('reason_code')}"
    )
    assert data["reason_code"] == "OK"
    assert data["signer_id"] == zw_org_id


def test_zwc_fallback_skipped_when_c2pa_succeeds(client, monkeypatch) -> None:
    """When C2PA verifies successfully (is_valid=True), ZWC fallback is not needed.

    Confirm that the change to the guard condition does not affect the happy path:
    C2PA success still returns valid=True without ZWC interference.
    """
    _, public_key = generate_ed25519_key_pair()
    signer_id = "org_c2pa_success_test"
    seg_uuid = uuid4()
    sig = _make_zw_signature(seg_uuid)
    article_text = f"Clean article text.{sig} No extra surrounding content."

    # C2PA succeeds immediately
    def _mock_verify_metadata(text, public_key_resolver=None):
        return (True, signer_id, {"assertions": []})

    monkeypatch.setattr(
        verify_endpoints.UnicodeMetadata,
        "verify_metadata",
        staticmethod(_mock_verify_metadata),
    )

    # ZWC resolve would succeed IF called, but we expect it NOT to be called
    # (is_valid=True means the guard skips ZWC).  Use a sentinel to detect calls.
    _zw_called = {"n": 0}

    # Provide a cert so the cert lookup succeeds and reason_code is determined
    # purely by C2PA result, not by missing cert.
    cert_payload = {
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
    }

    class _SentinelClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return False

        async def get(self, url: str, *args, **kwargs):
            return _DummyResponse(404)

        async def post(self, url: str, *args, **kwargs):
            if "/c2pa/zw/resolve" in url:
                _zw_called["n"] += 1
                return _DummyResponse(404)
            if "/api/v1/keys/validate" in url:
                return _DummyResponse(200, cert_payload)
            return _DummyResponse(404)

    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", _SentinelClient)

    response = client.post(
        "/api/v1/verify",
        json={"text": article_text},
        headers={"Authorization": "Bearer valid-api-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["valid"] is True
    assert data["reason_code"] == "OK"
    assert data["signer_id"] == signer_id
    # ZWC resolve must NOT have been called when C2PA already succeeded
    assert _zw_called["n"] == 0, "ZWC resolve should not be called when C2PA succeeded"


def test_content_tamper_rejected_when_zwc_not_in_db(client, monkeypatch) -> None:
    """Actual content tampering is still rejected when the DB has no matching UUIDs.

    ZWC fallback is now allowed to run (via the loosened guard), but since the
    tampered text's UUIDs are not in the DB, the resolve returns no results, and
    the endpoint correctly returns SIGNATURE_INVALID.
    """
    _, public_key = generate_ed25519_key_pair()
    c2pa_signer_id = "org_tamper_guard_test"
    seg_uuid = uuid4()
    sig = _make_zw_signature(seg_uuid)

    tampered_text = f"Modified article content.{sig} This is tampered. Final sentence."

    # C2PA: COSE valid (signer_id set) but hash fails (content was tampered)
    def _mock_verify_metadata(text, public_key_resolver=None):
        return (False, c2pa_signer_id, {"assertions": []})

    monkeypatch.setattr(
        verify_endpoints.UnicodeMetadata,
        "verify_metadata",
        staticmethod(_mock_verify_metadata),
    )

    # Provide cert so reason_code is determined by signature result, not missing cert.
    cert_payload = {
        "success": True,
        "data": {
            "key_id": "key_test",
            "organization_id": c2pa_signer_id,
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
    }

    class _EmptyResolveClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return False

        async def get(self, url: str, *args, **kwargs):
            return _DummyResponse(404)

        async def post(self, url: str, *args, **kwargs):
            if "/api/v1/keys/validate" in url:
                return _DummyResponse(200, cert_payload)
            # ZWC resolve: UUID not in DB (tampered -> UUID was never stored)
            if "/c2pa/zw/resolve" in url:
                return _DummyResponse(200, {"results": [], "not_found": []})
            return _DummyResponse(404)

    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", _EmptyResolveClient)

    response = client.post(
        "/api/v1/verify",
        json={"text": tampered_text},
        headers={"Authorization": "Bearer valid-api-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["valid"] is False
    assert data["tampered"] is True
    assert data["reason_code"] == "SIGNATURE_INVALID"
