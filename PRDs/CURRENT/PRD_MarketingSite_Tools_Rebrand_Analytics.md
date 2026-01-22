# PRD: Marketing Site Tools Rebrand + Analytics

**Status:** In Progress  
**Current Goal:** Add detailed analytics for the sign/verify tool flow and rebrand the marketing-site tool URLs and language from encode/decode to sign/verify with safe redirects.

## Overview
We will instrument the marketing-site tool flow to emit structured analytics for sign/verify usage and rebrand UI copy, routes, and SEO metadata from encode/decode to sign/verify. We will keep legacy routes via permanent redirects to preserve existing inbound links and SEO equity. The tooling will reflect cryptographic signing terminology while maintaining the same backend APIs.

## Objectives
- Track tool usage events for sign/verify actions, failures, and UI interactions.
- Add server-side logging/analytics hooks for verify requests to align with sign logging.
- Rebrand marketing-site tool pages and metadata to sign/verify naming.
- Add redirects from old encode/decode routes to new sign/verify routes.

## Tasks
- [x] 1.0 Discovery
  - [x] 1.0.1 Confirm analytics utilities and event format
  - [x] 1.0.2 Identify all encode/decode references and routes
- [x] 2.0 Tests (TDD)
  - [x] 2.0.1 Add unit tests for tools analytics helper
- [ ] 3.0 Implementation
  - [x] 3.0.1 Add tools analytics helper and event schema
  - [x] 3.0.2 Instrument encode/decode (sign/verify) UI flow with analytics
  - [x] 3.0.3 Add verify route logging similar to sign route
  - [x] 3.0.4 Rebrand UI copy, labels, and metadata
  - [x] 3.0.5 Add new sign/verify routes and legacy redirects
  - [x] 3.0.6 Update tool links, sitemap, and tests
- [ ] 4.0 Verification
  - [x] 4.0.1 Run marketing-site unit tests
  - [x] 4.0.2 Run marketing-site linting
  - [ ] 4.0.3 Manual sign/verify flow verification (✅ puppeteer)

## Success Criteria
- Tool usage analytics are emitted for key sign/verify actions and errors.
- New sign/verify routes render correctly; old encode/decode routes redirect.
- Tests/lint pass and metadata/SEO updated for new naming.

## Completion Notes
- _TBD_
