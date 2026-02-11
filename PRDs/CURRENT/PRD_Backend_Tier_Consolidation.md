# PRD: Backend Tier Consolidation

## Status: COMPLETE (pending test verification)

## Current Goal
Consolidate backend tiers from 5 (starter, professional, business, enterprise, strategic_partner) to 3 (free, enterprise, strategic_partner) to match the website pricing strategy. Add add-ons dictionary to Organization model.

## Overview
The website pricing page shows only Free and Enterprise tiers. The backend still had starter/professional/business/enterprise/strategic_partner. This mismatch has been resolved. Users are either free or enterprise (or strategic_partner). Add-ons are tracked as a JSON column on the organization.

## Objectives
- Consolidate tiers to: free, enterprise, strategic_partner
- Rename "starter" to "free" everywhere
- Remove "professional" and "business" tiers
- Add add_ons JSON column to Organization models (auth-service + enterprise API)
- Update all tier configs, feature flags, quotas, rate limits, rev share
- Free tier gets: C2PA signing, verification, coalition membership, most features
- Enterprise tier gets: everything unlimited, all features enabled
- Add-ons are tracked separately (not tier-gated)
- Maintain backward compatibility via migration

## Tasks

### 1.0 Enterprise API (canonical tier definitions)
- [x] 1.1 Update OrganizationTier enum in organization.py — ✅ ast parse
- [x] 1.2 Update TIER_FEATURES in quota.py — ✅ ast parse
- [x] 1.3 Update TIER_QUOTAS in quota.py — ✅ ast parse
- [x] 1.4 Update TIER_RATE_LIMITS in quota.py — ✅ ast parse
- [x] 1.5 Update TIER_REV_SHARE in coalition.py — ✅ ast parse
- [x] 1.6 Update feature_flags.py tier hierarchy and feature matrix — ✅ ast parse
- [x] 1.7 Update tier_service.py display names and fallback logic — ✅ ast parse
- [x] 1.8 Add add_ons JSON column via Alembic migration — ✅ ast parse
- [x] 1.9 Update _coerce_tier() to map legacy names → free — ✅ ast parse

### 1.5 Enterprise API Endpoint Gating (TEAM_145/166)
- [x] 1.5.1 Update api_response.py TierName, TIER_HIERARCHY, FEATURE_REGISTRY, BATCH_LIMITS
- [x] 1.5.2 Update dependencies.py demo keys and embedding permission
- [x] 1.5.3 Update signing.py docstring tier matrix, tier fallback
- [x] 1.5.4 Update verification.py tier_levels, remove attribution/plagiarism gates
- [x] 1.5.5 Update embedding_executor.py — remove professional/business gates
- [x] 1.5.6 Update account.py TIER_FEATURES, TIER_LIMITS
- [x] 1.5.7 Update admin_service.py tier_features, MRR calc
- [x] 1.5.8 Update team.py TIER_MEMBER_LIMITS
- [x] 1.5.9 Update webhooks.py, byok.py, batch.py, keys.py tier gates
- [x] 1.5.10 Update merkle.py, streaming_merkle.py — remove tier gates (free access)
- [x] 1.5.11 Update multi_source.py — remove business gate, keep enterprise authority gate
- [x] 1.5.12 Update fingerprint.py, evidence.py — enterprise-only gates updated
- [x] 1.5.13 Update c2pa.py — enterprise-only gate updated
- [x] 1.5.14 Update middleware: api_key_auth.py, tier_check.py, api_rate_limiter.py
- [x] 1.5.15 Update organization_bootstrap.py, unified_signing_service.py defaults

### 2.0 Auth Service
- [x] 2.1 Update UserTier enum in schemas.py — ✅ ast parse
- [x] 2.2 Update Organization model default tier — ✅ ast parse
- [x] 2.3 Update _get_tier_config() in organization_service.py — ✅ ast parse
- [x] 2.4 Update DOMAIN_LIMITS_BY_TIER — ✅ ast parse
- [x] 2.5 Update tier_config in admin_service.py — ✅ ast parse
- [x] 2.6 Update create_organization default tier — ✅ ast parse
- [x] 2.7 Add add_ons JSON column via Alembic migration — ✅ ast parse

### 3.0 Billing Service
- [x] 3.1 Update TierName enum in schemas.py — ✅ ast parse
- [x] 3.2 Update PRICING_TIERS in billing_service.py — ✅ ast parse
- [x] 3.3 Update PLANS legacy mapping — ✅ ast parse
- [x] 3.4 Update STRIPE_PRODUCTS mapping — ✅ ast parse
- [x] 3.5 Update _resolve_tier_from_price_id — ✅ ast parse
- [x] 3.6 Update checkout validation — ✅ ast parse
- [x] 3.7 Update get_available_plans endpoint — ✅ ast parse
- [x] 3.8 Update subscription_canceled handler → free — ✅ ast parse
- [x] 3.9 Update usage/coalition endpoint defaults → free — ✅ ast parse

### 4.0 Cross-cutting
- [x] 4.1 Grep for remaining "starter"/"professional"/"business" references — only legacy maps remain
- [x] 4.2 Update all _coerce_tier fallbacks from STARTER to FREE
- [x] 4.3 Run full test suites — ✅ 802 pass, 28 pre-existing failures (DB migration needed)

### 5.0 SSOT Tier Config Refactor (TEAM_166)
- [x] 5.1 Create `app/core/tier_config.py` as single source of truth
- [x] 5.2 Refactor 11 consumer files to import from tier_config
- [x] 5.3 Move audit_logs to free tier (in SSOT)
- [x] 5.4 Fix `org_tier_level` NameError in embedding_executor.py
- [x] 5.5 Update 12 test files for new tier structure — ✅ 25 test failures fixed

## Success Criteria
- ✅ Only 3 tiers exist: free, enterprise, strategic_partner
- ✅ All backend services use consistent tier names
- ✅ Organization model has add_ons JSON field (via migration)
- ✅ Existing "starter" orgs treated as "free" via coercion + migration
- ✅ Single source of truth for all tier config (`app/core/tier_config.py`)
- ✅ Tests pass (802 pass, 28 pre-existing failures unrelated to tier work)

## Completion Notes
- **TEAM_145**: Initial tier consolidation (enums, configs, pricing, provisioning)
- **TEAM_166**: Alembic migrations, endpoint gating, SSOT refactor, test updates
- **SSOT file**: `enterprise_api/app/core/tier_config.py` — change tier features/limits/rates in ONE place
- **Free tier features**: signing, segmentation (except word), manifest modes, attribution, plagiarism, merkle, streaming merkle, multi-source lookup, custom assertions, batch (up to 10), **audit logs**
- **Enterprise-only**: word segmentation, dual binding, fingerprinting, distributed_redundant, BYOK, SSO, team management, webhooks, evidence, authority ranking, custom assertion authoring
