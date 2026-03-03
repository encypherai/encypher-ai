# TEAM_248 - Embedding Mode Consolidation

## Status: IN PROGRESS

## Summary
Consolidate embedding modes: remove dead modes (lightweight_uuid, minimal_uuid, hybrid,
zw_embedding), delete zw_crypto.py, rename ZW6->legacy_safe, add legacy_safe_rs ECC variant,
and wire legacy_safe flag into micro mode routing.

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
- [ ] Phase 1: Remove dead modes + zw_crypto.py + dead test files
- [ ] Phase 2: Rename ZW6 -> legacy_safe
- [ ] Phase 3: Build legacy_safe_rs_crypto.py + tests
- [ ] Phase 4: Wire legacy_safe flag into SignOptions + routing
- [ ] Phase 5: Verify C2PA unity test

## Files to DELETE
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

## Files to RENAME
- app/utils/zw6_crypto.py -> app/utils/legacy_safe_crypto.py
- tests/test_zw6_crypto.py -> tests/test_legacy_safe_crypto.py

## Files to CREATE
- app/utils/legacy_safe_rs_crypto.py
- tests/test_legacy_safe_rs_crypto.py
- tests/test_micro_legacy_safe.py (integration)
- tests/test_c2pa_unity.py (Phase 5)
