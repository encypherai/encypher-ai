# TEAM_273 - Unified Verify Endpoint

**Status**: COMPLETE (Phase 1 + Phase 2)
**PRD**: PRDs/CURRENT/PRD_Unified_Verify_Endpoint.md
**Started**: 2026-03-23

## Objective
Consolidate 13 verification endpoints into a single smart `POST /api/v1/verify` that auto-detects content type and routes appropriately. Phase 2: wire up all advanced features (Merkle tamper detection, attribution, plagiarism, fuzzy search, print fingerprint) with optional auth and tier gating.

## Session Log

### Phase 1
- Read full verification codebase: 13 endpoints, 7 response schemas, 2 incompatible SignerIdentity models
- C2PA verification already unified internally (all media types call verify_c2pa())
- Designed unified endpoint with Content-Type routing, unified response envelope
- Plan approved by user
- Implemented: schemas, service layer, endpoints, tests, deprecation markers
- All 230 tests pass (30 new + 200 existing), lint clean

### Phase 2
- Analyzed /verify/advanced handler (466 lines) -- identified all features to port
- Analyzed auth patterns (optional API key via get_api_key_from_header)
- Added VerifyOptions fields: include_heat_map, fuzzy_*, min_match_percentage default change
- Ported _extract_manifest_metadata and _build_localization_events from verification.py
- Implemented 6 composable async functions: run_merkle_verification, run_attribution, run_plagiarism, run_fuzzy_search, run_print_fingerprint, resolve_rights
- Wired all into verify_text() with graceful error handling per feature
- Added optional auth to unified endpoint: API key resolves org context
- Added tier gating: Enterprise for fuzzy_search + search_scope=all
- Added quota checks: attribution, plagiarism, fuzzy via QuotaManager
- 24 new unit tests (49 total), all pass, lint clean
- Updated README endpoint tables + tier matrix
- Updated sdk/openapi.public.json with paths + schemas
- Updated Postman collection with 3 unified verify examples

## Files Modified (Phase 2)
- enterprise_api/app/schemas/verify_schemas.py -- Added include_heat_map, fuzzy_* fields to VerifyOptions
- enterprise_api/app/services/unified_verify_service.py -- Added 6 advanced feature functions, updated verify_text()
- enterprise_api/app/api/v1/public/verify.py -- Added optional auth, tier gating, quota checks, _requires_auth/_requires_enterprise helpers
- enterprise_api/tests/test_unified_verify.py -- 24 new tests for advanced features
- enterprise_api/README.md -- Updated endpoint tables, tier matrix, deprecation markers
- sdk/openapi.public.json -- Added unified paths + schemas (UnifiedVerifyRequest, VerifyOptions, UnifiedVerifyResponse, SignerInfo, ContentInfo, VerifyDocument)
- docs/postman/enterprise_api.postman_collection.json -- Added 3 unified verify examples

## Design Decisions
- CDN endpoints to be folded in (user decision) -- not yet implemented, Phase 3
- Quote integrity excluded (not cryptographic verification)
- GET /verify/{ref_id} unchanged (reference lookup, different operation)
- Rich article excluded this round (compound multi-asset, revisit later)
- Optional auth pattern: API key via Authorization header, matches existing public endpoints
- Tier gating at endpoint level, quota checks at endpoint level, service is auth-agnostic
- Each advanced feature is a composable async function with try/except (graceful degradation)
- Print fingerprint always runs (passive, cheap, no auth needed) unless explicitly disabled

## Hardening Backlog (from verification analysis)
1. Verify ALL signatures, not just the first (highest-impact gap)
2. Bind document_id + leaf_index into HMAC (prevent cross-document transplant)
3. Demo key path DB lookup (bring free-tier to same verification standard)

## Suggested Commit Message

```
feat(enterprise-api): wire up advanced features in unified verify endpoint

Port all advanced verification features from /verify/advanced into
the unified POST /api/v1/public/verify endpoint:

- Merkle root verification + tamper localization (difflib SequenceMatcher)
- Source attribution (MerkleService.find_sources)
- Plagiarism detection (MerkleService.generate_attribution_report)
- Fuzzy fingerprint search (Enterprise-gated, FuzzySearchConfig)
- Print leak detection (passive, decode_print_fingerprint)
- Rights resolution (ContentReference lookup)

Auth & tier gating:
- Optional API key for advanced features (attribution, plagiarism,
  fuzzy search, cross-org scope)
- Enterprise tier required for fuzzy_search and search_scope=all
- Quota enforcement via QuotaManager before expensive operations

Documentation:
- Updated README endpoint tables and tier matrix
- Added unified schemas to sdk/openapi.public.json
- Added 3 Postman collection examples (text, advanced, media)

Tests: 24 new unit tests (49 total), all pass, lint clean.
```
