"""
LiteLLM integration helpers for the Encypher Enterprise SDK.

LiteLLM lets teams proxy multiple providers through a consistent interface.
These wrappers add automatic signing to completion results.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Generator, Iterable, Optional

from ..client import EncypherClient
from ..streaming import StreamingSigner


def _ensure_litellm():  # pragma: no cover - optional dependency
    try:
        import litellm  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "LiteLLM integration requires `litellm`. "
            "Install with `pip install litellm` or "
            "`pip install encypher-enterprise[litellm]`."
        ) from exc

    return litellm


@dataclass
class SignedLiteLLMResponse:
    raw_response: Any
    signed_text: str
    signing_response: Any

    def as_dict(self) -> Dict[str, Any]:
        response_dict = (
            self.raw_response
            if isinstance(self.raw_response, dict)
            else getattr(self.raw_response, "model_dump", lambda: {})()
        )
        return {
            "raw_response": response_dict,
            "signed_text": self.signed_text,
            "signing_response": self.signing_response,
        }


@dataclass
class SignedLiteLLMStreamEvent:
    raw_event: Any
    signed_chunk: Optional[str]


def completion_with_signing(
    client: EncypherClient,
    *,
    document_title: Optional[str] = None,
    document_type: str = "ai_output",
    metadata: Optional[Dict[str, Any]] = None,
    **litellm_kwargs: Any,
) -> SignedLiteLLMResponse:
    """
    Run a LiteLLM completion request and sign the resulting text.
    """
    litellm = _ensure_litellm()
    response = litellm.completion(**litellm_kwargs)
    text = _extract_completion_text(response)
    signing_response = client.sign(
        text=text,
        document_title=document_title,
        document_type=document_type,
        metadata=metadata,
    )

    return SignedLiteLLMResponse(
        raw_response=response,
        signed_text=signing_response.signed_text,
        signing_response=signing_response,
    )


def stream_completion_with_signing(
    client: EncypherClient,
    *,
    document_title: Optional[str] = None,
    document_type: str = "ai_output",
    metadata: Optional[Dict[str, Any]] = None,
    **litellm_kwargs: Any,
) -> Generator[SignedLiteLLMStreamEvent, None, str]:
    """
    Stream a LiteLLM completion and sign chunks as they arrive.
    """
    litellm = _ensure_litellm()
    litellm_kwargs["stream"] = True
    stream: Iterable[Any] = litellm.stream(**litellm_kwargs)

    signer = StreamingSigner(
        client,
        document_title=document_title,
        document_type=document_type,
        metadata=metadata,
    )

    for event in stream:
        delta = _extract_stream_delta(event)
        signed_chunk = None
        if delta:
            signed_chunk = signer.process_chunk(delta)
        yield SignedLiteLLMStreamEvent(raw_event=event, signed_chunk=signed_chunk)

    final = signer.finalize()
    if final:
        yield SignedLiteLLMStreamEvent(raw_event=None, signed_chunk=final)

    return final


def _extract_completion_text(response: Any) -> str:
    """
    Handle both dict and object responses from LiteLLM.
    """
    # LiteLLM returns dict by default
    if isinstance(response, dict):
        choices = response.get("choices") or []
        if not choices:
            raise ValueError("LiteLLM response missing choices")
        message = choices[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str):
            raise ValueError("LiteLLM response content is not a string")
        return content

    # Some adapters return objects with a similar structure
    choices = getattr(response, "choices", None)
    if not choices:
        raise ValueError("LiteLLM response missing choices")
    message = getattr(choices[0], "message", None)
    if message is None:
        raise ValueError("LiteLLM response missing message")
    content = getattr(message, "content", None)
    if not isinstance(content, str):
        raise ValueError("LiteLLM response content is not a string")
    return content


def _extract_stream_delta(event: Any) -> str:
    if isinstance(event, dict):
        choices = event.get("choices") or []
        if not choices:
            return ""
        delta = choices[0].get("delta") or {}
        return delta.get("content", "")

    choices = getattr(event, "choices", None)
    if not choices:
        return ""
    delta = getattr(choices[0], "delta", None)
    if not delta:
        return ""
    return getattr(delta, "content", "") or ""
