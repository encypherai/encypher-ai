# PRD: CDN Provenance Continuity

**Status:** In Progress
**Team:** TEAM_249
**Current Goal:** Phase 1 MVP — Cloudflare-first provenance continuity for CDN-transformed images

## Overview
Publishers' CDNs strip C2PA provenance metadata when transforming images (resize, reformat, recompress). This builds a publisher provenance continuity layer — delivered through their existing CDN — that makes C2PA provenance survive real-world publisher delivery pipelines.

**Positioning:** Encypher makes C2PA provenance survive real-world publisher delivery pipelines, starting with CDN-transformed images.

## Objectives
- Sign images and store C2PA manifests server-side (indexed by pHash + SHA-256)
- Track derivative relationships as a lightweight graph
- Expose durable manifest lookup URL that survives any CDN transformation
- Cloudflare Worker injects `C2PA-Manifest-URL` header on image responses
- Verification endpoint returns three-state result: `ORIGINAL_SIGNED`, `VERIFIED_DERIVATIVE`, `PROVENANCE_LOST`

## Tasks

### 1.0 Backend Core
- [ ] 1.1 `CdnImageRecord` model (cdn_image_records table)
- [ ] 1.2 Alembic migration
- [ ] 1.3 `CdnProvenanceService` — register_image, lookup_by_phash, pre_register_variants
- [ ] 1.4 `image_signing_executor.py` — higher-level image signing with pHash registration
- [ ] 1.5 `cdn_provenance.py` router — 7 endpoints
- [ ] 1.6 CDN schemas (Pydantic)
- [ ] 1.7 Organization model: cdn_provenance_enabled, cdn_image_registrations_this_month
- [ ] 1.8 Quota: CDN_IMAGE_REGISTRATIONS type + tier limits
- [ ] 1.9 Router registration

### 2.0 Cloudflare Worker
- [ ] 2.1 `cdn-provenance-worker.js` — edge manifest injection
- [ ] 2.2 `wrangler.toml.template` — deployment config
- [ ] 2.3 `generate-worker-config` API endpoint

### 3.0 WordPress Integration
- [ ] 3.1 Remove image block skip rules from HTML parser

### 4.0 Tests
- [ ] 4.1 CdnProvenanceService unit tests
- [ ] 4.2 Router endpoint tests

## Success Criteria
- Sign JPEG → get record_id + signed bytes
- Simulate CDN transform (Pillow resize/WebP) → POST /cdn/verify → returns VERIFIED_DERIVATIVE
- POST unrelated image → returns PROVENANCE_LOST
- CF Worker deployed → C2PA-Manifest-URL header appears on image responses
