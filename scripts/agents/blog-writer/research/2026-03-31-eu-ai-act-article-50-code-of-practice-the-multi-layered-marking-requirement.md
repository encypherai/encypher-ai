---
# Research Notes
## Topic
EU AI Act Article 50 Code of Practice - The Multi-Layered Marking Requirement

## Proposed Thesis
Organizations racing to comply with EU AI Act Article 50 by August 2026 are building single-layer transparency solutions - metadata only or watermarking only - that the European Commission's own Code of Practice explicitly says are insufficient, and the five-month window to fix this is closing faster than most compliance teams realize.

## Suggested Title
EU AI Act Article 50: Why Single-Layer AI Marking Will Fail Compliance

## Suggested Tags
EU AI Act, Content Provenance, C2PA, AI Governance, Content Authentication, AI Watermarking, Publisher Strategy, AI Companies, Legal Analysis

## Sources
1. URL: https://digital-strategy.ec.europa.eu/en/library/commission-publishes-second-draft-code-practice-marking-and-labelling-ai-generated-content
   Date: 5 March 2026
   Key finding: The European Commission published the Second Draft Code of Practice on Marking and Labelling of AI-Generated Content. The Code mandates a revised two-layered marking approach: digitally signed metadata plus imperceptible watermarking, with optional fingerprinting and logging. No single marking technique is sufficient to meet Article 50 requirements on its own.
   Exact quotes: The Code states that providers must implement "at least two layers of machine-readable active marking" and that "no single marking technique is sufficient to meet the requirements of Article 50 on its own."
   Backup URL: https://www.kennedyslaw.com/en/thought-leadership/article/2026/the-eu-ai-act-s-draft-code-of-practice-on-marking-and-labelling-of-ai-generated-content-what-providers-and-deployers-need-to-know/
   Supports: Core thesis - single-layer solutions are explicitly insufficient under the Code.

2. URL: https://www.kennedyslaw.com/en/thought-leadership/article/2026/the-eu-ai-act-s-draft-code-of-practice-on-marking-and-labelling-of-ai-generated-content-what-providers-and-deployers-need-to-know/
   Date: March 2026
   Key finding: The two mandatory marking measures are (1) inclusion of digitally signed metadata, with signatories recording and embedding information on whether content is AI-generated or AI-manipulated, and (2) imperceptible watermarking techniques interwoven within the content, designed so that a fragment of the content suffices to detect the watermark. Companies that sign the final Code and implement its measures will be presumed compliant with Article 50. Companies that do not sign must demonstrate equivalent measures.
   Exact quotes: Kennedys describes the requirements as "a revised two-layered marking approach involving secured metadata and watermarking, optional fingerprinting and logging, and protocols for detection and verification."
   Backup URL: https://www.twobirds.com/en/insights/2026/taking-the-eu-ai-act-to-practice-understanding-the-draft-transparency-code-of-practice
   Supports: Specifics of what the two mandatory layers are - metadata plus watermarking.

3. URL: https://artificialintelligenceact.eu/article/50/
   Date: Standing legislation (enforcement 2 August 2026)
   Key finding: Article 50(2) requires providers of AI systems generating synthetic audio, image, video, or text content to "ensure that the outputs of the AI system are marked in a machine-readable format and detectable as artificially generated or manipulated." Technical solutions must be "effective, interoperable, robust and reliable." Article 50(4) requires deployers to disclose when content is AI-generated, particularly for text published on matters of public interest.
   Exact quotes: Providers shall "ensure that the outputs of the AI system are marked in a machine-readable format and detectable as artificially generated or manipulated" and solutions must be "effective, interoperable, robust and reliable as far as this is technically feasible."
   Backup URL: https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50
   Supports: The legal foundation - Article 50 text itself mandates machine-readable marking and detectability, which inherently requires more than one technique.

4. URL: https://www.hsfkramer.com/notes/ip/2026-03/transparency-obligations-for-ai-generated-content-under-the-eu-ai-act-from-principle-to-practice
   Date: March 2026
   Key finding: Herbert Smith Freehills Kramer analysis confirms the Code of Practice is structured in two sections - Section 1 for providers (marking and detection under Article 50(2)) and Section 2 for deployers (labelling under Article 50(4)). The Second Draft is more streamlined than the First Draft, offering greater flexibility but maintaining the multi-layered approach as the compliance baseline.
   Exact quotes: None confirmed verbatim - use for background context only.
   Backup URL: https://creativesunite.eu/article/roadmap-to-august-the-second-draft-code-of-practice-for-ai-transparency
   Supports: Timeline pressure - the Code finalizes June 2026, enforcement August 2026, leaving organizations minimal implementation time.

5. URL: https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content
   Date: Ongoing (Commission policy page)
   Key finding: The Commission collected feedback on the Second Draft until 30 March 2026 (deadline just passed). The final Code is expected by early June 2026 - two months before enforcement on 2 August 2026. Organizations that sign the Code get a presumption of compliance. Those that do not sign must independently demonstrate equivalent measures.
   Exact quotes: The Commission "expects to finalise the Code in early June this year" and the "transparency rules becoming applicable on 2 August 2026."
   Backup URL: none found
   Supports: Timeline urgency - feedback period just closed, finalization imminent, enforcement in five months.

## Counterarguments Found
- The Code of Practice is voluntary, not legally binding. Organizations can demonstrate compliance through equivalent measures without signing the Code. However, the Code creates a presumption of compliance, meaning non-signatories face a higher burden of proof. In practice, the Code will define what regulators consider adequate.
- The "technically feasible" qualifier in Article 50 gives organizations room to argue that multi-layered marking is not feasible for their specific content type or use case. Text presents genuine technical challenges for watermarking that do not apply to images or video. But the Code's explicit multi-layer mandate narrows this escape hatch considerably, and the Commission clearly intends text to be covered.
- Some organizations may argue that the Code of Practice is still in draft form and could change before finalization. This is technically true but increasingly unlikely - the Second Draft refined the First Draft's approach rather than abandoning it, and the feedback period has now closed. The multi-layered requirement has survived two drafts.
- Large AI providers (OpenAI, Google, Meta) may have the resources to implement multi-layer solutions quickly, making this primarily a mid-market and enterprise compliance problem. The real gap is among smaller AI deployers and publishers who need to both mark their AI-generated content and verify incoming content authenticity.

## Recommended Post Structure
- Opening: Most organizations preparing for EU AI Act Article 50 believe they need to pick a compliance technique - metadata or watermarking - and implement it before August 2026. The Commission's own Code of Practice says they are wrong. No single technique is sufficient. The requirement is both - at minimum.
- Section 1: What Article 50 actually says versus what most compliance guides claim. Walk through the statutory text ("marked in a machine-readable format and detectable"), then show how the Code of Practice interprets this as a mandatory two-layer approach: digitally signed metadata plus imperceptible watermarking. The distinction between provider obligations (Article 50(2) - marking) and deployer obligations (Article 50(4) - labelling). Use Sources 1, 2, 3.
- Section 2: Why single-layer solutions fail. Metadata alone (including C2PA) is easily stripped by screenshots, social media uploads, or file conversion - the Code acknowledges this. Watermarking alone lacks the structured, interoperable provenance information needed for verification chains. The Code requires both because each compensates for the other's weakness. This is where content provenance infrastructure becomes essential - C2PA provides the metadata layer with interoperable, standardized provenance records; invisible marking techniques provide the watermarking layer that survives content transformation. Together they satisfy both mandatory layers.
- Section 3: Steelman the counterargument - the Code is voluntary, technically feasible is a qualifier, and text is harder to watermark than images. Then rebut: voluntary codes that create presumptions of compliance become de facto mandates (cite GDPR codes of conduct as precedent). The technically feasible qualifier is narrower than it appears because the Commission is specifying what feasible means through the Code itself. And text watermarking, while harder, exists and is advancing rapidly - the question is not whether it is possible but whether organizations have implemented it.
- Section 4: The timeline math. Feedback closed March 30. Final Code expected June. Enforcement August 2. Organizations that have not begun multi-layer implementation have roughly five months, with the final technical requirements not confirmed until two months before enforcement. What publishers, AI companies, and enterprises should be doing now: auditing their current marking approach against the two-layer requirement, evaluating content provenance solutions that combine C2PA metadata with invisible marking, and preparing for the presumption-of-compliance framework the Code creates.
- Closing: The Commission has been clear about what Article 50 compliance looks like. The organizations that read only the statute and not the Code of Practice will discover in August that their single-layer solution does not qualify. The technical infrastructure to satisfy both layers exists today. The question is whether compliance teams will implement it before the deadline forces the issue.
---
