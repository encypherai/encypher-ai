# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Audio C2PA signing and verification (`/enterprise/audio/sign`, `/enterprise/audio/verify`)
  - Supported formats: WAV (RIFF), MP3 (ID3), M4A/AAC (ISO BMFF)
  - Per-org credential loading via Organization model
  - C2PA v2.3 audio actions: c2pa.created, c2pa.dubbed, c2pa.mixed, c2pa.mastered, c2pa.remixed
- Shared C2PA modules extracted from image pipeline (c2pa_signer, c2pa_manifest, c2pa_verifier_core, hashing)
- Generic `SIGNING_PASSTHROUGH` config flag (supersedes `IMAGE_SIGNING_PASSTHROUGH` for non-image media)

## [2026-03-10] CDN Provenance Continuity — All Phases

### Summary
Publisher provenance continuity layer that makes C2PA provenance survive CDN image transformations (resize, reformat, recompress). Images signed at origin remain verifiable even after CDN transforms strip the embedded manifest.

**Positioning:** Encypher makes C2PA provenance survive real-world publisher delivery pipelines, starting with CDN-transformed images.

### Phase 1 — Cloudflare-first MVP

**Backend**
- `CdnImageRecord` model (`cdn_image_records` table) — stores pHash (BigInt, 8×8 average hash), SHA-256, JSONB manifest, variant graph (`is_variant`, `parent_record_id`, `transform_description`)
- `CdnProvenanceService` — `register_image()` (idempotent via SHA-256), `lookup_by_phash()` (Hamming distance ≤8 threshold), `pre_register_variants()`
- `image_signing_executor.py` — orchestrates C2PA signing → pHash registration → returns `record_id` + signed bytes
- `cdn_provenance.py` router — 7 new endpoints at `/api/v1/cdn/`:
  - `POST /images/sign` — sign image, store manifest + pHash (Enterprise-gated)
  - `POST /images/register` — register pre-signed image
  - `GET /manifests/{record_id}` — public manifest fetch (JSON or `application/cbor`)
  - `GET /manifests/lookup?url=` — canonical URL lookup
  - `POST /images/{id}/variants` — pre-register CDN variants
  - `POST /verify` — three-state verification (`ORIGINAL_SIGNED` | `VERIFIED_DERIVATIVE` | `PROVENANCE_LOST`)
  - `POST /verify/url` — verify by URL
- `GET /.well-known/c2pa/manifests/{record_id}` — standards-aligned 301 redirect alias (C2PA 2.x §6.4)
- `CDN_IMAGE_REGISTRATIONS` quota type (FREE=blocked, Enterprise=unlimited)
- Migrations: `20260310_100000_add_cdn_image_records.py`, `20260310_110000_add_cdn_attribution_events.py`

**Cloudflare Worker**
- `integrations/cloudflare-workers/cdn-provenance-worker.js` — ES module Worker; strips `/cdn-cgi/image/{opts}/` transform prefix; KV-cached manifest lookup (TTL 3600s); injects `C2PA-Manifest-URL` + `X-Encypher-Provenance` headers; fails open on API errors
- `integrations/cloudflare-workers/wrangler.toml.template` — deployment config template
- `POST /api/v1/cdn/integrations/{id}/generate-worker-config` — returns pre-filled wrangler config + worker script for one-click download

### Phase 2 — WordPress media workflow + Dashboard analytics

**WordPress plugin** (`integrations/wordpress-provenance-plugin/`)
- Removed image/picture/wp:image/wp:gallery/wp:post-featured-image skip rules from HTML parser
- `sign_featured_image()` — called after text signing; POSTs featured image multipart to `/api/v1/cdn/images/sign`; stores `_encypher_image_record_id` + `_encypher_image_manifest_url` in post meta
- `inject_image_provenance_header()` — hooks `send_headers`; emits `C2PA-Manifest-URL` on singular post responses

**Dashboard analytics**
- `CdnAttributionEvent` model — one row per image request tracked via Cloudflare Logpush
- `cdn_analytics.py` router — `GET /cdn/analytics/summary` + `GET /cdn/analytics/timeline?days=N`
- Logpush extension — `_maybe_record_image_attribution()` detects image URIs in batches; strips CDN transform prefix to canonical URL; records `CdnAttributionEvent` rows (best-effort, fail-open)

### Phase 3 — Multi-CDN + Broader CMS

- `integrations/fastly-compute/src/main.rs` — Rust Compute@Edge handler; uses Edge Dictionary for config; same header injection pattern; fails open
- `integrations/lambda-edge/cdn-provenance-handler.mjs` — Node.js ESM viewer-response handler for CloudFront; in-process TTL cache (1h positive / 5min negative); 3s timeout; fails open
- Ghost CMS: `signFeaturedImage()` in `signer.ts` — fetches feature image after text signing; POSTs to `/cdn/images/sign` (fire-and-forget); `postFormData()` on `EncypherClient`; `ImageSigningRecord` in `MetadataStore`
- `GET /api/v1/cdn/manifests/{id}` now supports `Accept: application/cbor` → returns `cbor2`-encoded manifest for standards-native clients

### Tests
- 36 pytest tests across `test_cdn_provenance.py` and `test_cdn_analytics.py`
- Coverage: service register/idempotency/pHash lookup, Hamming distance edge cases, endpoint auth/quota gating, CBOR response, well-known 301 redirect, analytics summary/timeline, image URI detection in Logpush
