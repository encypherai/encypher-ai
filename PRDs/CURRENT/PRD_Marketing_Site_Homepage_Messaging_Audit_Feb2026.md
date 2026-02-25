# PRD: Marketing Site Homepage Messaging Audit (Feb 2026)

**Status:** In Progress  
**Current Goal:** Align homepage messaging and structure with proof-first, publisher-first positioning.  

## Overview
The homepage messaging must shift from generic AI licensing outcomes to Encypher's core differentiation: machine-readable cryptographic proof embedded in content that survives distribution. This PRD applies the audit recommendations to hero, flow, standards framing, differentiation messaging, and site-wide tagline touchpoints.

## Objectives
- Replace outcome-first homepage messaging with differentiation-first proof messaging.
- Reframe homepage as publisher-first while keeping AI Labs as secondary navigation.
- Remove inaccurate or premature homepage claims and align trust framing.
- Add explicit cryptographic-vs-detection differentiation and content-theft day-one value.
- Update site-wide tagline references to "Machine-Readable Rights for Your Content."

## Tasks
- [x] 1.0 Homepage hero + CTA positioning update
  - [x] 1.1 Replace hero headline/subhead with proof-first copy
  - [x] 1.2 Update CTA pair to "See It Work" and "How It's Different"
- [x] 2.0 Homepage narrative restructuring
  - [x] 2.1 Shift value section to publisher-first framing
  - [x] 2.2 Add "Not AI Detection. Cryptographic Proof." section
  - [x] 2.3 Restructure "How It Works" to Mark / Track / Own
  - [x] 2.4 Add content-theft detection section with Chrome extension CTA
  - [x] 2.5 Add lock analogy capability comparison table
- [x] 3.0 Standards/trust framing corrections
  - [x] 3.1 Update C2PA logo wall heading to standards-membership framing
  - [x] 3.2 Remove homepage FAQ JSON-LD usage after FAQ removal on homepage
- [x] 4.0 Site-wide tagline alignment
  - [x] 4.1 Update footer tagline text
  - [x] 4.2 Update metadata/SEO title strings away from legacy tagline
- [ ] 5.0 Verification
  - [x] 5.1 Targeted lint for changed files — ✅ next lint
  - [ ] 5.2 Marketing-site Jest suite — ⚠ pre-existing failure in `src/lib/blogMarkdown.test.ts` (ESM parsing of `remark`)
  - [ ] 5.3 Playwright homepage spec — ⚠ local environment blocked by stale port-3000 process and root-owned `.next` artifacts
  - [ ] 5.4 Puppeteer manual homepage verification — ⚠ blocked by same local server mismatch

## Success Criteria
- Homepage hero and section flow match proof-first and publisher-first narrative.
- Legacy homepage claims/messages removed from homepage implementation.
- C2PA members header uses accurate standards framing.
- Footer and metadata no longer use "Content Intelligence Infrastructure".
- Validation checks are run and blockers documented if environment issues prevent completion.

## Completion Notes
- Implemented in:
  - `apps/marketing-site/src/app/page.tsx`
  - `apps/marketing-site/src/components/solutions/standards-compliance.tsx`
  - `apps/marketing-site/src/components/layout/footer.tsx`
  - `apps/marketing-site/src/app/metadata.ts`
  - `apps/marketing-site/src/lib/seo.ts`
  - `apps/marketing-site/e2e/homepage-messaging.spec.ts`
- Local runtime verification is currently blocked by:
  - Root-owned files under `apps/marketing-site/.next` (`.next/server/_error.js` owner: root)
  - Existing process bound to port 3000 serving stale content
