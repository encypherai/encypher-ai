# Enterprise CMS Integration: Contentful App + Webhooks

**Status:** 📋 Planning  
**Current Goal:** Task 1.1 — Confirm Contentful entry model and decide where signed output and verification metadata will be stored.

## Overview

Contentful is an API-first CMS used by modern publishers. This PRD defines a Contentful Marketplace App and webhook-based workflow to sign content at publish time, store signed variants safely, and render a reader-facing verification badge.

## Objectives

- Provide a Contentful App for editors to configure Encypher signing
- Automatically sign content on publish (webhook-driven) and re-sign on update
- Store signed output and verification metadata in dedicated entry fields
- Provide documentation and templates for common publisher models (articles, pages)

## Workstream Ownership (Parallel)

- **Suggested workstream:** `CMS Integrations — Contentful`
- **Primary owners:** JS/React engineer + backend engineer
- **Primary repos/areas:** Contentful app (new), Enterprise API endpoints (existing)

## Tasks

### 1.0 Discovery & Data Modeling

- [ ] 1.1 Identify target Contentful spaces/environments
- [ ] 1.2 Define content types supported
  - [ ] 1.2.1 `article`
  - [ ] 1.2.2 `page`
  - [ ] 1.2.3 long-form + multi-part content
- [ ] 1.3 Decide canonicalization rules
  - [ ] 1.3.1 Extract plaintext from rich text
  - [ ] 1.3.2 Normalize whitespace deterministically
- [ ] 1.4 Define storage fields
  - [ ] 1.4.1 `encypherSignedText` (Text)
  - [ ] 1.4.2 `encypherVerificationUrl` (Symbol)
  - [ ] 1.4.3 `encypherSignerId` (Symbol)
  - [ ] 1.4.4 `encypherSignedAt` (Date)
  - [ ] 1.4.5 `encypherStatus` (Symbol)

### 2.0 Contentful App (UI Extensions)

- [ ] 2.1 Create Contentful App scaffolding
- [ ] 2.2 Implement configuration UI
  - [ ] 2.2.1 API base URL
  - [ ] 2.2.2 API key storage (Contentful secrets)
  - [ ] 2.2.3 Default claim_generator/actions
  - [ ] 2.2.4 Per-content-type mapping
- [ ] 2.3 Implement entry sidebar extension
  - [ ] 2.3.1 Show signed/unsigned status
  - [ ] 2.3.2 “Sign now” button
  - [ ] 2.3.3 “Verify” link
- [ ] 2.4 Implement field editor helper
  - [ ] 2.4.1 Preview extracted plaintext that will be signed

### 3.0 Webhook Signing Service

- [ ] 3.1 Implement webhook receiver
  - [ ] 3.1.1 Verify webhook signatures
  - [ ] 3.1.2 Handle publish/unpublish events
- [ ] 3.2 Implement publish signing
  - [ ] 3.2.1 Extract plaintext from entry
  - [ ] 3.2.2 Call `POST /api/v1/sign`
  - [ ] 3.2.3 Persist signed output back to entry fields
- [ ] 3.3 Implement update policy
  - [ ] 3.3.1 Re-sign when canonical content changes
  - [ ] 3.3.2 Avoid re-sign loops (webhook recursion guard)
- [ ] 3.4 Error handling
  - [ ] 3.4.1 Record error status in entry
  - [ ] 3.4.2 Alerting via webhook/email (optional)

### 4.0 Reader Verification UX

- [ ] 4.1 Provide embed badge snippet
- [ ] 4.2 Provide guidance for using signed fields in rendering layer
  - [ ] 4.2.1 Next.js
  - [ ] 4.2.2 Gatsby

### 5.0 Marketplace Distribution

- [ ] 5.1 Prepare Contentful Marketplace listing
- [ ] 5.2 Provide install/config docs

### 6.0 Testing & Validation

- [ ] 6.1 Unit tests passing — ✅ npm test
- [ ] 6.2 Integration tests passing — ✅ mocked Contentful webhook
- [ ] 6.3 End-to-end validation
  - [ ] 6.3.1 Publish entry → signed fields populated
  - [ ] 6.3.2 Render signed field on site → verification passes

## Success Criteria

- Contentful publishers can enable signing with minimal setup
- Signing and re-signing happen reliably without loops
- Signed fields render correctly in production sites

## Completion Notes

(Filled when PRD is complete.)
