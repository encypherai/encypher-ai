# Encypher Dashboard Full UX/UI Audit -- March 2026

**Team**: TEAM_262
**Date**: March 19, 2026
**Auditor**: UX/UI Expert Review (Opus)
**Viewport**: 1920x1080 desktop, light + dark mode
**Account**: test@encypherai.com (Publisher tier)
**Baseline**: Dec 2025 audit scored dashboard 6.5/10

---

## Audit Methodology

### 12-Category Rubric (0-10 each)

| # | Category | What it measures |
|---|----------|-----------------|
| 1 | Color Palette | Brand consistency, contrast ratios, semantic color usage |
| 2 | Typography | Font hierarchy, readability, weight/size consistency |
| 3 | Iconography | Icon source consistency (Lucide vs custom SVG), visual weight |
| 4 | Spacing & Layout | Padding/margin consistency, grid alignment, density |
| 5 | Content Hierarchy | Visual priority, scanability, information architecture |
| 6 | Navigation Structure | Sidebar organization, active states, breadcrumbs |
| 7 | Onboarding UX | First-run experience, progressive disclosure, guidance |
| 8 | Data Presentation | Charts, tables, metrics, empty states |
| 9 | Actionability | CTAs, next steps, task completion clarity |
| 10 | Empty/Zero States | Quality when no data exists |
| 11 | Brand Identity | Encypher brand alignment, C2PA/provenance positioning |
| 12 | Professional Polish | Animations, transitions, attention to detail, dark mode |

**ICP lens**: "Would a Fortune 500 GC on a vendor evaluation call trust this page?"

---

## Wave 0: Global Chrome Assessment

### Sidebar

| Aspect | Assessment | Score |
|--------|-----------|-------|
| Organization | 5 groups (top-level, Publish, Insights, Enterprise, Account) + Admin | 9 |
| Icon consistency | All custom inline SVGs with consistent stroke width (1.5) | 9 |
| Active state | Blue highlight fill on active item, clear contrast | 8 |
| Collapse behavior | Chevron toggle, collapses to icons-only | 8 |
| Org switcher | Top of sidebar, dropdown with org name | 8 |
| Enterprise gating | `enterpriseOnly` items visible but gated on click | 7 |

**Issues:**
- No breadcrumbs on any page (flat nav only)
- Sidebar label "Content Performance" wraps in collapsed mode
- "Print Leak Detection" label is long for collapsed sidebar

### Header Bar

| Aspect | Assessment | Score |
|--------|-----------|-------|
| Theme toggle | Moon/sun icon, works correctly | 9 |
| Notification bell | Present, centered | 8 |
| User avatar | Initial letter in circle, name displayed | 8 |
| Layout | Right-aligned controls, clean spacing | 9 |

### Global Chrome Scores (inherited by all pages unless noted)

| Category | Score | Notes |
|----------|-------|-------|
| Navigation Structure | 8 | Clean grouping, no breadcrumbs |
| Brand Identity | 9 | Consistent delft-blue sidebar, Encypher logo, C2PA badge on Overview |

---

## Wave 1: Power Pages

### Page 1: Overview (Demo Mode) -- `/?demo=true`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 9 | Brand colors throughout, semantic green/amber for status |
| Typography | 8 | Clear hierarchy: greeting > section headers > card labels > values |
| Iconography | 9 | Custom provenance SVGs (IconSign, IconVerify, etc.), domain-specific |
| Spacing & Layout | 9 | 4-column metric grid, consistent card padding, no wasted space |
| Content Hierarchy | 9 | Hero greeting > Quick Start > Metrics > API Keys > Activity |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 9 | Demo banner clear, "Exit Demo" CTA, sample data realistic |
| Data Presentation | 9 | Sparklines, percentage deltas, trend indicators, formal notice progress ring |
| Actionability | 9 | "View Progress", "Manage Keys", clickable metric cards |
| Empty/Zero States | N/A | Demo mode always populated |
| Brand Identity | 9 | C2PA badge, provenance-specific language |
| Professional Polish | 9 | Staggered fade-in animations, count-up numbers, sparkline draw, hover scale |

**Score: 8.8/10** (up from ~6.5 baseline)

**Strengths:**
- Custom provenance icons replace generic Lucide (IconSign pen nib, IconVerify magnifier+check)
- Animated count-up on metric values with requestAnimationFrame easing
- Live indicator on activity feed with pulsing green dot
- Staggered card entrance animations (80ms delay per card)

**Issues:**
- Formal notice progress ring is small and hard to read at a glance
- "344 more to qualify" text could use more context (qualify for what?)

---

### Page 2: Overview (Real Data) -- `/`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 9 | Same as demo |
| Typography | 8 | Same hierarchy |
| Iconography | 9 | Same custom SVGs |
| Spacing & Layout | 8 | Quick Start checklist adds vertical height but justified |
| Content Hierarchy | 8 | Quick Start prominent, metrics below fold for new users |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 9 | 3-step checklist with completion states, "Verify signed content" / "View content performance" CTAs |
| Data Presentation | 8 | Real metrics (104 API calls, 16 docs signed), decline trends shown |
| Actionability | 9 | "Try Verification" CTA in zero-state Verifications card |
| Empty/Zero States | 8 | Verifications card has meaningful zero state with action CTA |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 8 | Same animations, real data with lower numbers still looks professional |

**Score: 8.4/10**

**Issues:**
- "Needs attention" + "Declining" on Success Rate 92.4% could alarm users unnecessarily (92.4% is still good)
- Decline indicators (-75%, -92%) could be contextualized better (e.g., "vs prior 30 days when account was new")

---

### Page 3: Playground -- `/playground`

*(Scored 9.7/10 in prior visual audit; code analysis reveals several hidden issues)*

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 8 | `methodColors` and `tierColors` have NO dark: variants -- badges fail in dark mode |
| Typography | 9 | Method badges, code blocks well-styled |
| Iconography | 8 | All inline SVGs (no Lucide despite Image Signing using it), lock icon duplicated |
| Spacing & Layout | 10 | Split-pane, responsive sidebar |
| Content Hierarchy | 10 | Endpoint list > Request > Response flow |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 9 | Guided tour, Quick Start overlay; but tour state lost on refresh |
| Data Presentation | 10 | JSON syntax highlighting, response summaries |
| Actionability | 9 | Send Request CTA has no loading feedback (no spinner during 1-3s request) |
| Empty/Zero States | 8 | Response panel shows nothing when empty (no placeholder text) |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 8 | Unicode emoji in CopyPasteTester violates ASCII rule, duplicate rendering code |

**Score: 8.8/10** (adjusted down from 9.4 based on code findings)

**Issues (from code analysis):**
- `methodColors` (`bg-green-100 text-green-700` etc.) and `tierColors` have NO `dark:` variants -- badges fail contrast in dark mode
- No loading feedback on Send Request button -- no spinner, no text change during 1-3s API call
- Response panel is blank when no request sent (no placeholder like "Send a request to see results")
- Unicode emoji (`\u2705`, `\u274C`) in CopyPasteSurvivalTester violates project ASCII-only rule
- Lock icon SVG path duplicated inline in 2+ places without extraction to component
- Endpoint list has two near-identical rendering blocks (filtered vs unfiltered) -- maintenance hazard
- `localStorage.setItem('playground_tour_active')` set but never read on mount -- tour state lost on refresh
- Toast-only error handling -- if user misses toast, page looks silently broken

---

### Page 4: Content Performance (Analytics) -- `/analytics`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 8 | Chart colors use CSS variables |
| Typography | 8 | Section headers, metric labels clear |
| Iconography | 7 | All inline SVGs (no Lucide), but no custom icons per metric |
| Spacing & Layout | 8 | Grid layout for KPI cards, charts below |
| Content Hierarchy | 8 | KPIs above fold, detailed charts below |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 6 | No guidance for interpreting analytics |
| Data Presentation | 7 | Custom hand-rolled bar chart (no library), limited axis labels |
| Actionability | 6 | Limited -- mostly read-only; funnel CTAs use raw buttons (a11y issue) |
| Empty/Zero States | 7 | Bar chart: plain text "No data available" (no icon/CTA) |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 7 | 3 good skeleton components, but raw buttons mixed with design system Buttons |

**Score: 7.3/10**

**Issues (from code analysis):**
- Hand-rolled bar chart: no axis labels beyond 3 Y-axis values, always shows last 14 days regardless of selected time range
- `Link` wrapping `<button>` throughout the funnel -- nested interactive elements (a11y violation)
- Raw `<button>` with Tailwind used for funnel CTAs instead of design system `Button` component
- API Health section collapsed by default with no at-a-glance status indicator
- No error state for the funnel -- if query errors, renders all zeros instead of error boundary
- `text-slate-800 dark:text-slate-100` used inline instead of design system `text-foreground` token

---

### Page 5: API Keys -- `/api-keys`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 8 | Active/revoked status colors semantic |
| Typography | 8 | Key names, dates, permissions clearly styled |
| Iconography | 8 | All inline SVGs (key, copy, download, plus) |
| Spacing & Layout | 8 | Card-per-key layout with clear sections |
| Content Hierarchy | 8 | Create button prominent, key list scanable |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 8 | Strong zero state: icon circle + heading + description + CTA |
| Data Presentation | 8 | Key masking, `Badge` for permissions, `formatDate` |
| Actionability | 8 | Create, Copy, Delete actions; but Delete uses `window.confirm()` |
| Empty/Zero States | 9 | Best empty state of audited pages -- icon, heading, description, CTA |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 7 | Loading state is just text (no skeleton), `window.confirm()` breaks polish |

**Score: 8.1/10**

**Issues (from code analysis):**
- Loading state: plain text "Loading API keys..." (no skeleton -- jarring layout shift)
- `window.confirm()` for key deletion -- browser native dialog, visually inconsistent
- Modal textarea manually duplicates Input component styling instead of using Input
- `text-gray-900 dark:text-gray-100` on generated key code block instead of `text-foreground`

---

### Page 6: Rights Management -- `/rights`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 8 | Bronze/Silver/Gold tier colors, thorough dark mode with light/dark pairs |
| Typography | 8 | Tab labels, tier headers, field labels all clear |
| Iconography | 7 | Tier dots (colored circles), inline SVGs for status -- no custom icons |
| Spacing & Layout | 9 | 3-column tier card grid, public endpoints list well-organized |
| Content Hierarchy | 9 | Profile tab as default, progressive disclosure via 4 tabs |
| Navigation Structure | 9 | 4 tabs (Profile, Analytics, Notices, Licensing) -- clear grouping |
| Onboarding UX | 7 | Template picker exists but "Guide" is a raw `<a>` styled as button |
| Data Presentation | 8 | TierCard custom components, multiple data tables with scroll |
| Actionability | 7 | 6+ locations use raw `<button>` instead of design system Button |
| Empty/Zero States | 5 | Every empty state is just `<p>` gray text -- no icons, no CTAs, no guidance |
| Brand Identity | 9 | Rights/licensing language aligns with C2PA/ODRL standards |
| Professional Polish | 6 | 3 different badge implementations, pre-filled demo data in Notice form |

**Score: 7.7/10**

**Strengths:**
- Public discovery endpoints section is enterprise-ready (JSON, ODRL, RSL, robots.txt)
- Best dark mode coverage of any page (pre-defined light/dark class pairs in TIER_META)
- Version history shows audit trail

**Issues (from code analysis):**
- **3 different badge systems**: design system `Badge`, custom `StatusBadge` component, and inline `<span>` with conditional classes -- all on one page
- **6+ raw `<button>` locations**: Licensing approve/reject, Evidence "Download PDF" (styled with hardcoded `bg-blue-600`), template cards
- **Pre-filled demo data in Notice form**: Default values include "OpenAI", a specific email, and "Encypher Times" case text -- would confuse production users
- **All empty states are text-only**: "No formal notices issued yet", "No licensing requests yet" etc. -- no icons, no next-step CTAs (contrast with API Keys' strong empty state)
- **Hardcoded hex `#2A87C4`**: Template picker uses `hover:border-[#2A87C4]` instead of `blue-ncs` token
- **No pagination on discovery events table**: Query requests `limit: 50` but no pagination UI

---

## Wave 2: Content/Action Pages

### Page 7: Governance -- `/governance`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 8 | Consistent with global theme |
| Typography | 7 | Tab structure matches Rights |
| Iconography | 7 | Basic icons |
| Spacing & Layout | 7 | Tabbed interface |
| Content Hierarchy | 7 | Tabs organize content |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 6 | Limited guidance for governance features |
| Data Presentation | 7 | Tabbed content areas |
| Actionability | 6 | Actions depend on data availability |
| Empty/Zero States | 5 | **No empty state for policies list** -- renders blank when no policies exist |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 7 | Functional but not polished |

**Score: 7.0/10**

**Issues (code-level):**
- Policies list has no empty state -- renders blank when no governance policies exist
- Limited onboarding for what governance features do and why they matter

---

### Page 8: Enforcement -- `/enforcement`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 8 | Consistent |
| Typography | 7 | Clear headers |
| Iconography | 7 | Standard icons |
| Spacing & Layout | 7 | List/card layout |
| Content Hierarchy | 7 | Enforcement actions organized |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 6 | Limited onboarding for enforcement workflows |
| Data Presentation | 6 | Notice listings, **no pagination** -- all records load at once |
| Actionability | 6 | View/Evidence buttons visually identical -- unclear which does what |
| Empty/Zero States | 7 | Shared EmptyState component |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 7 | Functional |

**Score: 7.0/10**

**Issues (code-level):**
- No pagination on enforcement notices -- will not scale past ~50 records
- View and Evidence buttons are visually identical -- need distinct styling or labels
- Limited first-run guidance for enforcement workflows

---

### Page 9: Integrations -- `/integrations`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 8 | Consistent |
| Typography | 8 | Integration names, descriptions clear |
| Iconography | 8 | Integration-specific logos (WordPress, Ghost, etc.) |
| Spacing & Layout | 8 | Card grid, consistent sizing |
| Content Hierarchy | 8 | Categorized integrations |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 8 | "Connect" CTAs on each card |
| Data Presentation | 8 | Status badges (connected/available) |
| Actionability | 8 | Clear connect/configure actions |
| Empty/Zero States | N/A | Always shows available integrations |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 7 | WordPress plugin download URL has hardcoded version number |

**Score: 8.0/10**

**Issues (code-level):**
- WordPress plugin download URL has hardcoded version number -- will go stale with releases

---

### Page 10: Billing -- `/billing`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 7 | `bg-gray-100 text-gray-800` hardcoded without `dark:` variants; invoice badge colors light-only |
| Typography | 8 | Plan names, pricing, feature lists clear |
| Iconography | 7 | Mix of Lucide icons |
| Spacing & Layout | 8 | Plan comparison layout |
| Content Hierarchy | 8 | Current plan > usage > upgrade options |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 7 | Upgrade path clear |
| Data Presentation | 7 | Usage metrics display, but **`const subscription = null` hardcoded** -- plan data always shows "Free" |
| Actionability | 5 | **"Manage Billing" button never renders** because subscription is always null |
| Empty/Zero States | 7 | Free tier shows clear upgrade path |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 6 | Invoice status badges have no dark mode variants; subscription bug suppresses key CTA |

**Score: 7.2/10**

**Issues (code-level):**
- **CRITICAL BUG**: `const subscription = null` on line ~71 -- hardcoded null means "Manage Billing" button never renders and plan data always shows "Free" regardless of actual subscription state
- Invoice status badges (`bg-green-100 text-green-800`, `bg-yellow-100 text-yellow-800`, etc.) have NO `dark:` variants
- `bg-gray-100 text-gray-800` hardcoded without dark mode variant on plan cards

---

### Page 11: Settings -- `/settings`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 7 | Email change form panels have NO dark mode variants (`bg-blue-50`, `bg-yellow-50`) |
| Typography | 8 | Form labels, section headers clear |
| Iconography | 8 | Lucide icons (Copy, Check, CreditCard, KeyRound, ShieldCheck) |
| Spacing & Layout | 8 | Form layout with clear sections |
| Content Hierarchy | 8 | Personal > Security > Preferences |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 7 | Self-explanatory forms |
| Data Presentation | 7 | Profile data pre-filled, but zero skeleton loaders in ~2500-line file |
| Actionability | 8 | Save, update, change password CTAs |
| Empty/Zero States | N/A | Always has user data |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 6 | TOTP setup exposes raw `otpauth://` URI in plain text (security concern); no loading skeletons |

**Score: 7.5/10**

**Issues (code-level):**
- Email change form panels use `bg-blue-50`, `bg-yellow-50` without `dark:` variants -- renders as bright patches in dark mode
- TOTP setup flow exposes raw `otpauth://` URI in plain text -- should be hidden behind "Show secret" toggle for security
- Zero skeleton loaders in ~2500-line file -- all form sections flash in with no loading state
- No loading feedback during save operations

---

## Wave 3: Utility/Enterprise Pages

### Page 12: AI Crawlers -- `/ai-crawlers`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 7 | `getComplianceBadgeClass()` returns hardcoded light-only colors (no dark: variants) |
| Typography | 7 | Crawler names, domains, timestamps |
| Iconography | 7 | 5 inline SVG stat icons, LockIcon component; no Lucide |
| Spacing & Layout | 8 | Rich layout: company grid, stat row, charts, table |
| Content Hierarchy | 8 | Company spotlight > stats > charts > crawler table |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 5 | Empty states are all plain centered text -- no CTAs, no "connect Logpush" guidance |
| Data Presentation | 8 | Hand-rolled stacked bar chart, horizontal bars, 8-column table, badges |
| Actionability | 6 | Time range toggle + Export CSV (Enterprise-only, silently absent for others) |
| Empty/Zero States | 5 | 5+ different empty text strings, none with icons or next-step CTAs |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 6 | Compliance badges break in dark mode, inline hex colors may disappear on dark bg |

**Score: 7.0/10**

**Issues (from code analysis):**
- `getComplianceBadgeClass()` returns `bg-emerald-100 text-emerald-800` etc. with NO `dark:` variants -- fails in dark mode
- `CRAWLER_COLORS`/`COMPANY_COLORS` are hardcoded hex injected via `style` -- e.g. `#6b7280` gray nearly disappears on dark slate
- All 5+ empty states are plain text only -- no icons, no CTAs (e.g., "Connect Cloudflare Logpush to start detecting crawlers")
- Export CSV silently absent for non-Enterprise users -- no explanation
- `blur-[2px] select-none` on locked data reveals data exists but hides it -- frustrating UX pattern

---

### Page 13: Image Signing -- `/image-signing`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 9 | Consistent, toggle controls use accent colors, good dark mode coverage |
| Typography | 8 | Section headers "Upload Images" / "Signing Options" clear |
| Iconography | 8 | Uses Lucide (Upload, Download, CheckCircle, XCircle, Loader2) -- only page using Lucide |
| Spacing & Layout | 9 | 2-column layout (upload left, options right), well-balanced |
| Content Hierarchy | 9 | Upload area prominent, options secondary |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 8 | Drop zone with file type hints, "Enterprise" badge on TrustMark |
| Data Presentation | 8 | ResultCard shows manifest summary, per-image badges, file sizes |
| Actionability | 9 | "Sign N Images" full-width CTA, per-image + bulk download |
| Empty/Zero States | 8 | Drop zone IS the natural empty state -- well-designed |
| Brand Identity | 9 | C2PA Manifest toggle, provenance-specific language |
| Professional Polish | 8 | Suspense boundary, loading spinner, toggle animations |

**Score: 8.5/10**

**Strengths:**
- Clean 2-column layout balances input and configuration
- Enterprise tier badge on TrustMark option is subtle but clear
- Only page using Lucide icons consistently -- all others use inline SVGs
- Good dark mode: all badges carry proper `dark:` variants

**Issues (from code analysis):**
- `ResultCard` shows placeholder icon instead of actual signed image thumbnail (has `img.preview` available)
- `downloadAll` triggers multiple sequential `<a>.click()` calls -- browsers may block as popup flood (should ZIP)
- Quality slider uses bare `<input type="range">` with `accent-blue-ncs` instead of design system component

---

### Page 14: Webhooks -- `/webhooks`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 8 | Consistent, `text-red-500` error messages missing `dark:` variant |
| Typography | 8 | Clear heading, description |
| Iconography | 7 | All inline SVGs, link icon in empty state |
| Spacing & Layout | 7 | Centered empty state, doc section below |
| Content Hierarchy | 7 | Empty state > documentation link |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 8 | Good empty state: icon + heading + description + CTA + doc link |
| Data Presentation | 7 | Status badges, event type chips as unstyled `<span>` |
| Actionability | 7 | Delete uses `window.confirm()`; Enable/Disable label ambiguous |
| Empty/Zero States | 8 | Well-structured: icon + heading + description + CTA |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 7 | Good skeleton loading; but `window.confirm()` for delete |

**Score: 7.4/10**

**Issues (from code analysis):**
- `window.confirm()` for webhook delete -- blocking, non-styleable
- Enable/Disable toggle is text-only -- ambiguous whether label shows current state or action
- `text-red-500` on error messages has no `dark:` variant
- Event type chips rendered as unstyled `<span>` instead of design system `Badge`

---

### Page 15: Team -- `/team`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 6 | `ROLE_CONFIG` avatar colors (`bg-yellow-100` etc.) have NO `dark:` variants |
| Typography | 7 | Clean heading and description |
| Iconography | 7 | All inline SVGs, team/people icon in circle |
| Spacing & Layout | 6 | Very sparse upgrade wall; main view has complex multi-form layout |
| Content Hierarchy | 6 | Upgrade: just icon > title > description > button |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 5 | No explanation of what Team features include; main view has no onboarding |
| Data Presentation | 7 | Members as flex rows, seat usage metric, bulk invite preview |
| Actionability | 6 | `window.confirm()` for Remove and Revoke All; disabled invite button with no tooltip |
| Empty/Zero States | 5 | "No team members yet" plain text only (no icon, no CTA link) |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 5 | Loading states are text-only, avatar colors break in dark mode |

**Score: 6.3/10**

**Issues (from code analysis):**
- `ROLE_CONFIG` avatar colors (`bg-yellow-100`, `bg-blue-100`, `bg-purple-100`, `bg-green-100`, `bg-gray-100`) have NO `dark:` variants -- bright white patches in dark mode
- `window.confirm()` for Remove and Revoke All
- Invite button disabled when at seat limit with no tooltip explaining why
- Loading states: "Loading team members..." and "Loading API keys..." plain text
- Team Members empty state: plain text only, no icon, no CTA

---

### Page 16: Audit Logs -- `/audit-logs`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 7 | Status/severity badges have `dark:` pairs, BUT `text-red-700` (Critical Failures) and `text-blue-700` (Correlate) have none |
| Typography | 8 | Monospace timestamps, endpoint paths; clear column headers |
| Iconography | 5 | Zero icons on entire page -- no Lucide, no inline SVGs |
| Spacing & Layout | 6 | Dense filter bar: 10+ controls in `flex gap-3 flex-wrap`, chaotic on mid-width viewports |
| Content Hierarchy | 8 | Summary KPIs up top > filters > table |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 6 | No explanation of what events are logged or how to use filters |
| Data Presentation | 7 | Inline badge classes (not design system `Badge`), "Severity: n/a" verbose prefix |
| Actionability | 7 | Export CSV/JSON, Saved Views; but "Correlate by request ID" is unstyled inline button |
| Empty/Zero States | 6 | "No matching telemetry events" text only; summary cards show `0` during loading |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 6 | `<details>` for dropdowns clashes with `<select>` controls; filter bar wraps chaotically |

**Score: 7.0/10**

**Issues (from code analysis):**
- `text-red-700` on Critical Failures metric -- near-invisible in dark mode (no `dark:` variant)
- `text-blue-700` on "Correlate by request ID" -- near-invisible in dark mode
- Zero icons on entire page -- most sparse alongside Compliance
- `<details>` HTML elements for Severity/Event Types dropdowns clash visually with `<select>` controls
- Filter bar: 10+ controls with `flex gap-3 flex-wrap` wraps chaotically
- Summary cards show `0` during loading (no skeleton) -- looks like "nothing happened"
- No "Reset filters" affordance
- Loading: "Loading audit logs..." plain text (no skeleton for table rows)

---

### Page 17: Print Leak Detection -- `/print-detection`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 7 | Same as Team upgrade wall |
| Typography | 7 | Clear description of feature |
| Iconography | 7 | Printer icon in circle |
| Spacing & Layout | 6 | Same sparse upgrade wall |
| Content Hierarchy | 6 | Icon > title > description > tier note > button |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 6 | Description explains the feature better than Team page |
| Data Presentation | N/A | |
| Actionability | 6 | Single upgrade button |
| Empty/Zero States | 5 | Same minimal pattern as Team |
| Brand Identity | 9 | Good feature description mentioning "imperceptible spacing patterns" |
| Professional Polish | 6 | Placeholder feel |

**Score: 6.4/10**

---

### Page 18: CDN Provenance Analytics -- `/cdn-analytics`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 7 | Same upgrade wall pattern |
| Typography | 7 | Clear feature description |
| Iconography | 7 | Cloud icon in circle |
| Spacing & Layout | 6 | Same sparse pattern |
| Content Hierarchy | 6 | Same structure |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 6 | Describes what CDN analytics offers |
| Data Presentation | N/A | |
| Actionability | 6 | Single upgrade button |
| Empty/Zero States | 5 | Same minimal pattern |
| Brand Identity | 9 | CDN provenance language is enterprise-appropriate |
| Professional Polish | 6 | Placeholder feel |

**Score: 6.4/10**

---

### Page 19: EU AI Act Compliance -- `/compliance`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 9 | Green ring for 100%, green "Compliant" badges, good dark mode |
| Typography | 8 | Section grouping (Content Provenance, Rights Management, Governance) |
| Iconography | 5 | Zero icons -- no Lucide, no inline SVGs. StatusBadge is text-only |
| Spacing & Layout | 8 | Clean card-per-requirement layout |
| Content Hierarchy | 9 | Score ring hero > categorized requirements > download report |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 7 | Self-explanatory but no celebratory 100% state, no partial-compliance guidance |
| Data Presentation | 9 | ReadinessCircle SVG donut, "7 of 7 requirements met", article references |
| Actionability | 6 | "Download Compliance Report" calls `window.print()` -- NOT a real PDF download |
| Empty/Zero States | 6 | If items array is empty, renders nothing (no explanation); no celebration at 100% |
| Brand Identity | 10 | EU AI Act compliance is a core differentiator -- excellent positioning |
| Professional Polish | 7 | Spinner loading (no skeleton), hardcoded deadline string will go stale |

**Score: 7.7/10** (adjusted down from 8.3 based on code findings)

**Strengths:**
- EU AI Act deadline date displayed prominently
- Article references (Article 50, Article 53) show regulatory depth
- Best dark mode handling of any page (proper SVG fill utilities)

**Issues (from code analysis):**
- **"Download Compliance Report" is `window.print()`** -- prints full page including sidebar/nav chrome, NOT a real PDF report download. Users expect PDF.
- Zero icons on the entire page -- most icon-sparse page in the dashboard
- Hardcoded deadline: "EU AI Act Compliance Deadline: August 2, 2026" is a static string that will go stale
- No empty state: if `data.items` is empty, the grouped checklist renders nothing with no explanation
- No celebratory state at 100% compliance -- just the same checklist with all items green
- Loading uses spinner + text (no skeleton) -- visible layout reflow when data loads

---

### Page 20: Support -- `/support`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 7 | `<textarea>` missing `bg-background text-foreground` -- CONFIRMED dark mode bug |
| Typography | 8 | Form labels, FAQ questions clear |
| Iconography | 7 | 4 inline SVG icons duplicated from docs/page.tsx |
| Spacing & Layout | 8 | 2-column (form + quick links), FAQ below |
| Content Hierarchy | 8 | Contact form primary, quick links secondary, FAQ tertiary |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 8 | Category dropdown, clear form structure |
| Data Presentation | 7 | FAQ uses native `<details>/<summary>` -- good a11y baseline |
| Actionability | 7 | "Send Message" CTA; no success state after submission (form just clears) |
| Empty/Zero States | N/A | |
| Brand Identity | 9 | (inherited) |
| Professional Polish | 6 | Dark mode textarea bug, icon duplication, uses `useState` instead of `useMutation` |

**Score: 7.5/10**

**Issues (from code analysis):**
- **CONFIRMED BUG**: `<textarea>` (line 164) missing `bg-background text-foreground` -- renders white in dark mode
- `IconApi`, `IconTerminal`, `IconPackage`, `IconStatus` are copy-pasted from docs/page.tsx -- should be centralized
- No success state after form submission -- toast fires but form just clears, no confirmation message
- Uses `useState` + `try/finally` for submission instead of `useMutation` (inconsistent with every other page)

---

### Page 21: Documentation -- `/docs`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 8 | Hardcoded `#2A87C4` in hover classes; `bg-white dark:bg-slate-800` correct |
| Typography | 8 | Guide titles, descriptions, tag badges |
| Iconography | 8 | 10+ inline SVG icons per file; BUT `IconQuote` uses checkmark path (semantic mismatch) |
| Spacing & Layout | 9 | 2-column card grid, consistent card sizing |
| Content Hierarchy | 9 | "Integration Guides" section header > card grid |
| Navigation Structure | 8 | (inherited) |
| Onboarding UX | 8 | Tags help users find relevant docs (WordPress, Plugin, 5 min setup) |
| Data Presentation | 8 | Card descriptions concise, tags scanable |
| Actionability | 8 | Each card is clickable, chevron indicates navigation |
| Empty/Zero States | N/A | Static content |
| Brand Identity | 9 | Covers all integration types (WordPress, Ghost, BYOK, Streaming, Coalition) |
| Professional Polish | 8 | Card hover states, but icon SVGs duplicated from support/page.tsx |

**Score: 8.4/10**

**Strengths:**
- Cards cover the full product surface (9 guides + 3 SDK/reference cards)
- Tags enable quick scanning
- Covers enterprise-specific docs (BYOK, Print Leak Detection, Add-Ons)

**Issues (from code analysis):**
- `IconQuote` (line 108) uses a checkmark SVG path, not a quote icon -- semantic mismatch
- Icon SVGs (`IconApi`, `IconTerminal`, etc.) are duplicated between docs/page.tsx and support/page.tsx
- Hardcoded `#2A87C4` in hover classes -- design system token bypass
- No search/filter on guides -- will degrade as more are added

---

### Page 22: Organization Settings -- `/settings/organization`

| Category | Score | Notes |
|----------|-------|-------|
| Color Palette | 9 | Best dark mode coverage of all pages -- all badges have proper `dark:` pairs |
| Typography | 8 | Section headers with icons, field labels and values aligned |
| Iconography | 8 | Uses Lucide (Shield, Settings, Package, ArrowLeft, Trash2) -- ONLY page using Lucide |
| Spacing & Layout | 8 | Card-per-section layout, clear key-value pairs |
| Content Hierarchy | 8 | "Back to Settings" breadcrumb > Organization name > Security > Signing > Features > Deletion |
| Navigation Structure | 9 | Has breadcrumb ("Back to Settings") -- only page with back navigation |
| Onboarding UX | 6 | Security policies display-only BUT user IS the admin -- can't edit what they should control |
| Data Presentation | 8 | Key-value display, feature list with checkmarks, plan badge, add-ons |
| Actionability | 6 | Security policies are read-only; Approve/Cancel deletion have identical styling |
| Empty/Zero States | 8 | Context-aware: "No active deletion requests" / "All add-ons included with Enterprise" |
| Brand Identity | 9 | "C2PA 2.3" badge, signing identity, provenance language |
| Professional Polish | 7 | Inline SVG checkmarks used alongside Lucide icons (inconsistent) |

**Score: 7.8/10**

**Note:** Previously crashed to login (TEAM_260 bug) -- now fixed and renders correctly.

**Issues (from code analysis):**
- Only page using Lucide React -- inconsistent with all other pages using inline SVGs
- Security policies (MFA, session timeout, password) are display-only but user IS the administrator -- "contact your administrator" is self-referential
- Approve/Cancel deletion requests have identical visual styling (`variant="outline"`) -- high-stakes approve should be distinct
- Inline SVG checkmarks in feature list used alongside Lucide icons -- mixed approach
- `useCurrentUserRole` fetches full member list to find current user's role -- could be a dedicated endpoint

---

## Aggregate Scorecard

| Page | Color | Type | Icon | Space | Hierarchy | Nav | Onboard | Data | Action | Empty | Brand | Polish | **AVG** |
|------|-------|------|------|-------|-----------|-----|---------|------|--------|-------|-------|--------|---------|
| Overview (Demo) | 9 | 8 | 9 | 9 | 9 | 8 | 9 | 9 | 9 | - | 9 | 9 | **8.8** |
| Overview (Real) | 9 | 8 | 9 | 8 | 8 | 8 | 9 | 8 | 9 | 8 | 9 | 8 | **8.4** |
| Playground | 8 | 9 | 8 | 10 | 10 | 8 | 9 | 10 | 9 | 8 | 9 | 8 | **8.8** |
| Analytics | 8 | 8 | 7 | 8 | 8 | 8 | 6 | 7 | 6 | 7 | 9 | 7 | **7.3** |
| API Keys | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 9 | 9 | 7 | **8.1** |
| Rights | 8 | 8 | 7 | 9 | 9 | 9 | 7 | 8 | 7 | 5 | 9 | 6 | **7.7** |
| Governance | 8 | 7 | 7 | 7 | 7 | 8 | 6 | 7 | 6 | 5 | 9 | 7 | **7.0** |
| Enforcement | 8 | 7 | 7 | 7 | 7 | 8 | 6 | 6 | 6 | 7 | 9 | 7 | **7.0** |
| Integrations | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | - | 9 | 7 | **8.0** |
| Billing | 7 | 8 | 7 | 8 | 8 | 8 | 7 | 7 | 5 | 7 | 9 | 6 | **7.2** |
| Settings | 7 | 8 | 8 | 8 | 8 | 8 | 7 | 7 | 8 | - | 9 | 6 | **7.5** |
| AI Crawlers | 7 | 7 | 7 | 8 | 8 | 8 | 5 | 8 | 6 | 5 | 9 | 6 | **7.0** |
| Image Signing | 9 | 8 | 8 | 9 | 9 | 8 | 8 | 8 | 9 | 8 | 9 | 8 | **8.5** |
| Webhooks | 8 | 8 | 7 | 7 | 7 | 8 | 8 | 7 | 7 | 8 | 9 | 7 | **7.4** |
| Team | 6 | 7 | 7 | 6 | 6 | 8 | 5 | 7 | 6 | 5 | 9 | 5 | **6.3** |
| Audit Logs | 7 | 8 | 5 | 6 | 8 | 8 | 6 | 7 | 7 | 6 | 9 | 6 | **7.0** |
| Print Detection | 7 | 7 | 7 | 6 | 6 | 8 | 6 | - | 6 | 5 | 9 | 6 | **6.4** |
| CDN Analytics | 7 | 7 | 7 | 6 | 6 | 8 | 6 | - | 6 | 5 | 9 | 6 | **6.4** |
| Compliance | 9 | 8 | 5 | 8 | 9 | 8 | 7 | 9 | 6 | 6 | 10 | 7 | **7.7** |
| Support | 7 | 8 | 7 | 8 | 8 | 8 | 8 | 7 | 7 | - | 9 | 6 | **7.5** |
| Docs | 8 | 8 | 8 | 9 | 9 | 8 | 8 | 8 | 8 | - | 9 | 8 | **8.4** |
| Org Settings | 9 | 8 | 8 | 8 | 8 | 9 | 6 | 8 | 6 | 8 | 9 | 7 | **7.8** |

### Dashboard Overall Score: **7.4/10** (up from 6.5/10 in Dec 2025)

### Score Distribution
- **8-9**: Overview Demo (8.8), Playground (8.8), Image Signing (8.5), Docs (8.4), Overview Real (8.4), API Keys (8.1), Integrations (8.0)
- **7-8**: Org Settings (7.8), Rights (7.7), Compliance (7.7), Support (7.5), Settings (7.5), Webhooks (7.4), Analytics (7.3), Billing (7.2)
- **6-7**: Governance (7.0), Enforcement (7.0), AI Crawlers (7.0), Audit Logs (7.0), Print Detection (6.4), CDN Analytics (6.4), Team (6.3)

---

## Priority Fix Queue

### P0 -- Critical (Enterprise demo blockers)

| # | Issue | Pages Affected | Effort | Impact |
|---|-------|---------------|--------|--------|
| 1 | **Upgrade walls are empty placeholders** -- No feature preview, no screenshots, no value proposition beyond one sentence | Team, Print Detection, CDN Analytics | M | 3 pages score 6.4 instead of 8+ |
| 2 | **Rights empty states are text-only** -- Every sub-tab empty state is just gray `<p>` text with no icon, no CTA, no guidance | Rights (Analytics, Notices, Licensing tabs) | M | Most complex page feels unfinished in empty state |
| 3 | **Pre-filled demo data in Notice form** -- Default values include "OpenAI", specific email, "Encypher Times" case -- would confuse real users | Rights (Notices tab) | S | Could cause accidental submissions |
| 4 | **Hardcoded colors without dark: variants** -- `bg-gray-100 text-gray-800` on Billing, `methodColors`/`tierColors` on Playground, `getComplianceBadgeClass()` on AI Crawlers, `ROLE_CONFIG` avatars on Team, `text-red-700`/`text-blue-700` on Audit Logs, `<textarea>` on Support, invoice badges on Billing, `bg-blue-50`/`bg-yellow-50` on Settings | Billing, Playground, AI Crawlers, Team, Audit Logs, Support, Settings | M | Dark mode contrast failure across 8+ pages |
| 5 | **"Download Compliance Report" is `window.print()`** -- prints full page with sidebar/nav chrome, not a real PDF | Compliance | M | Misleads enterprise evaluators expecting downloadable evidence |
| 6 | **Playground Send Request has no loading feedback** -- no spinner, no text change during 1-3s API call | Playground | S | Developer tool feels broken during use |
| 7 | **Billing `const subscription = null` hardcoded** -- "Manage Billing" button never renders, plan always shows "Free" | Billing | S | Paying customers see wrong tier, cannot manage subscription |

### P1 -- High (Polish items that signal quality)

| # | Issue | Pages Affected | Effort | Impact |
|---|-------|---------------|--------|--------|
| 8 | **Raw `<button>` instead of design system Button** -- 6+ on Rights, 2+ on Analytics, mode toggle on Playground | Rights, Analytics, Playground | M | Inconsistent hover/focus/disabled states |
| 9 | **3 badge implementations on Rights page** -- Design system `Badge`, custom `StatusBadge`, and inline `<span>` with conditional classes | Rights | M | Maintenance debt, visual inconsistency |
| 10 | **API Keys loading state is plain text** -- No skeleton, jarring layout shift | API Keys | S | Noticeable during demos |
| 11 | **`window.confirm()` for API key deletion** -- Browser native dialog, visually inconsistent | API Keys | S | Breaks polish during live demos |
| 12 | **Analytics funnel: Link wrapping button** -- Nested interactive elements (a11y violation) | Analytics | S | Screen reader and keyboard nav issues |
| 13 | **Unicode emoji in CopyPasteSurvivalTester** -- `\u2705`/`\u274C` violates project ASCII-only rule | Playground | S | Rule violation |
| 14 | **No breadcrumbs** -- Flat navigation everywhere except Org Settings "Back to Settings" | All pages | M | Enterprise users expect location awareness |
| 15 | **Governance/Enforcement pages feel sparse** -- Limited onboarding, basic empty states | Governance, Enforcement | M | Below the 8.0 bar for enterprise pages |
| 16 | **Webhooks dark mode card tint** -- Empty state card background doesn't match | Webhooks | S | Visual inconsistency |
| 17 | **Overview decline indicators alarming** -- 92.4% success shown as "Needs attention" | Overview | S | Could concern evaluators |
| 18 | **AI Crawlers empty states lack CTAs** -- 5+ empty text strings with no guidance on how to get data | AI Crawlers | M | New users get no onboarding |
| 19 | **`window.confirm()` used across 4 pages** -- Blocking, non-styleable, visually inconsistent | API Keys, Webhooks, Team (2x) | M | Should be modal confirmation dialog |
| 20 | **Support textarea dark mode bug** -- `<textarea>` missing `bg-background text-foreground`, renders white in dark mode | Support | S | Confirmed visual bug |
| 21 | **Print Detection: "Very High" confidence uses destructive (red) badge** -- Best outcome shown as error color | Print Detection | S | Semantically incorrect |
| 22 | **Settings TOTP secret exposed in plain text** -- Raw `otpauth://` URI visible during 2FA setup, should be behind "Show secret" toggle | Settings | S | Security concern for enterprise evaluators |
| 23 | **Settings zero skeleton loaders** -- ~2500-line file with no loading states, forms flash in with no transition | Settings | M | Layout shift during page load |
| 24 | **Billing invoice badge dark mode** -- `bg-green-100 text-green-800`, `bg-yellow-100 text-yellow-800` etc. with no `dark:` variants | Billing | S | Badges unreadable in dark mode |
| 25 | **Enforcement no pagination** -- All enforcement notices load at once, no pagination UI | Enforcement | M | Will not scale past ~50 records |
| 26 | **Enforcement View/Evidence buttons identical** -- Both render as same style, unclear which does what | Enforcement | S | Action ambiguity |
| 27 | **Settings email change form dark mode** -- `bg-blue-50`, `bg-yellow-50` panels render as bright patches in dark mode | Settings | S | Visual inconsistency |

### P2 -- Medium (Differentiation opportunities)

| # | Issue | Pages Affected | Effort | Impact |
|---|-------|---------------|--------|--------|
| 28 | **Upgrade walls should be mini sales pages** -- Feature preview, screenshots, testimonial, "Talk to Sales" CTA | Team, Print Detection, CDN Analytics | L | Convert upgrade walls from dead-ends to sales funnels |
| 29 | **AI Crawlers lacks interpretation** -- Raw data without "what does this mean?" context | AI Crawlers | M | Enterprise users want insights, not just data |
| 30 | **Audit Logs filter density + `<details>` inconsistency** -- 10+ controls, `<details>` clashes with `<select>` | Audit Logs | M | Collapsible advanced filters, unified dropdown pattern |
| 31 | **Analytics hand-rolled bar chart** -- No axis labels, always 14 days regardless of selected range | Analytics | M | Replace with proper chart library or fix axis/range |
| 32 | **Analytics needs export/share** -- No way to export chart data or share dashboards | Analytics | M | Enterprise reporting requirement |
| 33 | **Rights pagination missing** -- Discovery events capped at 50 with no pagination UI | Rights | S | Data may be hidden |
| 34 | **Centralize duplicate SVG icons** -- `IconApi`, `IconTerminal` etc. copy-pasted between docs + support | Docs, Support | M | DRY violation, maintenance hazard |
| 35 | **Docs: `IconQuote` uses checkmark SVG path** -- Semantic mismatch | Docs | S | Wrong icon |
| 36 | **Compliance hardcoded deadline string** -- "August 2, 2026" is static JSX that will go stale | Compliance | S | Maintenance issue |
| 37 | **Image Signing: no image preview in results** -- Shows placeholder icon instead of signed image thumbnail | Image Signing | S | Has `img.preview` available |
| 38 | **Image Signing: downloadAll may be blocked by browser** -- Multiple sequential `<a>.click()` | Image Signing | M | ZIP bundling would be more reliable |
| 39 | **Playground: duplicate endpoint list rendering** -- Two near-identical blocks for filtered vs unfiltered | Playground | M | Maintenance hazard |
| 40 | **Playground: tour state lost on refresh** -- `localStorage` set but never read on mount | Playground | S | Tour progress lost |
| 41 | **Org Settings: security policies display-only for admin** -- "Contact your administrator" is self-referential | Org Settings | M | Admin should be able to edit |
| 42 | **CDN Analytics: queryKey missing orgId** -- Stale data from previous org shows after org switch | CDN Analytics | S | Data integrity issue |
| 43 | **Integrations: WordPress plugin URL has hardcoded version** -- Download URL will go stale with new releases | Integrations | S | Maintenance issue |
| 44 | **Governance: no empty state for policies list** -- Renders blank when no governance policies exist | Governance | S | Confusing first-run experience |

### P3 -- Low (Nice-to-have refinements)

| # | Issue | Pages Affected | Effort | Impact |
|---|-------|---------------|--------|--------|
| 45 | **Sidebar label truncation** -- "Content Performance" and "Print Leak Detection" long labels | Global Chrome | S | Minor readability in collapsed mode |
| 46 | **Rights "Guide" link styled as raw `<a>`** -- Should use Button or Link component | Rights | S | Interaction inconsistency |
| 47 | **Support FAQ static** -- No search, no dynamic FAQ | Support | M | Low priority unless support volume is high |
| 48 | **Compliance: no celebration at 100%** -- Same checklist renders, no congratulatory moment | Compliance | S | Missed delight opportunity |
| 49 | **Image Signing: quality slider is bare `<input type="range">`** -- Not using design system component | Image Signing | S | Minor visual inconsistency |
| 50 | **Hardcoded hex `#2A87C4` in hover classes** -- Rights template picker, Docs guide cards | Rights, Docs | S | Design system token bypass |

---

## Score Progression vs Dec 2025

| Metric | Dec 2025 | Mar 2026 | Delta |
|--------|----------|----------|-------|
| Dashboard Overall | 6.5/10 | 7.4/10 | **+0.9** |
| Overview | ~6.5 | 8.8 (demo) / 8.4 (real) | **+2.0** |
| Playground | Broken | 9.4 | **Fixed + polished** |
| Org Settings | Crash | 7.8 | **Fixed** |
| Contact page | 404 | N/A (marketing) | **Fixed** |
| Mobile blank | Critical | Not re-tested | Needs verification |

### Key Improvements Since Dec 2025
1. Playground completely rebuilt (was crashing, now 9.4/10)
2. Overview redesigned with custom icons, animations, real-time polling, demo mode
3. Org Settings crash fixed
4. Dark mode largely functional across all pages
5. Custom provenance icons replace generic Lucide on Overview
6. Onboarding checklist with auto-completion
7. EU AI Act Compliance page is enterprise-ready
8. Documentation page covers full product surface

### Remaining Gaps
1. Upgrade walls (Team, Print Detection, CDN Analytics) are the weakest pages at 6.4/10
2. **Billing subscription bug** -- `const subscription = null` hardcoded, suppresses key CTA
3. Analytics and AI Crawlers lack actionability and interpretation
4. No breadcrumbs anywhere
5. Dark mode has scattered hardcoded color issues across 8+ pages (Billing, Settings, Playground, AI Crawlers, Team, Audit Logs, Support, Settings)
6. Governance and Enforcement need pagination, empty states, and more polish
7. Settings has zero loading states and exposes TOTP secret in plain text

---

## Recommendations for 10/10

To reach 10/10 enterprise demo readiness:

1. **Transform upgrade walls into feature marketing pages** -- Show what the feature does with screenshots, a feature list, and "Talk to Sales" CTA. This single change lifts 3 pages from 6.4 to 8+.

2. **Add breadcrumbs** -- Every page should show its location in the hierarchy. This is table stakes for enterprise SaaS.

3. **Make Analytics actionable** -- Add "insights" cards that interpret the data ("Your content was accessed by 12 AI crawlers this week, 3 new ones"). Add export/share.

4. **Polish Governance and Enforcement** -- These are differentiation features. They should feel as polished as Rights and Compliance.

5. **Audit Logs filter UX** -- Collapsible advanced filters, fix the "Save current view" overflow, add pagination.

6. **Dark mode sweep** -- Find and fix all hardcoded gray/white classes without dark: variants.

---

---

## Appendix: Code-Level Findings

### Cross-Page Pattern Analysis (from source code review)

| Dimension | Analytics | API Keys | Rights | AI Crawlers | Playground | Compliance | Image Signing | Billing | Settings | Governance | Enforcement | Integrations |
|-----------|-----------|----------|--------|-------------|------------|------------|---------------|---------|----------|------------|-------------|--------------|
| Loading states | Strong (3 skeletons) | Weak (text only) | Adequate (shimmer) | Strong (3 skeletons) | None (no spinner on Send) | Spinner only | Spinner on sign button | None | None (zero skeletons in ~2500 lines) | None | None | None needed (static) |
| Empty states | Inline | Strong (icon+CTA) | Weak (text only) | Weak (text only) | None (blank response) | None (renders nothing) | Drop zone IS empty state | Free tier path | N/A (always has data) | Missing (policies blank) | Shared EmptyState | N/A (always has cards) |
| Dark mode | Good w/ slips | Good w/ slips | Best coverage | Fails (badge classes) | Fails (method/tier colors) | Best coverage | Good | Fails (invoice badges, plan cards) | Fails (email form panels) | Good | Good | Good |
| Button consistency | Partial | Good | Poor (6+ raw) | Good | Partial (mode toggle) | Good | Good (Lucide) | Good | Good | Good | Poor (View/Evidence identical) | Good |
| Iconography | Inline SVGs | Inline SVGs | Inline SVGs | Inline SVGs | Inline SVGs | Zero icons | Lucide (only page) | Lucide | Lucide | Inline SVGs | Inline SVGs | Integration logos |
| Critical issue | Link-in-button a11y | window.confirm() | Demo data in form | Badge dark mode | No loading feedback | window.print() as PDF | downloadAll popup flood | subscription=null bug | TOTP secret exposed | No policies empty state | No pagination | Hardcoded version URL |

### Design System Adoption Gaps

1. **Button component**: Multiple pages bypass `Button` for raw `<button>` with Tailwind classes -- loses consistent hover/focus/disabled/loading states (Rights 6+, Analytics 2+, Playground mode toggle)
2. **Badge component**: Rights page has 3 implementations; should standardize on design system `Badge` with variants
3. **Input component**: API Keys modal textarea and Image Signing quality slider bypass design system components
4. **Color tokens**: Several pages use `text-slate-*` or `text-gray-*` instead of semantic tokens (`text-foreground`, `text-muted-foreground`). Playground `methodColors`/`tierColors` are fully hardcoded without `dark:` variants
5. **Hardcoded hex values**: `#2A87C4` in Rights template picker, `CRAWLER_COLORS`/`COMPANY_COLORS` in AI Crawlers
6. **Iconography inconsistency**: Image Signing uses Lucide, Compliance uses zero icons, all others use inline SVGs -- no consistent approach

### Accessibility Issues

1. **Nested interactive elements**: Analytics page wraps `<button>` inside `<Link>` (a11y violation -- screen readers, keyboard nav)
2. **window.confirm()**: API Keys uses browser native dialog, no keyboard trap management
3. **Toast-only errors**: Most pages surface errors only via `toast.error()` -- if tab is backgrounded, user misses the error and page looks silently broken

### Code Quality Flags

1. **Unicode emoji**: CopyPasteSurvivalTester uses `\u2705`/`\u274C` (violates project ASCII-only rule)
2. **Duplicate rendering**: Playground endpoint list has two near-identical rendering blocks (filtered vs unfiltered)
3. **window.print() as "Download"**: Compliance page prints full dashboard chrome, not a scoped PDF
4. **window.confirm() used in 4 pages**: API Keys, Webhooks, Team (x2) -- should be modal dialogs
5. **Duplicate SVG icons**: `IconApi`, `IconTerminal`, `IconPackage`, `IconStatus` copy-pasted between docs + support
6. **CDN Analytics queryKey missing orgId**: Stale data from previous org shows after org switch (cache bug)
7. **Print Detection error masking**: `documentsQuery.isError` shows empty-state message instead of error
8. **`IconQuote` semantic mismatch**: Uses checkmark SVG path (`M9 12l2 2 4-4m6 2a9 9 0 11-18 0`), not a quote icon
9. **Iconography inconsistency across dashboard**: Image Signing uses Lucide, Org Settings uses Lucide, all other pages use inline SVGs, Compliance uses zero icons
10. **TOTP secret exposure**: Settings page exposes raw `otpauth://` URI in plain text during 2FA setup -- should be behind "Show secret" toggle
11. **Billing subscription hardcoded null**: `const subscription = null` on line ~71 of billing page means "Manage Billing" button never renders and plan always shows "Free"
12. **Enforcement no pagination**: All enforcement notices load without pagination -- performance and usability issue at scale

### Loading State Inconsistency

| Pattern | Pages |
|---------|-------|
| Good skeletons | Analytics (3 components), AI Crawlers (3 components), Webhooks |
| Spinner only | Compliance, CDN Analytics (`<Loader>` component) |
| Plain text only | API Keys, Team, Audit Logs, Print Detection, Org Settings |
| None at all | Settings (~2500-line file, zero skeleton loaders), Billing, Governance, Enforcement |
| None needed | Docs, Support (static), Image Signing (form), Integrations (static cards) |

### Empty State Quality Spectrum

| Quality | Pattern | Pages |
|---------|---------|-------|
| Strong | Icon + heading + description + CTA | API Keys, Webhooks, CDN Analytics, Enforcement |
| Adequate | Icon + heading + description (no CTA) | Print Detection, Team (upgrade wall) |
| Weak | Plain centered text only | Rights (all tabs), AI Crawlers (5+ strings), Audit Logs, Team members |
| Absent | Renders nothing / blank | Compliance (empty items), Playground (response panel), Governance (policies list) |

---

*Audit completed by TEAM_262 on March 19-20, 2026. 50 prioritized fixes (P0: 7, P1: 20, P2: 17, P3: 6). Next audit recommended after P0/P1 fixes are implemented.*
