# Prebid C2PA Auto-Provenance Distribution

**Status:** In Progress
**Current Goal:** Phase 1 complete. Submit upstream PR, then build CDN integration handshake (Phase 2).

## Overview

The Prebid RTD module (`encypherRtdProvider.js`) is a distribution channel for C2PA content provenance. It reads existing provenance signals on each pageload and injects them into OpenRTB bid requests at `site.ext.data.c2pa`, making provenance-verified inventory visible to DSPs and SSPs across 70k+ Prebid publisher sites.

The production path (Path A) reads a `<meta name="c2pa-manifest-url">` tag placed by an upstream signing mechanism: the Encypher CDN worker (see `PRD_CDN_Content_Provenance_Worker.md`), a CMS plugin (WordPress, Ghost), or direct API integration. The CDN worker is the primary adoption carrot because it requires zero publisher code changes (one DNS record).

Path C (auto-sign) serves as an onboarding and demo mechanism. It lets publishers see provenance signals in bid requests immediately, before deploying CDN or CMS integration. This proves the CPM-lift hypothesis and motivates permanent adoption via CDN or CMS.

The strategy: CDN worker creates provenance (upstream). Prebid distributes it to DSPs (downstream). CPM lift from provenance-verified inventory drives voluntary Enterprise conversion.

## Objectives

- Distribute C2PA provenance signals into the OpenRTB bid stream via Prebid's RTD framework
- Path A (production): read provenance from upstream signing (CDN worker, CMS plugin, API) and inject into bid requests
- Path C (onboarding): auto-sign content on first visit so publishers see immediate value before deploying permanent signing
- Maintain notarization model: Encypher signs as attester ("this content published at {url} on {date}"), not as author or copyright holder
- Never store publisher content -- only hashes, metadata, and C2PA manifests
- Free tier (1,000 signs/month) naturally gates toward Enterprise conversion for high-volume publishers
- Ship as a single Encypher-branded RTD module (`encypherRtdProvider.js`); existing V1 read-only module (`c2paProvenanceRtdProvider.js`) stays for WordPress CMS users

## Relationship to CDN Worker

The Prebid RTD module and the CDN Content Provenance Worker (`PRD_CDN_Content_Provenance_Worker.md`) form a two-stage pipeline:

| Stage | Component | Function |
|-------|-----------|----------|
| Upstream (signing) | CDN Worker / CMS Plugin / API | Signs content, injects `<meta name="c2pa-manifest-url">` |
| Downstream (distribution) | Prebid RTD Module (Path A) | Reads meta tag, injects `site.ext.data.c2pa` into bid requests |

**Publisher adoption funnel:**
1. Publisher installs Prebid RTD module (zero config, included in Prebid.js build)
2. Path C auto-signs on first visit, publisher sees provenance in bid stream
3. Publisher sees CPM lift on provenance-verified inventory
4. Publisher deploys CDN worker (one DNS record) for permanent, production-grade signing
5. Path A reads CDN-injected meta tag on every pageload (no API calls, no latency)
6. Enterprise conversion for high-volume publishers who want publisher-identity signing, sentence-level provenance, or rights metadata

**Cross-channel org resolution:** When a publisher uses both CDN and Prebid channels, the org provisioning system checks for existing orgs across both namespaces (`org_prebid_{hash}`, `org_cdn_{hash}`) to share a single quota pool. See CDN Worker PRD Task 5.0.

## Architecture

### Data Flow

```
Page Load
  |
  v
encypherRtdProvider.js (client-side, in Prebid.js)
  |
  +--> PATH A (Production): Check <meta name="c2pa-manifest-url">
  |      Source: CDN worker, CMS plugin (WordPress/Ghost), or direct API
  |      Found? --> Fetch manifest JSON, inject site.ext.data.c2pa
  |                 source="cms", no API call, no latency cost
  |                 Done.
  |
  +--> PATH B (Cache): Check localStorage for canonical URL hash
  |      Hit and not expired (30-day TTL)?
  |      --> Inject cached payload into site.ext.data.c2pa
  |          source="cache", no API call
  |          Done.
  |
  +--> PATH C (Onboarding/Demo): Extract article text, call signing API
  |      1. Extract text from DOM (JSON-LD > <article> > [role="main"])
  |      2. POST /api/v1/public/prebid/sign (public, no auth, rate-limited)
  |      3. Cache result in localStorage
  |      4. Inject site.ext.data.c2pa, source="auto"
  |
  v
All paths: inject site.ext.data.c2pa into OpenRTB bid request
All paths: call callback() (never block auction)
All error branches: call callback() (fail-open)
```

**Path C server-side flow (Prebid Signing Service):**

```
POST /api/v1/public/prebid/sign
  |
  +--> 1. Lookup domain org: org_prebid_{sha256(domain)[:12]}
  |      Not found? --> Auto-provision org (free tier, Encypher-managed cert)
  |
  +--> 2. Check dedup: content_hash + domain in prebid_content_records
  |      Already signed? --> Return existing manifest_url (cached=true, no quota charge)
  |
  +--> 3. Check quota (1,000/month for free tier)
  |      Exceeded? --> Return error with upgrade_url
  |
  +--> 4. Sign via execute_unified_signing (managed signer, notarization model)
  |      - Claim generator: "Encypher Prebid Provenance/1.0"
  |      - Content NOT stored. Only: hash, manifest metadata.
  |
  +--> 5. Store record in prebid_content_records, return manifest_url
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

- [x] 1.1 Add `prebid_content_records` DB model and Alembic migration
  - [x] 1.1.1 Fields: id, org_id, domain, canonical_url, content_hash (SHA-256), manifest_store (JSONB), manifest_url, page_title, signer_tier, signed_at, created_at
  - [x] 1.1.2 Unique constraint on (domain, content_hash)
  - [x] 1.1.3 Index on organization_id
- [x] 1.2 Add `prebid_signing_service.py`
  - [x] 1.2.1 `sign_or_retrieve(db, page_url, text_content, document_title)` -- main entry point
  - [x] 1.2.2 Domain org lookup/provisioning: `_ensure_prebid_org(domain)` using `org_prebid_{hash}` namespace with ON CONFLICT DO NOTHING
  - [x] 1.2.3 Content dedup: check `prebid_content_records` by (domain, content_hash)
  - [x] 1.2.4 Quota check via organizations.documents_signed counter
  - [x] 1.2.5 Build manifest metadata and store in `prebid_content_records.manifest_store` JSONB
  - [x] 1.2.6 Return manifest_url + metadata (content text never stored)
- [x] 1.3 Add `prebid_schemas.py`
  - [x] 1.3.1 `PrebidSignRequest`: text, page_url, document_title (Pydantic with min_length=50)
  - [x] 1.3.2 `PrebidSignResponse`: success, manifest_url, signer_tier, signed_at, content_hash, org_id, cached, error, upgrade_url
- [x] 1.4 Add `app/api/v1/public/prebid.py` router at `/public/prebid/`
  - [x] 1.4.1 `POST /api/v1/public/prebid/sign` -- public, no auth, IP rate-limited (3600/hr)
  - [x] 1.4.2 `GET /api/v1/public/prebid/manifest/{record_id}` -- serves stored manifest with CORS headers
  - [x] 1.4.3 `GET /api/v1/public/prebid/status/{domain}` -- returns org signing stats
  - [ ] 1.4.4 `POST /api/v1/public/prebid/claim` -- authenticated domain claim (Phase 3)
- [x] 1.5 Register router in `app/api/v1/api.py`
- [x] 1.6 Add `prebid_sign` rate limiter entry in `public_rate_limiter.py`
- [x] 1.7 Wire full C2PA JUMBF signing via `execute_unified_signing` (managed signer, notarization model)

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

### 4.0 Prebid.js -- encypherRtdProvider.js (Single Module)

Garrett (Prebid chairman) confirmed that a single Encypher-branded RTD module is the standard approach. All Prebid RTD modules are vendor-specific. The previously planned two-module split (vendor-neutral reader + companion script) is unnecessary. Conformance and cert management are managed services, not something publishers or Prebid.org would DIY.

The existing V1 `c2paProvenanceRtdProvider.js` (read-only, 7 tests passing) stays in the Prebid.js fork for WordPress CMS users. The new `encypherRtdProvider.js` supersedes it with auto-signing.

Code lives in private repo: `encypherai/prebid-rtd-provider`

- [x] 4.1 Create private repo scaffold (`package.json`, `.gitignore`, `README.md`)
- [x] 4.2 Write `encypherRtdProvider.js` with three execution paths:
  - [x] 4.2.1 Path A (CMS): `<meta name="c2pa-manifest-url">` or `params.manifestUrl` -- fetch manifest, inject `site.ext.data.c2pa`
  - [x] 4.2.2 Path B (Cache): localStorage hit for canonical URL hash (30-day TTL, djb2 hash, Prebid `getStorageManager` for GDPR)
  - [x] 4.2.3 Path C (Auto-sign): Extract article text (JSON-LD > `<article>` > `[role="main"]`), POST to `/api/v1/public/prebid/sign`, cache result, inject
  - [x] 4.2.4 Every path and every error branch calls `callback()` (fail-open)
- [x] 4.3 Write `encypherRtdProvider_spec.js` (20+ tests, Mocha + assert + server mock)
  - [x] 4.3.1 init, Path A (5 cases), Path B (2 cases), Path C (7 cases), payload shape, utilities
- [x] 4.4 Write `encypherRtdProvider.md` (Prebid docs for PR review)
- [ ] 4.5 Create GitHub private repo and push
- [ ] 4.6 Copy module + tests into Prebid.js fork and verify (`gulp test`, `gulp build`)
- [ ] 4.7 Submit upstream PR to `prebid/Prebid.js`

### 6.0 Testing & Validation

- [x] 6.1 `test_prebid_signing.py` -- 25 tests passing (pytest)
  - [x] 6.1.1 Service utilities: extract_domain, hash_content, org ID generation (9 unit tests)
  - [x] 6.1.2 POST /sign endpoint: new content, dedup, different content, validation, rate limiting, CORS (7 integration tests)
  - [x] 6.1.3 GET /manifest/{id}: returns signed record, 404 for unknown (2 tests)
  - [x] 6.1.4 GET /status/{domain}: provisioned and unprovisioned domains (2 tests)
  - [x] 6.1.5 Service layer: sign_or_retrieve, dedup, invalid URL, idempotent provisioning, quota check (5 tests)
- [x] 6.2 E2E Puppeteer tests -- 7 tests passing (`prebid-rtd-provider/test/e2e/`)
  - [x] 6.2.1 Path C: article extraction + signing API call + ortb2 injection
  - [x] 6.2.2 Path C: JSON-LD extraction priority over article element
  - [x] 6.2.3 Path A: CMS meta tag (no signing API call)
  - [x] 6.2.4 No content: graceful degradation (no c2pa injected)
  - [x] 6.2.5 Path B: cache hit on second visit (no signing API call)
  - [x] 6.2.6 Auction always completes (fail-open)
  - [x] 6.2.7 Payload shape validation (all required fields present)
- [x] 6.4 `encypherRtdProvider_spec.js` -- 20+ tests covering all three paths
  - [x] 6.4.1 init (returns true, correct name, exposes getBidRequestData)
  - [x] 6.4.2 Path A: meta tag fetch+inject, params.manifestUrl override, HTTP 500 fail-open, malformed JSON, verified=false
  - [x] 6.4.3 Path B: cache hit with source='cache' and no XHR, expired cache falls through to Path C
  - [x] 6.4.4 Path C: article extraction + API call, JSON-LD priority, role=main fallback, API error fail-open, success=false fail-open, no content skip, cache write after signing
  - [x] 6.4.5 Payload shape (Path A fields, Path C fields including extraction_method)
  - [x] 6.4.6 Utilities (hashUrl consistency, extractContent null/short-content handling)
- [ ] 6.6 Load test: simulate 1,000 domains, 100 pages each

### 7.0 Strategy & Distribution

- [ ] 7.1 Submit `encypherRtdProvider.js` upstream PR to `prebid/Prebid.js`
  - [x] 7.1.1 Copy module + tests into Prebid.js fork, verify `gulp test` (23 passing) and `gulp build` (3.79 KiB minified)
  - [ ] 7.1.2 Open PR from `erik-sv/Prebid.js` to `prebid/Prebid.js`
- [ ] 7.2 Seed `prebid_domain_ownership` table with known media company properties
- [ ] 7.3 Update internal strategy docs with Prebid distribution play
- [ ] 7.4 Dashboard: Prebid org view showing domain signing stats and upgrade CTA

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Production path | Path A (read meta tag from CDN/CMS) | Zero latency, no API call per pageview. CDN worker or CMS plugin does the signing upstream. |
| Onboarding path | Path C (auto-sign) as demo mechanism | Lets publishers see value before deploying permanent signing. Proves CPM-lift hypothesis. |
| Auth model | Public endpoint, no API key | Zero-friction distribution. Rate limiting + domain-based quota prevents abuse. |
| Signer identity | Notarization (Encypher signs as attester) | No publisher cooperation needed. C2PA Section A.7: attestation of publication, not copyright claim. |
| IP ownership | Attestation model, not rights claim | Publisher content may include quotes, wire content, facts. Provenance = "published here at this time." Rights metadata is a separate, opt-in layer. |
| Org namespace | `org_prebid_{hash}` | Avoids collision with email-provisioned orgs. Cross-channel resolution shares org with CDN channel. |
| Content storage | Never stored. Hash + manifest only. | Legal, privacy, storage cost. Content hash sufficient for dedup and verification. |
| Module architecture | Single Encypher-branded RTD module | Garrett confirmed all Prebid RTD modules are vendor-specific. V1 read-only module stays for CMS users. |
| Dedup strategy | content_hash + domain | Same article content on same domain only signed once. Re-requests are free (no quota charge). |
| Cert model | Self-signed Ed25519 per org (free), sub-CA issued (Enterprise) | Existing infra handles free tier. SSL.com client already exists for CA path. |

## Success Criteria

- `encypherRtdProvider.js` passes all 20+ tests in Prebid.js test harness
- Path A correctly reads CDN-injected `<meta name="c2pa-manifest-url">` and injects into bid requests with zero API calls
- Path C auto-signs on first visit, proving the onboarding flow
- Public signing endpoint handles 100 req/sec sustained
- Org auto-provisioning is idempotent and sub-100ms
- Cross-channel org resolution correctly shares quota between Prebid and CDN channels
- Content dedup prevents double-charging quota
- Manifest is publicly verifiable via existing `/public/verify/media` and CDN manifest endpoints
- Free tier cap naturally identifies high-volume publishers as Enterprise conversion targets

## Phasing

**Phase 1 (RTD module + backend + C2PA signing -- COMPLETE):** Tasks 1.0, 4.0, 6.0
- `encypherRtdProvider.js` written, tested (23 unit + 7 E2E), built (3.79 KiB)
- Backend: DB model, signing service with real C2PA via `execute_unified_signing`, public router, rate limiting, 25 pytest tests
- Copied to Prebid.js fork, registered in `.submodules.json`, `gulp test` and `gulp build` green
- Private repo at `encypherai/prebid-rtd-provider` (GitHub)
- Task 1.7 complete: `sign_or_retrieve` calls `execute_unified_signing` with managed signer key (notarization model). Manifest endpoint returns `document_id` and `verification_url` from real signing result.
- Next: submit upstream PR (Task 7.1.2)

**Phase 2 (CDN Integration Handshake):** New tasks below
- Cross-channel org resolution so CDN and Prebid channels share quota
- RTD module Path A verification against CDN-injected meta tags
- Shared publisher analytics across both channels
- Depends on: `PRD_CDN_Content_Provenance_Worker.md` Phase 1

**Phase 3 (Upgrade path):** Tasks 2.0, 7.0
- Domain claim/verification flow
- Known media company ownership mapping
- Dashboard Prebid org view

**Phase 4 (Enterprise upsell):** Task 3.0
- S/MIME sub-CA cert issuance via SSL.com
- Publisher signs under own identity
- Sentence-level + media signing unlocked on upgrade

## Value Proposition

| Audience | Value |
|----------|-------|
| Publisher | One DNS record (CDN worker), zero code. Content gets C2PA provenance. Prebid distributes it to DSPs. CPM lift follows. |
| DSP/SSP | `site.ext.data.c2pa` on every bid request from opted-in inventory. Filter for provenance-verified supply. |
| Encypher | CDN worker is the adoption carrot (zero-friction onboarding). Prebid is the distribution rail (70k sites). Enterprise conversion follows CPM lift. |

**Path C as onboarding tool:** A publisher who installs Prebid with the Encypher RTD module sees provenance signals in bid requests on their first pageload (Path C auto-signs). This proves the concept. When they see CPM lift, they deploy the CDN worker (one DNS record) for permanent, zero-latency signing (Path A reads the CDN-injected meta tag).

## Completion Notes

(Filled when PRD is complete.)
