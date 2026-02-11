# TEAM_144 — Pricing & Homepage: Remove Rev Splits and Add-Ons

## Status: COMPLETE

## Task
Remove all revenue split percentages (60/40, 80/20) from pricing page, homepage, and feature comparison table. Remove add-on sections from pricing page and homepage (save for sales upsell). Replace with vague language about licensing revenue sharing.

## Files Modified
- `packages/pricing-config/src/coalition.ts` — Remove specific split percentages
- `packages/pricing-config/src/tiers.ts` — Remove 60/40 and 80/20 from foundingCoalition
- `apps/marketing-site/src/lib/pricing-config/coalition.ts` — Same (auto-generated copy)
- `apps/marketing-site/src/lib/pricing-config/tiers.ts` — Same (auto-generated copy)
- `apps/marketing-site/src/app/pricing/page.tsx` — Remove Two-Track section, add-ons, bundles, infra/ops sections, rev splits from enterprise
- `apps/marketing-site/src/app/page.tsx` — Replace 60/40 stat on homepage
- `apps/marketing-site/src/components/pricing/pricing-table.tsx` — Remove rev share box, remove add-ons column
- `apps/marketing-site/src/components/pricing/FeatureComparisonTable.tsx` — Remove rev share rows
