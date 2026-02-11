# TEAM_157: Sign Existing PDFs

## Status: COMPLETE ✅

## Goal
Add capability to sign pre-existing PDFs without changing their visual appearance.
Embed zero-width provenance characters directly into the PDF text layer AND inject
an `EncypherSignedText` metadata stream into the PDF catalog.

## Approach
1. Extract plain text from existing PDF via `pymupdf` (`page.get_text()`)
2. Sign text via enterprise API (reuse `signer.py`)
3. Diff original vs signed text to find where invisible chars were inserted
4. Inject ZW chars into the PDF text layer at correct positions using a prepared
   font with synthetic zero-width glyphs (via `encypher-pdf`'s
   `prepare_font_with_invisible_glyphs`)
5. Inject `EncypherSignedText` metadata stream into PDF catalog
6. Save — visual appearance completely unchanged

## Files
- `tools/xml-to-pdf/src/xml_to_pdf/sign_existing.py` — NEW: core module
- `tools/xml-to-pdf/src/xml_to_pdf/cli_sign_existing.py` — NEW: CLI entry point
- `tools/xml-to-pdf/tests/test_sign_existing.py` — NEW: 22 tests
- `tools/xml-to-pdf/pyproject.toml` — Add `sign-pdf` script entry

## Test Results
- **xml-to-pdf**: 70/70 ✅ (22 new sign_existing tests)
- **encypher-pdf**: 19/19 ✅ (no regression)
- **E2E minimal**: `status=Success reason=OK valid=True payload_bytes=127924` ✅
- **E2E zw_sentence**: `status=Success reason=OK valid=True payload_bytes=44930` ✅
  - 7,964 invisible chars injected into text layer, visual appearance preserved

## Tasks
- [x] 1.0 Investigate pymupdf capabilities — ✅ xref_set_key, update_stream, update_object
- [x] 2.0 Write tests (TDD) — ✅ 22 tests (red → green)
- [x] 3.0 Implement `sign_existing.py` — ✅ extract_text, inject_stream, sign_existing_pdf
- [x] 3.1 ZW text layer injection — ✅ _build_char_position_map, _diff_for_insertions, _inject_zw_chars_into_pages
- [x] 4.0 Add CLI entry point (`sign-pdf`) — ✅ with --mode, --title, --in-place flags
- [x] 5.0 E2E verification tests — ✅ both minimal and zw_sentence modes pass
- [x] 5.1 Visual verification — ✅ Puppeteer screenshot confirms no visual changes
- [x] 6.0 Update team file — ✅
