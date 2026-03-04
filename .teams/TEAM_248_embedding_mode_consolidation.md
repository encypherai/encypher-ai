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

## Final Test Results (session 1)
- 1563 passed, 44 skipped (after all observability + SSOT + simplification changes)
- All ruff checks pass across all modified files

## VS256 ECC Verification Fix (TEAM_248 continuation - session 2)

### Root Cause Analysis: post 37 (micro+ecc+embed_c2pa) fails Chrome/paste verification

1. **WS normalization works correctly**: Mathematically verified that
   `re.sub(r"\s+", " ", chrome_text).strip() == wp_text` and hashes match.
   The WS normalization code in endpoints.py is correct and handles Chrome/paste.

2. **VS256 detection was broken for ECC format**:
   - `vs256_detect.py` only looked for 36-char signatures (SIGNATURE_CHARS = 36)
   - The new micro+ecc signing produces **44-char** signatures (4 magic + 40 RS payload)
   - VS256 fallback in the verify service therefore found ZERO signatures in post 37
   - This meant the fallback could not attribute sentences or resolve the org

3. **DB resolve key mismatch**:
   - New micro+ecc signing stores `embedding_metadata["log_id"] = log_id.hex()`
     (16-byte hex without dashes, e.g. "a1b2c3d4e5f67890abcdef1234567890")
   - Old ZWC signing stored `embedding_metadata["segment_uuid"]` (UUID with dashes)
   - The resolve SQL only checked `embedding_metadata->>'segment_uuid'`
   - Even if ECC signatures were found, their log_id couldn't be resolved from DB
   - This is what the user called "swapping to use log seq#"

### Fixes Applied

**`services/verification-service/app/utils/vs256_detect.py`**:
- Added `ECC_SIGNATURE_CHARS = 44` constant
- Updated `find_vs256_signatures()` to detect both 36 and 44-char sigs
  (tries 44-char ECC first at each magic prefix)
- Updated `extract_uuid_from_vs256_signature()` to handle 44-char format:
  RS decode 40-byte payload -> 32 data bytes, UUID = bytes[:16]
- Updated `reassemble_signature_from_distributed()` to try 44-char ECC first
- All changes backward-compatible with 36-char legacy signatures

**`enterprise_api/app/api/v1/public/c2pa.py`**:
- Single-resolve SQL: added `OR embedding_metadata->>'log_id' = REPLACE(:seg_uuid, '-', '')`
- Bulk-resolve SQL: added `OR embedding_metadata->>'log_id' = ANY(:log_id_hexes)`
  and post-processing to match log_id hex back to input UUID string

**`services/verification-service/tests/test_vs256_detect.py`**:
- Added 7 new tests in `TestECCSignatureDetection` class covering:
  - 44-char ECC detection
  - ECC preferred over 36-char on same magic prefix
  - UUID extraction from 44-char ECC signature
  - Roundtrip with find_vs256_signatures
  - Mixed 36 and 44-char sigs in same text
  - UUID-to-log_id-hex format conversion (critical for DB lookup)
  - Reassembly from distributed VS chars

**Test results**: 91 passed, 0 failed (verification-service), all ruff checks pass

### Key Insight
The "log seq#" the user mentioned = the `log_id` field. When micro+ecc signing
was added, the DB key changed from `segment_uuid` to `log_id`, breaking the
VS256 fallback path in the verification service. The primary C2PA path (COSE +
WS normalization) was always correct but the VS256 sentence-attribution fallback
was completely blind to the new format.

### Commit Message Suggestion
```
fix(verification): support 44-char ECC signatures and log_id DB lookup

vs256_detect.py: detect both 36-char (legacy) and 44-char (ECC) VS256
signatures; try ECC format first at each magic prefix position; update
UUID extraction to RS-decode 40-byte payloads for ECC format; update
reassemble_from_distributed to prefer 44-char.

enterprise_api c2pa.py: extend single and bulk resolve SQL to also match
embedding_metadata->>'log_id' (new micro+ecc format stores hex log_id
without dashes) in addition to segment_uuid (old ZWC/VS256 format).

The new micro+ecc signing (post 37) stored log_id not segment_uuid in
embedding_metadata, breaking VS256 sentence attribution fallback. Primary
C2PA path (COSE + WS normalization) was always correct.
```

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
