# PRD: WordPress Plugin Archive Pricing Alignment

**Status:** 🟡 In Progress
**Current Goal:** Align the WordPress plugin with the Feb 2026 freemium pricing model and close the archive backfill UX gaps
**Team:** TEAM_237

---

## Overview

This PRD addresses the gaps identified in the WordPress provenance plugin audit. The plugin already supports post signing, frontend verification, and archive backfill mechanics, but it does not yet express the current product model clearly or correctly.

The current marketing and dashboard pricing model defines:

- Free signing infrastructure with **1,000 documents/month** included
- **$0.02/sign request** overage for ongoing free-tier publishing workflows after the monthly cap
- **Bulk Archive Backfill** as a **one-time $0.01/document** operations add-on
- Enterprise as including **unlimited signing** and **all add-ons**, including archive backfill

The plugin still contains older bulk-sign assumptions and lacks a clear archive purchase handoff. This PRD brings the plugin UX, tier behavior, and billing handoff into alignment with the current model.

---

## Objectives

- Align plugin archive/backfill messaging with the current pricing model
- Remove stale free-tier bulk limits that conflict with the 1,000/month free plan
- Let users discover and estimate the cost of signing their entire archive
- Provide a one-click handoff from the plugin to billing for archive backfill purchase
- Ensure Enterprise users are never treated like free users in the bulk UX
- Make badge-position settings truthful by matching frontend behavior to the configured option
- Preserve current signing and verification behavior

---

## User Problems

### 1. Free-tier messaging is inconsistent
The plugin references old bulk limits while the marketing site says free includes 1,000 documents/month.

### 2. Archive backfill is discoverable but not monetized cleanly
Users can run bulk signing, but they are not shown:

- archive size
n- one-time estimated cost
- a dedicated archive purchase path
- what Enterprise includes automatically

### 3. Enterprise users can still hit free-tier client behavior
The current bulk page JavaScript infers tier from `body[data-tier]`, which is not rendered.

### 4. Badge position settings are misleading
The settings UI offers top/bottom/bottom-right options, but the frontend behavior is effectively bottom-of-content.

---

## Target Users

- WordPress site owners on the free plan
- Small publishers who want to protect an existing archive without a sales call
- Enterprise publishers who expect archive backfill to be included and frictionless
- Admin users who need clear usage, billing, and archive status visibility

---

## Success Criteria

- [ ] Free-tier plugin surfaces show **1,000 documents/month** as the included monthly volume
- [ ] Plugin bulk page shows a live **archive document count** and **estimated one-time price** at **$0.01/document**
- [ ] Plugin bulk page includes a **one-click billing handoff** for archive backfill
- [ ] Enterprise users see archive backfill as **included**
- [ ] Bulk-sign JavaScript uses explicit localized tier/config data rather than DOM assumptions
- [ ] Free-tier users are no longer capped at **10 docs per bulk operation** in plugin UI or server-side handler
- [ ] Badge position behavior matches the selected setting for `top`, `bottom`, and `bottom-right`
- [ ] Existing signing, verification, and archive execution flows continue to work locally

---

## Product Requirements

### 1. Bulk Archive Backfill UX

The bulk-sign page must:

- explain archive backfill in business language, not internal implementation language
- show the number of matching posts/pages in the selected archive scope
- compute and display a one-time archive estimate using **$0.01/document**
- show free-tier included monthly remaining usage for ongoing publishing workflows
- show Enterprise archive backfill as included
- provide a billing CTA that deep-links to the dashboard billing page with the add-on preselected
- allow the user to continue directly into bulk signing from the same page

### 2. Tier Behavior

The plugin must:

- use localized script config for `tier`, usage, and pricing constants
- remove the stale **10 docs** free-tier client and server limits
- keep monthly usage tracking intact
- show the free plan as **1,000/month included**, not a per-bulk-operation cap

### 3. Billing Handoff

Given the current product architecture, WordPress does not authenticate the user into the dashboard automatically. Therefore the plugin must provide the cleanest real handoff available today:

- deep-link to the dashboard billing page
- pass `addon=bulk-archive-backfill`
- pass `quantity=<estimated archive count>`
- pass `source=wordpress-plugin`

The dashboard billing page must:

- detect the archive-backfill deep link
- highlight the archive add-on
- display the passed quantity and estimated one-time total
- present a checkout action for the archive backfill add-on when the user is authenticated

### 4. Frontend Badge Positioning

The plugin frontend must:

- render the badge at the **top of post content** when configured to `top`
- render the badge at the **bottom of post content** when configured to `bottom`
- render the badge as a **floating bottom-right trust affordance** when configured to `bottom-right`

---

## Technical Requirements

### WordPress Plugin

Files expected to change:

- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/includes/class-encypher-provenance-bulk.php`
- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/assets/js/bulk-mark.js`
- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/assets/css/bulk-mark.css`
- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/includes/class-encypher-provenance-frontend.php`
- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/includes/class-encypher-provenance-admin.php`

### Dashboard

Files expected to change:

- `apps/dashboard/src/app/billing/page.tsx`
- `apps/dashboard/src/lib/api.ts`

### Billing Service

Files expected to change:

- `services/billing-service/app/api/v1/endpoints.py`
- `services/billing-service/app/models/schemas.py`
- `services/billing-service/app/services/stripe_service.py`

---

## Implementation Tasks

### 1.0 WordPress Plugin Pricing Alignment

- [ ] 1.1 Remove the stale free-tier `10 documents per bulk operation` UI copy
- [ ] 1.2 Remove the stale free-tier `10 documents` bulk server-side restriction
- [ ] 1.3 Localize tier, usage, archive price, and billing URL into the bulk JS
- [ ] 1.4 Show live archive estimate and billing CTA on the bulk page
- [ ] 1.5 Update free-tier helper copy to reference `1,000/month` and archive backfill pricing

### 2.0 Badge Position Truthfulness

- [ ] 2.1 Implement `top` badge placement
- [ ] 2.2 Implement `bottom` badge placement
- [ ] 2.3 Implement `bottom-right` floating badge placement
- [ ] 2.4 Preserve modal verification behavior for all placements

### 3.0 Dashboard Billing Deep Link

- [ ] 3.1 Read `addon`, `quantity`, and `source` from billing page search params
- [ ] 3.2 Highlight the `bulk-archive-backfill` add-on when deep-linked
- [ ] 3.3 Show estimated total cost and requested archive quantity
- [ ] 3.4 Provide an authenticated checkout action for archive backfill

### 4.0 Billing Service Add-On Checkout

- [ ] 4.1 Add a one-time archive add-on checkout request schema
- [ ] 4.2 Add an authenticated add-on checkout endpoint
- [ ] 4.3 Add Stripe helper for one-time checkout sessions
- [ ] 4.4 Support `bulk-archive-backfill` at **$0.01/document** with variable quantity

### 5.0 Local Validation

- [ ] 5.1 Validate bulk page estimate updates live on the Docker WordPress site
- [ ] 5.2 Validate archive backfill execution still completes successfully
- [ ] 5.3 Validate frontend badge placement for `bottom-right` and `bottom`
- [ ] 5.4 Validate dashboard billing page deep link rendering locally where possible

---

## Acceptance Test Plan

### WordPress Plugin

1. Open `Encypher > Bulk Sign`
2. Change post-type and status filters
3. Confirm total archive count updates
4. Confirm estimated archive cost updates at `$0.01/document`
5. Confirm free-tier guidance references `1,000/month`
6. Confirm Enterprise guidance says archive backfill is included
7. Run a bulk sign job and confirm completion
8. Confirm content inventory reflects the updated signing state

### Frontend

1. Set badge position to `bottom`
2. Confirm badge appears after the post content
3. Set badge position to `bottom-right`
4. Confirm badge floats at the bottom-right of the viewport
5. Click badge in both positions
6. Confirm the verification modal still loads and displays data

### Dashboard Billing

1. Open `/billing?addon=bulk-archive-backfill&quantity=500&source=wordpress-plugin`
2. Confirm the billing page highlights the archive backfill add-on
3. Confirm the page shows `500` documents and `$5.00` estimate
4. Confirm checkout CTA is visible for non-enterprise users

---

## Risks

- WordPress plugin cannot itself authenticate a user into the dashboard billing experience
- Stripe configuration for the archive add-on may not be present in all environments
- One-time add-on checkout introduces a new billing path that may need additional webhook/accounting follow-up
- Frontend badge placement changes must avoid duplicate badge rendering in certain themes

---

## Non-Goals

- Native in-plugin Stripe checkout inside WordPress admin
- Archive-job entitlement tracking inside WordPress options
- Reworking the full dashboard add-ons IA beyond the archive-backfill flow
- Replacing existing signing or verification APIs

---

## References

- `apps/marketing-site/src/lib/pricing-config/tiers.ts`
- `apps/dashboard/src/app/billing/page.tsx`
- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/includes/class-encypher-provenance-bulk.php`
- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/assets/js/bulk-mark.js`
- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/includes/class-encypher-provenance-frontend.php`
