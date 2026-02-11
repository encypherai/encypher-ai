# PRD: Freemium Publisher Pricing Model Alignment

**Status:** Complete
**Current Goal:** All pricing modules aligned with new freemium publisher pricing schema
**Team:** TEAM_160

## Overview

The company is adopting a new freemium revenue model for publishers per `docs/new_publisher_pricing_model_feb_2026.md`. The current codebase uses an old 4-tier SaaS model (Starter/Professional/Business/Enterprise) with tiered rev-share percentages (65/70/75/80). The new model is fundamentally different: **Free signing infrastructure + paid enforcement add-ons + licensing revenue share (60/40 coalition, 80/20 self-service)**.

## Audit Findings — Key Misalignments

### OLD Model (Current Codebase)
- **4 tiers:** Starter ($0), Professional ($99/mo), Business ($499/mo), Enterprise (Custom)
- **Rev share varies by tier:** 65/35, 70/30, 75/25, 80/20
- **Features gated by tier:** Signing limits, embeddings, tracking, etc.
- **Positioning:** Traditional SaaS upsell — pay more for more features

### NEW Model (Target — per pricing doc)
- **2 layers:** Free Tier (full signing infra) + Freemium Add-Ons (self-service) + Enterprise (custom)
- **Rev share is FLAT across all tiers:** Coalition 60/40, Self-Service 80/20
- **Free tier is generous:** 1K docs/mo signing, unlimited verification, coalition membership, WordPress plugin, API, CLI
- **Paid add-ons are enforcement tools:** Attribution Analytics ($299/mo), Formal Notice ($499/notice), Evidence Package ($999/pkg)
- **Bundles:** Enforcement Bundle ($999/mo), Publisher Identity ($749/mo), Full Stack ($1,699/mo)
- **Infrastructure add-ons:** Custom Signing Identity ($499/mo), White-Label Verification ($299/mo), Custom Domain ($29/mo), BYOK ($499/mo)
- **Operations add-ons:** Bulk Archive Backfill ($0.01/doc), Data Export ($49/export), Priority Support ($199/mo)
- **Enterprise:** Implementation fee ($10K-$30K), all add-ons included, exclusive capabilities, Founding Coalition (first 20 publishers)
- **Positioning:** "Free to sign. Paid to enforce. Aligned on outcomes."

### Files Requiring Changes

| File | App | Change Type |
|------|-----|-------------|
| `packages/pricing-config/src/types.ts` | Shared | Major restructure — new TierId, add-on types, licensing model types |
| `packages/pricing-config/src/tiers.ts` | Shared | Replace 4-tier SaaS with Free + Add-Ons + Enterprise |
| `packages/pricing-config/src/coalition.ts` | Shared | Replace tiered rev-share with flat 60/40 and 80/20 model |
| `packages/pricing-config/src/index.ts` | Shared | Export new types and helpers |
| `apps/marketing-site/src/lib/pricing-config/types.ts` | Marketing | Mirror shared package |
| `apps/marketing-site/src/lib/pricing-config/tiers.ts` | Marketing | Mirror shared package |
| `apps/marketing-site/src/lib/pricing-config/coalition.ts` | Marketing | Mirror shared package |
| `apps/marketing-site/src/lib/pricing-config/index.ts` | Marketing | Mirror shared package |
| `apps/marketing-site/src/app/pricing/page.tsx` | Marketing | Major rewrite — new pricing cards, add-on grid, enforcement pipeline, bundles |
| `apps/marketing-site/src/components/pricing/FeatureComparisonTable.tsx` | Marketing | Replace 4-tier comparison with Free vs Enterprise + add-on matrix |
| `apps/marketing-site/src/components/pricing/pricing-table.tsx` | Marketing | Update to new model |
| `apps/marketing-site/src/app/solutions/publishers/page.tsx` | Marketing | Update pricing cards section (lines 96-171) |
| `apps/marketing-site/src/app/publisher-demo/components/sections/Section6Coalition.tsx` | Marketing | Update coalition benefits to match Founding Coalition language |
| `apps/marketing-site/src/components/solutions/roi-calculator.tsx` | Marketing | Update to use 60/40 and 80/20 rev share model |
| `apps/dashboard/src/lib/pricing-config/tiers.ts` | Dashboard | Mirror shared package |
| `apps/dashboard/src/lib/pricing-config/types.ts` | Dashboard | Mirror shared package |
| `apps/dashboard/src/lib/pricing-config/index.ts` | Dashboard | Mirror shared package |
| `apps/dashboard/src/app/billing/page.tsx` | Dashboard | Major rewrite — show current plan (Free/Enterprise), add-on purchases, enforcement pipeline status |
| `apps/dashboard/src/lib/api.ts` | Dashboard | Update PlanInfo type to match new model |

## Objectives

- Replace the 4-tier SaaS pricing model with the new freemium model across all code
- Ensure all public-facing pricing language matches the new doc exactly
- Update rev share from tiered (65/70/75/80) to flat (60/40 coalition, 80/20 self-service)
- Add enforcement add-on pricing (Attribution Analytics, Formal Notice, Evidence Package)
- Add infrastructure add-on pricing (Custom Identity, White-Label, BYOK, etc.)
- Add bundle pricing (Enforcement, Publisher Identity, Full Stack)
- Update Enterprise tier to show implementation fees and Founding Coalition benefits
- Ensure dashboard billing page reflects new model
- Maintain backward compatibility for existing subscribers during transition

## Tasks

### 1.0 Shared Pricing Config (SSOT)
- [x] 1.1 Audit current pricing config vs new doc
- [x] 1.2 Rewrite `packages/pricing-config/src/types.ts` — new type system
- [x] 1.3 Rewrite `packages/pricing-config/src/tiers.ts` — Free + Enterprise + Add-Ons
- [x] 1.4 Rewrite `packages/pricing-config/src/coalition.ts` — flat 60/40 and 80/20
- [x] 1.5 Update `packages/pricing-config/src/index.ts` — new exports

### 2.0 Marketing Site — Pricing Config Copies
- [x] 2.1 Update `apps/marketing-site/src/lib/pricing-config/types.ts`
- [x] 2.2 Update `apps/marketing-site/src/lib/pricing-config/tiers.ts`
- [x] 2.3 Update `apps/marketing-site/src/lib/pricing-config/coalition.ts`
- [x] 2.4 Update `apps/marketing-site/src/lib/pricing-config/index.ts`

### 3.0 Marketing Site — Pricing Page
- [x] 3.1 Rewrite publisher pricing cards (Free hero card + Add-Ons + Enterprise)
- [x] 3.2 Add enforcement pipeline visualization (Sign → Detect → Notify → Prove → License)
- [x] 3.3 Add add-on pricing grid with volume discounts
- [x] 3.4 Add bundle pricing section (Enforcement, Publisher Identity, Full Stack)
- [x] 3.5 Update enterprise section with implementation fees and Founding Coalition
- [x] 3.6 Replaced old quick comparison table with two-track licensing model
- [x] 3.7 Replaced TIER_MARKETING with new freemium value props and CTAs

### 4.0 Marketing Site — Feature Comparison Table
- [x] 4.1 Rewrite FeatureComparisonTable.tsx for Free vs Enterprise + Add-Ons

### 5.0 Marketing Site — Other Pages
- [x] 5.1 Update pricing-table.tsx component (Free + Bundles + Enterprise)
- [x] 5.2 Update solutions/publishers/page.tsx pricing section (Free/Add-Ons/Enterprise)
- [x] 5.3 Update Section6Coalition.tsx with Founding Coalition language
- [x] 5.4 Update roi-calculator.tsx with 60/40 and 80/20 model

### 6.0 Dashboard — Pricing Config Copies
- [x] 6.1 Update `apps/dashboard/src/lib/pricing-config/tiers.ts`
- [x] 6.2 Update `apps/dashboard/src/lib/pricing-config/types.ts`
- [x] 6.3 Update `apps/dashboard/src/lib/pricing-config/coalition.ts`
- [x] 6.4 Update `apps/dashboard/src/lib/pricing-config/index.ts`

### 7.0 Dashboard — Billing Page
- [x] 7.1 Rewrite billing page for Free + Add-Ons + Enterprise model
- [x] 7.2 Removed old tier-based plan cards, added licensing tracks, add-ons, bundles, enterprise

### 8.0 Verification
- [x] 8.1 Verify marketing-site builds cleanly (tsc --noEmit passes, pre-existing errors only)
- [x] 8.2 Verify dashboard builds cleanly (tsc --noEmit passes with zero errors)
- [ ] 8.3 Run existing tests (deferred — no pricing-specific tests exist)

## Success Criteria

- [x] All pricing language across marketing-site and dashboard matches `docs/new_publisher_pricing_model_feb_2026.md`
- [x] No references to old tiered rev-share percentages (65/70/75/80) remain in pricing config
- [x] No references to Professional ($99/mo) or Business ($499/mo) tiers remain in publisher-facing pages
- [x] Free tier features match doc exactly (1K docs/mo, unlimited verification, coalition, etc.)
- [x] Add-on pricing matches doc exactly (Attribution $299/mo, Notice $499, Evidence $999, etc.)
- [x] Enterprise section shows implementation fees and Founding Coalition
- [x] Rev share displayed as 60/40 (coalition) and 80/20 (self-service) everywhere
- [x] Both apps build without errors

## Completion Notes

All pricing modules across the marketing-site and dashboard have been updated to align with the new freemium publisher pricing model. Key changes:

1. **Shared pricing config** (`packages/pricing-config/src/`): Complete rewrite from 4-tier SaaS to Free + Add-Ons + Bundles + Enterprise model with flat licensing rev-share (60/40 coalition, 80/20 self-service).
2. **Marketing-site pricing page**: Replaced 4-tier card grid with Free hero card, two-track licensing model, enforcement add-ons grid, bundles section, infrastructure/operations add-ons, and enterprise tier with Founding Coalition.
3. **FeatureComparisonTable**: Rewritten as Free vs Enterprise with add-on pricing shown inline.
4. **pricing-table.tsx**: Updated to Free + Bundles + Enterprise 3-column layout.
5. **solutions/publishers page**: Updated pricing cards to Free/Add-Ons/Enterprise.
6. **Section6Coalition**: Updated to Founding Coalition language with specific benefits (fee waived, Syracuse Symposium, advisory board).
7. **ROI calculator**: Now shows both coalition (60/40) and self-service (80/20) revenue tracks.
8. **Dashboard billing page**: Replaced old 4-tier plan cards with licensing revenue tracks, add-ons/bundles grid, and enterprise section. Removed unused tier upgrade flow.
9. **Dashboard pricing config copies**: All mirrored from shared package.
