<p align="center">
  <img src="docs/assets/horizontal-logo.png" alt="EncypherAI Logo" width="600">
</p>

# EncypherAI Core

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-docs.encypherai.com-blue)](https://docs.encypherai.com)

A Python package for embedding and extracting metadata in text using Unicode variation selectors without affecting readability.

## Overview

EncypherAI Core provides tools for invisibly encoding metadata (such as model information, timestamps, and custom data) into text generated by AI models. This enables:

- **Provenance tracking**: Identify which AI model generated a piece of text
- **Timestamp verification**: Know when text was generated
- **Custom metadata**: Embed any additional information you need
- **Tamper detection using digital signatures**: Verify text integrity using digital signatures
- **Streaming support**: Works with both streaming and non-streaming LLM outputs
- **LLM integrations**: Ready-to-use integrations with OpenAI, Google Gemini, Anthropic Claude, and more

The encoding is done using Unicode variation selectors, which are designed to specify alternative forms of characters without affecting text appearance or readability.

## Relationship with C2PA

EncypherAI's manifest format is inspired by the [Coalition for Content Provenance and Authenticity (C2PA)](https://c2pa.org/) standard, adapted specifically for plain-text environments. While C2PA focuses on embedding provenance information in rich media file formats, EncypherAI extends these concepts to text-only content where traditional file embedding methods aren't applicable.

Key alignments include:
- Structured provenance manifests with claim generators and actions
- Cryptographic integrity through digital signatures
- Shared mission of improving content transparency and trust

Learn more about [EncypherAI's relationship with C2PA](https://docs.encypherai.com/package/user-guide/c2pa-relationship/) in our documentation.

## LLM Integrations

EncypherAI seamlessly integrates with popular LLM providers:

- **OpenAI**: GPT-3.5, GPT-4o, and other OpenAI models
- **Google Gemini**: Gemini 2.0 Flash, Pro, and other Gemini models
- **Anthropic Claude**: Claude 3 Opus, Sonnet, Haiku, and other Claude models
- **LiteLLM**: For unified access to multiple LLM providers

Check our [documentation](https://github.com/encypherai/encypher-ai/tree/main/docs/package/integration) for detailed integration examples and code snippets for each provider.

## Demo Video

[![EncypherAI Demo Video](https://img.youtube.com/vi/_MNP0nHc77k/0.jpg)](https://www.youtube.com/watch?v=_MNP0nHc77k)

Watch our demo video to see EncypherAI in action, demonstrating how to embed and verify metadata in AI-generated content.

## Interactive Colab Notebook

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1fJBEGwUQSTomaBzwOwuYqAOftoGeoFDC?usp=sharing)

Try EncypherAI directly in your browser with our interactive Google Colab notebook. The notebook demonstrates all the core features including metadata embedding, extraction, digital signature verification, and tampering detection.

### Local Jupyter Notebook Example

For a local demonstration, check out the detailed Jupyter Notebook example included in the repository:
[`examples/encypher_v2_demo.ipynb`](./encypher/examples/encypher_v2_demo.ipynb)

This notebook covers key generation, basic and manifest format usage, and tamper detection using the latest version (v2.0.0+).

## Installation

First, install the uv package manager if you don't have it already:

```bash
# Install uv (recommended)
pip install uv

# Then install EncypherAI
uv pip install encypher-ai
```

## Quick Start

> **Note:** Digital signatures require managing a private/public key pair. You can use the helper script `encypher/examples/generate_keys.py` to create your first key pair and get setup instructions.

### Basic Encoding and Verification

```python
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from typing import Optional
import time

# --- Key Management (Replace with your actual key management) ---
# Generate a new key pair
private_key, public_key = generate_key_pair()
key_id_1 = "readme-key-1"

# Store public keys (e.g., in a database or secure store)
public_keys_store: Dict[str, PublicKeyTypes] = { key_id_1: public_key }

# Create a resolver function to look up public keys by ID
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    return public_keys_store.get(key_id)
# -----------------------------------------------------------------

# Metadata must include a 'key_id' matching a stored public key
metadata_to_embed = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),  # Current Unix timestamp
    "key_id": key_id_1, # Identifier for the key pair
    "version": "2.0.0"
}
encoded_text = UnicodeMetadata.embed_metadata(
    text="This is a sample text generated by an AI model.",
    metadata=metadata_to_embed,
    private_key=private_key, # Use the private key for signing
    target="whitespace",  # Embed in whitespace characters
)

# Extract metadata (without verification)
extracted_unverified = UnicodeMetadata.extract_metadata(encoded_text)
print(f"Extracted (unverified): {extracted_unverified}")

# Verify the embedded metadata using the public key resolver
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)
print(f"Metadata verified: {is_valid}")
if is_valid:
    print(f"Verified metadata: {verified_metadata}")
```

### Streaming Support

```python
from encypher.streaming.handlers import StreamingHandler
import time

# Initialize streaming handler
# Metadata must include a 'key_id'
stream_metadata = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),
    "key_id": key_id_1, # Use the same key_id as before for verification
    "custom_field": "streaming value",
    "version": "2.0.0"
}
handler = StreamingHandler(
    metadata=stream_metadata,
    private_key=private_key, # Provide the private key
    target="whitespace",
    encode_first_chunk_only=True  # Only encode the first non-empty chunk
)

chunks = [
    "This is ",
    "a sample ",
    "text generated ",
    "by an AI model."
]

full_response = ""
for chunk in chunks:
    processed_chunk = handler.process_chunk(chunk=chunk)
    if processed_chunk:
        print(processed_chunk, end="") # Use in your streaming response
        full_response += processed_chunk

# !!! IMPORTANT: Finalize the stream to process any remaining buffer !!!
final_chunk = handler.finalize()
if final_chunk:
    print(final_chunk, end="")
    full_response += final_chunk

print("\n--- Stream Complete ---")

# Verify the full response
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=full_response,
    public_key_resolver=resolve_public_key # Use the same resolver
)

if is_valid:
    print(f"\nStreaming content verified: {verified_metadata}")
else:
    print("\nStreaming content verification failed.")
```

### Configuration

```python
from encypher.config.settings import Settings

# Load settings from environment variables and/or config file
settings = Settings(
    config_file="config.json",  # Optional
    env_prefix="ENCYPHER_"  # Environment variable prefix
)

# Get configuration values
metadata_target = settings.get_metadata_target()
encode_first_chunk_only = settings.get_encode_first_chunk_only()
# You might add settings for key file paths or key store connection strings
```

### Including Custom Metadata

```python
from encypher.core.unicode_metadata import UnicodeMetadata
import time

# Metadata must include 'key_id'
custom_metadata_to_embed = {
    "model_id": "gpt-4",
    "timestamp": int(time.time()),  # Current Unix timestamp
    "key_id": key_id_1,
    "user_id": "user123", # Custom fields
    "session_id": "abc456",
    "context": {
        "source": "knowledge_base",
        "reference_id": "doc789"
    },
    "version": "2.0.0"
}
# Include custom metadata along with required fields
encoded_text = UnicodeMetadata.embed_metadata(
    text="This is a sample text generated by an AI model.",
    metadata=custom_metadata_to_embed,
    private_key=private_key
)

# Verify and extract
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    encoded_text, public_key_resolver=resolve_public_key
)

if is_valid:
    print(f"Verified metadata: {verified_metadata}")
```

## Features

- **Invisible Embedding**: Metadata is embedded using Unicode variation selectors that don't affect text appearance
- **Flexible Targets**: Choose where to embed metadata (whitespace, punctuation, etc.)
- **Streaming Support**: Works with both streaming and non-streaming LLM outputs
- **Digital Signature Verification**: Optionally verify the integrity and authenticity of embedded metadata
- **Customizable**: Embed any JSON-serializable data
- **LLM Integration**: Ready-to-use integrations with popular LLM providers

## Metadata Target Options

You can specify where to embed metadata using the `target` parameter:

- `whitespace`: Embed in whitespace characters (default, least noticeable)
- `punctuation`: Embed in punctuation marks
- `first_letter`: Embed in the first letter of each word
- `last_letter`: Embed in the last letter of each word
- `all_characters`: Embed in all characters (not recommended)
- `none`: Don't embed metadata (for testing/debugging)

## Security Features

### Digital Signature Verification

EncypherAI uses digital signatures to ensure the security and integrity of embedded metadata:

- **Tamper Detection**: Cryptographically verifies that metadata hasn't been modified
- **Authentication**: Confirms metadata was created by an authorized source
- **Integrity Protection**: Ensures the relationship between content and metadata remains intact

```python
# Example of verifying metadata with digital signature
from encypher.core.unicode_metadata import UnicodeMetadata

# Assuming a public key resolver function is defined (e.g., from previous example)
public_key_resolver = resolve_public_key

encoded_text = "AI-generated text with embedded metadata..."

# Verify the embedded metadata using the public key resolver
is_valid, verified_metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=public_key_resolver
)

if is_valid:
    print(f"Verified metadata: {verified_metadata}")
else:
    print("Warning: Metadata has been tampered with!")
```

For production use, set your key management and public key resolver according to your organization's security policies.

## FastAPI Integration

See the `examples/fastapi_example.py` for a complete example of integrating EncypherAI with FastAPI, including:

- Encoding endpoint
- Decoding endpoint
- Streaming support

## CLI Usage

The package includes a comprehensive command-line interface:

```bash
# Encode metadata into text
python -m encypher.examples.cli_example encode --text "This is a test" --model-id "gpt-4" --target "whitespace"

# Encode with custom metadata
python -m encypher.examples.cli_example encode --input-file input.txt --output-file output.txt --model-id "gpt-4" --custom-metadata '{"source": "test", "user_id": 123}'

# Decode metadata from text
python -m encypher.examples.cli_example decode --input-file encoded.txt --show-clean

# Decode with debug information
python -m encypher.examples.cli_example decode --text "Your encoded text here" --debug
```

## Development and Contributing

We welcome contributions to EncypherAI! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Code Style

EncypherAI follows PEP 8 style guidelines with Black as our code formatter. All code must pass Black formatting checks before being merged. We use pre-commit hooks to automate code formatting and quality checks.

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/encypherai/encypher-ai.git
cd encypher-ai

# Install development dependencies
uv pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install
```

The pre-commit hooks will automatically:
- Format your code with Black (including Jupyter notebooks)
- Sort imports with isort
- Check for common issues with flake8 and ruff
- Perform type checking with mypy

You can also run the formatting tools manually:

```bash
# Format all Python files
black encypher

# Format Python files including Jupyter notebooks
black --jupyter encypher
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=encypher
```

## License

EncypherAI is provided under a dual licensing model:

### Open Source License (AGPL-3.0)

The core EncypherAI package is released under the [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.en.html). This license allows you to use, modify, and distribute the software freely, provided that:

- You disclose the source code when you distribute the software
- Any modifications you make are also licensed under AGPL-3.0
- If you run a modified version of the software as a service (e.g., over a network), you must make the complete source code available to users of that service

### Commercial License

For organizations that wish to incorporate EncypherAI into proprietary applications without the source code disclosure requirements of AGPL-3.0, we offer a commercial licensing option.

Benefits of the commercial license include:

- **Proprietary Integration**: Use EncypherAI in closed-source applications without AGPL obligations
- **Legal Certainty**: Clear licensing terms for commercial use
- **Support & Indemnification**: Access to professional support and IP indemnification

For commercial licensing inquiries, please contact [enterprise@encypherai.com](mailto:enterprise@encypherai.com).

See the [LICENSE](LICENSE.md) file for details of the AGPL-3.0 license.

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the open-source community for their invaluable tools and libraries

## Contact

For questions, feedback, or support, please [open an issue](https://github.com/encypherai/encypher-ai/issues) on our GitHub repository.
