# Encypher Enterprise SDK

<div align="center">

![Encypher Logo](https://encypher.com/encypher_full_logo_color.svg)

**Enterprise-grade content signing and verification for publishers, news organizations, and content creators**

[![PyPI version](https://badge.fury.io/py/encypher-enterprise.svg)](https://badge.fury.io/py/encypher-enterprise)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-23%2F23%20passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen.svg)]()

[Features](#-features) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[Examples](#-examples) •
[CI/CD](#-cicd-integration) •
[Support](#-support)

</div>

---

## 🎯 Overview

The Encypher Enterprise SDK provides cryptographic content signing and verification using **C2PA standards**, enabling publishers to prove content authenticity, track provenance, and detect tampering at scale.

### Why Encypher?

- **🔒 Cryptographic Proof**: C2PA-compliant digital signatures
- **⚡ Lightning Fast**: 10x faster with incremental signing
- **🤖 CI/CD Ready**: GitHub Actions & GitLab CI templates included
- **📊 Enterprise Features**: Sentence-level tracking, Merkle trees, source attribution
- **🎨 Beautiful Reports**: HTML/Markdown/CSV verification reports
- **🔄 Git Integration**: Automatic metadata extraction from git history
- **📝 CMS Compatible**: YAML/TOML/JSON frontmatter parsing

---

## ✨ Features

### Core Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| **Content Signing** | Sign text, documents, and repositories | ✅ Production |
| **Verification** | Verify signed content and detect tampering | ✅ Production |
| **Batch Operations** | Sign/verify entire repositories | ✅ Production |
| **Incremental Signing** | Only sign changed files (10x faster) | ✅ Production |
| **Streaming Support** | Sign content as it's generated | ✅ Production |
| **Async Operations** | High-performance async client | ✅ Production |

### Enterprise Features

| Feature | Description | Tier |
|---------|-------------|------|
| **Sentence Tracking** | Track individual sentences with Merkle trees | Enterprise |
| **Source Attribution** | Find original sources of content | Enterprise |
| **Plagiarism Detection** | Detect copied content | Enterprise |
| **Git Integration** | Extract metadata from git history | All Tiers |
| **Frontmatter Parsing** | Parse YAML/TOML/JSON metadata | All Tiers |
| **Verification Reports** | Generate HTML/Markdown/CSV reports | All Tiers |

### Integrations

- **✅ LangChain**: Sign AI-generated content automatically
- **✅ OpenAI**: Wrap OpenAI API calls with signing
- **✅ LiteLLM**: Universal LLM signing wrapper
- **✅ WordPress**: Gutenberg & Classic editor plugin
- **✅ GitHub Actions**: Auto-sign on every commit
- **✅ GitLab CI**: CI/CD pipeline integration

### Enhanced Embeddings (Enterprise)

Use the Enterprise API’s invisible embedding endpoint to attach C2PA manifests, Merkle metadata, and portable provenance to any article.

```python
from encypher_enterprise import EncypherClient, EmbeddingOptions

client = EncypherClient(api_key="encypher_live_...")

response = client.sign_with_embeddings(
    text="Breaking news article with multiple sentences...",
    document_id="article_2025_11_12",
    segmentation_level="sentence",
    metadata={"title": "Breaking News", "author": "Jane Doe"},
    embedding_options=EmbeddingOptions(format="markdown", include_text=False),
)

print(response.merkle_tree.root_hash)
print(response.embedded_content[:200])
```

> Need full control? Build an `EncodeWithEmbeddingsRequest` and pass it via `client.sign_with_embeddings(request=request)`.

### Sentence-Level Verification (Enterprise)

Verify a single embedded paragraph or sentence through the public extract-and-verify endpoint.

```python
verification = client.verify_sentence(signed_paragraph)

print("Valid:", verification.valid)
if verification.document:
    print("Document:", verification.document.document_id)
if verification.merkle_proof:
    print("Merkle root:", verification.merkle_proof.root_hash)
```

### Merkle Retrieval & Proofs

```python
tree = client.get_merkle_tree(root_id="root_123")
print("Leaves:", tree.leaf_count)

proof = client.get_merkle_proof(root_id="root_123", leaf_index=42)
print("Verified:", proof.verified)
```

### Streaming over SSE

```python
for event in client.stream_sign(
    "Live content stream...", document_title="Keynote", document_type="article"
):
    print(f"[{event.event}]", event.data)
```

---

## 🚀 Quick Start

### Installation

```bash
# Using UV (recommended)
uv add encypher-enterprise

# Using pip
pip install encypher-enterprise

# With optional dependencies
uv add encypher-enterprise[git,frontmatter]
```

### Basic Usage

```python
from encypher_enterprise import EncypherClient

# Initialize client
client = EncypherClient(api_key="encypher_...")

# Sign content
result = client.sign(
    text="Your content here",
    title="Article Title",
    metadata={"author": "Jane Doe"}
)

print(f"Document ID: {result.document_id}")
print(f"Verification URL: {result.verification_url}")

# Verify content
verification = client.verify(result.signed_text)
print(f"Valid: {verification.is_valid}")
print(f"Tampered: {verification.tampered}")
```

### Sentence Verification

```python
verification = client.verify_sentence(signed_sentence)
print("Valid:", verification.valid)
print("Leaf index:", verification.content.leaf_index if verification.content else "-")
```

### Streaming from the API

```python
for event in client.stream_sign("Streaming response...", document_title="Live Demo"):
    print(f"[{event.event}] {event.data}")
```

### Repository Signing

```python
from pathlib import Path
from encypher_enterprise import RepositorySigner

signer = RepositorySigner(client)

# Sign entire repository with incremental support
result = signer.sign_directory(
    directory=Path("./articles"),
    patterns=["*.md", "*.txt"],
    incremental=True,  # Only sign changed files!
    use_git_metadata=True,  # Extract from git
    use_frontmatter=True  # Parse YAML frontmatter
)

print(result.summary())
# Batch Signing Complete
#   Total: 42
#   Success: 42
#   Skipped (unchanged): 38
#   Time: 2.34s
```

### CLI Usage

```bash
# Sign a single file
encypher sign --file article.md --title "My Article"

# Sign entire repository
encypher sign-repo ./articles \
  --incremental \
  --use-git-metadata \
  --use-frontmatter \
  --report report.html

# Verify repository
encypher verify-repo ./articles \
  --fail-on-tampered \
  --report verification.json

# Generate HTML report
encypher sign-repo ./articles \
  --report report.html \
  --report-format html

# Sentence verification with invisible embeddings
encypher verify-sentence --file signed_snippet.txt

# Inspect Merkle storage
encypher merkle-tree ROOT_ID
encypher merkle-proof ROOT_ID --leaf-index 42

# Stream signing events via SSE
encypher stream-sign --file live.txt --document-title "Keynote"
```

---

## 📚 Documentation

### Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Core Concepts](#core-concepts)
3. [Repository Signing](#repository-signing)
4. [Metadata Providers](#metadata-providers)
5. [Verification & Reports](#verification--reports)
6. [CI/CD Integration](#cicd-integration)
7. [Enterprise Features](#enterprise-features)
8. [Framework Integrations](#framework-integrations)
9. [API Reference](#api-reference)

---

## 🔧 Installation & Setup

### Requirements

- Python 3.9 or higher
- API key from [Encypher Dashboard](https://dashboard.encypher.com)

### Environment Variables

```bash
# Required
export ENCYPHER_API_KEY="encypher_..."

# Optional
export ENCYPHER_BASE_URL="https://api.encypher.com/api/v1"
```

### Optional Dependencies

```bash
# Git integration
uv add gitpython

# Frontmatter parsing
uv add pyyaml

# All optional features
uv add encypher-enterprise[all]
```

---

## 💡 Core Concepts

### Content Signing

Every signed document receives:
- **Document ID**: Unique identifier
- **Cryptographic Signature**: C2PA-compliant
- **Verification URL**: Public verification page
- **Metadata**: Author, date, license, custom fields
- **Merkle Root** (Enterprise): Sentence-level tracking

### Incremental Signing

Encypher tracks file hashes in `.encypher-state.json`:

```json
{
  "version": "1.0",
  "last_updated": "2025-10-29T18:00:00Z",
  "files": {
    "/path/to/file.md": {
      "file_hash": "sha256:abc123...",
      "document_id": "doc_xyz789",
      "signed_at": "2025-10-29T17:30:00Z",
      "file_size": 1024
    }
  }
}
```

**Benefits:**
- ⚡ **10x faster** for large repositories
- 💾 **Bandwidth savings** (only upload changed files)
- 🔄 **Git-friendly** (state file can be committed)

### Metadata Providers

Extract metadata from multiple sources:

```python
from encypher_enterprise import (
    GitMetadataProvider,
    FrontmatterMetadataProvider,
    CombinedMetadataProvider
)

# Git metadata
git_provider = GitMetadataProvider()

# Frontmatter metadata
frontmatter_provider = FrontmatterMetadataProvider(
    fallback_author="Jane Doe"
)

# Combined (frontmatter takes priority)
combined = CombinedMetadataProvider([
    frontmatter_provider,
    git_provider
])

# Use in signing
result = signer.sign_directory(
    directory=Path("./articles"),
    metadata_fn=combined.get_metadata
)
```

---

## 📁 Repository Signing

### Basic Repository Signing

```python
from encypher_enterprise import RepositorySigner, FileMetadata

signer = RepositorySigner(client)

result = signer.sign_directory(
    directory=Path("./articles"),
    patterns=["*.md", "*.txt", "*.html"],
    exclude_patterns=["drafts/**", "node_modules/**"],
    recursive=True
)
```

### With Custom Metadata

```python
def custom_metadata(file_path: Path) -> FileMetadata:
    return FileMetadata(
        title=file_path.stem,
        author="Jane Doe",
        publisher="Acme News",
        license="CC-BY-4.0",
        category="Technology"
    )

result = signer.sign_directory(
    directory=Path("./articles"),
    metadata_fn=custom_metadata
)
```

### Incremental Signing

```python
# First run: Signs all files
result1 = signer.sign_directory(
    directory=Path("./articles"),
    incremental=True
)
# Total: 100, Success: 100, Skipped: 0

# Second run: Only signs changed files
result2 = signer.sign_directory(
    directory=Path("./articles"),
    incremental=True
)
# Total: 5, Success: 5, Skipped: 95
```

### Force Re-signing

```python
# Force re-sign all files (ignores state)
result = signer.sign_directory(
    directory=Path("./articles"),
    incremental=True,
    force_resign=True
)
```

---

## 🏷️ Metadata Providers

### Git Metadata Provider

Extracts metadata from git history:

```python
from encypher_enterprise import GitMetadataProvider

provider = GitMetadataProvider(repo_path=Path("."))

metadata = provider.get_metadata(Path("article.md"))

# Extracted fields:
# - author: Last commit author
# - created: First commit date
# - modified: Last commit date
# - custom.git_commit: Latest commit SHA
# - custom.git_branch: Current branch
# - custom.git_contributors: List of all contributors
```

### Frontmatter Metadata Provider

Parses YAML/TOML/JSON frontmatter:

```python
from encypher_enterprise import FrontmatterMetadataProvider

provider = FrontmatterMetadataProvider(
    field_mapping={"writer": "author"},  # Custom mapping
    fallback_author="Default Author"
)

# Supports:
# - YAML (---)
# - TOML (+++)
# - JSON ({})
```

**Example Frontmatter:**

```yaml
---
title: My Article
author: Jane Doe
date: 2025-10-29
tags: [technology, ai]
license: CC-BY-4.0
---

Article content here...
```

### Combined Metadata Provider

Merge multiple providers with priority:

```python
from encypher_enterprise import CombinedMetadataProvider

combined = CombinedMetadataProvider([
    frontmatter_provider,  # Priority 1
    git_provider,          # Priority 2 (fills gaps)
    filesystem_provider    # Priority 3 (fallback)
])
```

---

## ✅ Verification & Reports

### Batch Verification

```python
from encypher_enterprise import RepositoryVerifier

verifier = RepositoryVerifier(client)

result = verifier.verify_directory(
    directory=Path("./articles"),
    patterns=["*.signed.md"],
    fail_on_tampered=True  # Raise exception if tampered
)

print(result.summary())
# Batch Verification Complete
#   Total: 42
#   Valid: 40
#   Tampered: 2
#   Failed: 0
```

### Generate Reports

```python
from encypher_enterprise import ReportGenerator

generator = ReportGenerator()

# HTML report (beautiful, responsive)
generator.generate_html(
    result,
    Path("report.html"),
    title="Content Verification Report",
    publisher="Acme News"
)

# Markdown report (for docs)
generator.generate_markdown(result, Path("report.md"))

# CSV export (for spreadsheets)
generator.generate_csv(result, Path("report.csv"))
```

### Verification Badges

```python
from encypher_enterprise import generate_verification_badge

badge_svg = generate_verification_badge(
    document_id="doc_123",
    verification_url="https://encypher.com/verify/doc_123",
    output_path=Path("badge.svg")
)
```

---

## 🤖 CI/CD Integration

### GitHub Actions

**Setup (2 minutes):**

1. Add `ENCYPHER_API_KEY` secret to repository
2. Workflows are already in `.github/workflows/`
3. Commit and push!

**Auto-Sign Workflow** (`.github/workflows/sign-content.yml`):

```yaml
name: Sign Content

on:
  push:
    branches: [main]
    paths: ['articles/**']

jobs:
  sign:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: uv pip install --system encypher-enterprise
      - run: |
          encypher sign-repo ./articles \
            --incremental \
            --use-git-metadata \
            --report report.html
        env:
          ENCYPHER_API_KEY: ${{ secrets.ENCYPHER_API_KEY }}
      - run: |
          git add .
          git commit -m "Sign content [skip ci]"
          git push
```

**Auto-Verify Workflow** (`.github/workflows/verify-content.yml`):

```yaml
name: Verify Content

on:
  pull_request:
    paths: ['**.signed.md']

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: uv pip install --system encypher-enterprise
      - run: |
          encypher verify-repo . \
            --fail-on-tampered \
            --report verification.json
        env:
          ENCYPHER_API_KEY: ${{ secrets.ENCYPHER_API_KEY }}
```

### GitLab CI

Copy `.gitlab-ci.yml.example` to `.gitlab-ci.yml`:

```yaml
sign_content:
  script:
    - uv pip install --system encypher-enterprise
    - encypher sign-repo ./articles --incremental
  only:
    - main
```

---

## 🎓 Examples

### Example 1: News Publisher

```python
# Sign all articles with author metadata
from encypher_enterprise import RepositorySigner, GitMetadataProvider

git_provider = GitMetadataProvider()
signer = RepositorySigner(client)

result = signer.sign_directory(
    directory=Path("./articles"),
    patterns=["*.md"],
    metadata_fn=git_provider.get_metadata,
    incremental=True
)

# Generate public verification page
from encypher_enterprise import ReportGenerator
generator = ReportGenerator()
generator.generate_html(
    result,
    Path("public/verification.html"),
    title="Acme News - Verified Content",
    publisher="Acme News Corp"
)
```

### Example 2: Academic Publisher

```python
# Sign research papers with frontmatter metadata
from encypher_enterprise import FrontmatterMetadataProvider

frontmatter_provider = FrontmatterMetadataProvider(
    field_mapping={
        "authors": "author",
        "doi": "custom.doi",
        "journal": "publisher"
    }
)

result = signer.sign_directory(
    directory=Path("./papers"),
    patterns=["*.md"],
    metadata_fn=frontmatter_provider.get_metadata
)
```

### Example 3: Content Platform

```python
# Verify all user-submitted content
from encypher_enterprise import RepositoryVerifier

verifier = RepositoryVerifier(client, max_concurrent=10)

result = verifier.verify_directory(
    directory=Path("./user-content"),
    patterns=["*.signed.*"],
    fail_on_tampered=True
)

# Alert if tampering detected
if result.tampered > 0:
    send_alert(f"Tampering detected in {result.tampered} files!")
```

---

## 🔬 Enterprise Features

### Sentence-Level Tracking

```python
# Enable Merkle tree encoding
signer = RepositorySigner(client, use_sentence_tracking=True)

result = signer.sign_directory(
    directory=Path("./articles"),
    patterns=["*.md"]
)

# Each sentence gets a unique hash in Merkle tree
```

### Source Attribution

```python
# Find original sources
result = client.find_sources(
    text="Text to check for sources",
    min_similarity=0.85,
    max_results=10
)

for match in result['matches']:
    print(f"Source: {match['document_id']}")
    print(f"Similarity: {match['similarity']:.2%}")
    print(f"Matched: {match['matched_text']}")
```

### Plagiarism Detection

```python
# Detect plagiarism
result = client.detect_plagiarism(
    text="Text to check",
    threshold=0.80
)

if result['is_plagiarized']:
    print(f"Plagiarism detected!")
    print(f"Original: {result['original_document_id']}")
    print(f"Similarity: {result['similarity']:.2%}")
```

---

## 🔌 Framework Integrations

### LangChain

```python
from encypher_enterprise.integrations import EncypherLangChain

# Wrap any LangChain LLM
llm = EncypherLangChain(
    base_llm=ChatOpenAI(),
    encypher_client=client,
    auto_sign=True
)

# All outputs are automatically signed
response = llm.invoke("Write an article about AI")
print(response.verification_url)
```

### OpenAI

```python
from encypher_enterprise.integrations import EncypherOpenAI

# Drop-in replacement for OpenAI client
client_wrapped = EncypherOpenAI(
    api_key="sk-...",
    encypher_client=client
)

response = client_wrapped.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# Response includes verification URL
print(response.verification_url)
```

### LiteLLM

```python
from encypher_enterprise.integrations import EncypherLiteLLM

# Works with any LLM provider
llm = EncypherLiteLLM(
    model="gpt-4",
    encypher_client=client
)

response = llm.completion(
    messages=[{"role": "user", "content": "Hello"}]
)
```

---

## 📖 API Reference

### EncypherClient

```python
client = EncypherClient(
    api_key="encypher_...",
    base_url="https://api.encypher.com/api/v1"
)

# Sign content
result = client.sign(text, title, metadata)

# Verify content
verification = client.verify(signed_text)

# Lookup sentence
lookup = client.lookup(sentence)

# Get stats
stats = client.stats()

# Enterprise features
client.encode_document_merkle(text, document_id)
client.find_sources(text, min_similarity)
client.detect_plagiarism(text, threshold)
client.sign_with_embeddings(text="...", document_id="doc_123")
client.get_merkle_tree(root_id="root_123")
client.get_merkle_proof(root_id="root_123", leaf_index=5)
client.verify_sentence(text_with_embeddings)
client.stream_sign("Streaming text...")
```

### RepositorySigner

```python
signer = RepositorySigner(
    client,
    use_sentence_tracking=False,
    max_concurrent=5
)

result = signer.sign_directory(
    directory,
    patterns,
    exclude_patterns,
    metadata_fn,
    recursive,
    output_dir,
    save_manifest,
    incremental,
    state_file,
    force_resign
)
```

### RepositoryVerifier

```python
verifier = RepositoryVerifier(client, max_concurrent=5)

result = verifier.verify_directory(
    directory,
    patterns,
    exclude_patterns,
    recursive,
    fail_on_tampered
)
```

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=encypher_enterprise --cov-report=html

# Run specific test file
uv run pytest tests/test_state.py -v
```

**Current Test Coverage:**
- `state.py`: 91% ✅
- `batch.py`: 63% ✅
- Overall: ~30% (Integration tests expanding)

---

## 🤝 Support

- **Documentation**: [docs.encypher.com](https://docs.encypher.com)
- **Email**: sdk@encypher.com
- **GitHub Issues**: [github.com/encypherai/enterprise-sdk/issues](https://github.com/encypherai/enterprise-sdk/issues)
- **Dashboard**: [dashboard.encypher.com](https://dashboard.encypher.com)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- [C2PA](https://c2pa.org/) - Content authenticity standards
- [Python](https://python.org/) - Programming language
- [UV](https://github.com/astral-sh/uv) - Package manager
- [GitPython](https://github.com/gitpython-developers/GitPython) - Git integration
- [PyYAML](https://pyyaml.org/) - YAML parsing

---

<div align="center">

**Made with ❤️ by Encypher**

[Website](https://encypher.com) • [Dashboard](https://dashboard.encypher.com) • [Docs](https://docs.encypher.com)

</div>
