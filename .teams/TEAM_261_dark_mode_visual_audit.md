# TEAM_261 -- Dark Mode Visual Audit

## Status: COMPLETE

## Goal
Audit all new dashboard pages in dark mode at 1440x900, identifying styling issues.

## Pages Audited
- [x] /settings (Profile tab)
- [x] /settings Organization tab
- [x] /settings/organization
- [x] /image-signing
- [x] /print-detection
- [x] /api-keys (incl. create modal with IP allowlist)
- [x] /billing (incl. add-ons, Connect Payout)
- [x] /cdn-analytics
- [x] /webhooks
- [x] /team

---

## Findings by Severity

### P0 -- Critical: White Background Leak

**1. /webhooks -- Documentation footer section (line 552)**
- Class: `bg-slate-50 rounded-lg border border-slate-200`
- Missing: `dark:bg-slate-800 dark:border-slate-700` (or use `bg-muted border-border`)
- Impact: Bright white/near-white box at bottom of webhooks page in dark mode
- File: `apps/dashboard/src/app/webhooks/page.tsx:552`

**2. /webhooks -- Empty-state icon circle (line 425)**
- Class: `bg-slate-100`
- Missing: `dark:bg-slate-800` (or use `bg-muted`)
- Impact: White circle behind the link icon in the empty state
- File: `apps/dashboard/src/app/webhooks/page.tsx:425`

**3. /webhooks -- Loading skeleton placeholders (lines 416-417)**
- Class: `bg-slate-200`
- Missing: `dark:bg-slate-700`
- Impact: Light gray shimmer blocks on dark background during loading
- File: `apps/dashboard/src/app/webhooks/page.tsx:416-417`

### P1 -- High: Low Contrast Text

**4. /webhooks -- "No webhooks configured" heading (line 430)**
- Class: `text-slate-700`
- Missing: `dark:text-slate-200` (or use `text-foreground`)
- Impact: Dark gray text on dark background = nearly invisible
- File: `apps/dashboard/src/app/webhooks/page.tsx:430`

**5. /webhooks -- "Webhook Documentation" heading (line 558)**
- Class: `text-slate-700`
- Missing: `dark:text-slate-200` (or use `text-foreground`)
- Impact: Same low-contrast issue
- File: `apps/dashboard/src/app/webhooks/page.tsx:558`

**6. /webhooks -- Webhook URL code text (line 465)**
- Class: `text-slate-700`
- Missing: `dark:text-slate-200`
- Impact: Webhook URL barely readable in dark mode (when webhooks exist)
- File: `apps/dashboard/src/app/webhooks/page.tsx:465`

### P2 -- Medium: Hardcoded Light-Mode Colors Without Dark Variants

**7. /webhooks -- Delivery history borders (lines 91, 102, 109)**
- Class: `border-slate-100`
- Missing: `dark:border-slate-700` (or use `border-border`)
- File: `apps/dashboard/src/app/webhooks/page.tsx:91,102,109`

**8. /webhooks -- Delivery log row (line 117)**
- Class: `border-slate-100 bg-slate-50/50`
- Missing: `dark:border-slate-700 dark:bg-slate-800/50`
- File: `apps/dashboard/src/app/webhooks/page.tsx:117`

**9. /webhooks -- Delivery log event type text (line 123)**
- Class: `text-slate-600`
- Missing: `dark:text-slate-300`
- File: `apps/dashboard/src/app/webhooks/page.tsx:123`

**10. /webhooks -- Event tag pills (line 489)**
- Class: `bg-slate-100 text-slate-600`
- Missing: `dark:bg-slate-700 dark:text-slate-300`
- Impact: Light pills with dark text on dark card background
- File: `apps/dashboard/src/app/webhooks/page.tsx:489`

**11. /webhooks -- Create form event checkbox border (line 363)**
- Class: `border-slate-200 hover:border-slate-300`
- Missing: `dark:border-slate-600 dark:hover:border-slate-500`
- File: `apps/dashboard/src/app/webhooks/page.tsx:363`

**12. /webhooks -- Delete button hover (line 533)**
- Class: `hover:bg-red-50`
- Missing: `dark:hover:bg-red-900/20`
- File: `apps/dashboard/src/app/webhooks/page.tsx:533`

**13. /audit-logs -- Status badge colors (lines 96, 108)**
- Class: `bg-slate-100 text-slate-700` (hardcoded without dark variant)
- Missing: `dark:bg-slate-700 dark:text-slate-300`
- File: `apps/dashboard/src/app/audit-logs/page.tsx:96,108`

### P3 -- Low: Minor / Cosmetic

**14. /webhooks -- Chevron icon color (line 458)**
- Class: `text-slate-400`
- This is borderline acceptable but could use `text-muted-foreground`

**15. Design system theme.css mismatch (lines 115-120, 119-120)**
- The design system's `theme.css` uses bare HSL values for dark mode card/muted/popover
  (e.g., `--card: 213 43% 33%;`) while the dashboard's `globals.css` also defines them.
- The dashboard's globals.css takes precedence, but this inconsistency could cause
  issues if the design system CSS loads after globals.
- File: `apps/dashboard/node_modules/@encypher/design-system/src/styles/theme.css:115-124`

---

## Pages With No Dark Mode Issues Found
- /settings (Profile tab) -- uses semantic tokens (bg-card, text-foreground, etc.)
- /settings Organization tab -- properly themed
- /settings/organization -- cards use bg-card, badges have dark: variants
- /image-signing -- uses border-border, text-muted-foreground correctly
- /print-detection -- simple gate page, properly themed
- /api-keys -- including IP allowlist modal, all themed
- /billing -- all cards/sections properly themed
- /cdn-analytics -- simple gate page, properly themed
- /team -- simple gate page, properly themed

---

## Recommended Fix Strategy
The webhooks page is the main offender. All issues can be fixed by:
1. Replace `bg-slate-50` with `bg-muted` or add `dark:bg-slate-800`
2. Replace `bg-slate-100` with `bg-muted` or add `dark:bg-slate-700`
3. Replace `bg-slate-200` with add `dark:bg-slate-600`
4. Replace `text-slate-700` with `text-foreground` or add `dark:text-slate-200`
5. Replace `text-slate-600` with `text-muted-foreground` or add `dark:text-slate-300`
6. Replace `border-slate-100/200` with `border-border` or add dark variants
7. Audit-logs badge function needs conditional dark variants

Preferred approach: use semantic tokens (`bg-muted`, `text-foreground`, `border-border`)
instead of adding more `dark:` overrides. This is more maintainable and aligns with
how the rest of the dashboard is styled.
