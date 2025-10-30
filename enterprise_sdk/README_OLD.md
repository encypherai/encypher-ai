# Encypher Enterprise SDK

> Python SDK for the Encypher Enterprise API - C2PA content signing with streaming support

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-proprietary-red.svg)](../LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

The Encypher Enterprise SDK provides a simple Python interface to the Encypher Enterprise API, enabling:

- **C2PA content signing** - Sign text with industry-standard C2PA manifests
- **Streaming support** - Real-time signing for LLM chat completions
- **Async operations** - Full async/await support for high-performance applications
- **Framework integrations** - Ready-made adapters for LangChain, OpenAI, and LiteLLM
- **CLI tooling** - Command-line interface for quick testing and automation

## Installation

```bash
# Basic installation
pip install encypher-enterprise

# With framework integrations
pip install encypher-enterprise[all]  # LangChain + OpenAI + LiteLLM

# Just LangChain
pip install encypher-enterprise[langchain]

# Just OpenAI
pip install encypher-enterprise[openai]
```

## Quick Start

### Basic Signing

```python
from encypher_enterprise import EncypherClient

client = EncypherClient(api_key="encypher_your_api_key")

result = client.sign(
    text="Breaking news: Scientists discover new exoplanet.",
    title="New Exoplanet Discovered",
)

print(f"Signed! Document ID: {result.document_id}")
print(f"Verification URL: {result.verification_url}")
print(f"Signed text: {result.signed_text}")
```

### Verification

```python
verification = client.verify(result.signed_text)

if verification.is_valid:
    print(f"[OK] Valid signature from {verification.organization_name}")
    print(f"Signed at: {verification.signature_timestamp}")
else:
    print(f"[ERR] Invalid signature (tampered: {verification.tampered})")
```

### Sentence Lookup

```python
provenance = client.lookup("Breaking news: Scientists discover new exoplanet.")

if provenance.found:
    print(f"Found in: {provenance.document_title}")
    print(f"Published by: {provenance.organization_name}")
    print(f"Date: {provenance.publication_date}")
```

## Framework Integrations

Install optional extras to plug signing into your favorite orchestration stack:

```bash
pip install encypher-enterprise[all]           # Everything
pip install encypher-enterprise[langchain]     # LangChain helpers
pip install encypher-enterprise[openai]        # OpenAI client wrappers
pip install encypher-enterprise[litellm]       # LiteLLM integration
```

### LangChain

```python
from encypher_enterprise import EncypherClient
from encypher_enterprise.integrations.langchain import apply_signing
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a provenance assistant."),
    ("human", "{question}"),
])
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
chain = prompt | llm

with EncypherClient(api_key="encypher_live_xxx") as client:
    signed_chain = apply_signing(chain, client, document_title="LangChain Demo")
    result = signed_chain.invoke({"question": "Why use C2PA?"})
    print(result["signed_text"])
```

### OpenAI

```python
from encypher_enterprise import EncypherClient
from encypher_enterprise.integrations.openai import chat_completion_with_signing

with EncypherClient(api_key="encypher_live_xxx") as client:
    signed = chat_completion_with_signing(
        client,
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You track provenance."},
            {"role": "user", "content": "Summarize C2PA."},
        ],
        document_title="OpenAI Demo",
    )
    print(signed.signed_text)
```

### LiteLLM

```python
from encypher_enterprise import EncypherClient
from encypher_enterprise.integrations.litellm import completion_with_signing

with EncypherClient(api_key="encypher_live_xxx") as client:
    signed = completion_with_signing(
        client,
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You track provenance."},
            {"role": "user", "content": "Give me two reasons to sign content."},
        ],
        document_title="LiteLLM Demo",
    )
    print(signed.signed_text)
```

See `examples/` for runnable scripts covering each adapter, including streaming usage.

## Command-Line Interface

The SDK ships with a `encypher` CLI that mirrors the Enterprise API onboarding flow. The tool reads `ENCYPHER_API_KEY` from your environment and loads a local `.env` file when present.

```bash
pip install encypher-enterprise
export ENCYPHER_API_KEY=encypher_live_xxx
encypher sign --text "Hello world" --title "CLI Demo"
encypher verify --file signed.txt
encypher lookup "Hello world"
encypher stats
```

## Streaming Support

Perfect for real-time LLM chat completions:

### Basic Streaming

```python
from encypher_enterprise import EncypherClient, StreamingSigner

client = EncypherClient(api_key="encypher_...")
signer = StreamingSigner(client)

# Wrap your streaming LLM
for chunk in openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Tell me about AI"}],
    stream=True
):
    content = chunk.choices[0].delta.content
    if content:
        signed_chunk = signer.process_chunk(content)
        if signed_chunk:
            print(signed_chunk, end='', flush=True)

# Finalize at the end
final_signed_text = signer.finalize()
```

### Stream Wrapper

```python
from encypher_enterprise import sign_stream

# Create content stream
content_stream = (
    chunk.choices[0].delta.content
    for chunk in openai_stream
    if chunk.choices[0].delta.content
)

# Wrap with signing
for signed_chunk in sign_stream(client, content_stream):
    print(signed_chunk, end='', flush=True)
```

### Async Streaming

```python
from encypher_enterprise import AsyncEncypherClient, async_sign_stream

async def stream_and_sign():
    async with AsyncEncypherClient(api_key="...") as client:
        # Your async LLM stream
        async_stream = get_async_llm_stream()

        # Sign as it streams
        async for signed_chunk in async_sign_stream(client, async_stream):
            print(signed_chunk, end='', flush=True)

# Run
import asyncio
asyncio.run(stream_and_sign())
```

## Framework Integrations

### OpenAI SDK Integration

```python
from encypher_enterprise.integrations.openai import EncypherOpenAI

# Drop-in replacement for OpenAI client
client = EncypherOpenAI(
    openai_api_key="sk-...",
    encypher_api_key="encypher_..."
)

# Normal OpenAI usage - automatically signed!
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# Response content is signed with C2PA
print(response.choices[0].message.content)

# Streaming also works
for chunk in client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    stream=True
):
    print(chunk.choices[0].delta.content, end='')
```

### LangChain Integration

```python
from langchain.chat_models import ChatOpenAI
from encypher_enterprise import EncypherClient
from encypher_enterprise.integrations.langchain import EncypherCallbackHandler

# Create callback handler
client = EncypherClient(api_key="...")
handler = EncypherCallbackHandler(client)

# Use with LangChain
llm = ChatOpenAI(callbacks=[handler])
response = llm.invoke("Tell me about AI")

# Response is automatically signed
signed_response = handler.get_signed_response()
print(signed_response)
```

## CLI Tool

The SDK includes a command-line tool for quick operations:

```bash
# Set API key
export ENCYPHER_API_KEY="encypher_your_key"

# Sign content
encypher sign "Content to sign" --title "My Document"

# Verify content
encypher verify "Signed content..."

# Look up sentence
encypher lookup "Some sentence to find"

# Sign a file
encypher sign-file article.txt --output signed_article.txt

# Get usage statistics
encypher stats
```

## Async Client

Full async/await support for high-performance applications:

```python
from encypher_enterprise import AsyncEncypherClient

async def main():
    async with AsyncEncypherClient(api_key="...") as client:
        # Async signing
        result = await client.sign("Content to sign")

        # Async verification
        verification = await client.verify(result.signed_text)

        # Async lookup
        provenance = await client.lookup("Some sentence")

        # Async stats
        stats = await client.get_stats()

import asyncio
asyncio.run(main())
```

## Configuration

### Environment Variables

```bash
# API key
export ENCYPHER_API_KEY="encypher_your_key"

# Base URL (optional, defaults to production)
export ENCYPHER_BASE_URL="https://api.encypherai.com"

# Timeout (optional, default 30s)
export ENCYPHER_TIMEOUT=30

# Max retries (optional, default 3)
export ENCYPHER_MAX_RETRIES=3
```

### Programmatic Configuration

```python
from encypher_enterprise import EncypherClient

client = EncypherClient(
    api_key="encypher_...",
    base_url="https://api.encypherai.com",
    timeout=30.0,
    max_retries=3
)
```

## Error Handling

```python
from encypher_enterprise import (
    EncypherClient,
    AuthenticationError,
    QuotaExceededError,
    SigningError,
    VerificationError,
    APIError
)

client = EncypherClient(api_key="...")

try:
    result = client.sign("Content")
except AuthenticationError:
    print("Invalid API key")
except QuotaExceededError:
    print("Monthly quota exceeded - upgrade your plan")
except SigningError as e:
    print(f"Signing failed: {e}")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## API Reference

### EncypherClient

```python
class EncypherClient:
    def __init__(self, api_key: str, base_url: str = "...", ...): ...

    def sign(
        self,
        text: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
        document_type: str = "article"
    ) -> SignResponse: ...

    def verify(self, text: str) -> VerifyResponse: ...

    def lookup(self, sentence: str) -> LookupResponse: ...

    def get_stats(self) -> StatsResponse: ...
```

### StreamingSigner

```python
class StreamingSigner:
    def __init__(
        self,
        client: EncypherClient,
        buffer_size: int = 1000,
        sign_on_sentence: bool = True
    ): ...

    def process_chunk(self, chunk: str) -> str: ...

    def finalize(self) -> str: ...
```

## Response Models

### SignResponse

```python
class SignResponse:
    success: bool
    document_id: str
    signed_text: str  # Text with embedded C2PA manifest
    total_sentences: int
    verification_url: str
```

### VerifyResponse

```python
class VerifyResponse:
    success: bool
    is_valid: bool
    signer_id: str
    organization_name: str
    signature_timestamp: Optional[datetime]
    manifest: Dict[str, Any]  # Full C2PA manifest
    tampered: bool
```

### LookupResponse

```python
class LookupResponse:
    success: bool
    found: bool
    document_title: Optional[str]
    organization_name: Optional[str]
    publication_date: Optional[datetime]
    sentence_index: Optional[int]
    document_url: Optional[str]
```

## Repository Signing (New!)

Sign entire repositories with C2PA-compliant metadata:

```python
from encypher_enterprise import EncypherClient, RepositorySigner, FileMetadata
from pathlib import Path

client = EncypherClient(api_key="encypher_...")
signer = RepositorySigner(client, use_sentence_tracking=True)

# Define metadata for files
def get_metadata(file_path: Path) -> FileMetadata:
    return FileMetadata(
        author="Jane Doe",
        publisher="Acme News",
        license="CC-BY-4.0",
        category="journalism"
    )

# Sign all markdown files in repository
result = signer.sign_directory(
    directory=Path("./articles"),
    patterns=["*.md", "*.txt"],
    metadata_fn=get_metadata,
    save_manifest=True  # Save C2PA manifests
)

print(result.summary())
# Output:
# Batch Signing Complete
#   Total: 42
#   Success: 42
#   Failed: 0
#   Time: 23.45s
```

### CLI Repository Signing

```bash
# Sign all files in a directory
encypher sign-repo ./articles \
  --author "Jane Doe" \
  --publisher "Acme News" \
  --license "CC-BY-4.0" \
  --pattern "*.md" \
  --pattern "*.txt" \
  --save-manifest \
  --report signing-report.json

# Output:
# Signing repository: ./articles
# Patterns: *.md, *.txt
# 
# Batch Signing Complete
#   Total: 42
#   Success: 42
#   Failed: 0
#   Time: 23.45s
```

## Enterprise Features (Merkle Trees)

For Enterprise tier customers with sentence-level tracking:

### Encode Document for Attribution

```python
# Encode document into Merkle trees
result = client.encode_document_merkle(
    text="Your document content...",
    document_id="doc_123",
    segmentation_levels=["sentence", "paragraph"]
)

print(f"Sentence root: {result['roots'][0]['root_hash']}")
print(f"Paragraph root: {result['roots'][1]['root_hash']}")
```

### Find Sources (Attribution)

```python
# Find source documents for text
result = client.find_sources(
    text="Some text to check for sources",
    min_similarity=0.85,
    max_results=10
)

for match in result['matches']:
    print(f"Found in: {match['document_id']}")
    print(f"Similarity: {match['similarity']:.2%}")
    print(f"Matched: {match['matched_text']}")
```

### Detect Plagiarism

```python
# Check document for plagiarism
result = client.detect_plagiarism(
    text="Document to check...",
    document_id="doc_456",
    threshold=0.85
)

if result['is_plagiarized']:
    print(f"Plagiarism detected: {result['plagiarism_percentage']:.1%}")
    for match in result['matches']:
        print(f"  - {match['source_document']}: {match['similarity']:.2%}")
```

### CLI Enterprise Commands

```bash
# Encode document
encypher merkle-encode --file article.txt --document-id doc_123

# Find sources
encypher find-sources --text "Text to check" --min-similarity 0.85

# Detect plagiarism (coming soon)
```

## Examples

See the `examples/` directory for runnable scripts:

- `basic_signing.py` - Basic signing and verification
- `repository_signing.py` - **NEW!** Sign entire repositories with C2PA metadata
- `streaming_chat.py` - Real-time LLM streaming
- `async_example.py` - Async operations
- `langchain_integration.py` - LangChain pipeline adapter
- `openai_integration.py` - OpenAI helper usage
- `litellm_integration.py` - LiteLLM helper usage

## Development

### Setup

```bash
# Clone repository
cd enterprise_sdk

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=encypher_enterprise --cov-report=html

# Format code
black encypher_enterprise/ tests/

# Lint
ruff check encypher_enterprise/ tests/

# Type checking
mypy encypher_enterprise/
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_client.py

# With coverage
pytest --cov=encypher_enterprise tests/

# Async tests
pytest tests/test_async_client.py
```

## Troubleshooting

### "Invalid API key"

Make sure your API key is set correctly:
```python
client = EncypherClient(api_key="encypher_your_key_here")
```

### "Monthly quota exceeded"

Upgrade your plan at https://dashboard.encypherai.com or contact sales@encypherai.com

### Streaming not working

Ensure you call `finalize()` at the end:
```python
signer = StreamingSigner(client)
# ... process chunks ...
final_text = signer.finalize()  # Important!
```

## Support

- **Documentation**: https://docs.encypherai.com/sdk
- **API Reference**: https://docs.encypherai.com/api
- **Email**: sdk@encypherai.com
- **Issues**: GitHub Issues (for enterprise customers)

## License

Proprietary - EncypherAI Commercial License

Copyright (c) 2025 EncypherAI. All rights reserved.

---

**Built with care by the EncypherAI team**
