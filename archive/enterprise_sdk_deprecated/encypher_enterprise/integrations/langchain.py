"""
LangChain integration helpers for the Encypher Enterprise SDK.

Import these utilities only when `langchain-core` is installed. They provide
helpers to append a signing stage to LangChain runnables and to stream signed
tokens via callback handlers.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from ..client import EncypherClient
from ..exceptions import ConfigurationError
from ..streaming import StreamingSigner


def _ensure_langchain_core() -> Any:
    """
    Lazily import LangChain core utilities so the SDK does not require
    LangChain unless these helpers are used.
    """
    try:
        from langchain_core.runnables import RunnableLambda
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "LangChain integration requires `langchain-core>=0.1`. "
            "Install it via `pip install langchain-core` or "
            "`pip install encypher-enterprise[langchain]`."
        ) from exc

    return RunnableLambda


def _ensure_callback_base():
    try:
        from langchain.callbacks.base import BaseCallbackHandler
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "LangChain callback integration requires `langchain` to be installed. "
            "Install with `pip install langchain` or "
            "`pip install encypher-enterprise[langchain]`."
        ) from exc

    return BaseCallbackHandler


def _extract_text_from_output(output: Any) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Extract textual content from a typical LangChain output.

    Returns a tuple of (text, container_dict_or_none).
    """
    if isinstance(output, str):
        return output, None

    if isinstance(output, dict):
        for key in ("output_text", "text", "answer", "content"):
            value = output.get(key)
            if isinstance(value, str):
                return value, output

    content = getattr(output, "content", None)
    if isinstance(content, str):
        return content, None

    raise ConfigurationError(
        "Unable to extract text from LangChain output. "
        "Ensure your chain returns a string, dict with `text`/`output_text`, "
        "or an object exposing a `.content` attribute."
    )


def apply_signing(
    runnable: Any,
    client: EncypherClient,
    *,
    document_title: Optional[str] = None,
    document_type: str = "ai_output",
    metadata: Optional[Dict[str, Any]] = None,
    sign_kwargs: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Pipe a LangChain runnable into a signing step.

    Example:
        >>> signed_chain = apply_signing(chain, client, document_title="Demo")
        >>> result = signed_chain.invoke({"question": "What is C2PA?"})

    The returned runnable appends `signed_text` to dict outputs or returns the
    signed text directly when the upstream runnable yields a string.
    """
    RunnableLambda = _ensure_langchain_core()
    sign_kwargs = sign_kwargs or {}

    def _sign_output(output: Any) -> Any:
        text, container = _extract_text_from_output(output)
        response = client.sign(
            text=text,
            document_title=document_title,
            document_type=document_type,
            metadata=metadata,
            **sign_kwargs,
        )

        if container is None:
            return response.signed_text

        enriched = dict(container)
        enriched.setdefault("original_text", text)
        enriched["signed_text"] = response.signed_text
        enriched["signing_response"] = response
        return enriched

    return runnable | RunnableLambda(_sign_output)


def make_streaming_callback(
    client: EncypherClient,
    *,
    document_title: Optional[str] = None,
    document_type: str = "ai_output",
    metadata: Optional[Dict[str, Any]] = None,
    sign_kwargs: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Create a LangChain callback handler that signs streamed LLM tokens.

    The returned handler buffers tokens, signs them via `StreamingSigner`,
    and exposes the signed text on the `signed_output` attribute.
    """
    BaseCallbackHandler = _ensure_callback_base()
    sign_kwargs = sign_kwargs or {}

    class EncypherLangChainCallback(BaseCallbackHandler):  # type: ignore
        def __init__(self) -> None:
            self._signer = StreamingSigner(
                client,
                document_title=document_title,
                document_type=document_type,
                metadata=metadata,
                **sign_kwargs,
            )
            self.signed_output: str = ""

        def on_llm_new_token(  # pragma: no cover - requires LangChain runtime
            self,
            token: str,
            *,
            run_id: str,
            parent_run_id: Optional[str] = None,
            **kwargs: Any,
        ) -> None:
            signed = self._signer.process_chunk(token)
            if signed:
                self.signed_output += signed

        def on_llm_end(  # pragma: no cover - requires LangChain runtime
            self,
            response: Any,
            *,
            run_id: str,
            parent_run_id: Optional[str] = None,
            **kwargs: Any,
        ) -> None:
            final = self._signer.finalize()
            if final:
                self.signed_output += final

    return EncypherLangChainCallback()
