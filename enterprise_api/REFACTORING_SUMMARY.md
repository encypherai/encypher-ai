# Enterprise API Refactoring: Invisible Embeddings

**Date:** October 30, 2025  
**Branch:** `feature/invisible-embeddings-refactor`  
**Status:** ✅ Core refactoring complete

## Overview

Refactored the Enterprise API to properly use the free `encypher-ai` package as its foundation, replacing visible embedding strings with invisible Unicode variation selector embeddings.

## Problem Statement

The Enterprise API had **two separate embedding systems**:

1. ✅ `/sign` endpoint - Used `encypher-ai` (invisible Unicode embeddings)
2. ❌ `/encode-with-embeddings` endpoint - Custom implementation (visible `ency:v1/...` strings)

This violated our core principle: **The Enterprise API should build on top of the free open-source package, not reinvent it.**

## Solution

### Architecture Before

```
Enterprise API
├── /sign endpoint → Uses encypher-ai ✅
└── /encode-with-embeddings → Custom HMAC signatures ❌
    ├── Visible format: ency:v1/a3f9c2e1/8k3mP9xQ
    ├── HTML data attributes
    └── Hidden spans/comments
```

### Architecture After

```
Free Package (encypher-ai)
├── Invisible Unicode variation selector embeddings
├── Digital signatures (Ed25519)
├── C2PA manifest support
└── Basic verification
         ↓ (foundation)
Enterprise API
├── /sign endpoint → Uses encypher-ai ✅
└── /encode-with-embeddings → Uses encypher-ai ✅
    ├── Merkle tree integration (enterprise feature)
    ├── Per-sentence embeddings (using encypher-ai)
    ├── Database storage (enterprise feature)
    └── Public verification API (enterprise feature)
```

## Changes Made

### 1. `embedding_service.py` - Core Service

**Before:**
- Custom HMAC-SHA256 signatures
- Generated visible `ency:v1/...` strings
- 64-bit ref_id generation

**After:**
- Uses `encypher.core.unicode_metadata.UnicodeMetadata`
- Invisible Unicode variation selector embeddings
- Enterprise features layered on top:
  - Merkle tree integration
  - Database storage
  - Batch operations
  - Analytics

**Key Changes:**
```python
# OLD: Custom HMAC
def _generate_signature(self, ref_id: int) -> str:
    hmac_full = hmac.new(self.secret_key, ref_bytes, hashlib.sha256).digest()
    return hmac_full[:8].hex()

# NEW: Uses encypher-ai
embedded_text = UnicodeMetadata.embed_metadata(
    text=segment,
    private_key=self.private_key,
    signer_id=self.signer_id,
    custom_metadata=enterprise_metadata
)
```

### 2. `embeddings.py` - API Endpoint

**Before:**
- Initialized with `SECRET_KEY` for HMAC
- Returned visible embedding strings
- Used HTML embedder for injection

**After:**
- Loads organization's Ed25519 private key
- Returns text with invisible embeddings
- No HTML manipulation needed

**Key Changes:**
```python
# OLD: Secret key
SECRET_KEY = os.getenv('EMBEDDING_SECRET_KEY').encode()
embedding_service = EmbeddingService(SECRET_KEY)

# NEW: Organization's private key
private_key = await load_organization_private_key(organization_id, db)
embedding_service = EmbeddingService(private_key, signer_id)
```

### 3. `embeddings.py` - Schemas

**Before:**
- Required fields: `ref_id`, `signature`, `embedding`, `verification_url`
- Visible format strings

**After:**
- All visible fields now `Optional` (deprecated)
- `text` field contains invisible embedding
- Added deprecation notices

### 4. `html_embedder.py` - Utility

**Before:**
- Injected visible markers into HTML
- Three methods: data-attribute, span, comment

**After:**
- Marked as DEPRECATED
- Returns HTML unchanged (embeddings already invisible)
- Warns users to use encypher-ai directly

## Benefits

### 1. **Unified Architecture**
- Single source of truth: `encypher-ai` package
- No duplicate embedding logic
- Consistent behavior across all endpoints

### 2. **Invisible by Design**
- Zero visible footprint in content
- Portable across copy/paste
- Standards-compliant (Unicode variation selectors)

### 3. **Clear Value Proposition**

**Free Package (`encypher-ai`):**
- Single document signing
- Basic verification
- Self-hosted only

**Enterprise API (Paid):**
- Merkle trees for hierarchical authentication
- Per-sentence tracking
- Source attribution & plagiarism detection
- Public verification API (no auth)
- Batch operations
- SaaS infrastructure
- Analytics & forensics

### 4. **Maintainability**
- Less code to maintain
- Bug fixes in `encypher-ai` benefit Enterprise API
- Clear separation of concerns

## Migration Guide

### For API Users

**Old Response:**
```json
{
  "embeddings": [
    {
      "ref_id": "a3f9c2e1",
      "signature": "8k3mP9xQ",
      "embedding": "ency:v1/a3f9c2e1/8k3mP9xQ",
      "verification_url": "https://verify.encypher.ai/a3f9c2e1"
    }
  ]
}
```

**New Response:**
```json
{
  "embeddings": [
    {
      "leaf_index": 0,
      "text": "Sentence with invisible embedding.",
      "leaf_hash": "abc123..."
    }
  ],
  "embedded_content": "Full document with invisible embeddings..."
}
```

### For Verification

**Old Method:**
```bash
curl "https://api.encypherai.com/api/v1/public/verify/a3f9c2e1?signature=8k3mP9xQ"
```

**New Method:**
```bash
curl -X POST https://api.encypherai.com/api/v1/public/extract-and-verify \
  -d '{"text": "Content with invisible embeddings..."}'
```

## Next Steps

### Pending Work

1. ✅ Core refactoring complete
2. ✅ HTML embedder deprecated
3. ⏳ Update public verification API
4. ⏳ Update tests
5. ⏳ Update API documentation
6. ⏳ Migration guide for existing users

### Testing Required

- [ ] Unit tests for `embedding_service.py`
- [ ] Integration tests for `/encode-with-embeddings`
- [ ] End-to-end tests with verification
- [ ] Performance benchmarks
- [ ] Backward compatibility tests

### Documentation Updates

- [ ] API reference documentation
- [ ] OpenAPI/Swagger specs
- [ ] SDK examples
- [ ] Migration guide for existing integrations

## Technical Details

### Unicode Variation Selectors

The `encypher-ai` package uses Unicode variation selectors (U+FE00-FE0F) to embed metadata invisibly:

- **3 bytes per selector** in UTF-8
- **Attached to base characters** in the text
- **Rendering engines ignore them** - display only base character
- **Standards-compliant** - proper Unicode usage
- **Portable** - survives copy/paste

Example (conceptual - actual selectors are invisible):
```
"Hello world" → "H[VS]e[VS]l[VS]l[VS]o[VS] w[VS]o[VS]r[VS]l[VS]d"
```

### Enterprise Features

The Enterprise API adds these features on top of `encypher-ai`:

1. **Merkle Tree Integration**
   - Links embeddings to hierarchical authentication
   - Stores tree structure in database
   - Provides proof generation

2. **Database Storage**
   - Tracks all embeddings per organization
   - Links to documents and Merkle trees
   - Enables analytics and reporting

3. **Public Verification API**
   - No authentication required
   - Third-party verification
   - Batch operations

4. **Source Attribution**
   - Track content origins
   - Detect plagiarism
   - Monitor unauthorized use

### 5. `verify.py` - Public Verification API

**Before:**
- `/verify/{ref_id}` - Verified visible embeddings with HMAC signatures
- Required `ref_id` and `signature` parameters

**After:**
- ✅ Old endpoints still work (backward compatibility)
- ✅ **NEW:** `/extract-and-verify` - Extracts invisible embeddings from text
- Uses `encypher-ai` to extract and verify
- Returns full enterprise metadata

**Key Changes:**
```python
# NEW: Extract and verify invisible embedding
@router.post("/extract-and-verify")
async def extract_and_verify_embedding(
    extract_request: ExtractAndVerifyRequest,
    ...
):
    # Use encypher-ai to extract invisible embedding
    is_valid, signer_id, payload = UnicodeMetadata.verify_metadata(
        text=extract_request.text,
        public_key_provider=public_key_provider
    )
    
    # Look up enterprise metadata in database
    # Return full verification result
```

## Commits

1. `docs: update embeddings documentation to reflect invisible Unicode technique`
2. `feat: refactor embeddings to use encypher-ai invisible Unicode technique`
3. `docs: deprecate HTML embedder and add refactoring summary`
4. `feat: add public extract-and-verify endpoint for invisible embeddings`

## References

- [encypher-ai Package](../encypher-ai/README.md)
- [Unicode Variation Selectors](https://unicode.org/faq/vs.html)
- [Enterprise API README](./README.md)
