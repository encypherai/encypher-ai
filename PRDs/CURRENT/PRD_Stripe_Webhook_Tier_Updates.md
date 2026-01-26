# Stripe Webhook Tier Updates

**Status:** 🔄 In Progress
**Current Goal:** Implement webhook-driven tier updates after Stripe checkout.

## Overview
Stripe checkout completes successfully, but organization tiers are not updated because webhook handlers are TODO and no internal auth-service update path exists. This work adds a service-to-service endpoint in auth-service and updates billing-service webhook handlers to sync Stripe subscription data, tier, and org settings.

## Objectives
- Add internal auth-service endpoint to update org tier/stripe metadata.
- Update billing-service webhook handlers to resolve tier and sync subscription/org state.
- Add tests for tier mapping and internal update endpoint.
- Verify webhook logs + dashboard reflect updated tier.

## Tasks

### 1.0 Internal Tier Update API
- [x] 1.1 Add INTERNAL_SERVICE_TOKEN config in auth-service
- [x] 1.2 Add internal org tier update endpoint + service method
- [x] 1.3 Add auth-service tests for internal endpoint

### 2.0 Billing Webhook Sync
- [x] 2.1 Add INTERNAL_SERVICE_TOKEN config in billing-service
- [x] 2.2 Resolve tier from Stripe price IDs
- [x] 2.3 Upsert subscription record and call auth-service internal endpoint
- [x] 2.4 Add billing-service tests for tier mapping

### 3.0 Verification
- [x] 3.1 Run lint + tests
- [ ] 3.2 Verify webhook logs show updates
- [ ] 3.3 Verify dashboard tier reflects upgrade

## Success Criteria
- Stripe webhooks update org tier + subscription fields.
- Billing-service logs show successful sync.
- Dashboard shows updated tier after payment.
- Tests pass.

## Completion Notes
- 
