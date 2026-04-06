# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2026-04-04

### Added
- Segment-level rights (Enterprise)
  - Per-segment `RightsMetadata` mappings via `segment_rights` field on `SignOptions`
  - `com.encypher.rights.v2` compound C2PA assertion mapping segment indices to rights profiles
  - Segments without explicit mapping inherit document-level `options.rights`
  - Tier-gated: Enterprise and strategic_partner only
  - Index validation against actual segment count at signing time (422 if out of bounds)
- Audio soft-binding watermarking (Enterprise)
  - New `audio-watermark-service` microservice (port 8011) using time-domain spread-spectrum embedding
  - 64-bit payload embedded directly in audio signal, survives MP3 re-encoding and loudness normalization
  - `enable_audio_watermark` form field on `POST /sign/media` (audio files only)
  - `c2pa.soft_binding.v1` assertion added to C2PA manifest when watermarking enabled
  - Enterprise API client (`audio_watermark_client.py`) mirroring TrustMark pattern
  - Combined C2PA + watermark verification via `/verify/audio` endpoint
  - Tier-gated: Enterprise and strategic_partner only
- Video spread-spectrum watermarking (Enterprise)
  - New `video-watermark-service` microservice (port 8012) using frame-domain spread-spectrum embedding
  - Supports VOD files and live stream segments
  - Combined C2PA + watermark verification via `/verify/video` endpoint
  - `encypher.spread_spectrum_video.v1` method identifier
  - Tier-gated: Enterprise and strategic_partner only
- Concatenated ECC for audio and video watermarks
  - Shared ECC module at `services/shared/` (RS(32,8) outer code + rate-1/3 K=7 convolutional inner code + soft Viterbi decoder)
  - Method identifier: `rs32_8_conv_r3_k7`
  - Applied to both `audio-watermark-service` and `video-watermark-service`
- Image soft-binding watermarking via TrustMark (Enterprise)
  - `enable_image_watermark` form field on `POST /sign/media` (image files only)
  - TrustMark neural watermark (100-bit payload, Adobe Research, Apache 2.0)
  - `c2pa.soft_binding.v1` assertion added to C2PA manifest when watermarking enabled
  - TrustMark detection wired into `/verify/image` endpoint (best-effort, non-blocking)
  - `ImageWatermarkRecord` model and `image_watermark_records` migration for persistence
  - `TrustMarkClient` refactored to inherit `WatermarkClientBase` (connection pooling)
  - Tier-gated: Enterprise and strategic_partner only

### Changed
- Consolidated `RightsMetadata` to single source of truth in `sign_schemas.py` (removed duplicates from `embeddings.py` and `request_models.py`)
- Refactored watermark application to shared helper (`apply_watermark_to_signed_audio`) eliminating duplication between `media_signing.py` and `audio_signing_executor.py`
- Upgraded PN sequence RNG from `RandomState(4 bytes)` to `default_rng(SeedSequence(32 bytes))` for full HMAC entropy

## [1.1.0] - 2026-03-21

### Added
- Video C2PA signing and verification (`/enterprise/video/sign`, `/enterprise/video/verify`, `/enterprise/video/download/{video_id}`)
  - Supported formats: MP4, MOV, M4V (ISO BMFF), AVI (RIFF)
  - Multipart upload (not base64) for files up to 500 MB
  - Large file download endpoint for signed files > 50 MB (10-min TTL cache)
  - Magic byte detection: ftyp (ISO BMFF), RIFF+AVI, EBML (rejected with clear error)
- Live video stream C2PA signing (C2PA 2.3 Section 19)
  - REST-based session lifecycle: start, segment, finalize, status
  - Per-segment C2PA manifest with backwards-linked provenance chain (`com.encypher.stream.chain.v1`)
  - Merkle root computation over all segment manifest hashes on finalize
  - Session-cached signing credentials (1-hour TTL, 5-min idle timeout)
- Audio C2PA signing and verification (`/enterprise/audio/sign`, `/enterprise/audio/verify`)
  - Supported formats: WAV (RIFF), MP3 (ID3), M4A/AAC (ISO BMFF)
  - Per-org credential loading via Organization model
  - C2PA v2.3 audio actions: c2pa.created, c2pa.dubbed, c2pa.mixed, c2pa.mastered, c2pa.remixed
- Shared C2PA modules extracted from image pipeline (c2pa_signer, c2pa_manifest, c2pa_verifier_core, hashing)
- Generic `SIGNING_PASSTHROUGH` config flag (supersedes `IMAGE_SIGNING_PASSTHROUGH` for non-image media)

### Security
- Sanitized error messages in signing executors (audio, video) to prevent internal detail leakage
- Added enterprise tier gate to audio C2PA endpoints
- Sanitized c2pa-rs error messages in verifier core
- Added XMP XML attribute escaping to prevent injection in image provenance metadata

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
