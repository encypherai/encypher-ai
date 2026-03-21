# UX/UI Audit -- Encypher Dashboard (Mobile, iPhone Pro)
**Date:** 2026-03-21 | **Version:** v1 (pre-fix baseline) | **Overall Score:** 6.5 / 10

## Context

Encypher's publisher dashboard viewed on iPhone 15 Pro (393px). The primary audience is publishers and enterprise compliance teams. On mobile, the dashboard must provide quick status checks, key metric visibility, and actionable next steps without requiring a laptop. This audit evaluates the production mobile experience before the 32 responsive fixes implemented in the same session.

## Score Summary

| Group | Category | Score | Grade |
|---|---|---|---|
| Visual | Color Palette | 7.5 | B |
| Visual | Typography | 6.5 | C |
| Visual | Iconography | 6.5 | C |
| Visual | Spacing & Layout | 5.5 | C |
| IA | Content Hierarchy | 6.0 | C |
| IA | Navigation Structure | 7.0 | B |
| IA | Onboarding UX | 7.5 | B |
| Functional | Data Presentation | 5.0 | C |
| Functional | Actionability | 7.0 | B |
| Functional | Empty/Zero States | 7.0 | B |
| Brand | Brand Identity | 7.5 | B |
| Brand | Professional Polish | 5.5 | C |
| **Overall** | | **6.5** | **C** |

Grade: A (9-10), B (7-8.9), C (5-6.9), D (3-4.9), F (0-2.9)

## Detailed Assessment

### Visual Design

**Color Palette (7.5 / B):** The dark navy-to-teal gradient hero is distinctive and professional. Delft blue (#1B2F50) as the primary brand color communicates trust and authority, while the blue-ncs teal accent provides clear priority signaling on CTAs and badges. White text on the dark hero gradient delivers good contrast. The two-tone button treatment (solid white primary vs. white/10 outlined secondary) creates clear visual hierarchy. Minor issue: the header bar and hero gradient share similar dark tones, losing separation in dark mode.

**Typography (6.5 / C):** The greeting at text-3xl (30px) is immediately readable. Three distinct levels of hierarchy are visible: greeting (30px bold), subtitle (18px medium), description (14px regular). The "PUBLISHER QUICK START" eyebrow uses uppercase tracking-wider to signal a section label, which is a mature pattern. However, text-3xl is too generous for a 297px content width (after 48px total padding) -- "Good afternoon, Erik Svilich" fills the entire width and would overflow for longer names. The type scale is desktop-proportioned, not mobile-optimized.

**Iconography (6.5 / C):** The shield/checkmark logo renders cleanly at mobile size. The "+" icon on "Open Integrations" and grid icon on "Publisher Docs" are functional and correctly sized for touch targets. The C2PA Compliant badge icon is identifiable at small size. However, the visible iconography is entirely generic -- no domain-specific provenance or signing icons appear above the fold. The icons do not yet carry semantic weight beyond standard UI affordances.

**Spacing & Layout (5.5 / C):** The hero card has generous p-8 (32px) internal padding, which combined with the px-4 (16px) container padding, leaves only ~297px for text content. The hero card consumes roughly 45% of the 852px viewport before any actionable content appears. The "PUBLISHER QUICK START" section starts below the fold. The rounded-2xl corners and gradient treatment create clean visual separation between hero and content sections. However, the vertical space allocation is desktop-proportioned -- the hero banner's padding and description text are designed for a wide layout and waste precious mobile viewport real estate.

### Information Architecture

**Content Hierarchy (6.0 / C):** The greeting dominates the viewport -- warm but not actionable. A publisher opening their dashboard on their phone wants to see "are my articles signed?" and "any new verifications?" -- not a welcome message taking half the screen. The two hero CTAs (Open Integrations, Publisher Docs) are important for onboarding but repeat what the Quick Start section below provides with more context. The actual Quick Start steps with contextual guidance are below the fold. For mobile, the hierarchy should invert: status/metrics first, then actions, then welcome context.

**Navigation Structure (7.0 / B):** The mobile header is clean: hamburger menu (left), logo (center-left), theme toggle + user avatar (right). The MobileNav drawer slides out at w-72 (288px) with a semi-transparent backdrop, leaving a 105px tap-to-close zone. Navigation groups (Publish, Insights, Enterprise, Account) map to the user's mental model. Active states are clearly indicated. The breadcrumb system provides orientation on interior pages. Solid mobile nav implementation -- the score reflects that it follows established patterns without innovation.

**Onboarding UX (7.5 / B):** The "PUBLISHER QUICK START" section adapts to the user's selected workflow and platform (WordPress, Ghost, custom CMS). It provides a three-step guided path (Connect CMS, Sign first article, Verify proof) with completion checkmarks. The contextual messaging ("Get your publishing stack publishing with proof of origin") is specific and actionable, not generic. The "Verify signed content" CTA is prominent and full-width -- good mobile button pattern. Score docked because on mobile, this excellent onboarding content is buried below a hero that largely restates the same message less usefully.

### Functional Design

**Data Presentation (5.0 / C):** The most significant mobile gap. The screenshot shows zero data above the fold -- no stat cards, no sparklines, no metrics. The 2x4 stat card grid (API Calls, Documents Signed, Verifications, Success Rate) with sparklines and trend badges is one of the dashboard's strongest features, but on mobile it sits below both the hero AND the quick start section. A publisher checking their phone wants to see "42 articles signed, 12 external verifications, 99.8% success rate" immediately -- not after scrolling past welcome copy. The stat cards themselves use text-3xl numbers in grid-cols-2, which at ~172px per card is technically legible but cramped.

**Actionability (7.0 / B):** Four CTAs visible in the screenshot: "Open Integrations" (hero primary), "Publisher Docs" (hero secondary), "Verify signed content" (quick start primary), "View content performance" (quick start secondary). All have appropriate touch target sizing (min 44px height). The full-width gradient "Verify signed content" button is the strongest mobile CTA pattern. Issue: the four CTAs compete without clear prioritization. On mobile, one primary action per viewport section is the gold standard.

**Empty/Zero States (7.0 / B):** The quick start section effectively serves as a zero-state for new users -- it appears when onboarding steps remain incomplete. The stat cards have dedicated zero states (from code review): "Sign your first document" with a CTA to the playground, and "Verify your first signed document" with contextual guidance. These zero states include icons, descriptions, and direct action links. Good pattern. Score docked slightly because the zero-state stat cards still use grid-cols-2 layout, meaning the CTA text ("Try Signing") in a ~172px card feels cramped.

### Brand & Differentiation

**Brand Identity (7.5 / B):** The Encypher brand reads clearly on mobile. The dark navy/teal palette is distinctive and doesn't look like a generic SaaS template. The shield/checkmark logo works at small sizes. The "C2PA Compliant" badge reinforces institutional credibility. The gradient hero with decorative blur circles (visible in the code as bg-white rounded-full blur-3xl) adds visual texture without clutter. The enterprise-serious tone is appropriate for a product shown to Fortune 500 GCs. Score reflects strong brand presence but not yet iconic -- the interface is recognizable with the logo but not necessarily without it.

**Professional Polish (5.5 / C):** The hero gradient renders cleanly with proper rounded-2xl corners. Button styling is consistent. The dark mode implementation works. However, the mobile experience reveals clear "desktop design viewed on mobile" patterns: text-3xl in 297px containers, p-8 padding consuming precious mobile viewport, stat card text-3xl numbers in 172px grid cells, tables that compress to illegible column widths, forced multi-column grids (grid-cols-3 at 393px = 113px per cell). The fix list of 32 responsive issues illustrates the gap. Settings page sidebar stacking above content, governance form inputs at 65px wide, and tables clipping with overflow-hidden are the most visible polish failures.

## Prioritized Recommendations

| # | Recommendation | Impact | Effort | Priority |
|---|---|---|---|---|
| 1 | **Reorder mobile homepage: metrics first, hero second.** On mobile, show the 4 stat cards above the hero welcome section. Publishers checking their phone want status, not a greeting. Use `order-first lg:order-none` on the stat grid and `order-last lg:order-none` on the hero. The welcome message becomes supporting context below the data, not a wall blocking it. | High | S | P0 |
| 2 | **Compress the hero for mobile.** Reduce hero padding from p-8 to p-5 on mobile (`p-5 sm:p-8`). Change greeting from text-3xl to text-xl on mobile. Hide the C2PA badge description text on mobile (`hidden sm:inline`). Collapse to a single primary CTA on mobile with the secondary in a text link below. This recovers ~120px of vertical space. | High | S | P0 |
| 3 | **Add a mobile-optimized "at a glance" strip.** Above the hero, render a compact 4-metric strip (sign count, verify count, success rate, activity indicator) in a single horizontal scrollable row. Think GitHub mobile's contribution streak -- immediate status without scrolling. Show full stat cards further down. | High | M | P1 |
| 4 | **Convert all data tables to card-list view on mobile.** Instead of horizontally scrolling 8-column tables that require precise finger swiping, show each row as a stacked card on mobile. The card shows the 2-3 most important fields prominently, with secondary fields in a compact grid below. Use `hidden md:table-cell` for the table view and a parallel card view for mobile. | Medium | L | P1 |
| 5 | **Add pull-to-refresh on mobile.** The activity feed polls every 30s, but mobile users expect pull-to-refresh as a gesture. Implement via a lightweight touch handler on the main content area that triggers refetch on all visible queries. This makes the mobile experience feel native rather than web-app-ish. | Low | M | P2 |

## Notes

This audit scores the pre-fix production state. The 32 responsive fixes implemented in this session (TEAM_268) address most of the P2/P3 polish issues: forced grids now collapse responsively, tables have min-widths so horizontal scroll triggers properly, text overflow is handled, and toolbars wrap on mobile. Recommendations 1-3 above go beyond responsive fixes into mobile-specific UX optimization -- restructuring what appears above the fold for the mobile use case rather than just making the desktop layout render without breaking.
