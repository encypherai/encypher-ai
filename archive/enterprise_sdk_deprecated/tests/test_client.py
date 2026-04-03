import json
import httpx
import pytest

from encypher_enterprise import EncypherClient
from encypher_enterprise.exceptions import AuthenticationError
from encypher_enterprise.models import (
    SignResponse,
    VerifyResponse,
    VerifyVerdict,
    LookupResponse,
    StatsResponse,
    UsageStats,
    EncodeWithEmbeddingsRequest,
    EmbeddingOptions,
)


class DummyStream:
    def __init__(self, lines):
        self._lines = lines
        self.status_code = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def iter_lines(self):
        for line in self._lines:
            yield line


def _setup_mock_client(monkeypatch, handler) -> EncypherClient:
    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    def client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr("encypher_enterprise.client.httpx.Client", client_factory)
    return EncypherClient(api_key="test-token", base_url="https://api.encypher.com")


def test_sign_success_includes_metadata(monkeypatch):
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = json.loads(request.content.decode())
        response = SignResponse(
            success=True,
            document_id="doc_123",
            signed_text="signed:hello",
            total_sentences=1,
            verification_url="https://verify/123",
        )
        return httpx.Response(200, json=response.model_dump())

    client = _setup_mock_client(monkeypatch, handler)
    result = client.sign("hello world", metadata={"source": "unit-test"})
    client.close()

    assert result.document_id == "doc_123"
    assert captured["json"]["custom_metadata"] == {"source": "unit-test"}
    assert captured["json"]["text"] == "hello world"


def test_sign_raises_authentication_error(monkeypatch):
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": "invalid"}})

    client = _setup_mock_client(monkeypatch, handler)

    with pytest.raises(AuthenticationError):
        client.sign("should fail")

    client.close()


def test_verify_success(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/verify"
        payload = VerifyResponse(
            success=True,
            correlation_id="req-123",
            data=VerifyVerdict(
                valid=True,
                tampered=False,
                reason_code="OK",
                signer_id="org_1",
                signer_name="Encypher",
                timestamp=None,
                details={"manifest": {"data": "value"}},
            ),
        )
        return httpx.Response(200, json=payload.model_dump())

    client = _setup_mock_client(monkeypatch, handler)
    result = client.verify("signed content")
    client.close()

    assert result.data is not None
    assert result.data.valid is True
    assert result.data.details["manifest"] == {"data": "value"}
    assert result.correlation_id == "req-123"


def test_lookup_success(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/lookup"
        payload = LookupResponse(
            success=True,
            found=True,
            document_title="Title",
            organization_name="Org",
            publication_date=None,
            sentence_index=3,
            document_url="https://example.com",
        )
        return httpx.Response(200, json=payload.model_dump())

    client = _setup_mock_client(monkeypatch, handler)
    result = client.lookup("sentence")
    client.close()

    assert result.found is True
    assert result.document_title == "Title"


def test_stats_success(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/stats"
        payload = StatsResponse(
            success=True,
            organization_id="org_1",
            organization_name="Encypher",
            tier="enterprise",
            usage=UsageStats(
                documents_signed=10,
                sentences_signed=50,
                api_calls_this_month=5,
                monthly_quota=100,
                quota_remaining=95,
            ),
        )
        return httpx.Response(200, json=payload.model_dump())

    client = _setup_mock_client(monkeypatch, handler)
    stats = client.get_stats()
    client.close()

    assert stats.usage.documents_signed == 10
    assert stats.tier == "enterprise"


def test_sign_with_embeddings_serializes_payload(monkeypatch):
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = json.loads(request.content.decode())
        return httpx.Response(
            201,
            json={
                "success": True,
                "document_id": "doc_embed",
                "merkle_tree": {"root_hash": "abc", "total_leaves": 2, "tree_depth": 2},
                "embeddings": [{"leaf_index": 0, "leaf_hash": "hash0"}],
                "embedded_content": "<p>signed</p>",
                "statistics": {"segmentation_level": "sentence"},
                "metadata": {"instance_id": "inst_123"},
            },
        )

    client = _setup_mock_client(monkeypatch, handler)
    result = client.sign_with_embeddings(
        text="Hello world. This is another sentence.",
        document_id="doc_embed",
        segmentation_level="sentence",
        metadata={"title": "Demo"},
        embedding_options=EmbeddingOptions(include_text=False, format="markdown"),
    )
    client.close()

    assert captured["json"]["segmentation_level"] == "sentence"
    assert captured["json"]["metadata"]["title"] == "Demo"
    assert captured["json"]["embedding_options"]["include_text"] is False
    assert result.embedded_content == "<p>signed</p>"
    assert result.embeddings[0].leaf_index == 0


def test_sign_with_embeddings_accepts_request(monkeypatch):
    payload = EncodeWithEmbeddingsRequest(
        text="Sample text.",
        document_id="doc_req",
    )

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode())
        assert body["document_id"] == "doc_req"
        return httpx.Response(
            201,
            json={
                "success": True,
                "document_id": "doc_req",
                "merkle_tree": None,
                "embeddings": [{"leaf_index": 0, "leaf_hash": "hash"}],
                "embedded_content": None,
                "statistics": {"embeddings_created": 1},
                "metadata": None,
            },
        )

    client = _setup_mock_client(monkeypatch, handler)
    result = client.sign_with_embeddings(request=payload)
    client.close()

    assert result.document_id == "doc_req"


def test_get_merkle_tree(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/enterprise/merkle/tree/root_123"
        return httpx.Response(
            200,
            json={
                "root_id": "root_123",
                "root_hash": "abc",
                "tree_depth": 3,
                "leaf_count": 4,
                "nodes": [],
            },
        )

    client = _setup_mock_client(monkeypatch, handler)
    tree = client.get_merkle_tree("root_123")
    client.close()

    assert tree.root_hash == "abc"
    assert tree.leaf_count == 4


def test_get_merkle_proof_requires_selector(monkeypatch):
    client = _setup_mock_client(monkeypatch, lambda _: httpx.Response(200, json={}))
    with pytest.raises(ValueError):
        client.get_merkle_proof("root_123")
    client.close()


def test_get_merkle_proof_with_leaf_index(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/enterprise/merkle/tree/root_123/proof"
        assert request.url.params["leaf_index"] == "5"
        return httpx.Response(
            200,
            json={
                "root_hash": "abc",
                "leaf_index": 5,
                "verified": True,
                "proof_path": [{"hash": "h1", "position": "left"}],
            },
        )

    client = _setup_mock_client(monkeypatch, handler)
    proof = client.get_merkle_proof("root_123", leaf_index=5)
    client.close()

    assert proof.verified is True
    assert proof.proof_path[0].hash == "h1"


def test_verify_sentence_success(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/public/extract-and-verify"
        payload = {
            "valid": True,
            "content": {"text_preview": "Preview", "leaf_hash": "abc", "leaf_index": 1},
        }
        return httpx.Response(200, json=payload)

    client = _setup_mock_client(monkeypatch, handler)
    result = client.verify_sentence("signed text")
    client.close()

    assert result.valid is True
    assert result.content.leaf_index == 1


def test_stream_sign_parses_events(monkeypatch):
    client = _setup_mock_client(monkeypatch, lambda _: httpx.Response(200, json={}))

    stream = DummyStream(
        [
            "event: start",
            'data: {"pct": 0}',
            "",
            "event: final",
            'data: {"pct": 100}',
            "",
        ]
    )

    monkeypatch.setattr(client.client, "stream", lambda *args, **kwargs: stream)

    events = list(client.stream_sign("stream me"))
    client.close()

    assert events[0].event == "start"
    assert events[-1].data["pct"] == 100


def test_get_stream_run(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/stream/runs/run_123"
        return httpx.Response(200, json={"run_id": "run_123", "state": {"pct": 50}})

    client = _setup_mock_client(monkeypatch, handler)
    state = client.get_stream_run("run_123")
    client.close()

    assert state["state"]["pct"] == 50
