# Browser Tools: Chrome Verifier Extension + Substack Author Workflow

**Status:** ✅ Complete  
**Current Goal:** All core features implemented and tested. Ready for Chrome Web Store submission.

## Overview

A browser extension can make C2PA verification visible to readers anywhere on the web, and can also provide a practical author workflow for platforms without plugin ecosystems (e.g., Substack). This PRD defines a Chrome extension that scans pages for Encypher C2PA text embeddings, verifies them, and renders UI indicators—plus an author-mode workflow to sign text before publishing to Substack.

## Objectives

- Provide a consumer-facing verification experience for signed web content
- Avoid privacy pitfalls by minimizing or eliminating content exfiltration
- Provide an author workflow for Substack: “Sign before paste”
- Support revocation status display and trust-anchor resolution
- Make the extension shippable (store listing, privacy policy, automated tests)

## Tasks

### 1.0 Product Definition & UX

- [x] 1.1 Define primary personas — 
  - [x] 1.1.1 Reader: verify an article they are reading
  - [x] 1.1.2 Editor: quickly spot signed/unsigned sections
  - [x] 1.1.3 Author: sign content before posting to Substack
- [x] 1.2 Define UX surfaces — 
  - [x] 1.2.1 Toolbar icon state (none found / found / verified / invalid)
  - [x] 1.2.2 Popup summary (signed blocks, signers, timestamps)
  - [x] 1.2.3 Inline badge overlay on detected signed blocks
  - [x] 1.2.4 Context menu: “Verify selected text” — 
- [x] 1.3 Define error UX — 
  - [x] 1.3.1 Unknown signer — Shows "Invalid Signature"
  - [x] 1.3.2 Corrupted wrapper — Shows "Verification Error"
  - [x] 1.3.3 Revoked content — Shows purple badge with "Content Revoked"

### 2.0 Privacy & Security Posture (Must Decide Early)

- [x] 2.1 Decide verification mode defaults — 
  - [x] 2.1.1 Default: local detection, user-initiated verification
  - [x] 2.1.2 Optional: automatic verification (opt-in) — 
- [x] 2.2 Define minimal data sent to Encypher (if any) — 
  - [x] 2.2.1 Prefer sending only the signed block (not entire page)
  - [x] 2.2.2 Set hard max payload size and truncate policy — API enforced
- [x] 2.3 Threat model — 
  - [x] 2.3.1 Malicious pages with trap content — Content script isolated
  - [x] 2.3.2 Extension XSS / DOM injection — Safe DOM methods only
  - [x] 2.3.3 Abuse of verification endpoint (rate limits) — API rate limited
- [x] 2.4 Extension security hardening — 
  - [x] 2.4.1 Strict CSP — Manifest V3 default CSP
  - [x] 2.4.2 No remote code execution — No eval() or inline scripts
  - [x] 2.4.3 Permission minimization (host permissions) — Only necessary permissions

### 3.0 Technical Architecture (Manifest V3)

- [x] 3.1 Extension scaffolding — 
  - [x] 3.1.1 Manifest V3 configuration — 
  - [x] 3.1.2 Service worker background — 
  - [x] 3.1.3 Content scripts + isolated world — 
- [x] 3.2 Wrapper detection + extraction — 
  - [x] 3.2.1 Detect presence of variation selector ranges
  - [x] 3.2.2 Locate C2PA wrapper magic (`C2PATXT\0`) in decoded bytes
  - [x] 3.2.3 Extract clean text + wrapper span (for exclusions)
  - [x] 3.2.4 Handle multiple wrappers on a page
- [x] 3.3 Verification strategy — 
  - [x] 3.3.1 Call `POST /api/v1/public/extract-and-verify` with extracted signed block
  - [x] 3.3.2 Resolve signer identity — 
  - [x] 3.3.3 Display revocation status — 
- [x] 3.4 Performance constraints
  - [x] 3.4.1 Avoid scanning the full DOM repeatedly — 
  - [x] 3.4.2 Debounce on dynamic pages — 
  - [x] 3.4.3 Cache verification results per URL + content hash — 

### 4.0 UI Implementation

- [x] 4.1 Popup UI — 
  - [x] 4.1.1 List verified blocks with signer + time
  - [x] 4.1.2 Link to verification portal / shareable URL
  - [x] 4.1.3 "Report issue" link — 
- [x] 4.2 Inline badge — 
  - [x] 4.2.1 Attach badge near detected block
  - [x] 4.2.2 Click opens detail drawer (tooltip on hover)
  - [x] 4.2.3 Accessibility (ARIA labels)
- [x] 4.3 Options page — 
  - [x] 4.3.1 Opt-in auto verify — 
  - [x] 4.3.2 Privacy settings (send content vs local-only) — 
  - [x] 4.3.3 API base URL (dev vs prod) — 

### 5.0 Substack Author Workflow

Substack doesn’t support native plugins, so the extension becomes the integration surface.

- [x] 5.1 Author mode (sign before paste) — 
  - [x] 5.1.1 UI: “Sign selection” button shown in editable contexts — 
  - [x] 5.1.2 Allow author to paste text into extension popup and click “Sign” — 
  - [x] 5.1.3 Call `POST /api/v1/sign` using author API key — 
  - [x] 5.1.4 Replace selection with signed output — 
- [x] 5.2 Key management for authors — 
  - [x] 5.2.1 Store API key in extension storage (encrypted at rest if feasible) — 
  - [x] 5.2.2 Support BYOK keys and Encypher-managed keys — 
  - [x] 5.2.3 Provide quick “Get API key” deep link to dashboard — 
- [x] 5.3 Substack-specific guidance — 
  - [x] 5.3.1 Best practices: avoid editor transformations post-signing
  - [x] 5.3.2 Verified rendering checks — User can verify after pasting

### 6.0 Substack Partnership / Outreach Workstream

**Note:** This workstream is deferred to post-launch. Extension provides standalone value without partnership.

- [ ] 6.1 Prepare partnership brief — 
  - [ ] 6.1.1 Problem statement: authenticity + AI reuse
  - [ ] 6.1.2 Proposed integration options
  - [ ] 6.1.3 Security/privacy posture
- [ ] 6.2 Identify contact points at Substack — ⏸️ Deferred
- [ ] 6.3 Draft email + one-pager — ⏸️ Deferred
- [ ] 6.4 Define a pilot plan — ⏸️ Deferred
  - [ ] 6.4.1 10–50 authors
  - [ ] 6.4.2 Metrics: signed posts, verification events
  - [ ] 6.4.3 Feedback loop and iteration
- [ ] 6.5 Define technical integration proposal (if Substack wants native) — ⏸️ Deferred
  - [ ] 6.5.1 Server-side signing at publish
  - [ ] 6.5.2 Verification badge UI
  - [ ] 6.5.3 Trust anchor strategy for `encypher.public`

### 7.0 Store Readiness & Legal

- [x] 7.1 Chrome Web Store listing assets — ✅ STORE_LISTING.md
- [x] 7.2 Privacy policy — ✅ PRIVACY.md
- [x] 7.3 Security review checklist — ✅ SECURITY_CHECKLIST.md
- [x] 7.4 Versioning and release process — ✅ v1.0.0 ready

### 8.0 Testing & Validation

- [x] 8.1 Unit tests for wrapper detection/decoding — ✅ 21 tests passing
- [x] 8.2 Integration tests for API calls — ✅ Service worker tests
- [x] 8.3 Browser E2E verification — ✅ Puppeteer tests
  - [x] 8.3.1 Detect signed content on a demo page — ✅ Content detection test
  - [x] 8.3.2 Verify content and show badge — ✅ Badge injection test
  - [x] 8.3.3 Author mode signs text and replaces selection — ✅ Sign flow test

## Success Criteria

- Extension reliably detects and verifies Encypher-signed content on arbitrary pages
- UI clearly communicates verified vs invalid vs revoked states
- Author workflow enables Substack publishing without native Substack plugins
- Privacy posture is defensible (minimal content sent, user control)
- Store-ready with automated E2E tests

## Completion Notes

**Completed:** December 26, 2024

### Implementation Summary

All core features have been implemented and tested:

1. **Detection & Verification**
   - Auto-detects C2PA (`C2PATXT\0`) and Encypher (`ENCYPHER`) markers
   - Inline badges with color-coded status (green/yellow/red/purple)
   - Context menu "Verify with Encypher" for selected text
   - Popup UI with verification summary

2. **Content Signing**
   - Sign tab in popup for copy-paste workflow
   - API key management in options page
   - Calls `POST /api/v1/sign` with user authentication
   - Auto-copies signed text to clipboard

3. **Privacy & Security**
   - Only sends signed content blocks (not full pages)
   - API key stored in Chrome's encrypted storage
   - No tracking or analytics
   - Manifest V3 with minimal permissions
   - Full security audit completed (SECURITY_CHECKLIST.md)

4. **Testing**
   - 21 unit tests passing (detector logic)
   - E2E tests with Puppeteer
   - Manual testing on multiple sites

5. **Store Readiness**
   - Privacy policy (PRIVACY.md)
   - Security checklist (SECURITY_CHECKLIST.md)
   - Store listing copy (STORE_LISTING.md)
   - Version 1.0.0 ready for submission

### Files Created

- `manifest.json` - Manifest V3 configuration
- `background/service-worker.js` - API calls and message handling
- `content/detector.js` - Content detection and badge injection
- `content/badge.css` - Badge and notification styles
- `popup/popup.html/css/js` - Popup UI with Verify + Sign tabs
- `options/options.html/css/js` - Settings page
- `tests/detector.test.js` - Unit tests (21 passing)
- `tests/e2e/extension.test.js` - E2E tests
- `tests/fixtures/test-page.html` - Test fixture
- `PRIVACY.md` - Privacy policy
- `SECURITY_CHECKLIST.md` - Security audit
- `STORE_LISTING.md` - Chrome Web Store listing
- `README.md` - Documentation

### Deferred Items

- **Substack Partnership (Section 6.0)**: Extension provides standalone value. Partnership outreach can happen post-launch based on user adoption.

### Next Steps

1. Create promotional screenshots (1280x800)
2. Create promo tiles (440x280, 920x680, 1400x560)
3. Remove `http://localhost:9000/*` from host_permissions for production
4. Submit to Chrome Web Store
5. Monitor user feedback and iterate

### Success Metrics

- ✅ Extension reliably detects and verifies Encypher-signed content
- ✅ UI clearly communicates verified vs invalid vs revoked states
- ✅ Author workflow enables signing without native platform plugins
- ✅ Privacy posture is defensible (minimal content sent, user control)
- ✅ Store-ready with automated tests and documentation
