# PRD: Minimal Signed Embeddings System

**Status:** Draft  
**Priority:** High  
**Target Release:** Q1 2026  
**Owner:** Engineering Team

---

## Problem Statement

Publishers need a way to **protect their content at the sentence level** with proof that travels with the text when copied. Current Merkle tree system requires content submission for verification (reactive). We need **proactive protection** via minimal signed embeddings that:

1. Travel with content when copied/scraped
2. Enable third-party verification without API keys
3. Link to our database for full metadata (C2PA manifest, licensing)
4. Support future web scraping partnerships for plagiarism detection

---

## Goals

### Primary Goals
- ✅ Create **minimal signed embeddings** (target: <30 bytes per sentence)
- ✅ Enable **public verification API** (no authentication required)
- ✅ Maintain **existing Merkle tree system** (hybrid approach)
- ✅ Support **web scraping partner integration** for monitoring

### Success Metrics
- Embedding size: <30 bytes per sentence
- Verification API response time: <100ms
- Public API uptime: 99.9%
- Partner integration: 1+ scraping partner by Q2 2026

---

## Solution Overview

### Architecture: Hybrid System

```
Content Creation
    ↓
1. Build Merkle Tree (existing) → Store in DB
    ↓
2. Generate Minimal Embeddings (new) → Store references
    ↓
3. Embed in Content → Publish with markers
    ↓
Verification: Extract embedding → Verify signature → Query DB
```

### Embedding Format

```
ency:v1/a3f9c2e1/8k3mP9xQ
```

- **Size:** 28 bytes
- **Components:** protocol + version + ref_id (8 hex) + signature (8 hex)
- **Verification:** HMAC-SHA256 signature (truncated to 8 bytes)

---

## Technical Specification

### Database Schema

```sql
CREATE TABLE content_references (
    ref_id BIGINT PRIMARY KEY,
    merkle_root_id UUID NOT NULL REFERENCES merkle_roots(root_id),
    leaf_hash VARCHAR(64) NOT NULL,
    leaf_index INTEGER NOT NULL,
    organization_id VARCHAR(255) NOT NULL,
    document_id VARCHAR(255) NOT NULL,
    text_content TEXT,
    text_preview VARCHAR(200),
    c2pa_manifest_url VARCHAR(500),
    license_type VARCHAR(100),
    license_url VARCHAR(500),
    signature_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### API Endpoints

#### 1. Encode with Embeddings (Authenticated)
```http
POST /api/v1/enterprise/merkle/encode-with-embeddings
Authorization: Bearer {api_key}

Request:
{
    "document_id": "article_001",
    "text": "Full article...",
    "segmentation_level": "sentence",
    "c2pa_manifest_url": "https://...",
    "license": {...},
    "embedding_options": {
        "format": "html",
        "method": "data-attribute"
    }
}

Response:
{
    "merkle_tree": {...},
    "embeddings": [{...}],
    "embedded_content": "<p data-encypher=\"...\">..."
}
```

#### 2. Public Verification (No Auth)
```http
GET /api/v1/public/verify/{ref_id}?signature={signature}

Response:
{
    "valid": true,
    "content": {...},
    "document": {...},
    "c2pa": {...},
    "licensing": {...}
}
```

#### 3. Partner Findings Report (Partner Auth)
```http
POST /api/v1/partner/report-findings
Authorization: Bearer {partner_api_key}

Request:
{
    "findings": [{
        "ref_id": "a3f9c2e1",
        "found_url": "https://...",
        "found_at": "2025-10-30T16:45:00Z"
    }]
}
```

#### 4. Organization Findings Dashboard (Org Auth)
```http
GET /api/v1/enterprise/embeddings/findings
Authorization: Bearer {org_api_key}

Response:
{
    "findings": [{
        "ref_id": "a3f9c2e1",
        "document_id": "article_001",
        "found_url": "https://...",
        "status": "unauthorized"
    }]
}
```

---

## Implementation Plan

### Phase 1: Core Infrastructure (2 weeks)

**Tasks:**
- [ ] Create `content_references` table migration
- [ ] Implement ref_id generation algorithm (64-bit: timestamp + sequence + random + checksum)
- [ ] Implement HMAC-SHA256 signature service
- [ ] Build `EmbeddingService` class
- [ ] Secret key management (environment variable + rotation strategy)
- [ ] Unit tests (>90% coverage)

**Deliverables:**
- Database migration file
- `app/services/embedding_service.py`
- `app/models/content_reference.py`
- Test suite

### Phase 2: API Endpoints (2 weeks)

**Tasks:**
- [ ] Implement `POST /encode-with-embeddings` endpoint
- [ ] Implement `GET /public/verify/{ref_id}` endpoint (no auth)
- [ ] Implement `POST /partner/report-findings` endpoint
- [ ] Implement `GET /enterprise/embeddings/findings` endpoint
- [ ] Rate limiting on public API (1000 req/hour per IP)
- [ ] OpenAPI documentation
- [ ] Integration tests

**Deliverables:**
- `app/api/v1/endpoints/embeddings.py`
- `app/api/v1/public/verify.py`
- `app/api/v1/partner/findings.py`
- API documentation

### Phase 3: Embedding Utilities (1 week)

**Tasks:**
- [ ] HTML embedding utility (BeautifulSoup)
- [ ] Markdown embedding utility
- [ ] PDF embedding utility (XMP metadata)
- [ ] Plain text embedding utility
- [ ] JavaScript extraction library (for browser extension)
- [ ] Python extraction library (for partners)

**Deliverables:**
- `app/utils/embeddings/html_embedder.py`
- `app/utils/embeddings/markdown_embedder.py`
- `app/utils/embeddings/pdf_embedder.py`
- `encypher-verify.js` (public library)
- `encypher-extract.py` (partner library)

### Phase 4: Integration & Tools (1 week)

**Tasks:**
- [ ] Update WordPress plugin (auto-embed on publish)
- [ ] Create browser extension (detect & verify embeddings)
- [ ] Partner integration guide
- [ ] Example code for web scrapers
- [ ] End-to-end testing
- [ ] Documentation site update

**Deliverables:**
- WordPress plugin v2.0
- Browser extension (Chrome/Firefox)
- Partner integration guide
- Example implementations

**Total Timeline: 6 weeks**

---

## User Stories

### Story 1: Publisher Protects Article
**As a** news publisher  
**I want to** automatically embed protection markers in my articles  
**So that** I can prove authorship when content is copied

**Acceptance Criteria:**
- WordPress plugin embeds markers on publish
- Each sentence gets unique 28-byte marker
- Markers are invisible to readers
- No impact on page load time (<50ms overhead)

### Story 2: Third Party Verifies Content
**As a** reader or fact-checker  
**I want to** verify the authenticity of an article  
**So that** I can trust the source

**Acceptance Criteria:**
- Browser extension detects embedded markers
- Shows verification badge on verified content
- Displays author, publication date, license info
- Works without requiring API key

### Story 3: Organization Monitors Usage
**As a** content owner  
**I want to** see where my content appears online  
**So that** I can enforce copyright and licensing

**Acceptance Criteria:**
- Dashboard shows all detected uses
- Filters: authorized vs unauthorized
- Actions: send DMCA, contact site, ignore
- Email alerts for unauthorized use

### Story 4: Scraping Partner Reports Findings
**As a** web scraping partner  
**I want to** report discovered markers to Encypher  
**So that** organizations can monitor their content

**Acceptance Criteria:**
- Partner API accepts batch findings
- Validates partner authentication
- Notifies organizations of findings
- Returns acknowledgment with statistics

---

## Technical Considerations

### Security

**Signature Security:**
- HMAC-SHA256 with 8-byte truncation (2^64 possibilities)
- Secret key stored in environment (AWS Secrets Manager in production)
- Key rotation every 90 days (old keys kept for verification)
- Rate limiting: 1000 requests/hour per IP on public API

**Privacy:**
- Public API only exposes: title, author, org, text preview (200 chars)
- Full text content NOT exposed
- Internal document IDs mapped to public IDs

### Performance

**Encoding:**
- Current Merkle tree: 100-200ms for 1000-word article
- Additional embedding generation: +50ms
- Total: 150-250ms (acceptable)

**Verification:**
- Signature verification: <5ms (local HMAC check)
- Database lookup: 10-20ms (indexed query)
- Total: <100ms (target met)

**Storage:**
- Per document (50 sentences): +25KB in database
- HTML size increase: +1.4KB (0.3% for typical article)

### Scalability

**Database:**
- Indexed on ref_id (primary key)
- Indexed on leaf_hash (for reverse lookup)
- Partitioning strategy: by organization_id (future)

**API:**
- Public verification API: CDN caching (5 min TTL)
- Rate limiting: Redis-based
- Horizontal scaling: stateless design

---

## Dependencies

### Internal
- ✅ Merkle tree system (already implemented)
- ✅ Organization/API key system (already implemented)
- ⚠️ C2PA manifest generation (in progress)

### External
- Python libraries: `cryptography`, `beautifulsoup4`, `pypdf`
- JavaScript libraries: None (vanilla JS for public library)
- Infrastructure: PostgreSQL, Redis (rate limiting)

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Embeddings removed by attackers | High | Medium | Multiple embedding methods, steganography option |
| Secret key compromise | Critical | Low | HSM in production, key rotation, audit logs |
| Public API abuse | Medium | Medium | Rate limiting, CAPTCHA for repeated failures |
| Performance degradation | Medium | Low | Caching, database optimization, load testing |
| Partner integration complexity | Low | Medium | Clear documentation, example code, support |

---

## Success Criteria

### Launch Criteria (MVP)
- [ ] All Phase 1-4 tasks complete
- [ ] 100+ unit tests passing
- [ ] 20+ integration tests passing
- [ ] Load testing: 1000 req/sec on public API
- [ ] Security audit complete
- [ ] Documentation complete

### Post-Launch Metrics (3 months)
- **Adoption:** 10+ enterprise organizations using embeddings
- **Volume:** 10,000+ documents encoded with embeddings
- **Verification:** 100,000+ public API verification requests
- **Partners:** 1+ scraping partner integrated
- **Performance:** <100ms p95 verification latency
- **Uptime:** 99.9% public API availability

---

## Open Questions

1. **Key rotation strategy:** How to handle verification of old signatures after key rotation?
   - **Answer:** Keep key history table, verify against all valid keys

2. **Embedding removal:** What if sophisticated attackers strip all embeddings?
   - **Answer:** Merkle tree DB still provides proof, embeddings are additional layer

3. **International content:** How to handle non-English text segmentation?
   - **Answer:** spaCy supports 60+ languages, use appropriate model

4. **Legal validity:** Are embedded signatures legally binding?
   - **Answer:** Consult legal team, likely need blockchain anchoring for legal cases

5. **Partner revenue model:** How to monetize scraping partner relationships?
   - **Answer:** Revenue share on enforcement actions, or flat fee per finding

---

## Future Enhancements (Post-MVP)

### Phase 5: Advanced Features
- Steganographic embedding (invisible in images)
- Blockchain anchoring for legal proof
- Machine learning for paraphrase detection
- Multi-language support (60+ languages)

### Phase 6: Enterprise Features
- White-label verification portal
- Custom branding for verification badges
- Advanced analytics dashboard
- Automated DMCA takedown service

### Phase 7: Ecosystem
- Publisher network (cross-verify content)
- Content marketplace (license tracking)
- Attribution API for AI training datasets
- Academic citation verification

---

## Appendix

### Example Embedding in HTML

```html
<!DOCTYPE html>
<html>
<head>
    <title>AI Breakthrough 2025</title>
</head>
<body>
    <article>
        <h1>AI Breakthrough 2025</h1>
        <p data-encypher="v1/a3f9c2e1/8k3mP9xQ">
            Breaking news: AI advances in 2025 with new breakthrough 
            in quantum computing that promises to revolutionize the field.
        </p>
        <p data-encypher="v1/b4g8d3f2/9m4nQ0yR">
            Researchers at MIT announced today that they have successfully 
            demonstrated a quantum algorithm that outperforms classical 
            computers by a factor of 1000x.
        </p>
    </article>
</body>
</html>
```

### Example Verification Response

```json
{
    "valid": true,
    "ref_id": "a3f9c2e1",
    "verified_at": "2025-10-30T17:22:00Z",
    "content": {
        "text_preview": "Breaking news: AI advances in 2025 with new breakthrough...",
        "leaf_hash": "def456abc...",
        "leaf_index": 0
    },
    "document": {
        "document_id": "article_001",
        "title": "AI Breakthrough 2025",
        "published_at": "2025-10-30T12:00:00Z",
        "author": "John Doe",
        "organization": "TechNews Corp"
    },
    "merkle_proof": {
        "root_hash": "abc123def...",
        "verified": true
    },
    "c2pa": {
        "manifest_url": "https://api.encypher.ai/manifests/xyz789",
        "manifest_hash": "789xyz...",
        "verified": true
    },
    "licensing": {
        "license_type": "All Rights Reserved",
        "license_url": "https://technews.com/license",
        "contact_email": "licensing@technews.com"
    },
    "verification_url": "https://verify.encypher.ai/a3f9c2e1"
}
```

---

**Next Steps:**
1. Review PRD with stakeholders
2. Get approval for 6-week timeline
3. Assign engineering resources
4. Begin Phase 1 implementation

**Status:** Ready for review  
**Last Updated:** October 30, 2025
