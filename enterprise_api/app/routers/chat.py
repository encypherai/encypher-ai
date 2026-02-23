"""
Chat Application Router - OpenAI-Compatible Streaming.

Provides OpenAI-compatible streaming endpoints for chat applications.
"""

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.models.organization import Organization
from app.services.streaming_service import streaming_service

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models


class ChatMessage(BaseModel):
    """Chat message in OpenAI format."""

    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""

    messages: List[ChatMessage]
    model: Optional[str] = "gpt-3.5-turbo"
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: bool = False
    stop: Optional[List[str]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None
    # Encypher-specific
    sign_response: bool = True


class ChatCompletionChoice(BaseModel):
    """Chat completion choice."""

    index: int
    message: Optional[ChatMessage] = None
    delta: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response."""

    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[Dict[str, int]] = None


# OpenAI-Compatible Endpoint


@router.post("/chat/completions")
async def openai_compatible_chat(
    request: ChatCompletionRequest, organization: Organization = Depends(get_current_organization), db: AsyncSession = Depends(get_db)
):
    """
    OpenAI-compatible chat completion endpoint with signing.

    This endpoint mimics the OpenAI Chat Completions API but adds
    C2PA signing to the response content.

    Args:
        request: Chat completion request
        organization: Authenticated organization
        db: Database session

    Returns:
        Chat completion response (streaming or non-streaming)
    """
    if not request.sign_response:
        raise HTTPException(status_code=400, detail="This endpoint requires sign_response=true. Use standard OpenAI API for unsigned responses.")

    if request.stream:
        # Return streaming response
        return StreamingResponse(_stream_chat_completion(request, organization), media_type="text/event-stream")
    else:
        # Return non-streaming response
        import time

        response_text = _generate_mock_response(request.messages)

        session_result = await streaming_service.create_session(
            organization_id=organization.organization_id,
            session_type="chat",
            metadata={"model": request.model, "messages": [m.dict() for m in request.messages]},
        )
        session_id = session_result["session_id"]

        await streaming_service.process_chunk(
            chunk=response_text,
            session_id=session_id,
            organization_id=organization.organization_id,
            private_key_encrypted=organization.private_key_encrypted,
            chunk_id="chunk_0",
        )

        await streaming_service.finalize_stream(
            session_id=session_id,
            organization_id=organization.organization_id,
            private_key_encrypted=organization.private_key_encrypted,
        )

        prompt_text = " ".join(m.content for m in request.messages)
        prompt_tokens = len(prompt_text.split())
        completion_tokens = len(response_text.split())
        total_tokens = prompt_tokens + completion_tokens

        return ChatCompletionResponse(
            id=f"chatcmpl-{session_id}",
            object="chat.completion",
            created=int(time.time()),
            model=request.model or "gpt-3.5-turbo",
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=response_text),
                    finish_reason="stop",
                )
            ],
            usage={"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens, "total_tokens": total_tokens},
        )


async def _stream_chat_completion(request: ChatCompletionRequest, organization: Organization) -> AsyncGenerator[str, None]:
    """
    Generate streaming chat completion response.

    Args:
        request: Chat completion request
        organization: Organization

    Yields:
        SSE-formatted chunks
    """
    import time

    # Create session
    session_result = await streaming_service.create_session(
        organization_id=organization.organization_id,
        session_type="chat",
        metadata={"model": request.model, "messages": [m.dict() for m in request.messages]},
    )
    session_id = session_result["session_id"]

    try:
        # Simulate LLM response (in production, this would call actual LLM)
        # For now, we'll generate a simple response
        response_text = _generate_mock_response(request.messages)

        # Split into chunks and stream
        chunks = _split_into_chunks(response_text)

        for i, chunk in enumerate(chunks):
            # Sign the chunk
            signed_result = await streaming_service.process_chunk(
                chunk=chunk,
                session_id=session_id,
                organization_id=organization.organization_id,
                private_key_encrypted=organization.private_key_encrypted,
                chunk_id=f"chunk_{i}",
            )

            # Format as OpenAI streaming response
            chunk_response = {
                "id": f"chatcmpl-{session_id}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{"index": 0, "delta": {"content": chunk, "role": "assistant" if i == 0 else None}, "finish_reason": None}],
                # Encypher-specific metadata
                "encypher": {"signed": signed_result.get("signed", False), "session_id": session_id},
            }

            # Send as SSE
            yield f"data: {json.dumps(chunk_response)}\n\n"

            # Small delay to simulate streaming
            await asyncio.sleep(0.05)

        # Send final chunk
        final_chunk = {
            "id": f"chatcmpl-{session_id}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"

        # Send [DONE]
        yield "data: [DONE]\n\n"

        # Finalize session
        await streaming_service.finalize_stream(
            session_id=session_id, organization_id=organization.organization_id, private_key_encrypted=organization.private_key_encrypted
        )

    except Exception as e:
        logger.error(f"Error in streaming chat completion: {e}", exc_info=True)
        error_chunk = {"error": {"message": str(e), "type": "server_error"}}
        yield f"data: {json.dumps(error_chunk)}\n\n"


def _generate_mock_response(messages: List[ChatMessage]) -> str:
    """
    Generate a mock LLM response.

    In production, this would call an actual LLM API.

    Args:
        messages: Chat messages

    Returns:
        Generated response text
    """
    last_message = messages[-1].content if messages else ""

    # Simple mock responses
    if "hello" in last_message.lower():
        return "Hello! I'm an AI assistant with C2PA-signed responses. How can I help you today?"
    elif "c2pa" in last_message.lower():
        return "C2PA (Coalition for Content Provenance and Authenticity) is a standard for content authenticity. It allows creators to add tamper-evident metadata to their content, proving its origin and history."
    else:
        return f"I understand you said: '{last_message}'. This is a signed response demonstrating the Encypher streaming API with OpenAI-compatible format."


def _split_into_chunks(text: str, chunk_size: int = 20) -> List[str]:
    """
    Split text into chunks for streaming.

    Args:
        text: Text to split
        chunk_size: Approximate chunk size in characters

    Returns:
        List of chunks
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0

    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1

        if current_size >= chunk_size:
            chunks.append(" ".join(current_chunk) + " ")
            current_chunk = []
            current_size = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# Chat-specific health check


@router.get("/chat/health")
async def chat_health_check():
    """
    Health check for chat streaming endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy", "service": "chat_streaming", "features": {"openai_compatible": True, "streaming": True, "signing": True}}
