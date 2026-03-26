# PRD: Unified Verify Endpoint

**Status**: COMPLETE (Phase 2)
**Current Goal**: Phase 2 complete -- advanced features wired up, auth/tier gating, docs updated
**Team**: TEAM_273

## Overview
Consolidate 13 verification endpoints (text, image, audio, video, advanced, batch, rich, CDN) into a single smart endpoint that auto-detects content type and routes to the appropriate verification logic. Phase 1 covers text + C2PA media (image, audio, video). Phase 2 wires up all advanced features with optional auth.

## Objectives
- Single entry point for all content verification
- Auto-detect content type from Content-Type header + magic bytes
- Unified response envelope across all media types
- Optional flags for advanced features (tamper localization, attribution, fuzzy search)
- Optional auth for advanced features, Enterprise tier for fuzzy/cross-org
- Deprecation path for old endpoints

## Tasks

### Phase 1 -- Schemas + Basic Routing (COMPLETE)
- [x] 1.1 Create verify_schemas.py with UnifiedVerifyRequest, VerifyOptions, VerifyDocument -- pytest
- [x] 1.2 Create UnifiedVerifyResponse, SignerInfo, ContentInfo response models -- pytest
- [x] 2.1 Write unit tests for unified verify service (routing logic, response mapping) -- pytest (25 unit tests)
- [x] 2.2 Write integration tests for unified verify endpoint (text, media, error cases) -- pytest (5 integration tests)
- [x] 3.1 Create unified_verify_service.py with media type detection (classify_mime) -- pytest
- [x] 3.2 Implement text verification path (delegates to execute_verification) -- pytest
- [x] 3.3 Implement media verification path (delegates to verify_*_c2pa) -- pytest
- [x] 3.4 Implement response mapping (VerificationExecution/C2paVerificationResult -> UnifiedVerifyResponse) -- pytest
- [x] 4.1 Add POST /api/v1/public/verify JSON route (text + batch) -- pytest
- [x] 4.2 Add POST /api/v1/public/verify/media multipart route (binary media) -- pytest
- [x] 4.3 Wire up rate limiting, DB sessions -- pytest
- [x] 5.1 Add deprecated=True + Deprecation/Sunset headers to verify-text, verify/image, verify/audio, verify/video, verify/advanced
- [x] 5.2 Keep old endpoints functional (Phase 1 -- no redirects yet)

### Phase 2 -- Advanced Features (COMPLETE)
- [x] 6.1 Add VerifyOptions fields: include_heat_map, fuzzy_similarity_threshold, fuzzy_max_candidates, fuzzy_fallback_when_no_binding -- pytest
- [x] 6.2 Port _extract_manifest_metadata from verification.py -- pytest
- [x] 6.3 Port _build_localization_events from verification.py -- pytest
- [x] 6.4 Implement run_merkle_verification (Merkle root + tamper localization) -- pytest
- [x] 6.5 Implement run_attribution (MerkleService.find_sources) -- pytest
- [x] 6.6 Implement run_plagiarism (MerkleService.generate_attribution_report) -- pytest
- [x] 6.7 Implement run_fuzzy_search (fuzzy_fingerprint_service.search) -- pytest
- [x] 6.8 Implement run_print_fingerprint (decode_print_fingerprint) -- pytest
- [x] 6.9 Implement resolve_rights (ContentReference lookup) -- pytest
- [x] 6.10 Wire all advanced features into verify_text() -- pytest
- [x] 6.11 Add optional auth (API key) to unified endpoint -- pytest
- [x] 6.12 Add tier gating (Enterprise for fuzzy + cross-org scope) -- pytest
- [x] 6.13 Add quota checks (attribution, plagiarism, fuzzy search) -- pytest
- [x] 6.14 Write 24 new unit tests for advanced features -- pytest (49 total unit tests)
- [x] 6.15 All tests pass (49 unit + 5 integration) -- pytest
- [x] 6.16 Lint clean (ruff check + format) -- ruff

### Phase 2 -- Documentation (COMPLETE)
- [x] 7.1 Update enterprise_api/README.md endpoint tables + tier matrix
- [x] 7.2 Add unified schemas to sdk/openapi.public.json (paths + component schemas)
- [x] 7.3 Add unified verify examples to Postman collection

## Success Criteria
- Single POST /api/v1/public/verify handles text (JSON body) with full advanced features
- Single POST /api/v1/public/verify/media handles image, audio, video (multipart)
- Response envelope is consistent regardless of media type
- Advanced features (Merkle tamper, attribution, plagiarism, fuzzy, print fingerprint) fully functional
- Optional auth: basic verify public, advanced requires API key, Enterprise for fuzzy/cross-org
- Quota enforcement for attribution, plagiarism, fuzzy search
- Old endpoints still work with deprecation markers
- All tests pass, lint clean
- Documentation updated (README, OpenAPI, Postman)

## Completion Notes
- Text endpoint: POST /api/v1/public/verify with {"text": "..."} or {"documents": [...]}
- Media endpoint: POST /api/v1/public/verify/media with multipart file upload
- Separate paths required because FastAPI cannot route by Content-Type on the same path
- Deprecated endpoints: verify-text, verify/image, verify/audio, verify/video, verify/advanced
- Advanced features ported from /verify/advanced into unified_verify_service.py as composable functions
- Auth pattern: optional API key via Authorization header (matches existing public endpoint pattern)
- Tier gating: fuzzy_search and search_scope=all require Enterprise/strategic_partner/demo
- Quota checks happen at endpoint level before service calls (clean separation)
- Phase 3 (future): redirect old endpoints to unified, remove deprecated code
