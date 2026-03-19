# PRD: Dashboard Overview -- From 7.4 to 10/10

**Status:** Active
**Current Goal:** Phase 2 items remaining
**Team:** TEAM_262
**Date:** March 19, 2026

## Overview
Comprehensive WBS to elevate the publisher provenance dashboard from 7.4/10 to 10/10. Primary audience: publisher GCs (ICP 1A) and platform distribution partners (ICP 1C). Every design decision tested against: "Would this help close a publisher coalition deal in Q2?"

## Phase 1: Demo-Ready (P0) -- COMPLETE

### WBS 1.1 -- Trend Indicators on All Applicable Cards
- [x] 1.1.1 -- API Calls: trend badge vs prior 30 days -- tsc
- [x] 1.1.2 -- Documents Signed: trend indicator replacing "X articles protected" -- tsc
- [x] 1.1.3 -- Verifications: trend badge vs prior 30 days -- tsc
- [x] 1.1.4 -- Success Rate: stability indicator (Excellent/Consistent, Up from X%) -- tsc
- [x] 1.1.5 -- Trend color system: green (up), amber (flat/steady), red (down) -- tsc
- [x] 1.1.6 -- Zero-base edge case: "+X new" instead of infinity% -- tsc

### WBS 2.1 -- Verifications Progress Visualization
- [x] 2.1.1 -- Progress ring showing X/500 verifications -- tsc
- [x] 2.1.2 -- State transitions: zero / early (1-99) / momentum (100-499) / qualified (500+) -- tsc
- [ ] 2.1.3 -- Milestone celebrations at 10, 50, 100, 250, 500 (future)

### WBS 5.1 -- Type Scale Revision
- [x] 5.1.1 -- Greeting headline: text-3xl lg:text-4xl tracking-tight -- tsc
- [x] 5.1.2 -- Section headers: uppercase tracking-tight font-semibold -- tsc
- [x] 5.1.3 -- Consistent card sub-labels -- tsc

### WBS 7.1 -- Demo Mode (Highest Leverage)
- [x] 7.1.1 -- Demo data provider with realistic publisher data (60 days in) -- tsc
- [x] 7.1.2 -- Demo mode banner ("Demo Mode -- Sample Data") -- tsc
- [x] 7.1.3 -- Demo mode toggle via ?demo=true URL param -- tsc
- [x] 7.1.4 -- Shows post-onboarding layout (hides onboarding) -- tsc

## Phase 1.5: Audit Feedback Implementation -- COMPLETE

### Metric Card Clickability (P1)
- [x] API Calls -> /analytics -- tsc
- [x] Documents Signed -> /analytics -- tsc
- [x] Verifications -> /analytics (early/momentum) or /rights (qualified) -- tsc
- [x] Success Rate -> /analytics -- tsc
- [x] Hover: border-blue-ncs/30 transition-all on all cards -- tsc

### Sparkline on Documents Signed (P2 quick win)
- [x] Documents Signed sparkline with Delft Blue color -- tsc
- [x] Demo data: DEMO_DOCS_SPARKLINE with steady growth curve -- tsc
- [x] Real data: docsSparklineQuery for documents_signed time series -- tsc

### Recommended Next Action Banner (P1)
- [x] Contextual single-line banner between greeting and metrics -- tsc
- [x] 4 states: no docs -> no verifications -> progress % -> eligible -- tsc
- [x] Links to appropriate action page per state -- tsc

### Content Protection Funnel (P1)
- [x] Three-step visual funnel: Signed -> Verified -> Notice Ready -- tsc
- [x] Step indicators with checkmarks (done) or numbers (pending) -- tsc
- [x] Each step clickable, linking to respective page -- tsc
- [x] Connecting dashed lines between steps -- tsc
- [x] Progress bar for formal notice when not yet qualified -- tsc

### Recent Activity Feed (P1)
- [x] Activity feed card with 6 recent events -- tsc
- [x] Color-coded left border per event type (sign=blue, verify=green, api=gray) -- tsc
- [x] "View all activity" link to audit logs -- tsc
- [x] Demo data with 8 realistic events -- tsc
- [x] Real-time polling via refetchInterval (30s) with discovery events API -- tsc
- [x] Live indicator badge (green pulsing dot + "Live" label) -- tsc
- [x] Staggered slide-in-right entrance animation per event row -- tsc

### Micro-Interactions (P2)
- [x] Card hover states: hover:border-blue-ncs/30 hover:shadow-md -- tsc
- [x] Progress ring: 600ms ease-out transition on stroke-dashoffset -- tsc
- [x] Progress bar: transition-all duration-700 on width -- tsc
- [x] Staggered card entrance: fade-in-up with 80ms delay per card -- tsc
- [x] Count-up animation: numbers animate from 0 to target with ease-out cubic -- tsc
- [x] Sparkline draw animation: stroke-dashoffset 1.2s CSS animation -- tsc
- [x] Card hover scale: group-hover:scale-[1.02] on metric cards -- tsc
- [x] Activity feed row slide-in-right with 60ms stagger -- tsc

## Phase 2: Activation-Optimized (P1) -- REMAINING

### WBS 3.1 -- Quick Start Auto-Dismissal
- [ ] 3.1.1 -- Hide when rollout >= 4/6
- [ ] 3.1.2 -- Manual dismiss (persists)
- [ ] 3.1.3 -- Restore in Settings

### WBS 3.2 -- Post-Onboarding Dashboard State
- [ ] 3.2.1 -- Onboarded layout (ops summary replaces setup)
- [ ] 3.2.2 -- Rollout collapses to single-line "Setup complete" banner
- [ ] 3.2.3 -- Both states designed as first-class layouts

### WBS 10.2 -- Recommended Next Action (advanced)
- [ ] 10.2.1 -- Dismissable per action (next recommendation surfaces)
- [ ] 10.2.2 -- Decision tree with formal notice served state

## Phase 3: Differentiation & Polish (P2) -- REMAINING

### WBS 1.3 -- Time Window Selector
- [ ] 1.3.1 -- "7d | 30d | 90d" toggle above metric cards
- [ ] 1.3.2 -- Persist in localStorage
- [ ] 1.3.3 -- Updates all cards/sparklines

### WBS 4.1 -- C2PA Badge Enhancement
- [ ] 4.1.1 -- Clickable badge -> modal with C2PA details
- [ ] 4.1.2 -- Hover tooltip
- [ ] 4.1.3 -- No visual weight increase

### WBS 6.1 -- Sidebar Reorganization
- [ ] 6.1.1 -- Rename "Rights" to "Rights Management"
- [ ] 6.1.2 -- Move "Print Leak Detection" to INSIGHTS
- [ ] 6.1.3 -- Move "Docs" to footer or rename INSIGHTS section
- [ ] 6.1.4 -- Collapsible sidebar sections

### WBS 6.2 -- Quick Links Deduplication
- [ ] 6.2.1 -- Quick Links hide when rollout = 6/6

### WBS 7.2 -- ICP-Specific Demo Overlays
- [ ] 7.2.1 -- Publisher GC overlay (Legal Status card)
- [ ] 7.2.2 -- Platform partner overlay (Network card)
- [ ] 7.2.3 -- Enterprise overlay (Compliance card)

### WBS 9.1 -- Custom Iconography -- COMPLETE
- [x] 9.1.1 -- 7 custom provenance SVG icons (IconSign, IconVerify, IconProvenance, IconSignedDoc, IconFormalNotice, IconContentProtection, IconApiKey) -- tsc
- [x] 9.1.2 -- Lucide kept for generic UI (arrows, plus, book, link, chart) -- tsc

## Success Criteria
- [x] Demo account convincingly shows 60-day publisher with growth trajectory
- [x] All metric cards have contextual sub-labels (no card restates its own number)
- [x] Verification progress ring fills proportionally to 500 threshold
- [x] All metric cards clickable to detail pages
- [x] Activity feed shows recent events in demo mode
- [x] Content protection funnel shows three-step journey
- [x] Recommended next action contextually adapts to account state
- [ ] Post-onboarding layout feels intentional
- [x] Screenshot test: looks unmistakably like a provenance product (custom icons + domain-specific visual language)
- [x] Activity feed polls for real-time updates (30s interval)
- [x] Metric cards animate on load (count-up, sparkline draw, staggered entrance)
- [x] Custom provenance iconography replaces generic Lucide icons

## Completion Notes
- Build passes clean (next build)
- Demo mode activated via ?demo=true URL param
- All P0, P1, and P2 items from audit feedback implemented
- Custom icons: IconSign (quill), IconVerify (magnifier+check), IconProvenance (shield+chain), IconSignedDoc (doc+seal), IconFormalNotice (gavel), IconContentProtection (shield+lines), IconApiKey (key+circuit)
- Real-time: activity feed uses getDiscoveryEvents with 30s refetchInterval + refetchOnWindowFocus
- Animations: 3 new keyframes (fade-in-up, count-up, slide-in-right) + sparkline draw CSS animation
