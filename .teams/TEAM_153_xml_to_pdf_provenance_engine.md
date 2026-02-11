# TEAM_153 — XML-to-PDF Provenance Rendering Engine

## Session Summary
Built a Python (uv) XML-to-PDF rendering engine that uses the enterprise_api signing tool to test all embedding approaches: default C2PA, lightweight manifests, minimal manifests, and ZW embeddings (sentence-level + doc-level).

## Status: COMPLETE

## Tasks
- [x] Create uv Python project at `tools/xml-to-pdf/` — ✅ pytest
- [x] Design XML schema for research papers — ✅ pytest
- [x] Write sample research paper XML on content provenance — ✅ pytest
- [x] Build XML parser — ✅ pytest (22 tests)
- [x] Build PDF renderer (reportlab) — ✅ pytest (7 tests)
- [x] Integrate enterprise_api signing for all modes — ✅ pytest (17 tests)
- [x] Write tests (TDD) — ✅ 46/46 passing
- [x] E2E: XML -> signed PDF with all embedding modes — ✅ 5/5 PDFs generated

## E2E Results (live API)
| Mode | Segments | Signed Text | Invisible Chars | Overhead |
|------|----------|-------------|-----------------|----------|
| c2pa_full | 82 | 11,138 chars | 1 | 0.0% |
| lightweight | 82 | 44,298 chars | 0 | 0.0% |
| minimal | 82 | 36,640 chars | 1 | 0.0% |
| zw_sentence | 82 | 20,066 chars | 7,847 | 64.2% |
| zw_document | 1 | 9,732 chars | 107 | 1.1% |

## Architecture
- `tools/xml-to-pdf/` — standalone uv project
- Uses `reportlab` for PDF generation
- Calls enterprise_api `/api/v1/sign` endpoint
- CLI interface: `uv run xml-to-pdf <xml_file> [--mode all|c2pa_full|lightweight|minimal|zw_sentence|zw_document] [--unsigned]`

## Files Created
- `tools/xml-to-pdf/pyproject.toml` — uv project config
- `tools/xml-to-pdf/src/xml_to_pdf/parser.py` — XML parser
- `tools/xml-to-pdf/src/xml_to_pdf/renderer.py` — PDF renderer
- `tools/xml-to-pdf/src/xml_to_pdf/signer.py` — Enterprise API integration
- `tools/xml-to-pdf/src/xml_to_pdf/cli.py` — CLI entry point
- `tools/xml-to-pdf/examples/content_provenance_paper.xml` — Sample paper
- `tools/xml-to-pdf/tests/` — 46 tests (parser, renderer, signer, CLI)
