# TEAM_225: Publisher Value Proof Dashboard

**PRD**: PRDs/CURRENT/PRD_Publisher_Value_Proof_Dashboard.md
**Status**: Substantially Complete -- backend endpoints live, frontend redesigned, 3 items remaining

## Session Accomplishments

### Frontend Changes (apps/dashboard/)

**Task 7.0 - Nav Reframing:**
- `DashboardLayout.tsx:191-192` -- "Analytics" -> "Content Performance", "AI Crawlers" -> "Provenance Activity"

**Task 4.0 - AI Crawlers Honest Copy:**
- `ai-crawlers/page.tsx:221-260` -- Page title -> "Provenance Activity", amber capability callout added
  explaining what the data IS (provenance checks) and IS NOT (raw crawler traffic), Cloudflare waitlist CTA

**Task 2.0 - Analytics Page Value Accumulation Timeline:**
- `analytics/page.tsx` -- FULL REWRITE
  - Primary view: 6-stage FunnelStage timeline (SIGNED -> VERIFIED -> SPREAD -> NOTICE READY -> LICENSING -> EARNINGS)
  - SPREAD stage shows "coming soon" placeholder
  - NOTICE READY shows CTA when verifications >= 500
  - EARNINGS pulls `apiClient.getCoalitionEarnings()`
  - API Health metrics moved to collapsible section (default closed)
  - Notice progress bar (X / 500 verifications)
  - Right column: "This Period" summary card + Notice Progress card + legend

**Task 1.0 - Home Page Value Proof Card:**
- `page.tsx:99-178` -- `ValueProofCard` component added above `OnboardingChecklist`
  - Shows: content protected count, external verifications, Formal Notice progress bar %
  - CTA: "View Content Performance" link to /analytics
- Quick Links updated: "Analytics" -> "Content Performance"

### Backend Changes (enterprise_api/)

**Task 3.0 - Content Spread Endpoint:**
- `routers/rights.py` -- Added `GET /api/v1/rights/analytics/content-spread`
  - Queries `ContentDetectionEvent.detected_on_domain` (field already existed)
  - Returns: total_external_detections, unique_external_domains, domains[], documents[]
  - Gated: Enterprise tier or `attribution_analytics` add-on

**Task 5.0 - Progression Status Endpoint:**
- `routers/onboarding.py` -- Added `GET /api/v1/onboarding/progression-status`
  - Returns 6-stage journey: Sign/Accumulate/Document/Notice Ready/Negotiating/Earnings
  - Current stage computed from documents_signed, total_verifications, coalition_active, earnings
  - Threshold: 500 verifications to qualify for Formal Notice

**Task 8.0 - Public Coalition Stats Endpoint:**
- `routers/coalition.py` -- Added `GET /api/v1/coalition/public/stats` (no auth)
  - Returns: coalition_members, total_signed_documents, as_of
  - Uses `get_db` directly (no auth dependency)

### API Client (apps/dashboard/src/lib/api.ts)
- `getProgressionStatus(accessToken)` -- new
- `getContentSpread(accessToken, days)` -- new
- `getPublicCoalitionStats()` -- new (no auth)

### Docs/Artifacts Updated
- `enterprise_api/README.md` -- Added 3 new endpoints to endpoint tables
- `sdk/openapi.public.json` -- Added 3 new endpoint definitions

## Test Results
- `uv run pytest tests/ -q`: **1234 passed**, 58 skipped, 17 deselected
- `npx tsc --noEmit`: **clean** (no errors)

## Remaining Tasks
- [ ] 3.3: Content Spread UI panel in analytics page (SPREAD stage shows placeholder now)
- [ ] 5.3: Stage-specific email/notification triggers when publisher reaches Notice Ready
- [ ] 6.4: Puppeteer verification of nav rename
- [ ] 8.1/8.3: Marketing site coalition counter component (new UI in marketing-site/)
- [ ] 6.0 (Shareable Provenance Report): Not yet implemented -- full task remaining

## Marketing Site Copy Changes (Session 2 -- Continuation)

**Opus analysis** (agent ae041a5b758278d25) completed. User approved revised strategy with constraint:
- No revenue share percentages publicly (60/40, 80/20 reserved for 1:1 conversations)
- "Switzerland" positioning: neutral infrastructure, not adversarial to AI companies
- Laymen-friendly language while keeping technical details accessible

**Implemented changes:**

`apps/marketing-site/src/app/page.tsx` (homepage):
- H1: "Cryptographic Proof for the AI Economy" -> "The Licensing Infrastructure for AI Content"
- Sub-headline: neutral "Publishers need to get paid / AI companies need proof" framing
- "For AI Labs" card: new H4 "License Content at Scale. Prove You Did It Right.", Licensed Content Mark bullet
- "Why Encypher" section: renamed cards, added Visa/Stripe "Neutral Infrastructure" card
- Final CTA: "The AI content economy is being built right now" -- coalition FOMO framing

`apps/marketing-site/src/app/solutions/publishers/page.tsx`:
- Added "Legal Reality" section: $30K vs $150K statutory damages callout (publisher-page-only)
- Added "Bridge Value" section: 3 cards (protected corpus, evidence accumulates, content spread analytics)
- Updated "How It Works" header: "Protection From Day One" with competitive differentiation framing

`apps/marketing-site/src/app/solutions/ai-companies/page.tsx`:
- H1: "License Content at Scale. Prove You Did It Right."
- Sub: coalition access + compliance + trust signal framing
- Value props: expanded to 4 cards, added "Licensed Content Mark" card (Award icon)
- "How It Works": 3 steps now cover coalition access, provenance verification, compliance+intelligence
- Header: "One Integration. Three Outcomes."

`apps/marketing-site/src/app/publisher-demo/components/sections/Section6Coalition.tsx`:
- Added "Bridge Value" box above "Founding Coalition Members" section
- 3 sub-items: protected corpus, evidence accumulates, content spread analytics
- Blue bg to visually differentiate from the existing slate-50 box

## Persona Alignment Audit (Session 3 -- Per-User-Story Subagents)

3 Explore agents run in parallel against publisher-customer-stories.md personas. Key findings implemented:

**Maya (small publisher) -- CRITICAL fixes applied:**
- Added "No Engineering Required" section to `/solutions/publishers` (Ghost/Substack/WordPress, 4-step setup, "20 min")
- Overhauled "How It Works" accordion: Step 0 = archive signing, Step 2 = dashboard free-to-paid trigger, Bonus = Quote Integrity

**Alex (midsized publisher) -- CRITICAL fixes applied:**
- How It Works Step 0: explicit archive signing story ("500,000 articles in an overnight job")
- How It Works Step 2: "See who's using your content" -- free dashboard + $299/mo analytics upgrade path
- Quote Integrity added to How It Works Bonus step

**CMG (large enterprise) -- CRITICAL fixes applied:**
- `solutions/enterprises/page.tsx`: BYOK added to Layer 1 Compliance list
- New "BYOK: Your Keys Stay in Your Infrastructure" section (3-stat card + explanation)
- New "Multi-Organization Architecture" section (per-org controls + enterprise API scale)

**AI Company (Meridian) -- New user story added:**
- `docs/user-stories/publisher-customer-stories.md`: Full 7-phase user story written
- Entry via formal notice received (not marketing campaign)
- Journey: evaluation -> coalition access -> EU AI Act compliance -> Verified Sources product launch -> performance intelligence
- Cross-persona table updated with AI company column

**Still pending from audit (lower priority, separate session):**
- [x] API rate limits / SLA section on platform page (CMG FIX #3) -- DONE: 4-card developer section (API Specs, REST API, Integrations, Docs); rate limits (1K/10K req/min), batch size (10K docs/req), 99.95% uptime SLA, idempotency; also fixed revenue share percentage violation in coalition licensing capability card
- [ ] Attribution Analytics free-to-paid callout on pricing page (Maya FIX #3)

## Session 4 -- /try Live Demo + Mobile Polish (TEAM_225 continuation)

### /try page created (apps/marketing-site/src/app/try/page.tsx)
- 3-step interactive demo: Sign -> Verify flow, no account required
- Stage machine: input | signing | signed | verifying | verified | tampered | unsigned | error
- Sample text: Stanford/Nature AI detection article (3 realistic sentences)
- Signed state: "+{n} invisible chars" badge + Copy button, single row on mobile
- Verified state: green banner, signer/timestamp/standard/integrity table, "aha" paragraph
- CTAs: "Get Started Free" + "See the Full Publisher Story" (flex-col on mobile, full-width)
- Tamper detection FIX: `effectivelyTampered = !valid && found` -- API returns valid:false,
  tampered:false, embeddings_found:1 for modified text; old logic fell to `error` state
- Mobile badge fix: badge text shortened to "+N invisible chars" (was wrapping on 390px)

### Puppeteer verification results
- [x] 6.4 (repurposed): /try page -- desktop initial, signed, verified states all pass
- [x] Mobile (390px): initial, signed, verified, CTAs, hamburger nav all pass
- [x] Tamper detection API test: direct fetch confirms stage='tampered' with fix applied
- [x] Navbar Platform link visible on desktop and in mobile hamburger
- [x] Auth buttons: Sign In (ghost) + Get Started (primary filled)
- [x] Verified result table: Signed by / Signed at / Standard / Content integrity all render

### Remaining Tasks (product work)
- [ ] 3.3: Content Spread UI panel in analytics page (SPREAD stage shows placeholder now)
- [ ] 5.3: Stage-specific email/notification triggers when publisher reaches Notice Ready
- [ ] 8.1/8.3: Marketing site coalition counter component (uses GET /api/v1/coalition/public/stats)
- [ ] 6.0 (Shareable Provenance Report): Not yet implemented -- full task remaining
- [ ] Attribution Analytics free-to-paid callout on pricing page (Maya FIX #3)

## Suggested Commit Message (Updated)
```
feat(marketing): Switzerland positioning -- neutral AI content infrastructure framing (TEAM_225)

Homepage:
- H1: "The Licensing Infrastructure for AI Content" (was: "Cryptographic Proof for the AI Economy")
- Sub: neutral publishers + AI companies both-sides framing
- "For AI Labs" card: "License Content at Scale. Prove You Did It Right." + Licensed Content Mark
- "Why Encypher": "Neutral Infrastructure" (Visa/Stripe analogy), plain-English card text
- Final CTA: coalition FOMO framing

/solutions/publishers:
- New "Legal Reality" section: $30K innocent vs $150K willful infringement (publisher-page-only)
- New "Bridge Value" section: protected corpus, evidence package, content spread -- pre-revenue value
- "How It Works" header: "Protection From Day One" + competitive differentiation framing

/solutions/ai-companies:
- H1: "License Content at Scale. Prove You Did It Right."
- Value props: 4 cards, new "Licensed Content Mark" (trust badge for AI company GTM)
- "How It Works": coalition access -> provenance verification -> compliance + intelligence

Publisher demo Section 6:
- Added bridge value box: what publishers get during the 12-24 month pre-revenue period
```
