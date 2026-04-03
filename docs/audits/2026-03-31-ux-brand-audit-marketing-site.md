# UX/UI Audit - Encypher Marketing Site
**Date:** 2026-03-31 | **Version:** v1 (feat/seo-content-provenance-dominance) | **Overall Score: 7.2 / 10**

## Context
Encypher's marketing site (Next.js 15, ~94 routes) serves three ICPs: publishers (primary GTM), AI labs (collaborative positioning), and enterprises (compliance). This audit covers all key page categories: homepage, solutions pages, tools, pillar content, pricing, blog, compare, glossary, and conformance explorer. Scored as a **landing page / marketing site** (adapted rubric: "Data presentation" -> "Value proposition clarity", "Empty states" -> "Trust signals").

## Score Summary
| Group | Category | Score | Grade |
|---|---|---|---|
| Visual | Color Palette | 7.0 | B |
| Visual | Typography | 7.5 | B |
| Visual | Iconography | 6.5 | C |
| Visual | Spacing & Layout | 7.0 | B |
| IA | Content Hierarchy | 8.0 | B |
| IA | Navigation Structure | 7.0 | B |
| IA | Onboarding UX | 7.0 | B |
| Functional | Value Proposition Clarity | 8.0 | B |
| Functional | Actionability | 7.0 | B |
| Functional | Trust Signals | 8.0 | B |
| Brand | Brand Identity | 6.5 | C |
| Brand | Professional Polish | 7.0 | B |
| **Overall** | | **7.2** | **B** |

Grade: A (9-10), B (7-8.9), C (5-6.9), D (3-4.9), F (0-2.9)

---

## Detailed Assessment

### Group 1: Visual Design

#### 1. Color Palette - 7.0 / 10

**Working:** The navy (#1b2f50) / azure (#2A87C4) / white palette is cohesive and reads as enterprise-serious. The homepage hero, pillar page hero sections, and pricing page all carry a consistent blue gradient band below the navbar that creates visual continuity across the site. The azure CTA buttons are immediately recognizable as interactive elements.

**Not working:** Under the hood, the brand palette leaks. The codebase contains **247+ hardcoded instances of #2a87c4** in inline styles rather than using `BRAND_COLORS` tokens or Tailwind's `bg-primary`/`text-primary` classes. The `button.tsx` base component itself hardcodes `bg-[#2a87c4]` (line 13), which cascades brand-token bypass to all 62 consuming files. Two instances of `#1a365d` on the homepage (lines 307, 395) use a non-brand dark blue instead of the defined `#1b2f50`. The brand teal (#00CED1, `--color-cyber-teal`) is defined in the theme but appears in zero Tailwind classes across the entire site, a missed opportunity for accent hierarchy.

**Impact:** Visually the palette holds together today. The real risk is drift: any designer or developer adding a new page will copy-paste inline hex values rather than tokens, and the palette will fragment over time. The button.tsx root fix would propagate correctly to 62 files in one change.

#### 2. Typography - 7.5 / 10

**Working:** Roboto is loaded consistently via Google Fonts and applied through CSS custom properties (`--font-roboto`). The hero sections use a bold 5xl-6xl heading with clear weight contrast against the lg-xl body text beneath. Pillar pages (content-provenance, c2pa-standard, cryptographic-watermarking) use a consistent badge -> h1 -> subtitle -> body hierarchy that reads well. Code blocks correctly use Roboto Mono. The type scale creates clear scanability: 3-second scan yields the core message on every hero.

**Not working:** The cookie consent CSS uses a different fallback stack (`system-ui, -apple-system`) than the main globals (`Arial`). This is cosmetic but represents system-level inconsistency. The blog page has no visual differentiation between post title weight and description weight, making the feed feel flat. Some pillar sub-headings ("Why Content Provenance Matters Now", "What Is C2PA?") are set in the same size as nearby body text and rely solely on bold weight for hierarchy.

**Impact:** Typography is a strength. The remaining issues are polish-tier, not structural.

#### 3. Iconography - 6.5 / 10

**Working:** The `EncypherMark` brand icon (from `@encypher/icons`) is integrated as bullet-point marks on the homepage value prop cards and as the completion/verification indicator on the /try page's stepped verification sequence. This gives the brand's checkmark a distinctive, ownable treatment. The `EncypherLoader` is used for loading states on /try. Lucide icons are used consistently (same stroke weight) across all utility positions, and the selection is appropriate: `FileText` for publishers, `Bot` for AI labs, `Building2` for enterprises, `Shield` for security, `ArrowRight` for CTAs.

**Not working:** Only 3 files import from `@encypher/icons`. The other 63 files use generic lucide-react icons. On pages like the conformance explorer, pricing, solutions/ai-companies, and content-provenance, bullet points use `CheckCircle2` (lucide) rather than `EncypherMark`, creating inconsistency with the homepage. The encode-decode tool and file inspector have no brand icon presence. The `@encypher/design-system` package is installed but has **zero imports** anywhere in the codebase.

**Impact for ICP:** A Fortune 500 GC evaluating Encypher alongside competitors will not consciously register icon inconsistency. But the cumulative effect of branded vs generic signals adds up: the homepage "feels like Encypher" while deeper pages feel like a template. This is the biggest brand differentiation gap in the audit.

#### 4. Spacing & Layout - 7.0 / 10

**Working:** Homepage uses a strong 4/3/3 column grid for the value prop cards, giving publishers visual primacy (correct per GTM strategy). The pillar pages have generous whitespace between sections. Pricing page's audience tabs (Publishers / AI Labs / Enterprises) are well-spaced. Mobile layout stacks cleanly: hero text, CTAs, and credential bar all maintain readable line lengths on 390px viewport. The conformance explorer's stat cards (47 Products, 20 Orgs, 39 Generators, 8 Validators) use consistent card spacing.

**Not working:** The encode-decode tool page has excessive empty space below the form and a single "All Tools" link floating in the void. The inspect page splits into a 30/70 layout that wastes the left column (supported formats list) when the right column (drop zone) is the primary interaction. The blog page lacks any grid structure for posts, reading as a plain chronological feed with no visual rhythm between entries. On mobile, the homepage hero background animation (MetadataBackground) shows floating metadata labels that overlap with the CTA text at some scroll positions.

**Impact:** Layout is functional and clean on the main conversion paths (homepage, solutions, pricing). The tools pages and blog are the weak points.

---

### Group 2: Information Architecture

#### 5. Content Hierarchy - 8.0 / 10

**Working:** The homepage flows in a deliberate priority sequence: hero (what + proof) -> credentials bar (authority) -> three-audience value props (publisher-first by size) -> "How It Works" steps -> embedded live demo -> detection section -> comparison table -> standards -> final CTA. This is textbook SaaS structure. The pillar pages (content-provenance, c2pa-standard, cryptographic-watermarking) each open with a badge establishing Encypher's authority, then the topic title, then the definition, then the CTAs, creating a consistent "trust first, educate second, convert third" pattern. The compare page's "Three-Layer Stack" (Access Control -> Content Provenance -> Attribution/Monetization) is an especially strong hierarchical framework that positions Encypher precisely in the market.

**Not working:** The homepage has a JSX comment `{/* Content Theft Detection */}` that labels a section which is actually about content *tracking* (Chrome extension detection). This internal naming misalignment suggests the messaging has evolved but the code structure has not fully caught up. The "How It Works" section uses the language "Own It" with "enforce against unauthorized use" which conflicts with the Switzerland positioning per internal strategy docs.

**Impact:** The homepage is the single most important page and its hierarchy is strong. The compare page is a standout. Minor messaging alignment issues noted below in Brand section.

#### 6. Navigation Structure - 7.0 / 10

**Working:** Seven top-level nav items (Solutions, Tools, Blog, Resources, Pricing, Company, Platform) cover the site well. Dropdown menus on Solutions and Resources group sub-pages logically. Breadcrumbs appear on all sub-pages (Home / C2PA Standard / Conformance Explorer) and use link styling for wayfinding. The blog sidebar topic filter ("Popular Topics" with counts) is useful for a growing content library. Mobile hamburger menu is clean.

**Not working:** Seven top-level items is at the upper bound for cognitive load. "Platform" (which goes to the dashboard) could be absorbed into the "Sign In" / "Get Started" CTA area since it serves existing users, not prospects. "Resources" is a catch-all that overlaps with "Blog" and "Tools". The navbar shows "Blog" and "Pricing" in `text-primary` (azure) while "Solutions", "Tools", "Company" are dark, creating an unintentional visual hierarchy among nav items that does not reflect business priority.

**Impact:** Navigation works. The color inconsistency on nav items and the 7-item count are addressable without structural changes.

#### 7. Onboarding UX - 7.0 / 10

**Working:** The /try page is an excellent zero-friction onboarding surface: pre-filled sample text, single "Sign This Text" CTA, no account required. The homepage embeds this same /try experience inline below "How It Works", so visitors see the product working before scrolling past the fold. The publishers page has a "Setup in 4 Steps" card (sign up -> copy API key -> paste into CMS -> publish) that clearly communicates time-to-value (under 20 minutes). The new `VerificationSequence` stepped loading animation (Analyzing document structure -> Generating cryptographic signatures -> Embedding provenance markers) makes the signing process feel intentional and educational.

**Not working:** After signing text on /try, the user sees signed output but no clear "Now what?" pathway. There is no prompt to verify the text they just signed, try it with their own content, or sign up for a free account. The demo ends at the result. The encode-decode tool has no pre-filled sample or guidance, just empty text areas and a faded-looking button. The inspect tool's drop zone has no sample file or example output to show what a successful inspection looks like.

**Impact:** The homepage-to-/try path is the primary conversion funnel. The /try -> sign-up handoff is the gap.

---

### Group 3: Functional Design

#### 8. Value Proposition Clarity - 8.0 / 10

**Working:** Each audience gets a distinct, specific value proposition:
- Publishers: "Protect Ownership Across Every Channel" with cryptographic proof, competitor detection, machine-readable licensing
- AI Labs: "Compatible Infrastructure for Marked Content" with one integration, quote integrity verification, standards-based
- Enterprises: "AI Content Governance at Scale" with C2PA compliance, sentence-level authentication, on-premise deployment

The differentiation by audience is sharp and each proposition is concrete rather than abstract. The AI labs card explicitly names "OpenAI, Google, Adobe, and Microsoft as members" which grounds the collaborative positioning. The pricing page headline "Free to Sign. Paid to Enforce." is one of the clearest freemium articulations in the category. The compare page's per-competitor cards (vs SynthID, vs WordProof, vs TollBit, etc.) with technical tags and one-paragraph positioning are useful for buyers doing competitive research.

**Not working:** The homepage sub-headline still contains "When someone uses your content, you can prove it's yours" which, while accurate, frames the value through a surveillance/adversarial lens rather than an infrastructure lens. The updated third line ("When questions arise about origin or licensing, the proof is already there") is better but the middle line still sets up a you-vs-them frame. The "How It Works" Step 3 ("Own It") bullet "enforce against unauthorized use" reads as adversarial. The publishers page hero "Stop absorbing litigation costs" opens with a negative frame.

**Impact:** Proposition clarity is a strength. The remaining adversarial language fragments are concentrated on the homepage and publisher hero, not systemic.

#### 9. Actionability - 7.0 / 10

**Working:** Every page has a primary CTA in azure blue. Publisher-facing CTAs use solid fill, AI lab and enterprise CTAs use outline variant, creating correct visual hierarchy. The homepage has dual CTAs (See It Work + How It's Different) that serve both action-oriented and research-oriented visitors. Solution pages use a three-CTA pattern (primary demo + secondary free + tertiary sales) which covers all buying stages. The blog "Read more" links and tag pills are well-styled.

**Not working:** The encode-decode tool's "Sign Text" button renders with a faded light blue gradient that visually reads as disabled. This is the most critical actionability bug in the site: the primary CTA on a tool page looks unclickable. The inspect page "Browse files" button is small and secondary-styled despite being the only action on the page. The homepage's bottom CTA section has "Get Started Free" + "Talk to Sales" but uses `#1a365d` background (wrong navy shade) rather than the brand's standard azure.

**Impact:** The encode-decode button appearance is a P0 fix. The other issues are P1.

#### 10. Trust Signals - 8.0 / 10

**Working:** Trust signals are layered and repeated at appropriate intervals:
- C2PA and Content Authenticity Initiative logos on homepage hero, pricing page, company page
- "Authors of C2PA Section A.7" credential bar on homepage with four metrics (Section A.7, Jan 8 2026, Co-Chair, Free)
- Conformance explorer showing 47 conformant products / 20 organizations in the ecosystem
- AI companies page explicitly names OpenAI, Google, Adobe, Microsoft, BBC as C2PA co-builders
- Free tier positioning removes barrier-to-entry objections
- Company page mission statement: "We believe AI and creators can thrive together"
- Open-source GitHub CTA on homepage footer

The standards-body credentials and the concrete conformance data are the strongest trust signals in the site. They differentiate Encypher from competitors who cannot claim standards authorship.

**Not working:** No customer logos, testimonials, or case studies anywhere on the site. The pricing page mentions "we only win when you win" which is aspirational but not backed by a customer proof point. The company page has no team photos or headshots. For a Fortune 500 GC evaluating the platform, the absence of social proof from named customers is the biggest trust gap. The conformance explorer correctly notes Encypher is "actively pursuing" conformance but has not yet achieved it, which a careful buyer will notice.

**Impact:** Standards authority is strong. Customer proof and team visibility are the gaps.

---

### Group 4: Brand & Differentiation

#### 11. Brand Identity - 6.5 / 10

**Working:** The MetadataBackground animation on the homepage hero is the single most distinctive visual element on the site: floating metadata labels (model_id, timestamp, signature, version) create an immediately ownable aesthetic that no competitor has. The navy/azure palette reads as enterprise-serious without being corporate-sterile. The EncypherMark brand icon, where it appears (homepage value props, /try verification sequence), creates a recognizable "brand check" that could become an ownable asset like Stripe's gradient or Slack's hashtag.

**Not working:** The EncypherMark appears on only 3 of 94 pages. The `@encypher/design-system` package is installed but imported zero times. If you removed the Encypher logo from the navbar, most pages (solutions, tools, pillar content, blog, glossary) would be indistinguishable from any shadcn/ui template site. The MetadataBackground animation only appears on the homepage hero, not on any other page. There are no brand illustrations, no custom patterns, no distinctive card treatments. Purple and indigo colors (`text-indigo-500`, `bg-purple-500`) appear in 5 dashboard-adjacent files, which are entirely off-brand.

**Impact:** This is the highest-leverage improvement area. The EncypherMark and MetadataBackground are strong assets that are underdeployed. Extending them to pillar pages and tools would shift the entire site's brand score.

#### 12. Professional Polish - 7.0 / 10

**Working:** Happy-path experiences are clean. The new VerificationSequence loading states (stepped progress with EncypherMark completion icons and EncypherLoader animation) are a significant polish improvement over generic spinners. The homepage credentials bar is pixel-precise. Pillar page hero sections have consistent badge + heading + subtitle + CTA structure. Pricing page audience tabs work smoothly. Conformance explorer stat cards are well-balanced.

**Not working:** The encode-decode tool "Sign Text" button has a washed-out gradient that looks disabled (likely a CSS specificity issue with the hardcoded `bg-[#2a87c4]` in button.tsx interacting with the tool's styling). The blog page is a plain text feed with no post thumbnails, hero images, or visual differentiation between entries, which reduces scannability. The inspect page has no empty-state illustration or example output, just a dashed-border drop zone. Loading states are inconsistent: /try and homepage demo use the new VerificationSequence, but other API-driven interactions may still use generic spinners.

**Impact:** The encode-decode button is the most visible polish issue. Blog imagery and inspect empty-state are secondary.

---

## Brand Alignment: Code-Level Findings

### Critical: button.tsx Root Cause
`/src/components/ui/button.tsx` lines 13, 17 hardcode `bg-[#2a87c4]`, `border-[#2a87c4]`, `hover:bg-[#2387b5]`. This single component is imported by **62 files**. Fixing this to `bg-primary border-primary hover:bg-primary/90` would propagate brand-token compliance to the entire site in one change.

### Hardcoded Color Hotspots (top 5 by violation count)
| File | Violations | Fix |
|---|---|---|
| content-provenance/page.tsx | 26 | Replace inline `style={{ color: '#2a87c4' }}` with `className="text-primary"` |
| cryptographic-watermarking/page.tsx | 24 | Same pattern |
| ConformanceExplorer.tsx | 20 | Same pattern |
| c2pa-standard/page.tsx | 17 | Same pattern |
| music-industry/page.tsx | 12 | Same pattern |

### Off-Brand Colors in Use
| Color | Where | Should Be |
|---|---|---|
| `#1a365d` | Homepage lines 307, 395 | `BRAND_COLORS.navy` (#1b2f50) or `bg-delft-blue` |
| `#2387b5` | button.tsx hover | `primary/90` or define as `--color-primary-hover` |
| `text-indigo-500` | Dashboard components (5 files) | `text-primary` or `text-blue-ncs` |
| `bg-purple-*` | Admin, conformance, ai-demo | Remove or replace with brand tokens |
| `text-blue-600/700` | ai-demo, publisher-demo (7 files) | `text-blue-ncs` or `text-primary` |

### Design System Gap
`@encypher/design-system` exports Badge, Button, Card, Alert, etc. but has **zero imports** in the marketing site. The site is built entirely on local shadcn/ui components. This means no shared design system exists across Encypher products. Whether to migrate to `@encypher/design-system` or keep shadcn/ui as the SSOT is an architectural decision, but the current state of "installed but unused" is ambiguous.

---

## Messaging Alignment vs Internal Strategy

The internal strategy docs (GTM, Marketing Guidelines, ICPs) mandate "Building WITH AI companies, not against them" and flag "AI Company Perceives as Adversarial" as a CRITICAL risk. The site is mostly aligned, with these exceptions:

### Homepage (seen by ALL audiences - highest priority)
| Current Copy | Issue | Suggested Revision |
|---|---|---|
| "When someone uses your content, you can prove it's yours." | Surveillance framing | "When your content travels, the proof of origin travels with it." |
| "enforce against unauthorized use" (Step 3 "Own It") | Adversarial verb | "resolve usage questions with cryptographic evidence" |
| `{/* Content Theft Detection */}` JSX comment | Internal naming | `{/* Content Tracking & Detection */}` |
| "Know Where Your Content Appears. With Certainty." (h2) | Borderline - reads as surveillance | Keep - this is factual capability language |
| "Don't Just Lock Your Front Door. Lock Everything Inside." (h2) | Defensive/fortress metaphor | "Your Proof Travels With Your Content. Theirs Stays at the Gate." |

### Pricing Page
| Current Copy | Issue | Suggested Revision |
|---|---|---|
| "Free to Sign. Paid to Enforce." | "Enforce" is adversarial-adjacent | "Free to Sign. Paid to License." |
| "Pay only for enforcement tools" | Same | "Pay only for licensing and detection tools" |

### Publishers Page (acceptable per strategy)
Heavy enforcement/litigation language ("Stop absorbing litigation costs", "willful infringement") is **appropriate** for this audience per GTM strategy. Publishers expect this register. No changes recommended.

### AI Companies Page (well-aligned)
Collaborative tone throughout. "Encypher is not an enforcement mechanism" is explicitly stated. No changes needed.

---

## Prioritized Recommendations

| # | Recommendation | Impact | Effort | Priority |
|---|---|---|---|---|
| 1 | **Fix button.tsx token bypass**: Replace `bg-[#2a87c4]` with `bg-primary` in the base Button component. One file change propagates to 62 consumers. | High | S | P0 |
| 2 | **Fix encode-decode CTA appearance**: The "Sign Text" button renders as faded/disabled. Debug the CSS specificity chain from button.tsx. | High | S | P0 |
| 3 | **Homepage copy alignment**: Replace the 3 adversarial fragments identified above. Maintain publisher-first positioning without surveillance framing. | High | S | P0 |
| 4 | **Extend EncypherMark to pillar pages**: Replace `CheckCircle2` bullets on content-provenance, c2pa-standard, and cryptographic-watermarking pages with `EncypherMark color="azure"`. Migrate ~14 files for site-wide brand consistency. | Medium | M | P1 |
| 5 | **Batch-fix hardcoded #2a87c4 inline styles**: Convert the top-5 offending files (99 violations) from `style={{ color: '#2a87c4' }}` to `className="text-primary"`. | Medium | M | P1 |
| 6 | **Add post-demo conversion step on /try**: After signing, show a "Verify This Text" CTA and a "Get Your Own Key - Free" prompt. The demo currently dead-ends at the result. | High | S | P1 |
| 7 | **Pricing page copy**: "Free to Sign. Paid to Enforce." -> "Free to Sign. Paid to License." Aligns with Switzerland positioning. | Medium | S | P1 |
| 8 | **Define semantic color tokens**: Add `--color-success` (green), `--color-warning` (yellow) to theme.css. Currently green/yellow are hardcoded across 20+ files. | Low | M | P2 |
| 9 | **Blog post imagery**: Add thumbnail/hero images to blog feed. Currently plain text reduces scannability and looks unfinished. | Medium | M | P2 |
| 10 | **Resolve @encypher/design-system status**: Either migrate shadcn components to the shared package or remove the dependency. "Installed but unused" creates confusion. | Low | L | P2 |
