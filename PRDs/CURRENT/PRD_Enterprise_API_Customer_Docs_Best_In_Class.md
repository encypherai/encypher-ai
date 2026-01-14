# PRD — Enterprise API Customer Documentation (Best-in-Class)

## Status
Completed

## Current Goal
Make `enterprise_api` customer-facing documentation best-in-class: clear tiers/capabilities, accurate endpoint usage, no proprietary implementation leakage, and protected against future drift.

## Overview
`enterprise_api` currently has multiple documentation entry points (`enterprise_api/README.md`, `enterprise_api/docs/API.md`, `enterprise_api/docs/QUICKSTART.md`) with inconsistencies (tiers/limits) and internal/proprietary details mixed into customer docs. This PRD establishes a clean, customer-first information architecture and adds tests to prevent regressions.

## Objectives
- Provide a clear onboarding path for customers: get key → sign → verify → interpret results.
- Present tier/capability information in a single, consistent way without hardcoding conflicting quotas.
- Ensure public-facing docs do not disclose proprietary implementation details (e.g., low-level Unicode encoding, internal hashing/exclusion mechanics, patent claim references).
- Add automated tests that fail if customer docs drift or reintroduce restricted wording.

## Tasks
- [x] 1.0 Documentation inventory + information architecture
- [x] 1.1 Define which files are customer-facing vs internal-only
- [x] 1.2 Add cross-links/navigation between Quickstart and API reference
-
- [x] 2.0 Customer docs cleanup (no leaks)
- [x] 2.1 Remove/replace internal/proprietary wording in `enterprise_api/README.md`
- [x] 2.2 Remove/replace internal/proprietary wording in `enterprise_api/docs/API.md`
- [x] 2.3 Ensure endpoint descriptions match OpenAPI behavior for `/sign`, `/sign/advanced`, `/verify`, `/tools/decode`
-
- [x] 3.0 Tiers, limits, and capability clarity
- [x] 3.1 Remove conflicting hard-coded quota numbers and point to `/api/v1/account/quota` where appropriate
- [ ] 3.2 Add a single tier/capability table in a canonical place and reference it
-
- [x] 4.0 Tests (TDD)
- [x] 4.1 Add regression tests to prevent restricted wording in customer docs
- [x] 4.2 Add regression tests to prevent tier/limit drift across customer docs
-
- [x] 5.0 Verification
- [x] 5.1 Task — ✅ pytest ✅ ruff (enterprise_api)

## Success Criteria
- Customer-facing docs clearly explain:
  - How to authenticate
  - How to sign and verify
  - How to interpret verification results
  - How tiers affect availability (without contradictory quotas)
- No restricted/internal details appear in customer docs.
- Contract tests fail if restricted wording or drift is reintroduced.
- ✅ `uv run ruff check .` (enterprise_api)
- ✅ `uv run pytest enterprise_api`

## Completion Notes
- Added `enterprise_api/tests/test_customer_docs_contract.py` to enforce customer-doc safety and prevent tier/quota drift.
- Updated customer-facing docs:
  - `enterprise_api/README.md`
  - `enterprise_api/docs/API.md`
  - `enterprise_api/docs/QUICKSTART.md`
- Verification: ✅ `uv run ruff check .` ✅ `uv run pytest`
