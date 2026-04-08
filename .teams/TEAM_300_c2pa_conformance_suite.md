# TEAM_300 - C2PA Conformance Suite

## Session Start
- Date: 2026-04-07
- Agent: Opus
- Objective: Build an open-source C2PA conformance test suite that evaluates any implementation against the spec's normative validation rules using declarative predicates from the c2pa-knowledge-graph repo.

## Context
- The c2pa-knowledge-graph repo contains 45 predicates formalizing 67/237 v2.4 rules (content binding layer)
- The remaining 170 rules are 89% format-agnostic (JUMBF/CBOR layer) and 86% deterministic given test fixtures
- This suite replaces hand-coded validation in c2pa-rs/c2pa-tool with a declarative, language-agnostic approach
- New repo: /home/developer/code/c2pa-conformance-suite

## Architecture
- Layer 1: Container extraction (format-specific, thin) - 16 extractors covering 27+ MIME types
- Layer 2: JUMBF/CBOR manifest parser (format-agnostic core)
- Layer 3: Predicate evaluator (evaluates conditions from predicates.json)
- Layer 4: Crypto verifier (COSE/X.509/OCSP with test PKI)
- Layer 5: Reporter (conformance reports, c2pa-tool comparison)

## Progress
- [x] PRD written
- [x] Repo initialized (pyproject.toml, src layout)
- [x] Test PKI infrastructure (root CA, intermediate CA, 4 signer variants)
- [x] JUMBF/CBOR parser (box hierarchy, JUMD labels, CBOR decoding)
- [x] Manifest store parser (claims, assertions, active manifest)
- [x] Predicate evaluator (30+ operators, status codes, reports)
- [x] Original 11 extractors (JPEG, PNG, BMFF, RIFF, TIFF, GIF, SVG, JXL, PDF, Text, Sidecar)
- [x] Full validation pipeline (extract -> parse -> build context -> evaluate)
- [x] 5 new extractors (ID3v2, OGG, Font, HTML, ZIP) - completes all v2.4 MIME types
- [x] Text extractor rewritten for v2.4 C2PATextManifestWrapper (VS encoding)
- [x] SVG extractor extended for generic structured text delimiters
- [x] Engine INFORMATIONAL result type (was always collapsed to PASS)
- [x] MAY decision logic (severity="may" -> INFORMATIONAL on pass and fail)
- [x] ConformanceReport.informational_count + report serialization
- [x] 167 tests passing, lint clean (ruff) (session 1)
- [x] Fixed JPEG APP11 extractor: CI(2)+En(2)+Z(4)=8 byte header, truncate to LBox
- [x] Fixed BMFF uuid box extractor: skip 4-byte version/flags after UUID
- [x] Fixed SVG extractor: exclude ZIP archives from can_handle (PK magic check)
- [x] Fixed font extractor: C2PA table contains raw JUMBF (no 20-byte header)
- [x] Fixed JXL extractor: accept c2pa box type in addition to jumb
- [x] Added FLAC extractor: APPLICATION metadata block with c2pa identifier
- [x] Added .sfnt suffix to font extractor
- [x] Real-world validation: 52 c2pa-rs signed files, 51/52 pass (1 JUMBF parser limitation)
- [x] 171 tests passing, lint clean (ruff) (session 2)
- [ ] Cryptographic verification (COSE_Sign1, X.509 chain, OCSP, TSA)
- [ ] Add MAY predicates to predicates.json (iat: VAL-CRYP-0029/30, OCSP: VAL-CRYP-0035)
- [ ] Test vector generation (structural, binding, crypto, ingredient, timestamp)
- [ ] c2pa-tool comparison runner
- [ ] Fix JUMBF parser to handle opaque content boxes (ingredient JPEG with embedded thumbnail)

## Test Summary (171 passing)
| Component | Tests |
|-----------|-------|
| JUMBF parser | 15 |
| Predicate evaluator | 26 |
| Container extractors (original 11) | 53 |
| PKI generation | 12 |
| Integration (full pipeline) | 17 |
| Extended extractors (ID3, OGG, Font, HTML, ZIP, FLAC, Text v2.4, structured) | 39 |
| Engine INFORMATIONAL + MAY | 9 |

## Files Created/Modified (this session)

### New extractors
- `src/c2pa_conformance/extractors/id3.py` - ID3v2 GEOB frame (MP3, FLAC)
- `src/c2pa_conformance/extractors/ogg.py` - OGG logical bitstream reassembly
- `src/c2pa_conformance/extractors/font.py` - OpenType C2PA table (TTF/OTF/WOFF1/WOFF2)
- `src/c2pa_conformance/extractors/html.py` - script/link element, data: URI
- `src/c2pa_conformance/extractors/zip.py` - META-INF/content_credential.c2pa

### Updated extractors
- `src/c2pa_conformance/extractors/text.py` - Rewritten for v2.4 C2PATextManifestWrapper with Unicode VS encoding (U+FE00-FE0F, U+E0100-E01EF), keeps legacy ASCII-armor fallback
- `src/c2pa_conformance/extractors/svg.py` - Added generic structured text delimiters (-----BEGIN/END C2PA MANIFEST-----) with data: URI support

### Previous session extractors (unchanged, still passing)
- `src/c2pa_conformance/extractors/base.py` - Protocol, registry, auto-detect
- `src/c2pa_conformance/extractors/jpeg.py` - APP11 multi-segment
- `src/c2pa_conformance/extractors/png.py` - caBX chunk
- `src/c2pa_conformance/extractors/bmff.py` - C2PA uuid box
- `src/c2pa_conformance/extractors/riff.py` - C2PA chunk
- `src/c2pa_conformance/extractors/tiff.py` - Tag 0xCD41
- `src/c2pa_conformance/extractors/gif.py` - App Extension
- `src/c2pa_conformance/extractors/jxl.py` - ISOBMFF jumb box
- `src/c2pa_conformance/extractors/pdf.py` - Stream scan

### Engine changes
- `src/c2pa_conformance/evaluator/engine.py` - INFORMATIONAL result type now produced by evaluate_predicate when on_match has result="informational" or predicate has severity="may"; ConformanceReport tracks informational_count; MAY predicates never produce FAIL

### Tests
- `tests/test_extractors_extended.py` - 35 tests for new/updated extractors
- `tests/test_engine_may.py` - 9 tests for INFORMATIONAL + MAY logic

## Files Modified (session 2)

### Extractor fixes
- `src/c2pa_conformance/extractors/jpeg.py` - Fixed APP11 header: CI(2)+En(2)+Z(4)=8 bytes for all packets; added LBox truncation for multi-instance JPEGs
- `src/c2pa_conformance/extractors/bmff.py` - Fixed FullBox: skip 4-byte version/flags between UUID and purpose string
- `src/c2pa_conformance/extractors/svg.py` - Added ZIP magic exclusion in can_handle to prevent false matches on DOCX/EPUB/ODT
- `src/c2pa_conformance/extractors/font.py` - Removed 20-byte header parsing; C2PA table contains raw JUMBF. Added .sfnt suffix
- `src/c2pa_conformance/extractors/jxl.py` - Added c2pa box type (c2pa-rs convention) in addition to jumb
- `src/c2pa_conformance/extractors/id3.py` - Removed .flac from suffix list (FLAC has dedicated extractor)

### New extractor
- `src/c2pa_conformance/extractors/flac.py` - FLAC APPLICATION metadata block with c2pa identifier

### Updated tests
- `tests/test_extractors.py` - Updated JPEG builder (Z field), BMFF builder (version/flags)
- `tests/test_extractors_extended.py` - Updated font builder (raw JUMBF), added FLAC tests (4)

## MIME Type Coverage (from c2pa-knowledge-graph v2.4)
27 spec-normative MIME types covered by 17 extractors:
- image: jpeg, png, tiff, dng, gif, svg+xml, jxl, heif, heic, avif, webp
- video: mp4, quicktime, 3gpp, avi
- audio: wav, mp4, mpeg, flac, ogg
- text: plain, markdown, xml, html
- application: pdf, xml, xhtml+xml, epub+zip, OOXML, ODF, zip
- font: ttf, otf, woff2
- sidecar: application/c2pa

## Handoff Notes
All 17 extractors validated against real c2pa-rs signed assets (52 files, 51/52 pass). The one failure is a JUMBF parser limitation: the ingredient JPEG file contains an embedded JPEG thumbnail whose raw bytes the recursive box parser misinterprets as invalid JUMBF boxes. Fix: the parser should treat assertion content boxes as opaque blobs rather than recursively parsing their children.

### Bugs found and fixed this session
1. **JPEG APP11**: Header is CI(2)+En(2)+Z(4)=8 bytes for ALL packets. En is the box instance number, Z is the packet sequence. The old code used En as the sequence number and had different skip sizes for first vs continuation packets.
2. **BMFF uuid box**: C2PA uuid box is a FullBox with 4 bytes of version/flags between the extended type UUID and the purpose string.
3. **SVG can_handle**: Matched ZIP archives (DOCX, EPUB, ODT, OXPS) because their decompressed XML content contains `<?xml` and `c2pa` strings.
4. **Font C2PA table**: The table contains raw JUMBF data with no separate header structure. The old code assumed a 20-byte header with version/offset/length fields.
5. **JXL**: c2pa-rs uses a `c2pa` box type (not `jumb`) in JXL containers.
6. **FLAC**: Uses APPLICATION metadata blocks (not ID3v2) for C2PA embedding.
7. **JPEG ingredient**: Multi-instance JPEG has trailing bytes beyond the jumb superbox LBox. Fixed by truncating to declared LBox size.

### Next session should focus on
1. Fix JUMBF parser to handle opaque content boxes (stops ingredient JPEG from failing)
2. Add MAY predicates to predicates.json in c2pa-knowledge-graph repo
3. Cryptographic verification layer (COSE_Sign1 + X.509 chain) - unlocks ~48 crypto rules
4. Test vector generation using the PKI infrastructure
5. c2pa-tool comparison runner

## Suggested Commit Message (session 2)
```
fix(conformance-suite): validate all extractors against real c2pa-rs signed assets

Fix 7 extraction bugs discovered by testing 52 c2pa-rs signed files:

JPEG APP11: header is CI(2)+En(2)+Z(4)=8 bytes for all packets.
Old code used En as packet sequence and had wrong skip sizes.
Add LBox truncation for multi-instance JPEGs with trailing bytes.

BMFF uuid box: skip 4-byte version/flags (FullBox) between the
16-byte UUID and the null-terminated purpose string.

SVG: exclude ZIP archives (PK magic) from can_handle to prevent
false matches on DOCX/EPUB/ODT whose XML content contains c2pa.

Font: C2PA table contains raw JUMBF (no 20-byte header). Add
.sfnt suffix support.

JXL: accept c2pa box type (c2pa-rs convention) alongside jumb.

Add FLAC extractor for APPLICATION metadata block with c2pa
identifier (native FLAC embedding, not ID3v2).

17 extractors validated against 52 real signed files (51/52 pass,
1 pre-existing JUMBF parser limitation with ingredient thumbnails).
171 tests passing, lint clean.
```
