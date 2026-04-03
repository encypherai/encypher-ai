# PRD: Publisher Value Proof Dashboard

**Status:** Active
**Current Goal:** Bridge the 12-24 month gap between publisher signup and coalition licensing revenue by surfacing interim business-outcome metrics that keep publishers engaged and give champions ammunition for internal advocacy.

## Overview

Encypher's free signing tier creates a "foot in the door" for publishers, but the primary economic value (coalition licensing revenue from AI companies) may take 12-24 months to materialize at scale. The current dashboard surfaces product metrics (API calls, documents signed, response time) which answer "is the API working?" but not "is this worth staying for?"

This PRD defines the product changes needed to surface business outcomes, make interim value visible, and give champions the proof artifacts they need to maintain organizational commitment through the coalition-building phase.

## Objectives

- Surface the 3 business-outcome metrics that matter to publisher champions and buyers
- Make content distribution/spread analytics a primary value driver (independent of licensing timeline)
- Give champions a shareable proof artifact for internal advocacy
- Reframe the analytics page around outcomes, not product health
- Clarify what the AI Crawlers dashboard currently shows vs. what it aspires to show

## Tasks

### 1.0 Value Proof Card on Dashboard Home

- [x] 1.1 Design a "Your Content Protection" summary card for `apps/dashboard/src/app/page.tsx` -- ✅ tsc
  - 1.1.1 Metric: Total content protected (documents signed)
  - 1.1.2 Metric: External verifications received (third-party proofs of adoption)
  - 1.1.3 Metric: Formal Notice progress % bar
- [x] 1.2 "View Content Performance" CTA links to analytics page -- ✅ tsc
- [x] 1.3 Progress bar shows path to Formal Notice threshold -- ✅ tsc
- [x] 1.4 Position the card above the fold, above the OnboardingChecklist -- ✅ tsc

### 2.0 Analytics Page: Value Accumulation Timeline

The analytics page primary experience should tell a progressive business story, not show API health metrics. The goal is that a publisher logging in during the 12-24 month pre-revenue period sees visible forward progress at every stage.

The primary view is a funnel/timeline that maps directly to the enforcement journey:

```
SIGNED: X articles  (your protected corpus -- content you can enforce on)
    |
VERIFIED: X external provenance checks this month
    [Breakdown: EntityA (891), EntityB (412), Unknown (N)]
    |
SPREAD: Your content detected on X external domains
    [New this month: X | Top domain: example.com]
    |
NOTICE READY: You qualify for Formal Notice to X entities  [Take Action ->]
    |
LICENSING: Coalition negotiation active with X entities  [View Status ->]
    |
EARNINGS: $X earned  |  $X estimated pipeline
```

Each stage should feel like an achievement, not a waiting room. The "Verified" and "Spread" lines show that the system is working even before Earnings is non-zero.

- [x] 2.1 Redesign `apps/dashboard/src/app/analytics/page.tsx` primary section as the 6-stage funnel -- ✅ tsc
  - 2.1.1 SIGNED: `total_documents_signed` -- active
  - 2.1.2 VERIFIED: `total_verifications` -- active with provenance check framing
  - 2.1.3 SPREAD: placeholder "tracking coming soon" -- pending Task 3.0
  - 2.1.4 NOTICE READY: computed from 500-verification threshold -- CTA when qualifying
  - 2.1.5 EARNINGS: pulls coalition earnings via `apiClient.getCoalitionEarnings`
- [x] 2.2 API Health metrics moved to collapsible "API Health Metrics" section -- ✅ tsc
- [x] 2.3 Renamed page to "Content Performance" in header, nav (DashboardLayout.tsx) -- ✅ tsc
- [x] 2.4 Tests: tsc clean, 1234 pytest passing

### 3.0 Content Spread Analytics

Content spread = signed content detected on domains other than the publisher's own. This is Tier 1 detection and has standalone value now, independent of the licensing timeline.

- [x] 3.1 Audited: `ContentDetectionEvent` model has `detected_on_domain` field (already exists) -- no schema change needed -- ✅ verified
- [x] 3.2 Added `GET /api/v1/rights/analytics/content-spread` endpoint to `enterprise_api/app/routers/rights.py` -- ✅ pytest (1234 passing)
  - 3.2.1 Returns: unique_external_domains, total_external_detections, domains list, documents list
  - 3.2.2 Gated: Enterprise tier or `attribution_analytics` add-on
- [ ] 3.3 Add "Content Spread" panel to analytics page (SPREAD stage in funnel shows "coming soon" placeholder until data available)
- [x] 3.4 Tests: 1234 pytest passing, tsc clean, README + openapi.public.json updated

### 4.0 AI Crawlers Dashboard - Honest Capability Framing

The current AI Crawlers dashboard shows provenance-checking activity (RSL lookups, Chrome extension sightings, API verifications). It does NOT show raw crawler traffic to a publisher's site. This distinction must be clear in the UI to avoid overpromising.

- [x] 4.1 Updated `apps/dashboard/src/app/ai-crawlers/page.tsx` header to "Provenance Activity" -- ✅ tsc
- [x] 4.2 Added amber callout explaining what data is/isn't shown (honest capability framing) -- ✅ tsc
- [x] 4.3 Added "Join Waitlist" CTA (mailto: partnerships@encypher.com) for Cloudflare integration -- ✅ tsc
- [x] 4.4 Nav item renamed "Provenance Activity" in DashboardLayout.tsx -- ✅ tsc

### 5.0 Formal Notice Progression System

The Formal Notice Package ($499) should not be a standalone purchase. It should be the destination of a visible progression arc that keeps publishers engaged through the 12-24 month pre-revenue period.

- [ ] 5.1 Design a "Your Journey" status component (home page or dedicated progression page)
  - Stage 1: Sign -- "Sign your first X articles" (progress bar)
  - Stage 2: Accumulate -- "Reach 500 external verifications" (leading indicator)
  - Stage 3: Document -- "Evidence Package building automatically" (every verification logged)
  - Stage 4: Notice Ready -- "You qualify to serve Formal Notice to X entities" [Take Action ->]
  - Stage 5: Negotiating -- "Notice served. Coalition negotiation active." [View Status ->]
  - Stage 6: Earnings -- "$X earned | $Y estimated pipeline"
- [x] 5.2 Backend: `GET /api/v1/onboarding/progression-status` endpoint added to `enterprise_api/app/routers/onboarding.py` -- ✅ pytest
- [ ] 5.3 Stage-specific email/notification triggers (post-MVP)
- [x] 5.4 Stage 4 CTA links to `/rights` in analytics page funnel -- ✅ tsc
- [x] 5.5 Tests: 1234 pytest passing, tsc clean, README + openapi.public.json updated

### 6.0 Shareable Provenance Report

Champions need to show their technology investment to editorial leadership and CFOs. A one-page shareable summary converts dashboard data into advocacy ammunition.

- [ ] 5.1 Add "Generate Report" button to analytics page
- [ ] 5.2 API endpoint: `GET /org/analytics/provenance-report` returns structured report data
  - Period: last 30 days or custom range
  - Includes: content protected, external verifications, content spread (if available), coalition status
- [ ] 5.3 Frontend: render as print-friendly HTML or downloadable PDF
  - Header: "[Org Name] Content Provenance Report -- [Period]"
  - 3-4 headline metrics (outcome-focused, not product-health)
  - Coalition status and next milestone
  - "Powered by Encypher / C2PA Standard"
- [ ] 5.4 "Share via link" option (generates time-limited public URL to the report view)
- [ ] 5.5 Tests: pytest for report endpoint, tsc for report component

### 7.0 Dashboard Navigation Reframing

Current nav is organized by feature. Reorder to reflect outcome priority.

- [x] 6.1 Renamed "Analytics" -> "Content Performance" and "AI Crawlers" -> "Provenance Activity" in `DashboardLayout.tsx` -- ✅ tsc
- [x] 6.2 "Content Performance" label updated in home page Quick Links too -- ✅ tsc
- [x] 6.3 Page headers updated to match new nav names -- ✅ tsc
- [ ] 6.4 Puppeteer nav render verification (manual)

### 8.0 Coalition Membership Counter (Marketing Site)

A public coalition counter on the marketing site creates FOMO for prospective publishers and signals scale to AI companies watching from a distance. This is a marketing site change, not a dashboard change, but it belongs in this PRD because the data it displays comes from the same coalition infrastructure.

- [ ] 8.1 Add a coalition stats section to `apps/marketing-site/src/app/` home page or publisher landing page
  - Show: number of publishers in coalition, total estimated annual content revenue represented
  - Individual member names can remain confidential if needed -- aggregate numbers are sufficient
  - Updates dynamically (or on a daily refresh) as publishers join
- [x] 8.2 Added `GET /api/v1/coalition/public/stats` (no auth) to `enterprise_api/app/routers/coalition.py` -- ✅ pytest
  - Returns: coalition_members, total_signed_documents, as_of
  - Also exposed via `apiClient.getPublicCoalitionStats()` in api.ts
- [ ] 8.3 Marketing site coalition counter component (TODO: marketing site changes)
- [x] 8.3 pytest and openapi artifact updated -- ✅ 1234 pytest passing

## Success Criteria

- A publisher champion can generate a 1-page "Content Provenance Report" and share it with their leadership without leaving the dashboard
- The analytics page primary section shows the 6-stage Value Accumulation Timeline funnel -- a publisher sees forward progress even at $0 earnings
- The home page card answers "what has Encypher done for me this month?" with at least one business-outcome metric
- The Formal Notice Progression system surfaces "Notice Ready" status and a clear CTA when a publisher qualifies
- AI Crawlers page copy accurately describes what is and isn't shown (no overpromising)
- Content spread data (external domain detections) is surfaced as a standalone value metric
- The coalition counter is live on the marketing site with aggregate member/content-value data

## Completion Notes

TBD
