# TEAM_249 — CDN Provenance Continuity

## Session
Phase 1 MVP implementation: publisher provenance continuity layer for CDN-transformed images.

## Objectives
1. `CdnImageRecord` model + alembic migration
2. `CdnProvenanceService` — register_image, lookup_by_phash, pre_register_variants
3. `image_signing_executor.py` — pHash registration + C2PA image signing
4. `cdn_provenance.py` router — 5 new endpoints
5. Org model: cdn_provenance_enabled, cdn_image_registrations_this_month
6. Quota: CDN_IMAGE_REGISTRATIONS type + tier limits
7. Verification service: pHash sidecar fallback path
8. Cloudflare Worker + wrangler config template
9. WordPress HTML parser: remove image block skip rules
10. Tests

## Status
- [x] Team file created
- [x] PRD created — PRDs/CURRENT/PRD_CDN_Provenance_Continuity.md
- [x] Phase 1 — 16/16 tests pass
- [x] Phase 2 — 18/18 analytics tests + WordPress media signing + logpush image attribution
- [x] Phase 3 — Fastly Compute@Edge (Rust), Lambda@Edge (Node.js), Ghost image signing, CBOR manifests, well-known alias
- [x] Tests — 36/36 pass (pytest), ruff clean

## Handoff
All phases complete. Ready for design partner deployment.

## Suggested Commit Message
```
feat(cdn-provenance): Phase 1 MVP — publisher provenance continuity layer

- CdnImageRecord model + migration (20260310_100000)
- CdnProvenanceService: register_image, lookup_by_phash (Hamming ≤8), pre_register_variants
- image_signing_executor: C2PA sign → pHash register → return record_id
- cdn_provenance router: 7 endpoints (/images/sign, /images/register,
  /manifests/{id}, /manifests/lookup, /images/{id}/variants, /verify, /verify/url)
- Three-state verification: ORIGINAL_SIGNED | VERIFIED_DERIVATIVE | PROVENANCE_LOST
- Cloudflare Worker: edge header injection + KV caching (wrangler.toml.template)
- WordPress HTML parser: removed image/picture/wp:image block skip rules
- Quota: CDN_IMAGE_REGISTRATIONS (Enterprise-only)
- 16/16 tests pass

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```
