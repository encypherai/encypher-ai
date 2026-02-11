# TEAM_162 — Enterprise Pricing Page Cleanup

## Status: Complete

## Objective
Remove internal enterprise tier details (Tier 1/2/3 tables, implementation fees, licensing potential ranges, founding coalition internal details) from all public-facing pricing pages. Enterprise should only show benefits + "Contact for Pricing".

## Changes Made

### 1. Pricing Page — Publishers Enterprise Section
**File**: `apps/marketing-site/src/app/pricing/page.tsx` (lines ~420-468)
- **Removed**: Tier 1/2/3 table with Licensing Potential (>$20M, $3-20M, <$3M) and Implementation Fee ($30K, $20K, $10K)
- **Removed**: Founding Coalition (First 20 Publishers) section with internal benefits
- **Replaced with**: Two-column benefits layout (Everything Unlimited + Exclusive Capabilities) + "Contact for Pricing" CTA

### 2. Pricing Page — Enterprises Section
**File**: `apps/marketing-site/src/app/pricing/page.tsx` (lines ~638-702)
- **Removed**: Pilot / Production / Strategic 3-card tier layout with internal engagement levels
- **Replaced with**: Single enterprise card with Infrastructure + Support & Services benefits + "Contact for Pricing" CTA

### 3. Pricing Table Component
**File**: `apps/marketing-site/src/components/pricing/pricing-table.tsx`
- **Removed**: "Founding coalition members get implementation fee waived" from description
- **Removed**: Licensing Revenue "Same 60/40 · 80/20 splits" internal detail box
- **Fixed**: Contact Sales link from `/company#contact` to `/contact`

### 4. Publisher Demo Section6
**File**: `apps/marketing-site/src/app/publisher-demo/components/sections/Section6Coalition.tsx`
- **Changed**: "Implementation fee waived (up to $30K value)" → "Implementation fee waived for founding members" (removed specific dollar amount)

### 5. AI Copyright Infringement Page
**File**: `apps/marketing-site/src/app/ai-copyright-infringement/page.tsx`
- **Removed**: "Implementation fee + 25-30% of licensing revenue enabled"
- **Replaced with**: "Success-aligned pricing means no licensing revenue = no payment. Contact us for details."

### 6. Enforcement Add-Ons — "Coming Soon" (no pricing)
**Type changes**: `packages/pricing-config/src/types.ts`, `apps/marketing-site/src/lib/pricing-config/types.ts`, `apps/dashboard/src/lib/pricing-config/types.ts`
- Added `comingSoon?: boolean` to `AddOnConfig` and `BundleConfig` interfaces

**Data changes**: `packages/pricing-config/src/tiers.ts`, `apps/marketing-site/src/lib/pricing-config/tiers.ts`, `apps/dashboard/src/lib/pricing-config/tiers.ts`
- Marked `attribution-analytics`, `formal-notice`, `evidence-package` as `comingSoon: true`
- Marked `enforcement-bundle` and `full-stack` bundles as `comingSoon: true` (depend on unbuilt enforcement features)
- `publisher-identity` bundle and `custom-verification-domain` add-on kept with pricing (near-term buildable)

**UI changes — Marketing site pricing page** (`apps/marketing-site/src/app/pricing/page.tsx`):
- Enforcement add-on cards: show "Coming Soon" badge instead of price, hide volume pricing
- Bundle cards: show "Coming Soon" badge, hide price/savings, suppress "Most Popular" badge
- Infrastructure/operations cards: comingSoon-aware (future-proofed)

**UI changes — Pricing table component** (`apps/marketing-site/src/components/pricing/pricing-table.tsx`):
- Bundle list items: show "Coming Soon" badge instead of price/savings for comingSoon bundles
- Hardcoded enforcement add-on list items: replaced prices with "Coming Soon" badges

**UI changes — Dashboard billing page** (`apps/dashboard/src/app/billing/page.tsx`):
- Bundle cards: show "Coming Soon" badge, hide price/savings for comingSoon bundles
- Individual add-on list: show "Coming Soon" badge, hide price for comingSoon items

## Verification
- TypeScript compilation: No errors in any modified files (marketing site + dashboard)
- `curl` server-side HTML: 5x "Coming Soon" present, enforcement prices removed from add-on cards
- `curl` confirms "Everything Unlimited", "Exclusive Capabilities", "Contact for Pricing" present
- Dev server restarted on port 3003 with fresh .next cache
