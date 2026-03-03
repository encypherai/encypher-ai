# TEAM_247 — Post-Quantum Hyperscale Test Migration

## Status: COMPLETE

## Summary
Migrated all worktree test files from old vs256/zw6 UUID-based API to new bytes-based
hyperscale API (LOG_ID_BYTES=16, MARKER_CHARS=100, PAYLOAD_BYTES=32).

## Context
Previous sessions (TEAM_247 continuation) updated zw6_crypto.py, vs256_crypto.py,
vs256_rs_crypto.py, embedding_service.py, and verification_logic.py in the main repo
for hyperscale safety. This session migrated all test files in the worktree.

## API Changes (old -> new)
- `create_minimal_signed_uuid(uuid4(), key)` -> `create_signed_marker(generate_log_id(), key)`
- `find_all_minimal_signed_uuids(text)` -> `find_all_markers(text)`
- `verify_minimal_signed_uuid(sig, key)` -> `verify_signed_marker(sig, key)` (returns `(bool, bytes)` not `(bool, UUID)`)
- `UUID_BYTES` removed -> `LOG_ID_BYTES = 16`
- `MARKER_CHARS == 75` -> `MARKER_CHARS == 100`
- `PAYLOAD_BYTES == 24` -> `PAYLOAD_BYTES == 32`

## Files Modified

### Crypto test files (primary goal):
- `tests/test_zw6_crypto.py` -- updated constants (MARKER_CHARS=100, PAYLOAD_BYTES=32, LOG_ID_BYTES=16)
- `tests/test_vs256_crypto.py` -- complete rewrite for new API
- `tests/test_vs256_rs_crypto.py` -- complete rewrite for new API
- `tests/test_verification_logic.py` -- small import fix
- `tests/test_email_embedding_survivability.py` -- rewrite for new API
- `tests/test_vs256_word_copypaste.py` -- bulk rename
- `tests/test_micro_c2pa_embedding.py` -- bulk rename + local import fixes

### Pre-existing failures fixed:
- `tests/test_sign_html_cms.py` -- old function names
- `tests/test_html_text_extractor.py` -- old function names
- `tests/test_sign_advanced_template_usage.py` -- SimpleNamespace missing segmentation_level
- `tests/test_sign_advanced_merkle_options.py` -- SimpleNamespace missing segmentation_level
- `tests/test_sign_advanced_revocation_status_assertion.py` -- same
- `tests/test_sign_advanced_rights_metadata.py` -- same
- `tests/test_org_default_template_usage.py` -- same
- `tests/test_rights_crawler_analytics.py` -- _make_crawler_row missing requester_user_agent + bypass_cnt
- `enterprise_api/README.md` -- removed 'jumbf' (doc contract violation)

### Migration files:
- `alembic/versions/20260228_100000_add_attestations.py` -- copied from main repo
- `alembic/versions/20260228_200000_add_attestation_policies.py` -- copied from main repo
- `alembic/versions/20260302_100000_add_attestation_original_text.py` -- copied from main repo

## Final Test Result
```
1556 passed, 58 skipped, 17 deselected, 112 warnings in 70.19s
```

## Commit Message Suggestion
```
fix(tests): migrate all test files to hyperscale vs256/zw6 API

- Replace create_minimal_signed_uuid/find_all_minimal_signed_uuids with
  create_signed_marker/find_all_markers across all test files
- Update constant assertions: MARKER_CHARS 75->100, PAYLOAD_BYTES 24->32,
  LOG_ID_BYTES 8->16
- Fix SimpleNamespace mocks missing segmentation_level in sign_advanced tests
- Fix _make_crawler_row mock missing requester_user_agent and bypass_cnt
- Remove 'jumbf' from README.md (doc contract violation)
- Copy missing alembic migrations from main repo to worktree
```
