# TEAM_173 — Pricing Alignment Audit & Rev Share SSOT Consolidation

**Date:** 2026-02-12
**Task:** Audit codebase pricing alignment, fix discrepancies, and consolidate all revenue share values into a single source of truth.

## Status: Complete

## Session 1 — Audit & Initial Fixes

The codebase was **largely aligned** with the new pricing model but had several discrepancies:
- Enterprise tier rev share was 85/15 → fixed to 60/40
- Auth-service default coalition_rev_share was 65 → fixed to 60
- Stripe service had legacy professional/business products → replaced with freemium add-ons
- Enterprise API README had old 4-tier structure → updated to free/enterprise + two-track
- Test fixtures had stale rev share values → fixed

## Session 2 — SSOT Consolidation

**Goal:** Eliminate ALL hardcoded revenue share numbers. Everything must derive from a single source of truth.

### Created SSOT Module
- `shared_commercial_libs/src/encypher_commercial_shared/core/pricing_constants.py` — canonical source
- `enterprise_api/app/core/pricing_constants.py` — enterprise API local copy (no shared lib dependency)
- Vendored copies to: auth-service, billing-service, key-service, coalition-service

### Files Updated to Import from SSOT

**Enterprise API:**
- `app/core/tier_config.py` — imports from `app.core.pricing_constants`
- `app/utils/pricing.py` — `DEFAULT_COALITION_REV_SHARE`
- `app/models/organization.py` — DB column defaults
- `app/dependencies.py` — fallback rev share values
- `app/services/organization_bootstrap.py` — bootstrap defaults
- `tests/conftest.py` — seed data
- `tests/test_coalition_api.py` — assertions
- `tests/test_api_key_auth.py` — mock data

**Auth Service:**
- `app/services/auth_service.py` — org creation default
- `app/services/organization_service.py` — tier config dict
- `app/db/models.py` — DB column default
- `tests/conftest.py` — registered core.pricing_constants in mock module hierarchy
- `tests/test_internal_org_context.py` — fixture
- `tests/test_internal_org_tier_update.py` — fixture

**Key Service:**
- `app/db/models.py` — DB column default (was 65, now SSOT)
- `app/services/key_service.py` — org creation fallback + super-admin context

**Billing Service:**
- `app/services/billing_service.py` — PRICING_TIERS dict

### Test Results
- **Enterprise API:** 35/35 passed (test_api_key_auth + test_coalition_api)
- **Auth Service:** 129/129 passed (1 pre-existing email test failure excluded)
- **Key Service:** 12/12 passed
- **Billing Service:** imports verified; pre-existing test failures (tier enum consolidation) unrelated

### Alembic Migrations
Left unchanged — they are historical records and should not be modified.

### Remaining Hardcoded Values (intentional)
- `key-service/tests/conftest.py`: `coalition_rev_share=0` — intentional test fixture for non-coalition org
- Alembic migration files — historical, must not change

## Suggested Git Commit Message

```
feat(pricing): consolidate all rev share values into SSOT

TEAM_173: Eliminate hardcoded revenue share numbers across all services.

Created pricing_constants.py as the single source of truth for:
- Coalition deals: 60% publisher / 40% Encypher
- Self-service deals: 80% publisher / 20% Encypher

Updated consumers in enterprise_api, auth-service, key-service, and
billing-service to import from the SSOT module instead of hardcoding
values. Fixed key-service DB default from stale 65 to SSOT constant.

Updated test fixtures and assertions to use SSOT constants.
Updated auth-service test conftest to register shared lib core module.

Files created:
- shared_commercial_libs/.../core/pricing_constants.py
- enterprise_api/app/core/pricing_constants.py
- Vendored copies to auth/billing/key/coalition services

No alembic migrations modified (historical records).
```
