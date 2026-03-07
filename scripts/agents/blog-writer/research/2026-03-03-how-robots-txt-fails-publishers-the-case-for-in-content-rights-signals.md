---
# Research Notes
## Topic
How Robots.txt Fails Publishers: The Case for In-Content Rights Signals

## Proposed Thesis
Robots.txt is a 1994 crawl-politeness protocol with no legal standing as a rights reservation
mechanism - a U.S. federal court confirmed this in December 2025 - and its deeper architectural
flaw (it cannot travel with syndicated content) means publishers need C2PA in-content credentials
as the only technically sound answer to the rights-reservation problem the EU is now scrambling
to define.

## Suggested Title
Robots.txt Is Not a Rights Signal: Why Publishers Need In-Content Credentials

## Suggested Tags
C2PA, Content Provenance, Publisher Licensing, EU AI Act, AI Governance, Publisher Strategy,
Content Authentication, Legal Analysis, AI Training Data, Copyright Law

## Sources

1. URL: https://law.justia.com/cases/federal/district-courts/new-york/nysdce/1:2025cv04315/643043/302/
   Date: 2025-12-18
   Key finding: In Ziff Davis, Inc. v. OpenAI, Inc. (S.D.N.Y.), Judge Sidney H. Stein ruled
   that a robots.txt file is not a "technological measure that effectively controls access"
   to copyrighted works under the DMCA. The court compared it to a "keep off the grass" sign
   because it relies on readers choosing to comply rather than enforcing any barrier. OpenAI's
   motion to dismiss the robots.txt-based circumvention claim (DMCA Section 1201) was granted.
   Exact quotes: The court compared robots.txt to a "keep off the grass" sign (per court
   commentary reproduced in the Goldman Technology & Marketing Law Blog below; exact verbatim
   language from the opinion not confirmed - do not quote directly without reading the opinion).
   Backup URL: https://blog.ericgoldman.org/archives/2025/12/are-robots-txt-instructions-legally-binding-ziff-davis-v-openai.htm
   (law professor analysis confirming the ruling and its reasoning)
   Supports: Central thesis - robots.txt has no legal standing as a rights-reservation mechanism

2. URL: https://digital-strategy.ec.europa.eu/en/consultations/commission-launches-consultation-protocols-reserving-rights-text-and-data-mining-under-ai-act-and
   Date: 2025-12-01
   Key finding: The European Commission launched a stakeholder consultation on machine-readable
   protocols for reserving rights against text and data mining under the AI Act and the GPAI
   Code of Practice. The consultation period ran from December 1, 2025 to January 23, 2026.
   The Commission explicitly seeks protocols that go beyond existing conventions such as
   robots.txt, seeking standardized, machine-readable solutions that can be implemented
   consistently and interoperably across different media, languages, and sectors. After
   publication of agreed solutions, the list will be reviewed at least every two years.
   Exact quotes: None confirmed verbatim from this source.
   Backup URL: https://cadeproject.org/updates/commission-opens-consultation-on-machine-readable-copyright-opt-out-protocols-under-the-ai-act/
   Supports: The EU itself is acknowledging robots.txt is insufficient and actively seeking
   something better - publishers who rely on robots.txt today will not satisfy the standard
   being defined right now.

3. URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5555040
   Date: 2025-10-01
   Key finding: Nathan Reitinger's paper "Measured Failures of robots.txt: Legal and Empirical
   Insights for Regulating Robots" uses empirical measurement to show that unless a website is
   in the top 1% of the most popular and best-resourced sites in the world, robots.txt is simply
   not used to control AI crawlers effectively. The paper argues for a purpose-based, opt-in
   (allow-list) approach to replace the current opt-out regime.
   Exact quotes: "unless a website is one of the most popular and best-resourced websites in the
   world - the top 1% - robots.txt is simply not used to control AI" (from SSRN abstract
   summary; confirm exact wording before quoting directly from paper).
   Backup URL: none found for same empirical finding from a second independent source.
   Supports: Empirical evidence that robots.txt fails the vast majority of publishers even
   before the legal and architectural limitations are considered.

4. URL: https://www.theregister.com/2025/12/08/publishers_say_no_ai_scrapers/
   Date: 2025-12-08
   Key finding: Data from Tollbit (a crawler monetization company) shows that across all AI
   bots, 13.26 percent of requests ignored robots.txt directives in Q2 2025, up from 3.3
   percent in Q4 2024. This is a four-fold increase in non-compliance in six months, meaning
   even voluntary compliance is eroding rapidly.
   Exact quotes: None confirmed verbatim.
   Backup URL: none found for the same Tollbit figure from a second independent source.
   Note: figure originates from Tollbit's proprietary data; cited as reported by The Register.
   Supports: Even where robots.txt is legally and technically possible to enforce, compliance
   is declining rapidly - making a crawl-server-dependent mechanism structurally unreliable.

5. URL: https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html
   Date: 2026-01-08
   Key finding: Section A.7 of the C2PA 2.3 specification, published January 8, 2026, defines
   the mechanism for embedding machine-readable content credentials - including rights and
   licensing assertions - directly into unstructured text using zero-width Unicode characters.
   Encypher co-authored this section. The resulting credentials travel with the content through
   any system it passes through, including syndication feeds, cached copies, and RAG indexes.
   Exact quotes: None; the spec itself is the primary source.
   Backup URL: https://c2pa.org/ (C2PA consortium homepage confirming the standard's scope)
   Supports: C2PA in-content credentials are the technical answer because they solve the
   syndication problem - the credential is embedded in the text itself, not stored externally.

## Counterarguments Found

- Server-level blocking (Cloudflare AI bot filtering, CDN-level controls, IP blocklists) is a
  practical alternative that many publishers are already deploying and does not require any new
  standard. Publishers who block at the server level prevent the content from being scraped in
  the first place. Rebuttal: server-level blocking cannot reach content that has already been
  scraped, syndicated, cached, or re-published by third parties before the block was set up -
  and it cannot communicate affirmative licensing terms, only denial.

- AI companies are increasingly willing to sign commercial licensing agreements directly with
  publishers (Amazon-NYT, Amazon-Hearst/Conde Nast, 2025 deals). If commercial licensing is
  the practical outcome, the infrastructure question may be moot. Rebuttal: licensing deals
  cover named parties and specific time periods; they create no per-query audit record showing
  that a given retrieval was authorized at the moment it occurred, and they do not cover the
  long tail of content outside the signatories' catalogs.

- Robots.txt compliance is improving: major AI companies including OpenAI, Google, and Anthropic
  have publicly committed to honoring it. Rebuttal: voluntary commitments from the top players
  do not bind the long tail of smaller models, open-source scrapers, or non-US actors; and as
  Tollbit's Q2 2025 data shows, non-compliance is increasing not decreasing, even among bots
  claiming to honor robots.txt.

## Recommended Post Structure

- Opening: Start with the Ziff Davis ruling (December 18, 2025). Courts have now decided:
  robots.txt is legally equivalent to a "keep off the grass" sign. Three years of publisher
  energy spent updating robots.txt files - energy that may not have achieved what publishers
  assumed it did. The question is not whether AI companies honor robots.txt; the question is
  what actually constitutes a legally and technically sound rights reservation.

- Section 1 - What robots.txt actually is: The standard was written in 1994 as a crawl-
  politeness protocol to prevent server overload, not to signal intellectual property rights.
  It has no authentication mechanism (any bot can claim any identity), no legal binding force
  (confirmed by Ziff Davis), and no way to express granular permissions (cannot say "you may
  index for search but not train on this"). Explain these three failure modes without jargon.

- Section 2 - The fourth failure mode that no server-level fix can address: robots.txt only
  covers content on your origin server at the moment of the crawl. Content that leaves your
  server through syndication, licensing, caching, or even a single copy-paste carries no rights
  signal at all. The moment an article is published on an aggregator, an API feed, or a partner
  site, robots.txt on your domain is irrelevant. For the vast majority of publishers whose
  content circulates freely, this is the decisive failure. Use the Reitinger empirical finding
  that robots.txt is effectively unused by the bottom 99% of websites to ground this section.

- Section 3 - The EU is designing a replacement right now (steelman and rebuttal): The EU
  Commission's December 2025 consultation on machine-readable TDM opt-out protocols shows that
  regulators understand the problem. The GPAI Code of Practice commits signatories to honor
  opt-out protocols "in addition to existing conventions such as robots.txt" - language that
  implicitly acknowledges robots.txt is a baseline, not a ceiling. Steelman: maybe regulators
  will converge on a robots.txt successor and AI companies will honor it. Rebuttal: any header-
  or file-based signal still faces the syndication problem; only credentials embedded in content
  can travel with that content. The Commission's consultation explicitly asks whether protocols
  can be implemented across different media - the answer C2PA 2.3 Section A.7 provides for text
  is the only standard that already exists.

- Section 4 - What in-content credentials solve: C2PA content credentials are embedded directly
  in the text, not stored in a separate file on the origin server. They are cryptographically
  signed, so they cannot be stripped without detection. They can carry granular assertions:
  rights holder identity, licensing terms, TDM permission flags, rights resolution URL. A C2PA-
  aware crawler reads the credential at the moment of retrieval, not the moment of first
  crawl. Encypher co-authored Section A.7 of C2PA 2.3, published January 8, 2026, which defines
  exactly this mechanism for unstructured text. Publishers who sign their content today are
  building the audit record that licensing deals and future regulation will require.

- Closing: The EU Commission's consultation closed January 23, 2026. The list of agreed machine-
  readable opt-out protocols will be published and reviewed at least every two years. Publishers
  who are waiting for the standard to be finalized before acting are waiting to learn which door
  to walk through while the room is being designed around a door that already exists. The
  specific call to action: sign your content with C2PA credentials now - not to check a
  compliance box, but because the credential is the only rights signal that will still be
  present when your article appears in a RAG corpus six months after it left your server.
---
