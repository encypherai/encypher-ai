# PRD: Outlook Email Add-in and Embedding Survivability

## Status: COMPLETE
## Current Goal: Outlook add-in scaffold and survivability testing complete

## Overview
Build a native Outlook add-in integration (Office Mailbox host) for compose/read sign/verify workflows and add empirical survivability tests that simulate common email processor transformations. The tests compare micro_ecc_c2pa-style variation selector embeddings and zero-width embeddings under realistic degradation.

## Objectives
- Create Outlook add-in scaffold with Mailbox manifest + task pane UI.
- Implement compose-body sign and verify actions for HTML/text email content.
- Add test harness for embedding survivability under common email processing transforms.
- Document expected risk profile for each embedding mode in email pipelines.

## Tasks

### 1.0 Outlook Add-in Scaffold
- [x] 1.1 Create `integrations/outlook-email-addin` structure. - ✅ implemented
- [x] 1.2 Add Outlook Mailbox manifest and command surface. - ✅ implemented
- [x] 1.3 Add task pane UI and mailbox host adapter. - ✅ implemented

### 2.0 API + Provenance for Email
- [x] 2.1 Add sign/verify API client for email content. - ✅ implemented
- [x] 2.2 Add settings storage and API URL validation. - ✅ implemented
- [x] 2.3 Add provenance extraction and `previous_embeddings` pass-through. - ✅ implemented

### 3.0 Survivability Harness
- [x] 3.1 Implement email processor transforms (normalization/sanitization scenarios). - ✅ implemented
- [x] 3.2 Add tests comparing micro_ecc_c2pa vs zero-width survival and recoverability. - ✅ implemented
- [x] 3.3 Run tests and record observations. - ✅ npm test + uv run pytest

### 4.0 Documentation
- [x] 4.1 Add README for Outlook add-in setup and sideloading. - ✅ implemented
- [x] 4.2 Add survivability matrix summary and recommendations. - ✅ implemented

## Success Criteria
- Outlook add-in scaffold is runnable via sideloaded manifest.
- Sign/verify paths work against email body content.
- Survivability tests run and show comparative behavior for both embedding methods.
- Documentation includes practical recommendation for default email embedding strategy.

## Completion Notes
- Added Outlook Mailbox add-in scaffold in `integrations/outlook-email-addin/` with manifest, task pane UI, mailbox adapter, API client, settings storage, provenance utils, and app orchestration.
- Added JS survivability harness and tests (`tests/survivability-harness.test.js`) simulating multiple email processor transformations.
- Added Python enterprise-level survivability tests (`enterprise_api/tests/test_email_embedding_survivability.py`) using real crypto utilities.
- Added survivability matrix documentation and strategy guidance in `docs/architecture/EMAIL_EMBEDDING_SURVIVABILITY_MATRIX.md`.
- Updated Outlook add-in manifest/UI copy and visual language to align with `docs/company_internal_strategy/Encypher_Marketing_Guidelines.md`.
- Applied official Encypher palette and Roboto-first typography in task pane CSS.
- Added standards-authority and proof-of-origin messaging in task pane hero and trust context sections.
- Performed browser UI verification via Puppeteer screenshot and DOM checks for brand tokens/copy.
- Test results:
  - `npm test` in `integrations/outlook-email-addin`: 14/14 passing
  - `uv run pytest enterprise_api/tests/test_email_embedding_survivability.py -q`: 5/5 passing
- Recommendation: default to `micro_ecc_c2pa` with fallback to `zw_embedding` for known VS-stripping processors.
