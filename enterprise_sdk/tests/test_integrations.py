from types import SimpleNamespace

import pytest

from encypher_enterprise.models import SignResponse
from encypher_enterprise.integrations import langchain, openai as openai_integration, litellm as litellm_integration


class StubClient:
    def __init__(self):
        self.calls = []

    def sign(self, text: str, **kwargs):
        self.calls.append({"text": text, **kwargs})
        return SignResponse(
            success=True,
            document_id="doc",
            signed_text=f"signed:{text}",
            total_sentences=1,
            verification_url="https://verify/doc",
        )


def test_apply_signing_invokes_client(monkeypatch):
    client = StubClient()

    class DummyRunnable:
        def __or__(self, other):
            return other

    class DummyRunnableLambda:
        def __init__(self, func):
            self.func = func

        def invoke(self, value):
            return self.func(value)

    monkeypatch.setattr(langchain, "_ensure_langchain_core", lambda: DummyRunnableLambda)

    runnable = DummyRunnable()
    signed_runnable = langchain.apply_signing(
        runnable,
        client,
        document_title="Demo",
        metadata={"integration": "langchain"},
    )

    result = signed_runnable.invoke({"output_text": "Hello"})
    assert result["signed_text"] == "signed:Hello"
    assert client.calls[0]["metadata"] == {"integration": "langchain"}


def test_make_streaming_callback_accumulates(monkeypatch):
    client = StubClient()

    class DummyBase:
        pass

    monkeypatch.setattr(langchain, "_ensure_callback_base", lambda: DummyBase)

    callback = langchain.make_streaming_callback(
        client,
        metadata={"stream": True},
    )

    callback.on_llm_new_token("Chunk one. ", run_id="1")
    callback.on_llm_end(None, run_id="1")

    assert callback.signed_output.startswith("signed:")
    assert client.calls


def test_openai_chat_completion_wrapper(monkeypatch):
    client = StubClient()

    class FakeChatCompletion:
        def __init__(self, content):
            self.choices = [SimpleNamespace(message=SimpleNamespace(content=content))]

    class FakeChatAPI:
        def __init__(self, response):
            self._response = response

        def create(self, **kwargs):
            return self._response

    class FakeOpenAIClient:
        def __init__(self):
            self.chat = SimpleNamespace(completions=FakeChatAPI(FakeChatCompletion("hi there")))

    monkeypatch.setattr(openai_integration, "_ensure_openai", lambda: (lambda **_: FakeOpenAIClient(), None))

    result = openai_integration.chat_completion_with_signing(
        client,
        document_title="OpenAI Demo",
        metadata={"source": "test"},
    )

    assert result.signed_text.startswith("signed:")
    assert client.calls[0]["metadata"] == {"source": "test"}


def test_litellm_completion_wrapper(monkeypatch):
    client = StubClient()

    fake_response = {
        "choices": [
            {
                "message": {
                    "content": "response text",
                }
            }
        ]
    }

    fake_stream_events = [
        {"choices": [{"delta": {"content": "stream chunk. "}}]},
    ]

    fake_module = SimpleNamespace(
        completion=lambda **kwargs: fake_response,
        stream=lambda **kwargs: iter(fake_stream_events),
    )

    monkeypatch.setattr(litellm_integration, "_ensure_litellm", lambda: fake_module)

    completion = litellm_integration.completion_with_signing(
        client,
        document_title="LiteLLM Demo",
        metadata={"provider": "litellm"},
    )

    assert completion.signed_text.startswith("signed:")
    assert client.calls[0]["metadata"] == {"provider": "litellm"}

    events = list(
        litellm_integration.stream_completion_with_signing(
            client,
            document_title="LiteLLM Stream",
        )
    )
    assert events[-1].signed_chunk.startswith("signed:")
    assert len(client.calls) >= 2
