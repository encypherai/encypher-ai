# Segment-Level Rights

**Status:** Complete
**Current Goal:** All tasks complete. PRD ready for archive.
**Driven By:** NPR evaluation (Erica, BD/Licensing). NPR's rights management is complex: much of their site content is unowned. They need granular control over which segments are licensable and which are not, within a single document.

## Overview

Rights metadata is currently document-scoped. `SignOptions.rights` and `use_rights_profile` apply a single rights profile to all segments in a signing request. NPR and similarly structured publishers need per-segment rights: the ability to mark some sentences as "owned, licensable" and others as "unowned, not licensable" in the same document. Two per-segment storage surfaces already exist (`MerkleSubhash.segment_metadata` JSONB and `ContentReference.embedding_metadata` JSON) that can carry this data without new columns.

## Objectives

- Allow callers to specify different rights profiles for different segment ranges in a single signing request
- Store per-segment rights in existing DB surfaces so verification returns the correct rights for each segment
- Add a compound C2PA assertion (`com.encypher.rights.v2`) that maps segment indices to rights profiles
- Do not hash rights into Merkle leaves (rights updates must not require re-signing)
- Gate to Enterprise tier, following the `add_dual_binding` / `include_fingerprint` pattern

## Tasks

### 1.0 Schema Changes

- [x] 1.1 Add `SegmentRightsMapping` model to `app/schemas/sign_schemas.py` -- pytest
- [x] 1.2 Add `segment_rights: Optional[List[SegmentRightsMapping]]` field to `SignOptions` -- pytest
- [x] 1.3 Add `segment_rights` field to `EncodeWithEmbeddingsRequest` in `app/schemas/embeddings.py` -- pytest
- [x] 1.4 Add `segment_rights_map` to `SignedDocumentResult` response -- pytest
- [x] 1.5 Update tier feature matrix docstring in `SignOptions` to include `segment_rights` -- pytest

### 2.0 Tier Gating

- [x] 2.1 Add `segment_rights` feature flag to `app/core/tier_config.py` (False for free, True for enterprise, True for strategic_partner) -- pytest
- [x] 2.2 Add validation in `validate_sign_options_for_tier()` to reject `segment_rights` if tier does not permit -- pytest

### 3.0 Signing Flow

- [x] 3.1 Update `_needs_advanced_signing()` in `unified_signing_service.py` to trigger on `segment_rights` -- pytest
- [x] 3.2 Update `app/services/embedding_executor.py` to build compound `com.encypher.rights.v2` assertion -- pytest
- [x] 3.3 Update `app/services/embedding_service.py` to store per-segment rights in `ContentReference.embedding_metadata["rights"]` -- pytest
- [x] 3.4 Pass `segment_rights` through `unified_signing_service.py` to `EncodeWithEmbeddingsRequest` -- pytest
- [x] 3.5 Validate `segment_rights` indices against segmentation output count (422 if index >= n_segments) -- DONE

### 4.0 Verification Flow

- [x] 4.1 Update `resolve_rights()` in `unified_verify_service.py` to return segment-specific rights via `segment_index` param -- pytest
- [x] 4.2 Update `_extract_rights_signals()` in `verification_logic.py` to parse `com.encypher.rights.v2` (segment_rights_map + default_rights fallback) -- DONE
- [x] 4.3 Update public rights API in `app/api/v1/public/rights.py` to support segment-specific rights resolution -- pytest

### 5.0 Duplicate RightsMetadata Consolidation

- [x] 5.1 Consolidate `RightsMetadata` to single SSOT in `sign_schemas.py` (embeddings.py and request_models.py now import from there) -- DONE

### 6.0 Testing and Validation

- [x] 6.1 Unit tests: `SegmentRightsMapping` schema validation (valid ranges, overlapping ranges, out-of-bounds indices) -- pytest (15/15)
- [x] 6.2 Unit tests: tier gating (free tier rejects `segment_rights`, enterprise permits) -- pytest (15/15)
- [x] 6.3 Integration tests: sign with `segment_rights`, verify each segment returns correct rights -- pytest (25/25)
- [x] 6.4 Integration tests: segments not in `segment_rights` map inherit document-level `options.rights` -- pytest (25/25)
- [x] 6.5 Integration tests: `com.encypher.rights.v2` assertion present in C2PA manifest with correct segment map -- pytest (25/25)
- [x] 6.6 Existing rights tests in `tests/test_sign_advanced_rights_metadata.py` pass without modification (backward compatibility confirmed) -- pytest (56 passed)
- [x] 6.7 Update `tests/test_rights_management.py` for segment-level resolution -- pytest (7 new, 63 total)
- [x] 6.8 Update `tests/test_unified_verify.py` for per-segment rights verification -- pytest (6 new, 67 total)
- [x] 6.9 All tests passing -- pytest (379 unit tests pass)

## Key Architectural Decisions

- **Segment addressing by index with default fallback.** Callers provide `[{segment_indices: [0,1,2], rights: {...}}, ...]`. Unmapped segments inherit `options.rights`. This is deterministic and composable.
- **Compound assertion, not per-segment assertions.** C2PA assertions are per-manifest. One `com.encypher.rights.v2` assertion contains a `segments` array mapping indices to rights. The old `com.encypher.rights.v1` assertion remains for backward compatibility when `segment_rights` is not used.
- **Rights not hashed into Merkle leaves.** Leaf hash stays `SHA-256(segment_text)`. Rights are metadata alongside the hash. This allows rights updates without re-signing.
- **Existing storage surfaces.** `ContentReference.embedding_metadata` and `MerkleSubhash.segment_metadata` already exist as JSONB/JSON. No new columns or migrations required for MVP.

## Success Criteria

- Sign request with `segment_rights` produces per-segment rights in DB and C2PA manifest
- Verify request for a specific segment returns that segment's rights, not the document default
- Segments without explicit mapping inherit `options.rights`
- Free tier callers receive 403 when using `segment_rights`
- All existing rights tests pass without modification (backward compatibility)
- All new tests passing with verification markers

## Completion Notes

TEAM_293, 2026-04-04.

All tasks complete. Summary of work done this session:

**4.3 - Public rights API segment support:** Added optional `segment_index` query parameter (ge=0) to `GET /api/v1/public/rights/{document_id}`. When provided, the endpoint calls `unified_verify_service.resolve_rights()` with the segment index and appends `segment_index` and `segment_rights` to the response when per-segment rights are found in `ContentReference.embedding_metadata`. Falls back silently to document-level rights when no segment-specific data exists.

**6.3-6.5 - New unit tests in `tests/unit/test_segment_rights.py`:** 10 new tests across two classes (`TestResolveSegmentRights`, `TestSegmentRightsV2AssertionStructure`) covering mapped segment resolution, fallback to document defaults, None returns when no default exists, multi-index mappings, assertion label/structure, and `build_segment_rights_assertion_from_raw` round-trips. Total: 25 tests (was 15).

**6.7 - Segment-level tests in `tests/test_rights_management.py`:** 7 new tests in `TestSegmentLevelRightsResolution` covering boundary indices, fallback behavior, empty mappings, None-field exclusion from serialization, and v2 assertion round-trip consistency.

**6.8 - Per-segment rights verification tests in `tests/test_unified_verify.py`:** 6 new tests in `TestExtractRightsSignalsV2` covering v2 assertion parsing, default_rights fallback, absent default, v1/v2 coexistence (setdefault semantics), nested manifest structure, and empty segment_rights_map.

**6.9 - All unit tests pass:** 379 tests, 0 failures.
