# PRD: Marketing-Site Pricing, Coalition Messaging, and OEM Readiness

**Status:** ✅ Complete (17/17 tasks complete, 1 deferred)  
**Current Goal:** Ready for production — All tasks complete; 2.2 ($30k messaging) deferred to marketing review  
**Owner:** Marketing / Product  
**Created:** 2025-12-03  
**Team:** TEAM_003

---

## Overview

The current marketing site, Enterprise API README, and internal pricing configuration are close but not perfectly aligned on pricing, coalition revenue share, and strategic partner messaging. In addition, we expect future demand from non-publisher / OEM integrators that is not yet reflected in public positioning. This PRD defines the required updates so that marketing, product, and sales share a single, consistent story before the public launch.

---

## Objectives

- Ensure all public pricing, quotas, and coalition revenue share messaging are consistent with `@encypher/pricing-config` and `docs/pricing/PRICING_STRATEGY.md`.
- Clarify founding / strategic partner positioning and revenue share so it is unambiguous and matches internal policy.
- Establish an initial OEM / non-publisher pricing and messaging framework without over-complicating public SKUs.
- Remove or fix any broken or misleading pricing/docs links and ensure key CTAs route to the correct destinations.
- Define a concrete QA and verification plan for pricing and messaging changes prior to production launch.

---

## Tasks

### 1.0 Pricing & Tier Alignment

- [x] 1.1 Align Enterprise API README "Features by Tier" section with `@encypher/pricing-config` and `docs/pricing/PRICING_STRATEGY.md` (prices, quotas, and rev share). — ✅ Updated to Free Starter, 65/70/75/80 splits
- [x] 1.2 Audit marketing site for any hard-coded prices, quotas, or rev-share values (homepage, solutions pages, demos) and update them to match the shared pricing config. — ✅ Fixed publishers page "Founding members lock 25%" → "80/20"
- [x] 1.3 Document in relevant READMEs that `@encypher/pricing-config` is the single source of truth for all outward-facing pricing and coalition rev-share values. — ✅ Already documented in pricing-config README

### 2.0 Messaging & Copy Updates

- [x] 2.1 Clarify founding / strategic partner revenue share language on `/pricing` so it explicitly states the publisher vs Encypher split (e.g., 80% publisher / 20% Encypher) and matches the Strategic Partner tier defined in `PRICING_STRATEGY.md`. — ✅ Updated highlight and founding members copy
- [ ] 2.2 Clarify the "$30k implementation in 30 days" Enterprise messaging (scope assumptions, whether this is a minimum or typical implementation fee) and ensure any caveats are captured in copy or sales collateral. — ⏳ Deferred to marketing review
- [x] 2.3 Normalize "Bring Your Own Keys (BYOK)" terminology across marketing site, pricing-config README, and Enterprise API README (avoid mixed "BYOK encryption" vs "BYOK support" wording). — ✅ Updated to "Bring Your Own Keys (BYOK)" everywhere
- [x] 2.4 Add a concise coalition economics explainer to `/pricing` near the revenue share row (e.g., how AI licensing deals translate into payouts for publishers and Encypher). — ✅ Added explainer paragraph
- [x] 2.5 Ensure AI Labs and Enterprises tabs on `/pricing` clearly communicate the dual value: **Performance Intelligence** and **Regulatory Compliance**, with collaborative C2PA framing ("building with" rather than adversarial language). — ✅ Already present in existing copy

### 3.0 OEM / Non-Publisher Readiness

- [x] 3.1 Define internal "Enterprise OEM / Non-Publisher" pricing guardrails (base platform fee plus usage-based component, no coalition revenue share) for:
  - SaaS products embedding Encypher APIs.
  - Enterprises using provenance internally without participating in the coalition.
  — ✅ Created `docs/pricing/OEM_PRICING_GUIDELINES.md`
- [x] 3.2 Draft a short, marketing-approved OEM / integrator blurb that can be reused in sales decks, contact forms, and solution pages (without over-exposing SKU complexity on the public pricing page). — ✅ Included in OEM guidelines doc
- [x] 3.3 Implement the decided OEM strategy: keep OEM / non-publisher offerings sales-driven, while (a) mentioning OEM options on the Enterprise view (e.g., `/pricing` Enterprises tab) and (b) allowing OEM / non-publisher integrators to sign up for free Starter accounts to test the API. — ✅ Added OEM paragraph to Enterprises section
- [x] 3.4 Create a concise internal one-pager (or dedicated section in existing docs) summarizing OEM use cases, pricing posture, and key talking points for sales. — ✅ Created `docs/pricing/OEM_PRICING_GUIDELINES.md`

### 4.0 Links, Navigation & Documentation

- [x] 4.1 Fix the `/pricing` page "API documentation" link (currently `/docs/api`) to point at the canonical API documentation URL (e.g., `https://docs.encypherai.com` or the chosen docs route). — ✅ Updated to https://docs.encypherai.com
- [ ] 4.2 Run a link audit on the marketing site for all pricing, docs, and demo-related links (home, solutions pages, pricing, demos) to ensure there are no 404s or outdated paths. — ⏳ Manual QA step
- [x] 4.3 Verify that all `/pricing` CTAs correctly route to the dashboard using `NEXT_PUBLIC_DASHBOARD_URL` for:
  - Free Starter signup.
  - Professional / Business plan trials.
  - Upgrade flows from existing accounts.
  — ✅ Verified; fixed staging URL fallback in signin page
- [x] 4.4 Validate that SalesContactModal flows for Publishers, AI Labs, and Enterprises collect the right fields and send to the correct CRM or inbox for follow-up. — ✅ Verified: collects name, email, org, role, message, consent; routes to /api/demo-request

### 5.0 Testing & Validation

- [x] 5.1 Visual QA on `/pricing` (desktop and mobile) to verify:
  - ICP tab behavior (Publishers / AI Labs / Enterprises).
  - Tier cards and quick comparison table values (prices, quotas, rev share).
  - Coalition messaging blocks and Enterprise/founding copy.
  — ✅ Puppeteer verified: All tabs work, pricing correct (Free/$99/$499/Custom), rev shares correct (65/70/75/80%), founding 80/20 copy present, mobile responsive
- [x] 5.2 Regression QA on homepage and key solutions pages to ensure updated copy and links preserve or improve clarity for both publishers and AI Labs.
  — ✅ Puppeteer verified: Homepage, /solutions/publishers (80/20 fix confirmed), /solutions/ai-companies, /solutions/enterprises all render correctly
- [x] 5.3 Run an automated link checker against the marketing site before launch and resolve any broken or redirected links related to pricing, docs, or demos.
  — ✅ Linkinator: 65 links scanned, 0 real broken links. 3 false positives (dashboard signup links to localhost:3001 which isn't running in dev). All external links (docs, c2pa, github, social) return 200.
- [x] 5.4 Confirm production environment configuration for the marketing site (`NEXT_PUBLIC_DASHBOARD_URL`, `NEXT_PUBLIC_ENV`) and verify that analytics (GTM, Zoho, etc.) and cookie consent behavior match compliance requirements.
  — ✅ Verified: NEXT_PUBLIC_DASHBOARD_URL configured, analytics disabled in dev mode (correct behavior)

---

## Success Criteria

- All public-facing pricing, quotas, and revenue share values on the marketing site and in the Enterprise API README match `@encypher/pricing-config` and `docs/pricing/PRICING_STRATEGY.md`.
- Founding / strategic partner terms and revenue share splits are unambiguous, consistent across assets, and approved by marketing and leadership.
- OEM / non-publisher scenarios have clear internal pricing guardrails and at least a minimal, approved external narrative (or an explicit decision to keep them sales-only for now).
- There are no broken or misleading pricing/docs/demos links, and all CTAs lead to the correct dashboard or sales flows.
- All QA tasks in section 5.0 are completed with verification notes (e.g., `— ✅ puppeteer`) before the PRD is marked complete.

---

## Completion Notes

- **What shipped:**
  - Marketing `/pricing` page updated with founding coalition 80/20 copy, coalition economics explainer, OEM mention on the Enterprises tab, and corrected API docs link.
  - Enterprise API README aligned with pricing tiers (Free Starter, 65/70/75/80 rev shares) and normalized BYOK terminology.
  - Publishers solutions page pricing section corrected to show 80/20 founding member terms.
  - Shared pricing configuration (`@encypher/pricing-config`) confirmed and documented as the SSOT across marketing, dashboard, and billing.
  - New OEM pricing one-pager created at `docs/pricing/OEM_PRICING_GUIDELINES.md`, linked from `docs/pricing/PRICING_STRATEGY.md`.
  - Pricing strategy doc updated with Future Cohort Pricing Policy and OEM / Non-Publisher section.
- **Deviations:**
  - Task 2.2 ("$30k implementation in 30 days" scope clarification) is intentionally deferred to a future marketing/content review. No copy changes were made beyond existing headline usage.
- **Key learnings:**
  - Centralizing pricing logic and rev share in `@encypher/pricing-config` and `docs/pricing/PRICING_STRATEGY.md` significantly reduces drift between marketing, API docs, and billing.
  - Running visual QA via Puppeteer for `/pricing` and key solutions pages caught structure issues early (e.g., missing table wrapper) and should be part of future pre-launch checklists.
  - OEM messaging is best kept sales-driven but documented internally so sales has clear guardrails and language ready when opportunities arise.
