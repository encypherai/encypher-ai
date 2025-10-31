# Test Migration Guide

## Overview

Tests have been updated to reflect the refactoring from visible embeddings to invisible Unicode embeddings using the `encypher-ai` package.

## Test Files

### Active Tests

**`test_embedding_service_invisible.py`** - NEW
- Tests the refactored `EmbeddingService` with invisible Unicode embeddings
- Uses `encypher-ai` package for embedding/extraction
- Tests Ed25519 key pair generation and signing
- Integration tests for end-to-end workflow

### Deprecated Tests

**`test_embedding_service.py`** - DEPRECATED
- Tests the old HMAC-based visible embedding system
- Will be removed after migration is complete
- DO NOT update these tests

**`test_embedding_utilities.py`** - DEPRECATED
- Tests HTML embedding utilities (now deprecated)
- Will be removed after migration is complete

**`test_embedding_api.py`** - NEEDS UPDATE
- API endpoint tests
- Needs to be updated for invisible embeddings

## Running Tests

### Run new invisible embedding tests:
```bash
pytest tests/test_embedding_service_invisible.py -v
```

### Run all tests (including deprecated):
```bash
pytest tests/ -v
```

### Skip deprecated tests:
```bash
pytest tests/ -v -k "not (test_embedding_service.py or test_embedding_utilities.py)"
```

## Test Requirements

The new tests require:
- `encypher-ai` package installed
- `cryptography` package for Ed25519 keys
- `pytest-asyncio` for async tests

Install with:
```bash
uv sync
```

## Key Differences

### Old Tests (Visible Embeddings)
```python
# Old: HMAC signatures
service = EmbeddingService(b'secret_key')
ref_id = service._generate_ref_id()
signature = service._generate_signature(ref_id)

# Old: Visible format
assert embedding == "ency:v1/a3f9c2e1/8k3mP9xQ"
```

### New Tests (Invisible Embeddings)
```python
# New: Ed25519 key pairs
private_key, public_key = generate_ed25519_key_pair()
service = EmbeddingService(private_key, "signer_id")

# New: Invisible embeddings
embeddings = await service.create_embeddings(...)
assert embeddings[0].embedded_text != embeddings[0].text_content

# New: Extraction and verification
is_valid, signer_id, payload = UnicodeMetadata.verify_metadata(
    text=embedded_text,
    public_key_provider=public_key_provider
)
```

## Migration Checklist

- [x] Create new test file for invisible embeddings
- [ ] Update API endpoint tests
- [ ] Add integration tests for public verification API
- [ ] Add performance benchmarks
- [ ] Remove deprecated test files
- [ ] Update CI/CD pipeline

## Notes

- Old tests will continue to work until the old code is removed
- New tests use mocking for database operations
- Integration tests require a test database
- Performance tests should compare old vs new approach
