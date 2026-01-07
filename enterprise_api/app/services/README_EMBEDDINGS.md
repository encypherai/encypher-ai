# Invisible Signed Embeddings System

## Overview

The **Invisible Signed Embeddings** system provides cryptographically signed, invisible references embedded directly into text content using Unicode variation selectors. These embeddings are:

- **Completely invisible** to readers
- **Portable** - travel with content when copied/pasted
- **Verifiable** by third parties without API keys
- **C2PA-compliant** using the `encypher-ai` package

## How It Works

Embeddings use **Unicode variation selectors (U+FE00-FE0F, U+E0100-E01EF)** attached to characters in the text. These selectors are:

- **Invisible** - Rendering engines display only the base character
- **Standards-compliant** - Using Unicode variation selectors as designed
- **Portable** - Preserved during copy/paste operations
- **Distributed** - Spread across multiple characters for resilience

```
"Hello world" → "H[VS]e[VS]l[VS]l[VS]o[VS] w[VS]o[VS]r[VS]l[VS]d"
                 (variation selectors are invisible)
```

## Architecture

```
┌─────────────────┐
│  Content Owner  │
└────────┬────────┘
         │ 1. Submit document
         ▼
┌─────────────────────────────────────┐
│  Enterprise API                     │
│  POST /api/v1/sign/advanced         │
│                                     │
│  1. Build Merkle tree               │
│  2. Generate Ed25519 signatures     │
│  3. Embed using Unicode VS          │
│  4. Store in content_references     │
└────────┬────────────────────────────┘
         │ 2. Returns embedded content
         ▼
┌─────────────────┐
│  Published      │
│  Content        │
│  (invisible     │
│   embeddings)   │
└────────┬────────┘
         │ 3. Content copied/scraped
         ▼
┌─────────────────┐
│  Third Party    │
│  (Reader/Bot)   │
└────────┬────────┘
         │ 4. Extract & verify
         ▼
┌─────────────────────────────────────┐
│  Public Verification API            │
│  POST /api/v1/public/extract-and-   │
│       verify                        │
│                                     │
│  Returns: metadata, C2PA, license   │
└─────────────────────────────────────┘
```

## API Endpoints

### Sign with Advanced Embeddings

**Endpoint:** `POST /api/v1/sign/advanced`  
**Auth:** Required (API key)  
**Tier:** Professional+

**Request:**
```json
{
  "document_id": "article_001",
  "text": "Full article text...",
  "segmentation_level": "sentence",
  "c2pa_manifest_url": "https://...",
  "license": {
    "type": "All Rights Reserved",
    "contact_email": "licensing@example.com"
  }
}
```

**Response:**
```json
{
  "success": true,
  "document_id": "article_001",
  "merkle_tree": {
    "root_hash": "abc123...",
    "total_leaves": 42,
    "tree_depth": 6
  },
  "embeddings": [
    {
      "leaf_index": 0,
      "text": "Sentence one.",
      "ref_id": "a3f9c2e1",
      "leaf_hash": "def456...",
      "embedded_text": "Sentence one."
    }
  ],
  "embedded_content": "Full article text with invisible embeddings...",
  "statistics": {
    "total_sentences": 42,
    "embeddings_created": 42,
    "processing_time_ms": 234.56
  }
}
```

### Public: Extract and Verify

**Endpoint:** `POST /api/v1/public/extract-and-verify`  
**Auth:** None (public)

**Request:**
```json
{
  "text": "Content with invisible embeddings..."
}
```

**Response:**
```json
{
  "success": true,
  "embeddings_found": 5,
  "verified": [
    {
      "ref_id": "a3f9c2e1",
      "valid": true,
      "signer_id": "org_technews",
      "signer_name": "TechNews Corp",
      "document_id": "article_001"
    }
  ]
}
```

### Public: Verify by Reference ID

**Endpoint:** `GET /api/v1/public/verify/{ref_id}`  
**Auth:** None (public)

## Security

### Cryptographic Signing

- **Algorithm:** Ed25519 (elliptic curve)
- **Key Management:** Per-organization key pairs
- **Trust Anchors:** Public keys stored in organizations table
- **Verification:** Cryptographic signature verification against trust anchor

### Privacy

- Public API only exposes:
  - Text preview (first 200 characters)
  - Document metadata (title, author, org)
  - C2PA manifest URL (not content)
  - License information
- Full text content is NOT exposed publicly

## Performance

### Encoding
- Small documents (<1000 words): 100-200ms
- Medium documents (1000-10000 words): 300ms-1s
- Large documents (>10000 words): 1-5s

### Verification
- Signature verification: <10ms
- Database lookup: 10-20ms
- **Total: <100ms** ✅

## Testing

```bash
cd enterprise_api
uv run pytest tests/test_embedding_service_invisible.py -v
uv run pytest tests/test_embedding_api.py -v
```

## Related Files

- **Service:** `app/services/embedding_service.py`
- **Executor:** `app/services/embedding_executor.py`
- **Schemas:** `app/schemas/embeddings.py`
- **Tests:** `tests/test_embedding_service_invisible.py`
- **Package:** `encypher-ai` (C2PA text manifest wrapper)
