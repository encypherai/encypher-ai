# C2PA Content Signing System

## Overview

The Encypher Enterprise API provides **C2PA-compliant content signing** via a unified endpoint:

| Endpoint | Tier | Description |
|----------|------|-------------|
| `POST /api/v1/sign` | All (features gated) | Unified signing with optional advanced features |
| `POST /api/v1/sign/advanced` | - | ⚠️ **DEPRECATED** - Returns 410 Gone. Use `/sign` with `options` instead |

The unified `/sign` endpoint uses the `encypher-ai` package to embed **invisible C2PA manifests** using Unicode variation selectors. Advanced features (sentence segmentation, Merkle trees, etc.) are enabled via the `options` parameter and gated by tier.

## How Signing Works

### `/sign` - Document-Level Signing (All Tiers)

Embeds a **single C2PA manifest** into the document:

1. Load organization's **pre-existing** Ed25519 private key
2. Create C2PA manifest with metadata, assertions, and digital signature
3. Embed manifest at a **single point** using Unicode variation selectors
4. Store document record in database
5. Return signed text

**Use case:** Simple content authentication for articles, blog posts, AI outputs.

### `/sign` with `options` - Advanced Signing (Professional+)

The unified `/sign` endpoint supports advanced features via the `options` parameter:

```json
{
  "text": "Your content...",
  "options": {
    "segmentation_level": "sentence",
    "manifest_mode": "minimal_uuid",
    "index_for_attribution": true
  }
}
```

Creates **per-sentence embeddings** with Merkle tree integration:

1. Parse document into sentences
2. Build Merkle tree from sentence hashes
3. Sign each sentence with organization's **pre-existing** Ed25519 key
4. Embed manifest at a **single point per sentence**
5. Store each sentence in `content_references` table
6. Return embedded content with Merkle tree info

**Use case:** Granular plagiarism detection, sentence-level attribution, quote verification.

**Note:** The legacy `/sign/advanced` endpoint is deprecated and returns 410 Gone.

## Key Management

| User Type | Signing Key |
|-----------|-------------|
| **Free/Starter users** | Encypher demo key (shared) |
| **Professional+ (BYOK)** | Organization's own Ed25519 key pair |

**Note:** Free users currently use a shared demo key. A future enhancement would be to obtain a root CA certificate for Encypher to sign free user content with proper PKI chain.

## Invisible Embedding Technology

Both endpoints use **Unicode variation selectors** to embed manifests invisibly:

- **Single-point embedding** - Manifest embedded at one location in the text
- **Invisible** - Rendering engines display only the base character
- **Standards-compliant** - Using Unicode variation selectors as designed
- **Portable** - Preserved during copy/paste operations

The `encypher-ai` package handles the low-level embedding using the C2PA Text Manifest specification.

## Architecture

```
┌─────────────────┐
│  Content Owner  │
└────────┬────────┘
         │ 1. Submit document
         ▼
┌─────────────────────────────────────┐
│  Enterprise API                     │
│                                     │
│  /sign          → Document manifest │
│  /sign/advanced → Per-sentence +    │
│                   Merkle tree       │
└────────┬────────────────────────────┘
         │ 2. Returns signed content
         ▼
┌─────────────────┐
│  Published      │
│  Content        │
│  (invisible     │
│   C2PA manifest)│
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
│  Verification API                   │
│  POST /api/v1/verify                │
│                                     │
│  Returns: signer, validity, tamper  │
│           detection, metadata       │
└─────────────────────────────────────┘
```

## API Endpoints

### Sign with Advanced Embeddings

**Endpoint:** `POST /api/v1/sign` (with `options`)  
**Auth:** Required (API key)  
**Tier:** Professional+ (for advanced options)

**Request:**
```json
{
  "text": "Full article text...",
  "document_id": "article_001",
  "options": {
    "segmentation_level": "sentence",
    "manifest_mode": "minimal_uuid"
  },
  "rights": {
    "license_type": "All Rights Reserved",
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

### Verify Advanced

**Endpoint:** `POST /api/v1/verify/advanced`  
**Auth:** Required (API key)

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
  "data": {
    "valid": true,
    "embeddings_found": true,
    "signer_id": "org_technews",
    "signer_name": "TechNews Corp"
  }
}
```

**Note:** The legacy `/api/v1/public/extract-and-verify` endpoint is deprecated and returns 410 Gone.

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
