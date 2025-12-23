# Enterprise CMS Integration: Ghost (Webhooks + Admin API)

**Status:** 📋 Planning  
**Current Goal:** Task 1.1 — Confirm Ghost publishing workflow and determine safe storage for signed content.

## Overview

Ghost is a fast-growing CMS for publishers and newsletters. This PRD defines a Ghost integration using webhooks and the Ghost Admin API to sign posts on publish/update, store signed output, and surface verification badges in Ghost themes.

## Objectives

- Enable automatic C2PA signing on publish and re-signing on update
- Use Ghost webhooks + Admin API for integration (no custom server mods required)
- Provide theme helpers for verification badges
- Provide bulk backfill tooling

## Workstream Ownership (Parallel)

- **Suggested workstream:** `CMS Integrations — Ghost`
- **Primary owners:** JS/Node engineer + frontend/theme engineer
- **Primary repos/areas:** integration service (new), Ghost theme snippets (new)

## Tasks

### 1.0 Discovery & Content Model

- [ ] 1.1 Confirm Ghost versions and deployment types
  - [ ] 1.1.1 Ghost(Pro)
  - [ ] 1.1.2 Self-hosted Ghost
- [ ] 1.2 Define canonical content extraction
  - [ ] 1.2.1 Source: mobiledoc/lexical/html
  - [ ] 1.2.2 Deterministic plaintext extraction rules
- [ ] 1.3 Define storage approach
  - [ ] 1.3.1 Store signed content in a separate custom field (preferred)
  - [ ] 1.3.2 Store verification URL in a tag or custom field

### 2.0 Webhook Integration Service

- [ ] 2.1 Create webhook receiver
  - [ ] 2.1.1 Verify webhook authenticity
  - [ ] 2.1.2 Handle publish/update events
- [ ] 2.2 Implement signing pipeline
  - [ ] 2.2.1 Extract canonical plaintext
  - [ ] 2.2.2 Call `POST /api/v1/sign`
  - [ ] 2.2.3 Update post via Ghost Admin API
- [ ] 2.3 Prevent webhook recursion loops
  - [ ] 2.3.1 Use a marker header/tag
  - [ ] 2.3.2 Ignore updates triggered by signer
- [ ] 2.4 Error handling
  - [ ] 2.4.1 Persist signing status
  - [ ] 2.4.2 Provide manual retry endpoint

### 3.0 Theme Integration (Reader Experience)

- [ ] 3.1 Provide theme snippets
  - [ ] 3.1.1 Badge UI
  - [ ] 3.1.2 Link to verification URL
- [ ] 3.2 Provide guidance for rendering signed content
  - [ ] 3.2.1 Ensure variation selectors survive HTML rendering
  - [ ] 3.2.2 Avoid transformations that mutate text post-signing

### 4.0 Bulk Backfill

- [ ] 4.1 Build backfill script
  - [ ] 4.1.1 Iterate posts via Admin API
  - [ ] 4.1.2 Sign in batches
  - [ ] 4.1.3 Emit report

### 5.0 Packaging & Documentation

- [ ] 5.1 Create install/config docs
- [ ] 5.2 Provide sample deployment options (serverless vs container)

### 6.0 Testing & Validation

- [ ] 6.1 Unit tests passing — ✅ npm test
- [ ] 6.2 Integration tests passing — ✅ mocked Ghost webhooks/Admin API
- [ ] 6.3 End-to-end validation
  - [ ] 6.3.1 Publish → signed content stored
  - [ ] 6.3.2 Reader verifies and sees badge

## Success Criteria

- Ghost publishers can enable signing without custom platform modifications
- Signing/re-signing works reliably and avoids loops
- Reader UI shows verification badge and links to valid verification details

## Completion Notes

(Filled when PRD is complete.)
