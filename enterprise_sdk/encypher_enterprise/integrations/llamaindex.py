"""
LlamaIndex integration for Encypher Enterprise SDK.

Provides callback handlers and utilities for signing LlamaIndex outputs.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging

from ..client import EncypherClient
from ..streaming import StreamingSigner

logger = logging.getLogger(__name__)


def _ensure_llamaindex():
    """Ensure LlamaIndex is installed."""
    try:
        from llama_index.core.callbacks import CBEventType, EventPayload
        from llama_index.core.callbacks.base_handler import BaseCallbackHandler
        return CBEventType, EventPayload, BaseCallbackHandler
    except ImportError as exc:
        raise ImportError(
            "LlamaIndex integration requires `llama-index-core`. "
            "Install it via `pip install llama-index-core` or "
            "`pip install encypher-enterprise[llamaindex]`."
        ) from exc


class EncypherCallbackHandler:
    """
    LlamaIndex callback handler for signing query responses.
    
    This handler signs the final response from LlamaIndex queries.
    
    Example:
        >>> from encypher_enterprise import EncypherClient
        >>> from encypher_enterprise.integrations.llamaindex import EncypherCallbackHandler
        >>> 
        >>> client = EncypherClient(api_key="your-key")
        >>> handler = EncypherCallbackHandler(client)
        >>> 
        >>> # Add to LlamaIndex query engine
        >>> query_engine = index.as_query_engine(callback_manager=CallbackManager([handler]))
        >>> response = query_engine.query("What is C2PA?")
        >>> signed_text = handler.get_signed_response()
    """
    
    def __init__(
        self,
        client: EncypherClient,
        *,
        document_title: Optional[str] = None,
        document_type: str = "ai_output",
        metadata: Optional[Dict[str, Any]] = None,
        sign_kwargs: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize callback handler.
        
        Args:
            client: Encypher client
            document_title: Optional document title
            document_type: Document type (default: "ai_output")
            metadata: Optional metadata
            sign_kwargs: Additional signing kwargs
        """
        CBEventType, EventPayload, BaseCallbackHandler = _ensure_llamaindex()
        
        self.client = client
        self.document_title = document_title
        self.document_type = document_type
        self.metadata = metadata or {}
        self.sign_kwargs = sign_kwargs or {}
        
        self._responses: List[str] = []
        self._signed_response: Optional[str] = None
        
        # Create base handler
        class _Handler(BaseCallbackHandler):
            def __init__(self, parent):
                super().__init__(event_starts_to_ignore=[], event_ends_to_ignore=[])
                self.parent = parent
            
            def on_event_end(
                self,
                event_type: CBEventType,
                payload: Optional[Dict[str, Any]] = None,
                event_id: str = "",
                **kwargs: Any
            ) -> None:
                """Handle event end."""
                if event_type == CBEventType.QUERY and payload:
                    # Extract response
                    response = payload.get(EventPayload.RESPONSE)
                    if response:
                        response_text = str(response)
                        self.parent._responses.append(response_text)
                        
                        # Sign the response
                        try:
                            sign_result = self.parent.client.sign(
                                text=response_text,
                                document_title=self.parent.document_title,
                                document_type=self.parent.document_type,
                                metadata=self.parent.metadata,
                                **self.parent.sign_kwargs
                            )
                            self.parent._signed_response = sign_result.signed_text
                            logger.info("LlamaIndex response signed successfully")
                        except Exception as e:
                            logger.error(f"Failed to sign LlamaIndex response: {e}")
        
        self._handler = _Handler(self)
    
    def get_handler(self):
        """Get the underlying LlamaIndex callback handler."""
        return self._handler
    
    def get_signed_response(self) -> Optional[str]:
        """
        Get the signed response.
        
        Returns:
            Signed response text or None if not yet signed
        """
        return self._signed_response
    
    def get_responses(self) -> List[str]:
        """
        Get all responses captured.
        
        Returns:
            List of response texts
        """
        return self._responses.copy()


class EncypherStreamingCallbackHandler:
    """
    LlamaIndex streaming callback handler for signing streamed responses.
    
    This handler signs responses as they stream from LlamaIndex.
    
    Example:
        >>> handler = EncypherStreamingCallbackHandler(client)
        >>> query_engine = index.as_query_engine(
        ...     streaming=True,
        ...     callback_manager=CallbackManager([handler.get_handler()])
        ... )
        >>> response = query_engine.query("Explain C2PA")
        >>> for chunk in response.response_gen:
        ...     print(chunk, end="")
        >>> signed_text = handler.get_signed_output()
    """
    
    def __init__(
        self,
        client: EncypherClient,
        *,
        document_title: Optional[str] = None,
        document_type: str = "ai_output",
        metadata: Optional[Dict[str, Any]] = None,
        sign_on_sentence: bool = True,
        **sign_kwargs
    ):
        """
        Initialize streaming callback handler.
        
        Args:
            client: Encypher client
            document_title: Optional document title
            document_type: Document type
            metadata: Optional metadata
            sign_on_sentence: Sign on sentence boundaries
            **sign_kwargs: Additional signing kwargs
        """
        CBEventType, EventPayload, BaseCallbackHandler = _ensure_llamaindex()
        
        self.client = client
        self.signer = StreamingSigner(
            client,
            document_title=document_title,
            document_type=document_type,
            metadata=metadata,
            sign_on_sentence=sign_on_sentence,
            **sign_kwargs
        )
        
        self._signed_output = ""
        
        # Create base handler
        class _StreamHandler(BaseCallbackHandler):
            def __init__(self, parent):
                super().__init__(event_starts_to_ignore=[], event_ends_to_ignore=[])
                self.parent = parent
            
            def on_event_end(
                self,
                event_type: CBEventType,
                payload: Optional[Dict[str, Any]] = None,
                event_id: str = "",
                **kwargs: Any
            ) -> None:
                """Handle streaming chunks."""
                if event_type == CBEventType.LLM and payload:
                    # Extract streamed chunk
                    chunk = payload.get(EventPayload.RESPONSE)
                    if chunk:
                        chunk_text = str(chunk)
                        
                        # Process through streaming signer
                        try:
                            signed_chunk = self.parent.signer.process_chunk(chunk_text)
                            if signed_chunk:
                                self.parent._signed_output += signed_chunk
                        except Exception as e:
                            logger.error(f"Failed to sign chunk: {e}")
        
        self._handler = _StreamHandler(self)
    
    def get_handler(self):
        """Get the underlying LlamaIndex callback handler."""
        return self._handler
    
    def get_signed_output(self) -> str:
        """
        Get the accumulated signed output.
        
        Returns:
            Signed output text
        """
        # Finalize any remaining buffer
        final = self.signer.finalize()
        if final:
            self._signed_output += final
        
        return self._signed_output
    
    def reset(self):
        """Reset the handler for a new query."""
        self.signer = StreamingSigner(
            self.client,
            sign_on_sentence=self.signer.sign_on_sentence
        )
        self._signed_output = ""


def sign_query_response(
    response: Any,
    client: EncypherClient,
    *,
    document_title: Optional[str] = None,
    document_type: str = "ai_output",
    metadata: Optional[Dict[str, Any]] = None,
    **sign_kwargs
) -> str:
    """
    Sign a LlamaIndex query response.
    
    Args:
        response: LlamaIndex response object
        client: Encypher client
        document_title: Optional document title
        document_type: Document type
        metadata: Optional metadata
        **sign_kwargs: Additional signing kwargs
        
    Returns:
        Signed response text
    """
    # Extract response text
    response_text = str(response)
    
    # Sign it
    sign_result = client.sign(
        text=response_text,
        document_title=document_title,
        document_type=document_type,
        metadata=metadata,
        **sign_kwargs
    )
    
    return sign_result.signed_text
