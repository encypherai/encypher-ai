import json
import httpx
import pytest

from encypher_enterprise import AsyncEncypherClient
from encypher_enterprise.models import (
    SignResponse,
    EncodeWithEmbeddingsRequest,
    EmbeddingOptions,
)


class DummyAsyncStream:
    def __init__(self, lines):
        self._lines = lines
        self.status_code = 200

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def aiter_lines(self):
        for line in self._lines:
            yield line


def _setup_async_client(monkeypatch, handler) -> AsyncEncypherClient:
    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    def async_client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr("encypher_enterprise.async_client.httpx.AsyncClient", async_client_factory)
    return AsyncEncypherClient(api_key="async-token", base_url="https://api.encypher.com")


@pytest.mark.asyncio
async def test_async_sign_includes_metadata(monkeypatch):
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = json.loads(request.content.decode())
        payload = SignResponse(
            success=True,
            document_id="doc_async",
            signed_text="signed:async",
            total_sentences=1,
            verification_url="https://verify/doc_async",
        )
        return httpx.Response(200, json=payload.model_dump())

    client = _setup_async_client(monkeypatch, handler)

    result = await client.sign("async content", metadata={"mode": "async"})
    await client.close()

    assert result.document_id == "doc_async"
    assert captured["json"]["custom_metadata"] == {"mode": "async"}


@pytest.mark.asyncio
async def test_async_sign_with_embeddings(monkeypatch):
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = json.loads(request.content.decode())
        return httpx.Response(
            201,
            json={
                "success": True,
                "document_id": "doc_async_embed",
                "merkle_tree": {"root_hash": "abc", "total_leaves": 1, "tree_depth": 1},
                "embeddings": [{"leaf_index": 0, "leaf_hash": "hash"}],
                "embedded_content": "signed",
                "statistics": {"segmentation_level": "sentence"},
                "metadata": None,
            },
        )

    client = _setup_async_client(monkeypatch, handler)
    result = await client.sign_with_embeddings(
        text="Hello async world.",
        document_id="doc_async_embed",
        embedding_options=EmbeddingOptions(method="span"),
    )
    await client.close()

    assert captured["json"]["embedding_options"]["method"] == "span"
    assert result.document_id == "doc_async_embed"


@pytest.mark.asyncio
async def test_async_sign_with_embeddings_request(monkeypatch):
    request = EncodeWithEmbeddingsRequest(text="Req text", document_id="doc_req_async")

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            201,
            json={
                "success": True,
                "document_id": "doc_req_async",
                "merkle_tree": None,
                "embeddings": [{"leaf_index": 0, "leaf_hash": "hash"}],
                "embedded_content": None,
                "statistics": {"count": 1},
                "metadata": None,
            },
        )

    client = _setup_async_client(monkeypatch, handler)
    result = await client.sign_with_embeddings(request=request)
    await client.close()

    assert result.embeddings[0].leaf_index == 0


@pytest.mark.asyncio
async def test_async_get_merkle_tree(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"root_id": "root_async", "root_hash": "abc", "nodes": []},
        )

    client = _setup_async_client(monkeypatch, handler)
    tree = await client.get_merkle_tree("root_async")
    await client.close()

    assert tree.root_hash == "abc"


@pytest.mark.asyncio
async def test_async_get_merkle_proof(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["leaf_index"] == "2"
        return httpx.Response(
            200,
            json={
                "root_hash": "abc",
                "leaf_index": 2,
                "verified": True,
                "proof_path": [],
            },
        )

    client = _setup_async_client(monkeypatch, handler)
    proof = await client.get_merkle_proof("root_async", leaf_index=2)
    await client.close()

    assert proof.verified is True


@pytest.mark.asyncio
async def test_async_verify_sentence(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"valid": True})

    client = _setup_async_client(monkeypatch, handler)
    result = await client.verify_sentence("signed text")
    await client.close()

    assert result.valid is True


@pytest.mark.asyncio
async def test_async_stream_sign(monkeypatch):
    client = _setup_async_client(monkeypatch, lambda _: httpx.Response(200, json={}))
    dummy_stream = DummyAsyncStream(
        [
            "event: start",
            'data: {"pct": 1}',
            "",
            "event: final",
            'data: {"pct": 100}',
            "",
        ]
    )
    monkeypatch.setattr(client.client, "stream", lambda *args, **kwargs: dummy_stream)

    events = []
    async for event in client.stream_sign("hello async"):
        events.append(event)
    await client.close()

    assert events[-1].data["pct"] == 100


@pytest.mark.asyncio
async def test_async_get_stream_run(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"run_id": "run_async", "state": {"pct": 10}})

    client = _setup_async_client(monkeypatch, handler)
    state = await client.get_stream_run("run_async")
    await client.close()

    assert state["state"]["pct"] == 10
