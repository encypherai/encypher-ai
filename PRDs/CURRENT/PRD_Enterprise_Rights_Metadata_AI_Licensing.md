# Enterprise Rights Metadata + AI Licensing Signals

**Status:** 🚧 In Progress
**Current Goal:** Task 4.0 — AI Company Consumption (Coalition / Licensing).
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

- [x] 1.1 Identify standard C2PA assertions to use for rights
  - **Decision:** Use `c2pa.training-mining.v1` as the primary assertion for AI usage rights. This aligns with C2PA standard (publishes Jan 8, 2026) and our coalition strategy.
- [x] 1.2 Define Encypher canonical rights schema
  - **Decision:** Canonical rights metadata is embedded via `com.encypher.rights.v1` using the `rights` payload (Business+).
  - [x] 1.2.1 `copyright_holder` — ✅ pytest
  - [x] 1.2.2 `license_url` — ✅ pytest
  - [x] 1.2.3 `usage_terms` — ✅ pytest
  - [x] 1.2.4 `syndication_allowed` — ✅ pytest
  - [x] 1.2.5 `embargo_until` — ✅ pytest
  - [x] 1.2.6 `contact_email` — ✅ pytest
- [x] 1.3 Define AI usage permission schema
  - **Decision:** Use `c2pa.training-mining.v1` schema with `use.ai_training`, `use.ai_inference`, `use.data_mining` booleans + `constraint_info.license` and `constraint_info.attribution_required`.
  - [x] 1.3.1 `ai_training` — boolean in `use` object
  - [x] 1.3.2 `ai_inference` — boolean in `use` object
  - [x] 1.3.3 `ai_fine_tuning` — **Deferred:** Not in C2PA standard; can add via custom assertion later if needed
  - [x] 1.3.4 `commercial_ai_use` — **Deferred:** Not in C2PA standard; can add via custom assertion later if needed
- [x] 1.4 Decide which fields are included in
  - [x] 1.4.1 `c2pa.training-mining.v1` — **Primary assertion.** Fields: `use.ai_training`, `use.ai_inference`, `use.data_mining`, `constraint_info.license`, `constraint_info.attribution_required`
  - [x] 1.4.2 `c2pa.rights` — **Not used.** Not defined in C2PA text spec.
  - [x] 1.4.3 `com.encypher.rights.v1` — **Implemented.** Used to embed canonical rights metadata via the `rights` payload (Business+).

### 2.0 API & Manifest Embedding

- [x] 2.1 Extend `SignRequest` model to accept rights metadata
  - Added `template_id`, `validate_assertions`, and `rights` to `SignRequest` (Business+ gated)
- [x] 2.2 Add assertion construction logic
  - Template assertions are resolved and passed to `UnicodeMetadata.embed_metadata(custom_assertions=...)`
- [x] 2.3 Add template selection
  - [x] 2.3.1 Per-org default template — ✅ pytest
  - [x] 2.3.2 Per-document override — **Implemented.** `template_id` on `/sign` and `/sign/advanced`
- [x] 2.4 Surface rights fields in verification responses
  - `/verify` now returns `details.rights_signals.training_mining` and `details.rights_signals.rights`

### 3.0 Template Management

- [x] 3.1 Create assertion template CRUD (enterprise endpoints)
  - Enterprise-only schema authoring; Business+ template usage. Implemented in `/api/v1/enterprise/c2pa/templates`.
- [x] 3.2 Provide built-in templates
  - [x] 3.2.1 CC-BY — ✅ pytest (`tmpl_builtin_cc_by_4_0_v1`)
  - [x] 3.2.2 CC-BY-NC — ✅ pytest (`tmpl_builtin_cc_by_nc_4_0_v1`)
  - [x] 3.2.3 All Rights Reserved — ✅ pytest (`tmpl_builtin_all_rights_reserved_v1`)
  - [x] 3.2.4 Academic Open Access — ✅ pytest (`tmpl_builtin_academic_open_access_v1`)
  - [x] 3.2.5 News Wire syndication — ✅ pytest (`tmpl_builtin_news_wire_syndication_v1`)
- [ ] 3.3 Dashboard UI for template selection — Phase 2 (frontend work)

### 4.0 AI Company Consumption (Coalition / Licensing)

- [x] 4.1 Expose an API for AI companies to query licensing signals at scale — ✅ pytest (`test_licensing_content_include_rights_signals_creates_audit_log`)
- [x] 4.2 Ensure audit logs for AI access to rights metadata — ✅ pytest (`test_licensing_content_include_rights_signals_creates_audit_log`)
- [ ] 4.3 Integrate rights metadata with existing licensing agreements

### 5.0 Testing & Validation

- [x] 5.1 Unit tests passing — ✅ pytest
  - `test_builtin_c2pa_templates.py`, `test_sign_basic_template_usage.py`, `test_sign_advanced_template_usage.py`, `test_verify_rights_signals.py`, `test_sign_basic_rights_metadata.py`, `test_sign_advanced_rights_metadata.py`, `test_verify_rights_metadata_signals.py`, `test_org_default_template_usage.py`, `test_sign_basic_syndication_template_usage.py`
- [x] 5.2 Integration tests passing — ✅ pytest
  - All 426 tests pass, 60 skipped (opt-in load/e2e tests)

## Success Criteria

- Rights metadata is embedded and verifiable in manifests
- Templates reduce publisher errors and enforce consistency
- AI usage signals are machine-readable and auditable
- All tests passing with verification markers

## Completion Notes

**Phase 1 Complete (Dec 27, 2025):**
- Decided on `c2pa.training-mining.v1` as primary rights assertion (aligns with C2PA standard + GTM strategy)
- Implemented 4 built-in templates aligned with business value: All Rights Reserved, No AI Training, RAG Allowed, Real-time Quotes Allowed
- Template selection works on `/sign` and `/sign/advanced` (Business+ gated)
- Verification surfaces `rights_signals.training_mining` in `/verify` response
- All tests passing (✅ pytest, ✅ ruff)

**Deferred to Phase 2:**
- Dashboard UI for template selection
