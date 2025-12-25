# Browser Tools: Chrome Verifier Extension + Substack Author Workflow

**Status:** 🚧 In Progress  
**Current Goal:** Task 4.1 — Testing and refinement of core extension functionality.

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

- [ ] 1.1 Define primary personas
  - [ ] 1.1.1 Reader: verify an article they are reading
  - [ ] 1.1.2 Editor: quickly spot signed/unsigned sections
  - [ ] 1.1.3 Author: sign content before posting to Substack
- [ ] 1.2 Define UX surfaces
  - [ ] 1.2.1 Toolbar icon state (none found / found / verified / invalid)
  - [ ] 1.2.2 Popup summary (signed blocks, signers, timestamps)
  - [ ] 1.2.3 Inline badge overlay on detected signed blocks
  - [ ] 1.2.4 Context menu: “Verify selected text”
- [ ] 1.3 Define error UX
  - [ ] 1.3.1 Unknown signer
  - [ ] 1.3.2 Corrupted wrapper
  - [ ] 1.3.3 Revoked content

### 2.0 Privacy & Security Posture (Must Decide Early)

- [ ] 2.1 Decide verification mode defaults
  - [ ] 2.1.1 Default: local detection, user-initiated verification
  - [ ] 2.1.2 Optional: automatic verification (opt-in)
- [ ] 2.2 Define minimal data sent to Encypher (if any)
  - [ ] 2.2.1 Prefer sending only the signed block (not entire page)
  - [ ] 2.2.2 Set hard max payload size and truncate policy
- [ ] 2.3 Threat model
  - [ ] 2.3.1 Malicious pages with trap content
  - [ ] 2.3.2 Extension XSS / DOM injection
  - [ ] 2.3.3 Abuse of verification endpoint (rate limits)
- [ ] 2.4 Extension security hardening
  - [ ] 2.4.1 Strict CSP
  - [ ] 2.4.2 No remote code execution
  - [ ] 2.4.3 Permission minimization (host permissions)

### 3.0 Technical Architecture (Manifest V3)

- [x] 3.1 Extension scaffolding — ✅ `integrations/chrome-extension/`
  - [x] 3.1.1 Manifest V3 configuration — ✅ `manifest.json`
  - [x] 3.1.2 Service worker background — ✅ `background/service-worker.js`
  - [x] 3.1.3 Content scripts + isolated world — ✅ `content/detector.js`
- [x] 3.2 Wrapper detection + extraction — ✅ `content/detector.js`
  - [x] 3.2.1 Detect presence of variation selector ranges
  - [x] 3.2.2 Locate C2PA wrapper magic (`C2PATXT\0`) in decoded bytes
  - [x] 3.2.3 Extract clean text + wrapper span (for exclusions)
  - [x] 3.2.4 Handle multiple wrappers on a page
- [x] 3.3 Verification strategy — ✅ `background/service-worker.js`
  - [x] 3.3.1 Call `POST /api/v1/public/extract-and-verify` with extracted signed block
  - [ ] 3.3.2 Resolve signer identity via `GET /api/v1/public/c2pa/trust-anchors/{signer_id}` (if needed)
  - [ ] 3.3.3 Display revocation status (StatusList endpoints)
- [x] 3.4 Performance constraints
  - [x] 3.4.1 Avoid scanning the full DOM repeatedly — ✅ TreeWalker
  - [x] 3.4.2 Debounce on dynamic pages — ✅ MutationObserver with 500ms debounce
  - [x] 3.4.3 Cache verification results per URL + content hash — ✅ 5min TTL cache

### 4.0 UI Implementation

- [x] 4.1 Popup UI — ✅ `popup/popup.html`, `popup.css`, `popup.js`
  - [x] 4.1.1 List verified blocks with signer + time
  - [x] 4.1.2 Link to verification portal / shareable URL
  - [ ] 4.1.3 "Report issue" link
- [x] 4.2 Inline badge — ✅ `content/badge.css`, `content/detector.js`
  - [x] 4.2.1 Attach badge near detected block
  - [x] 4.2.2 Click opens detail drawer (tooltip on hover)
  - [x] 4.2.3 Accessibility (ARIA labels)
- [ ] 4.3 Options page
  - [ ] 4.3.1 Opt-in auto verify
  - [ ] 4.3.2 Privacy settings (send content vs local-only)
  - [ ] 4.3.3 API base URL (dev vs prod)

### 5.0 Substack Author Workflow

Substack doesn’t support native plugins, so the extension becomes the integration surface.

- [ ] 5.1 Author mode (sign before paste)
  - [ ] 5.1.1 UI: “Sign selection” button shown in editable contexts
  - [ ] 5.1.2 Allow author to paste text into extension popup and click “Sign”
  - [ ] 5.1.3 Call `POST /api/v1/sign` using author API key
  - [ ] 5.1.4 Replace selection with signed output
- [ ] 5.2 Key management for authors
  - [ ] 5.2.1 Store API key in extension storage (encrypted at rest if feasible)
  - [ ] 5.2.2 Support BYOK keys and Encypher-managed keys
  - [ ] 5.2.3 Provide quick “Get API key” deep link to dashboard
- [ ] 5.3 Substack-specific guidance
  - [ ] 5.3.1 Best practices: avoid editor transformations post-signing
  - [ ] 5.3.2 Verified rendering checks

### 6.0 Substack Partnership / Outreach Workstream

- [ ] 6.1 Prepare partnership brief
  - [ ] 6.1.1 Problem statement: authenticity + AI reuse
  - [ ] 6.1.2 Proposed integration options
  - [ ] 6.1.3 Security/privacy posture
- [ ] 6.2 Identify contact points at Substack
- [ ] 6.3 Draft email + one-pager
- [ ] 6.4 Define a pilot plan
  - [ ] 6.4.1 10–50 authors
  - [ ] 6.4.2 Metrics: signed posts, verification events
  - [ ] 6.4.3 Feedback loop and iteration
- [ ] 6.5 Define technical integration proposal (if Substack wants native)
  - [ ] 6.5.1 Server-side signing at publish
  - [ ] 6.5.2 Verification badge UI
  - [ ] 6.5.3 Trust anchor strategy for `encypher.public`

### 7.0 Store Readiness & Legal

- [ ] 7.1 Chrome Web Store listing assets
- [ ] 7.2 Privacy policy
- [ ] 7.3 Security review checklist
- [ ] 7.4 Versioning and release process

### 8.0 Testing & Validation

- [ ] 8.1 Unit tests for wrapper detection/decoding — ✅ node test runner
- [ ] 8.2 Integration tests for API calls — ✅ mocked HTTP
- [ ] 8.3 Browser E2E verification — ✅ puppeteer
  - [ ] 8.3.1 Detect signed content on a demo page
  - [ ] 8.3.2 Verify content and show badge
  - [ ] 8.3.3 Author mode signs text and replaces selection

## Success Criteria

- Extension reliably detects and verifies Encypher-signed content on arbitrary pages
- UI clearly communicates verified vs invalid vs revoked states
- Author workflow enables Substack publishing without native Substack plugins
- Privacy posture is defensible (minimal content sent, user control)
- Store-ready with automated E2E tests

## Completion Notes

(Filled when PRD is complete.)
