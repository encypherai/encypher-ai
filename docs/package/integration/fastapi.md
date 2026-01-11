# FastAPI Integration

This guide explains how to integrate Encypher with FastAPI to build robust web applications that can embed and verify metadata in AI-generated content. We will use `UnicodeMetadata` for embedding and verification, and `StreamingHandler` for streaming responses.

## Prerequisites

Before you begin, ensure you have installed the required packages:

```bash
uv add encypher-ai fastapi uvicorn
```

## Complete Example

This example provides a complete FastAPI application with endpoints for embedding metadata in both standard and streaming responses, as well as an endpoint for verification. You can save this code as `main.py` and run it with `uvicorn main:app --reload`.

```python
# main.py
import asyncio
import time
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.streaming import StreamingHandler
from encypher.core.keys import generate_ed25519_key_pair

# --- 1. Initialization and Key Management ---
app = FastAPI(
    title="Encypher FastAPI Integration",
    description="An example of embedding and verifying metadata in API responses using UnicodeMetadata and StreamingHandler.",
)

# For demonstration, we generate keys in memory.
# In production, load these securely (e.g., from environment variables or a vault).
private_key, public_key = generate_ed25519_key_pair()
signer_id = "fastapi-server-signer-001"

# A simple in-memory store for public keys.
# In production, this would be a database or a call to a key management service.
public_keys_store: Dict[str, object] = {signer_id: public_key}

# Public key resolver used during verification.
def public_key_resolver(key_id: str):
    return public_keys_store.get(key_id)

# --- 2. Pydantic Models for Requests ---
class EmbedRequest(BaseModel):
    text: str
    custom_metadata: Dict[str, Any]

class VerifyRequest(BaseModel):
    text: str
    from_stream: bool = False

class StreamRequest(BaseModel):
    custom_metadata: Optional[Dict[str, Any]] = None


# --- 3. Non-Streaming Endpoints ---
@app.post("/embed", summary="Embed metadata in text")
async def embed_metadata(request: EmbedRequest) -> Dict[str, str]:
    """
    Embeds the provided custom metadata into the text and returns the encoded text.
    """
    try:
        encoded_text = UnicodeMetadata.embed_metadata(
            text=request.text,
            private_key=private_key,
            signer_id=signer_id,
            custom_metadata=request.custom_metadata,
            metadata_format="basic",
        )
        return {"encoded_text": encoded_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to embed metadata: {e}")


@app.post("/verify", summary="Verify metadata in text")
async def verify_metadata(request: VerifyRequest) -> Dict[str, Any]:
    """
    Verifies the metadata in the text and returns the validation status and payload.
    For streamed content, set `from_stream` to true to disable hard binding verification.
    """
    try:
        # For streamed content, hard binding is not present and must be disabled.
        is_valid, extracted_signer_id, payload = UnicodeMetadata.verify_metadata(
            text=request.text,
            public_key_resolver=public_key_resolver,
            require_hard_binding=not request.from_stream,
        )

        if payload is None:
            return {"is_valid": False, "message": "No metadata found in text."}

        return {"is_valid": is_valid, "signer_id": extracted_signer_id, "payload": payload}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: {e}")


# --- 4. Streaming Endpoint ---
@app.post("/stream", summary="Get a streaming response with embedded metadata")
async def stream_response(request: StreamRequest):
    """
    Generates a streaming response from a simulated source and embeds metadata.
    """
    streaming_handler = StreamingHandler(
        private_key=private_key,
        signer_id=signer_id,
        timestamp=None,
        custom_metadata=request.custom_metadata or {},
        metadata_format="basic",
        encode_first_chunk_only=True,
    )

    async def stream_generator():
        # In a real application, you would call an LLM API here.
        # For this example, we simulate a streaming response.
        simulated_llm_chunks = [
            "This is the first chunk ",
            "of a streamed response, ",
            "and this is the final part.",
        ]

        for chunk in simulated_llm_chunks:
            encoded_chunk = streaming_handler.process_chunk(chunk=chunk)
            if encoded_chunk:
                yield encoded_chunk
            await asyncio.sleep(0.1)  # Simulate network delay

        # Finalize the stream to process any buffered content and embed the signature
        final_chunk = streaming_handler.finalize()
        if final_chunk:
            yield final_chunk

    return StreamingResponse(stream_generator(), media_type="text/plain")


# --- 5. Run the Application ---
if __name__ == "__main__":
    import uvicorn

    # To run: uvicorn main:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## How It Works

1.  **Key Management**: We generate an Ed25519 key pair and set up a simple `public_keys_store` dictionary to act as our `public_key_resolver`.

2.  **/embed Endpoint**: This endpoint calls `UnicodeMetadata.embed_metadata()` to sign and embed metadata into a given text.

3.  **/verify Endpoint**: This endpoint calls `UnicodeMetadata.verify_metadata()`. It accepts a `from_stream` flag. If `True`, it disables the hard binding check (`require_hard_binding=False`), which is required for content generated via streaming.

4.  **/stream Endpoint**: For streaming, we instantiate a `StreamingHandler` for each request.
    - `process_chunk()`: Each chunk of the incoming stream is processed. The handler buffers content to optimize for the Unicode encoding space.
    - `finalize()`: Once the source stream is complete, `finalize()` is called to process any remaining buffered content and append the final metadata payload and signature.
    - `StreamingResponse`: FastAPI's `StreamingResponse` is used to send the processed chunks to the client as they become available.

This setup provides a robust and modern way to handle content integrity in a FastAPI application.
```

## Authentication and Security

### API Key Authentication

Implementing API key authentication:

```python
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN
from typing import Dict, Any

app = FastAPI()

# Define API key header
API_KEY = "your-api-key"  # In production, use a secure key management system
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Dependency for API key validation
async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key"
    )

# Protected endpoint
@app.post("/encode", dependencies=[Depends(get_api_key)])
async def encode_metadata(request: Dict[str, Any]):
    # Your implementation here
    pass
```

### CORS Configuration

Configuring CORS for production:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify your frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Specify allowed methods
    allow_headers=["*"],  # Or specify allowed headers
)
```

### Rate Limiting

Implementing rate limiting:

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any, Optional
import time

app = FastAPI()

# Rate limiting configuration
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        window_size: int = 60  # seconds
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = window_size
        self.request_counts: Dict[str, Dict[int, int]] = {}

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host

        # Get current time window
        current_window = int(time.time() / self.window_size)

        # Initialize or update request count
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {}

        # Clean up old windows
        self.request_counts[client_ip] = {
            window: count for window, count in self.request_counts[client_ip].items()
            if window >= current_window - 1
        }

        # Get current count
        current_count = self.request_counts[client_ip].get(current_window, 0)

        # Check if rate limit exceeded
        if current_count >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Update count
        self.request_counts[client_ip][current_window] = current_count + 1

        # Process the request
        return await call_next(request)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
```

## Deployment

### Docker Deployment

Here's a sample Dockerfile for deploying a FastAPI application with Encypher:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

And a sample `requirements.txt`:

```
fastapi>=0.100.0
uvicorn>=0.22.0
encypher-ai>=1.0.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
cryptography>=4.0.0
```

### Environment Variables

Using environment variables for configuration:

```python
from fastapi import FastAPI
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_ed25519_key_pair
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Get configuration from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_URL = os.getenv("DATABASE_URL")
# --- Key Loading/Management ---
# Load your main private key (e.g., from a file or env var)
# Example: Load from PEM file
try:
    with open("private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None # Add password if key is encrypted
        )
except FileNotFoundError:
    print("Warning: private_key.pem not found. Using generated key for demo.")
    private_key, _ = generate_ed25519_key_pair() # Fallback for demo

# Load public keys for resolver (e.g., from DB or config file)
# public_keys_store = load_public_keys_from_db(DB_URL)
# For demo, we used an in-memory dict initialized earlier
# ----------------------------
```

## Best Practices

1. **Secure Key Management**: Store your Encypher private key securely using environment variables or a secure key management system.
2. **Timestamps (optional)**: Timestamps are recommended but optional across all metadata formats (including C2PA). When a timestamp is omitted, C2PA assertions that normally include a `when` field will simply omit it.

3. **Input Validation**: Use Pydantic models to validate input data and provide clear error messages.

4. **Error Handling**: Implement proper error handling for both FastAPI and Encypher operations.

5. **Rate Limiting**: Implement rate limiting to prevent abuse of your API.

6. **Authentication**: Implement API key authentication or OAuth2 for secure access to your API.

7. **CORS Configuration**: Configure CORS properly to allow only trusted domains to access your API.

8. **Logging**: Implement structured logging to track API usage and errors.

9. **Documentation**: Use FastAPI's automatic documentation generation to provide clear API documentation.

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure `allow_origins` in `CORSMiddleware` is correctly configured for your frontend URL in production.

2. **Key Management**: Securely store private keys. Never commit them to version control. Implement a robust `public_key_resolver` that fetches keys from a secure store (like a database or vault) based on `key_id`.

3. **Verification Failures**:
   - Check if the text content was modified *after* metadata embedding.
   - Ensure the `public_key_resolver` correctly retrieves the public key corresponding to the `key_id` used during signing.
   - Verify that the `private_key` used for signing matches the `public_key` returned by the resolver for the given `key_id`.

4. **Streaming Issues**: Ensure the `finalize()` method of `StreamingHandler` is called after the loop to process any buffered content. Check for errors in the async generator logic.

5. **Dependencies**: Make sure `cryptography` is installed (it is included as a dependency of `encypher-ai`).

## Related Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Encypher Streaming Support](../user-guide/streaming.md)
- [Metadata Encoding Guide](../user-guide/metadata-encoding.md)
- [Extraction and Verification](../user-guide/extraction-verification.md)
