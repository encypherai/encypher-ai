# CDN Provenance Continuity — Technical Reference

**Last Updated**: March 10, 2026
**Status**: Production (Phases 1–3 complete)
**Tier**: Enterprise

---

## Problem Statement

CDNs strip C2PA provenance metadata when transforming images (resize, reformat, recompress). A JPEG with a valid C2PA JUMBF manifest becomes an unsigned WebP thumbnail after a typical CDN transform pipeline. This breaks verifiability for images that were correctly signed at origin.

**Solution:** A server-side provenance sidecar indexed by perceptual hash (pHash) and SHA-256. Even when a CDN strips every byte of embedded metadata, the original manifest remains retrievable via a Hamming-distance lookup against the registered pHash.

**One-sentence positioning:**
> Encypher makes C2PA provenance survive real-world publisher delivery pipelines, starting with CDN-transformed images.

---

## Architecture

### Core Model: Asset Identity + Derivative Graph

```
CdnImageRecord
├── id (UUID)
├── organization_id
├── original_url       -- canonical URL before CDN transforms
├── content_sha256     -- "sha256:" + 64 hex chars (post-EXIF-strip, pre-sign)
├── phash              -- signed int64 average hash (8×8 = 64 bits)
├── manifest_store     -- JSONB: full C2PA manifest
├── is_variant         -- True for CDN-transform derivatives
├── parent_record_id   -- FK to self for derivative graph
└── transform_description -- "resize:800x600,webp"
```

### Three-State Verification Model

| State | Meaning | `verification_path` |
|---|---|---|
| `ORIGINAL_SIGNED` | Embedded manifest present and valid, or SHA-256 exact match | `EMBEDDED` or `URL_LOOKUP` |
| `VERIFIED_DERIVATIVE` | No embedded manifest, but pHash lookup found a signed original within Hamming distance 8 | `PHASH_SIDECAR` |
| `PROVENANCE_LOST` | Transform too aggressive; no match found | `NONE` |

### pHash Lookup Algorithm

```python
def _hamming_distance(a: int, b: int) -> int:
    xor = (a & 0xFFFFFFFFFFFFFFFF) ^ (b & 0xFFFFFFFFFFFFFFFF)
    return bin(xor).count('1')
```

Threshold: **8 bits out of 64** (≈87.5% similarity). Acceptable for <10k images per org in Phase 1. Phase 2 can upgrade to PostgreSQL bit-parallel operator for >10k orgs.

---

## API Reference

All endpoints live under `/api/v1/cdn/`. Authenticated endpoints require `Authorization: Bearer <api_key>`.

### Image Signing & Registration

#### `POST /api/v1/cdn/images/sign`
Sign an image, embed C2PA manifest, store pHash + manifest server-side.

**Auth:** Required (Enterprise tier)
**Quota:** `CDN_IMAGE_REGISTRATIONS`
**Body:** `multipart/form-data`
- `file` — image bytes (JPEG, PNG, WebP, TIFF, HEIC; max 10 MB)
- `title` — string (optional)
- `original_url` — canonical URL before CDN transforms (optional but recommended)

**Response 201:**
```json
{
  "record_id": "uuid",
  "manifest_url": "/api/v1/cdn/manifests/{record_id}",
  "image_id": "img_aabbccdd",
  "phash": -4611686018427387904,
  "sha256": "sha256:deadbeef...",
  "signed_image_b64": "base64...",
  "mime_type": "image/jpeg"
}
```

#### `POST /api/v1/cdn/images/register`
Register a pre-signed image without re-signing (for images already signed by other tools).

**Auth:** Required
**Body:** `multipart/form-data` — `file`, `original_url`, `manifest_data` (JSON string, optional)

#### `POST /api/v1/cdn/images/{record_id}/variants`
Pre-register expected CDN transform variants so they can be matched before any request arrives.

**Body:**
```json
{ "transforms": ["resize:800x600", "webp", "q75"] }
```

---

### Manifest Retrieval

#### `GET /api/v1/cdn/manifests/{record_id}`
Fetch the stored C2PA manifest for a record.

**Auth:** None (public endpoint)
**Accept header:**
- `application/json` (default) — JSON manifest
- `application/cbor` — CBOR-encoded manifest (C2PA 2.x §5.3 native format)

**Response 200 (JSON):**
```json
{
  "record_id": "uuid",
  "manifest": { ... },
  "manifest_url": "/api/v1/cdn/manifests/{record_id}"
}
```

#### `GET /api/v1/cdn/manifests/lookup?url=<canonical_url>`
Look up a record by its registered canonical URL. Called by CDN edge workers.

**Auth:** None (public, rate-limited by IP)

#### `GET /.well-known/c2pa/manifests/{record_id}`
Standards-aligned discovery alias (C2PA 2.x §6.4 external manifest URIs). Returns HTTP 301 → `/api/v1/cdn/manifests/{record_id}`.

---

### Verification

#### `POST /api/v1/cdn/verify`
Upload an image and get a provenance verdict.

**Auth:** None (public)
**Body:** `multipart/form-data` — `file`

**Response 200:**
```json
{
  "verdict": "VERIFIED_DERIVATIVE",
  "verification_path": "PHASH_SIDECAR",
  "record_id": "uuid",
  "manifest": { ... },
  "hamming_distance": 3,
  "confidence": 0.95
}
```

Verification pipeline:
1. Extract Encypher XMP from image → if found and manifest exists → `ORIGINAL_SIGNED / EMBEDDED`
2. SHA-256 lookup across all records → if exact match → `ORIGINAL_SIGNED / URL_LOOKUP`
3. pHash Hamming distance scan → if best distance ≤ 8 → `VERIFIED_DERIVATIVE / PHASH_SIDECAR`
4. No match → `PROVENANCE_LOST`

#### `POST /api/v1/cdn/verify/url`
Same as `/verify` but accepts `{"url": "https://..."}` JSON body. Fetches image via HTTP then runs the same pipeline.

---

### Worker Config

#### `POST /api/v1/cdn/integrations/{integration_id}/generate-worker-config`
Returns a pre-filled Cloudflare Worker script + `wrangler.toml` for one-click download.

---

### Analytics

#### `GET /api/v1/cdn/analytics/summary`
**Auth:** Required

```json
{
  "organization_id": "org_xxx",
  "assets_protected": 1423,
  "variants_registered": 287,
  "image_requests_tracked": 94210,
  "recoverable_percent": 1.81
}
```

#### `GET /api/v1/cdn/analytics/timeline?days=30`
Day-by-day counts of images signed + image requests tracked.

---

## CDN Edge Integrations

All three workers implement the same pattern:

1. Intercept image response (detect by `Content-Type`)
2. Strip CDN transform parameters from the request URL to recover the canonical URL
3. Call `GET /api/v1/cdn/manifests/lookup?url=<canonical>` (cached)
4. If found, inject `C2PA-Manifest-URL: https://api.encypher.com/api/v1/cdn/manifests/{id}` response header
5. Fail open — never block image delivery if the API is unavailable

### Cloudflare Worker

**File:** `integrations/cloudflare-workers/cdn-provenance-worker.js`
**Config template:** `integrations/cloudflare-workers/wrangler.toml.template`

Transform stripping: removes `/cdn-cgi/image/{opts}/` path prefix and resize query params (`width`, `height`, `format`, `quality`, `w`, `h`, `q`, `fit`).

Caching: KV namespace (`CDN_PROVENANCE_CACHE`), TTL 3600s positive / 300s negative.

Deployment:
```bash
cp wrangler.toml.template wrangler.toml
# Fill in: account_id, zone_name, KV namespace ID
wrangler deploy
```

### Fastly Compute@Edge (Rust)

**File:** `integrations/fastly-compute/src/main.rs`

Required Fastly backends:
- `origin` — publisher's origin server
- `encypher_api` — `api.encypher.com`

Required Edge Dictionary `encypher_config`:
- `api_base_url` — e.g. `https://api.encypher.com`
- `cache_ttl_s` — e.g. `3600`

Deployment:
```bash
fastly compute publish
```

### Lambda@Edge (CloudFront)

**File:** `integrations/lambda-edge/cdn-provenance-handler.mjs`

Trigger type: **viewer-response** (CloudFront)
Runtime: Node.js 18.x

Caching: In-process `Map` with TTL (1h positive / 5min negative). Note: Lambda@Edge containers are reused across requests; the cache persists within a container lifetime.

Deployment:
```bash
npm run package  # produces function.zip
# Upload to Lambda, associate with CloudFront distribution viewer-response trigger
```

---

## CMS Integrations

### WordPress Plugin

On post publish, after text signing:
1. Reads the featured image file from disk
2. POSTs multipart to `/api/v1/cdn/images/sign`
3. Stores `_encypher_image_record_id` + `_encypher_image_manifest_url` in post meta
4. Hooks `send_headers` to emit `C2PA-Manifest-URL: <url>` on singular post responses

Image MIME types supported: `image/jpeg`, `image/jpg`, `image/png`, `image/webp`

### Ghost CMS

After text signing succeeds, `signFeaturedImage()` fires and-forget:
1. Fetches `post.feature_image` bytes via HTTP
2. POSTs multipart to `/api/v1/cdn/images/sign`
3. Stores `ImageSigningRecord` in `MetadataStore` keyed by `image_{post_id}`

---

## Dashboard Analytics

Analytics data comes from two sources:

1. **`CdnImageRecord`** — every `POST /images/sign` or `/images/register` call
2. **`CdnAttributionEvent`** — populated by Cloudflare Logpush ingestion; `_maybe_record_image_attribution()` detects image URIs (by extension + path hint) and records one event per image request

Metric definitions:
- **Assets protected** — `CdnImageRecord` rows where `is_variant = False`
- **Variants registered** — `CdnImageRecord` rows where `is_variant = True`
- **Image requests tracked** — `CdnAttributionEvent` row count
- **% recoverable** — `(assets_protected + variants_registered) / image_requests_tracked × 100`

---

## Key Files

| File | Purpose |
|---|---|
| `enterprise_api/app/models/cdn_image_record.py` | ORM model |
| `enterprise_api/app/models/cdn_attribution_event.py` | Analytics event model |
| `enterprise_api/app/services/cdn_provenance_service.py` | register / lookup / variants |
| `enterprise_api/app/services/image_signing_executor.py` | High-level sign + register |
| `enterprise_api/app/routers/cdn_provenance.py` | 7 endpoints + well-known router |
| `enterprise_api/app/routers/cdn_analytics.py` | Summary + timeline endpoints |
| `enterprise_api/app/utils/image_utils.py` | pHash, SHA-256, XMP inject/extract |
| `enterprise_api/alembic/versions/20260310_100000_add_cdn_image_records.py` | Migration |
| `enterprise_api/alembic/versions/20260310_110000_add_cdn_attribution_events.py` | Migration |
| `enterprise_api/tests/test_cdn_provenance.py` | 18 tests |
| `enterprise_api/tests/test_cdn_analytics.py` | 18 tests |
| `integrations/cloudflare-workers/cdn-provenance-worker.js` | CF Worker |
| `integrations/fastly-compute/src/main.rs` | Rust Compute@Edge |
| `integrations/lambda-edge/cdn-provenance-handler.mjs` | Lambda@Edge |

---

## Related Documentation

- [C2PA_PROVENANCE_CHAIN.md](./C2PA_PROVENANCE_CHAIN.md) — ingredient references, edit chain
- [docs/image-signing/implementation-guide.md](../image-signing/implementation-guide.md) — image signing pipeline (XMP, pHash, JUMBF layers)
- [PRDs/CURRENT/PRD_CDN_Provenance_Continuity.md](../../PRDs/CURRENT/PRD_CDN_Provenance_Continuity.md) — product requirements

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| pHash fails for aggressive crop/overlay/filter | Pre-register variants at publish time; URL-based fallback; `PROVENANCE_LOST` state is honest, not silent |
| Scale beyond 10k images/org | Upgrade pHash scan to PostgreSQL bit-parallel operator (`<->` with `bit` type) in Phase 2 |
| C2PA standard evolves | Manifest sidecar is standards-aligned (C2PA 2.x §6.4 external manifest URIs); well-known alias ready |
| CDN scope creep | Cloudflare → Fastly → Lambda@Edge already shipped; gate new CDNs on design partner demand |
