"""
LiteLLM Integration Example for EncypherAI

This example demonstrates how to integrate EncypherAI with LiteLLM
to encode metadata into LLM responses.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import litellm
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field

from encypher.config.settings import Settings
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.streaming.handlers import StreamingHandler

# Initialize settings
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="EncypherAI API",
    description="""
    EncypherAI API for encoding metadata in LLM outputs.

    This API provides endpoints for:
    - Encoding metadata in LLM responses
    - Streaming support with real-time metadata encoding
    - Support for all major LLM providers through LiteLLM

    For more information, visit [EncypherAI Documentation](https://docs.encypherai.com).
    """,
    version="0.1.0",
    docs_url=None,
    redoc_url="/docs",
    openapi_tags=[
        {
            "name": "chat",
            "description": "Chat completion endpoints with metadata encoding",
        },
        {"name": "status", "description": "API status and health check endpoints"},
    ],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # type: ignore
    allow_credentials=True,  # type: ignore
    allow_methods=["*"],  # type: ignore
    allow_headers=["*"],  # type: ignore
)


# Custom Swagger UI with dark theme
@app.get("/swagger", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=app.openapi_url or "",  # Ensure it's not None
        title=app.title + " - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_favicon_url="https://encypherai.com/favicon.ico",
    )


# Request and response models with enhanced documentation
class ChatMessage(BaseModel):
    """A chat message in the conversation."""

    role: str = Field(description="Message role (system, user, assistant)", example="user")
    content: str = Field(description="Message content", example="What is the capital of France?")


class ChatRequest(BaseModel):
    """Request model for chat completions."""

    messages: List[ChatMessage] = Field(description="List of chat messages in the conversation")
    model: str = Field(description="LLM model to use", example="gpt-3.5-turbo")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature (0.0 to 1.0)", ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate", gt=0)
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    metadata_target: Optional[str] = Field(
        "whitespace",
        description="Where to embed metadata (whitespace, punctuation, first_letter)",
    )
    encode_first_chunk_only: Optional[bool] = Field(
        True,
        description="Whether to encode metadata only in the first chunk when streaming",
    )


class ChatResponse(BaseModel):
    """Response model for chat completions."""

    model: str = Field(description="Model used for generation", example="gpt-3.5-turbo")
    content: str = Field(description="Generated content with embedded metadata")
    metadata: Dict[str, Any] = Field(description="Metadata embedded in the response")


@app.post("/v1/chat/completions", response_model=ChatResponse, tags=["chat"])
async def chat_completions(
    request: ChatRequest,
) -> Union[ChatResponse, StreamingResponse]:
    """
    Generate a chat completion with metadata encoding.

    Args:
        request (ChatRequest): The chat completion request parameters

    Returns:
        ChatResponse: The generated response with embedded metadata

    Raises:
        HTTPException: If there's an error generating the completion
    """
    try:
        # Convert messages to LiteLLM format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        if request.stream:
            return StreamingResponse(
                stream_chat_completion(request, messages),
                media_type="text/event-stream",
            )

        # Generate completion
        response = await litellm.acompletion(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        # Extract content
        content = response.choices[0].message.content

        # Prepare metadata
        metadata = {
            "model_id": request.model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": response.id,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }

        # Encode metadata
        model_id = metadata.get("model_id", "")
        timestamp = metadata.get("timestamp", datetime.now(timezone.utc).isoformat())
        target = request.metadata_target if request.metadata_target is not None else "whitespace"

        encoded_content = UnicodeMetadata.embed_metadata(
            text=content,
            model_id=model_id,
            timestamp=timestamp,
            target=target,
            custom_metadata={k: v for k, v in metadata.items() if k not in ["model_id", "timestamp"]},
        )

        return ChatResponse(model=request.model, content=encoded_content, metadata=metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating completion: {str(e)}")


async def stream_chat_completion(request: ChatRequest, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    """
    Stream a chat completion with metadata encoding.

    Args:
        request (ChatRequest): The chat completion request parameters
        messages (List[Dict[str, str]]): LiteLLM-formatted messages

    Yields:
        Streaming response chunks with metadata
    """
    try:
        # Prepare metadata
        metadata = {
            "model_id": request.model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": f"req_{int(datetime.now().timestamp())}",
        }

        # Initialize streaming handler
        handler = StreamingHandler(
            metadata={
                "model_id": metadata.get("model_id", ""),
                "timestamp": metadata.get("timestamp", datetime.now(timezone.utc).isoformat()),
                "request_id": metadata.get("request_id", f"req_{int(datetime.now().timestamp())}"),
                "session_id": metadata.get("session_id", ""),
            },
            target=(request.metadata_target if request.metadata_target is not None else "whitespace"),
            encode_first_chunk_only=(request.encode_first_chunk_only if request.encode_first_chunk_only is not None else True),
        )

        # Stream completion
        stream = await litellm.acompletion(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
        )

        async for chunk in stream:
            # Extract content from chunk
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content

                # Process chunk with streaming handler
                processed_chunk = handler.process_chunk(content)

                # Yield as server-sent event
                yield f"data: {json.dumps({'content': processed_chunk})}\n\n"
            elif chunk.choices and chunk.choices[0].finish_reason:
                # End of stream
                yield f"data: {json.dumps({'done': True})}\n\n"
    except Exception as e:
        # Yield error
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@app.get("/status", tags=["status"])
async def get_status() -> Dict[str, Any]:
    """
    Get the current status of the API.

    Returns:
        dict: Status information including version and health status
    """
    # Get the package version (fallback to "0.1.0" if not found)
    try:
        import importlib.metadata

        version = importlib.metadata.version("encypher")
    except (ImportError, importlib.metadata.PackageNotFoundError):
        version = "0.1.0"

    return {
        "status": "ok",
        "version": version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    # Set your API keys here or in environment variables
    os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
    # os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"
    # os.environ["GEMINI_API_KEY"] = "your-gemini-api-key"

    uvicorn.run(app, host="0.0.0.0", port=8000)
