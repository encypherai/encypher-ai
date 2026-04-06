# TEAM_293 - Global Text Provenance Legislative Report

## Session Start
- **Date:** 2026-04-03
- **Objective:** Generate a branded DOCX report on global text provenance guidelines across jurisdictions, incorporating Encypher's EU AI Act public comment themes as a lens for gap analysis.
- **Deliverable:** `docs/legal/generate_provenance_report.py` -> `docs/legal/Encypher_Global_Text_Provenance_Legislative_Report.docx`

## Status
- [ ] DOCX generator script written
- [ ] Report generated and verified
- [x] Team file updated with handoff notes

## Session 2 (2026-04-04) - Segment-Level Rights PRD Completion

Completed all remaining tasks in PRD_Segment_Level_Rights.md. PRD moved to ARCHIVE.

### Tasks Completed

**4.3 - Public rights API (`app/api/v1/public/rights.py`):**
- Added `segment_index: Optional[int]` query parameter (ge=0) to `GET /api/v1/public/rights/{document_id}`
- When segment_index is provided, calls `unified_verify_service.resolve_rights()` with the index
- Returns `segment_index` and `segment_rights` keys in the response when per-segment embedding metadata is found
- Falls back silently to document-level rights when no segment-specific data exists

**6.3-6.5 - `tests/unit/test_segment_rights.py`:**
- Added `TestResolveSegmentRights` (5 tests): mapped segment resolution, second mapping, unmapped+default, unmapped+no default, all multi-index
- Added `TestSegmentRightsV2AssertionStructure` (5 tests): label, segment_rights_map key, entries structure, default_rights, build_from_raw
- Total: 25 tests (was 15), all passing

**6.7 - `tests/test_rights_management.py`:**
- Added `TestSegmentLevelRightsResolution` (7 tests): boundary indices, mapped segment, unmapped+default, unmapped+no default, empty mappings, None-field exclusion, v2 round-trip
- Total: 63 tests in file

**6.8 - `tests/test_unified_verify.py`:**
- Added `TestExtractRightsSignalsV2` (6 tests): v2 segment_rights parsing, default_rights fallback, absent default, v1+v2 coexistence (setdefault semantics), nested manifest, empty segment_map
- Total: 67 tests in file

**6.9 - All unit tests:** 379 unit tests pass. 3 pre-existing failures in test_unified_verify.py (PDF classify_mime tests) unchanged.

### Commit Message Suggestion

```
feat(segment-rights): complete public API + test coverage for segment-level rights

- Wire segment_index query param through GET /public/rights/{document_id} to
  resolve per-segment rights from ContentReference.embedding_metadata
- Add 10 unit tests for resolve_segment_rights() and v2 assertion structure
  (tests/unit/test_segment_rights.py: 15->25 tests)
- Add 7 segment-level resolution tests to test_rights_management.py
- Add 6 _extract_rights_signals v2 parsing tests to test_unified_verify.py
- Move PRD_Segment_Level_Rights to ARCHIVE (all tasks complete)
```
