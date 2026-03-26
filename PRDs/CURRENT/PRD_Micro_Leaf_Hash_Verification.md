# PRD: Micro Leaf Hash Verification

**Status**: COMPLETE
**Current Goal**: Add server-side leaf_hash verification to micro embedding DB resolution path
**Team**: TEAM_272

## Overview

The micro verification path (`_resolve_uuids_from_db`) authenticates markers via HMAC but never
compares the full SHA-256 `leaf_hash` stored in `content_references` against the submitted text.
This leaves 192 bits of available integrity evidence on the table. Fix: fetch `leaf_hash` from the
DB after HMAC passes, recompute `compute_leaf_hash(clean_sentence)`, and require both to match.

## Objectives

- Harden micro verification by adding full SHA-256 content hash comparison
- Expose `leaf_hash_verified` flag in verification output so consumers know the check ran
- Maintain backward compatibility for old rows where `leaf_hash` may be NULL or document-level

## Tasks

- [x] 1.0 Tests (TDD) -- pytest
  - [x] 1.1 Test: leaf_hash match passes verification
  - [x] 1.2 Test: leaf_hash mismatch fails verification despite valid HMAC
  - [x] 1.3 Test: missing leaf_hash in DB row gracefully skips check (backward compat)
  - [x] 1.4 Test: leaf_hash_verified flag present in manifest output
- [x] 2.0 Implementation
  - [x] 2.1 Add `leaf_hash` to `_RESOLVE_UUID_SQL` SELECT
  - [x] 2.2 After HMAC passes in `_resolve_uuids_from_db`, recompute and compare leaf_hash
  - [x] 2.3 Add `leaf_hash_verified` to returned manifest dict
  - [x] 2.4 Log leaf_hash mismatch at WARNING level
- [x] 3.0 Verification
  - [x] 3.1 All existing tests pass (no regressions) -- 1520 passed
  - [x] 3.2 New tests pass -- 4/4
  - [x] 3.3 Lint clean -- ruff

## Success Criteria

- [x] `_resolve_uuids_from_db` returns `is_valid=False` when HMAC passes but leaf_hash mismatches
- [x] Backward compatible: old content_references rows without per-sentence leaf_hash still verify
- [x] `leaf_hash_verified` flag in manifest output indicates whether the check ran and passed

## Completion Notes

Changed files:
- `app/services/verification_logic.py` -- added `leaf_hash` to SQL, recompute+compare after HMAC, `leaf_hash_verified` in manifest
- `tests/test_leaf_hash_verification.py` -- 4 new tests covering match/mismatch/missing/flag
