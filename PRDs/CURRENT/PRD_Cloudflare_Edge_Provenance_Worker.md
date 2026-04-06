# Cloudflare Edge Provenance Worker

**Status:** In Progress (Phase 1 complete)
**Current Goal:** Phase 1 backend + worker core complete, 80/80 tests passing. Phase 2 (dashboard, publishing, docs) pending.

## Overview

A publishable Cloudflare Worker that embeds copy-paste-survivable provenance markers into HTML article text at the CDN edge. Publishers deploy in one click, get sentence-level micro+ECC+C2PA markers on every article, and never touch code. The worker is the primary publisher adoption mechanism: a free lead magnet that demonstrates provenance value and creates organic pull toward enterprise features. This PRD supersedes the meta-tag injection approach in PRD_CDN_Content_Provenance_Worker.md.

## Objectives

- Embed invisible Unicode provenance markers (micro+ECC+C2PA, sentence-level) into article text at the CDN edge with zero publisher code changes
- Survive copy-paste, aggregation, scraping, and redistribution so provenance travels with the text
- Provide one-click deployment via Cloudflare's Deploy button with zero configuration required
- Auto-provision publisher accounts and verify domain ownership through the worker's presence
- Gate enterprise features (fingerprinting, dual binding, per-segment rights) at the backend via dashboard-controlled org tiers, never requiring worker reconfiguration
- Convert free publishers to enterprise through natural "see value, want enforcement" funnel
- Publish as open GitHub repo (`encypher/cloudflare-worker-provenance`) and submit to Cloudflare template gallery

## Strategic Context

The GTM strategy (v5.2) states: "Publishers (Free Tier): Full text signing infrastructure at no cost + freemium enforcement add-ons." The CDN worker is the purest expression of this. The signing API tier matrix confirms that micro+ECC+C2PA at sentence-level segmentation is Free tier. Enterprise gates protect fingerprinting, dual binding, and per-segment rights.

The conversion funnel:
1. Deploy worker (5 minutes). Articles carry invisible markers.
2. Dashboard auto-provisions. Publisher sees signed article count and quota.
3. Attribution Analytics detects their signed content on aggregator sites (Tier 1 detection, no AI company cooperation needed).
4. Publisher wants to send formal notice to a scraper. That requires enterprise features. Natural upsell.

Sources: Encypher_GTM_Strategy.md (v5.2), Encypher_API_Sandbox_Strategy.md (v4.2), Encypher_Future_Partnerships_Products.md (Section 7), Encypher_OpenSource_Strategy.md (v4.1).

---

## Content Boundary Detection Strategy

The worker must find article text within an HTML page and ignore navigation, footers, ads, and other non-article content. Detection methods ordered by web prevalence (based on CMS market share research):

### Detection Chain (Most Common to Least Common)

**Priority 0: Publisher Override**
If `ARTICLE_SELECTOR` is set in worker config, use it exclusively. The publisher knows their own markup. Supported formats: tag name (`article`), class (`.post-content`), attribute selector (`[data-testid="article-body"]`).

**Priority 1: `<article>` tag (~50%+ of content sites)**
Used by WordPress classic themes, Ghost, Jekyll, Hugo, Squarespace, Medium. The HTML5 semantic element designed for self-contained article content. This is the single most reliable signal across the web.

Implementation: regex match `<article\b[^>]*>([\s\S]*?)<\/article>`. If multiple `<article>` tags exist, use the one with the most `<p>` children (content article vs. sidebar article teasers).

**Priority 2: CMS content wrapper classes (~43% via WordPress alone)**
WordPress and other CMSes use specific classes for the article body within the `<article>` wrapper. When found inside an `<article>` tag, these narrow the boundary. When found without an `<article>` tag (WordPress block themes), they serve as the primary boundary.

Selectors tried in order:
- `.entry-content` (WordPress default, classic + block themes)
- `.wp-block-post-content` (WordPress block themes, Twenty Twenty-Four)
- `.post-content` (Jekyll Minima, generic blog themes)
- `.article-body`, `.article-content`, `.story-body` (news publisher conventions)
- `.gh-content` (Ghost CMS Casper theme)
- `.w-richtext` (Webflow)
- `.sqs-block-content` (Squarespace)
- `.body.markup` (Substack)
- `.e-content` (Microformats2, IndieWeb)

Implementation: regex match each pattern against the HTML. Use the first match found.

**Priority 3: Schema.org microdata attribute**
`[itemprop="articleBody"]` is used by Jekyll, some WordPress themes, and sites following Schema.org markup. Direct semantic signal for article content.

Implementation: regex match `itemprop=["']articleBody["']` on any element, extract inner content.

**Priority 4: `<main>` / `[role="main"]` (~60% of modern sites)**
Broader than article (may include sidebar) but reliable as a fallback. The fragment extractor within the boundary already skips `<nav>`, `<aside>`, `<footer>`, `<header>` elements, so a wider boundary is acceptable.

Implementation: regex match `<main\b[^>]*>` or `role=["']main["']`.

**Priority 5: JSON-LD `articleBody`**
Present on ~20% of content sites (CNN confirmed, Yoast SEO does NOT include it). When available, this is clean plain text. Use as the text source when HTML boundary detection fails, or as a validation check when HTML extraction succeeds.

Implementation: find `<script type="application/ld+json">` blocks, parse JSON, check for `articleBody` field on `Article`, `NewsArticle`, or `ReportageNewsArticle` types. Handle both `@type` and `@graph` patterns.

**Priority 6: Largest `<p>` cluster heuristic**
Emergency fallback. Count `<p>` tags within each container element. The container with the highest density of `<p>` tags relative to its children is likely the article body. Apply a minimum threshold (5+ paragraphs) to avoid false positives.

**Priority 7: Full `<body>` with aggressive skip list**
Last resort. Extract from the entire `<body>`, relying entirely on the fragment extractor's skip list (`<script>`, `<style>`, `<nav>`, `<aside>`, `<footer>`, `<header>`, `<form>`) to filter non-article content. Higher risk of including unwanted text, but better than not signing at all.

### Within-Boundary Text Extraction

Once the article boundary is identified, the worker extracts text using the byte-level fragment extraction approach proven in the Ghost integration (`ghost-provenance/src/html-utils.ts`):

1. Walk the boundary HTML byte-by-byte
2. Track tag boundaries. Skip: `<script>`, `<style>`, `<code>`, `<pre>`, `<noscript>`, `<svg>`, `<math>`, `<video>`, `<audio>`, `<canvas>`, `<iframe>`, `<img>`, `<picture>`, `<template>`
3. Collect text runs between tags as fragments with byte offsets: `[{byteOffset, byteLength, rawText}]`
4. Decode HTML entities, normalize whitespace, join with spaces at block-element boundaries
5. Apply floor filter: skip pages with <50 characters of extracted text
6. Apply ceiling: truncate at 50KB

### Validation via JSON-LD

When JSON-LD `articleBody` exists alongside HTML extraction, compare the two:
- If they match (after normalization): high confidence in extraction quality
- If they diverge: log a warning, prefer the HTML extraction (since markers must be injected into HTML text nodes)

---

## Deployment & Onboarding UX

### One-Click Deploy

The worker is published as a GitHub repo (`encypher/cloudflare-worker-provenance`) with a Cloudflare Deploy button:

```
https://deploy.workers.cloudflare.com/?url=https://github.com/encypher/cloudflare-worker-provenance
```

The Deploy button:
1. User clicks the button on our GitHub README or encypher.com/cloudflare
2. Authenticates with GitHub + Cloudflare (if not already)
3. Cloudflare auto-provisions the KV namespace from `wrangler.toml`
4. User selects their Cloudflare zone and clicks Deploy
5. Worker is live. No code, no CLI, no configuration required.

Post-deploy, the user adds a route in their Cloudflare dashboard: `*example.com/*`. The worker processes all requests but only modifies HTML responses that contain article text. Non-article pages, images, API calls, and static assets pass through unmodified.

### Worker Configuration

```toml
# wrangler.toml - ships with the template
name = "encypher-provenance"
main = "src/worker.js"
compatibility_date = "2026-04-01"

[[kv_namespaces]]
binding = "PROVENANCE_CACHE"
# Auto-provisioned by Deploy button

[vars]
# Everything below is optional. The worker works with zero configuration.
# Publisher can override content detection:
# ARTICLE_SELECTOR = ".my-article-class"
# MIN_TEXT_LENGTH = "50"
# MAX_TEXT_LENGTH = "51200"
```

No API key, no domain, no account ID. The worker auto-detects the domain from request headers and auto-provisions everything.

### Auto-Provisioning Flow

On the first HTML request the worker processes:

```
Worker intercepts HTML response
  --> Extracts article text
  --> Checks KV for domain provisioning record
  --> MISS (first request ever):
        POST /api/v1/public/cdn/provision
        {
          "domain": "example.com",
          "worker_version": "1.0.0"
        }
        Response:
        {
          "org_id": "org_cdn_a1b2c3d4e5f6",
          "domain_token": "dtk_...",
          "dashboard_url": "https://encypher.com/cdn/example.com",
          "claim_url": "https://encypher.com/claim/org_cdn_a1b2c3d4e5f6"
        }
        Store in KV: "provision:{domain}" -> {org_id, domain_token}
  --> Proceeds to sign content using org_id
```

Cross-channel org resolution: if example.com already has an org from Prebid RTD or dashboard signup, the provisioning endpoint finds and reuses it. One publisher, one org, shared quota across all channels.

### Domain Verification

The worker's presence on a domain IS the domain verification. If a Cloudflare Worker is running on example.com, the person who deployed it controls that domain's Cloudflare zone. This is stronger proof of domain control than DNS TXT records.

The worker serves a verification endpoint:

```
GET /.well-known/encypher-verify
Response: {"domain_token": "dtk_...", "org_id": "org_cdn_..."}
```

The backend can verify domain ownership at any time by fetching this endpoint.

### Account Claiming (Dashboard Access)

After deployment, the publisher can claim their dashboard:

1. Worker logs the `claim_url` to Cloudflare Workers logs on first provisioning
2. The worker also injects a small HTML comment in signed pages: `<!-- Encypher: Dashboard at https://encypher.com/claim/org_cdn_... -->`
3. Publisher visits the claim URL
4. Claim page asks for an email address (any email, no domain restriction)
5. Backend calls `https://example.com/.well-known/encypher-verify` to confirm the worker is live and the domain_token matches
6. If confirmed: domain ownership verified. Send email with verification code.
7. User enters code. Account created. Dashboard access granted for this org.
8. Dashboard shows: signed articles, quota usage, content hash history, Attribution Analytics results

If the publisher already has an Encypher account (from Prebid, WordPress plugin, or direct signup), they can link the CDN domain to their existing account from the dashboard.

### Upgrade Path (Zero Reconfiguration)

Enterprise features are gated at the backend, not the worker. The publisher never touches the worker after initial deployment.

**How it works:**
- The worker always calls the same endpoint: `POST /api/v1/public/cdn/sign`
- The worker always sends the same payload: `{text, page_url, org_id, options: {return_embedding_plan: true}}`
- The backend checks the org's tier and applies signing options accordingly:
  - Free tier: `manifest_mode: "micro", ecc: true, embed_c2pa: true, segmentation_level: "sentence"`
  - Enterprise tier: same plus `include_fingerprint: true, add_dual_binding: true` and any org-level signing config from the dashboard
- The response always has the same shape: `{embedding_plan, document_id, verification_url}`
- The worker always applies the embedding plan the same way

**Upgrade flow:**
1. Publisher logs into encypher.com dashboard
2. Clicks Upgrade on their domain's settings
3. Payment flow (Stripe)
4. Backend sets org tier to Enterprise
5. Next article signed by the worker automatically gets enterprise-level markers
6. No worker redeployment, no config change, no API key

**Optional power-user path:**
Publishers who want fine-grained control (specific fingerprint density, custom rights profiles, specific segmentation levels) configure these as org-level signing defaults in the dashboard. The backend applies them when signing for that org.

**API key path (secondary):**
Technical users who prefer explicit auth can add `ENCYPHER_API_KEY` as a Cloudflare environment variable. When present, the worker uses authenticated endpoints with the user's own account instead of auto-provisioning. This path exists for users who want to manage signing configuration themselves rather than through the dashboard.

---

## Technical Architecture

### Data Flow (Steady State, Cache Hit)

```
Reader requests article
  --> Cloudflare Edge (Worker intercepts)
    --> Fetch origin HTML response
    --> Check: Content-Type is text/html? Status 200? Yes.
    --> Find article boundary (detection chain)
    --> Extract text fragments with byte offsets
    --> Assemble visible text, SHA-256 hash
    --> KV lookup: "plan:{domain}:{hash[:16]}"
    --> HIT: cached {embedding_plan, boundary_selector}
    --> Apply embedding plan to HTML at byte offsets
    --> Return modified HTML
```

Latency overhead on cache hit: <1ms (pure in-memory string manipulation).

### Data Flow (Cache Miss, First Pageview of New Article)

```
Reader requests article
  --> Cloudflare Edge (Worker intercepts)
    --> Fetch origin HTML response (buffered)
    --> Find article boundary, extract fragments, assemble text
    --> SHA-256 hash
    --> KV lookup: MISS
    --> POST /api/v1/public/cdn/sign
        {
          "text": "extracted article text...",
          "page_url": "https://example.com/article/slug",
          "org_id": "org_cdn_a1b2c3d4e5f6",
          "options": {
            "manifest_mode": "micro",
            "ecc": true,
            "embed_c2pa": true,
            "segmentation_level": "sentence",
            "return_embedding_plan": true
          }
        }
    --> Response: {embedding_plan, document_id, verification_url}
    --> Cache in KV: "plan:{domain}:{hash[:16]}" (TTL: 1 hour)
    --> Apply embedding plan to HTML at byte offsets
    --> Return modified HTML
```

Latency overhead on cache miss: ~50-100ms (API round-trip). Acceptable for first pageview of a new article. All subsequent readers get cache-hit latency.

### Embedding Plan Application (Ported from Ghost Integration)

The core algorithm from `ghost-provenance/src/html-utils.ts` `embedEmbeddingPlanIntoHtml()` handles the hard problem of mapping codepoint-indexed embedding operations to byte offsets in HTML:

1. Extract visible text from boundary HTML (`extractText` equivalent)
2. Extract text fragments with byte offsets (`extractFragments`)
3. Walk fragments and visible text in parallel, building `Map<codepointIndex, absoluteByteOffset>`
4. For each embedding plan operation, look up the byte offset for `insert_after_index`
5. Group markers by byte offset, sort insertions in reverse order
6. Splice marker bytes into the HTML buffer at computed offsets
7. Return modified HTML

Port from Node.js to Cloudflare Workers: replace `Buffer` with `TextEncoder`/`TextDecoder` and `Uint8Array`. Logic is otherwise identical.

Fail-safe: if alignment fails at any step, `embedEmbeddingPlanIntoHtml` returns `null`. The worker serves the original unmodified HTML. Never corrupt visible content.

### Caching Strategy

**Embedding plan cache (KV):**
- Key: `plan:{domain}:{sha256(text)[:16]}`
- Value: JSON `{embeddingPlan, documentId, verificationUrl, boundarySelector, signedAt}`
- TTL: 1 hour
- Rationale: article content is stable; 1-hour TTL balances freshness with API call reduction

**Provisioning cache (KV):**
- Key: `provision:{domain}`
- Value: JSON `{orgId, domainToken, dashboardUrl, claimUrl, provisionedAt}`
- TTL: 24 hours (re-provision daily to pick up tier changes)

**Negative cache:**
- Key: `skip:{domain}:{sha256(text)[:16]}`
- Value: `"NO_ARTICLE"` (extraction found <50 chars) or `"ALIGN_FAIL"` (embedding plan could not be applied)
- TTL: 5 minutes (short, so fixes to detection logic take effect quickly)

### Skip Conditions

Do not sign a response when:
- Content-Type is not `text/html`
- Response status is not 200
- Request is a bot/crawler (optional: skip Googlebot to avoid indexing markers, configurable)
- Extracted text is below 50 characters
- Response already contains provenance markers (VS character detection)
- Response body exceeds 5MB (avoid buffering extremely large pages)
- Request path matches skip patterns: `/api/*`, `/wp-admin/*`, `/wp-json/*`, `/feed/*`, `*.xml`, `*.json`

### Rate Limiting

- Per-domain: 100 signing requests/hour to the API (KV cache means most pageviews never hit the API)
- Per-IP: 60 provisioning requests/minute (prevent provisioning abuse)
- Quota: 1,000 unique article signs/month per org (Free tier, deduped by content hash)
- Quota exceeded: worker serves unmodified HTML, adds `X-Encypher-Quota: exceeded` header

---

## Free vs. Enterprise Feature Matrix

| Capability | Free (auto-provisioned) | Enterprise (dashboard upgrade) |
|---|:---:|:---:|
| Sentence-level micro+ECC+C2PA markers | Yes | Yes |
| Copy-paste survival (Reed-Solomon ECC) | Yes | Yes |
| Public verification (no auth) | Yes | Yes |
| Dashboard with signing stats | Yes (after claiming) | Yes |
| Attribution Analytics (Tier 1) | Basic (where content appears) | Full (detailed, alerts) |
| Unique signs/month | 1,000 | Unlimited |
| Fingerprinting (per-session leak detection) | No | Yes |
| Dual binding | No | Yes |
| Per-segment rights metadata | No | Yes |
| Print leak detection | No | Yes |
| Formal notice generation | No | Yes |
| Evidence package export | No | Yes |
| Custom assertion templates | No | Yes |
| Priority support | No | Yes |

---

## Backend Endpoints

### New Endpoints

**POST /api/v1/public/cdn/provision**
- Public, no auth, rate-limited
- Input: `{domain, worker_version}`
- Behavior: cross-channel org resolution (check Prebid, CDN, dashboard orgs), create if none exists
- Output: `{org_id, domain_token, dashboard_url, claim_url}`

**POST /api/v1/public/cdn/sign**
- Public, no auth, rate-limited by org quota
- Input: `{text, page_url, org_id, options: {return_embedding_plan: true, ...}}`
- Behavior: same as unified signing but with org-tier-aware option injection. Backend reads org tier, merges default signing options from org config, signs content, returns embedding plan.
- Output: `{embedding_plan, document_id, verification_url, content_hash, cached, signer_tier}`
- Dedup: unique constraint on `(domain, content_hash)` in `cdn_content_records`. Duplicate requests return cached embedding plan, no quota charge.

**GET /api/v1/public/cdn/manifest/{record_id}**
- Public, CORS-enabled
- Returns manifest metadata for a signed CDN content record

**GET /.well-known/encypher-verify** (served by the worker, not the API)
- Returns domain_token and org_id for domain ownership verification

**POST /api/v1/public/cdn/claim**
- Input: `{org_id, email}`
- Behavior: verify domain ownership via `/.well-known/encypher-verify`, send verification email
- Output: `{verification_sent: true}`

### Modified Endpoints

**Unified signing service:**
- Add org-tier-aware option injection: when signing for an org, read the org's tier and default signing config, merge with request options
- This is the mechanism that makes dashboard upgrades work without worker reconfiguration

---

## Database

### New Table: `cdn_content_records`

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| organization_id | String(64) | FK to organizations |
| domain | String(255) | Publisher eTLD+1 |
| canonical_url | Text | Full page URL |
| content_hash | String(71) | "sha256:" + 64 hex |
| embedding_plan | JSONB | Cached embedding plan |
| manifest_store | JSONB | C2PA signing result metadata |
| manifest_url | Text | Public manifest endpoint URL |
| page_title | String(500) | Optional |
| signer_tier | String(32) | "encypher_free" or "enterprise" |
| boundary_selector | String(100) | Which detection method matched |
| signed_at | Timestamp | When content was signed |
| created_at | Timestamp | Row creation |

Unique constraint on `(domain, content_hash)`. Index on `organization_id`.

Parallel to `prebid_content_records`. Shares the same cross-channel org resolution.

---

## Tasks

### 1.0 Backend - CDN Signing Endpoint

- [x] 1.1 Add `cdn_content_records` DB model (`app/models/cdn_content_record.py`) -- 25/25 pytest
  - [x] 1.1.1 Fields: id, org_id, domain, canonical_url, content_hash, embedding_plan (JSONB), manifest_store, manifest_url, page_title, signer_tier, boundary_selector, signed_at, created_at
  - [x] 1.1.2 Unique constraint on (domain, content_hash), index on organization_id
- [x] 1.2 Alembic migration for `cdn_content_records` table
- [x] 1.3 Add `cdn_content_schemas.py` (Pydantic request/response models) -- 25/25 pytest
  - [x] 1.3.1 `CdnProvisionRequest`: domain, worker_version
  - [x] 1.3.2 `CdnProvisionResponse`: org_id, domain_token, dashboard_url, claim_url
  - [x] 1.3.3 `CdnSignRequest`: text (min 50 chars), page_url, org_id, options (with return_embedding_plan forced true)
  - [x] 1.3.4 `CdnSignResponse`: embedding_plan, document_id, verification_url, content_hash, cached, signer_tier, org_id
  - [x] 1.3.5 `CdnClaimRequest`: org_id, email
- [x] 1.4 Add `cdn_signing_service.py` -- 25/25 pytest
  - [x] 1.4.1 `provision_domain(db, domain, worker_version)` - cross-channel org resolution, create if needed
  - [x] 1.4.2 `sign_or_retrieve(db, text, page_url, org_id, options)` - dedup, quota check, sign with org-tier-aware options
  - [x] 1.4.3 `_apply_org_tier_options(db, org_id, options)` - read org tier, merge default signing config
  - [ ] 1.4.4 `claim_domain(db, org_id, email)` - verify via .well-known, send email (deferred to Phase 2)
- [x] 1.5 Add `app/api/v1/public/cdn_signing.py` router
  - [x] 1.5.1 `POST /api/v1/public/cdn/provision` - rate-limited, provisions domain
  - [x] 1.5.2 `POST /api/v1/public/cdn/sign` - rate-limited by org quota, returns embedding plan
  - [x] 1.5.3 `GET /api/v1/public/cdn/manifest/{record_id}` - public manifest retrieval with CORS
  - [ ] 1.5.4 `POST /api/v1/public/cdn/claim` - domain claim initiation (deferred to Phase 2)
- [x] 1.6 Register router in `app/api/v1/api.py`
- [x] 1.7 Add rate limiter entries in `public_rate_limiter.py`
- [x] 1.8 Cross-channel org resolution utility
  - [x] 1.8.1 Extract shared `resolve_publisher_org(db, domain)` from Prebid + CDN
  - [x] 1.8.2 Check namespaces: org_prebid_{hash}, org_cdn_{hash}, dashboard-claimed orgs
  - [x] 1.8.3 Shared quota pool across channels

### 2.0 Cloudflare Worker - Content Boundary Detection

- [x] 2.1 Article boundary detector module (`src/boundary.js`) -- 16/16 node:test
  - [x] 2.1.1 Publisher override (ARTICLE_SELECTOR config)
  - [x] 2.1.2 `<article>` tag detection with multi-article disambiguation
  - [x] 2.1.3 CMS content wrapper classes: .entry-content, .wp-block-post-content, .post-content, .article-body, .article-content, .story-body, .gh-content, .w-richtext, .sqs-block-content, .body.markup, .e-content, .RichTextStoryBody
  - [x] 2.1.4 Schema.org microdata: [itemprop="articleBody"]
  - [x] 2.1.5 `<main>` / [role="main"] fallback
  - [x] 2.1.6 JSON-LD articleBody extraction
  - [ ] 2.1.7 Largest `<p>` cluster heuristic (deferred - low priority fallback)
  - [ ] 2.1.8 Full `<body>` with skip list (last resort) (deferred - low priority fallback)
- [x] 2.2 Fragment extraction module (`src/fragments.js`) -- 22/22 node:test
  - [x] 2.2.1 Port Ghost `extractFragments` to Cloudflare Workers (TextEncoder/Uint8Array instead of Buffer)
  - [x] 2.2.2 Byte-level tag scanner with skip elements
  - [x] 2.2.3 HTML entity decoding
  - [x] 2.2.4 Whitespace normalization
- [x] 2.3 Text assembly module (integrated into `src/fragments.js`)
  - [x] 2.3.1 Assemble visible text from fragments (`assembleText()`)
  - [x] 2.3.2 Block-element boundary handling (paragraph breaks to spaces)
  - [x] 2.3.3 SHA-256 hashing via Web Crypto API (`hashText()`)
  - [x] 2.3.4 Floor (50 chars) and ceiling (50KB) enforcement (in worker.js)

### 3.0 Cloudflare Worker - Embedding Plan Application

- [x] 3.1 Codepoint-to-byte mapper (`src/embed.js`) -- 17/17 node:test
  - [x] 3.1.1 Port Ghost `embedEmbeddingPlanIntoHtml` core algorithm
  - [x] 3.1.2 Fragment-to-visible-text alignment with `Map<codepointIndex, absoluteByteOffset>`
  - [x] 3.1.3 Boundary offset accounting (byte offset of article boundary within full HTML)
  - [x] 3.1.4 Reverse-order insertion to preserve offsets
  - [x] 3.1.5 Fail-safe: return null on alignment failure, serve unmodified HTML
- [x] 3.2 VS marker detection (integrated into `src/embed.js`)
  - [x] 3.2.1 Detect existing VS markers in response (`hasExistingMarkers()`)
  - [x] 3.2.2 Skip signing when markers already present (in worker.js)

### 4.0 Cloudflare Worker - Provisioning & API Client

- [x] 4.1 API client module (`src/api.js`)
  - [x] 4.1.1 `provisionDomain(domain)` - calls /cdn/provision, caches result in KV
  - [x] 4.1.2 `signContent(text, pageUrl, orgId)` - calls /cdn/sign, returns embedding plan
  - [x] 4.1.3 Error handling: API unavailable = fail open (serve unmodified HTML)
  - [x] 4.1.4 API key detection: if ENCYPHER_API_KEY env var present, use authenticated endpoints
- [x] 4.2 KV cache layer (`src/cache.js`)
  - [x] 4.2.1 Embedding plan cache: `plan:{domain}:{hash[:16]}`
  - [x] 4.2.2 Provisioning cache: `provision:{domain}`
  - [x] 4.2.3 Negative cache: `skip:{domain}:{hash[:16]}`
  - [x] 4.2.4 TTL management (1h plans, 24h provisioning, 5m negative)
- [x] 4.3 Verification endpoint handler
  - [x] 4.3.1 Serve `GET /.well-known/encypher-verify` with domain_token and org_id

### 5.0 Cloudflare Worker - Main Handler

- [x] 5.1 Request handler (`src/worker.js`)
  - [x] 5.1.1 Skip conditions: non-HTML, non-200, oversized, bot, skip paths
  - [x] 5.1.2 Buffer HTML response body
  - [x] 5.1.3 Orchestrate: boundary detection -> fragment extraction -> cache check -> API call -> embed -> respond
  - [x] 5.1.4 Fail-open on any error (serve unmodified HTML)
  - [x] 5.1.5 Add response headers: `X-Encypher-Provenance: active|skipped|error`, `X-Encypher-Org: org_cdn_...`
- [x] 5.2 Configuration handler
  - [x] 5.2.1 Read optional env vars: ARTICLE_SELECTOR, MIN_TEXT_LENGTH, MAX_TEXT_LENGTH, ENCYPHER_API_KEY
  - [x] 5.2.2 Default values for all config (zero-config deployment works)
- [x] 5.3 `wrangler.toml` template
  - [x] 5.3.1 KV namespace binding
  - [x] 5.3.2 Compatible with Deploy button auto-provisioning
  - [x] 5.3.3 Commented optional configuration fields
- [x] 5.4 HTML comment injection
  - [x] 5.4.1 Inject `<!-- Encypher Provenance: verified at {verification_url} | Dashboard: {claim_url} -->` before `</body>`

### 6.0 Dashboard - CDN Domain Management

- [ ] 6.1 CDN domain listing in org settings
  - [ ] 6.1.1 Show auto-provisioned CDN domains with signing stats
  - [ ] 6.1.2 Show claim status (unclaimed, claimed, verified)
- [ ] 6.2 Domain claim flow in dashboard
  - [ ] 6.2.1 "Claim a CDN domain" button
  - [ ] 6.2.2 Enter domain, backend verifies via .well-known
  - [ ] 6.2.3 Link to existing account
- [ ] 6.3 Org-level signing configuration
  - [ ] 6.3.1 Default signing options per org (segmentation_level, embedding_strategy, etc.)
  - [ ] 6.3.2 Enterprise options when tier permits (fingerprinting, dual binding, rights)
  - [ ] 6.3.3 Changes take effect on next cache miss (within 1 hour)
- [ ] 6.4 CDN analytics view
  - [ ] 6.4.1 Articles signed, unique content hashes, quota usage
  - [ ] 6.4.2 Boundary detection method distribution (which selector matched)
  - [ ] 6.4.3 Cache hit rate

### 7.0 Publishing & Distribution

- [ ] 7.1 GitHub repo setup (`encypher/cloudflare-worker-provenance`)
  - [ ] 7.1.1 README with Deploy button, 5-minute setup guide, architecture overview
  - [ ] 7.1.2 LICENSE (proprietary for the worker, AGPL for the signing is server-side)
  - [ ] 7.1.3 CHANGELOG
- [ ] 7.2 Deploy button configuration
  - [ ] 7.2.1 Button image and URL in README
  - [ ] 7.2.2 Auto-provisioning of KV namespace confirmed working
- [ ] 7.3 Cloudflare template gallery submission (if available)
- [ ] 7.4 Landing page at encypher.com/cloudflare
  - [ ] 7.4.1 Deploy button
  - [ ] 7.4.2 How it works (3-step visual)
  - [ ] 7.4.3 Free vs. Enterprise comparison
  - [ ] 7.4.4 FAQ

### 8.0 Testing

- [x] 8.1 Backend unit + integration tests (`test_cdn_signing_service.py`) -- 25/25 pytest
  - [x] 8.1.1 Provisioning: new domain, org_id generation, domain extraction
  - [x] 8.1.2 Signing: content hashing, tier-aware option injection (free/enterprise)
  - [x] 8.1.3 Schema validation: all request/response models
  - [ ] 8.1.4 Rate limiting integration tests (deferred to Phase 2)
- [x] 8.2 Worker boundary detection tests -- 16/16 node:test
  - [x] 8.2.1 WordPress classic theme HTML
  - [x] 8.2.2 WordPress block theme HTML
  - [x] 8.2.3 Ghost CMS HTML
  - [x] 8.2.4 Squarespace HTML
  - [x] 8.2.5 Webflow HTML
  - [ ] 8.2.6 Substack HTML (deferred)
  - [ ] 8.2.7 Jekyll/Hugo static site HTML (deferred)
  - [x] 8.2.8 Custom HTML with JSON-LD articleBody
  - [x] 8.2.9 Page with no article content
  - [x] 8.2.10 Page with multiple `<article>` tags
- [x] 8.3 Worker fragment extraction tests -- 22/22 node:test
  - [x] 8.3.1 HTML entities (named, decimal, hex)
  - [x] 8.3.2 Inline elements (em, strong)
  - [x] 8.3.3 Block element boundaries
  - [x] 8.3.4 Script/style/code skip
  - [x] 8.3.5 Whitespace handling, empty input, comments
- [x] 8.4 Worker embedding plan application tests -- 17/17 node:test
  - [x] 8.4.1 Simple HTML (single `<p>`)
  - [x] 8.4.2 Complex HTML (multiple operations, inline elements, entities)
  - [x] 8.4.3 Alignment failure returns null (fail-safe: null plan, invalid index_unit, out-of-range)
  - [x] 8.4.4 Markers appear at correct positions in text nodes
  - [x] 8.4.5 Visible text unchanged after embedding (stripped comparison)
  - [ ] 8.4.6 Embedded markers survive copy-paste from rendered HTML (requires browser, deferred)
  - [ ] 8.4.7 Embedded markers verify successfully via public verification API (requires live API, deferred)
- [ ] 8.5 End-to-end tests (deferred to Phase 2 - requires live API + KV)
  - [ ] 8.5.1 Full flow: HTML in -> signed HTML out -> copy text -> verify -> provenance confirmed
  - [ ] 8.5.2 Cache hit path: second request uses cached plan
  - [ ] 8.5.3 Quota exceeded: serves unmodified HTML
  - [ ] 8.5.4 API unavailable: serves unmodified HTML (fail-open)
  - [ ] 8.5.5 Already-signed content: skips re-signing

### 9.0 Documentation

- [ ] 9.1 Publisher setup guide (in GitHub README)
- [ ] 9.2 Content detection troubleshooting (how to set ARTICLE_SELECTOR for non-standard sites)
- [ ] 9.3 API reference for /cdn/provision, /cdn/sign, /cdn/manifest, /cdn/claim
- [ ] 9.4 Architecture diagram (data flow, caching, provisioning)
- [ ] 9.5 FAQ: what is signed, what is stored, IP ownership, copy-paste survival

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Marker embedding over meta tag | Embed VS markers in text nodes | Meta tags die on copy-paste. Markers survive. Copy-paste survivability is the differentiator. |
| Byte-level HTML manipulation over HTMLRewriter | Port Ghost fragment/embed approach | Proven algorithm, handles entities/whitespace/inline elements. No two-pass requirement. Portable to other CDN platforms later. |
| Backend-controlled tier gating | Org tier in DB, not worker config | Publisher never reconfigures worker. Upgrade = payment in dashboard. Simplest possible UX. |
| Worker as domain verification | .well-known endpoint served by worker | Deploying a Worker on a domain proves zone control. Stronger than DNS TXT records. Zero extra steps. |
| Auto-provisioning over account-first | Provision on first request | Zero friction. Publisher deploys, worker works. Account claiming is optional. |
| Content detection chain over single method | 7-priority fallback chain | No single selector covers all CMSes. WordPress alone needs multiple selectors. Fallback chain maximizes coverage. |
| KV cache for embedding plans | Cache per content hash | Articles are stable. Cache plan for 1 hour. 99%+ of pageviews hit cache. API call only on new/updated articles. |
| Fail-open on all errors | Serve unmodified HTML | Never break a publisher's site. Provenance is additive. If anything fails, the reader gets the normal page. |

## Phasing

**Phase 1 (Backend + Worker Core):** Tasks 1.0, 2.0, 3.0, 4.0, 5.0, 8.1-8.5
- New backend endpoints, service, model
- Worker with boundary detection, fragment extraction, embedding plan application
- Full test suite including CMS-specific HTML fixtures
- This phase delivers the publishable free-tier product

**Phase 2 (Dashboard + Claiming):** Tasks 6.0, 7.0, 9.0
- Dashboard CDN domain management and analytics
- Account claiming flow
- GitHub repo, Deploy button, landing page
- Documentation

**Phase 3 (Multi-CDN):** Separate PRD
- Lambda@Edge and Fastly Compute ports of the worker
- These platforms lack HTMLRewriter but the byte-level approach works everywhere

**Phase 4 (Enterprise Edge Fingerprinting):** Separate PRD (see CDN_Edge_Signing_Leak_Detection.md)
- Per-session WASM fingerprinting at edge
- Requires CIP patent filing and privacy framework (P0 prerequisites)

## Success Criteria

- Worker deploys via one-click Deploy button with zero configuration
- Boundary detection correctly identifies article text on WordPress, Ghost, Squarespace, Webflow, Substack, Jekyll, Hugo sites
- Embedding plan applies to HTML without corrupting visible text (fail-safe verified)
- Embedded markers survive copy-paste from Chrome, Firefox, Safari
- Embedded markers verify successfully via public verification API
- Cache hit rate >95% for steady-state publisher traffic
- Auto-provisioning creates org on first request, cross-channel resolution works
- Domain claiming via .well-known verification completes in <30 seconds
- Dashboard upgrade to Enterprise takes effect on next cache miss without worker reconfiguration
- Publisher setup: deploy to signing in under 5 minutes

## Completion Notes

(Filled when PRD is complete.)
