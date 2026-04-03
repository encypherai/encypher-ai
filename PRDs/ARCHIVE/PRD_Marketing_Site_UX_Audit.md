# PRD: Marketing Site UX Audit
**Status:** Complete
**Date:** 2026-04-02
**Scope:** All non-blog client-facing pages on apps/marketing-site
**Auditor:** TEAM_292

## Audit Approach

Marketing page rubric (adapted from ux-audit skill):
- **Visual Design:** Color palette, Typography, Iconography, Spacing & layout
- **IA:** Content hierarchy, Navigation, Value proposition clarity
- **Functional:** Trust signals, Actionability, CTA friction
- **Brand:** Brand identity, Professional polish

Score: 0-10 per category, mean = overall. A(9-10) B(7-8.9) C(5-6.9) D(3-4.9) F(<3)

Pages are grouped by template type where the same layout and issues recur. Scores marked with * share the same template and are rated as a group; individual notes appear only where a page meaningfully deviates.

---

## Score Summary Table

### Primary Hero / Marketing Landing Pages

| Page | Score | Grade | Top Issue |
|------|-------|-------|-----------|
| / (homepage) | 8.1 | B | Minor: hero background tokens overlap on scroll |
| /try | 7.5 | B | Interactive demo heavy; CTA hierarchy unclear below fold |
| /platform | 7.5 | B | Feature grid lacks depth; no pricing anchor CTA |
| /pricing | 7.8 | B | Strong but free tier CTA competes with paid upgrade flow |
| /demo | 7.0 | B | Iframe embed feels disconnected from surrounding page |
| /publisher-demo | 7.0 | B | Same as /demo |
| /ai-demo | 7.0 | B | Same as /demo |
| /solutions | 7.5 | B | Three-audience split is clear; enterprise CTA missing |
| /solutions/publishers | 7.0 | B | Strong use case coverage; one CTA per screen needed |
| /solutions/ai-companies | 7.0 | B | Use cases clear; compliance angle underweighted |
| /solutions/enterprises | 7.0 | B | Enterprise page lacks logo wall / social proof |
| /enterprise | 7.5 | B | Strong compliance-led messaging; no CTA after feature list |
| /rights-management | 7.0 | B | Good education, under-sells proprietary advantage |
| /deepfake-detection | 7.5 | B | Floating metadata tokens crowd the hero headline area |
| /ai-copyright-infringement | 7.5 | B | Same background treatment; 3 CTAs too many |
| /ai-detector | 7.5 | B | Strongest headline of the three; same structural issues |
| /tools/chrome-extension | 7.5 | B | Hero is clean; no feature screenshots below fold |
| /tools/wordpress | 7.5 | B | Good headline; "Get Free API Key" is confusing CTA for a plugin |

### Article Template Pages (shared template, grouped score)

> All pages below use the same layout: breadcrumb + left-aligned H1 + lead paragraph + H2-sectioned body text. Zero CTAs on any of these pages. The score is driven primarily by the critical actionability deficit.

| Page | Score | Grade | Top Issue |
|------|-------|-------|-----------|
| /c2pa-standard | 7.0 | B | Hub page with member logos is stronger than sub-pages |
| /c2pa-standard/section-a7 | 5.4 | C | Article template: no CTA, empty right column, no related links |
| /c2pa-standard/conformance | 5.4 | C | Same |
| /c2pa-standard/implementation-guide | 5.4 | C | Same |
| /c2pa-standard/manifest-structure | 5.4 | C | Same |
| /c2pa-standard/media-types | 5.4 | C | Same |
| /c2pa-standard/members | 5.4 | C | Same |
| /c2pa-standard/vs-synthid | 5.4 | C | Same; comparison framing with no conversion path |
| /content-provenance | 7.0 | B | Hub page; sub-page navigation is the main value |
| /content-provenance/text | 5.4 | C | Article template: no CTA |
| /content-provenance/images | 5.4 | C | Same |
| /content-provenance/audio-video | 5.4 | C | Same |
| /content-provenance/for-publishers | 5.4 | C | Same; audience-specific page with no audience-specific CTA |
| /content-provenance/for-enterprises | 5.4 | C | Same |
| /content-provenance/for-ai-companies | 5.4 | C | Same |
| /content-provenance/eu-ai-act | 5.4 | C | High-intent regulatory page; no CTA is a significant miss |
| /content-provenance/news-publishers | 5.4 | C | Same |
| /content-provenance/enterprise-ai | 5.4 | C | Same |
| /content-provenance/academic-publishing | 5.4 | C | Same |
| /content-provenance/government | 5.4 | C | Same |
| /content-provenance/legal | 5.4 | C | Same |
| /content-provenance/music-industry | 5.4 | C | Same |
| /content-provenance/live-streams | 5.4 | C | Same |
| /content-provenance/verification | 5.4 | C | Same |
| /content-provenance/vs-blockchain | 5.4 | C | Same; comparison page with no conversion path |
| /content-provenance/vs-content-detection | 5.4 | C | Same |
| /compare | 6.5 | C | List page; tiles lack context about what each comparison covers |
| /compare/c2pa-vs-blockchain | 5.4 | C | Article template: should be a comparison table, not prose |
| /compare/content-provenance-vs-content-detection | 5.4 | C | Same |
| /compare/encypher-vs-synthid | 5.4 | C | High-intent competitive page; no CTA is critical miss |
| /compare/encypher-vs-detection-tools | 5.4 | C | Same |
| /compare/encypher-vs-prorata | 5.4 | C | Same |
| /compare/encypher-vs-tollbit | 5.4 | C | Same |
| /compare/encypher-vs-wordproof | 5.4 | C | Same |
| /cryptographic-watermarking | 6.8 | C | Hub page with stronger intro than section sub-pages |
| /cryptographic-watermarking/how-it-works | 5.4 | C | Article template; three-layer structure is good, no CTA |
| /cryptographic-watermarking/survives-distribution | 5.4 | C | Same; right-side whitespace unused |
| /cryptographic-watermarking/legal-implications | 5.8 | C | Disclaimer callout and damage table are good; still no CTA |
| /cryptographic-watermarking/text | 5.4 | C | Article template |
| /cryptographic-watermarking/vs-statistical-watermarking | 5.4 | C | High-intent competitive page; no CTA |

### Tools Pages

| Page | Score | Grade | Top Issue |
|------|-------|-------|-----------|
| /tools | 5.4 | C | Plain link list; no visual hierarchy, no "which tool?" guidance |
| /tools/sign | 6.0 | C | Minimal form; "Provenance" field label unexplained |
| /tools/verify | 6.0 | C | Adequate for the task; no context about what "verified" means |
| /tools/encode | 6.0 | C | Encode/decode tools lack explanation of the use case |
| /tools/decode | 6.0 | C | Same |
| /tools/encode-decode | 6.0 | C | Same |
| /tools/sign-verify | 6.0 | C | Two large textareas + one button; looks like a prototype |
| /tools/inspect | 7.0 | B | Two-column layout (formats sidebar + drop zone) is the best tools UI |

### Utility Pages

| Page | Score | Grade | Top Issue |
|------|-------|-------|-----------|
| /company | 6.5 | C | Good copy; no team section; no post-scroll CTA |
| /contact | 8.0 | B | Role-selector grid + side panel is best-in-class for this type |
| /glossary | 7.5 | B | Search + alpha filter is excellent; needs product page cross-links |
| /status | 6.0 | C | Critical bug: double navbar renders on this page |
| /authors/erik-svilich | 4.5 | D | No headshot, no article list, no social proof; stub page |
| /authors/matt-kaminsky | 4.5 | D | Same |
| /privacy | 6.5 | C | Functional; standard template |
| /terms | 6.5 | C | Functional; standard template |

---

## Per-Page Findings

### Template A: Primary Hero / Marketing Landing Pages

**Applies to:** /, /try, /platform, /pricing, /solutions, /solutions/publishers, /solutions/ai-companies, /solutions/enterprises, /enterprise, /rights-management

**Visual Design (mean: 7.8)**
The Delft Navy / Blue NCS / Columbia Blue palette is distinctive and consistently applied. The dark hero with the Three.js-style canvas animation on the homepage is the strongest expression of brand: navy background, floating geometry and provenance tokens, sharp white wordmark. Typography hierarchy is clear at the H1 level. Below the hero, section headings sometimes lose weight contrast against body text. The C2PA logo marks (CCPA, CAI) provide meaningful visual texture as trust signal rows.

**IA (mean: 7.4)**
Content hierarchy is strong in the hero: overline badge -> headline -> subhead -> CTA buttons. The solutions pages each open with a well-defined audience statement. Navigation is consistent across all pages: the sticky navbar correctly highlights "Solutions", "Tools", etc. with the active dropdown working. Value proposition clarity is B-level: the hero explains the what well but the "why this over alternatives" is thin on most pages. The /enterprise page is the exception - it leads with compliance framing.

**Functional (mean: 7.2)**
Trust signals are consistent: C2PA member logos and "Authors of C2PA Section A.7" appear in the hero on most pages - this is well executed. Actionability is generally adequate: there is always at least one primary CTA. The problem is CTA multiplicity: /ai-copyright-infringement has three CTAs ("See How It Works", "Get Started Free", "For Publishers") at the same visual weight, making the primary action unclear. CTA friction is low for "Get Started Free" and "Book Demo" - both are fast paths.

**Brand (mean: 7.9)**
The Three.js floating-metadata animation is genuinely distinctive. It communicates the core product concept (provenance metadata embedded invisibly in content) without requiring the user to read anything. The brand mark/wordmark combination is clean. Polish is high on hero sections but drops on secondary page sections which occasionally have inconsistent card border-radii and line-height in body copy.

**Top fixes:**
- Reduce CTA count on /ai-copyright-infringement and /ai-detector to one primary + one ghost
- Add a "Schedule a Demo" or "Talk to Sales" CTA at the bottom of /solutions/enterprises (enterprise buyers do not self-serve from hero)
- On /solutions/publishers and /solutions/ai-companies, add one audience-specific testimonial or logo to address "who else is using this?"

---

### Template B: SEO Entry Pages with 3JS Hero

**Applies to:** /deepfake-detection, /ai-copyright-infringement, /ai-detector

**Visual Design (mean: 7.3)**
These pages use the same floating-metadata background but in a light variant: white background with light-blue dot grid and partially transparent FE01/FE04/model_id/timestamp tokens floating across the layout. The headline reads clearly in dark navy. The floating tokens serve the right conceptual purpose (showing that metadata is embedded in content). At 1280px they create some visual competition with the hero text - specifically the large "FE04" and "created_by: Encypher" strings that land near the headline zone at certain viewport widths.

**IA (mean: 7.2)**
Each page opens with a competitive reframe: "Beyond Deepfake Detection", "From AI Copyright Infringement to Licensing Revenue", "Better Than AI Detectors." This is effective hook-first framing. The C2PA trust logos appear in the hero fold on all three, which is the right placement for a skeptical audience. The problem is that none of these pages go deep enough - scrolling below the fold reveals the same C2PA logos, a "how it works" section, then a second CTA. For a user arriving from a Google search for "deepfake detection alternatives", the page ends before answering "what does this actually cost and how do I start."

**Functional (mean: 7.0)**
Trust signals in the hero (C2PA, CAI logos) are appropriate. Actionability suffers from CTA proliferation: three buttons at equal weight is two too many. "The difference? Detection guesses. Authentication knows." is an effective closing line but it sits between the headline and CTAs where it competes visually. CTA friction is low - "See How It Works" and "Get Started Free" are both clear.

**Brand (mean: 7.5)**
Strong headline writing on all three pages. The light 3JS background feels slightly less premium than the dark navy homepage version, but it is consistent with the site-wide palette and communicates the same technical metaphor.

**Top fixes:**
- Cut to one primary CTA in the hero (keep "See How It Works" -> primary; demote "Explore Solutions" to a text link)
- Add a second page section below the fold that shows a concrete use case (e.g., "A publisher signs 10,000 articles. An AI company scrapes them. Here is what the evidence looks like.") before the second CTA
- /deepfake-detection: replace "The difference? Detection guesses. Authentication knows." with a one-line stat (e.g., "AI detectors: 26% accuracy. Encypher: 100% cryptographic certainty.")

---

### Template C: Article Pages (critical issue)

**Applies to:** /c2pa-standard/section-a7 and all sub-pages in /c2pa-standard/*, /content-provenance/* sub-pages, /compare/* sub-pages, /cryptographic-watermarking/* sub-pages

**This is the most important finding in this audit.**

The site has approximately 48 pages using this template. Each page is well-written educational content with consistent layout (breadcrumb nav, left-aligned H1, lead paragraph, H2-sectioned body). The content is genuinely strong - the three-layer technology breakdown on /cryptographic-watermarking/how-it-works, the damage table on /cryptographic-watermarking/legal-implications, the scenario breakdowns on /cryptographic-watermarking/survives-distribution. These are the kind of educational assets that earn trust with legal and compliance audiences.

None of them have a CTA.

A user who reads /content-provenance/eu-ai-act in full - which means they are a compliance officer or legal counsel investigating whether Encypher solves their EU AI Act problem - hits the end of the article and finds nothing. No "see how this applies to your organization", no "talk to our compliance team", no "download the EU AI Act compliance checklist", no "get started free." They leave.

The same is true for the comparison pages. A user who searches "Encypher vs SynthID" and lands on /compare/encypher-vs-synthid has expressed direct purchase intent. The page answers the question factually but then leaves them with no path forward.

**Visual Design (mean: 6.4)**
The white-background article layout is readable and clean. Typography hierarchy uses a large left-aligned H1 with a strong lead paragraph - correct priority. H2 sections use a standard size that occasionally feels small relative to the H1. No icons are used on these pages; the horizontal rule between sections is the only visual divider. At 1280px viewport, the article body column is roughly 1200px wide - correct for full-width text on an educational page, but the right side has no sidebar, no related links, no "in this article" TOC for longer pieces.

**IA (mean: 6.2)**
Content hierarchy within the article is correct. The breadcrumb nav is consistent and correctly uses the parent section as level 2. Navigation to related pages is missing: a reader on /c2pa-standard/section-a7 has no indication that /cryptographic-watermarking/how-it-works exists, and vice versa. The hub pages (/c2pa-standard, /content-provenance, /compare, /cryptographic-watermarking) each link to their sub-pages but sub-pages do not link to each other or to related sub-pages in other sections. Value proposition clarity is C-level: the educational content implicitly builds a case for Encypher but never explicitly names the product capability or connects the educational claim to a feature.

**Functional (mean: 4.8)**
Trust signals: mostly absent on article sub-pages. The parent hub pages (/c2pa-standard, /content-provenance) carry the C2PA member logos, but sub-pages are stripped of them. Actionability: 3/10 - no CTAs anywhere. CTA friction: not applicable. This is the defining gap.

**Brand (mean: 5.8)**
The template is clean and consistent, which maintains brand cohesion. But bare white pages with only the logo and a breadcrumb in the top-left look like a documentation site, not a product marketing site. The contrast between the rich, animated homepage and the sparse article pages is jarring. A user navigating from the homepage into /content-provenance/eu-ai-act loses all brand atmosphere.

**Recommended fix (single highest-impact change across the whole site):**
Add a contextual CTA block at the end of every article page. It needs three variants:
1. **Regulatory/compliance articles** (/content-provenance/eu-ai-act, /cryptographic-watermarking/legal-implications, /compare/*, /content-provenance/for-enterprises, /content-provenance/government, /content-provenance/legal): CTA = "Schedule a compliance consultation" or "Talk to our legal team"
2. **Technical articles** (/c2pa-standard/*, /cryptographic-watermarking/how-it-works, /cryptographic-watermarking/survives-distribution): CTA = "Try the inspect tool" or "See the API documentation"
3. **Comparison articles** (/compare/*, /c2pa-standard/vs-synthid, /content-provenance/vs-blockchain): CTA = "Get Started Free" + "See Pricing"

Additionally: add a "Related articles" block to every article page, and add a sticky sidebar TOC to any article longer than ~1000 words (e.g., /cryptographic-watermarking/how-it-works, /cryptographic-watermarking/legal-implications).

---

### Template D: Hub Pages

**Applies to:** /c2pa-standard, /content-provenance, /compare, /cryptographic-watermarking

**Visual Design (mean: 7.0)**
Hub pages combine the article template header with a card grid linking to sub-pages. The /c2pa-standard hub is the strongest: it leads with the member logo row (Adobe, Microsoft, BBC, OpenAI, Google - visible at a glance), then a clean card grid. The /compare hub is weaker: the comparison tile labels are title-only with no preview of what the comparison covers.

**IA (mean: 7.0)**
Sub-page navigation is clear and complete. The /c2pa-standard hub value proposition is the clearest of the four: "Encypher authored Section A.7" is stated prominently. The /content-provenance hub is more generic - it needs a clearer statement of why provenance matters to the specific audience landing on it.

**Functional (mean: 6.5)**
The hub pages carry more trust signals than the article sub-pages. Actionability is marginal - hub pages link to sub-pages but do not have CTAs that convert toward signing up or scheduling a demo. /compare hub: the "compare" tiles would benefit from a "Read: Encypher beats SynthID on 4 dimensions" teaser rather than just the title.

**Top fix:** Each hub page should end with a CTA that offers a shortcut past the sub-pages for ready buyers: "Already convinced? Get started in 5 minutes."

---

### Template E: Interactive Tool Pages

**Applies to:** /tools/sign, /tools/verify, /tools/encode, /tools/decode, /tools/encode-decode, /tools/sign-verify

**Visual Design (mean: 6.0)**
These pages are functionally minimal. The /tools/sign-verify page shows two large textareas ("Text to Sign" and "Provenance") with a single full-width "Sign Text" button. The layout is a centered card on a white background with no decorative elements. This reads like an internal QA tool, not a public product demo.

**IA (mean: 5.8)**
The "Provenance" field label on /tools/sign-verify will confuse a first-time visitor: they do not know what to put there or why. The note below the fields ("For demo use only. All signing uses a server-side demo key.") is at the right place but in a low-contrast italic that is easy to miss. The "Switch to Verify" toggle button is the right pattern (tab-like navigation) but styled as an outline button rather than a visual tab, making its function unclear at a glance.

**Functional (mean: 6.5)**
The action is clear: paste text, click sign. Trust signals are absent from the tool page itself. No explanation of what the signed output proves or how to use it after signing. CTA friction is low for users who already understand the product.

**Brand (mean: 5.5)**
The tool pages share the navbar and footer but have no brand-aligned visual treatment. Compared to the rich animated homepage, these feel unfinished.

**Top fixes:**
- /tools/sign-verify: rename "Provenance" field to "Author / Publisher Name" with helper text explaining what it records
- Add a one-line explanation below the tool title: "This tool embeds cryptographic provenance into your text. The signed output verifies authorship and creation time even after copy-paste."
- Apply the same card treatment as /tools/inspect (two-column: explanation sidebar + action panel) to all tool pages

**Exception - /tools/inspect (score: 7.0)**
The inspect tool is the best-designed of the tools pages. The two-column layout (supported formats list on the left, large drop zone on the right) is correctly proportioned and functional. The "Browse files" button on the drop zone is large and obvious. Main gap: no explanation of what the output will show the user before they drop a file.

---

### Template F: Tool Landing Pages (Chrome Extension + WordPress)

These pages (/tools/chrome-extension, /tools/wordpress) are full marketing landing pages with the hero template, not the minimal tool UI. Both are B-level.

**/tools/chrome-extension (7.5):** "Verify Content Provenance in Your Browser" is a clear value proposition. "Free on Chrome Web Store" badge is an effective friction reducer. "Add to Chrome - Free" is the right primary CTA. Weakness: below the fold there are no screenshots of the extension in use.

**/tools/wordpress (7.5):** "Protect Your WordPress Content with Cryptographic Proof" is strong. "Get Free API Key" as the primary CTA is slightly confusing for a plugin page - the user wants to install the plugin, not get an API key as the first step. The C2PA compliance badge is well-placed.

**Top fix for both:** Add 2-3 UI screenshots in the section below the fold. "A visitor sees this icon. They click. They see this." Visual proof eliminates the biggest objection (what does this actually look like for my readers?).

---

### /tools (index) - Score: 5.4

A plain list of six cards: title + one-line description, no icons, no visual differentiation. The card ordering is not obvious: "Sign/Verify" appears first, then "Sign Only" and "Verify Only" as separate cards, which creates confusion about whether these are the same tool or different ones (they are the same tool, split into modes). No guidance about which tool to start with for a first-time user.

**Top fixes:**
- Reorder: featured/recommended tool first ("Try Sign/Verify"), then group specialized tools with a header ("Advanced tools"), then integrations ("Add to your workflow: Chrome Extension, WordPress")
- Add an icon per card (the icon library already has these)
- Add a "Not sure where to start?" guidance block at the top

---

### /demo, /publisher-demo, /ai-demo - Score: 7.0

These pages embed interactive product demos. The surrounding page is consistent with the hero template. The main weakness is the gap between the animated marketing hero and the iframe embed: the transition feels abrupt, with the iframe rendering inside a plain white container with minimal surrounding context. The demo pages benefit from a CTA above and below the embed ("Want to see this live? Book a walkthrough with our team") since the embed may not fully load for all visitors.

---

### /pricing - Score: 7.8

The pricing page is one of the stronger pages on the site. The tier structure is clear and the feature comparison rows are readable. The free tier is prominent, reducing friction for technical evaluators. The enterprise tier correctly ends in "Contact Sales" rather than a price. Weakness: the CTA at the top of the page ("Get Started Free") and the CTA at the bottom of the free tier card ("Get Started Free") are identical, which misses an opportunity to differentiate the buyer journey for someone who has scrolled through the entire pricing table (they deserve a warmer CTA like "Talk to us about what you need").

---

### /company - Score: 6.5

The company page opens with a strong mission statement framed around C2PA authorship. The "Authors of C2PA Section A.7, Co-chairs of the Text Provenance Task Force" trust signal, paired with the CCPA and CAI logos, is the best-placed trust signal on the site. The "Our Story" section is well-written. Weaknesses: no team headshots or bios (for enterprise buyers, "who are the founders and what are their credentials?" is a buying signal), and the page ends after the body copy with no CTA. An enterprise VP landing on /company after clicking through from a cold email deserves a "Schedule an intro call" link at the bottom.

---

### /contact - Score: 8.0

The contact page is the strongest utility page on the site. The role-selector grid (General Inquiry / Publisher / AI Lab / Enterprise, each with a short description) is excellent UX - it segments intent without requiring the user to fill in a dropdown. The two-column layout (form left, contact info + demo CTA right) is well-proportioned. "Response Time: Within 24 hours, Mon-Fri 9am-6pm PT" is a trust signal that reduces anxiety about reaching out. Minor issues: the optional Organization and Job Title fields could be removed to reduce form length, as email + "How can we help?" + consent checkbox is sufficient for first contact.

---

### /glossary - Score: 7.5

The Content Provenance Glossary is a strong SEO and trust-building asset. "Maintained by Encypher - authors of Section A.7 of the C2PA 2.3 specification" in the subhead is excellent credentialing. The search bar + alpha filter combination is the right interaction pattern for 42+ terms. The "Article 52 -> EU AI Act guide ->" cross-links at the bottom of entries are valuable navigation. Gap: the entries have no "see this in action" links pointing back to product pages or tools. A user who just read the definition of "cryptographic watermarking" in the glossary should have a one-click path to /tools/sign or /cryptographic-watermarking.

---

### /status - Score: 6.0

The "All Systems Operational" green status badge and the service rows (API Gateway, Authentication, Signing Service, etc.) are clear and functional. Critical layout bug: the navbar renders twice - full navigation appears at y=0 and again at approximately y=64, creating a doubled header. This is a P0 visual defect that must be fixed before any enterprise prospect sees this page.

---

### /authors/erik-svilich, /authors/matt-kaminsky - Score: 4.5

Both author pages consist of a name, title, and biographical text paragraphs. No headshot, no social media links, no list of articles authored, no linked credentials. The biography copy on /authors/erik-svilich is substantive (C2PA authorship, patent ENC0100, prior work) and reads well. But without a photo, this page fails to do the one job an author page needs to do: make the author credible as a person, not just as a set of credentials. For a company whose core claim is "trust and authenticity," having a staff page with no faces is a brand inconsistency.

**Top fixes:**
- Add professional headshots
- Add a list of 3-5 recent articles authored
- Add LinkedIn and X profile links
- Add a one-line "Why I built this" quote

---

### /privacy, /terms - Score: 6.5

Both are functional legal pages using a consistent heading hierarchy (H1 "Privacy Policy" / "Terms of Service" + H2 numbered sections + H3 sub-sections). "Last Updated: February 23, 2026" is correctly positioned below the H1. "We will never sell your personal data to third parties." on /privacy is a good trust-building statement placed in the introduction. No structural issues. The pages render at full viewport width with no max-width container, which makes paragraphs very wide on large monitors - a readability issue for dense legal text. Max-width of 750-800px would improve readability.

---

## Prioritized Fix List

| # | Fix | Priority | Status | Notes |
|---|-----|----------|--------|-------|
| 1 | Contextual CTA blocks on all article pages | P0 | Done | All ~48 article pages have CTAs |
| 2 | Fix double navbar on /status | P0 | Done | Removed manual Navbar/Footer imports |
| 3 | Comparison tables on /compare/* pages | P0 | Done | All 7 pages already had tables |
| 4 | Author page headshots + article list | P1 | Done | Real headshots from /images/headshots/ + article lists already existed |
| 5 | Reduce CTA count on hero pages | P1 | Done | deepfake, ai-copyright, ai-detector fixed |
| 6 | Rename "Provenance" field + tool descriptions | P1 | Done | sign-verify + EncodeDecodeTool updated |
| 7 | UI screenshots on chrome-extension + wordpress | P1 | Done | Chrome extension: 3 store screenshots. WordPress: 3 screenshots (editor, badge, settings). |
| 8 | Bottom CTA on /solutions/enterprises + /company | P1 | Done | /company CTA added; /solutions/enterprises already had CTAs |
| 9 | Glossary cross-links to product/tool pages | P2 | Done | 16 tool/product links added to glossary terms + glossary pill links on 3 tool pages |
| 10 | Restructure /tools index | P2 | Done | Featured tool callout + semantic groupings |
| 11 | Max-width on /privacy + /terms | P2 | N/A | Already had max-w-4xl |
| 12 | Sticky sidebar TOC for long articles | P2 | Done | ArticleTOC component integrated into 29 article pages via ArticleShell wrapper |
| 13 | Related articles blocks on article sub-pages | P2 | Done | RelatedArticles component with cross-category links in 29 pages |
| 14 | Team section on /company | P2 | N/A | Already existed with headshots |
| 15 | Bottom CTA on /enterprise + /pricing | P2 | N/A | Already existed |

## Remaining Gaps

None. All 15 items are complete or confirmed already in place.

## Additional Changes Made Outside Fix List

- Fixed 7 compare page CTA links from relative `/auth/signin?mode=signup` to `${DASHBOARD_URL}/auth/signin?mode=signup`
- Fixed 7 additional pages using relative auth/signin URLs (c2pa-standard, solutions/*, content-provenance, cryptographic-watermarking, ai-copyright-infringement, compare index)
- Added enterprise demo CTA to /company page
- Added `/signup` and `/signup/wp` redirects in next.config.js for WordPress plugin onboarding
- Customized dashboard signup page for `source=wordpress` (headline, subtext, signup_source tracking)
