# FastAPI Integration

This guide explains how to integrate EncypherAI with FastAPI to build robust web applications that can embed, extract, and verify metadata in AI-generated content.

## Prerequisites

Before you begin, make sure you have:

1. FastAPI and its dependencies installed
2. EncypherAI installed
3. (Optional) An LLM provider API key if you're integrating with an LLM

```bash
uv pip install encypher-ai fastapi uvicorn cryptography
```

## Basic Integration

### Creating a FastAPI Application with EncypherAI

Here's a simple FastAPI application that demonstrates how to embed and extract metadata:

```python
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes, PrivateKeyTypes
import time
import json

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Key Management (Replace with your actual key management) ---
private_key, public_key = generate_key_pair()

# Store public keys (in a real app, this would be a database or secure store)
public_keys_store: Dict[str, PublicKeyTypes] = {
    "fastapi-key-1": public_key
}

def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    """Retrieves the public key based on its ID."""
    return public_keys_store.get(key_id)

# Define request and response models
class EncodeRequest(BaseModel):
    text: str
    metadata: Dict[str, Any]
    target: Optional[str] = "whitespace"
    key_id: str = "fastapi-key-1" # Default key ID

class VerifyRequest(BaseModel):
    text: str

class MetadataResponse(BaseModel):
    has_metadata: bool
    metadata: Optional[Dict[str, Any]] = None
    verified: Optional[bool] = None
    error: Optional[str] = None

# Endpoints
@app.post("/encode", response_model=Dict[str, Any])
async def encode_metadata(request: EncodeRequest):
    """Embed metadata into text"""
    try:
        # Add timestamp if not provided
        request.metadata["timestamp"] = request.metadata.get("timestamp", time.time())
        request.metadata["key_id"] = request.metadata.get("key_id", request.key_id) # Ensure key_id is in metadata

        # Embed metadata
        encoded_text = UnicodeMetadata.embed_metadata(
            text=request.text,
            metadata=request.metadata,
            private_key=private_key # Use the loaded private key
        )

        return {
            "text": encoded_text,
            "metadata": request.metadata
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/verify", response_model=MetadataResponse) # Renamed from extract-verified
async def verify_text(request: VerifyRequest):
    """Extract and verify metadata from text"""
    result = {
        "has_metadata": False,
        "metadata": None,
        "verified": None,
        "error": None
    }

    try:
        # Extract and verify metadata using the resolver
        is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
            request.text,
            public_key_resolver=resolve_public_key
        )
        # Check if metadata was found (even if invalid)
        if verified_metadata is not None:
            result["has_metadata"] = True
            result["metadata"] = verified_metadata
            result["verified"] = is_valid
        else:
             result["has_metadata"] = False # No metadata marker found
    except Exception as e:
        result["error"] = str(e)

    return result

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Advanced Integration

### Streaming Support with FastAPI

To handle streaming content with FastAPI:

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, AsyncGenerator
from encypher.streaming import StreamingHandler
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair # Key management
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
import time
import json
import asyncio
import openai  # Or any other LLM provider

app = FastAPI()

# --- Key Management (Same as above or separate for streaming) ---
stream_private_key, stream_public_key = generate_key_pair()
public_keys_store["fastapi-stream-key"] = stream_public_key # Add to store
# ---------------------------------------------------------------

# Define request model
class StreamRequest(BaseModel):
    prompt: str
    model: str = "gpt-4"
    system_prompt: Optional[str] = "You are a helpful assistant."
    metadata: Optional[Dict[str, Any]] = None

@app.post("/stream")
async def stream_response(request: StreamRequest):
    # Initialize OpenAI client
    client = openai.OpenAI(api_key="your-api-key")

    # Create metadata if not provided
    metadata = request.metadata or {}
    metadata["timestamp"] = metadata.get("timestamp", time.time())
    metadata["model"] = metadata.get("model", request.model)
    metadata["key_id"] = metadata.get("key_id", "fastapi-stream-key") # Use a stream-specific key ID

    # Initialize the streaming handler
    handler = StreamingHandler(
        metadata=metadata,
        private_key=stream_private_key # Use the stream private key
    )

    # Initialize OpenAI client
    client = openai.OpenAI(api_key="your-api-key")

    async def generate():
        try:
            # Create a streaming completion
            completion = client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": request.prompt}
                ],
                stream=True
            )

            # Process each chunk
            for chunk in completion:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content

                    # Process the chunk
                    processed_chunk = handler.process_chunk(chunk=content)

                    # Yield the processed chunk
                    yield processed_chunk

            # Finalize the stream
            final_chunk = handler.finalize()
            if final_chunk:
                yield final_chunk

        except Exception as e:
            # Handle errors
            yield f"Error: {str(e)}"

    # Return a streaming response
    return StreamingResponse(generate(), media_type="text/plain")
```

### WebSocket Support

For real-time communication with WebSockets:

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Dict, Any, List, Optional
from encypher.streaming import StreamingHandler
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair # Key management
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
import time
import json
import openai  # Or any other LLM provider

app = FastAPI()

# --- Key Management (Same as above or separate for streaming) ---
stream_private_key, stream_public_key = generate_key_pair()
public_keys_store["fastapi-stream-key"] = stream_public_key # Add to store
# ---------------------------------------------------------------

# HTML for a simple WebSocket client
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>EncypherAI WebSocket Demo</title>
        <script>
            var ws = null;

            function connect() {
                ws = new WebSocket("ws://localhost:8000/ws");
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages');
                    var message = document.createElement('li');
                    message.textContent = event.data;
                    messages.appendChild(message);
                };
                ws.onclose = function(event) {
                    document.getElementById('status').textContent = 'Disconnected';
                };
                ws.onopen = function(event) {
                    document.getElementById('status').textContent = 'Connected';
                };
            }

            function sendMessage() {
                var input = document.getElementById('messageText');
                var message = input.value;
                ws.send(message);
                input.value = '';
            }

            function verifyMetadata() {
                var text = document.getElementById('messages').innerText;
                fetch('/verify', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({text: text})
                })
                .then(response => response.json())
                .then(data => {
                    var verification = document.getElementById('verification');
                    if (data.has_metadata) {
                        verification.innerHTML = '<h3>Metadata Found</h3>' +
                            '<p>Verified: ' + (data.verified ? '✅' : '❌') + '</p>' +
                            '<pre>' + JSON.stringify(data.metadata, null, 2) + '</pre>';
                    } else {
                        verification.innerHTML = '<h3>No Metadata Found</h3>' +
                            '<p>Error: ' + data.error + '</p>';
                    }
                });
            }

            window.onload = function() {
                connect();
            };
        </script>
    </head>
    <body>
        <h1>EncypherAI WebSocket Demo</h1>
        <p>Status: <span id="status">Connecting...</span></p>
        <input type="text" id="messageText" placeholder="Enter your message here">
        <button onclick="sendMessage()">Send</button>
        <button onclick="verifyMetadata()">Verify Metadata</button>
        <h2>Messages:</h2>
        <ul id="messages"></ul>
        <div id="verification"></div>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Create metadata
    metadata = {
        "model": "gpt-4",
        "organization": "YourOrganization",
        "timestamp": time.time(),
        "prompt": ""
    }

    # Initialize streaming handler
    handler = StreamingHandler(
        metadata=metadata,
        private_key=stream_private_key # Use the stream private key
    )

    try:
        while True:
            # Receive message from client
            prompt = await websocket.receive_text()

            # Update metadata with the prompt
            metadata["prompt"] = prompt

            # Initialize OpenAI client
            client = openai.OpenAI(api_key="your-api-key")

            # Create a streaming completion
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )

            # Process and send each chunk
            for chunk in completion:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content

                    # Process the chunk
                    processed_chunk = handler.process_chunk(chunk=content)

                    # Send the processed chunk
                    await websocket.send_text(processed_chunk)

            # Finalize the stream
            final_chunk = handler.finalize()
            if final_chunk:
                await websocket.send_text(final_chunk)

    except WebSocketDisconnect:
        print("Client disconnected")
```

### Middleware for Automatic Metadata Embedding

You can create a middleware to automatically embed metadata in all responses:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair # Assuming key management is accessible
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
import time

# Initialize FastAPI app
app = FastAPI()

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
    private_key, _ = generate_key_pair() # Fallback for demo

# Load public keys for resolver (e.g., from DB or config file)
# public_keys_store = load_public_keys_from_db(DB_URL)
# For demo, we used an in-memory dict initialized earlier
# ----------------------------

class MetadataMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Process the request normally
        response = await call_next(request)

        # Check if this is a JSON response
        if response.headers.get("content-type") == "application/json":
            # Get the response body
            body = await response.body()
            content = json.loads(body)

            # Assuming the response has a 'text' field to embed metadata into
            if isinstance(content, dict) and 'text' in content:
                text_to_encode = content['text']

                # Prepare metadata
                metadata_to_embed = {
                    "processed_by": "middleware",
                    "timestamp": time.time(),
                    "key_id": "middleware-key-1"
                }

                # Embed metadata using UnicodeMetadata
                encoded_text = UnicodeMetadata.embed_metadata(
                    text=text_to_encode,
                    metadata=metadata_to_embed,
                    private_key=private_key
                )

                # Update the response content
                content['text'] = encoded_text

                # Return the modified response
                return JSONResponse(
                    content=content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )

        return response

# Add middleware to the app
app.add_middleware(MetadataMiddleware)
```

## Integration with LLM Providers

### OpenAI Integration

Combining FastAPI, EncypherAI, and OpenAI:

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, AsyncGenerator
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.streaming import StreamingHandler
from encypher.core.keys import generate_key_pair # Key management
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
import time
import openai

app = FastAPI()

# --- Key Management (Load appropriate keys) ---
private_key = get_private_key_for_user("your-user-id") # Example function
key_id = f"user-your-user-id-key"
# ----------------------------------------------

# Define request model
class GenerateRequest(BaseModel):
    prompt: str
    model: str = "gpt-4"
    system_prompt: Optional[str] = "You are a helpful assistant."
    stream: bool = False
    additional_metadata: Optional[Dict[str, Any]] = None

@app.post("/generate")
async def generate(request: GenerateRequest):
    # Initialize OpenAI client
    client = openai.OpenAI(api_key="your-api-key")

    # Create metadata
    metadata = {
        "model": request.model,
        "timestamp": time.time(),
        "key_id": key_id,
        "user_id": "your-user-id"
    }

    # Add additional metadata if provided
    if request.additional_metadata:
        metadata.update(request.additional_metadata)

    # Handle streaming requests
    if request.stream:
        return StreamingResponse(
            generate_stream(client, request, metadata, private_key),
            media_type="text/plain"
        )

    # Create a completion
    response = client.chat.completions.create(
        model=request.model,
        messages=[
            {"role": "system", "content": request.system_prompt},
            {"role": "user", "content": request.prompt}
        ]
    )

    # Get the response text
    text = response.choices[0].message.content

    # Update metadata with usage information
    if hasattr(response, "usage"):
        metadata.update({
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        })

    # Embed metadata
    encoded_text = UnicodeMetadata.embed_metadata(
        text=text,
        metadata=metadata,
        private_key=private_key
    )

    # Return the response
    return {
        "text": encoded_text,
        "metadata": metadata
    }

async def generate_stream(client, request: GenerateRequest, metadata: Dict[str, Any], private_key: PrivateKeyTypes) -> AsyncGenerator[str, None]:
    # Initialize the streaming handler
    handler = StreamingHandler(
        metadata=metadata,
        private_key=private_key
    )

    # Create a streaming completion
    completion = client.chat.completions.create(
        model=request.model,
        messages=[
            {"role": "system", "content": request.system_prompt},
            {"role": "user", "content": request.prompt}
        ],
        stream=True
    )

    # Process each chunk
    for chunk in completion:
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content

            # Process the chunk
            processed_chunk = handler.process_chunk(chunk=content)

            # Yield the processed chunk
            yield processed_chunk

    # Finalize the stream
    final_chunk = handler.finalize()
    if final_chunk:
        yield final_chunk
```

### Anthropic Integration

Combining FastAPI, EncypherAI, and Anthropic:

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, AsyncGenerator
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.streaming import StreamingHandler
from encypher.core.keys import generate_key_pair # Key management
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
import time
import anthropic

app = FastAPI()

# --- Key Management (Load appropriate keys) ---
private_key = get_private_key_for_user("your-user-id") # Example function
key_id = f"user-your-user-id-key"
# ----------------------------------------------

# Define request model
class GenerateRequest(BaseModel):
    prompt: str
    model: str = "claude-3-opus-20240229"
    stream: bool = False
    additional_metadata: Optional[Dict[str, Any]] = None

@app.post("/generate")
async def generate(request: GenerateRequest):
    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key="your-api-key")

    # Create metadata
    metadata = {
        "model": request.model,
        "timestamp": time.time(),
        "key_id": key_id,
        "user_id": "your-user-id"
    }

    # Add additional metadata if provided
    if request.additional_metadata:
        metadata.update(request.additional_metadata)

    # Handle streaming requests
    if request.stream:
        return StreamingResponse(
            generate_stream(client, request, metadata, private_key),
            media_type="text/plain"
        )

    # Create a message
    response = client.messages.create(
        model=request.model,
        max_tokens=1000,
        messages=[
            {"role": "user", "content": request.prompt}
        ]
    )

    # Get the response text
    text = response.content[0].text

    # Update metadata with usage information
    if hasattr(response, "usage"):
        metadata.update({
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        })

    # Embed metadata
    encoded_text = UnicodeMetadata.embed_metadata(
        text=text,
        metadata=metadata,
        private_key=private_key
    )

    # Return the response
    return {
        "text": encoded_text,
        "metadata": metadata
    }

async def generate_stream(client, request: GenerateRequest, metadata: Dict[str, Any], private_key: PrivateKeyTypes) -> AsyncGenerator[str, None]:
    # Initialize the streaming handler
    handler = StreamingHandler(
        metadata=metadata,
        private_key=private_key
    )

    # Create a streaming message
    with client.messages.stream(
        model=request.model,
        max_tokens=1000,
        messages=[
            {"role": "user", "content": request.prompt}
        ]
    ) as stream:
        # Process each chunk
        for text_delta in stream.text_deltas:
            # Process the chunk
            processed_chunk = handler.process_chunk(chunk=text_delta)

            # Yield the processed chunk
            yield processed_chunk

    # Finalize the stream
    final_chunk = handler.finalize()
    if final_chunk:
        yield final_chunk
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

Here's a sample Dockerfile for deploying a FastAPI application with EncypherAI:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
    private_key, _ = generate_key_pair() # Fallback for demo

# Load public keys for resolver (e.g., from DB or config file)
# public_keys_store = load_public_keys_from_db(DB_URL)
# For demo, we used an in-memory dict initialized earlier
# ----------------------------
```

## Best Practices

1. **Secure Key Management**: Store your EncypherAI private key securely using environment variables or a secure key management system.

2. **Input Validation**: Use Pydantic models to validate input data and provide clear error messages.

3. **Error Handling**: Implement proper error handling for both FastAPI and EncypherAI operations.

4. **Rate Limiting**: Implement rate limiting to prevent abuse of your API.

5. **Authentication**: Implement API key authentication or OAuth2 for secure access to your API.

6. **CORS Configuration**: Configure CORS properly to allow only trusted domains to access your API.

7. **Logging**: Implement structured logging to track API usage and errors.

8. **Documentation**: Use FastAPI's automatic documentation generation to provide clear API documentation.

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure `allow_origins` in `CORSMiddleware` is correctly configured for your frontend URL in production.

2. **Key Management**: Securely store private keys. Never commit them to version control. Implement a robust `public_key_resolver` that fetches keys from a secure store (like a database or vault) based on `key_id`.

3. **Verification Failures**:
   - Check if the text content was modified *after* metadata embedding.
   - Ensure the `public_key_resolver` correctly retrieves the public key corresponding to the `key_id` used during signing.
   - Verify that the `private_key` used for signing matches the `public_key` returned by the resolver for the given `key_id`.

4. **Streaming Issues**: Ensure the `finalize()` method of `StreamingHandler` is called after the loop to process any buffered content. Check for errors in the async generator logic.

5. **Dependencies**: Make sure `cryptography` is installed (`uv pip install cryptography`).

## Related Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [EncypherAI Streaming Support](../user-guide/streaming.md)
- [Metadata Encoding Guide](../user-guide/metadata-encoding.md)
- [Extraction and Verification](../user-guide/extraction-verification.md)
