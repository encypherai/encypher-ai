import asyncio

import pytest

from encypher_enterprise.streaming import (
    StreamingSigner,
    AsyncStreamingSigner,
    sign_stream,
    async_sign_stream,
)
from encypher_enterprise.models import SignResponse


class StubClient:
    def __init__(self):
        self.calls = []

    def sign(self, text: str, **kwargs):
        self.calls.append({"text": text, **kwargs})
        return SignResponse(
            success=True,
            document_id="doc",
            signed_text=f"signed:{text}",
            total_sentences=len(text.split(".")),
            verification_url="https://verify/doc",
        )


class StubAsyncClient:
    def __init__(self):
        self.calls = []

    async def sign(self, text: str, **kwargs):
        self.calls.append({"text": text, **kwargs})
        return SignResponse(
            success=True,
            document_id="doc_async",
            signed_text=f"signed_async:{text}",
            total_sentences=len(text.split(".")),
            verification_url="https://verify/doc_async",
        )


def test_streaming_signer_chunks_and_finalize():
    client = StubClient()
    signer = StreamingSigner(client)

    chunk = "Hello world. "
    emitted = signer.process_chunk(chunk)
    assert emitted.startswith("signed:")
    assert client.calls[0]["text"] == "Hello world."

    final = signer.finalize()
    assert final == emitted  # buffer empty so only original chunk


@pytest.mark.asyncio
async def test_async_streaming_signer(monkeypatch):
    client = StubAsyncClient()
    signer = AsyncStreamingSigner(client)

    emitted = await signer.process_chunk("Async chunk. ")
    assert emitted.startswith("signed_async:")
    assert client.calls[0]["text"] == "Async chunk."

    final = await signer.finalize()
    assert final == emitted


def test_sign_stream_generator():
    client = StubClient()
    chunks = iter(["Hello world. ", "Another sentence. "])
    result = "".join(sign_stream(client, chunks))
    assert result
    assert len(client.calls) == 2


@pytest.mark.asyncio
async def test_async_sign_stream_generator():
    client = StubAsyncClient()

    async def chunker():
        for chunk in ["One async sentence. ", "Two async sentences. "]:
            yield chunk
            await asyncio.sleep(0)

    collected = []
    async for signed in async_sign_stream(client, chunker()):
        collected.append(signed)

    assert collected
    assert len(client.calls) == 2
