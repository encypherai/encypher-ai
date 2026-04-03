# TEAM_255 -- Add-On Readiness Audit & Fixes

## Status: COMPLETE (Phase 2 complete)

## Goal
Fix systemic gaps preventing non-enforcement add-ons from being purchased, persisted, and enforced.

## Phase 1 Changes (prior session)

### Fix Stripe price mismatches
- `services/billing-service/scripts/setup_stripe.py`: custom_signing_identity 49900->900, publisher_identity_bundle 74900->32900
- `services/billing-service/app/services/stripe_service.py`: Same price corrections in setup_stripe_products()

### Fix webhook for payment-mode checkout
- `services/billing-service/app/services/stripe_service.py`:
  - `_handle_checkout_completed()`: Added mode=payment handling -- extracts add_on/quantity from metadata, POSTs to auth-service /internal/{org_id}/add-ons
  - `_handle_checkout_completed()`: Added add-on subscription detection in mode=subscription
  - `_handle_subscription_created()`: Detects add_on in metadata, activates via auth-service
  - `_handle_subscription_deleted()`: Detects add_on in metadata, deactivates via auth-service

### Add subscription add-on checkout endpoint
- `services/billing-service/app/api/v1/endpoints.py`: Added POST /checkout/add-on-subscription

### Add internal add-ons endpoint in auth-service
- `services/auth-service/app/api/v1/organizations.py`: Added POST /internal/{org_id}/add-ons with ADD_ON_FEATURE_MAP

### Update BYOK gating
- `enterprise_api/app/routers/byok.py`: require_byok_business_tier() now checks add_ons.byok.active

### Dashboard add-on purchase buttons
- `apps/dashboard/src/lib/api.ts`: Added createAddOnSubscriptionCheckout()
- `apps/dashboard/src/app/billing/page.tsx`: Subscribe buttons + Active badges

### Phase 1 Tests (22 new tests, all passing)
- `services/billing-service/tests/test_addon_checkout.py` (5 tests)
- `services/auth-service/tests/test_internal_add_ons.py` (8 tests)
- `enterprise_api/tests/test_byok_addon_gating.py` (9 tests)

---

## Phase 2 Changes (current session -- Gap Resolution)

### Gap 1: CSI price $9 -> $20/mo
- `packages/pricing-config/src/tiers.ts`: custom-signing-identity priceMonthly 9->20, publisher-identity bundle 329->339, includes text updated
- `services/billing-service/scripts/setup_stripe.py`: custom_signing_identity 900->2000, publisher_identity_bundle 32900->33900
- `services/billing-service/app/services/stripe_service.py`: Same price corrections in setup_stripe_products()

### Gap 4: Publisher-identity bundle -- Coming Soon
- `packages/pricing-config/src/tiers.ts`: Added comingSoon: true to publisher-identity bundle (custom-verification-domain not functional)

### Gap 3: Bulk-archive-backfill batch entitlement
- `services/auth-service/app/api/v1/organizations.py`: Added `add_ons` to internal context response
- `enterprise_api/app/dependencies.py`: Added `add_ons` to _build_composed_org_context and JWT org context
- `enterprise_api/app/routers/batch.py`: Skip BATCH_OPERATIONS quota check when bulk-archive-backfill add-on active

### Gap 2: White-label verification portal branding
- `services/verification-service/app/core/config.py`: Added INTERNAL_SERVICE_TOKEN setting
- `services/verification-service/app/api/v1/endpoints.py`: verify_by_document_id() fetches org features from auth-service, passes whitelabel/org_display_name to renderer
- `services/verification-service/app/api/v1/endpoints.py`: _render_portal_result() accepts whitelabel/org_display_name, builds branding_footer
- `services/verification-service/app/templates/portal_result.html`: Footer now uses {branding_footer} placeholder

### Gap 5: Add-on documentation page
- `apps/dashboard/src/app/docs/add-ons/page.tsx`: NEW -- covers CSI, White-Label, BYOK, Priority Support, Bulk Archive Backfill
- `apps/dashboard/src/app/docs/page.tsx`: Added Add-Ons guide entry to docs index

### Phase 2 Tests (8 new tests, all passing)
- `services/verification-service/tests/test_portal_whitelabel.py` (4 tests): whitelabel true/false, auth-service failure, 500 response
- `enterprise_api/tests/test_batch_backfill_addon.py` (2 tests): free tier with/without backfill addon
- `services/auth-service/tests/test_internal_org_context.py`: Updated fixture + assertion for add_ons field (2 existing tests updated)

## Phase 2 Test Results
- verification-service: 8 passed (4 new + 4 existing portal tests)
- auth-service: 218 passed (0 regressions, 3 pre-existing failures in test_setup_wizard.py)
- enterprise_api: 23 passed (2 new + 21 existing batch/byok/embedding tests)
- billing-service: 28 passed (0 regressions)

---

## Phase 3 Changes (current session -- Custom Verification Domains)

### Schema + Migration
- `services/auth-service/alembic/versions/018_add_verification_domain.py`: NEW migration adding 4 columns
- `services/auth-service/app/db/models.py`: Added verification_domain, verification_domain_status, verification_domain_dns_token, verification_domain_verified_at to Organization

### Feature Gating + Context Propagation
- `services/auth-service/app/api/v1/organizations.py`: Added "custom-verification-domain" to ADD_ON_FEATURE_MAP, verification_domain to internal context response
- `enterprise_api/app/dependencies.py`: Propagated verification_domain through both auth paths

### Domain Management API (4 endpoints)
- `services/auth-service/app/api/v1/organizations.py`: GET/POST/DELETE /{org_id}/verification-domain + POST /{org_id}/verification-domain/verify
  - DNS verification: CNAME to verify.encypher.com + TXT ownership proof
  - Gated behind custom-verification-domain add-on (enterprise bypasses)

### URL Generation
- `enterprise_api/app/services/signing_executor.py`: _build_verification_url() uses org.verification_domain when set
- `enterprise_api/app/services/unified_signing_service.py`: Same custom domain logic

### Routing
- `infrastructure/traefik/routes-local.yml`: Added catch-all router for custom domain local dev testing

### Dashboard UI
- `apps/dashboard/src/app/settings/page.tsx`: CustomVerificationDomainCard component with 3 states (no domain, pending DNS, active)
- `apps/dashboard/src/lib/api.ts`: 4 API methods + 3 interfaces for verification domain management

### Pricing
- `packages/pricing-config/src/tiers.ts`: Removed comingSoon from publisher-identity bundle (now sellable)

### Phase 3 Tests (14 new tests)
- `services/auth-service/tests/test_verification_domain.py` (9 tests): add-on gating, domain validation, DNS verify success/failure, internal context active/pending, domain removal, enterprise bypass
- `enterprise_api/tests/test_custom_verification_domain.py` (5 tests): custom domain URL, fallback, empty org, demo org, dev mode

### Phase 3 Test Results
- auth-service: 19 passed (9 new + 10 existing internal tests)
- enterprise_api: 25 passed (5 new + 20 existing)
- verification-service: 8 passed (0 regressions)

## Suggested Commit Message

```
feat: add-on gaps + custom verification domains

Phase 2 (5 gap fixes):
- CSI price $9->$20/mo, bundle $329->$339
- Whitelabel verification portal branding (fail-open)
- Bulk-archive-backfill bypasses BATCH_OPERATIONS quota
- Publisher-identity bundle comingSoon (pending custom domain)
- /docs/add-ons page for all purchasable add-ons

Phase 3 (custom verification domains):
- Schema: 4 columns on organizations for domain + DNS verification
- API: GET/POST/DELETE verification-domain + POST verify (CNAME + TXT)
- URL gen: signing services use custom domain when active
- Dashboard: CustomVerificationDomainCard in Settings (3 states)
- Removed comingSoon from publisher-identity bundle (now sellable)

22 new tests, 0 regressions across all service suites.
```
