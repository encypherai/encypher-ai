# Enterprise Rights Metadata + AI Licensing Signals

**Status:** 📋 Planning  
**Current Goal:** Task 1.1 — Decide which C2PA assertions and Encypher custom assertions will be authoritative for rights + AI usage.
**Related PRD:** `PRDs/CURRENT/PRD_API_Tier_Endpoint_Simplification.md` (TEAM_034) defines tier gating + public endpoint contract; this PRD remains the SSOT for rights field definitions and templates.

## Overview

Enterprise publishers require standardized licensing metadata embedded into C2PA manifests so that downstream consumers (including AI companies) can understand usage rights and training permissions. This PRD defines rights assertions, templates, and integration points with coalition/licensing workflows.

## Objectives

- Embed explicit rights metadata in manifests in a standards-aligned way
- Provide per-publisher templates for consistent rights declarations
- Support machine-readable AI training/mining permissions
- Surface rights signals in verification responses and dashboards

## Tasks

### 1.0 Spec Alignment & Schema Design

- [ ] 1.1 Identify standard C2PA assertions to use for rights
- [ ] 1.2 Define Encypher canonical rights schema
  - [ ] 1.2.1 `copyright_holder`
  - [ ] 1.2.2 `license_url`
  - [ ] 1.2.3 `usage_terms`
  - [ ] 1.2.4 `syndication_allowed`
  - [ ] 1.2.5 `embargo_until`
  - [ ] 1.2.6 `contact_email`
- [ ] 1.3 Define AI usage permission schema
  - [ ] 1.3.1 `ai_training`
  - [ ] 1.3.2 `ai_inference`
  - [ ] 1.3.3 `ai_fine_tuning`
  - [ ] 1.3.4 `commercial_ai_use`
- [ ] 1.4 Decide which fields are included in
  - [ ] 1.4.1 `c2pa.training-mining.v1`
  - [ ] 1.4.2 `c2pa.rights` (if applicable)
  - [ ] 1.4.3 `com.encypher.rights.v1` (custom assertion, if needed)

### 2.0 API & Manifest Embedding

- [ ] 2.1 Extend `SignRequest` model to accept rights metadata
- [ ] 2.2 Add assertion construction logic
- [ ] 2.3 Add template selection
  - [ ] 2.3.1 Per-org default template
  - [ ] 2.3.2 Per-document override
- [ ] 2.4 Surface rights fields in verification responses

### 3.0 Template Management

- [ ] 3.1 Create assertion template CRUD (enterprise endpoints)
- [ ] 3.2 Provide built-in templates
  - [ ] 3.2.1 CC-BY
  - [ ] 3.2.2 CC-BY-NC
  - [ ] 3.2.3 All Rights Reserved
  - [ ] 3.2.4 Academic Open Access
  - [ ] 3.2.5 News Wire syndication
- [ ] 3.3 Dashboard UI for template selection

### 4.0 AI Company Consumption (Coalition / Licensing)

- [ ] 4.1 Expose an API for AI companies to query licensing signals at scale
- [ ] 4.2 Ensure audit logs for AI access to rights metadata
- [ ] 4.3 Integrate rights metadata with existing licensing agreements

### 5.0 Testing & Validation

- [ ] 5.1 Unit tests passing — ✅ pytest
- [ ] 5.2 Integration tests passing — ✅ pytest

## Success Criteria

- Rights metadata is embedded and verifiable in manifests
- Templates reduce publisher errors and enforce consistency
- AI usage signals are machine-readable and auditable
- All tests passing with verification markers

## Completion Notes

(Filled when PRD is complete.)
