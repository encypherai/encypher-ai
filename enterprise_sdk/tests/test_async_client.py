import json
import httpx
import pytest

from encypher_enterprise import AsyncEncypherClient
from encypher_enterprise.models import SignResponse


def _setup_async_client(monkeypatch, handler) -> AsyncEncypherClient:
    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    def async_client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr("encypher_enterprise.async_client.httpx.AsyncClient", async_client_factory)
    return AsyncEncypherClient(api_key="async-token", base_url="https://api.encypherai.com")


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
