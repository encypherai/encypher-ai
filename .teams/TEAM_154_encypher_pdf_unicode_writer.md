# TEAM_154: encypher-pdf — Unicode-Faithful PDF Writer

## Status: COMPLETE ✅ (Session 2 — full C2PA round-trip verified)

## Goal
Build a Python PDF writing library (`encypher-pdf`) that preserves ALL Unicode characters in PDF text streams — including BMP variation selectors (U+FE00–FE0F), supplementary variation selectors (U+E0100–E01EF), and zero-width characters (U+200B, U+200C, U+200D, U+FEFF, U+034F, U+180E) — so they survive PDF generation and extraction by pdfjs-dist for C2PA verification.

## Why
- ReportLab, fpdf2, and PyMuPDF all drop variation selectors because standard fonts lack glyphs for them.
- Encypher's invisible provenance embedding relies on these characters persisting through copy-paste.
- C2PA VS256 encoding uses all 256 variation selectors (BMP + supplementary plane) as a base-256 alphabet.
- pdfjs-dist's `getTextContent()` strips `\p{Cf}` characters — operator list API must be used instead.

## Approach (Final)
- **Synthetic glyph injection**: For each invisible codepoint, a unique zero-width glyph is injected into the TTF font's cmap and glyf tables using fonttools. Each gets a unique GID.
- **CIDToGIDMap /Identity**: CID = GID directly, no custom CIDToGIDMap stream needed.
- **DW 1 + /W array**: Default width 1 (tiny non-zero) for invisible chars. pdfjs-dist filters zero-width glyphs, so 1/1000 em keeps them extractable while visually invisible.
- **ToUnicode CMap**: Maps each unique GID back to its Unicode codepoint. Supplementary plane codepoints use UTF-16 surrogate pairs.
- **cmap format 12 with platEncID=10**: Supplementary plane codepoints require format 12 cmap. Must use `platEncID=10` (UCS-4) — `platEncID=3` is ignored by `getBestCmap()`.
- **Tj splitting**: Each invisible char gets its own Tj operation to avoid MuPDF's multi-zero-width-glyph truncation bug.
- **pdfjs-dist operator list extraction**: Client-side extraction uses operator list API instead of `getTextContent()` to preserve `\p{Cf}` characters.
- **xml-to-pdf integration**: Renderer rewritten to use encypher-pdf; signed_text rendered directly preserving invisible provenance chars.

## Key Bugs Discovered & Fixed
1. **MuPDF GID 0 truncation**: MuPDF stops extracting text when CIDToGIDMap maps a CID to GID 0 (.notdef). Fixed by giving each invisible char its own real GID via synthetic glyph injection.
2. **MuPDF /W array truncation**: Including zero-width GIDs in the /W array causes MuPDF to truncate text at those boundaries. Fixed by using DW 0 and only listing visible GIDs in /W.
3. **MuPDF multi-zero-width Tj truncation**: MuPDF drops chars when a single Tj operation contains multiple zero-width glyphs. Fixed by splitting each invisible char into its own Tj operation.
4. **pdfjs-dist \p{Cf} filtering**: `getTextContent()` unconditionally strips Unicode Format category chars via `isInvisibleFormatMark`. Fixed by using operator list API for extraction.
5. **pdfjs-dist zero-width glyph filtering**: Glyphs with width 0 are skipped during extraction. Fixed by using DW 1 (tiny non-zero width).
6. **cmap format 12 platEncID=3 ignored by getBestCmap()**: All supplementary VS mapped to GID 0, causing all to decode as the same codepoint. Fixed by using `platEncID=10` (UCS-4).
7. **Missing CGJ (U+034F) and MVS (U+180E)**: ZW embedding base-4 chars were missing from invisible codepoints set. Added to fonttools_subset.py and writer.py.
8. **ToUnicode CMap supplementary plane encoding**: Supplementary codepoints need UTF-16 surrogate pairs in the CMap, not raw 32-bit hex.

## Full-Circle Verification (Session 2)
- Generated C2PA-signed PDF via xml-to-pdf + enterprise API
- Extracted text via pdfjs-dist operator list API
- All 1,534 invisible chars preserved (1 BOM + 8 BMP VS + 1,525 supp VS)
- 74 unique VS codepoints (diverse, matching original signed text)
- `find_and_decode()` successfully decodes C2PA manifest (1,520 bytes)
- Verification service returns `CERT_NOT_FOUND` with correct `signer_id: org_07dd7ff77fa7e949` (matches original text verification — cert not in local trust store)

## Test Results
- **encypher-pdf**: 18/18 tests pass ✅
- **xml-to-pdf**: 48/48 tests pass ✅

## Files Modified
- `tools/encypher-pdf/src/encypher_pdf/fonttools_subset.py` — synthetic glyph injection, cmap format 12 with platEncID=10, CGJ/MVS/supp VS
- `tools/encypher-pdf/src/encypher_pdf/font.py` — Identity CIDToGIDMap, DW 1, ToUnicode CMap with UTF-16 surrogates
- `tools/encypher-pdf/src/encypher_pdf/writer.py` — Tj splitting, CGJ/MVS in invisible codepoints
- `tools/encypher-pdf/tests/test_unicode_roundtrip.py` — content stream verification
- `tools/xml-to-pdf/src/xml_to_pdf/renderer.py` — rewritten to use encypher-pdf
- `tools/xml-to-pdf/tests/test_renderer.py` — e2e provenance round-trip tests
- `apps/marketing-site/src/lib/pdfTextExtractor.ts` — operator list API extraction
