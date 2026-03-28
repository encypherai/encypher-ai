# Prebid C2PA Auto-Provenance Distribution

**Status:** Planning
**Current Goal:** Architecture review and approval

## Overview

Distribute free-tier C2PA text provenance to 70k+ Prebid publisher sites via a lazy signing model. The Prebid RTD module V2 checks for existing provenance on pageload; if absent, it extracts article text, sends it to Encypher's public signing endpoint, caches the manifest URL, and injects provenance signals into OpenRTB bid requests. Encypher auto-provisions one org per domain (1,000 signs/month free tier), manages all certificates (notarization model), and offers S/MIME sub-CA cert issuance as an Enterprise add-on.

This is a supply-side flooding strategy: create enough provenance-verified ad inventory that DSPs begin factoring it into bid decisions, which drives CPM lift, which drives voluntary Enterprise adoption.

## Objectives

- Auto-provision C2PA signing for any Prebid publisher site with zero publisher-side configuration
- Maintain notarization model: Encypher signs as attester ("this content observed at {url} on {date}"), not as author
- Lazy org-per-domain provisioning with media company grouping when ownership is known
- Free tier (1,000 signs/month) naturally gates toward Enterprise conversion for high-volume publishers
- S/MIME sub-CA cert issuance as Enterprise/add-on upgrade (publisher signs under their own identity)
- Never store publisher content -- only hashes, metadata, and C2PA manifests
- Ship as two modules: vendor-neutral RTD reader (upstream to Prebid.org) + Encypher signing companion

## Architecture

### Data Flow

```
Page Load
  |
  v
RTD Module V2 (client-side, in Prebid.js)
  |
  +--> 1. Check <meta name="c2pa-manifest-url"> (WordPress plugin, existing CMS integration)
  |      Found? --> Read manifest, inject site.ext.data.c2pa, done.
  |
  +--> 2. Check localStorage cache for canonical URL
  |      Hit? --> Inject cached manifest_url into site.ext.data.c2pa, done.
  |
  +--> 3. Cache miss: Extract article text from DOM
  |      - Structured data (JSON-LD, schema.org Article.articleBody) preferred
  |      - Fallback: <article> element innerText
  |      - Fallback: Readability-style heuristic
  |
  +--> 4. POST /api/v1/prebid/sign
  |      Body: { domain, canonical_url, text_content, page_title }
  |      No auth required (public endpoint, IP + domain rate-limited)
  |
  v
Prebid Signing Service (server-side, Enterprise API)
  |
  +--> 5. Lookup domain org: org_prebid_{sha256(domain)[:12]}
  |      Not found? --> Auto-provision org (free tier, Encypher-managed cert)
  |
  +--> 6. Check server-side dedup: content_hash + domain
  |      Already signed? --> Return existing manifest_url (no quota charge)
  |
  +--> 7. Check quota (1,000/month for free tier)
  |      Exceeded? --> Return 429 with upgrade_url
  |
  +--> 8. Sign text content (document-level C2PA, notarization model)
  |      - Claim generator: "Encypher Prebid Provenance/1.0"
  |      - Assertions: c2pa.created, source_domain, canonical_url, content_hash
  |      - Cert: Encypher-managed Ed25519 (per-org, self-signed)
  |      - Content NOT stored. Only: hash, manifest, metadata.
  |
  +--> 9. Store manifest at /.well-known/c2pa/manifests/{record_id}
  |
  +--> 10. Return response:
          {
            manifest_url: "https://api.encypher.com/.well-known/c2pa/manifests/{id}",
            signer_tier: "notarized",
            signed_at: "2026-03-27T...",
            action: "c2pa.created",
            org_id: "org_prebid_...",
            upgrade_url: "https://encypher.com/enterprise?ref=prebid&domain=..."
          }
  |
  v
RTD Module V2 (client-side)
  |
  +--> 11. Cache manifest_url in localStorage (key: canonical_url, TTL: 30 days)
  +--> 12. Inject site.ext.data.c2pa into OpenRTB bid request
```

### Signer Identity Model

**Phase 1 (Notarization -- no publisher cooperation required):**
- Signer: "Encypher Prebid Provenance" (Encypher-managed cert)
- signer_tier: "notarized" (new value, distinct from "local"/"connected"/"byok")
- Manifest assertions include source domain and canonical URL
- Encypher attests: "this content was observed at {url} on {date} with hash {hash}"
- Trust level: self_signed (Encypher's per-org cert, no CA chain)

**Phase 2 (Publisher-claimed -- opt-in, Enterprise add-on):**
- Publisher claims their domain via DNS TXT record or dashboard setup
- Encypher issues S/MIME cert under Encypher's sub-CA, with CN = publisher domain
- signer_tier upgrades to "connected" or "byok"
- Trust level: ca_verified (real cert chain)
- Sentence-level, media signing, enforcement tools unlocked

### Org Provisioning Model

- **Default:** One org per eTLD+1 domain (e.g., nytimes.com, not www.nytimes.com)
- **Namespace:** `org_prebid_{sha256(domain)[:12]}` (avoids collision with email-based orgs)
- **Known ownership:** If Encypher knows domain -> media company mapping (e.g., nytimes.com, theathletic.com -> NYT Corp), group under one parent org via `parent_org_id`. Shared quota pool.
- **Lazy creation:** Org provisioned on first signing request for that domain. Uses existing `ON CONFLICT DO NOTHING` pattern.
- **Cert provisioning:** Auto-generated Ed25519 cert on org creation (existing `_ensure_organization_certificate` flow)
- **Tier:** All Prebid-provisioned orgs start at `free` (1,000 signs/month)
- **Upgrade path:** Publisher visits `upgrade_url`, claims domain via dashboard, upgrades to Enterprise

### Content Extraction (Client-Side)

Priority order for article text extraction in RTD module:
1. `JSON-LD` schema.org `Article.articleBody` or `NewsArticle.articleBody`
2. `<meta name="c2pa-text-content">` (future CMS integration hook)
3. `<article>` element `.innerText` (stripped of scripts/styles)
4. `document.querySelector('[role="main"]').innerText`
5. No content found --> skip signing, behave as read-only module

Max text size sent to API: 100KB (covers virtually all articles). Larger content is truncated with a note in the manifest.

### Caching Strategy

**Client-side (localStorage):**
- Key: `c2pa_manifest_{sha256(canonical_url)}`
- Value: `{ manifest_url, signed_at, content_hash }`
- TTL: 30 days
- Invalidation: If extracted content hash differs from cached content_hash, re-sign

**Server-side (DB dedup):**
- Table: `prebid_content_records` (new)
- Unique constraint: `(domain, content_hash)`
- If same content already signed, return existing manifest (no quota charge)
- Manifest stored in `manifest_store` JSONB column (same pattern as `cdn_image_records`)

### Rate Limiting

- IP-based: 60 requests/minute per IP (prevents single-origin abuse)
- Domain-based: 100 requests/hour per domain (prevents runaway pageview loops)
- Quota: 1,000 unique signs/month per org (deduped by content_hash, so re-requests for same content are free)

## Tasks

### 1.0 Enterprise API -- Prebid Signing Service

- [ ] 1.1 Add `prebid_content_records` DB model and Alembic migration
  - [ ] 1.1.1 Fields: id, org_id, domain, canonical_url, content_hash (SHA-256), manifest_store (JSONB), manifest_url, page_title, signed_at, created_at
  - [ ] 1.1.2 Unique constraint on (domain, content_hash)
  - [ ] 1.1.3 Index on domain for org lookup
- [ ] 1.2 Add `prebid_signing_service.py`
  - [ ] 1.2.1 `sign_or_retrieve(domain, canonical_url, text_content, page_title)` -- main entry point
  - [ ] 1.2.2 Domain org lookup/provisioning: `_ensure_prebid_org(domain)` using `org_prebid_{hash}` namespace
  - [ ] 1.2.3 Content dedup: check `prebid_content_records` by (domain, content_hash)
  - [ ] 1.2.4 Quota check via existing `QuotaManager.check_quota`
  - [ ] 1.2.5 Delegate to `execute_unified_signing` with notarization assertions
  - [ ] 1.2.6 Store manifest in `prebid_content_records`
  - [ ] 1.2.7 Return manifest_url + metadata (no content stored)
- [ ] 1.3 Add `prebid_schemas.py`
  - [ ] 1.3.1 `PrebidSignRequest`: domain, canonical_url, text_content, page_title
  - [ ] 1.3.2 `PrebidSignResponse`: manifest_url, signer_tier, signed_at, action, org_id, upgrade_url, cached (bool)
- [ ] 1.4 Add `prebid_router.py` at `/api/v1/prebid/`
  - [ ] 1.4.1 `POST /api/v1/prebid/sign` -- public endpoint, no auth, IP + domain rate-limited
  - [ ] 1.4.2 `GET /api/v1/prebid/status/{domain}` -- public, returns org signing stats (total signed, quota remaining)
  - [ ] 1.4.3 `POST /api/v1/prebid/claim` -- authenticated, publisher claims a Prebid-provisioned domain (links to their real org)
  - [ ] 1.4.4 CORS headers permitting cross-origin requests from any publisher domain
- [ ] 1.5 Add `signer_tier: "notarized"` to claim generator metadata
  - [ ] 1.5.1 Update `c2pa_claim_builder.py` to accept and emit `notarized` tier
  - [ ] 1.5.2 Add `source_domain` and `canonical_url` as custom assertions in manifest
- [ ] 1.6 Register router in `bootstrap/routers.py`
- [ ] 1.7 Add domain-based rate limiter (extend existing `public_rate_limiter`)

### 2.0 Enterprise API -- Domain Ownership & Upgrade Path

- [ ] 2.1 Add `domain` field to `organizations` model (nullable, indexed)
- [ ] 2.2 Add `provisioning_source` field to `organizations` model (enum: manual, prebid, wordpress, api)
- [ ] 2.3 Domain claim flow in `POST /api/v1/prebid/claim`:
  - [ ] 2.3.1 Authenticated publisher provides domain
  - [ ] 2.3.2 Verify domain ownership via DNS TXT record (`_c2pa-verify.{domain} TXT "encypher-org-id={org_id}"`) or meta tag
  - [ ] 2.3.3 Link Prebid-provisioned org to publisher's real org (merge or re-parent)
  - [ ] 2.3.4 Upgrade signer_tier from "notarized" to "connected"
- [ ] 2.4 Domain ownership mapping table for known media companies
  - [ ] 2.4.1 `prebid_domain_ownership` table: domain, parent_org_id, media_company_name
  - [ ] 2.4.2 Seed with known publisher properties (can be manually maintained)

### 3.0 Enterprise API -- S/MIME Sub-CA Cert Issuance (Enterprise Add-On)

- [ ] 3.1 Wire existing `ssl_com_client.py` into org certificate provisioning flow
  - [ ] 3.1.1 CSR generation from org's Ed25519 key
  - [ ] 3.1.2 Submit CSR to SSL.com SWS API (code signing / C2PA signing product)
  - [ ] 3.1.3 Poll/webhook for issuance, download cert chain
  - [ ] 3.1.4 Store in `certificate_pem` + `cert_chain_pem`, flip status to `active`
- [ ] 3.2 Add `add_ons["ca_cert"]` gating (same pattern as BYOK add-on)
- [ ] 3.3 Dashboard UI for cert request/status (Enterprise orgs only)
- [ ] 3.4 Trust level automatically upgrades to `ca_verified` (existing logic)

### 4.0 Prebid.js -- RTD Module V2

- [ ] 4.1 Extend `c2paProvenanceRtdProvider.js` with signing companion logic
  - [ ] 4.1.1 Content extraction: JSON-LD > article element > main role
  - [ ] 4.1.2 localStorage cache layer (key: canonical_url hash, TTL: 30 days)
  - [ ] 4.1.3 Content hash computation (SHA-256 of extracted text, via SubtleCrypto)
  - [ ] 4.1.4 Cache invalidation when content hash changes
  - [ ] 4.1.5 POST to `/api/v1/prebid/sign` on cache miss
  - [ ] 4.1.6 Gated behind `params.enableAutoSign: true` (disabled by default for Prebid.org governance)
- [ ] 4.2 Add `signer_tier: "notarized"` to OpenRTB payload schema
- [ ] 4.3 Update module docs (c2paProvenanceRtdProvider.md) for V2 capabilities
- [ ] 4.4 Update Prebid.org docs site (prebid.github.io) for V2

### 5.0 Prebid.js -- Signing Companion Script (Standalone)

- [ ] 5.1 Create `encypher-prebid-companion.js` -- standalone script for publishers who want auto-signing without building custom Prebid
  - [ ] 5.1.1 Same content extraction logic as 4.1.1
  - [ ] 5.1.2 Same caching logic as 4.1.2-4.1.4
  - [ ] 5.1.3 Injects `<meta name="c2pa-manifest-url">` into DOM after signing
  - [ ] 5.1.4 Existing read-only RTD module picks it up naturally
- [ ] 5.2 Host companion script on Encypher CDN (or npm package)
- [ ] 5.3 One-line install: `<script src="https://cdn.encypher.com/prebid-companion.js" async></script>`

### 6.0 Testing & Validation

- [ ] 6.1 Unit tests for `prebid_signing_service.py` -- pytest
  - [ ] 6.1.1 Org auto-provisioning (new domain, existing domain, known media company)
  - [ ] 6.1.2 Content dedup (same hash returns cached manifest, no quota charge)
  - [ ] 6.1.3 Quota enforcement (1,000 unique signs/month, 429 on exceed)
  - [ ] 6.1.4 Rate limiting (IP + domain)
  - [ ] 6.1.5 Notarization assertions in manifest
- [ ] 6.2 Unit tests for `prebid_router.py` -- pytest
  - [ ] 6.2.1 Public endpoint (no auth), CORS headers
  - [ ] 6.2.2 Domain claim flow with DNS verification
  - [ ] 6.2.3 Status endpoint
- [ ] 6.3 Integration test: full signing flow (POST /prebid/sign -> verify manifest) -- pytest
- [ ] 6.4 RTD module V2 tests -- extend existing 7 tests with auto-signing scenarios
  - [ ] 6.4.1 Cache miss triggers signing
  - [ ] 6.4.2 Cache hit skips signing
  - [ ] 6.4.3 Content hash change triggers re-signing
  - [ ] 6.4.4 enableAutoSign=false skips signing (backward compat)
  - [ ] 6.4.5 Signing failure falls back to no-provenance (graceful degradation)
- [ ] 6.5 Companion script tests
- [ ] 6.6 Load test: simulate 1,000 domains, 100 pages each

### 7.0 Strategy & Distribution

- [ ] 7.1 Validate Prebid.org governance path with Aditude (AI working group)
  - [ ] 7.1.1 Read-only RTD module (V1) -- submit upstream PR
  - [ ] 7.1.2 Auto-signing companion -- determine if bundled (params.enableAutoSign) or separate script
- [ ] 7.2 Seed `prebid_domain_ownership` table with known media company properties
- [ ] 7.3 Update internal strategy docs with Prebid distribution play
- [ ] 7.4 Dashboard: Prebid org view showing domain signing stats and upgrade CTA

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth model | Public endpoint, no API key | Zero-friction distribution. Rate limiting + domain-based quota prevents abuse. |
| Signer identity | Notarization (Encypher signs as attester) | No publisher cooperation needed. Honest C2PA manifest. Upgrade path to publisher-signed via sub-CA. |
| Org namespace | `org_prebid_{hash}` | Avoids collision with email-provisioned orgs. Clear provenance of how org was created. |
| Content storage | Never stored. Hash + manifest only. | Legal, privacy, storage cost. Content hash sufficient for dedup and verification. |
| Module architecture | Two modules (reader + companion) | Prebid.org governance: reader is vendor-neutral, companion is Encypher-specific. |
| Dedup strategy | content_hash + domain | Same article content on same domain only signed once. Re-requests are free (no quota charge). |
| Cert model | Self-signed Ed25519 per org (free), sub-CA issued (Enterprise) | Existing infra handles free tier. SSL.com client already exists for CA path. |

## Success Criteria

- Prebid RTD module V2 passes all existing + new tests
- Public signing endpoint handles 100 req/sec sustained
- Org auto-provisioning is idempotent and sub-100ms
- Content dedup prevents double-charging quota
- Manifest is publicly verifiable via existing `/public/verify/media` and CDN manifest endpoints
- Companion script install is one line of HTML
- Domain claim flow works with DNS TXT verification
- Free tier cap naturally identifies high-volume publishers as Enterprise conversion targets

## Phasing

**Phase 1 (Ship first, 2-3 weeks):** Tasks 1.0, 4.0, 5.0, 6.1-6.5
- Public signing endpoint + auto-provisioning + RTD module V2 + companion script
- Notarization model only (Encypher-managed certs)
- Submit read-only RTD module (V1) upstream to Prebid.org

**Phase 2 (Upgrade path, 2 weeks):** Tasks 2.0, 7.0
- Domain claim/verification flow
- Known media company ownership mapping
- Dashboard Prebid org view
- Aditude governance validation for auto-signing

**Phase 3 (Enterprise upsell, 2 weeks):** Task 3.0
- S/MIME sub-CA cert issuance via SSL.com
- Publisher signs under own identity
- Sentence-level + media signing unlocked on upgrade

## Completion Notes

(Filled when PRD is complete.)
