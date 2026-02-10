# TEAM_156: Regression tests for ZW embedding verification via enterprise API.
"""Tests that ZW embeddings are detected and resolved via enterprise API HTTP call."""

from __future__ import annotations

from uuid import uuid4

from app.api.v1 import endpoints as verify_endpoints
from app.utils.zw_detect import ZWNJ, ZWJ, CGJ, MVS


# ---------------------------------------------------------------------------
# Helpers — build ZW signatures inline
# ---------------------------------------------------------------------------

_CHARS = [ZWNJ, ZWJ, CGJ, MVS]


def _encode_byte(b: int) -> str:
    result = []
    v = b
    for _ in range(4):
        result.append(_CHARS[v % 4])
        v //= 4
    return "".join(result)


def _encode_bytes(data: bytes) -> str:
    return "".join(_encode_byte(b) for b in data)


def _make_zw_signature(sentence_uuid) -> str:
    """Build a 128-char ZW signature (UUID + fake HMAC)."""
    uuid_bytes = sentence_uuid.bytes
    fake_hmac = b"\xab" * 16
    return _encode_bytes(uuid_bytes + fake_hmac)


class _DummyResponse:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload


class _RoutingAsyncClient:
    """Mock httpx.AsyncClient that returns different responses based on URL."""

    def __init__(self, route_map: dict[str, _DummyResponse], default: _DummyResponse | None = None):
        self._route_map = route_map
        self._default = default or _DummyResponse(404)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url: str, *args, **kwargs):
        for pattern, resp in self._route_map.items():
            if pattern in url:
                return resp
        return self._default

    async def post(self, *args, **kwargs):
        raise AssertionError("unexpected POST")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_verify_zw_embedding_resolved_via_api(client, mock_db, monkeypatch) -> None:
    """When text contains a ZW embedding whose UUID is resolved by the enterprise API,
    the verify endpoint should return valid=True with the org info."""
    seg_uuid = uuid4()
    sig = _make_zw_signature(seg_uuid)
    text_with_zw = f"This is a test sentence.{sig}"

    org_id = "org_test_zw_123"
    doc_id = "doc_zw_abc"

    zw_resolve_response = _DummyResponse(200, {
        "segment_uuid": str(seg_uuid),
        "organization_id": org_id,
        "document_id": doc_id,
    })

    monkeypatch.setattr(
        verify_endpoints.httpx,
        "AsyncClient",
        lambda: _RoutingAsyncClient({
            "/zw/resolve/": zw_resolve_response,
        }),
    )

    response = client.post("/api/v1/verify", json={"text": text_with_zw})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["valid"] is True
    assert payload["data"]["reason_code"] == "OK"
    assert payload["data"]["signer_id"] == org_id


def test_verify_zw_embedding_not_found_returns_signer_unknown(client, mock_db, monkeypatch) -> None:
    """When text contains a ZW embedding but enterprise API returns 404,
    the verify endpoint should return SIGNER_UNKNOWN."""
    seg_uuid = uuid4()
    sig = _make_zw_signature(seg_uuid)
    text_with_zw = f"This is a test sentence.{sig}"

    # All HTTP calls return 404
    monkeypatch.setattr(
        verify_endpoints.httpx,
        "AsyncClient",
        lambda: _RoutingAsyncClient({}),
    )

    response = client.post("/api/v1/verify", json={"text": text_with_zw})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["valid"] is False
    assert payload["data"]["reason_code"] == "SIGNER_UNKNOWN"


def test_verify_plain_text_no_zw_returns_signer_unknown(client, mock_db, monkeypatch) -> None:
    """Plain text with no embeddings should return SIGNER_UNKNOWN."""
    monkeypatch.setattr(
        verify_endpoints.httpx,
        "AsyncClient",
        lambda: _RoutingAsyncClient({}),
    )

    response = client.post("/api/v1/verify", json={"text": "Just plain text with no embeddings."})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["valid"] is False
    assert payload["data"]["reason_code"] == "SIGNER_UNKNOWN"
