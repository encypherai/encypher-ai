# TEAM_248 - Embedding Mode Consolidation

## Status: COMPLETE

## Summary
Consolidated embedding modes: removed dead modes (lightweight_uuid, minimal_uuid, hybrid,
zw_embedding), deleted zw_crypto.py, renamed ZW6->legacy_safe, added legacy_safe_rs ECC variant,
wired legacy_safe flag into micro mode routing, and fixed all stale docstring references.

## Context
Previous session (TEAM_247) completed hyperscale test migration (1556 passed).
This session implements the embedding architecture simplification decided in TEAM_247:
- Only `full` and `micro` modes remain (others were never used in production)
- `zw_crypto.py` used only for internal testing, never production -> deleted
- ZW6 renamed to `legacy_safe` (also works better in terminals)
- Reed-Solomon ECC applied to legacy_safe -> `micro + ecc=True + legacy_safe=True`
- `embed_c2pa=True` already unified with `full` mode (same UnicodeMetadata.embed_metadata call)

## Architecture Decisions
- 4 micro combinations after changes:
  | ecc | legacy_safe | Module | Chars |
  |-----|-------------|--------|-------|
  | False | False | VS256 | 36 |
  | True | False | VS256-RS | 44 (DEFAULT) |
  | False | True | legacy_safe | 100 |
  | True | True | legacy_safe_rs | 112 |
- ZW6-RS math: 36 bytes total -> ceil(36*8*log(2)/log(6)) = 112 base-6 chars
- Detection: length-based (100 chars = legacy_safe, 112 chars = legacy_safe_rs)
- Legacy safe chars: ZWNJ, ZWJ, CGJ, MVS, LRM, RLM (base-6)

## Tasks
- [x] Phase 1: Remove dead modes + zw_crypto.py + dead test files -- completed in commit 64b5c779
- [x] Phase 2: Rename ZW6 -> legacy_safe -- completed in commit 64b5c779
- [x] Phase 3: Build legacy_safe_rs_crypto.py + tests -- completed in commit 64b5c779
- [x] Phase 4: Wire legacy_safe flag into SignOptions + routing -- completed in commit 64b5c779
- [x] Phase 5: C2PA unity test (test_c2pa_unity.py, 6 tests) -- completed in commit 64b5c779
- [x] Cleanup: fix stale zw_embedding/zw_crypto.py refs in vs256_crypto.py comments
- [x] Cleanup: fix stale lightweight_uuid/hybrid in streaming_merkle_service.py docstring
- [x] Cleanup: fix dead mode choices in scripts/sign_blog_posts.py
- [x] Create test_micro_legacy_safe.py (48 unit tests for legacy_safe encoding/decoding)

## Files DELETED
- app/utils/zw_crypto.py
- tests/test_sign_advanced_lightweight_uuid.py
- tests/test_sign_advanced_minimal_uuid.py
- tests/test_sign_advanced_zw_embedding.py
- tests/test_public_extract_and_verify_minimal_uuid.py
- tests/test_zw_crypto.py
- tests/test_zw_minimal_no_magic.py
- tests/debug_zw_response.py
- tests/interactive_word_test.py
- tests/e2e_local/test_local_zw_embedding.py

## Files RENAMED
- app/utils/zw6_crypto.py -> app/utils/legacy_safe_crypto.py
- tests/test_zw6_crypto.py -> tests/test_legacy_safe_crypto.py

## Files CREATED
- app/utils/legacy_safe_rs_crypto.py
- tests/test_legacy_safe_rs_crypto.py
- tests/test_micro_legacy_safe.py (48 tests covering constants, round-trips, key derivation,
  embed/extract, length-based detection, invalid inputs, alphabet properties)
- tests/test_c2pa_unity.py (6 tests verifying C2PA manifests across all micro variants)

## Files MODIFIED (cleanup)
- app/utils/vs256_crypto.py: updated comments from zw_embedding/zw_crypto.py -> legacy_safe/legacy_safe_crypto.py
- app/services/streaming_merkle_service.py: docstring full/lightweight_uuid/hybrid -> full or micro
- scripts/sign_blog_posts.py: choices removed dead modes, now only ["full", "micro"]

## Observability Fixes (TEAM_248 continuation)
- P0: logger.warning() before all silent 403/429s in signing.py (proxy tier, batch limit) and quota.py (feature gating, quota exceeded)
- P1: write_api_audit_log() helper in audit.py + asyncio.create_task wiring in signing.py (DOCUMENT_SIGNED, BATCH_SIGN_COMPLETED) and verify.py (DOCUMENT_VERIFIED)
- P2: x-request-id forwarded on all outbound httpx calls: api_key_auth.py (key-service validate) and auth_service_client.py (3 endpoints)
- P3: /readyz in main.py now probes key-service and auth-service via asyncio.gather with 2s timeout; returns degraded if either is down
- P4: OpenTelemetry tracing added; app/observability/tracing.py with setup_tracing()/shutdown_tracing(); auto-instruments FastAPI + httpx; opt-in via OTEL_EXPORTER_OTLP_ENDPOINT env var (no-op/safe when unset)

## Additional Simplification (TEAM_248 continuation)
- Deleted dead TextEmbedder, MarkdownEmbedder classes (app/utils/embeddings/)
- Deleted test_embedding_api.py (all tests were pytestmark=skip)
- vs256_crypto.py: removed duplicate embed_signature_safely, uses legacy_safe_crypto version via import alias
- SSOT violations fixed: LEGACY_TIER_MAP, QUOTA_FIELD_MAPPING, is_enterprise_tier(), coerce_tier_name() all now come from tier_config.py in 6 files that previously inlined copies

## Final Test Results
- 1563 passed, 44 skipped (after all observability + SSOT + simplification changes)
- All ruff checks pass across all modified files

## Commit Message Suggestion (comprehensive for all work this session)
```
refactor(observability,embeddings,ssot): mode consolidation, SSOT cleanup, and full observability

Embedding mode consolidation:
- Remove dead modes: lightweight_uuid, minimal_uuid, hybrid, zw_embedding
- Delete zw_crypto.py (test-only, never production)
- Rename zw6_crypto.py -> legacy_safe_crypto.py
- Add legacy_safe_rs_crypto.py (RS ECC variant, 112 base-6 chars)
- Wire legacy_safe flag into SignOptions + micro routing (4 sub-combinations)
- Add test_micro_legacy_safe.py (48 tests), test_c2pa_unity.py (6 tests)

Dead code removal:
- Delete TextEmbedder, MarkdownEmbedder (never imported in production)
- Delete test_embedding_api.py (entirely skipped)
- embeddings/__init__.py: replace dead re-exports with orientation comment

SSOT violations resolved:
- LEGACY_TIER_MAP: was duplicated in quota.py, tier_service.py, pricing.py, provisioning_service.py -> all now use tier_config.py
- QUOTA_FIELD_MAPPING: was duplicated inline in quota.py + tier_service.py -> single constant in quota.py
- is_enterprise_tier(): was inlined in embedding_executor.py + multi_source.py -> both now call tier_config.py
- _coerce_tier(): was duplicated in quota.py + tier_service.py -> both now call LEGACY_TIER_MAP

Observability (P0-P4):
- P0: logger.warning before all silent 403/429 responses in signing.py + quota.py (4 sites)
- P1: write_api_audit_log() helper in audit.py; wired into signing.py (DOCUMENT_SIGNED, BATCH_SIGN_COMPLETED) and verify.py (DOCUMENT_VERIFIED) via asyncio.create_task
- P2: x-request-id forwarded in all outbound httpx calls (api_key_auth.py, auth_service_client.py)
- P3: /readyz probes key-service + auth-service with 2s timeout; returns degraded if either is down
- P4: OpenTelemetry tracing (app/observability/tracing.py); auto-instruments FastAPI + httpx; opt-in via OTEL_EXPORTER_OTLP_ENDPOINT (safe no-op when unset)
```
