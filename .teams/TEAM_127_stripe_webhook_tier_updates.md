# TEAM_127: Stripe webhook tier updates

**Active PRD**: `PRDs/CURRENT/PRD_Stripe_Webhook_Tier_Updates.md`
**Working on**: Update org tier after Stripe checkout via webhook
**Started**: 2026-01-22 18:25
**Status**: in_progress

## Session Progress
- [ ] Add internal auth-service endpoint to update org tier
- [ ] Update billing-service webhook handlers to call auth-service
- [ ] Add tests for tier update workflow
- [ ] Verify webhook logs + dashboard tier state

## Blockers
- None

## Handoff Notes
- Ensure STRIPE_WEBHOOK_SECRET set for valid webhook verification.
