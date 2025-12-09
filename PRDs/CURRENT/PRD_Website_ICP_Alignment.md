# PRD: Website ICP Alignment & Messaging Update

**Status:** Complete  
**Current Goal:** Align website messaging and UX with updated ICP framework  
**Owner:** Marketing / Product  
**Created:** 2025-11-30  
**Team:** TEAM_001

---

## Overview

UX audit conducted by embodying the two primary ICPs (Eleanor - Publisher Strategist, Kenji - AI Platform Architect) revealed critical gaps between the ICP framework v2.0 messaging and the current website implementation. The homepage favors publishers while leaving AI Labs with a broken path, and several messaging elements contradict the updated ICP guidelines.

---

## Objectives

1. Fix critical broken links blocking AI Labs conversion path
2. Align homepage messaging with ICP v2.0 guidelines (remove deprecated messaging)
3. Create parity between Publisher and AI Labs user journeys
4. Emphasize collaborative C2PA positioning (not adversarial)
5. Improve discoverability of demo pages

---

## Success Criteria

- [ ] Zero 404 errors on any CTA path
- [ ] Both ICPs can reach relevant demo page within 2 clicks
- [ ] Homepage messaging matches ICP v2.0 approved language
- [ ] AI Labs messaging emphasizes "building WITH" not "against"
- [ ] Pricing page clearly communicates value for both personas

---

## Tasks

### 1.0 Critical Bug Fixes

- [x] **1.1 ~~Fix /solutions/ai-labs 404~~** — RESOLVED
  - Page exists at `/solutions/ai-companies` (not `/solutions/ai-labs`)
  - Homepage CTA correctly links to `/solutions/ai-companies`
  - **Status:** No bug — path was misidentified during audit

- [x] **1.2 Add "Demo" to main navigation**
  - Added to Solutions dropdown with separator
  - Added to mobile navigation

### 2.0 Homepage Messaging Updates

- [x] **2.1 Update hero headline**
  - **Current:** "Turn Content Intelligence Into Market Advantage"
  - **Suggested:** "Cryptographic Proof for the AI Economy"
  - **Reason:** Current headline is abstract; doesn't communicate what product does

- [x] **2.2 Update hero subtext for parity**
  - **Current:** "AI Labs: See how your models perform in the wild. Publishers: Transform content theft into revenue."
  - **Suggested:** "Publishers: Transform unmarked content into provably owned assets. AI Labs: Performance Intelligence on your models across the internet."
  - **Reason:** Current copy gives publishers emotional hook, AI Labs get vague technical statement. "Content theft" implies AI companies are adversaries.

- [x] **2.3 Remove deprecated messaging from "For Publishers" card**
  - **Remove:** "Mathematical certainty vs. 26% accuracy detection"
  - **Remove:** "Transform $14M in legal costs into $20M+ in licensing revenue"
  - **Replace with:** 
    - "Cryptographic watermarking that survives copy-paste and scraping"
    - "Serve formal notice to AI companies with mathematical proof"
    - "Enable licensing frameworks that didn't exist before"
  - **Reason:** ICP v2.0 explicitly marks these as REMOVED messaging (lines 70-72)

- [x] **2.4 Update "For AI Labs" card messaging**
  - **Current:** "Track every output. Optimize every parameter..."
  - **Add:** Reference to C2PA collaboration and OpenAI membership
  - **Add:** "Building infrastructure WITH the AI industry"
  - **Reason:** ICP v2.0 emphasizes collaborative framing, not just features

### 3.0 Create AI Labs Solution Page

- [x] **3.1 ~~Create `/solutions/ai-labs` page~~** — Page exists at `/solutions/ai-companies`
  - **Headline:** "Performance Intelligence + Publisher Compatibility"
  - **Subtext:** "We're building text provenance standards WITH you through C2PA. One integration covers the entire publisher ecosystem."
  - Structure to mirror publisher page with AI-focused content

- [x] **3.2 Key messaging blocks for AI Labs page**
  - **Dual Value Prop Focus:**
    1. **Performance Intelligence** — Real-world engagement data on how models perform across the internet
    2. **Regulatory Compliance** — EU AI Act, China Watermarking Mandate, C2PA standard
  - **Problem statement:** "You spend $2.7B per model with zero visibility into real-world performance"
  - **Supporting props:** Publisher ecosystem compatibility, standards collaboration
  - **Reason:** AI Labs persona needs both R&D optimization AND compliance infrastructure

- [x] **3.4 Add ICP-specific pricing section below demo**
  - After the interactive demo, include a condensed pricing section
  - For AI Labs: Show "Custom Enterprise Licensing" with key features
  - For Publishers: Show tier cards (Free → Enterprise) with revenue share
  - Include "Schedule Technical Evaluation" / "Contact Sales" CTA
  - **Reason:** Reduces friction—users see value then immediately see how to buy

- [x] **3.3 Embed AI demo or link prominently** — Already embedded via iframe
  - Add interactive demo section (like publisher page has)
  - Or prominent "See Interactive Demo" CTA linking to `/ai-demo`

### 4.0 Pricing Page Refinements

- [x] **4.1 Update AI Labs tab headline**
  - **Current:** "Google Analytics for AI" — KEPT (tested well)
  - **Added:** C2PA collaboration messaging in subheadline
  - **Implementation:** Updated `ICP_VALUE_PROPS['ai-labs'].subheadline` in pricing page

- [x] **4.2 Ensure "For AI Labs" footer link works**
  - Footer already links to `/solutions/ai-companies` which is correct

### 5.0 Content Tone Audit

- [x] **5.1 Remove/soften adversarial language site-wide**
  - Removed "$5B+ active claims" from AI demo → replaced with "growing coalition"
  - Updated SEO metadata to remove "litigation" framing
  - Note: `/ai-copyright-infringement` page kept as-is (SEO landing page)

- [x] **5.2 Add C2PA collaboration messaging**
  - Homepage: Added "Building standards WITH OpenAI, Google, Adobe through C2PA"
  - AI Companies page: Added "OpenAI is a member" in hero
  - Pricing page: Added C2PA collaboration in AI Labs subheadline

### 6.0 Navigation & Information Architecture

- [x] **6.1 Solutions dropdown structure**
  - Added demos section to Solutions dropdown (desktop + mobile)
  - Structure: Publishers → AI Companies → Enterprises → [Demos] → Publisher Demo → AI Labs Demo

---

## ICP Messaging Reference (from v2.0)

### Eleanor (Publisher) - APPROVED Messaging
- "Transform unmarked content into provably owned assets"
- "Cryptographic watermarking that survives copy-paste and scraping"
- "Serve formal notice to AI companies with mathematical proof"
- "Co-Chair of C2PA Text Provenance Task Force"
- "Enable licensing frameworks that didn't exist before"

### Eleanor - REMOVED Messaging (DO NOT USE)
- ❌ "Transform $14M in legal costs into $20M+ in licensing revenue"
- ❌ "26% accuracy vs. 100%"
- ❌ Any AI detection tool comparisons

### Kenji (AI Labs) - APPROVED Messaging
- "We're building text provenance standards WITH you through C2PA—OpenAI is a member"
- "Publisher ecosystem implementing marked content—you need compatible infrastructure"
- "Performance intelligence from sentence-level attribution"
- "This isn't restriction—it's infrastructure for attribution and partnerships"
- "Building WITH the AI industry, not against it"

### Kenji - REMOVED Messaging (DO NOT USE)
- ❌ "Publishers are implementing our enhanced standard. Basic C2PA won't integrate."
- ❌ "$50M solution to a $78M problem"
- ❌ "The standard is inevitable. Early adopters shape it."
- ❌ Any "comply or bleed" framing

---

## Priority Matrix

| Task | Impact | Effort | Priority |
|------|--------|--------|----------|
| 1.1 Fix 404 | Critical | Low | P0 |
| 2.3 Remove deprecated messaging | High | Low | P0 |
| 3.1 Create AI Labs page | High | Medium | P1 |
| 2.1 Update homepage hero | Medium | Low | P1 |
| 2.2 Update subtext parity | Medium | Low | P1 |
| 1.2 Add Demo to nav | Medium | Low | P1 |
| 5.1 Tone audit | Medium | Medium | P2 |
| 5.2 C2PA collaboration messaging | Medium | Low | P2 |

---

## Appendix: UX Audit Findings Summary

### Eleanor (Publisher) Journey
| Page | Rating | Key Issue |
|------|--------|-----------|
| Homepage | B | Headline too abstract; good CTA path |
| /solutions/publishers | A- | Strong demo, clear value props |
| /pricing (Publishers tab) | A | Clear tiers, revenue share visible |
| /publisher-demo | A | Interactive, compelling |

### Kenji (AI Labs) Journey  
| Page | Rating | Key Issue |
|------|--------|-----------|
| Homepage | C | Secondary positioning; "content theft" adversarial |
| /solutions/ai-labs | F | **404 - Page doesn't exist** |
| /pricing (AI Labs tab) | B+ | Good content but missing collaboration framing |
| /ai-demo | A | Excellent but undiscoverable |

---

## Completion Notes

_To be filled upon completion_
