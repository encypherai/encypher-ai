# Encypher Corporation: Public Comment on the EU AI Act Code of Practice

## Second Draft - Code of Practice for Transparency of AI-Generated Content

**Submitted by:** Erik Svilich, Co-Chair, C2PA Text Provenance Task Force; Founder and CEO, Encypher Corporation

**Date:** [Submission Date]

**Re:** Second Draft Code of Practice for Transparency of AI-Generated Content under Articles 50(2) and 50(4) of the EU AI Act

**Status:** DRAFT - Pending EU regulatory counsel review before filing

**Version:** 3.0

**Distribution:** Executive Team, Legal

---

## Internal Context (Remove Before Filing)

### Purpose

This document is Encypher's public comment submission to the EU consultation on the second draft Code of Practice for transparency of AI-generated content. Written from Erik's position as C2PA Text Provenance Task Force Co-Chair. Framed as technical standards expertise, not product advocacy.

### Key Strategic Lines to Maintain

1. **C2PA = document-level provenance (open standard, we co-authored it)**
2. **Encypher's patent-pending technology = segment-level granularity down to per-character (proprietary, ENC0100 83 claims)**
3. These are distinct layers. The submission advocates for C2PA as the regulatory baseline. It does NOT claim C2PA provides segment-level capabilities. It notes that segment-level granularity exists as a best-practice enhancement beyond the standard.
4. C2PA AI assertion vocabularies already exist in the spec (`c2pa.ai_generated`, `c2pa.ai_training`, etc.). These are not something to be built.
5. Our free Chrome extension (no account required) already surfaces C2PA AI assertions to end users on any webpage. The deployer-side "gap" is narrow: it is about deployers rendering visible labels in their own page UI, not about detection or display.

### Voice and Style

This submission follows the Orwell/Lewis/Economist register used in Encypher's published content:
- Plain declarative sentences. Active voice. No hedging.
- Single hyphens with spaces for parenthetical breaks. Never double hyphens in prose.
- No throat-clearing ("It is important to note," "It is worth mentioning").
- No performed authority ("The pattern is clear," "This is significant").
- Concrete scenarios before abstract analysis.
- Conclusions stated matter-of-factly. The evidence carries its own weight.
- Precise calibration on legal and regulatory claims.
- ASCII only. No em-dashes, smart quotes, or Unicode punctuation.

### Documents That Informed This Submission

- Encypher_GTM_Strategy.md (master positioning, standards authority narrative)
- Encypher_ICPs.md (ICP 3 David - Enterprise Risk Officer, EU AI Act deadline)
- Encypher_OpenSource_Strategy.md (open source vs. proprietary capability boundaries)
- Encypher_Future_Partnerships_Products.md (product roadmap, data custody)
- ENC0100_SPEC_EXTRACT.md (patent claims mapping)
- Enterprise API codebase (signing capabilities, short text handling, verification API)

### How to Use This Document After Filing

- **Press release:** Anchor on the submission date, lead with Co-Chair role
- **Prospect outreach:** Send summary (not full submission) to AP, Taylor & Francis, Snack-Media, Valnet, NMA with personalized cover note
- **Thought leadership:** Adapt into a LinkedIn article or trade publication op-ed
- **Sales collateral:** Create a one-page "EU AI Act Compliance Mapping" derivative for ICP 3 (David) conversations
- **Standards credibility:** Add to the narrative alongside C2PA co-chair role and January 8, 2026 publication

---

## Submission Text

*(Everything below this line is the filing-ready public comment. Remove the Internal Context section above before submitting.)*

---

Dear Members of the Drafting Committee,

I am the Co-Chair of the C2PA Text Provenance Task Force and the specification author for C2PA 2.3 Section A.7 ("Embedding Manifests into Unstructured Text," published January 8, 2026). The task force includes Google, BBC, OpenAI, Adobe, and Microsoft. I submit these comments as technical input from the task force responsible for the text provenance standard this Code references.

The second draft is stronger than the first. The consolidation of measures, the added flexibility, and the removal of the AI-generated versus AI-assisted taxonomy all move the framework toward something that can be implemented and enforced in practice. One pattern warrants attention: the shift from mandatory to voluntary language between drafts. Several provisions that were requirements in the first draft are now "encouraged." Where this submission recommends strengthening specific provisions, it is because production-ready technology exists to meet the obligation and because voluntary compliance creates gaps the regulation was designed to close. Nine observations follow, each with a specific recommendation.

---

### 1. C2PA as the Reference Interoperability Framework

The two-layered marking approach in this draft, secured metadata combined with watermarking, only works if providers and deployers across all 27 member states use a common technical standard. Without one, each provider builds proprietary marking. Detection tools multiply. Cross-provider verification becomes impossible. Deployers face a matrix of incompatible formats.

C2PA 2.3, published January 8, 2026 and governed by the Joint Development Foundation under the Linux Foundation with over 100 member organizations, is the only published multi-stakeholder standard for content provenance with production implementations deployed at scale. The specification already defines machine-readable AI content assertion types (`c2pa.ai_generated`, `c2pa.ai_training`), providing the structured metadata vocabulary this Code requires. No competing standard offers equivalent multi-stakeholder governance, production deployment, media-type coverage, or established AI content assertion vocabularies.

C2PA manifests are cryptographically signed assertions about content origin, the AI system involved, and any human review. That is what "secured metadata" means in practice. Combined with invisible embedding techniques (the watermarking layer), this delivers the two-layered architecture the Code of Practice describes.

C2PA is an open specification. Anyone can implement it. Reference implementations are available under open-source licenses. Designating C2PA as the baseline creates interoperability, not vendor lock-in. GDPR references ISO standards for the same reason.

**Recommendation:** Designate C2PA as the reference technical standard for content provenance marking under Article 50, while permitting additional complementary methods above this baseline.

---

### 2. The Value of Granular, Sub-Document Marking

The draft contemplates document-level marking. A document is AI-generated or it is not. The C2PA standard, as published in Section A.7, provides this document-level baseline: a cryptographically signed manifest attesting to the provenance of a document as a whole. That baseline is production-ready and sufficient for minimum compliance.

But content workflows do not produce clean documents. A news article contains an AI-generated summary alongside reporter-written analysis. A legal brief uses AI drafting for certain sections while counsel authors others. A corporate report blends AI-produced data summaries with human-written conclusions. In each case, the document is neither fully AI-generated nor fully human-authored. It is both.

Document-level marking forces a binary choice that does not match this reality. Technologies exist today that extend beyond the C2PA document-level baseline to authenticate individual sentences, paragraphs, or sections within a document, binding provenance to specific text segments rather than to the document as a whole. The result is provenance that can identify which portions of a document involved AI generation, detect tampering at the specific passage that was modified, and verify whether an individual quotation is accurate or fabricated.

These capabilities go beyond the C2PA standard. They are not required for minimum compliance. But they serve the regulation's transparency purpose more faithfully when content is hybrid, which is increasingly the norm.

**Recommendation:** Note that best-practice implementations may provide sub-document granularity beyond the document-level baseline, and that such granularity better serves the transparency objective for hybrid human-AI content.

---

### 3. Fingerprinting Should Be Recommended, Not Merely Optional

The draft makes fingerprinting and logging optional. For smaller providers, that is proportionate. For providers processing content at scale, it leaves a gap.

Watermarks embedded in text can be stripped by paraphrasing, summarization, translation, and restructuring. AI systems perform these transformations routinely. An AI model that ingests a watermarked article and outputs a paraphrased summary has consumed the original content but destroyed the watermark. The provenance signal disappears at exactly the point where it matters most.

Fingerprinting addresses this. Techniques such as locality-sensitive hashing identify content that has been transformed, not just copied verbatim. Fingerprinting is what distinguishes a detection framework that works only for exact copies from one that works for the derivatives AI systems actually produce.

Without fingerprinting at the provider level, the detection protocol the Code of Practice envisions has a structural limitation: it catches verbatim reproduction but misses paraphrased use. For providers whose systems ingest and transform millions of documents, that limitation is not marginal.

The privacy considerations the Committee weighed in making fingerprinting optional are real but addressable. Fingerprinting does not require linking content to individual identity. A provenance attestation system functions as a notary: it certifies that specific content existed in a specific state at a specific time, and whether it was subsequently modified. That attestation can be bound to a system or organization rather than a natural person.

Privacy-preserving fingerprinting, using techniques such as locality-sensitive hashing that reduce content to non-reversible signatures, provides the detection benefit without creating a surveillance mechanism. Data minimization requirements (limiting retention duration, prohibiting reconstruction of original content from fingerprints, restricting access to authorized verification queries) can be specified alongside the fingerprinting recommendation.

**Recommendation:** Characterize fingerprinting as "recommended for providers processing content at scale or for high-risk applications," rather than purely optional. Specify that fingerprinting implementations must comply with data minimization principles: non-reversible signatures, limited retention, no reconstruction of original content, and no linkage to natural persons without explicit legal basis. This is proportionate. It does not burden smaller operators. It closes the detection gap for the providers whose scale makes manual attribution impossible.

---

### 4. Marking Must Survive Content Distribution

A news article generated by AI is published on one site, syndicated through a wire service, aggregated by three platforms, and quoted on social media. All of this happens within hours. If the marking is stripped at the first copy-paste, the compliance obligation is satisfied at publication and violated everywhere the content actually reaches readers.

This is not a hypothetical scenario. It is how content distribution works today, and it is the primary channel through which AI-generated content reaches end users.

The two-layered approach the Code of Practice describes addresses this, but only if both layers are understood as serving distinct functions:

- **Secured metadata** (C2PA manifests) provides the authoritative, cryptographically signed provenance record. It is rich and structured. It can be stripped by copy-paste.
- **Invisible embedding** (watermarking within the text itself, using techniques such as non-rendering Unicode characters) survives copy-paste, reformatting, and redistribution. It carries less data but persists where metadata does not.

These layers are not redundant. One provides depth. The other provides resilience. Together they provide marking that works at the point of publication and at every subsequent point of redistribution.

**Recommendation:** Include a distribution survival principle. Marking methods should demonstrate resilience across common distribution paths: copy-paste, syndication, aggregation, and cross-platform sharing. The two-layered approach should be understood as complementary layers serving metadata richness and distribution resilience, not as two methods applied in parallel for redundancy alone. Distribution survival should be a mandatory quality criterion under Commitment 3, not merely an implied benefit of the multi-layered approach.

---

### 5. Streaming and Real-Time Content Should Be Explicitly Addressed

The Code's obligations extend to all AI systems generating synthetic text content. The highest-volume category of such content, chat-based and API-based AI interactions, produces output as a token-by-token stream rather than a static document. A chatbot emits tokens one at a time over seconds or minutes. An API returns a response as a server-sent event stream. The completed output may never exist as a static file. The user consumes it in real time.

Marking protocols that require a completed document before signing can begin do not work for this content. Between the first token and the last, the output exists in an unmarked state. For chat-based AI applications, the primary consumer interface for generative AI, that unmarked state spans the entire interaction.

Incremental authentication during streaming is technically feasible. Cryptographic authentication structures can be constructed progressively as tokens are generated, with the final proof computed when generation completes. Production implementations of this approach exist today.

**Recommendation:** Clarify that marking obligations apply to streaming and real-time AI-generated content, and that incremental authentication during generation is a valid compliance method. Providers of chat-based and API-based AI systems should not be understood as exempt from marking obligations because their outputs are delivered as streams rather than static documents.

---

### 6. Short Text Segments Should Not Be Exempted

The draft includes a carve-out for short text segments. This exemption should be removed.

The premise behind the carve-out is that marking short text is technically infeasible. That premise is incorrect for standards-based provenance approaches. A C2PA manifest is metadata attached to content, not a statistical signal hidden inside it. There is no minimum content length. A manifest can be attached to a single sentence, a one-word chatbot reply, an automated caption, or any other short-form output. A chatbot that responds "OK" to a user query can have a provenance manifest attached to that two-character response. Production implementations handle text of any length today, with no minimum character threshold.

The concern driving the carve-out applies to a specific category of watermarking techniques, those that embed signals by modifying statistical properties of the text itself. Those techniques do need space to work. But the two-layered approach the Code of Practice already envisions solves this: the secured metadata layer (C2PA manifest) functions at any content length, while the watermarking layer adds resilience for content long enough to support embedding. For a one-word chatbot reply, the manifest alone provides the provenance signal. For a 2,000-word article, both layers apply.

Three reasons to remove the carve-out:

**Volume.** Short-form AI-generated content is the highest-volume category of AI output reaching consumers. Chatbot interactions, generated summaries, automated replies, social media posts, image captions. Collectively, these represent more AI-generated text encounters per day than all long-form content combined. Exempting short text creates a transparency gap that covers the majority of what consumers actually see.

**Perverse incentive.** The carve-out invites fragmentation. A provider generating a 500-word response can present it as a sequence of short messages, each below the threshold. The obligation disappears not because the content is different, but because it was chunked.

**Consumer exposure.** Chatbots, automated customer service agents, and generated social media replies are the AI applications most likely to be mistaken for human communication. They produce short-form text, and they are exactly the outputs where transparency serves the regulation's purpose most directly.

**Recommendation:** Remove the short text carve-out. C2PA manifests provide a technically feasible marking method for text of any length, including single sentences. If the Committee determines a transition accommodation is necessary, it should define a specific and narrow character threshold, include a sunset date, and require providers to demonstrate that no technically feasible marking method exists for their output type. A blanket exemption based on length alone is not justified by the current state of the technology. At minimum, if a length threshold is retained, it should apply only to the watermarking layer (Sub-measure 1.1.2), not to the secured metadata layer (Sub-measure 1.1.1). A C2PA manifest can be generated for text of any length. There is no technical basis for exempting short text from metadata-based provenance.

---

### 7. Verification Must Be Freely Accessible

Marking AI-generated content has value only if third parties can check the markings. Journalists, researchers, regulators, platforms, and ordinary citizens all need the ability to verify whether content carries provenance signals and what those signals assert.

Measure 2.1 already moves in this direction by requiring that an interface be made available free of charge for verification. This is the right instinct. The recommendation here is to make this principle explicit and universal: free verification should apply to all marking layers, not only to the detection interface the provider operates. Third-party verification tools, whether browser-based, server-side, or purpose-built for research, should be able to verify provenance markings without commercial agreements or API keys.

If verification requires payment, proprietary software, or a commercial account, the transparency framework creates a two-tier system. Organizations that pay see provenance data. The general public does not. That outcome contradicts the regulation's purpose.

Free, unauthenticated verification of content provenance is technically and commercially feasible. Production implementations offer it today across text, images, audio, video, and documents, at no cost and with no account required. The browser-based tools that perform this verification are freely available as extensions that any user can install. Verification can be a public good while the infrastructure for creating and embedding provenance remains a commercial service. The marginal cost of verification is low relative to the cost of signing.

Free verification also generates a network effect. Every check strengthens the trust chain. Journalists verifying content before publication, platforms checking provenance before hosting, and researchers auditing AI outputs all contribute to the transparency infrastructure the regulation aims to build. Gating verification behind payment reduces the number of checks, which reduces the value of the entire framework.

**Recommendation:** Require that verification of content provenance markings be freely accessible to any party, without commercial agreements, proprietary software, or authentication. Providers should offer or support a publicly accessible verification mechanism for the markings they embed.

---

### 8. The Removal of the AI-Generated vs. AI-Assisted Taxonomy Is Correct

The second draft removes the distinction between "AI-generated" and "AI-assisted" content. This is the right decision. The first draft's taxonomy was unenforceable and should not return.

The problem with the distinction was measurement. No reliable method exists to determine whether a document is 51% AI-generated or 49% AI-generated. Any threshold would be arbitrary. Any self-reporting obligation would create incentives to understate AI involvement. A company using AI to draft an entire document could claim it was "AI-assisted" because a human clicked approve. The compliance framework would depend on a distinction that cannot be objectively measured, consistently applied, or meaningfully audited.

A provenance-based approach solves this. Rather than classifying the degree of AI involvement, provenance records what happened: which AI system was used, what actions it performed, what human review occurred, and a cryptographic verification of the final output. The C2PA specification already defines the assertion vocabulary for this: `c2pa.ai_generated`, `c2pa.ai_training`, and structured action records. The question shifts from "how much AI was in this?" to "what is the verifiable chain of origin?"

For deployers, the removal simplifies compliance. The obligation becomes binary: if an AI system was involved in producing this content, attach provenance metadata and disclose accordingly. That obligation is clear, implementable, and auditable. The previous taxonomy made it ambiguous.

**Recommendation:** Maintain the current approach. Affirm that provenance-based marking, recording what AI system was involved and what human review occurred, satisfies the transparency obligation without requiring quantitative classification of AI contribution.

---

### 9. Editorial Review Claims Should Be Verifiable Through Standardized Provenance Records

Commitment 4 of Section 2 allows deployers to forgo disclosure of AI-generated text when human review or editorial control has occurred and a natural or legal person holds editorial responsibility. This exception is appropriate. It recognizes that professional editorial workflows already provide the transparency the regulation seeks.

But the exception currently requires only internal documentation: a description of organizational measures and the identity of the responsible person. This creates an enforcement gap. A deployer can claim editorial review occurred without any externally verifiable evidence that it did.

Provenance standards can close this gap. A C2PA manifest can record not only that content was AI-generated, but also that a human review step occurred, who or what organization performed it, and when. This record is cryptographically signed and externally verifiable. It transforms the editorial review exception from a self-reported assertion into a provenance-backed attestation.

This does not impose a new burden. It uses the same provenance infrastructure that providers are already required to implement under Section 1. The deployer's obligation is simply to add a human-review assertion to the existing provenance chain before publication.

**Recommendation:** Specify that deployers relying on the editorial review exception under Commitment 4 should document the human review step using standardized, externally verifiable provenance records, such as C2PA manifests with human-review assertions, rather than internal documentation alone. This ensures the exception is auditable by regulators and credible to the public.

---

### Closing

The C2PA text provenance specification was published January 8, 2026. It was developed collaboratively by publishers, AI companies, technology platforms, and media organizations. Production implementations are deployed. The specification defines the secured metadata format, the AI content assertion vocabulary, and the verification protocol this Code of Practice needs as its technical foundation.

The nine recommendations above address areas where the current draft either understates what the technology can do (short text, streaming, fingerprinting, editorial review verification) or misses an opportunity to require interoperability and accountability (C2PA reference, free verification, distribution survival, deployer-side provenance). In several cases, the shift from mandatory to voluntary language between drafts weakens provisions that production-ready technology can support. In each case, the technology to meet a stronger requirement exists today.

The C2PA Text Provenance Task Force is available to provide technical support to the Committee as the Code of Practice moves toward finalization.

Erik Svilich
Co-Chair, C2PA Text Provenance Task Force
Founder and CEO, Encypher Corporation
erik.svilich@encypher.com
[encypher.com](https://encypher.com)

*This document is signed with C2PA content provenance at sentence-level granularity. Verify at [encypher.com/tools/verify](https://encypher.com/tools/verify)*

---

## Appendix A: Technology Mapping Reference (Internal - Remove Before Filing)

This appendix maps the Code of Practice's requirements to Encypher's technology for internal reference and sales enablement. It is not part of the public filing.

### Section 1 - Provider Obligations (Article 50(2))

| Code of Practice Requirement | C2PA Standard Coverage | Encypher Proprietary Coverage | ENC0100 Patent Claims |
|---|---|---|---|
| **Secured metadata** | C2PA manifests (JUMBF/COSE signed, document-level) | Sentence-level Merkle trees (Enterprise) | Claims 1-18 (encoding/Merkle), Claims 31-44 (manifest embedding) |
| **Watermarking** | Not in C2PA text spec | ZWC invisible embedding (ZWNJ/ZWJ/CGJ/MVS), distributed variation selectors | Claims 31-40 (non-rendering Unicode), Claims 56-60 (distributed embedding), Claims 64-66 (error-correcting codes) |
| **Fingerprinting (optional)** | Not in C2PA | LSH fingerprinting with Merkle integration (Enterprise) | Claims 72-77 (fingerprint indexing, similarity-based discovery) |
| **Logging (optional)** | Not in C2PA | External data repository, hash tables, revocation registry | Claims 7-11 (hash table storage), Claims 50 (UUID repository), Claims 53-55 (revocation) |
| **Detection protocols** | C2PA verification of manifests | Public API (31 MIME types, free, no auth), Chrome extension (free, no account, surfaces AI assertions on any webpage) | Claims 21-30 (evidence generation), Claims 41-44 (manifest extraction) |
| **Verification protocols** | C2PA manifest validation | Dual-path verification: document-level + segment-level + cross-verification | Claims 61-63 (multi-layer verification system) |

### Section 2 - Deployer Obligations (Article 50(4))

| Code of Practice Requirement | Encypher Coverage | Status |
|---|---|---|
| **Labelling deepfakes** | Multi-media signing (Enterprise: images, audio, video). C2PA `c2pa.ai_generated` assertions already in spec. Chrome extension (free, no account) surfaces this to end users on any webpage. | Covered. Detection and display to consumers is production-ready. |
| **Text publications of public interest** | Core text provenance. C2PA manifests with AI assertions. WordPress plugin signs published content. | Covered. |
| **Design/placement of icons/labels/disclaimers** | Chrome extension displays provenance info. C2PA data layer exists. Deployer-side rendering in their own page UI is the deployer's responsibility; our data layer supports it. | Narrow gap: we provide the data and a consumer detection tool, not the deployer's own page rendering. |
| **Uniform EU icon** | Not yet finalized by EU task force. | Monitor. When icon ships, Chrome extension and WordPress plugin can surface it. |
| **Editorial review attestation** | C2PA human-review assertions (action records in manifest). | Covered. Encypher Attest workflow provides cryptographic attestation of human review with timestamp, reviewer identity, and diff record. |

### Capabilities That Exceed Baseline Requirements

1. **Sentence-level granularity (ENC0100)** - Document-level is the regulatory minimum. We provide per-character attribution. This is Encypher's proprietary technology, not part of C2PA.
2. **Multi-media signing (31 MIME types)** - Unified API for text, images (13 formats), audio (6), video (4), documents (5), fonts (3), live streams.
3. **Free public verification** - No auth, no API key, any third party, all media types. Chrome extension is free with no account required.
4. **Distribution survival** - ZWC encoding survives copy-paste, syndication, aggregation, wire service distribution.
5. **Real-time streaming signing** - Sign LLM outputs as they stream (WebSocket/SSE).
6. **Short text signing** - No minimum text length. Single character can be signed. No enforced minimum anywhere in the signing path.
7. **Evidence packaging** - Formal notice records, tamper-evident diffs, Merkle proofs for enforcement.
8. **Quote integrity verification** - Prove whether AI attributions are accurate or hallucinated.

---

## Appendix B: Patent Position Analysis (Internal - Remove Before Filing)

**ACCESS CONTROL NOTE:** This appendix maps patent claims to regulatory requirements. It is high-value internal strategy and high-risk if leaked. Recommend storing separately from the submission draft with tighter access controls once the filing is complete. The "remove before filing" header is necessary but not sufficient if this document is shared broadly during internal review.

### FRAND Risk Assessment

If C2PA becomes the referenced standard in EU regulation, there may be pressure for standard-essential patents to be licensed on FRAND terms.

Our position is protected:

- C2PA Section A.7 covers document-level provenance. That is what we contributed to the standard and what the submission advocates as the baseline.
- ENC0100 claims (sentence-level Merkle trees, fingerprinting, distributed embedding, streaming authentication) go beyond the C2PA standard. They are enhancements, not standard-essential patents.
- The submission draws this line explicitly. It never attributes segment-level capabilities to C2PA.

The discipline: never contribute patent-protected sentence-level claims to the C2PA standard. The standard stays document-level. Our patents cover the granular enhancements that organizations seeking robust compliance will want. That is the moat.

### Key Patent Intersections with Code of Practice

| Code of Practice Concept | ENC0100 Claims | Assessment |
|---|---|---|
| Two-layered marking (metadata + watermarking) | Claims 61-63 (multi-layer authentication) | Our patent covers the architecture the regulation describes |
| Secured metadata for text | Claims 31-44 (manifest embedding via non-rendering Unicode) | Anyone implementing text-specific invisible C2PA embedding likely practices our claims |
| Text watermarking | Claims 56-60 (distributed encoding), Claims 64-66 (ECC) | Text-specific invisible watermarking via Unicode is our patent territory |
| Fingerprinting | Claims 72-77 (LSH + Merkle integration) | If fingerprinting becomes standard practice, our hybrid approach is the strongest patented method |
| Streaming authentication | Claims 46-52 (incremental Merkle construction) | Only patented approach for real-time LLM output signing |
| Detection/verification | Claims 21-30 (evidence generation), Claims 41-44 (verification) | Verification tools will need to practice detection methods we have claimed |

---

## Appendix C: Commercial Leverage Plan (Internal - Remove Before Filing)

### Immediate Actions (Week of Filing)

| Action | Owner | Target |
|---|---|---|
| Submit public comment | Erik | EU Commission |
| Register as participant/observer via EUSurvey if channel is accessible | Erik | EU Commission AI Office (separate from the public comment) |
| Press release: "C2PA Task Force Co-Chair submits comments on EU AI Act Code of Practice" | Marketing | Axios Pro Rata, Nieman Lab, Press Gazette, AI trades, Euractiv, Politico Europe, MLex |
| Personalized outreach with submission summary | Erik + Matt | AP, Taylor & Francis, Snack-Media, Valnet, NMA |
| LinkedIn article adapted from submission | Erik | Organic reach + inbound |

**Timing:** The public comment submission and the LinkedIn share should happen the same day. The LinkedIn post drives organic visibility. The submission is the substance. Together they create a single news cycle.

### Prospect Outreach Framing

**EU-based prospects (Taylor & Francis, Snack-Media):** Compliance frame is the primary hook. The obligation is theirs and the deadline is August 2, 2026. Send the submission summary with a cover note explaining what it means for their specific operations. Offer a compliance mapping walkthrough.

**US-based prospects with EU exposure (AP, NMA members):** The EU AI Act applies to their EU readership and editorial operations. The submission is a reason to re-engage. Frame as: we are shaping the compliance framework through our standards role, and here is what it means for your organization.

**US-only prospects:** The EU is setting the global template for AI content transparency. US regulation tends to follow. Implementing C2PA provenance now is ahead-of-curve positioning, not premature compliance spend.

### ICP 3 (David - Enterprise Risk Officer) Acceleration

The Code of Practice confirms the architecture David needs: two-layered marking (secured metadata + watermarking). That is our stack. The August 2, 2026 enforcement deadline is four months away. Create a one-page "EU AI Act Compliance Mapping" sales asset derived from this submission for all ICP 3 conversations.

---

## Document Control

**Version:** 3.0
**Created:** March 28, 2026
**Author:** Strategic Advisor Agent (synthesizing Legal/IP, Product/Tech, and BD input), with BD Strategy Review edits
**Status:** DRAFT - Requires EU regulatory counsel review before filing
**Next Steps:**
1. Erik reviews and approves submission text
2. EU regulatory counsel reviews for regulatory language compliance
3. Confirm exact submission format and deadline from Commission website
4. File submission
5. Execute commercial leverage plan (press, outreach, thought leadership)

**Key Principle:** Encypher is mentioned zero times in the submission text. Every recommendation is framed in terms of technical feasibility, interoperability, and regulatory effectiveness. The commercial leverage comes from being the entity that submitted it, not from what it says.
