"""
OpenAI integration helpers for the Encypher Enterprise SDK.

These wrappers keep the official OpenAI Python client optional. Import this
module only when `openai>=1.0` is installed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Generator, Optional

from ..client import EncypherClient
from ..streaming import StreamingSigner


def _ensure_openai():  # pragma: no cover - optional dependency
    try:
        from openai import OpenAI, AsyncOpenAI  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "OpenAI integration requires the official `openai` package. "
            "Install with `pip install openai` or "
            "`pip install encypher-enterprise[openai]`."
        ) from exc

    return OpenAI, AsyncOpenAI


@dataclass
class SignedChatCompletion:
    """
    Wrapper for OpenAI chat completion responses paired with signing metadata.
    """

    raw_response: Any
    signed_text: str
    signing_response: Any

    def as_dict(self) -> Dict[str, Any]:
        return {
            "raw_response": self.raw_response,
            "signed_text": self.signed_text,
            "signing_response": self.signing_response,
        }


@dataclass
class SignedStreamEvent:
    """
    Represents an event in a streaming response along with signed content.
    """

    raw_event: Any
    signed_chunk: Optional[str]


def create_client(**kwargs: Any) -> Any:
    """
    Create an OpenAI client, ensuring the dependency is present.
    """
    OpenAI, _ = _ensure_openai()
    return OpenAI(**kwargs)


def create_async_client(**kwargs: Any) -> Any:
    """
    Create an Async OpenAI client.
    """
    _, AsyncOpenAI = _ensure_openai()
    return AsyncOpenAI(**kwargs)


def chat_completion_with_signing(
    client: EncypherClient,
    *,
    openai_client: Optional[Any] = None,
    document_title: Optional[str] = None,
    document_type: str = "ai_output",
    metadata: Optional[Dict[str, Any]] = None,
    **openai_kwargs: Any,
) -> SignedChatCompletion:
    """
    Request a chat completion from OpenAI and sign the resulting text.
    """
    if openai_client is None:
        openai_client = create_client()

    response = openai_client.chat.completions.create(**openai_kwargs)
    text = _extract_completion_text(response)
    signing_response = client.sign(
        text=text,
        document_title=document_title,
        document_type=document_type,
        metadata=metadata,
    )
    return SignedChatCompletion(
        raw_response=response,
        signed_text=signing_response.signed_text,
        signing_response=signing_response,
    )


def stream_chat_completion_with_signing(
    client: EncypherClient,
    *,
    openai_client: Optional[Any] = None,
    document_title: Optional[str] = None,
    document_type: str = "ai_output",
    metadata: Optional[Dict[str, Any]] = None,
    **openai_kwargs: Any,
) -> Generator[SignedStreamEvent, None, str]:
    """
    Stream a chat completion and yield signed chunks alongside OpenAI events.

    Returns the final signed text when the generator is exhausted.
    """
    if openai_client is None:
        openai_client = create_client()

    openai_kwargs["stream"] = True
    stream = openai_client.chat.completions.create(**openai_kwargs)

    signer = StreamingSigner(
        client,
        document_title=document_title,
        document_type=document_type,
        metadata=metadata,
    )

    for event in stream:
        delta = _extract_delta_text(event)
        signed_chunk = None
        if delta:
            signed_chunk = signer.process_chunk(delta)
        yield SignedStreamEvent(raw_event=event, signed_chunk=signed_chunk)

    final = signer.finalize()
    if final:
        yield SignedStreamEvent(raw_event=None, signed_chunk=final)

    return final


def _extract_completion_text(response: Any) -> str:
    """
    Extract the textual content from an OpenAI chat completion response.
    """
    try:
        choice = response.choices[0]
    except (AttributeError, IndexError, KeyError) as exc:
        raise ValueError("Unexpected OpenAI response structure") from exc

    message = getattr(choice, "message", None) or choice.get("message")  # type: ignore
    if not message:
        raise ValueError("OpenAI response missing message content")

    content = getattr(message, "content", None) or message.get("content")  # type: ignore
    if not isinstance(content, str):
        raise ValueError("OpenAI response content is not a string")

    return content


def _extract_delta_text(event: Any) -> str:
    """
    Extract incremental text from a streaming delta event.
    """
    delta = getattr(event, "choices", None)
    if not delta:
        delta = event.get("choices") if isinstance(event, dict) else None
    if not delta:
        return ""

    choice = delta[0]
    delta_obj = getattr(choice, "delta", None) or choice.get("delta")  # type: ignore
    if not delta_obj:
        return ""

    return getattr(delta_obj, "content", None) or delta_obj.get("content", "")  # type: ignore
