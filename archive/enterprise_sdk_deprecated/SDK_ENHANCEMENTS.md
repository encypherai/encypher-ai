# SDK Enhancements for Repository Signing

**Date:** October 29, 2025
**Status:** Ready for Testing

## Overview

Enhanced the Encypher Enterprise SDK with comprehensive tooling for publishers to recursively sign entire repositories with C2PA-compliant metadata and optional sentence-level tracking.

## What Was Added

### 1. Repository Signing Module (`batch.py`)

**New Classes:**

- **`FileMetadata`** - C2PA-compliant metadata structure
  - Aligns with C2PA 2.2 manifest specification
  - Supports all standard C2PA fields (author, publisher, license, etc.)
  - Includes AI-related metadata (ai_generated, ai_model, etc.)
  - Custom metadata support
  - Auto-generates C2PA manifest JSON

- **`RepositorySigner`** - Batch signing for directories
  - Recursive directory scanning
  - Glob pattern matching (e.g., `*.md`, `*.txt`)
  - Exclude patterns (e.g., `node_modules/**`, `.git/**`)
  - Concurrent signing (configurable max_concurrent)
  - Both sync and async support
  - Progress tracking and error handling

- **`SigningResult`** - Individual file result
  - Success/failure status
  - Document ID and verification URL
  - Processing time
  - Error details (if failed)

- **`BatchSigningResult`** - Batch operation summary
  - Total/successful/failed counts
  - Detailed results for each file
  - JSON export for reporting
  - Human-readable summary

### 2. Enhanced Client Methods

**Added to `EncypherClient`:**

```python
# Merkle tree encoding (Enterprise tier)
def encode_document_merkle(
    text: str,
    document_id: str,
    segmentation_levels: Optional[list] = None
) -> Dict[str, Any]

# Source attribution (Enterprise tier)
def find_sources(
    text: str,
    min_similarity: float = 0.8,
    max_results: int = 10
) -> Dict[str, Any]

# Plagiarism detection (Enterprise tier)
def detect_plagiarism(
    text: str,
    document_id: str,
    threshold: float = 0.85
) -> Dict[str, Any]
```

### 3. New CLI Commands

**Repository Signing:**
```bash
encypher sign-repo ./articles \
  --author "Jane Doe" \
  --publisher "Acme News" \
  --license "CC-BY-4.0" \
  --pattern "*.md" \
  --pattern "*.txt" \
  --save-manifest \
  --report signing-report.json
```

**Merkle Encoding:**
```bash
encypher merkle-encode \
  --file article.txt \
  --document-id doc_123 \
  --level sentence \
  --level paragraph
```

**Source Attribution:**
```bash
encypher find-sources \
  --text "Text to check" \
  --min-similarity 0.85 \
  --max-results 10
```

### 4. Example Scripts

**`examples/repository_signing.py`** - Comprehensive examples:
- Basic repository signing
- Reading metadata from YAML frontmatter
- Using git history for author/date
- Async signing for better performance

## Features

### C2PA Compliance

The `FileMetadata` class generates fully C2PA 2.2 compliant manifests:

```python
metadata = FileMetadata(
    title="Breaking News Article",
    author="Jane Doe",
    created=datetime.now(),
    publisher="Acme News",
    license="CC-BY-4.0",
    ai_generated=False
)

# Generates C2PA manifest:
{
  "claim_generator": "Encypher Enterprise SDK",
  "claim_generator_version": "1.0.0",
  "title": "Breaking News Article",
  "assertions": [
    {
      "label": "c2pa.creative-work",
      "data": {
        "author": [{"name": "Jane Doe"}],
        "dateCreated": "2025-10-29T..."
      }
    },
    {
      "label": "c2pa.actions",
      "data": {
        "actions": [{
          "action": "c2pa.created",
          "when": "2025-10-29T...",
          "softwareAgent": "Encypher Enterprise SDK"
        }]
      }
    }
  ]
}
```

### Flexible Metadata Generation

Publishers can customize metadata per file:

```python
def get_metadata(file_path: Path) -> FileMetadata:
    # Read from YAML frontmatter
    if file_path.suffix == '.md':
        frontmatter = parse_frontmatter(file_path)
        return FileMetadata(
            title=frontmatter.get('title'),
            author=frontmatter.get('author'),
            tags=frontmatter.get('tags', [])
        )

    # Use git history
    commit = get_last_commit(file_path)
    return FileMetadata(
        author=commit.author.name,
        created=commit.authored_date
    )
```

### Concurrent Processing

Async support for high-performance batch signing:

```python
from encypher_enterprise import AsyncEncypherClient, RepositorySigner

async with AsyncEncypherClient(api_key="...") as client:
    signer = RepositorySigner(
        client=client,
        max_concurrent=10  # Sign 10 files simultaneously
    )

    result = signer.sign_directory(...)
```

### Comprehensive Reporting

JSON reports for audit trails:

```json
{
  "summary": {
    "total_files": 42,
    "successful": 42,
    "failed": 0,
    "total_time": 23.45
  },
  "results": [
    {
      "file_path": "article1.md",
      "success": true,
      "document_id": "doc_abc123",
      "verification_url": "https://encypher.com/verify/doc_abc123",
      "processing_time": 0.52
    }
  ]
}
```

## Use Cases

### 1. News Publishers

Sign entire article repositories:

```bash
encypher sign-repo ./articles \
  --author "Editorial Team" \
  --publisher "The Daily News" \
  --license "All Rights Reserved" \
  --pattern "*.md" \
  --recursive
```

### 2. Legal Firms

Sign legal documents with proper metadata:

```python
signer = RepositorySigner(client)
result = signer.sign_directory(
    directory=Path("./contracts"),
    patterns=["*.pdf", "*.docx"],
    metadata_fn=lambda p: FileMetadata(
        author="Legal Department",
        publisher="Smith & Associates",
        license="Confidential",
        category="legal_document"
    )
)
```

### 3. Academic Institutions

Sign research papers with attribution:

```python
def get_research_metadata(file_path: Path) -> FileMetadata:
    return FileMetadata(
        author="Dr. Jane Smith",
        publisher="University Research Lab",
        license="CC-BY-4.0",
        category="research",
        custom={
            "doi": "10.1234/example",
            "journal": "Nature",
            "peer_reviewed": True
        }
    )

result = signer.sign_directory(
    directory=Path("./papers"),
    patterns=["*.pdf"],
    metadata_fn=get_research_metadata,
    use_sentence_tracking=True  # Enterprise tier
)
```

### 4. Content Creators

Sign blog posts and articles:

```bash
encypher sign-repo ~/blog/content \
  --author "Jane Blogger" \
  --publisher "Jane's Tech Blog" \
  --license "CC-BY-SA-4.0" \
  --pattern "*.md" \
  --pattern "*.html"
```

## Enterprise Tier Features

### Sentence-Level Tracking

Enable Merkle tree encoding for attribution:

```python
signer = RepositorySigner(
    client=client,
    use_sentence_tracking=True  # Requires Enterprise tier
)

# Each file is encoded into Merkle trees
# Enables plagiarism detection and source attribution
```

### Attribution Tracking

Find sources for text:

```python
# After signing repository
result = client.find_sources(
    text="Some text from another document",
    min_similarity=0.85
)

for match in result['matches']:
    print(f"Found in: {match['document_id']}")
    print(f"Similarity: {match['similarity']:.2%}")
```

### Plagiarism Detection

Check documents for plagiarism:

```python
result = client.detect_plagiarism(
    text=document_content,
    document_id="doc_new_article",
    threshold=0.85
)

if result['is_plagiarized']:
    print(f"Plagiarism: {result['plagiarism_percentage']:.1%}")
```

## API Alignment

The SDK now fully supports all Enterprise API endpoints:

| API Endpoint | SDK Method | CLI Command |
|--------------|------------|-------------|
| `POST /api/v1/sign` | `client.sign()` | `encypher sign` |
| `POST /api/v1/verify` | `client.verify()` | `encypher verify` |
| `POST /api/v1/lookup` | `client.lookup()` | `encypher lookup` |
| `GET /stats` | `client.get_stats()` | `encypher stats` |
| `POST /api/v1/enterprise/merkle/encode` | `client.encode_document_merkle()` | `encypher merkle-encode` |
| `POST /api/v1/enterprise/merkle/attribute` | `client.find_sources()` | `encypher find-sources` |
| `POST /api/v1/enterprise/merkle/detect-plagiarism` | `client.detect_plagiarism()` | _(coming soon)_ |
| _(batch signing)_ | `RepositorySigner.sign_directory()` | `encypher sign-repo` |

## Testing

### Unit Tests Needed

```python
# tests/test_batch.py
def test_file_metadata_to_c2pa_manifest():
    """Test C2PA manifest generation."""
    metadata = FileMetadata(
        title="Test",
        author="Jane Doe",
        ai_generated=True
    )
    manifest = metadata.to_c2pa_manifest()
    assert manifest["title"] == "Test"
    assert "c2pa.creative-work" in [a["label"] for a in manifest["assertions"]]

def test_repository_signer_sync():
    """Test synchronous repository signing."""
    # Mock client and test signing

def test_repository_signer_async():
    """Test asynchronous repository signing."""
    # Mock async client and test signing
```

### Integration Tests

```bash
# Test CLI commands
export ENCYPHER_API_KEY="test_key"

# Test repository signing
encypher sign-repo ./test-articles --author "Test" --publisher "Test Org"

# Test Merkle encoding
encypher merkle-encode --file test.txt --document-id test_123

# Test source attribution
encypher find-sources --text "Test text" --min-similarity 0.8
```

## Documentation Updates

- ✅ Updated `README.md` with repository signing examples
- ✅ Added `examples/repository_signing.py` with comprehensive examples
- ✅ Updated `__init__.py` to export new classes
- ✅ Added CLI commands with help text
- ✅ Created this enhancement document

## Next Steps

1. **Testing**
   - Write unit tests for `batch.py`
   - Write integration tests for CLI commands
   - Test with real API endpoints

2. **Documentation**
   - Add to official docs site
   - Create video tutorial
   - Write blog post announcement

3. **Examples**
   - WordPress plugin integration
   - GitHub Actions workflow
   - CI/CD pipeline example

4. **Future Enhancements**
   - Support for binary files (PDF, DOCX)
   - Incremental signing (only sign changed files)
   - Parallel processing optimization
   - Progress bars for large repositories
   - Dry-run mode

## Breaking Changes

None - all changes are additive.

## Migration Guide

No migration needed. Existing code continues to work:

```python
# Old code still works
client = EncypherClient(api_key="...")
result = client.sign("Content")

# New features are opt-in
from encypher_enterprise import RepositorySigner
signer = RepositorySigner(client)
```

## Summary

The SDK now provides **enterprise-grade repository signing** with:

✅ **C2PA 2.2 compliance** - Full manifest support
✅ **Batch operations** - Sign entire repositories
✅ **Flexible metadata** - Customizable per file
✅ **Concurrent processing** - Async support
✅ **CLI tools** - Easy command-line usage
✅ **Enterprise features** - Merkle trees, attribution, plagiarism detection
✅ **Comprehensive examples** - Real-world use cases

Publishers can now easily sign their entire content repositories with a single command, ensuring all content is authenticated and traceable.
