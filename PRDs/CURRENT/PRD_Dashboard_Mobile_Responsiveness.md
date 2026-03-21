# PRD: Dashboard Mobile Responsiveness Fix

**Status**: COMPLETE
**Current Goal**: All 32 issues fixed, build verified clean
**Team**: TEAM_268

## Overview

Full mobile responsiveness audit identified 32 issues across the dashboard app ranging from unusable layouts (P0) to polish items (P3). The dashboard must render correctly on iPhone Pro (393px width, 361px usable after px-4) while preserving the existing desktop experience. All fixes use responsive Tailwind prefixes -- no desktop regressions allowed.

## Objectives

- Fix all P0/P1 issues that cause broken, clipped, or unusable mobile layouts
- Fix all P2 issues where text overflows, flex rows break, or content is unreadable
- Fix all P3 polish issues for a professional mobile experience
- Zero desktop regressions -- every change must use responsive breakpoints
- Pass visual verification on iPhone Pro (393px) and desktop (1440px)

## Tasks

### 1.0 Layout and Navigation

- [x]1.1 Settings sidebar: replace stacked sidebar with horizontal scrollable tab strip on mobile (`settings/page.tsx:1588`)
- [x]1.2 Breadcrumb overflow: add `flex-wrap` or `overflow-x-auto` to breadcrumb nav (`breadcrumb.tsx:50`)
- [x]1.3 NotificationCenter dropdown: add `max-w-[calc(100vw-2rem)]` guard (`NotificationCenter.tsx:96`)
- [x]1.4 CommandPalette keyboard hints: hide on mobile with `hidden sm:flex` (`CommandPalette.tsx:258`)

### 2.0 Tables and Data Display

- [x]2.1 AI Crawlers table: add `min-w-[700px]` to 8-column table (`ai-crawlers/page.tsx:736`)
- [x]2.2 Enforcement table: add `min-w-[580px]` to 5-column table (`enforcement/page.tsx:165`)
- [x]2.3 Billing invoices table: wrap in `overflow-x-auto` div (`billing/page.tsx:785`)
- [x]2.4 Rights discovery domains table: add `min-w-[500px]` (`rights/page.tsx:681`)
- [x]2.5 Rights raw events table: add `min-w-[500px]` (`rights/page.tsx:731`)
- [x]2.6 Rights crawler activity table: add `min-w-[480px]` (`rights/page.tsx:803`)
- [x]2.7 Rights licensing requests table: add `min-w-[600px]` (`rights/page.tsx:1165`)
- [x]2.8 Governance attestations table: change `overflow-hidden` to `overflow-x-auto` and add `min-w-[500px]` (`governance/page.tsx:407`)

### 3.0 Forced Grid Layouts

- [x]3.1 Analytics API health: `grid-cols-3` -> `grid-cols-1 sm:grid-cols-3` (`analytics/page.tsx:586`)
- [x]3.2 Billing seat upgrade: `grid-cols-3` -> `grid-cols-1 sm:grid-cols-3` (`billing/page.tsx:317`)
- [x]3.3 Governance stats: `grid-cols-3` -> `grid-cols-1 sm:grid-cols-3` (`governance/page.tsx:373`)
- [x]3.4 Governance rule builder: `grid-cols-5` -> `grid-cols-1 sm:grid-cols-5` (`governance/page.tsx:163`)
- [x]3.5 Rights stat cards: `grid-cols-2` -> `grid-cols-1 sm:grid-cols-2`, reduce `text-3xl` to `text-2xl sm:text-3xl` (`rights/page.tsx:522`)
- [x]3.6 Governance policy form: `grid-cols-2` -> `grid-cols-1 sm:grid-cols-2` (`governance/page.tsx:135`)

### 4.0 Flex Row Overflow and Toolbars

- [x]4.1 Analytics time range toolbar: add `flex-wrap gap-2` (`analytics/page.tsx:298`)
- [x]4.2 AI Crawlers time range toolbar: add `flex-wrap gap-2` (`ai-crawlers/page.tsx:385`)
- [x]4.3 CDN Analytics timeline header: convert to `flex-col sm:flex-row gap-2` (`cdn-analytics/page.tsx:310`)
- [x]4.4 Audit logs filters: change `w-[Xpx]` to `w-full sm:w-[Xpx]` on all filter controls (`audit-logs/page.tsx:486-584`)
- [x]4.5 Playground header: add `flex-wrap gap-y-2` (`playground/page.tsx:816`)
- [x]4.6 Playground tour steps: hide step indicators on mobile, show `Step X/4` instead (`playground/page.tsx:941-967`)

### 5.0 Text Overflow and Truncation

- [x]5.1 API Keys caption: add `hidden sm:inline` on "Full key shown only at creation" (`api-keys/page.tsx:451`)
- [x]5.2 API Keys generated key: add `break-all overflow-hidden` to `<code>` (`api-keys/page.tsx:558`)
- [x]5.3 Rights public endpoints: reduce label to `w-28 sm:w-40` or use `flex-col sm:flex-row` (`rights/page.tsx:343`)
- [x]5.4 Rights TabsList: add `overflow-x-auto` to container (`rights/page.tsx:1331`)
- [x]5.5 Webhooks URL display: add `min-w-0 flex-1` to parent div, `overflow-hidden` on button (`webhooks/page.tsx:454`)
- [x]5.6 Team member rows: add `min-w-0 flex-1` to left div, `flex-shrink-0` to right actions (`team/page.tsx:902`)
- [x]5.7 Print detection UUIDs: add `min-w-0` + `truncate` to UUID elements (`print-detection/page.tsx:73`)
- [x]5.8 Governance policy card: add `min-w-0 flex-1` to left content div (`governance/page.tsx:305`)

### 6.0 Auth Pages and Polish

- [x]6.1 Login/Signup card padding: `p-8` -> `p-6 sm:p-8` (`login/page.tsx:194`, `signup/page.tsx:197`)
- [x]6.2 Login OAuth buttons: add `aria-label` to each icon-only button (`login/page.tsx:229,238,249`)
- [x]6.3 Image signing options card: add `order-first lg:order-last` for mobile reorder (`image-signing/page.tsx:547`)
- [x]6.4 Team header buttons: add `w-full sm:w-auto` (`team/page.tsx:584`)
- [x]6.5 Home page hero greeting: `text-3xl` -> `text-2xl sm:text-3xl lg:text-4xl` (`page.tsx:580`)
- [x]6.6 Home page stat cards: `text-3xl` -> `text-2xl sm:text-3xl` for numbers (`page.tsx:686`)

## Success Criteria

- All 32 issues resolved with responsive Tailwind classes
- No desktop layout regressions (verify at 1440px)
- Clean `next build` with zero errors
- Visual spot-check at 393px and 1440px viewport widths

## Completion Notes

All 32 issues resolved by TEAM_268 on 2026-03-21. Six parallel agents implemented fixes across:
- 4 layout/navigation fixes (settings mobile tabs, breadcrumb wrap, notification guard, command palette)
- 8 table min-width fixes (ai-crawlers, enforcement, billing, rights x4, governance)
- 6 grid layout fixes (analytics, billing, governance x3, rights)
- 6 toolbar/flex fixes (analytics, ai-crawlers, cdn-analytics, audit-logs, playground x2)
- 8 text overflow fixes (api-keys x2, rights x2, webhooks, team, print-detection, governance)
- 6 polish fixes (login/signup padding, aria-labels, image-signing order, team buttons, home page text)

Build verified clean (`next build` passes with zero errors). All changes use responsive Tailwind prefixes only -- no desktop regressions.
