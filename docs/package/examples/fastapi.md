# FastAPI Example

This example demonstrates how to build a complete FastAPI application that integrates Encypher for metadata embedding and verification using digital signatures. The application provides endpoints for encoding, decoding, and verifying metadata in text.

## Prerequisites

Before you begin, make sure you have:

1. FastAPI and its dependencies installed
2. Encypher installed
3. (Optional) An LLM provider API key if you're integrating with an LLM

```bash
uv add encypher-ai fastapi uvicorn python-multipart
```

## Complete FastAPI Application

Create a file named `app.py` with the following code:

```python
from fastapi import FastAPI, HTTPException, Request, Depends, Form
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List, Callable, Literal
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata
from encypher.streaming.handlers import StreamingHandler
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
import time
import json
import os
import secrets

# --- Key Management --- START ---
# WARNING: DEMONSTRATION ONLY!
# The following key generation should NOT be done on every application startup in production.
# Generate a private key ONCE for your application instance and store it securely
# (e.g., in an environment variable loaded from a .env file, or a secrets manager).
# Load the persistent private key here instead of generating a new one.
# Failure to use a persistent key will prevent verification of data signed by previous instances.
#
# Example (.env file entry):
# ENCYPHER_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...your private key PEM data...\n-----END PRIVATE KEY-----"
#
# Example loading code (replace generation below):
# from cryptography.hazmat.primitives import serialization
# private_pem = os.getenv("ENCYPHER_PRIVATE_KEY")
# if not private_pem:
#     raise ValueError("ENCYPHER_PRIVATE_KEY environment variable not set!")
# private_key = serialization.load_pem_private_key(private_pem.encode(), password=None)

# You can use the provided helper script `encypher/examples/generate_keys.py`
# to generate your initial key pair and get usage instructions.

# Generate private key (DEMO ONLY - REPLACE WITH LOADING PERSISTENT KEY)
private_key: PrivateKeyTypes = ed25519.Ed25519PrivateKey.generate()
public_key: PublicKeyTypes = private_key.public_key()

# Example key ID (could be based on version, environment, etc.)
EXAMPLE_KEY_ID = "fastapi-example-key-v1"

# Simple public key store (replace with a proper key management system)
public_key_store: Dict[str, PublicKeyTypes] = {
    EXAMPLE_KEY_ID: public_key
}

def public_key_resolver(key_id: str) -> Optional[PublicKeyTypes]:
    """Simple resolver to get public key by ID."""
    return public_key_store.get(key_id)

# Serialize keys for potential display/logging (DO NOT expose private key in production logs)
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# print(f"Generated Key ID: {EXAMPLE_KEY_ID}")
# print(f"Public Key (PEM):\n{public_pem.decode()}")
# --- Key Management --- END ---

# Initialize FastAPI app
app = FastAPI(
    title="Encypher Demo",
    description="API for embedding and extracting metadata in text using Digital Signatures",
    version="3.0.2"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request and response models
class EncodeRequest(BaseModel):
    text: str
    metadata: Dict[str, Any]
    target: Optional[str] = "whitespace"

class VerifyRequest(BaseModel):
    text: str

# Updated MetadataResponse
class MetadataResponse(BaseModel):
    payload: Optional[Dict[str, Any]] = None
    signer_id: Optional[str] = None
    verification_status: Literal["verified", "failed", "not_present"]
    error: Optional[str] = None

# Set up templates
templates = Jinja2Templates(directory="templates")

# Create templates directory and files
os.makedirs("templates", exist_ok=True)

# Create index.html template
with open("templates/index.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Encypher Demo</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .result-box {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 0.25rem;
            padding: 1rem;
            margin-top: 1rem;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
    </style>
</head>
<body>
    <div class="container my-5">
        <h1 class="mb-4">Encypher Demo</h1>

        <ul class="nav nav-tabs" id="myTab" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="encode-tab" data-bs-toggle="tab" data-bs-target="#encode" type="button" role="tab" aria-controls="encode" aria-selected="true">Encode</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="verify-tab" data-bs-toggle="tab" data-bs-target="#verify" type="button" role="tab" aria-controls="verify" aria-selected="false">Verify</button>
            </li>
        </ul>

        <div class="tab-content" id="myTabContent">
            <!-- Encode Tab -->
            <div class="tab-pane fade show active" id="encode" role="tabpanel" aria-labelledby="encode-tab">
                <div class="my-4">
                    <h3>Embed Metadata</h3>
                    <form id="encodeForm">
                        <div class="mb-3">
                            <label for="text" class="form-label">Text</label>
                            <textarea class="form-control" id="text" name="text" rows="5" required>This is a sample text that will have metadata embedded within it.</textarea>
                        </div>
                        <div class="mb-3">
                            <label for="metadata" class="form-label">Metadata (JSON)</label>
                            <textarea class="form-control" id="metadata" name="metadata" rows="5" required>{
    "model": "gpt-4",
    "organization": "Encypher",
    "timestamp": 1742713200,
    "version": "3.0.2"
}</textarea>
                        </div>
                        <div class="mb-3">
                            <label for="target" class="form-label">Target</label>
                            <select class="form-select" id="target" name="target">
                                <option value="whitespace">Whitespace</option>
                                <option value="punctuation">Punctuation</option>
                                <option value="first_letter">First Letter</option>
                                <option value="last_letter">Last Letter</option>
                                <option value="all_characters">All Characters</option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-primary">Encode</button>
                    </form>

                    <div id="encodeResult" class="result-box d-none">
                        <h4>Result</h4>
                        <div class="mb-3">
                            <h5>Original Text</h5>
                            <pre id="originalText"></pre>
                        </div>
                        <div class="mb-3">
                            <h5>Encoded Text</h5>
                            <pre id="encodedText"></pre>
                        </div>
                        <div class="mb-3">
                            <h5>Metadata</h5>
                            <pre id="encodedMetadata"></pre>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Verify Tab -->
            <div class="tab-pane fade" id="verify" role="tabpanel" aria-labelledby="verify-tab">
                <div class="my-4">
                    <h3>Extract and Verify Metadata</h3>
                    <form id="verifyForm">
                        <div class="mb-3">
                            <label for="verifyText" class="form-label">Text with Embedded Metadata</label>
                            <textarea class="form-control" id="verifyText" name="text" rows="5" required>Paste text with embedded metadata here...</textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Verify</button>
                    </form>

                    <div id="verifyResult" class="result-box d-none">
                        <h4>Result</h4>
                        <div id="verifyStatus"></div>
                        <div class="mb-3">
                            <h5>Extracted Metadata</h5>
                            <pre id="extractedMetadata"></pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('encodeForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const text = document.getElementById('text').value;
            const metadata = document.getElementById('metadata').value;
            const target = document.getElementById('target').value;

            try {
                const response = await fetch('/api/encode', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        text: text,
                        metadata: JSON.parse(metadata),
                        target: target
                    })
                });

                const data = await response.json();

                document.getElementById('originalText').textContent = text;
                document.getElementById('encodedText').textContent = data.encoded_text;
                document.getElementById('encodedMetadata').textContent = JSON.stringify(data.metadata, null, 2);
                document.getElementById('encodeResult').classList.remove('d-none');
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });

        document.getElementById('verifyForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const text = document.getElementById('verifyText').value;

            try {
                const response = await fetch('/api/verify', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        text: text
                    })
                });

                const data = await response.json();

                let statusHtml = '';
                if (data.verification_status === 'verified') {
                    statusHtml = '<div class="alert alert-success">✅ Metadata verified successfully! Signer ID: ' + (data.signer_id || 'N/A') + '</div>';
                } else if (data.verification_status === 'failed') {
                    statusHtml = '<div class="alert alert-warning">⚠️ Metadata found (Signer ID: ' + (data.signer_id || 'N/A') + ') but verification failed. The text may have been tampered with.</div>';
                } else {
                    statusHtml = '<div class="alert alert-danger">❌ No metadata found or extraction failed: ' + (data.error || 'Unknown error') + '</div>';
                }

                document.getElementById('verifyStatus').innerHTML = statusHtml;
                document.getElementById('extractedMetadata').textContent = data.payload ? JSON.stringify(data.payload, null, 2) : 'N/A';
                document.getElementById('verifyResult').classList.remove('d-none');
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    </script>
</body>
</html>
    """)

# API endpoints
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/encode", response_model=Dict[str, Any])
async def encode_text(request: EncodeRequest):
    """Encode metadata into text using digital signature."""
    try:
        # Ensure metadata includes the key_id for verification later
        metadata_to_embed = request.metadata.copy()
        # EXAMPLE_KEY_ID will be passed as signer_id directly
        # metadata_to_embed["key_id"] = EXAMPLE_KEY_ID

        # Validate target
        try:
            target_enum = MetadataTarget(request.target)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid target: {request.target}")

        encoded_text = UnicodeMetadata.embed_metadata(
            text=request.text,
            custom_metadata=metadata_to_embed,  # Changed from metadata
            private_key=private_key, # Use the globally generated private key
            signer_id=EXAMPLE_KEY_ID, # Added signer_id
            metadata_format="basic",
            timestamp=metadata_to_embed.get("timestamp"), # Added timestamp
            target=target_enum
        )
        return {
            "original_text": request.text,
            "encoded_text": encoded_text,
            "metadata": metadata_to_embed # This is the input metadata, not the extracted one
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encoding error: {str(e)}")

@app.post("/api/verify", response_model=MetadataResponse)
async def verify_text(request: VerifyRequest):
    """Verify text with embedded metadata using digital signature."""
    try:
        # Verify metadata using the provider
        is_valid, signer_id, payload_dict = UnicodeMetadata.verify_metadata(
            text=request.text,
            public_key_resolver=public_key_resolver, # Changed from public_key_resolver
            return_payload_on_failure=True,
        )

        if is_valid and payload_dict is not None:
            # Metadata found and signature verified
            return MetadataResponse(
                payload=payload_dict,
                signer_id=signer_id,
                verification_status="verified"
            )
        elif payload_dict is not None: # Metadata was extracted but signature is invalid
            return MetadataResponse(
                payload=payload_dict,
                signer_id=signer_id, # May still have signer_id from unverified payload
                verification_status="failed",
                error="Signature verification failed."
            )
        else: # No metadata could be extracted
            # Attempt to extract without verification to see if metadata exists but is malformed
            # This step might be redundant if verify_metadata already tries to return payload_on_failure
            # For simplicity, we'll assume verify_metadata handles this and payload_dict would be non-None if anything was found.
            extracted_raw_metadata = UnicodeMetadata.extract_metadata(request.text)
            if extracted_raw_metadata is not None:
                return MetadataResponse(
                    payload=extracted_raw_metadata, # This is unverified payload
                    verification_status="failed",
                    error="Metadata found but it is malformed or signature could not be processed."
                )
            else:
                # No metadata found at all
                return MetadataResponse(
                    verification_status="not_present",
                    error="No metadata found in text."
                )

    except Exception as e:
        # Include specific error details if possible
        return MetadataResponse(
            verification_status="failed",
            error=f"Verification process error: {str(e)}"
        )

@app.post("/api/generate")
async def generate_with_openai(
    prompt: str = Form(...),
    model: str = Form("gpt-4"),
    stream: bool = Form(False)
):
    """Generate text with OpenAI and embed metadata"""
    try:
        import openai

        # Check if API key is set
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return JSONResponse(
                status_code=400,
                content={"error": "OpenAI API key not set. Set the OPENAI_API_KEY environment variable."}
            )

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)

        # Create metadata
        metadata = {
            "model": model,
            "organization": "Encypher",
            "timestamp": int(time.time()),
            "prompt": prompt,
            "version": "3.0.2"
        }

        # Handle streaming
        if stream:
            return StreamingResponse(
                generate_stream(client, model, prompt, metadata),
                media_type="text/plain"
            )

        # Create a completion
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Get the response text
        text = response.choices[0].message.content

        # Update metadata with usage information
        metadata.update({
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        })

        # Embed metadata
        encoded_text = UnicodeMetadata.embed_metadata(
            text=text,
            custom_metadata=metadata, # Changed from metadata
            private_key=private_key, # Use the globally generated private key
            signer_id=EXAMPLE_KEY_ID, # Added signer_id
            timestamp=metadata.get("timestamp"), # Added timestamp
            target=MetadataTarget.WHITESPACE # Or get from request if needed
        )

        return {
            "text": encoded_text,
            "metadata": metadata,
            "original_text": text
        }
    except ImportError:
        return JSONResponse(
            status_code=400,
            content={"error": "OpenAI package not installed. Install it with 'uv add openai'."}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

async def generate_stream(client, model, prompt, metadata):
    """Generate a streaming response with OpenAI and embed metadata"""
    try:
        # Initialize the streaming handler
        handler = StreamingHandler(
            custom_metadata=metadata, # Changed from metadata
            private_key=private_key, # Use the globally generated private key
            signer_id=EXAMPLE_KEY_ID, # Added signer_id
            timestamp=metadata.get("timestamp"), # Added timestamp
            target=MetadataTarget.WHITESPACE, # Or get from request if needed
            metadata_format="basic",
        )

        # Create a streaming completion
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
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
        yield f"Error: {str(e)}"

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Running the Application

1. Save the code above to a file named `app.py`
2. Run the application:

```bash
uvicorn app:app --reload
```

3. Open your browser and navigate to `http://localhost:8000`

## Application Features

The application provides:

1. **Web Interface**:
   - A form for embedding metadata into text
   - A form for extracting and verifying metadata from text
   - Visual indicators for verification status

2. **API Endpoints**:
   - `/api/encode` - Embed metadata into text
   - `/api/verify` - Extract and verify metadata from text
   - `/api/generate` - (Optional) Generate text with OpenAI and embed metadata

## API Usage Examples

### Embedding Metadata

```python
import requests
import json
import time

# Endpoint
url = "http://localhost:8000/api/encode"

# Data
data = {
    "text": "This is a sample text that will have metadata embedded within it.",
    "metadata": {
        "model": "gpt-4",
        "organization": "Encypher",
        "timestamp": int(time.time()),
        "version": "3.0.2"
    },
    "target": "whitespace"
}

# Send request
response = requests.post(url, json=data)
result = response.json()

# Print result
print("Encoded text:")
print(result["encoded_text"])
print("\nMetadata:")
print(json.dumps(result["metadata"], indent=2))
```

### Verifying Metadata

```python
import requests
import json

# Endpoint
url = "http://localhost:8000/api/verify"

# Data
data = {
    "text": "Your text with embedded metadata here..."
}

# Send request
response = requests.post(url, json=data)
result = response.json()

# Print result
if result["verification_status"] == "verified":
    print("Verification result: ✅ Verified")
    print(f"Signer ID: {result.get('signer_id')}")
    print("\nExtracted metadata (payload):")
    print(json.dumps(result.get("payload"), indent=2))
elif result["verification_status"] == "failed":
    print("Verification result: ⚠️ Failed")
    print(f"Signer ID: {result.get('signer_id')}")
    print("\nExtracted metadata (payload):")
    print(json.dumps(result.get("payload"), indent=2))
    print("\nError:", result.get("error"))
else:
    print("No metadata found or extraction failed:", result.get("error"))
```

## Customization

### Adding Authentication

To add API key authentication:

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN

# Define API key header
API_KEY = os.getenv("API_KEY", "your-api-key")  # Use environment variable in production
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
@app.post("/api/encode", dependencies=[Depends(get_api_key)])
async def encode_text(request: EncodeRequest):
    # Your implementation here
    pass
```

### Adding Rate Limiting

To add rate limiting:

```python
from fastapi import Request
from fastapi.middleware.base import BaseHTTPMiddleware
import time

# Rate limiting middleware
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int = 60
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host

        # Get current time
        current_time = time.time()

        # Clean up old requests
        self.request_counts = {
            ip: [timestamp for timestamp in timestamps if current_time - timestamp < 60]
            for ip, timestamps in self.request_counts.items()
        }

        # Check rate limit
        if client_ip in self.request_counts and len(self.request_counts[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded. Try again later."}
            )

        # Add request timestamp
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        self.request_counts[client_ip].append(current_time)

        # Process request
        return await call_next(request)

# Add middleware to app
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60
)
