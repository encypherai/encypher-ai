---
# Research Notes
## Topic
Sentence-Level Attribution: Why Paragraph-Level Proof Is Not Enough

## Proposed Thesis
AI copyright settlements are calculated on the wrong unit of measurement: publishers collect flat
fees per book while AI systems extract value per sentence, and without sentence-level provenance
infrastructure - now standardized in C2PA Section A.7 - every future settlement will systematically
underpay rightsholders by orders of magnitude.

## Suggested Title
AI Copyright Settlements Are Calculated on the Wrong Unit

## Suggested Tags
C2PA, AI Copyright, Content Provenance, Copyright Law, AI Training Data, Content Authentication,
Publisher Strategy, Legal Analysis

---

## Sources

1. URL: https://www.axios.com/2025/09/05/anthropic-ai-copyright-settlement
   Date: 2025-09-05
   Key finding: Anthropic agreed to pay approximately $3,000 per book in its $1.5 billion
   AI copyright settlement (Bartz v. Anthropic). The headline confirms the per-work rate:
   "Anthropic to pay $3,000 per book in $1.5 billion AI copyright settlement."
   Exact quotes: Headline: "Anthropic to pay $3,000 per book in $1.5 billion AI copyright
   settlement" (confirmed from URL/headline). Note: writer must access full article to pull
   any body text verbatim.
   Backup URL: https://authorsguild.org/advocacy/artificial-intelligence/what-authors-need-to-know-about-the-anthropic-settlement/
   - Authors Guild confirms: "Rightsholders can expect at least $3,000 per title (less costs
   and fees)" and notes this amount "may be shared, with half generally going to the publisher
   depending on the author's contract."
   Supports: Core thesis - the unit of settlement is the work (book), not the usage (sentence,
   paragraph, or inference call). The flat fee is unrelated to how much of any work was actually
   extracted or used.

2. URL: https://authorsguild.org/advocacy/artificial-intelligence/what-authors-need-to-know-about-the-anthropic-settlement/
   Date: 2025-09-05 (updated through March 2026)
   Key finding: Claim deadline March 30, 2026. Final approval hearing April 23, 2026.
   The settlement covers an estimated 500,000 books from shadow libraries (Library Genesis,
   Pirate Library Mirror). Settlement awards are fixed per ISBN/ASIN, regardless of how
   frequently Anthropic queried content from those works during Claude training.
   Exact quotes: "Rightsholders can expect at least $3,000 per title (less costs and fees),
   which will be shared among the rightsholders for that title (if there is more than one
   rightsholder)." - verify verbatim against live page before quoting.
   Backup URL: https://www.npr.org/2025/09/05/nx-s1-5529404/anthropic-settlement-authors-copyright-ai
   Supports: Documents that settlement math ignores differential usage - a book cited 10,000
   times in Claude training gets the same $3,000 as one cited once.

3. URL: https://www.sternekessler.com/news-insights/insights/discovery-of-training-data-in-ai-litigation/
   Date: 2024-2025 (confirm exact date on page)
   Key finding: Discovery of AI training data is technically infeasible at scale. Plaintiffs
   reviewing one of OpenAI's training datasets were reportedly forced to abandon searching for
   one copyrighted work because it would have taken more than six hours to complete. This
   illustrates why per-sentence attribution cannot be established retroactively from raw training
   corpora.
   Exact quotes: Do not quote verbatim without accessing the full article directly. Summarize as:
   according to Sterne Kessler's analysis of AI discovery disputes, locating a single copyrighted
   work in OpenAI training data took so long that plaintiffs had to cancel the search.
   Backup URL: https://academic.oup.com/jiplp/article/20/3/182/7922541
   - Oxford JIPLP article on AI training data transparency confirms: "datasets derived from
   non-web sources pose significant challenges in terms of attribution and often lack inherent
   metadata linking them to original rightsholders."
   Supports: The retroactive attribution problem. Without provenance embedded at creation time,
   sentence-level traceability is technically infeasible even under court order.

4. URL: https://digital-strategy.ec.europa.eu/en/library/commission-publishes-second-draft-code-practice-marking-and-labelling-ai-generated-content
   Date: March 2026 (second draft published)
   Key finding: The European Commission published the second draft of its Code of Practice
   under EU AI Act Article 50 in March 2026. The draft specifies a "two-layered marking
   approach involving secured metadata and watermarking" for AI-generated content, with an
   optional fingerprinting layer. Feedback period closes March 30, 2026. Final code expected
   June 2026. Article 50 obligations become enforceable August 2, 2026.
   Exact quotes: Draft describes "a revised two-layered marking approach involving secured
   metadata and watermarking, optional fingerprinting and logging, and protocols for detection
   and verification." - verify verbatim from page before quoting.
   Backup URL: https://artificialintelligenceact.eu/article/50/
   - Confirms Article 50(2): "Providers of AI systems, including general-purpose AI systems,
   generating synthetic audio, image, video or text content, shall ensure that the outputs
   of the AI system are marked in a machine-readable format and detectable as artificially
   generated or manipulated."
   Supports: The regulatory angle - EU is mandating machine-readable marking at the output
   level, but publishers still lack the parallel infrastructure to embed machine-readable
   provenance at the source (input) level, which is where attribution begins.

5. URL: https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html
   Date: 2026-01-08 (C2PA 2.3 published)
   Key finding: C2PA Specification 2.3 Section A.7, "Embedding Manifests into Unstructured
   Text," defines how C2PA manifests are embedded into text using Unicode Variation Selectors
   as non-rendering characters. This provides a hard binding mechanism for text content
   provenance. Encypher co-chairs the C2PA Text Provenance Task Force and authored Section A.7.
   The standard allows signed, machine-readable provenance claims to travel with text at any
   granularity - including sentence or paragraph level - as content is excerpted and distributed.
   Exact quotes: From search result confirmation: "For unstructured text assets that have a
   C2PA Manifest embedded using Unicode Variation Selectors as described in Section A.7,
   'Embedding Manifests into Unstructured Text', a data hash assertion shall be used."
   Verify full section wording against the live spec before quoting.
   Backup URL: https://c2pa.org/news/
   Supports: The technical solution. Section A.7 is the infrastructure layer that makes
   sentence-level provenance possible. Without it, there is no cryptographic chain of custody
   for individual text segments as they travel through AI pipelines.

---

## Counterarguments Found

- The $1.5B Anthropic settlement is the largest copyright settlement in US history - far from
  a failure, it establishes that AI training on copyrighted works carries real financial
  liability. Critics of the thesis will argue that publishers have already "won" and that
  incremental improvements to settlement math are secondary to establishing liability at all.
  Rebuttal: liability is established, but compensation is permanently severed from actual
  usage - the structural flaw will compound over decades of AI development.

- Publishers lack the leverage to demand per-sentence licensing regardless of provenance
  infrastructure. Sentence-level metadata does not automatically translate to per-sentence
  royalties in the absence of legal frameworks requiring it. The settlement structure is
  partly a function of class action mechanics, not just technical measurement.
  Rebuttal: provenance infrastructure is a prerequisite, not a guarantee. EU AI Act Article 50
  and emerging TDM opt-out frameworks reward publishers who can prove machine-readable rights
  reservations. The legal framework is being built now - publishers who invest in infrastructure
  today will have standing to claim under it; those who do not, will not.

- Retroactive provenance is technically possible via server log analysis and URL-level scraping
  records. Some AI companies retained crawl logs that partially document which documents were
  ingested. Plaintiffs in NYT v. OpenAI relied on output memorization tests rather than
  training corpus analysis.
  Rebuttal: server logs prove document-level ingestion, not sentence-level usage or differential
  contribution to model weights. Memorization tests work for verbatim reproduction but cannot
  quantify the licensing value of paraphrased or distilled sentences - which is the dominant
  mode of AI value extraction.

---

## Recommended Post Structure

- Opening: Lead with the Anthropic $3,000-per-book figure. Frame it as a seemingly large
  number that reveals something disturbing - the settlement fund is divorced from usage.
  A book cited 50,000 times in training gets the same fee as one cited once. Ask: does that
  feel like justice, or accounting?

- Section 1 - The Unit Problem: Explain how the settlement math works. Per-work, per-ISBN,
  per-ASIN - the legal unit of copyright is the work. But AI systems do not consume works;
  they consume sentences, paragraphs, and semantic patterns. Walk through why this mismatch
  is structural, not incidental. Use the Sterne Kessler discovery finding as evidence that
  retroactive sentence-level attribution is technically infeasible even under court compulsion.

- Section 2 - What AI Actually Extracts: Explain how language models learn from text.
  Training does not "read" a book - it passes sentences through gradient descent millions
  of times. A single high-quality sentence on a technical topic may contribute more to model
  capability than an entire chapter of filler prose. The economic unit of value is the
  sentence (or semantic unit), not the work. This is not speculative - it is the architecture.

- Section 3 - The Provenance Solution (C2PA A.7): Introduce C2PA Section A.7 as the
  technical standard that closes this gap. Explain that C2PA manifests can be embedded into
  text at any granularity using Unicode Variation Selectors - they travel with the content,
  survive copy-paste, and provide a cryptographic chain of custody from author to AI pipeline.
  Note Encypher's role in co-authoring this section. Connect to EU AI Act Article 50's
  two-layered machine-readable marking requirement as regulatory confirmation that the industry
  is moving toward provenance-first infrastructure.

- Section 4 - The Counterargument and Rebuttal: Steel-man the "settlements are working"
  argument. $1.5B is not nothing. Licensing deals are forming (OpenAI/News Corp, OpenAI/AP,
  UMG/Udio). But licensing deals are also per-work, per-outlet, negotiated in bulk - not
  per-usage. The publisher who has C2PA provenance in their content will have a negotiating
  floor; the publisher who does not will continue to accept whatever the AI company offers.

- Section 5 - Implications for Publishers: Concrete steps. Implement sentence-level C2PA
  provenance now, before the next wave of AI model training. Register machine-readable
  rights reservations under EU AI Act TDM opt-out frameworks. Monitor EU AI Act Article 50
  Code of Practice (final version June 2026, enforceable August 2026) for infrastructure
  requirements that publishers can align to.

- Closing: The Anthropic settlement is a landmark. It proves liability. But it also proves
  that the current framework compensates authors the way flat-rate music licensing compensated
  musicians in the early streaming era - a bulk fee that ignores differential usage. Spotify
  eventually moved toward per-stream royalties. AI licensing will follow. Publishers who build
  the provenance infrastructure now will be positioned to claim that value. Those who wait
  for the next settlement will collect another flat check.
---
