# TEAM_227 -- Evidence PDF Generator

## Session Goal
Implement Encypher-branded PDF Evidence Package Generator per plan.

## Status: COMPLETE

## Tasks
- [x] Create PRD at PRDs/CURRENT/PRD_Evidence_PDF_Generator.md
- [x] Add reportlab dependency: `uv add reportlab`
- [x] Create enterprise_api/app/assets/ + copy logo from marketing-site
- [x] Create enterprise_api/app/services/evidence_pdf_service.py (3-page PDF)
- [x] Add GET /notices/{notice_id}/evidence/pdf endpoint to notices.py
- [x] Add downloadEvidencePackagePdf to apps/dashboard/src/lib/api.ts
- [x] Add "Download PDF" button (blue, loading state) to apps/dashboard/src/app/rights/page.tsx line ~775
- [x] Create tests/test_evidence_pdf.py -- 4 tests, all pass
- [x] Run full test suite: 1263 passed, 0 failed
- [x] ruff check clean
- [x] Fixed pre-existing contract drift: CDN endpoints added to README + sdk/openapi.public.json

## Files Changed
- enterprise_api/pyproject.toml (reportlab added via uv)
- enterprise_api/app/assets/logo_white.png (NEW, copied from marketing-site)
- enterprise_api/app/services/evidence_pdf_service.py (NEW)
- enterprise_api/app/routers/notices.py (added PDF endpoint + Response import)
- apps/dashboard/src/lib/api.ts (added downloadEvidencePackagePdf)
- apps/dashboard/src/app/rights/page.tsx (pdfLoading state + Download PDF button)
- enterprise_api/tests/test_evidence_pdf.py (NEW, 4 tests)
- enterprise_api/README.md (added PDF endpoint + CDN section -- fixed pre-existing drift)
- sdk/openapi.public.json (added PDF + CDN endpoints -- fixed pre-existing drift)

## Test Results
- test_evidence_pdf_requires_auth: PASSED
- test_evidence_pdf_not_found: PASSED
- test_evidence_pdf_wrong_org: PASSED
- test_evidence_pdf_returns_pdf: PASSED (PDF magic bytes verified)
- Full suite: 1263 passed, 0 failed, 58 skipped

## Suggested Git Commit

```
feat(evidence): Encypher-branded PDF evidence package generator

Add a programmatically generated, court-presentable PDF for formal notice
evidence packages. Publishers and their lawyers can download a fully
formatted PDF directly from the dashboard without any additional formatting.

Backend:
- Add reportlab dependency
- New evidence_pdf_service.py generates 3-page branded PDF:
  Page 1: cover + issuing org / recipient / scope / notice details
  Page 2: notice text in bordered box + SHA-256 hash + verification status
  Page 3+: full evidence chain table with hash integrity indicator
- Add GET /notices/{notice_id}/evidence/pdf endpoint returning application/pdf
- Logo embedded from enterprise_api/app/assets/logo_white.png (falls back to
  text wordmark if file missing)

Frontend:
- Add downloadEvidencePackagePdf() to api.ts (triggers browser file download)
- Add "Download PDF" button alongside "Copy as JSON" in the evidence panel
  with loading state and toast notifications

Tests:
- test_evidence_pdf_requires_auth: no token -> 401/403
- test_evidence_pdf_not_found: unknown ID -> 404
- test_evidence_pdf_wrong_org: other org -> 403
- test_evidence_pdf_returns_pdf: valid notice -> 200, application/pdf, PDF magic bytes

Also fix pre-existing contract drift from TEAM_226:
- Add CDN endpoints to README and sdk/openapi.public.json
```
