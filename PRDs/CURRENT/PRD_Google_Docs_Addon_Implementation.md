# PRD: Google Docs Add-on Implementation

## Status: COMPLETE
## Current Goal: Google Docs Add-on implementation complete

## Overview
Implement a new Google Docs Add-on under `integrations/google-docs-addon` using Apps Script. The add-on must provide a compliant manifest, Docs menu integration, sidebar UI, secure settings storage, Encypher sign/verify API integration, and provenance-chain support for re-signing.

## Objectives
- Create Apps Script add-on with valid `appsscript.json` and required scopes.
- Provide Docs add-on menu + sidebar UX for sign/verify flows.
- Support selection and full-document signing in-place.
- Store and reuse provenance chain (`previous_embeddings`) on re-sign.
- Provide local tests for provenance utility logic.
- Provide setup/publishing docs for Google review requirements.

## Tasks

### 1.0 Add-on Project Bootstrap
- [x] 1.1 Create `integrations/google-docs-addon` structure. - ✅ implemented
- [x] 1.2 Add Apps Script manifest (`appsscript.json`) with add-on metadata and scopes. - ✅ implemented
- [x] 1.3 Add entrypoints (`onOpen`, `onInstall`, add-on homepage card, sidebar opener). - ✅ implemented

### 2.0 Core Sign/Verify Flows
- [x] 2.1 Implement document/selection extraction helpers. - ✅ implemented
- [x] 2.2 Implement sign flow (selection/full-doc) with in-place replacement. - ✅ implemented
- [x] 2.3 Implement verify flow (selection/full-doc). - ✅ implemented
- [x] 2.4 Integrate Encypher API calls via `UrlFetchApp`. - ✅ implemented

### 3.0 Provenance Chain
- [x] 3.1 Implement embedding extraction (VS/ZWNBSP parsing). - ✅ implemented
- [x] 3.2 Implement document-level provenance storage and capping. - ✅ implemented
- [x] 3.3 Pass stored provenance as `previous_embeddings` on re-sign. - ✅ implemented

### 4.0 Sidebar UX
- [x] 4.1 Build branded sidebar HTML/CSS/JS. - ✅ implemented
- [x] 4.2 Add settings actions (API key/base URL save/clear). - ✅ implemented
- [x] 4.3 Add result reporting and provenance summary. - ✅ implemented

### 5.0 Validation and Documentation
- [x] 5.1 Add Node tests for provenance utility logic. - ✅ npm test (6 tests)
- [x] 5.2 Run tests and verify passing. - ✅ npm test
- [x] 5.3 Add README with setup, clasp deployment, and Google review checklist. - ✅ implemented

## Success Criteria
- Add-on can be deployed in Apps Script and opens in Google Docs.
- Sign/verify actions work for both selection and full document.
- Provenance entries are persisted and reused for re-signing.
- Local tests pass.
- Documentation includes steps for Google Workspace Marketplace submission.

## Completion Notes
- Created full Apps Script Google Docs Add-on in `integrations/google-docs-addon/`.
- Implemented manifest with required scopes and add-on metadata (`appsscript.json`).
- Implemented Docs menu + sidebar entrypoints (`onOpen`, `onInstall`, homepage card).
- Added sign/verify for both selection and full document via Encypher APIs.
- Added provenance chain extraction, storage in Document Properties, and re-sign reuse.
- Added API base URL allowlist validation (`https://*.encypherai.com`) for add-on security.
- Added local Node tests for provenance utilities (6/6 passing via `npm test`).
- Added deployment and Marketplace checklist documentation in add-on README.
- Branding/design conformance pass completed:
  - sidebar copy aligned to standards authority, proof-of-origin, and collaborative infrastructure messaging
  - official Encypher palette + Roboto typography applied
  - add-on manifest display name and universal action labels updated to C2PA provenance language
  - Puppeteer UI verification completed (screenshot + DOM token checks)
