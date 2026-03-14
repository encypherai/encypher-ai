# TEAM_170: Verify that the manifest format in verification responses reflects
# the actual manifest_mode used during signing, not a hardcoded internal name.
# Also tests multi-signature resolution, segment location, and C2PA manifest
# passthrough for the "copy a sentence / paragraph to verify" use case.
"""Tests for manifest_mode, segment location, and multi-embedding verification."""

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


# ---------------------------------------------------------------------------
# Helpers — build VS256 signatures inline
# ---------------------------------------------------------------------------

VS_BMP_START = 0xFE00
VS_SUPP_START = 0xE0100
_BYTE_TO_VS = [chr(VS_BMP_START + i) for i in range(16)] + [chr(VS_SUPP_START + i) for i in range(240)]
MAGIC_PREFIX = _BYTE_TO_VS[239] + _BYTE_TO_VS[240] + _BYTE_TO_VS[241] + _BYTE_TO_VS[242]


def _make_vs256_signature(sentence_uuid) -> str:
    """Build a 36-char VS256 signature (4 magic + 16 UUID + 16 HMAC)."""
    uuid_bytes = sentence_uuid.bytes
    fake_hmac = b"\xab" * 16
    payload = uuid_bytes + fake_hmac
    return MAGIC_PREFIX + "".join(_BYTE_TO_VS[b] for b in payload)


# ---------------------------------------------------------------------------
# Mock HTTP client — supports both GET (single) and POST (bulk) resolve
# ---------------------------------------------------------------------------


class _DummyResponse:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload


def _build_bulk_response(uuid_map: dict[str, dict], requested_uuids: list[str]) -> _DummyResponse:
    """Build a BulkResolveResponse from a UUID→payload map."""
    results = []
    not_found = []
    for uid in requested_uuids:
        if uid in uuid_map:
            results.append(uuid_map[uid])
        else:
            not_found.append(uid)
    return _DummyResponse(200, {"results": results, "not_found": not_found})


class _RoutingAsyncClient:
    """Mock httpx.AsyncClient that handles GET and POST for resolve endpoints."""

    def __init__(self, uuid_map: dict[str, dict], default_status: int = 404):
        self._uuid_map = uuid_map
        self._default_status = default_status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url: str, *args, **kwargs):
        # Single resolve: GET /zw/resolve/{uuid}
        for uid, payload in self._uuid_map.items():
            if uid in url:
                return _DummyResponse(200, payload)
        return _DummyResponse(self._default_status)

    async def post(self, url: str, *args, **kwargs):
        # Bulk resolve: POST /zw/resolve
        if "/zw/resolve" in url:
            body = kwargs.get("json", {})
            uuids = body.get("segment_uuids", [])
            return _build_bulk_response(self._uuid_map, uuids)
        return _DummyResponse(self._default_status)


def _mock_client(uuid_map: dict[str, dict]):
    """Create a monkeypatch-ready mock client factory."""
    return lambda: _RoutingAsyncClient(uuid_map)


# ---------------------------------------------------------------------------
# ZW manifest_mode tests
# ---------------------------------------------------------------------------


def test_zw_verify_returns_manifest_mode_from_resolve(client, mock_db, monkeypatch) -> None:
    """When the enterprise API returns manifest_mode='zw_embedding', the verify
    response should expose it on the embeddings array, NOT in the manifest dict."""
    seg_uuid = uuid4()
    sig = _make_zw_signature(seg_uuid)
    text_with_zw = f"This is a test sentence.{sig}"

    uuid_map = {
        str(seg_uuid): {
            "segment_uuid": str(seg_uuid),
            "organization_id": "org_zw_test",
            "document_id": "doc_zw_1",
            "manifest_mode": "zw_embedding",
        },
    }

    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", _mock_client(uuid_map))

    response = client.post("/api/v1/verify", json={"text": text_with_zw})
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["valid"] is True
    manifest = payload["data"]["details"]["manifest"]
    assert "format" not in manifest
    assert payload["data"]["embeddings"][0]["manifest_mode"] == "zw_embedding"


def test_zw_verify_defaults_to_zw_embedding_when_manifest_mode_missing(client, mock_db, monkeypatch) -> None:
    """When the enterprise API does NOT return manifest_mode, the verify
    response manifest should not contain a format field."""
    seg_uuid = uuid4()
    sig = _make_zw_signature(seg_uuid)
    text_with_zw = f"This is a test sentence.{sig}"

    uuid_map = {
        str(seg_uuid): {
            "segment_uuid": str(seg_uuid),
            "organization_id": "org_zw_test",
            "document_id": "doc_zw_1",
        },
    }

    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", _mock_client(uuid_map))

    response = client.post("/api/v1/verify", json={"text": text_with_zw})
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["valid"] is True
    manifest = payload["data"]["details"]["manifest"]
    assert "format" not in manifest


# ---------------------------------------------------------------------------
# VS256 manifest_mode tests
# ---------------------------------------------------------------------------


def test_vs256_verify_returns_micro_ecc_c2pa_from_resolve(client, mock_db, monkeypatch) -> None:
    """manifest_mode='micro_ecc_c2pa' should appear on embeddings, NOT in
    the manifest dict (which must not leak embedding method)."""
    seg_uuid = uuid4()
    sig = _make_vs256_signature(seg_uuid)
    text_with_vs256 = f"This is a test sentence.{sig}"

    uuid_map = {
        str(seg_uuid): {
            "segment_uuid": str(seg_uuid),
            "organization_id": "org_vs256_test",
            "document_id": "doc_vs256_1",
            "manifest_mode": "micro_ecc_c2pa",
        },
    }

    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", _mock_client(uuid_map))

    response = client.post("/api/v1/verify", json={"text": text_with_vs256})
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["valid"] is True
    assert "format" not in payload["data"]["details"]["manifest"]
    assert payload["data"]["embeddings"][0]["manifest_mode"] == "micro_ecc_c2pa"


def test_vs256_verify_returns_micro_c2pa_from_resolve(client, mock_db, monkeypatch) -> None:
    seg_uuid = uuid4()
    sig = _make_vs256_signature(seg_uuid)

    uuid_map = {
        str(seg_uuid): {
            "segment_uuid": str(seg_uuid),
            "organization_id": "org_vs256_test",
            "document_id": "doc_vs256_1",
            "manifest_mode": "micro_c2pa",
        },
    }

    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", _mock_client(uuid_map))

    response = client.post("/api/v1/verify", json={"text": f"Test.{sig}"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert "format" not in data["details"]["manifest"]
    assert data["embeddings"][0]["manifest_mode"] == "micro_c2pa"


def test_vs256_verify_returns_micro_from_resolve(client, mock_db, monkeypatch) -> None:
    seg_uuid = uuid4()
    sig = _make_vs256_signature(seg_uuid)

    uuid_map = {
        str(seg_uuid): {
            "segment_uuid": str(seg_uuid),
            "organization_id": "org_vs256_test",
            "document_id": "doc_vs256_1",
            "manifest_mode": "micro",
        },
    }

    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", _mock_client(uuid_map))

    response = client.post("/api/v1/verify", json={"text": f"Test.{sig}"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert "format" not in data["details"]["manifest"]
    assert data["embeddings"][0]["manifest_mode"] == "micro"


def test_vs256_verify_defaults_to_micro_when_manifest_mode_missing(client, mock_db, monkeypatch) -> None:
    seg_uuid = uuid4()
    sig = _make_vs256_signature(seg_uuid)

    uuid_map = {
        str(seg_uuid): {
            "segment_uuid": str(seg_uuid),
            "organization_id": "org_vs256_test",
            "document_id": "doc_vs256_1",
        },
    }

    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", _mock_client(uuid_map))

    response = client.post("/api/v1/verify", json={"text": f"Test.{sig}"})
    assert response.status_code == 200
    assert "format" not in response.json()["data"]["details"]["manifest"]


# ---------------------------------------------------------------------------
# Segment location tests — single sentence
# ---------------------------------------------------------------------------


def test_vs256_single_sentence_returns_segment_location(client, mock_db, monkeypatch) -> None:
    """Verifying a single copied sentence should return its segment_location
    (paragraph_index, sentence_in_paragraph) in the embeddings array."""
    seg_uuid = uuid4()
    sig = _make_vs256_signature(seg_uuid)
    text = f"The quick brown fox jumps.{sig}"

    uuid_map = {
        str(seg_uuid): {
            "segment_uuid": str(seg_uuid),
            "organization_id": "org_loc_test",
            "document_id": "doc_loc_1",
            "manifest_mode": "micro_ecc_c2pa",
            "segment_location": {"paragraph_index": 2, "sentence_in_paragraph": 1},
            "total_segments": 15,
            "leaf_index": 7,
        },
    }

    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", _mock_client(uuid_map))

    response = client.post("/api/v1/verify", json={"text": text})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["valid"] is True
    assert data["total_embeddings"] == 1
    assert data["total_segments_in_document"] == 15

    emb = data["embeddings"][0]
    assert emb["segment_uuid"] == str(seg_uuid)
    assert emb["leaf_index"] == 7
    assert emb["segment_location"]["paragraph_index"] == 2
    assert emb["segment_location"]["sentence_in_paragraph"] == 1
    assert emb["manifest_mode"] == "micro_ecc_c2pa"


# ---------------------------------------------------------------------------
# Multi-signature tests — copied paragraph
# ---------------------------------------------------------------------------


def test_vs256_multi_sentence_returns_all_embeddings(client, mock_db, monkeypatch) -> None:
    """Verifying a copied paragraph with 3 sentences should resolve all 3
    signatures and return embeddings with segment locations for each."""
    uuids = [uuid4() for _ in range(3)]
    sigs = [_make_vs256_signature(u) for u in uuids]
    text = f"First sentence.{sigs[0]} Second sentence.{sigs[1]} Third sentence.{sigs[2]}"

    uuid_map = {}
    for i, u in enumerate(uuids):
        uuid_map[str(u)] = {
            "segment_uuid": str(u),
            "organization_id": "org_multi_test",
            "document_id": "doc_multi_1",
            "manifest_mode": "micro_ecc_c2pa",
            "segment_location": {"paragraph_index": 1, "sentence_in_paragraph": i},
            "total_segments": 10,
            "leaf_index": 3 + i,
        }

    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", _mock_client(uuid_map))

    response = client.post("/api/v1/verify", json={"text": text})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["valid"] is True
    assert data["total_embeddings"] == 3
    assert data["total_segments_in_document"] == 10

    for i, emb in enumerate(data["embeddings"]):
        assert emb["segment_uuid"] == str(uuids[i])
        assert emb["leaf_index"] == 3 + i
        assert emb["segment_location"]["paragraph_index"] == 1
        assert emb["segment_location"]["sentence_in_paragraph"] == i


# ---------------------------------------------------------------------------
# C2PA manifest passthrough tests
# ---------------------------------------------------------------------------


def test_vs256_c2pa_manifest_shown_in_response(client, mock_db, monkeypatch) -> None:
    """When the DB has a C2PA manifest for the resolved segment, the verify
    response should include c2pa info with validation_type='db_backed_manifest'."""
    seg_uuid = uuid4()
    sig = _make_vs256_signature(seg_uuid)
    text = f"Signed content.{sig}"

    fake_manifest = {
        "manifest_hash": "abc123",
        "assertions": [{"label": "c2pa.actions", "data": {"actions": [{"action": "c2pa.created"}]}}],
    }

    uuid_map = {
        str(seg_uuid): {
            "segment_uuid": str(seg_uuid),
            "organization_id": "org_c2pa_test",
            "document_id": "doc_c2pa_1",
            "manifest_mode": "micro_ecc_c2pa",
            "manifest_data": fake_manifest,
            "total_segments": 5,
        },
    }

    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", _mock_client(uuid_map))

    response = client.post("/api/v1/verify", json={"text": text})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["valid"] is True

    c2pa = data["c2pa"]
    assert c2pa is not None
    assert c2pa["validated"] is True
    assert c2pa["validation_type"] == "db_backed_manifest"
    assert c2pa["manifest_hash"] == "abc123"
    assert len(c2pa["assertions"]) == 1


def test_vs256_manifest_uses_total_signatures_key(client, mock_db, monkeypatch) -> None:
    """TEAM_175 regression: manifest must use 'total_signatures', not
    'total_vs256_signatures' — internal naming should not leak into the API."""
    seg_uuid = uuid4()
    sig = _make_vs256_signature(seg_uuid)
    text = f"Signed content.{sig}"

    uuid_map = {
        str(seg_uuid): {
            "segment_uuid": str(seg_uuid),
            "organization_id": "org_key_test",
            "document_id": "doc_key_1",
            "manifest_mode": "micro_ecc_c2pa",
        },
    }

    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", _mock_client(uuid_map))

    response = client.post("/api/v1/verify", json={"text": text})
    assert response.status_code == 200
    manifest = response.json()["data"]["details"]["manifest"]
    assert "total_signatures" in manifest
    assert "total_vs256_signatures" not in manifest
    assert "format" not in manifest
    assert manifest["total_signatures"] == 1


def test_vs256_no_c2pa_manifest_when_not_stored(client, mock_db, monkeypatch) -> None:
    """When the DB has no manifest_data (e.g. 'micro' mode without C2PA),
    the c2pa field should be None."""
    seg_uuid = uuid4()
    sig = _make_vs256_signature(seg_uuid)
    text = f"Plain micro.{sig}"

    uuid_map = {
        str(seg_uuid): {
            "segment_uuid": str(seg_uuid),
            "organization_id": "org_no_c2pa",
            "document_id": "doc_no_c2pa",
            "manifest_mode": "micro",
        },
    }

    monkeypatch.setattr(verify_endpoints.httpx, "AsyncClient", _mock_client(uuid_map))

    response = client.post("/api/v1/verify", json={"text": text})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["valid"] is True
    assert data["c2pa"] is None
