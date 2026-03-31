# SEO Content Provenance Category Dominance

**Status:** Not Started
**Current Goal:** Task 1.0 -- Fix C2PA attribution accuracy across site
**Team:** TEAM_291

## Overview

Encypher's marketing site has 51 indexable pages (24 routes + 27 blog posts) and strong foundational SEO infrastructure (centralized keyword management, JSON-LD structured data, AI crawler optimization). However, we have no pillar page for "content provenance" (the category term we must own), no dedicated C2PA explainer (despite authoring Section A.7), no comparison pages, and no programmatic format pages leveraging our 31-MIME-type advantage. This PRD defines the full content architecture and technical SEO work required to own the "Content Provenance" search category before and after the public v2.0.0 API launch. Target: 200+ indexed pages by end of Q3 2026.

Additionally, several locations across the site and SEO configuration inaccurately state that Encypher "authored the C2PA standard" or "authored the C2PA text standard." The accurate claim: Encypher is an active contributor to C2PA and authored Section A.7 (Embedding Manifests into Unstructured Text) of the C2PA 2.3 specification. Erik Svilich co-chairs the C2PA Text Provenance Task Force. This distinction must be corrected everywhere before any new content is published.

## Objectives

- Fix all C2PA attribution claims across the site to reflect accurate contribution (authored Section A.7, not the entire standard)
- Build three pillar pages that serve as canonical ranking targets for "content provenance," "C2PA standard," and "cryptographic watermarking"
- Create comparison pages capturing high-intent evaluation traffic
- Build programmatic format pages for all 31 supported MIME types (scalable moat no competitor can replicate)
- Add industry vertical landing pages for each target segment
- Build a glossary/terminology hub as a long-tail keyword engine
- Overhaul internal linking from navigation-based to contextual keyword-rich anchors
- Expand structured data (BreadcrumbList, TechArticle, author pages)
- Update AI crawler optimization (llms.txt, AISummary) with new content architecture
- Double blog cadence to 2 posts/week and reach 100+ posts by end of Q3 2026
- Optimize all new and existing content for AI tools (LLM crawlers, AI search, citation engines)

## Architecture

Target URL structure after completion:

```
encypher.com/
  content-provenance/                    <- PILLAR 1 (category-defining)
    for-publishers/
    for-ai-companies/
    for-enterprises/
    vs-content-detection/
    vs-blockchain/
    eu-ai-act/
    text/
    images/
    audio-video/
    live-streams/
    verification/
    jpeg/ png/ pdf/ mp4/ ...             <- 31 programmatic format pages
    news-publishers/ academic/ ...       <- vertical pages
  c2pa-standard/                         <- PILLAR 2 (standards authority)
    section-a7/
    implementation-guide/
    members/
    vs-synthid/
    manifest-structure/
    media-types/
  cryptographic-watermarking/            <- PILLAR 3 (technical differentiation)
    how-it-works/
    vs-statistical-watermarking/
    text/
    survives-distribution/
    legal-implications/
  compare/                               <- COMPARISON HUB
    encypher-vs-synthid/
    encypher-vs-wordproof/
    encypher-vs-detection-tools/
    encypher-vs-tollbit/
    encypher-vs-prorata/
    c2pa-vs-blockchain/
    content-provenance-vs-content-detection/
  glossary/                              <- TERMINOLOGY HUB
    (individual term pages broken out post-launch based on Search Console data)
  docs/api/                              <- INTERACTIVE API REFERENCE (v2.0.0)
  blog/                                  <- 27 existing + 2/week cadence
```

## Tasks

### 1.0 Fix C2PA Attribution Accuracy

Correct all instances where the site claims Encypher "authored the C2PA standard" or "authored the C2PA text standard." The accurate claim: Encypher authored Section A.7 of the C2PA 2.3 specification and co-chairs the Text Provenance Task Force.

- [ ] 1.1 Audit and fix `apps/marketing-site/src/lib/seo.ts`
  - [ ] 1.1.1 Fix `siteConfig.description`: change "Encypher authored the C2PA text authentication standard" to "Encypher authored Section A.7 of the C2PA 2.3 specification -- the text provenance standard. Patent-pending granular content attribution with Merkle tree authentication for tamper-evident documentation."
  - [ ] 1.1.2 Fix `faqSchema` answer for "What is Encypher?": replace "Encypher authored the C2PA text authentication standard" with "Encypher authored Section A.7 of the C2PA 2.3 specification (text provenance)"
  - [ ] 1.1.3 Fix `faqSchema` answer for "What is the C2PA text standard?": replace "authored by Encypher" with "whose text provenance section (A.7) was authored by Encypher"
  - [ ] 1.1.4 Fix `getBlogListSchema` description: replace "From the authors of the C2PA text standard" with "From the authors of C2PA Section A.7 (text provenance)"
- [ ] 1.2 Audit and fix `apps/marketing-site/src/app/metadata.ts`
  - [ ] 1.2.1 Fix `twitter.description`: replace "Authors of the C2PA text standard" with "Authors of C2PA Section A.7 (text provenance)"
- [ ] 1.3 Audit all blog posts for overclaimed attribution
  - [ ] 1.3.1 Grep all .md files in `src/content/blog/` for "authored the C2PA" or "authors of the C2PA" and fix each instance to specify Section A.7
  - [ ] 1.3.2 Grep all .tsx/.ts page files for "authored the C2PA" or "authors of the C2PA" and fix each instance
- [ ] 1.4 Audit `public/llms.txt` for overclaimed attribution and fix
- [ ] 1.5 Verify no overclaimed attribution remains across entire `apps/marketing-site/` directory
- [ ] 1.6 Run `next build` to confirm no build errors after changes

### 2.0 SEO Infrastructure Expansion

Expand the centralized SEO configuration to support the new content architecture.

- [ ] 2.1 Expand keyword categories in `src/lib/seo.ts`
  - [ ] 2.1.1 Add "content provenance" keyword cluster: "content provenance," "what is content provenance," "content provenance standard," "content provenance API," "content provenance verification," "content provenance for publishers," "content provenance for AI"
  - [ ] 2.1.2 Add "C2PA" keyword cluster: "C2PA," "C2PA standard," "C2PA 2.3," "C2PA Section A.7," "C2PA text provenance," "C2PA specification," "C2PA manifest," "C2PA implementation," "C2PA members"
  - [ ] 2.1.3 Add "cryptographic watermarking" keyword cluster: "cryptographic watermarking," "text watermarking," "invisible watermarking," "digital watermarking," "watermarking vs detection," "AI watermarking technology"
  - [ ] 2.1.4 Add "comparison" keyword cluster: "Encypher vs SynthID," "C2PA vs blockchain," "content provenance vs content detection," "cryptographic vs statistical watermarking"
  - [ ] 2.1.5 Add media-format keyword cluster: "JPEG provenance," "PDF provenance," "MP4 provenance," "audio provenance," "video provenance," "image provenance," "document provenance"
  - [ ] 2.1.6 Add regulatory keyword cluster: "EU AI Act content provenance," "EU AI Act August 2026," "AI Act compliance," "AI transparency requirements"
- [ ] 2.2 Add metadata generator functions for new page types
  - [ ] 2.2.1 Add `getPillarMetadata(pillar: 'content-provenance' | 'c2pa-standard' | 'cryptographic-watermarking')` function
  - [ ] 2.2.2 Add `getCompareMetadata(comparison: string)` function
  - [ ] 2.2.3 Add `getGlossaryMetadata()` function
  - [ ] 2.2.4 Add `getFormatPageMetadata(format: string, mimeType: string, category: string)` function for programmatic format pages
  - [ ] 2.2.5 Add `getVerticalMetadata(vertical: string)` function for industry vertical pages
- [ ] 2.3 Add new structured data schemas
  - [ ] 2.3.1 Add `BreadcrumbList` schema generator function for hierarchical pages (pillar > cluster > format)
  - [ ] 2.3.2 Add `TechArticle` schema for pillar and technical guide pages
  - [ ] 2.3.3 Add `DefinedTermSet` schema for glossary page
  - [ ] 2.3.4 Add `Person` schema for author pages (Erik Svilich, Matt Kaminsky) with E-E-A-T credentials
- [ ] 2.4 Add author page metadata
  - [ ] 2.4.1 Add `getAuthorMetadata(author: 'erik' | 'matt')` function with structured Person schema including credentials, role, and standards participation

### 3.0 Pillar Pages

Build three pillar pages as the canonical ranking targets for Encypher's core search categories. Each pillar page must include: AISummary component, JSON-LD structured data (TechArticle + FAQPage + BreadcrumbList), contextual internal links to cluster pages, and full SEO metadata.

- [ ] 3.1 Pillar 1: `/content-provenance` -- "What Is Content Provenance?"
  - [ ] 3.1.1 Create `src/app/content-provenance/page.tsx` as the category-defining pillar page (3,000-4,000 words)
  - [ ] 3.1.2 Content sections: definition and technical foundations; why content provenance matters now (EU AI Act August 2026, synthetic media, publisher rights erosion); how content provenance works (cryptographic signing, manifest embedding, verification); content provenance across media types (31 MIME types across 6 categories); C2PA as the open standard (link to Pillar 2); content provenance vs. content detection; content provenance vs. blockchain timestamping; implementation approaches; FAQ section
  - [ ] 3.1.3 Add AISummary component with category-defining summary
  - [ ] 3.1.4 Add TechArticle + FAQPage + BreadcrumbList JSON-LD schemas
  - [ ] 3.1.5 Add page-specific metadata via `getPillarMetadata('content-provenance')`
  - [ ] 3.1.6 Include contextual links to all cluster pages, Pillar 2, Pillar 3, comparison pages, and glossary
- [ ] 3.2 Pillar 2: `/c2pa-standard` -- "The C2PA Standard: How Content Provenance Works"
  - [ ] 3.2.1 Create `src/app/c2pa-standard/page.tsx` as the standards authority pillar page (2,500-3,500 words)
  - [ ] 3.2.2 Content sections: what C2PA is (Coalition for Content Provenance and Authenticity, members, governance, mission); history and timeline (founding through January 8, 2026 publication); how C2PA manifests work (accessible to non-engineers); C2PA for text -- Section A.7 (Encypher authored this section, link to spec); C2PA for images, audio, video (31 MIME types); C2PA vs. other approaches (SynthID, blockchain, fingerprinting, detection); who uses C2PA (Adobe, Microsoft, Google, BBC, OpenAI -- and Encypher as Co-Chair of the Text Provenance Task Force); implementing C2PA; C2PA and regulation (EU AI Act, potential US frameworks); FAQ section
  - [ ] 3.2.3 Add AISummary component with standards authority summary
  - [ ] 3.2.4 Add TechArticle + FAQPage + BreadcrumbList JSON-LD schemas
  - [ ] 3.2.5 Add page-specific metadata via `getPillarMetadata('c2pa-standard')`
  - [ ] 3.2.6 Include contextual links to Pillar 1, Pillar 3, cluster pages, and glossary
- [ ] 3.3 Pillar 3: `/cryptographic-watermarking` -- "Cryptographic Watermarking: Proof Embedded in Content"
  - [ ] 3.3.1 Create `src/app/cryptographic-watermarking/page.tsx` as the technical differentiation pillar page (2,000-3,000 words)
  - [ ] 3.3.2 Content sections: what cryptographic watermarking is (distinguish from statistical watermarking like SynthID); how cryptographic watermarking differs from detection (proof vs. probability); cryptographic watermarking for text (sentence-level granularity, survives distribution); cryptographic watermarking for images, audio, video; why watermarking survives and detection does not (copy-paste, scraping, B2B distribution); legal implications (formal notice, willful infringement); implementation (C2PA standard, Encypher as reference implementation); FAQ section
  - [ ] 3.3.3 Add AISummary component with technical differentiation summary
  - [ ] 3.3.4 Add TechArticle + FAQPage + BreadcrumbList JSON-LD schemas
  - [ ] 3.3.5 Add page-specific metadata via `getPillarMetadata('cryptographic-watermarking')`
  - [ ] 3.3.6 Include contextual links to Pillar 1, Pillar 2, cluster pages, comparison pages, and glossary

### 4.0 Cluster Pages (Pillar Satellites)

Build cluster pages around each pillar, connected by contextual keyword-rich anchors. Each cluster page: 1,000-2,000 words, AISummary, JSON-LD (WebPage + BreadcrumbList), links back to parent pillar.

- [ ] 4.1 Content Provenance cluster pages
  - [ ] 4.1.1 `/content-provenance/for-publishers` -- publisher-specific provenance guide (proof of origin, licensing leverage, brand protection, formal notice)
  - [ ] 4.1.2 `/content-provenance/for-ai-companies` -- collaborative infrastructure framing (compatible infrastructure, quote integrity, performance intelligence)
  - [ ] 4.1.3 `/content-provenance/for-enterprises` -- governance and compliance angle (EU AI Act, audit trails, AI governance)
  - [ ] 4.1.4 `/content-provenance/vs-content-detection` -- why proof of origin beats statistical detection (comparison page, also linked from /compare/)
  - [ ] 4.1.5 `/content-provenance/vs-blockchain` -- embedded provenance vs. blockchain timestamping (WordProof distinction)
  - [ ] 4.1.6 `/content-provenance/eu-ai-act` -- EU AI Act compliance deadline August 2, 2026 (regulatory urgency)
  - [ ] 4.1.7 `/content-provenance/text` -- text-specific provenance deep dive (sentence-level granularity, Section A.7, Merkle trees)
  - [ ] 4.1.8 `/content-provenance/images` -- image provenance guide (13 formats, EXIF stripping, pHash attribution search)
  - [ ] 4.1.9 `/content-provenance/audio-video` -- audio and video provenance guide (RIFF/ID3/BMFF container logic, live streams)
  - [ ] 4.1.10 `/content-provenance/live-streams` -- live video stream provenance (C2PA 2.3 Section 19, per-segment manifests, backwards-linked chain)
  - [ ] 4.1.11 `/content-provenance/verification` -- free verification across all media types (no auth, public API, 31 MIME types)
- [ ] 4.2 C2PA Standard cluster pages
  - [ ] 4.2.1 `/c2pa-standard/section-a7` -- deep dive on the text provenance specification Encypher authored (link to spec URL: https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#embedding_manifests_into_unstructured_text)
  - [ ] 4.2.2 `/c2pa-standard/implementation-guide` -- developer-focused C2PA implementation guide (reference implementation, API quickstart)
  - [ ] 4.2.3 `/c2pa-standard/members` -- who is in C2PA and why it matters (200+ members, founding orgs, task force structure)
  - [ ] 4.2.4 `/c2pa-standard/vs-synthid` -- cryptographic C2PA vs. statistical SynthID watermarking
  - [ ] 4.2.5 `/c2pa-standard/manifest-structure` -- technical C2PA manifest explainer (JUMBF containers, COSE signatures, claim structure)
  - [ ] 4.2.6 `/c2pa-standard/media-types` -- all 31 MIME types supported with format-specific embedding details
- [ ] 4.3 Cryptographic Watermarking cluster pages
  - [ ] 4.3.1 `/cryptographic-watermarking/how-it-works` -- technical deep dive (variation selectors, ZWC encoding, Merkle tree authentication)
  - [ ] 4.3.2 `/cryptographic-watermarking/vs-statistical-watermarking` -- SynthID comparison (deterministic vs. statistical, survives paraphrasing)
  - [ ] 4.3.3 `/cryptographic-watermarking/text` -- text-specific watermarking (invisible embedding, sentence-level granularity)
  - [ ] 4.3.4 `/cryptographic-watermarking/survives-distribution` -- durability proof (copy-paste, B2B, wire services, aggregators, scraping)
  - [ ] 4.3.5 `/cryptographic-watermarking/legal-implications` -- willful infringement frame (formal notice, elimination of "we didn't know" defense)

### 5.0 Comparison Pages

Build high-intent comparison pages. Each page: 1,500-2,500 words, fair and technically grounded (not attack pieces), structured as side-by-side analysis. Include FAQ schema. All competitive positioning content draws from GTM Strategy (canonical messaging SSOT).

- [ ] 5.1 Create `/compare` hub page listing all comparisons
- [ ] 5.2 `/compare/encypher-vs-synthid` -- cryptographic (deterministic, survives distribution) vs. statistical (probabilistic, fragile to paraphrasing) watermarking. Reference: Google's SynthID is AI-output watermarking; Encypher marks human content.
- [ ] 5.3 `/compare/encypher-vs-wordproof` -- embedded provenance that travels with content vs. blockchain timestamping (external proof, doesn't travel with text). Reference: "Timestamping proves content existed. Provenance proves ownership wherever it appears."
- [ ] 5.4 `/compare/encypher-vs-detection-tools` -- proof of origin (100% accuracy, cryptographic) vs. AI detection (GPTZero, Originality.ai -- statistical, false positives). Reference: proof vs. probability.
- [ ] 5.5 `/compare/encypher-vs-tollbit` -- embedded provenance (works without AI company cooperation) vs. access gates (require AI developer opt-in). Complementary framing per GTM strategy.
- [ ] 5.6 `/compare/encypher-vs-prorata` -- unilateral provenance (works regardless of cooperation) vs. opt-in attribution (requires AI company integration). Reference: "One requires participation. The other works unilaterally."
- [ ] 5.7 `/compare/c2pa-vs-blockchain` -- open standards-based approach vs. decentralized timestamping. Technical comparison of manifest embedding vs. hash anchoring.
- [ ] 5.8 `/compare/content-provenance-vs-content-detection` -- category-level distinction. Proof of origin at creation vs. probabilistic detection after the fact. This is the category-defining comparison page.

### 6.0 Programmatic Format Pages

Build a templated page for each of the 31 supported MIME types. Each page: 800-1,200 words, generated from a shared template component with format-specific data. Targets long-tail queries like "JPEG content provenance," "PDF C2PA signing," "MP4 provenance." No competitor supports 31 formats; this is the scalable moat.

- [ ] 6.1 Create shared template component `src/components/content/FormatPage.tsx`
  - [ ] 6.1.1 Template sections: what {format} provenance means; how C2PA manifests are embedded in {format} files (format-specific technical detail); which verification pipeline handles {format} (c2pa-python native vs. custom JUMBF/COSE); use cases (which industries produce this format); how to sign {format} content with Encypher API; CTA to API docs and free verification tool
  - [ ] 6.1.2 Accept props for: format name, MIME type, file extension, media category, embedding method, verification pipeline, industry use cases, related formats
  - [ ] 6.1.3 Include AISummary, BreadcrumbList, and TechArticle JSON-LD schemas
  - [ ] 6.1.4 Include contextual links back to parent pillar (`/content-provenance`), media-category cluster page, and media-types reference page
- [ ] 6.2 Create format data configuration file `src/data/formats.ts`
  - [ ] 6.2.1 Define data for all 31 MIME types with format-specific details:
    - Images (13): JPEG, PNG, WebP, TIFF, AVIF, HEIC, HEIC-sequence, HEIF, HEIF-sequence, SVG, DNG, GIF, JXL
    - Audio (6): WAV, MP3, M4A, AAC, FLAC, MPA
    - Video (4): MP4, MOV, M4V, AVI
    - Documents (5): PDF, EPUB, DOCX, ODT, OXPS
    - Fonts (3): OTF, TTF, SFNT
  - [ ] 6.2.2 For each format include: display name, MIME type, file extension, media category, embedding method (c2pa-python native or custom JUMBF/COSE), container type (ISO BMFF, RIFF, etc.), industry use cases, related formats
- [ ] 6.3 Create route structure for format pages
  - [ ] 6.3.1 Create `src/app/content-provenance/[format]/page.tsx` using dynamic route with `generateStaticParams` returning all 31 format slugs
  - [ ] 6.3.2 Generate metadata per format via `getFormatPageMetadata()`
  - [ ] 6.3.3 Render `FormatPage` component with format-specific data from `formats.ts`
- [ ] 6.4 Verify all 31 format pages render correctly and build without errors

### 7.0 Industry Vertical Pages

Build landing pages for each target industry vertical. Each page: 1,000-1,500 words, audience-specific pain points and use cases, links to relevant pillar and cluster pages.

- [ ] 7.1 `/content-provenance/news-publishers` -- AP, Reuters, BBC use case (downstream distribution, B2B licensing, wire services, willful infringement)
- [ ] 7.2 `/content-provenance/academic-publishing` -- Springer Nature, Taylor & Francis (research integrity, peer review provenance, journal licensing)
- [ ] 7.3 `/content-provenance/music-industry` -- audio provenance for labels and distributors (streaming, unauthorized use, rights management)
- [ ] 7.4 `/content-provenance/enterprise-ai` -- Fortune 500 governance (EU AI Act, audit trails, compliance reporting, AI content transparency)
- [ ] 7.5 `/content-provenance/legal` -- law firms and legal departments (evidence provenance, formal notice, court admissibility, AI disclosure requirements)
- [ ] 7.6 `/content-provenance/government` -- public records provenance (document authentication, FOIA, regulatory filings)

### 8.0 Glossary and Terminology Hub

Build a glossary page as a long-tail keyword engine. Start as a single page; break out top-performing terms into standalone pages post-launch based on Search Console data.

- [ ] 8.1 Create `src/app/glossary/page.tsx` with 40-60 term definitions (150-300 words each)
- [ ] 8.2 Terms to include (minimum):
  - Content provenance, C2PA, C2PA manifest, JUMBF, COSE, Merkle tree authentication, cryptographic watermarking, statistical watermarking, variation selector markers, ZWC markers, provenance markers, invisible embedding, sentence-level attribution, document-level signing, willful infringement, innocent infringement, formal notice, quote integrity verification, content authenticity, Content Authenticity Initiative (CAI), digital source type, IPTC, perceptual hash (pHash), fingerprinting, ingredient chain, provenance chain, EU AI Act, Article 52, machine-readable rights, robots.txt, TDM reservation, C2PA 2.3, Section A.7, text provenance, image provenance, audio provenance, video provenance, live stream provenance, content licensing, coalition licensing, self-service licensing
- [ ] 8.3 Add `DefinedTermSet` JSON-LD schema with each term as a `DefinedTerm`
- [ ] 8.4 Add AISummary component with terminology hub summary
- [ ] 8.5 Add anchor links for each term (e.g., `/glossary#c2pa-manifest`) for use in contextual linking across site
- [ ] 8.6 Add alphabetical navigation and search/filter functionality

### 9.0 AI Optimization (LLM Crawlers, AI Search, Citation Engines)

Ensure all content is optimized for AI tools that visit the site: LLM crawlers (GPTBot, Claude-Web, CCBot), AI search engines (Perplexity, SearchGPT, Gemini), and citation/attribution systems.

- [ ] 9.1 Update `public/llms.txt`
  - [ ] 9.1.1 Fix C2PA attribution to specify Section A.7 (not "authored the C2PA standard")
  - [ ] 9.1.2 Add the three pillar pages as primary resources with summaries
  - [ ] 9.1.3 Add comparison pages section with one-line summaries
  - [ ] 9.1.4 Add glossary page reference
  - [ ] 9.1.5 Add media type coverage section listing all 31 MIME types by category
  - [ ] 9.1.6 Add v2.0.0 API summary with unified `/sign/media` endpoint
  - [ ] 9.1.7 Add FAQ entries for new content topics (what is content provenance, how C2PA works across media types, how verification works, EU AI Act compliance)
  - [ ] 9.1.8 Add "Content Provenance Infrastructure" positioning throughout (not just "text provenance")
- [ ] 9.2 Create `public/llms-full.txt` -- extended version with comprehensive technical detail
  - [ ] 9.2.1 Include full format support matrix (31 MIME types with embedding methods)
  - [ ] 9.2.2 Include API endpoint reference (sign, verify, media)
  - [ ] 9.2.3 Include competitive positioning summaries (vs. SynthID, WordProof, detection tools, access gates)
  - [ ] 9.2.4 Include pricing and tier information
  - [ ] 9.2.5 Include standards participation details (C2PA co-chair, Section A.7 authorship, task force members)
- [ ] 9.3 Update AISummary component usage across all pages
  - [ ] 9.3.1 Add AISummary to all three pillar pages with category-defining summaries
  - [ ] 9.3.2 Add AISummary to all comparison pages with competitive positioning summaries
  - [ ] 9.3.3 Add AISummary to glossary page
  - [ ] 9.3.4 Add AISummary to all format pages (templated, format-specific)
  - [ ] 9.3.5 Review and update existing AISummary props on homepage, solutions pages, tools pages
- [ ] 9.4 Add `data-ai-summary` semantic attributes to key content sections across new pages
- [ ] 9.5 Add structured citation metadata
  - [ ] 9.5.1 Add `citation` meta tags to pillar and technical pages (title, author, date, URL) for AI citation systems
  - [ ] 9.5.2 Add `dcterms` metadata (Dublin Core) to pillar pages for academic and institutional crawlers
- [ ] 9.6 Update `public/robots.txt`
  - [ ] 9.6.1 Add reference to `llms-full.txt`
  - [ ] 9.6.2 Verify all new page paths are crawlable (no accidental disallow patterns)
  - [ ] 9.6.3 Add Perplexity bot, Google-Extended, and other emerging AI crawlers to explicit allow list
- [ ] 9.7 Add `.well-known/ai-plugin.json` manifest (if applicable to emerging AI tool discovery standards)

### 10.0 Technical SEO Infrastructure

Expand sitemap, add missing structured data types, implement internal linking overhaul, and add author pages.

- [ ] 10.1 Expand sitemap (`src/app/sitemap.ts`)
  - [ ] 10.1.1 Add all three pillar pages with priority 0.9
  - [ ] 10.1.2 Add all cluster pages with priority 0.7
  - [ ] 10.1.3 Add all comparison pages with priority 0.7
  - [ ] 10.1.4 Add all 31 format pages with priority 0.6
  - [ ] 10.1.5 Add all vertical pages with priority 0.7
  - [ ] 10.1.6 Add glossary page with priority 0.7
  - [ ] 10.1.7 Add author pages with priority 0.5
  - [ ] 10.1.8 Verify total sitemap URL count exceeds 150
- [ ] 10.2 Add BreadcrumbList schema
  - [ ] 10.2.1 Create `src/components/seo/Breadcrumbs.tsx` component rendering both visible breadcrumbs and BreadcrumbList JSON-LD
  - [ ] 10.2.2 Add to all pillar pages: Home > [Pillar Name]
  - [ ] 10.2.3 Add to all cluster pages: Home > [Pillar Name] > [Cluster Page]
  - [ ] 10.2.4 Add to all format pages: Home > Content Provenance > [Media Category] > [Format]
  - [ ] 10.2.5 Add to all comparison pages: Home > Compare > [Comparison]
  - [ ] 10.2.6 Add to glossary: Home > Glossary
- [ ] 10.3 Create author pages
  - [ ] 10.3.1 Create `src/app/authors/erik-svilich/page.tsx` -- Erik Svilich profile with E-E-A-T credentials (C2PA Section A.7 author, Co-Chair of Text Provenance Task Force, Founder and CEO, patent holder ENC0100)
  - [ ] 10.3.2 Create `src/app/authors/matt-kaminsky/page.tsx` -- Matt Kaminsky profile with E-E-A-T credentials (CCO, 13+ years digital media/ad-tech, Digimarc/Via Licensing experience)
  - [ ] 10.3.3 Add Person JSON-LD schema to each author page
  - [ ] 10.3.4 Update blog post author bylines to link to author pages
  - [ ] 10.3.5 Update BlogPosting schema to reference author page URLs
- [ ] 10.4 Internal linking overhaul
  - [ ] 10.4.1 Create `src/components/content/InternalLink.tsx` utility component for consistent keyword-rich anchor text (auto-links first mention of key terms per page)
  - [ ] 10.4.2 Audit all 27 existing blog posts: add contextual links to pillar pages (first mention of "content provenance" links to `/content-provenance`, first mention of "C2PA" links to `/c2pa-standard`, first mention of "cryptographic watermarking" links to `/cryptographic-watermarking`)
  - [ ] 10.4.3 Audit all existing landing pages (homepage, solutions, tools, demos): add contextual pillar links
  - [ ] 10.4.4 Add cross-links between pillar pages (each pillar links to the other two)
  - [ ] 10.4.5 Add "Related Content" sections to cluster pages linking to sibling clusters and parent pillar
  - [ ] 10.4.6 Add contextual glossary links (key terms in body text link to `/glossary#{term}`)
- [ ] 10.5 Page performance
  - [ ] 10.5.1 Verify all new pages use static generation (SSG via `generateStaticParams`) not client-side rendering
  - [ ] 10.5.2 Ensure all new pages pass Core Web Vitals thresholds (LCP < 2.5s, FID < 100ms, CLS < 0.1)
  - [ ] 10.5.3 Add `loading="lazy"` to below-fold images on new pages
  - [ ] 10.5.4 Verify no hydration mismatches on new pages

### 11.0 Blog Content Acceleration

Increase blog cadence to 2 posts/week. Define the first 20 post topics aligned with the pillar-cluster architecture. Each post links to at least one pillar page and one cluster page.

- [ ] 11.1 Define blog content calendar (first 20 posts)
  - [ ] 11.1.1 Technical depth posts (Monday cadence):
    1. "Content Provenance Is Not Content Detection: The Technical Distinction"
    2. "31 Media Types, One Standard: Inside Encypher's v2.0.0 API"
    3. "How C2PA Manifests Are Embedded in JPEG Files"
    4. "Merkle Trees for Content: How Sentence-Level Attribution Works"
    5. "Live Stream Provenance: Per-Segment C2PA Manifests Explained"
    6. "Cryptographic Watermarking vs. Statistical Watermarking: A Technical Comparison"
    7. "How Free Verification Works Across 31 Media Types"
    8. "JUMBF Containers and COSE Signatures: The Structure of a C2PA Manifest"
    9. "Why Blockchain Timestamping Is Not Content Provenance"
    10. "Perceptual Hashing for Images: Finding Derivatives of Signed Content"
  - [ ] 11.1.2 Market/regulatory/use-case posts (Thursday cadence):
    1. "The EU AI Act Requires Content Provenance by August 2026. Here Is What That Means."
    2. "Content Provenance for Academic Publishers: Protecting Research Integrity"
    3. "The Three Layers of Content Protection: Access Control, Provenance, Attribution"
    4. "From Innocent Infringement to Willful: How Formal Notice Changes the Legal Calculus"
    5. "Why Audio Provenance Matters: Podcasts, Music, and the AI Training Pipeline"
    6. "Content Provenance for News Publishers: The AP, Reuters, and BBC Precedent"
    7. "Video Provenance in the Age of Deepfakes: Why Detection Is Not Enough"
    8. "The Document Provenance Gap: PDFs, EPUBs, and Legal Filings"
    9. "What Publishers Need to Know About the C2PA Conformance Program"
    10. "Machine-Readable Rights: How Content Licensing Becomes Automated"
- [ ] 11.2 Write and publish first 4 posts (launch week batch)
  - [ ] 11.2.1 Post 1: "Content Provenance Is Not Content Detection: The Technical Distinction" (links to `/content-provenance` and `/compare/content-provenance-vs-content-detection`)
  - [ ] 11.2.2 Post 2: "31 Media Types, One Standard: Inside Encypher's v2.0.0 API" (links to `/c2pa-standard/media-types` and `/content-provenance/verification`)
  - [ ] 11.2.3 Post 3: "The EU AI Act Requires Content Provenance by August 2026" (links to `/content-provenance/eu-ai-act` and `/content-provenance/for-enterprises`)
  - [ ] 11.2.4 Post 4: "Cryptographic Watermarking vs. Statistical Watermarking: A Technical Comparison" (links to `/cryptographic-watermarking/vs-statistical-watermarking` and `/compare/encypher-vs-synthid`)
- [ ] 11.3 Establish blog content workflow
  - [ ] 11.3.1 Document blog post template with required elements: frontmatter (title, date, excerpt, author, image, tags), AISummary component, minimum 2 internal links (1 pillar + 1 cluster), BlogPosting JSON-LD via existing schema, keyword-rich H2/H3 structure
  - [ ] 11.3.2 Add blog tags for new content categories: "ContentProvenance," "C2PA," "CryptographicWatermarking," "MediaTypes," "EUAIAct," "Comparison"

### 12.0 Existing Content Updates

Update existing pages and blog posts to align with the new content architecture, internal linking strategy, and corrected C2PA attribution.

- [ ] 12.1 Update homepage (`src/app/page.tsx`)
  - [ ] 12.1.1 Add contextual links to the three pillar pages in hero/body content
  - [ ] 12.1.2 Add "Content Provenance Hub" section linking to pillar pages, format pages, and comparison pages
  - [ ] 12.1.3 Update AISummary to reference pillar pages as primary resources
- [ ] 12.2 Update solutions pages
  - [ ] 12.2.1 `/solutions/publishers` -- add links to `/content-provenance/for-publishers`, `/compare/encypher-vs-tollbit`, `/content-provenance/text`
  - [ ] 12.2.2 `/solutions/ai-companies` -- add links to `/content-provenance/for-ai-companies`, `/c2pa-standard`, `/content-provenance/verification`
  - [ ] 12.2.3 `/solutions/enterprises` -- add links to `/content-provenance/for-enterprises`, `/content-provenance/eu-ai-act`, `/c2pa-standard/implementation-guide`
- [ ] 12.3 Update existing landing pages
  - [ ] 12.3.1 `/ai-copyright-infringement` -- add links to `/cryptographic-watermarking/legal-implications` and `/content-provenance`
  - [ ] 12.3.2 `/deepfake-detection` -- add links to `/compare/content-provenance-vs-content-detection` and `/cryptographic-watermarking`
  - [ ] 12.3.3 `/ai-detector` -- add links to `/compare/encypher-vs-detection-tools` and `/content-provenance`
  - [ ] 12.3.4 `/platform` -- add links to `/c2pa-standard/media-types` and `/content-provenance/verification`
- [ ] 12.4 Update all 27 existing blog posts
  - [ ] 12.4.1 Add contextual internal links to pillar pages (first mention of key terms per post)
  - [ ] 12.4.2 Fix any C2PA attribution overclaims (per Task 1.3)
  - [ ] 12.4.3 Add or update tags to align with new tag taxonomy
- [ ] 12.5 Update navigation
  - [ ] 12.5.1 Add "Resources" dropdown to navbar with links to: Content Provenance (pillar), C2PA Standard (pillar), Glossary, Compare, Blog
  - [ ] 12.5.2 Add footer links to pillar pages, glossary, and comparison hub

### 13.0 Build Verification and Quality Assurance

- [ ] 13.1 Run `next build` -- confirm zero errors across all new and modified pages
- [ ] 13.2 Verify sitemap generates correctly with 150+ URLs
- [ ] 13.3 Verify all JSON-LD schemas validate (use Google Rich Results Test or Schema.org validator)
- [ ] 13.4 Verify all canonical URLs are correct and self-referencing
- [ ] 13.5 Verify all internal links resolve (no 404s)
- [ ] 13.6 Verify all new pages include: title tag, meta description, OG tags, Twitter card, canonical URL, AISummary, at least one JSON-LD schema
- [ ] 13.7 Verify BreadcrumbList schema renders correctly on hierarchical pages
- [ ] 13.8 Verify llms.txt and llms-full.txt are accessible and accurate
- [ ] 13.9 Verify robots.txt allows all new page paths
- [ ] 13.10 Verify all 31 format pages render with correct format-specific data
- [ ] 13.11 Spot-check Core Web Vitals on 5 representative new pages
- [ ] 13.12 Verify no C2PA attribution overclaims remain anywhere on site (grep for "authored the C2PA standard" or "authored the C2PA text standard" -- zero results expected)

## Implementation Phases

### Phase 1: Foundations (Weeks 1-2)
Tasks: 1.0 (attribution fix), 2.0 (SEO infrastructure), 9.1-9.2 (AI optimization files)
New pages: 0 (infrastructure only)
Target: all new page types have metadata generators, schemas, and AI optimization ready

### Phase 2: Pillar Pages (Weeks 2-4)
Tasks: 3.0 (three pillar pages), 8.0 (glossary), 10.2-10.3 (breadcrumbs, author pages)
New pages: ~6 (3 pillars + glossary + 2 author pages)
Target: canonical ranking targets live and indexable

### Phase 3: Cluster and Comparison Pages (Weeks 3-6)
Tasks: 4.0 (22 cluster pages), 5.0 (8 comparison pages)
New pages: ~30
Target: full pillar-cluster architecture live

### Phase 4: Programmatic and Vertical Pages (Weeks 5-8)
Tasks: 6.0 (31 format pages), 7.0 (6 vertical pages)
New pages: ~37
Target: long-tail keyword coverage and industry targeting

### Phase 5: Internal Linking and Existing Content (Weeks 6-9)
Tasks: 10.4 (linking overhaul), 12.0 (existing content updates)
New pages: 0 (updates only)
Target: keyword equity flowing across full site architecture

### Phase 6: Blog Acceleration and QA (Weeks 7-12)
Tasks: 11.0 (blog acceleration), 13.0 (build verification)
New pages: 4 launch-week posts + 2/week ongoing
Target: 200+ indexed pages, all quality checks passing

## Success Criteria

- Zero instances of "authored the C2PA standard" or "authored the C2PA text standard" anywhere on the site (accurate attribution: "authored Section A.7")
- Three pillar pages live and indexed for "content provenance," "C2PA standard," and "cryptographic watermarking"
- 31 programmatic format pages live and indexed
- 7+ comparison pages live and indexed
- Glossary page live with 40+ term definitions
- 150+ URLs in sitemap (up from 40+)
- All pages include AISummary component and at least one JSON-LD schema
- BreadcrumbList schema on all hierarchical pages
- Author pages live with Person schema and E-E-A-T credentials
- llms.txt and llms-full.txt updated with new content architecture
- Blog cadence at 2 posts/week
- `next build` succeeds with zero errors
- All internal links resolve (no 404s)
- All new pages use static generation (SSG)

## Completion Notes

(Filled when PRD is complete.)
