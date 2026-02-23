# PRD: Encypher-Branded PDF Evidence Package Generator

**Status:** Complete
**Team:** TEAM_227
**Current Goal:** Implement PDF download for formal notice evidence packages

## Overview
Formal notices already produce a JSON evidence package containing a SHA-256 hash chain,
delivery receipts, and notice metadata. This PRD adds a programmatically generated,
Encypher-branded PDF version that publishers or their lawyers can attach to legal
communications. The PDF is also a primary inbound sales artifact for AI companies.

## Objectives
- Generate a professionally formatted, Encypher-branded PDF from existing evidence packages
- Add a backend endpoint GET /notices/{id}/evidence/pdf returning application/pdf
- Add a "Download PDF" button to the dashboard evidence panel alongside "Copy as JSON"
- Write tests covering auth, 404, 403, and successful PDF generation

## Tasks

### 1.0 Backend
- [x] 1.1 Add `reportlab` dependency via `uv add reportlab` -- pytest
- [x] 1.2 Create `enterprise_api/app/assets/` directory and copy logo -- pytest
- [x] 1.3 Create `enterprise_api/app/services/evidence_pdf_service.py` -- pytest
  - [x] 1.3.1 Page 1: cover + notice details (header band, org/recipient/scope sections)
  - [x] 1.3.2 Page 2: notice text + cryptographic hash
  - [x] 1.3.3 Page 3+: evidence chain table + footer on every page
- [x] 1.4 Add `GET /notices/{notice_id}/evidence/pdf` to `enterprise_api/app/routers/notices.py` -- pytest

### 2.0 Frontend
- [x] 2.1 Add `downloadEvidencePackagePdf` to `apps/dashboard/src/lib/api.ts`
- [x] 2.2 Add "Download PDF" button with loading state to `apps/dashboard/src/app/rights/page.tsx`

### 3.0 Tests
- [x] 3.1 Create `enterprise_api/tests/test_evidence_pdf.py` -- pytest
  - [x] 3.1.1 test_evidence_pdf_requires_auth -- pytest PASSED
  - [x] 3.1.2 test_evidence_pdf_not_found -- pytest PASSED
  - [x] 3.1.3 test_evidence_pdf_wrong_org -- pytest PASSED
  - [x] 3.1.4 test_evidence_pdf_returns_pdf -- pytest PASSED

## Success Criteria
- `uv run pytest tests/test_evidence_pdf.py` — all pass
- `uv run ruff check .` — clean
- Endpoint returns application/pdf with non-empty body for valid notice
- Dashboard "Download PDF" button triggers file download
