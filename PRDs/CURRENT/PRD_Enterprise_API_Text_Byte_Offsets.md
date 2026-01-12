# PRD — Enterprise API Text Byte Offsets

## Status
Completed

## Current Goal
Ensure `enterprise_api` signing and verification aligns with `docs/c2pa/Manifests_Text.txt` by using **byte offsets** (NFC-normalized UTF-8) for `c2pa.hash.data.exclusions`, not character offsets.

## Overview
The C2PA text manifest spec requires that exclusions are expressed as byte offsets into NFC-normalized UTF-8 encoded text. Our stack (`c2pa-text` → `encypher-ai` → `enterprise_api`) must compute and interpret offsets consistently so that embedded `C2PATextManifestWrapper` regions are excluded correctly when hashing.

## Objectives
- Enforce NFC normalization before offset computation.
- Compute `exclusions` offsets as **byte offsets** into UTF-8, not Python string indices.
- Verify the excluded region corresponds exactly to wrapper boundaries (U+FEFF prefix + contiguous VS block).
- Validate /sign, /sign/advanced, and /verify produce/consume consistent offsets.

## Tasks
- [x] 1.0 Baseline verification
- [x] 1.1 Run `uv run pytest` for `enterprise_api` and record baseline (564 passed, 62 skipped, 1 failed: `test_multi_embedding_verification_matches_sentence_segmentation`)
- [x] 1.2 Identify current offset semantics in `c2pa-text` and `encypher-ai` (byte offsets in NFC UTF-8 required; fixed `c2pa-text` Python API mismatch)
- [x] 2.0 Test coverage (TDD)
- [x] 2.1 Add regression tests covering non-ASCII (multi-byte UTF-8) text where char vs byte offsets differ
- [x] 2.2 Add integration tests asserting `exclusions` are byte-based and match wrapper boundaries
- [x] 3.0 Implementation fixes
- [x] 3.1 Update offset computations to NFC + UTF-8 byte offsets end-to-end
- [x] 3.2 Ensure /verify removes excluded bytes based on byte offsets
- [ ] 4.0 Verification
- [x] 4.1 Task — ✅ pytest (enterprise_api: 566 passed, 62 skipped)

## Success Criteria
- `enterprise_api` tests pass (`uv run pytest`).
- New tests demonstrate correct behavior on Unicode input where byte length != char length.
- `c2pa.hash.data.exclusions` align with spec: byte offsets in NFC-normalized UTF-8.

## Completion Notes

- Fixed `c2pa-text` Python `find_wrapper_info` to return UTF-8 byte offsets (start byte + length bytes) and updated wrapper removal logic accordingly.
- Added regression test `enterprise_api/tests/test_c2pa_text_exclusions_byte_offsets.py` asserting exclusions match wrapper byte span and hard-binding hash matches `compute_normalized_hash`.
