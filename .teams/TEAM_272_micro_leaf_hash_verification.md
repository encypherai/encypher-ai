# TEAM_272 -- Micro Leaf Hash Verification

**Status**: COMPLETE
**Started**: 2026-03-23
**PRD**: PRDs/CURRENT/PRD_Micro_Leaf_Hash_Verification.md

## Summary
Added server-side `leaf_hash` verification to the micro embedding DB resolution path.
Previously, `_resolve_uuids_from_db` only checked the HMAC (64-bit content commitment).
Now it also fetches and compares the full SHA-256 `leaf_hash` from `content_references`.

## Changes

### `app/services/verification_logic.py`
1. Added `leaf_hash` to `_RESOLVE_UUID_SQL` SELECT clause
2. Initialized `clean_sentence = None` before the HMAC block (scope fix)
3. After HMAC passes, recomputes `compute_leaf_hash(clean_sentence)` and compares to stored `leaf_hash`
4. If mismatch: sets `hmac_verified = False`, logs WARNING
5. Adds `leaf_hash_verified` (bool) to manifest dict when the check runs
6. Backward compatible: if `leaf_hash` is NULL (old rows), the check is skipped

### `tests/test_leaf_hash_verification.py` (new)
4 tests:
- `test_leaf_hash_match_passes_verification` -- HMAC + hash match -> valid
- `test_leaf_hash_mismatch_fails_verification` -- HMAC pass + hash mismatch -> invalid
- `test_missing_leaf_hash_skips_check` -- no stored hash -> HMAC-only (backward compat)
- `test_leaf_hash_verified_flag_in_manifest` -- flag present in output

## Suggested Commit Message

```
feat(verification): add server-side leaf_hash check to micro embedding path

The micro verification DB resolution path (_resolve_uuids_from_db) now
fetches the stored SHA-256 leaf_hash from content_references and compares
it against a recomputed hash of the submitted sentence text. Previously,
only the 64-bit HMAC content commitment was checked.

- Add leaf_hash to _RESOLVE_UUID_SQL SELECT
- After HMAC passes, recompute compute_leaf_hash(clean_sentence) and
  compare to stored value; reject on mismatch
- Add leaf_hash_verified flag to manifest output
- Backward compatible: NULL leaf_hash rows skip the check
- 4 new unit tests covering match/mismatch/missing/flag scenarios
```
