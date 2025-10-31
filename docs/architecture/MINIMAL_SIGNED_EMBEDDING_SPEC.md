# Minimal Signed Embedding Specification

**Date:** October 30, 2025  
**Status:** Technical Specification  
**Purpose:** Compressed, portable content authentication markers

---

## Executive Summary

Design for **minimal signed embeddings** that:
- ✅ Travel with text (portable)
- ✅ Enable third-party verification without API keys
- ✅ Reference our database for full metadata (C2PA manifest, license, etc.)
- ✅ Support future web scraping/monitoring partnerships
- ✅ Maximum compression (smallest possible footprint)

---

## Optimal Design: Compact Signed Reference

### Embedding Format (28 bytes)

```
ency:v1/a3f9c2e1/8k3mP9xQ
```

**Components:**
- `ency:` - Protocol identifier (5 bytes)
- `v1/` - Version (3 bytes)
- `a3f9c2e1` - Compact reference ID (8 bytes hex = 4 bytes binary)
- `8k3mP9xQ` - Compact HMAC signature (8 bytes hex = 4 bytes binary)

**Total: 28 characters = 28 bytes**

### Why This Design?

1. **Minimal size** - Only 28 bytes vs 80+ for UUID-based approaches
2. **Self-contained** - Includes verification signature
3. **URL-safe** - Can be used in URLs, HTML attributes, etc.
4. **Version-aware** - Can evolve format over time
5. **Human-readable** - Easy to spot and extract

---

## Database Schema

```sql
CREATE TABLE content_references (
    ref_id BIGINT PRIMARY KEY,
    merkle_root_id UUID NOT NULL REFERENCES merkle_roots(root_id) ON DELETE CASCADE,
    leaf_hash VARCHAR(64) NOT NULL,
    leaf_index INTEGER NOT NULL,
    
    organization_id VARCHAR(255) NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    document_id VARCHAR(255) NOT NULL,
    
    text_content TEXT,
    text_preview VARCHAR(200),
    
    c2pa_manifest_url VARCHAR(500),
    c2pa_manifest_hash VARCHAR(64),
    license_type VARCHAR(100),
    license_url VARCHAR(500),
    
    signature_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    embedding_metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_content_refs_ref_id ON content_references(ref_id);
CREATE INDEX idx_content_refs_leaf_hash ON content_references(leaf_hash);
CREATE INDEX idx_content_refs_org_doc ON content_references(organization_id, document_id);
```

---

## Embedding Methods

### HTML (Recommended)
```html
<p data-encypher="v1/a3f9c2e1/8k3mP9xQ">
    Breaking news: AI advances in 2025...
</p>
```

### Markdown
```markdown
Breaking news: AI advances in 2025...
[ency:v1/a3f9c2e1/8k3mP9xQ]: # 
```

### Plain Text
```
Breaking news: AI advances in 2025... [ency:v1/a3f9c2e1/8k3mP9xQ]
```

---

## Public Verification API

### Verify Reference (No Auth Required)

```http
GET /api/v1/public/verify/a3f9c2e1?signature=8k3mP9xQ
```

**Response:**
```json
{
    "valid": true,
    "ref_id": "a3f9c2e1",
    "content": {
        "text_preview": "Breaking news: AI advances in 2025...",
        "leaf_hash": "def456..."
    },
    "document": {
        "document_id": "article_001",
        "title": "AI Breakthrough 2025",
        "author": "John Doe",
        "organization": "TechNews Corp"
    },
    "c2pa": {
        "manifest_url": "https://api.encypher.ai/manifests/xyz789",
        "verified": true
    },
    "licensing": {
        "license_type": "All Rights Reserved",
        "contact_email": "licensing@technews.com"
    },
    "verification_url": "https://verify.encypher.ai/a3f9c2e1"
}
```

---

## Encoding Workflow

### API: Encode with Embeddings

```http
POST /api/v1/enterprise/merkle/encode-with-embeddings
Authorization: Bearer {api_key}

{
    "document_id": "article_001",
    "text": "Full article text...",
    "segmentation_level": "sentence",
    "c2pa_manifest_url": "https://...",
    "license": {
        "type": "All Rights Reserved",
        "contact_email": "licensing@technews.com"
    },
    "embedding_options": {
        "format": "html",
        "method": "data-attribute"
    }
}
```

**Response:**
```json
{
    "success": true,
    "merkle_tree": {
        "root_hash": "abc123...",
        "total_leaves": 42
    },
    "embeddings": [
        {
            "leaf_index": 0,
            "text": "Breaking news...",
            "embedding": "ency:v1/a3f9c2e1/8k3mP9xQ",
            "verification_url": "https://verify.encypher.ai/a3f9c2e1"
        }
    ],
    "embedded_content": "<p data-encypher=\"v1/a3f9c2e1/8k3mP9xQ\">Breaking news...</p>"
}
```

---

## Web Scraping Partner Integration

### Partner Reports Findings

```http
POST /api/v1/partner/report-findings
Authorization: Bearer {partner_api_key}

{
    "findings": [
        {
            "ref_id": "a3f9c2e1",
            "found_url": "https://competitor.com/stolen-article",
            "found_at": "2025-10-30T16:45:00Z",
            "screenshot_url": "https://partner.com/screenshots/abc123.png"
        }
    ]
}
```

### Organization Views Findings

```http
GET /api/v1/enterprise/embeddings/findings
Authorization: Bearer {org_api_key}
```

**Response:**
```json
{
    "findings": [
        {
            "ref_id": "a3f9c2e1",
            "document_id": "article_001",
            "found_url": "https://competitor.com/stolen-article",
            "status": "unauthorized",
            "actions_available": ["send_dmca", "contact_site"]
        }
    ]
}
```

---

## Implementation Plan

### Phase 1: Core (2 weeks)
- Create `content_references` table
- Implement ref_id generation (64-bit with timestamp + sequence + checksum)
- Implement HMAC-SHA256 signature (8-byte truncated)
- Build `EmbeddingService` class

### Phase 2: APIs (2 weeks)
- `POST /encode-with-embeddings` (authenticated)
- `GET /public/verify/{ref_id}` (public, no auth)
- `POST /partner/report-findings` (partner auth)
- `GET /enterprise/embeddings/findings` (org auth)

### Phase 3: Utilities (1 week)
- HTML embedding utility (BeautifulSoup)
- Markdown embedding utility
- PDF embedding utility (XMP metadata)
- JavaScript extraction library

### Phase 4: Integration (1 week)
- WordPress plugin update
- Browser extension (verification)
- Documentation and examples

**Total: 6 weeks**

---

## Size Impact

For 1000-word article (50 sentences):
- **Embedding size:** 50 × 28 bytes = 1.4KB
- **Database storage:** 50 rows × 500 bytes = 25KB
- **HTML size increase:** 0.3% (negligible)

---

## Security

- **Signature:** HMAC-SHA256 truncated to 8 bytes (2^64 possibilities)
- **Secret key:** Stored in environment, rotated every 90 days
- **Rate limiting:** 1000 requests/hour per IP on public API
- **Privacy:** Public API only exposes preview (200 chars), not full text

---

## Next Steps

1. Review specification with team
2. Get approval for database schema
3. Begin Phase 1 implementation
4. Pilot with 1-2 enterprise customers

