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
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field

from encypher.core.keys import generate_ed25519_key_pair, load_ed25519_private_key
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.streaming.handlers import StreamingHandler

# --- Configuration & Global Variables ---
# For a real application, manage keys securely and load from a proper config system.
# IMPORTANT: Ensure your LLM provider API keys (e.g., OPENAI_API_KEY) are set in your environment for LiteLLM to work.
EXAMPLE_LITELLM_KEYS_DIR = os.path.join(os.path.dirname(__file__), "example_litellm_keys")
EXAMPLE_LITELLM_PRIVATE_KEY_PATH = os.path.join(EXAMPLE_LITELLM_KEYS_DIR, "private_key.pem")
DEFAULT_LITELLM_SIGNER_ID = "litellm-example-signer"

EXAMPLE_PRIVATE_KEY: Optional[Ed25519PrivateKey] = None

# Initialize FastAPI app
app = FastAPI(
    title="EncypherAI LiteLLM Integration API",
    description="""
    EncypherAI API for encoding metadata in LLM outputs using LiteLLM, with Ed25519 digital signatures.

    This API provides endpoints for:
    - Encoding metadata in LLM responses
    - Streaming support with real-time metadata encoding
    - Support for all major LLM providers through LiteLLM

    For more information, visit [EncypherAI Documentation](https://docs.encypherai.com).
    """,
    version="2.2.0",
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


@app.on_event("startup")
async def startup_event():
    global EXAMPLE_PRIVATE_KEY

    os.makedirs(EXAMPLE_LITELLM_KEYS_DIR, exist_ok=True)

    if not os.path.exists(EXAMPLE_LITELLM_PRIVATE_KEY_PATH):
        priv_key, _ = generate_ed25519_key_pair()
        from cryptography.hazmat.primitives import serialization

        with open(EXAMPLE_LITELLM_PRIVATE_KEY_PATH, "wb") as f:
            f.write(
                priv_key.private_bytes(
                    encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()
                )
            )
        print(f"Generated dummy private key for LiteLLM example at {EXAMPLE_LITELLM_PRIVATE_KEY_PATH}")

    EXAMPLE_PRIVATE_KEY = load_ed25519_private_key(EXAMPLE_LITELLM_PRIVATE_KEY_PATH)
    if not EXAMPLE_PRIVATE_KEY:
        raise RuntimeError(f"Failed to load private key from {EXAMPLE_LITELLM_PRIVATE_KEY_PATH}. Please ensure it exists or can be generated.")
    print("LiteLLM EncypherAI example initialized with an example private key.")
    print("IMPORTANT: Ensure your LLM provider API keys (e.g., OPENAI_API_KEY) are set in your environment!")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom Swagger UI with dark theme
@app.get("/swagger", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    try:
        import importlib.metadata

        importlib.metadata.version("encypher")
    except (ImportError, importlib.metadata.PackageNotFoundError):
        pass

    return get_swagger_ui_html(
        openapi_url=app.openapi_url or "",
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
    signer_id: Optional[str] = Field(None, description=f"Signer ID for metadata. If not provided, '{DEFAULT_LITELLM_SIGNER_ID}' will be used.")
    encode_first_chunk_only: Optional[bool] = Field(
        True,
        description="Whether to encode metadata only in the first chunk when streaming",
    )


class ChatResponse(BaseModel):
    """Response model for chat completions."""

    model: str = Field(description="Model used for generation", example="gpt-3.5-turbo")
    content: str = Field(description="Generated content with embedded metadata")
    custom_metadata_embedded: Dict[str, Any] = Field(description="Custom metadata that was embedded in the response")


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
    if EXAMPLE_PRIVATE_KEY is None:
        raise HTTPException(status_code=500, detail="Server error: Private key not loaded.")

    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        actual_signer_id = request.signer_id or DEFAULT_LITELLM_SIGNER_ID

        if request.stream:
            return StreamingResponse(
                stream_chat_completion(request, messages, actual_signer_id),
                media_type="text/event-stream",
            )

        response = await litellm.acompletion(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        content_to_encode = response.choices[0].message.content

        custom_metadata_payload = {
            "llm_model_id": request.model,
            "llm_request_id": response.id,
            "llm_usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }
        timestamp_int = int(datetime.now(timezone.utc).timestamp())

        encoded_content = UnicodeMetadata.embed_metadata(
            text=content_to_encode,
            private_key=EXAMPLE_PRIVATE_KEY,
            signer_id=actual_signer_id,
            timestamp=timestamp_int,
            custom_metadata=custom_metadata_payload,
        )

        return ChatResponse(model=request.model, content=encoded_content, custom_metadata_embedded=custom_metadata_payload)
    except Exception as e:
        print(f"Error in /v1/chat/completions: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating completion: {str(e)}")


async def stream_chat_completion(request: ChatRequest, messages: List[Dict[str, str]], actual_signer_id: str) -> AsyncGenerator[str, None]:
    """
    Stream a chat completion with metadata encoding.
    Assumes StreamingHandler is updated to handle private_key, signer_id, and internal timestamping for signatures.

    Args:
        request (ChatRequest): The chat completion request parameters
        messages (List[Dict[str, str]]): LiteLLM-formatted messages
        actual_signer_id (str): The actual signer ID to use

    Yields:
        Streaming response chunks with metadata
    """
    if EXAMPLE_PRIVATE_KEY is None:
        yield f"data: {json.dumps({'error': 'Server error: Private key not loaded.'})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
        return

    custom_metadata_for_stream = {
        "llm_model_id": request.model,
        "stream_session_id": f"stream_{int(datetime.now(timezone.utc).timestamp())}",
    }

    try:
        handler = StreamingHandler(
            private_key=EXAMPLE_PRIVATE_KEY,
            signer_id=actual_signer_id,
            custom_metadata=custom_metadata_for_stream,
        )
    except TypeError as te:
        print(f"TypeError initializing StreamingHandler: {te}. This example expects an updated StreamingHandler.")
        yield f"data: {json.dumps({'error': 'StreamingHandler not compatible with required signature parameters. Needs library update.'})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
        return
    except Exception as e:
        print(f"Error initializing StreamingHandler: {e}")
        yield f"data: {json.dumps({'error': f'Failed to initialize StreamingHandler: {str(e)}'})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
        return

    try:
        response_stream = await litellm.acompletion(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
        )

        async for chunk_idx, chunk_data in enumerate(response_stream):
            content_delta = chunk_data.choices[0].delta.content
            if content_delta:
                processed_chunk_content = handler.process_chunk(content_delta)
                yield f"data: {json.dumps({'model': request.model, 'delta': processed_chunk_content, 'chunk_index': chunk_idx})}\n\n"
    except Exception as e:
        print(f"Error during LiteLLM streaming: {e}")
        yield f"data: {json.dumps({'error': f'Error during LiteLLM stream: {str(e)}'})}\n\n"
    finally:
        final_chunk = handler.finalize_stream()
        if final_chunk:
            yield f"data: {json.dumps({'model': request.model, 'delta': final_chunk, 'chunk_index': 'final'})}\n\n"
        yield f"data: {json.dumps({'done': True, 'final_custom_metadata_info': custom_metadata_for_stream})}\n\n"


@app.get("/status", tags=["status"])
async def get_status() -> Dict[str, Any]:
    """
    Get the current status of the API.

    Returns:
        dict: Status information including version and health status
    """
    try:
        import importlib.metadata

        version = importlib.metadata.version("encypher")
    except (ImportError, importlib.metadata.PackageNotFoundError):
        version = "2.2.0"

    return {
        "status": "ok",
        "version": version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
    uvicorn.run(app, host="0.0.0.0", port=8000)
