# CDN Content Provenance Worker

**Status:** Planning
**Current Goal:** Architecture finalized, implementation not started

## Overview

Expand Encypher's existing CDN edge workers (Cloudflare, Lambda@Edge, Fastly Compute) from image-only header injection to full HTML content signing with meta tag injection. A publisher adds one DNS record or route rule. The worker intercepts HTML responses at the edge, extracts article text, calls Encypher's public signing API, and injects `<meta name="c2pa-manifest-url">` into the response. No CMS changes, no code changes, no publisher-side development.

This is the primary publisher adoption mechanism. The CDN worker creates provenance; downstream consumers (Prebid RTD module, Chrome extension, verification widget) read it.

## Objectives

- Sign HTML article content at the CDN edge with zero publisher code changes
- Inject `<meta name="c2pa-manifest-url">` tag so downstream systems (Prebid, extensions, crawlers) can discover provenance
- Maintain notarization model: Encypher signs as attester ("published here at this time"), not as author or copyright holder
- Unify image and HTML signing in a single worker deployment per CDN platform
- Cross-channel org resolution: share a single org and quota pool when a publisher uses both CDN and Prebid channels
- Free tier (1,000 unique signs/month per domain) gates toward Enterprise conversion
- Optional rights profile on-ramp: publishers who want licensing metadata can link a PublisherRightsProfile after adoption

## Architecture

### Data Flow

```
Publisher DNS/Route -> CDN Edge (Worker) -> Origin Server
                         |
                         v
                    Response Content-Type?
                     /              \
                   text/html         image/*
                    |                  |
                    v                  v
              Already has             Existing image
              <meta c2pa-*>?          header flow
               /        \            (unchanged)
             Yes         No
              |           |
              v           v
           Pass through   Extract text (regex)
                          |
                          v
                    POST /api/v1/public/cdn/sign
                    (KV/cache dedup first)
                          |
                          v
                    Inject <meta name="c2pa-manifest-url"
                           content="https://...">
                    before </head>
                          |
                          v
                    Return modified HTML
```

### IP Ownership Model

C2PA Section A.7 authenticates a document as published, not copyright ownership over every word. A news article may contain public quotes, wire service content, government data, and facts that are not copyrightable. The C2PA manifest attests: "this document was published at {url} by {entity} on {date} with content hash {hash}." This is provenance, not a rights claim.

The signing API accepts the full extracted text and hashes it. The hash is stored; the text is not. The manifest URL points to metadata about the signing event, not the content itself.

For publishers who want to express licensing and rights metadata (e.g., "this content is licensed under AP Terms of Service" or "original reporting, all rights reserved"), Encypher's PublisherRightsProfile system provides an opt-in on-ramp after initial CDN adoption. This is not required for basic provenance signing.

### Backend Architecture

A dedicated endpoint keeps CDN analytics, quota, and rate limiting separate from the Prebid channel while sharing the signing infrastructure.

**Endpoint:** `POST /api/v1/public/cdn/sign`

```
Request:
{
  "text": "extracted article text (50-char min)",
  "page_url": "https://publisher.com/article/slug",
  "document_title": "Article Title" (optional)
}

Response:
{
  "success": true,
  "manifest_url": "https://api.encypher.com/api/v1/public/cdn/manifest/{uuid}",
  "signer_tier": "encypher_free",
  "signed_at": "2026-04-01T10:00:00Z",
  "content_hash": "sha256:abc123...",
  "org_id": "org_cdn_abc123def456",
  "cached": false
}
```

**Org provisioning with cross-channel resolution:**

```
Domain: nytimes.com
  1. Check for org_prebid_{sha256("nytimes.com")[:12]}  (Prebid channel)
  2. Check for org_cdn_{sha256("nytimes.com")[:12]}     (CDN channel)
  3. Check for org with domain="nytimes.com"             (dashboard-claimed)
  4. If any found: reuse that org (share quota)
  5. If none: create org_cdn_{hash} (free tier, 1,000/month)
```

**DB model:** `cdn_content_records` (parallel to `prebid_content_records`)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| organization_id | String(64) | FK to organizations |
| domain | String(255) | Publisher eTLD+1 |
| canonical_url | Text | Full page URL |
| content_hash | String(71) | "sha256:" + 64 hex |
| manifest_store | JSONB | C2PA signing result metadata |
| manifest_url | Text | Public manifest endpoint URL |
| page_title | String(500) | Optional |
| signer_tier | String(32) | "encypher_free" default |
| signed_at | Timestamp | When content was signed |
| created_at | Timestamp | Row creation |

Unique constraint on `(domain, content_hash)`. Index on `organization_id`.

### Edge Worker Architecture

**Text extraction (portable across all CDN platforms):**

Workers and Lambda@Edge do not have a DOM parser. Text extraction uses regex:
1. Find `<script type="application/ld+json">` blocks, parse JSON, extract `articleBody` from `NewsArticle` or `Article` schema
2. Fallback: extract text between `<article>` and `</article>` tags, strip HTML tags via regex
3. Fallback: extract text between `<main>` or `[role="main"]` tags
4. Apply 50-char floor filter (skip navigation-only pages)
5. Truncate at 50KB ceiling

**Meta tag injection:**

String replace `</head>` with `<meta name="c2pa-manifest-url" content="{url}">\n</head>`. If `</head>` is not found, skip injection (malformed HTML, fail-open).

**Skip conditions (do not sign):**
- Response already contains `<meta name="c2pa-manifest-url"` (CMS already signed)
- Content-Type is not `text/html`
- Response status is not 200
- Extracted text is below 50-char floor
- KV/cache lookup returns existing manifest for this domain + content hash

**Cloudflare-specific:** `HTMLRewriter` is available for meta tag injection as an alternative to string replace. It handles edge cases (multiple `</head>`, case variations) more robustly. Use `HTMLRewriter` for injection, regex for extraction.

**Lambda@Edge-specific:** Must use origin-response trigger, not viewer-response. Viewer-response cannot modify the response body (size limit: 40KB for viewer-response, 1MB for origin-response). Origin-response is invoked after the cache miss to origin, which is the correct point to inject the meta tag.

### Caching Strategy

**Edge-side (KV/cache per CDN platform):**
- Key: `cdn_content:{domain}:{sha256(text)[:16]}`
- Value: manifest URL string
- TTL: 1 hour (short, since article content can update)
- Negative cache: `NOT_FOUND` with 5-minute TTL

**Server-side (DB dedup):**
- Same pattern as Prebid: unique constraint on `(domain, content_hash)` in `cdn_content_records`
- Duplicate requests return existing manifest, no quota charge

### Rate Limiting

- IP-based: 60 requests/minute per worker IP (edge IPs are limited, so this is generous)
- Domain-based: 100 requests/hour per domain (prevents runaway pageview loops from misconfigured workers)
- Quota: 1,000 unique signs/month per org (deduped by content_hash)

## Tasks

### 1.0 Backend -- CDN Content Signing Endpoint

- [ ] 1.1 Add `cdn_content_records` DB model (`app/models/cdn_content_record.py`)
  - [ ] 1.1.1 Fields mirror `prebid_content_records`: id, org_id, domain, canonical_url, content_hash, manifest_store, manifest_url, page_title, signer_tier, signed_at, created_at
  - [ ] 1.1.2 Unique constraint on (domain, content_hash), index on organization_id
- [ ] 1.2 Alembic migration for `cdn_content_records` table
- [ ] 1.3 Add `cdn_content_schemas.py` (Pydantic request/response models)
  - [ ] 1.3.1 `CdnContentSignRequest`: text (min 50 chars), page_url (required), document_title (optional)
  - [ ] 1.3.2 `CdnContentSignResponse`: success, manifest_url, signer_tier, signed_at, content_hash, org_id, cached, error, upgrade_url
- [ ] 1.4 Add `cdn_content_signing_service.py`
  - [ ] 1.4.1 `sign_or_retrieve()` -- main entry point (same pattern as `prebid_signing_service.py`)
  - [ ] 1.4.2 `_ensure_cdn_org(db, domain)` -- cross-channel org resolution (check prebid, cdn, dashboard orgs)
  - [ ] 1.4.3 Content dedup via `cdn_content_records`
  - [ ] 1.4.4 Quota check and increment (reuse existing quota pattern)
  - [ ] 1.4.5 Sign via `execute_unified_signing` (managed signer, claim_generator: "Encypher CDN Provenance/1.0")
- [ ] 1.5 Add `app/api/v1/public/cdn_content.py` router
  - [ ] 1.5.1 `POST /api/v1/public/cdn/sign` -- public, no auth, rate-limited
  - [ ] 1.5.2 `GET /api/v1/public/cdn/manifest/{record_id}` -- public manifest retrieval with CORS
  - [ ] 1.5.3 `GET /api/v1/public/cdn/status/{domain}` -- domain signing stats
- [ ] 1.6 Register router in `app/api/v1/api.py`
- [ ] 1.7 Add `cdn_content_sign` rate limiter entry in `public_rate_limiter.py`

### 2.0 Cloudflare Worker -- HTML Content Signing

- [ ] 2.1 Add HTML content type detection to `cdn-provenance-worker.js`
- [ ] 2.2 Implement regex-based text extraction (JSON-LD > article > main)
- [ ] 2.3 Add KV cache check before API call (domain + content hash key)
- [ ] 2.4 Implement `HTMLRewriter`-based meta tag injection
- [ ] 2.5 Add skip conditions: existing meta tag, non-200 status, short content
- [ ] 2.6 Add `text/html` to fetch handler dispatch alongside existing image flow
- [ ] 2.7 Update wrangler.toml environment bindings if needed

### 3.0 Lambda@Edge -- HTML Content Signing

- [ ] 3.1 Switch trigger from viewer-response to origin-response (if not already)
- [ ] 3.2 Add HTML content type detection to `cdn-provenance-handler.mjs`
- [ ] 3.3 Port text extraction logic from Cloudflare worker
- [ ] 3.4 Implement string-replace meta tag injection (no HTMLRewriter available)
- [ ] 3.5 Add DynamoDB or ElastiCache lookup for dedup (Lambda has no KV equivalent)
- [ ] 3.6 Update CloudFormation/SAM template for origin-response trigger

### 4.0 Fastly Compute -- HTML Content Signing

- [ ] 4.1 Add HTML content type detection to Rust handler
- [ ] 4.2 Port text extraction logic to Rust (regex crate)
- [ ] 4.3 Implement string-replace meta tag injection
- [ ] 4.4 Add Fastly KV Store lookup for dedup
- [ ] 4.5 Update `Cargo.toml` dependencies if needed

### 5.0 Cross-Channel Org Resolution

- [ ] 5.1 Extract shared `_resolve_publisher_org(db, domain)` utility
  - [ ] 5.1.1 Check `org_prebid_{hash}`, `org_cdn_{hash}`, and dashboard-claimed orgs
  - [ ] 5.1.2 Return existing org if found, create new `org_cdn_{hash}` if not
- [ ] 5.2 Refactor `prebid_signing_service._ensure_prebid_org` to use shared resolver
- [ ] 5.3 Shared quota: when org is resolved across channels, `documents_signed` counter is shared

### 6.0 Rights On-Ramp (Optional, Post-Adoption)

- [ ] 6.1 Add `rights_profile_id` nullable FK to `cdn_content_records` and `prebid_content_records`
- [ ] 6.2 If publisher has linked a PublisherRightsProfile, include rights metadata in manifest
- [ ] 6.3 Dashboard UI: "Link rights profile to CDN signing" in org settings
- [ ] 6.4 Document the on-ramp in publisher setup guide

### 7.0 Testing

- [ ] 7.1 Backend unit + integration tests (`test_cdn_content_signing.py`)
  - [ ] 7.1.1 Service utilities: domain extraction, hash, org ID generation
  - [ ] 7.1.2 POST /sign: new content, dedup, validation, rate limiting
  - [ ] 7.1.3 GET /manifest: returns signed record, 404 for unknown
  - [ ] 7.1.4 GET /status: provisioned and unprovisioned domains
  - [ ] 7.1.5 Cross-channel org resolution: CDN finds existing Prebid org
- [ ] 7.2 Cloudflare Worker tests
  - [ ] 7.2.1 HTML detection and text extraction (JSON-LD, article, main)
  - [ ] 7.2.2 Meta tag injection (normal, already present, no </head>)
  - [ ] 7.2.3 Image passthrough unchanged
  - [ ] 7.2.4 KV cache hit/miss behavior
- [ ] 7.3 Lambda@Edge tests
  - [ ] 7.3.1 Origin-response trigger behavior
  - [ ] 7.3.2 Text extraction and injection
  - [ ] 7.3.3 Body size handling (under 1MB limit)
- [ ] 7.4 Fastly Compute tests
  - [ ] 7.4.1 Rust handler text extraction and injection
  - [ ] 7.4.2 KV Store dedup behavior

### 8.0 Documentation

- [ ] 8.1 Cloudflare setup guide (DNS route, worker deployment, KV namespace)
- [ ] 8.2 Lambda@Edge setup guide (CloudFront distribution, function association)
- [ ] 8.3 Fastly setup guide (Compute service, KV Store config)
- [ ] 8.4 API reference for `/api/v1/public/cdn/sign`, `/manifest`, `/status`
- [ ] 8.5 Publisher FAQ: what is signed, what is stored, IP ownership, rights on-ramp

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Separate endpoint | `/api/v1/public/cdn/sign` not `/prebid/sign` | Separate quota pools, analytics, rate limits. Different usage patterns (CDN = every pageview, Prebid = auction-time). |
| Cross-channel org | Check all org namespaces before creating | Publisher who adopts CDN then Prebid (or vice versa) should share one org and quota pool. |
| Text extraction | Regex, not DOM parser | Workers/Lambda have no DOM. Regex is portable across all three CDN platforms. |
| Meta tag injection | `HTMLRewriter` (Cloudflare), string replace (others) | `HTMLRewriter` handles edge cases better but is Cloudflare-only. String replace is portable. |
| Unified worker | One deployment handles images + HTML | Simpler ops. Publisher installs one worker, gets both image headers and HTML meta tags. |
| IP ownership | Attestation, not copyright | C2PA Section A.7: document-level provenance. "Published here at this time." Publisher rights are a separate, opt-in layer. |
| Rights on-ramp | Basic signing first, rights opt-in later | Minimizes adoption friction. Publishers who care about licensing metadata can add it after they see value from basic provenance. |
| Lambda trigger | Origin-response, not viewer-response | Viewer-response body limit is 40KB. Origin-response allows up to 1MB body modification. |

## Success Criteria

- Cloudflare Worker signs HTML content and injects meta tag on first request, serves from KV cache on subsequent requests
- Lambda@Edge and Fastly workers achieve feature parity with Cloudflare
- Backend handles 100 req/sec sustained on the CDN signing endpoint
- Cross-channel org resolution correctly shares quota between CDN and Prebid channels
- Existing meta tag detection prevents double-signing
- Image header injection continues to work unchanged after worker unification
- Publisher setup requires only a DNS record or CDN route rule (zero code changes)

## Phasing

**Phase 1 (Backend + Cloudflare):** Tasks 1.0, 2.0, 7.1, 7.2
- New backend endpoint, service, model, tests
- Cloudflare Worker extended for HTML
- This phase alone delivers the primary publisher adoption mechanism

**Phase 2 (Multi-CDN + Cross-Channel):** Tasks 3.0, 4.0, 5.0, 7.3, 7.4
- Lambda@Edge and Fastly workers
- Cross-channel org resolution
- Shared quota across CDN and Prebid channels

**Phase 3 (Rights On-Ramp + Docs):** Tasks 6.0, 8.0
- Optional rights profile linkage
- Setup guides for all three CDN platforms

## Completion Notes

(Filled when PRD is complete.)
