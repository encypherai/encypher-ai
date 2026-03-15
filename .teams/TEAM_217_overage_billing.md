# TEAM_217 -- Overage Billing, Payment Management, and WordPress Payment Flow

## Status: COMPLETE

## Current Goal
Implement automatic overage billing for users with a payment method on file, add payment management to dashboard settings, and let WordPress plugin users set up payment and bulk-sign from within the plugin.

## Overview
End-of-month reconciliation billing model: track overage in usage_records, monthly job creates Stripe InvoiceItems + Invoice. Uses Stripe Checkout SetupIntent for payment method collection. Overage preferences (overage_enabled, overage_cap_cents) stored on Organization model.

## Key Design Decisions
1. End-of-month reconciliation (not Stripe metered billing) -- free-tier orgs have no Stripe subscription
2. Stripe Checkout SetupIntent (not Elements) for payment collection -- minimal PCI scope
3. Overage preferences on Organization model, synced via internal endpoints

## Phase Tracking

### Phase 1: Schema Changes -- COMPLETE
- [x] 1.1 Auth-service Organization model: added has_payment_method, overage_enabled, overage_cap_cents
- [x] 1.2 Enterprise API Organization model: mirrored same columns
- [x] 1.3 UsageRecord ORM model created at enterprise_api/app/models/usage_record.py
- [x] 1.4 Auth-service internal billing-preferences endpoints (GET + POST)
- [x] Alembic migrations for both services

### Phase 2: Overage Auto-Billing -- COMPLETE
- [x] 2.1 Modify QuotaManager.check_quota() for overage allowance -- pytest
- [x] 2.2 UsageRecordService (record_overage, get_unbilled, mark_billed) -- pytest
- [x] 2.3 Overage pricing constants (OVERAGE_RATES_CENTS)
- [x] 2.4 Stripe overage product setup
- [x] 2.5 Monthly reconciliation job -- pytest
- [x] 2.6 Internal endpoints for usage billing
- [x] 2.7 Reconciliation endpoint on billing-service

### Phase 3: Dashboard Payment Management -- COMPLETE
- [x] 3.1 Billing-service payment method endpoints -- pytest
- [x] 3.2 Stripe webhook additions (setup mode + payment_method.detached)
- [x] 3.3 Dashboard API client types and methods
- [x] 3.4 Settings page billing tab

### Phase 4: WordPress Plugin Payment Flow -- COMPLETE
- [x] 4.1 Payment status endpoint in billing-service
- [x] 4.2 Plugin REST endpoints (payment-status, payment-setup)
- [x] 4.3 Bulk signing page payment gate
- [x] 4.4 Bulk signing JS payment check
- [x] 4.5 Settings page payment status display

### Phase 5: Tests -- COMPLETE (27 tests, all pass)
- [x] test_quota_overage.py (6 tests) -- pytest
- [x] test_usage_record_service.py (7 tests) -- pytest
- [x] test_payment_methods.py (9 tests) -- pytest
- [x] test_reconcile_overage.py (5 tests) -- pytest

## Files Modified (existing)
- services/auth-service/app/db/models.py (Organization model -- 3 new columns)
- services/auth-service/app/api/v1/organizations.py (billing-preferences endpoints)
- enterprise_api/app/models/organization.py (Organization model -- 3 new columns)
- enterprise_api/app/models/__init__.py (register UsageRecord)
- enterprise_api/app/utils/quota.py (overage logic in check_quota, overage headers)
- enterprise_api/app/utils/pricing.py (OVERAGE_RATES_CENTS)
- enterprise_api/app/api/v1/api.py (register internal_usage router)
- services/billing-service/app/api/v1/endpoints.py (payment method + overage + reconcile endpoints)
- services/billing-service/app/services/stripe_service.py (webhook handlers + overage product)
- services/billing-service/app/core/config.py (ENTERPRISE_API_URL)
- apps/dashboard/src/lib/api.ts (PaymentMethod, OveragePreferences types + methods)
- apps/dashboard/src/app/settings/page.tsx (billing tab)
- integrations/wordpress-provenance-plugin/.../class-encypher-provenance-rest.php (payment REST endpoints)
- integrations/wordpress-provenance-plugin/.../class-encypher-provenance-bulk.php (payment gate)
- integrations/wordpress-provenance-plugin/.../class-encypher-provenance-admin.php (payment status)
- integrations/wordpress-provenance-plugin/.../assets/js/bulk-mark.js (payment check)

## Files Created (new)
- services/auth-service/alembic/versions/017_add_overage_billing_columns.py
- enterprise_api/alembic/versions/20260315_100000_add_overage_billing_columns.py
- enterprise_api/app/models/usage_record.py
- enterprise_api/app/services/usage_record_service.py
- enterprise_api/app/api/v1/endpoints/internal_usage.py
- services/billing-service/app/tasks/__init__.py
- services/billing-service/app/tasks/reconcile_overage.py
- enterprise_api/tests/test_quota_overage.py
- enterprise_api/tests/test_usage_record_service.py
- services/billing-service/tests/test_payment_methods.py
- services/billing-service/tests/test_reconcile_overage.py

## Suggested Commit Message

feat: implement overage billing, payment management, and WordPress payment flow

Add automatic overage billing for users with a payment method on file.
When quota is exceeded and org has has_payment_method=true + overage_enabled=true,
requests are allowed and usage is tracked in usage_records for end-of-month
reconciliation via Stripe InvoiceItems.

Schema changes:
- Add has_payment_method, overage_enabled, overage_cap_cents to Organization
  model in both auth-service and enterprise_api with Alembic migrations
- Add UsageRecord ORM model mapping to existing usage_records table

Overage auto-billing:
- Modify QuotaManager.check_quota() to allow overage with cap enforcement
- Add UsageRecordService for recording and querying overage data
- Add OVERAGE_RATES_CENTS ($0.02/unit for billable quota types)
- Add monthly reconciliation job creating Stripe invoices
- Add internal endpoints for unbilled records, mark-billed, quota reset

Dashboard payment management:
- Add billing-service endpoints for payment method CRUD and overage preferences
- Add Stripe webhook handlers for setup_intent + payment_method.detached
- Add billing tab to dashboard settings with card management and overage toggle
- Add PaymentMethod/OveragePreferences types and API methods to dashboard client

WordPress plugin payment flow:
- Add payment-status and payment-setup REST endpoints to plugin
- Add payment gate on bulk signing page (requires payment method before purchase)
- Add payment status display in plugin admin settings

Tests: 27 tests across 4 test files, all passing
