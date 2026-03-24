---
# Research Notes
## Topic
The shift from AI copyright litigation to licensing marketplace infrastructure

## Proposed Thesis
While publishers pour resources into copyright lawsuits against AI companies, the licensing revenue is already flowing through new marketplaces that most publishers cannot participate in - because they lack the machine-readable provenance infrastructure these platforms require to attribute and compensate content usage.

## Suggested Title
AI Licensing Moved from Courtrooms to Marketplaces and Most Publishers Are Not Ready

## Suggested Tags
Publisher Licensing, Content Provenance, C2PA, AI Copyright, Publisher Strategy, AI Companies, Content Authentication, Industry News

## Sources
1. URL: https://about.ads.microsoft.com/en/blog/post/february-2026/building-toward-a-sustainable-content-economy-for-the-agentic-web
   Date: February 3, 2026
   Key finding: Microsoft launched the Publisher Content Marketplace (PCM) on February 3, 2026 - an AI licensing hub where publishers set usage terms and AI companies discover and license content for grounding scenarios. Launch partners include The Associated Press, Condé Nast, Hearst Magazines, Vox Media, and others. The platform includes usage-based reporting giving publishers visibility into how content creates value. Publishers must structure metadata and archives for content to be discoverable and attributable in the marketplace.
   Exact quotes: None confirmed verbatim from this source - writer should pull direct quotes after reading full post.
   Backup URL: https://searchengineland.com/microsoft-launches-publisher-content-marketplace-for-ai-licensing-468191
   Supports: Core thesis that licensing has moved to marketplace infrastructure requiring machine-readable signals

2. URL: https://digiday.com/media/news-media-alliance-signs-ai-licensing-deal-to-unlock-recurring-rag-revenue-for-small-and-mid-sized-publishers/
   Date: March 2026
   Key finding: The News/Media Alliance signed a licensing deal with AI startup Bria that lets its 2,200 publisher members opt in to monetizing RAG-driven enterprise demand. Revenue is split 50-50 between Bria and the publisher based on an attribution model. This collective approach is especially valuable for smaller publishers and local news outlets that lack resources to strike direct AI deals. The deal requires content to be identifiable and attributable for usage tracking.
   Exact quotes: None confirmed verbatim - writer should verify from source.
   Backup URL: https://www.newsmediaalliance.org/ai-licensing-partnership-bria-announcement/
   Supports: Thesis that marketplace infrastructure (not lawsuits) is where revenue flows, and attribution/provenance is prerequisite for participation

3. URL: https://fortune.com/2026/03/18/dictionaries-suing-openai-chatgpt-copyright-infringement/
   Date: March 18, 2026
   Key finding: Britannica and Merriam-Webster filed suit against OpenAI in the Southern District of New York on March 13, 2026, alleging OpenAI used nearly 100,000 copyrighted articles to train ChatGPT without permission. The suit also targets RAG-based real-time content retrieval that reproduces content verbatim. OpenAI responded that models are "trained on publicly available data and grounded in fair use." The lawsuit includes Lanham Act trademark claims for AI hallucinations falsely attributed to plaintiffs.
   Exact quotes: OpenAI stated their AI models "empower innovation and are trained on publicly available data and grounded in fair use" (attribution: OpenAI spokesperson, per Fortune reporting)
   Backup URL: https://techcrunch.com/2026/03/16/merriam-webster-openai-encyclopedia-brittanica-lawsuit/
   Supports: Counterpoint - shows that litigation is still active, but sets up the argument that lawsuits alone are insufficient because the market is moving to infrastructure solutions

4. URL: https://artificialintelligenceact.eu/article/50/
   Date: Ongoing (deadline August 2, 2026)
   Key finding: EU AI Act Article 50 requires providers of AI systems generating synthetic text, audio, image, or video to mark outputs in a machine-readable format detectable as artificially generated. The European Commission published a draft Code of Practice on December 17, 2025, with a final version expected June 2026, ahead of August 2, 2026 enforcement. The Code of Practice is expected to reference C2PA-compatible standards for machine-readable marking. Fines for non-compliance: up to 35 million euros or 7% of global annual turnover.
   Exact quotes: Providers "shall ensure that the outputs of the AI system are marked in a machine-readable format and detectable as artificially generated or manipulated" (Article 50, EU AI Act)
   Backup URL: https://digital-strategy.ec.europa.eu/en/news/commission-publishes-first-draft-code-practice-marking-and-labelling-ai-generated-content
   Supports: Regulatory backstop that makes machine-readable provenance not just commercially advantageous but legally required by August 2026

5. URL: https://www.hklaw.com/en/insights/publications/2026/03/the-final-word-supreme-court-refuses-to-hear-case-on-ai-authorship
   Date: March 2, 2026
   Key finding: The US Supreme Court denied certiorari in Thaler v. Perlmutter on March 2, 2026, affirming that AI cannot be an author under the Copyright Act. This settles that human authorship is required for copyright protection, but does not address the larger question of whether AI companies infringe copyright when training on human-authored works. The decision underscores that legal frameworks move slowly while the market is already building licensing infrastructure.
   Exact quotes: None confirmed verbatim - writer should verify from source.
   Backup URL: https://www.morganlewis.com/pubs/2026/03/us-supreme-court-declines-to-consider-whether-ai-alone-can-create-copyrighted-works
   Supports: Broader context that courts are resolving narrow questions while the commercial licensing infrastructure question remains unanswered by litigation

## Counterarguments Found
- Lawsuits have strategic value beyond winning: the Britannica/OpenAI suit and the court-ordered disclosure of 78 million training data logs (March 9, 2026) create leverage that makes AI companies more willing to negotiate licensing terms. Litigation and marketplace infrastructure are complementary, not alternatives. This is a legitimate point - but the rebuttal is that leverage without infrastructure still leaves publishers unable to capture revenue even if AI companies agree to pay.
- Microsoft's PCM may be a strategic move to consolidate power rather than genuinely empower publishers. Microsoft takes an undisclosed commission and controls the platform. Smaller publishers may be trading one gatekeeper (AI scrapers) for another (marketplace intermediaries). Rebuttal: even if imperfect, marketplaces create measurable, recurring revenue streams - which is more than lawsuits have delivered for most publishers so far.
- Machine-readable provenance infrastructure is expensive and technically complex for small publishers. Not every local newspaper can implement C2PA. Rebuttal: collective licensing deals like NMA/Bria reduce this barrier, and the cost of not having infrastructure is invisibility in the marketplace.

## Recommended Post Structure
- Opening: Open with the contrast - in the same week of March 2026, Britannica filed yet another copyright lawsuit against OpenAI while the News/Media Alliance quietly signed a licensing deal that gives 2,200 publishers a path to recurring AI revenue. One approach fights over the past; the other builds for the future. State thesis: the licensing war has moved from courtrooms to marketplace infrastructure, and publishers without machine-readable provenance signals are invisible to the systems that would pay them.
- Section 1: The Marketplace Moment - Detail Microsoft PCM (launched Feb 2026), NMA/Bria deal, and Meta's expanding publisher partnerships. Argue that these represent a phase shift: AI companies are now actively shopping for licensed content, not just scraping it. The key requirement across all platforms is content that can be programmatically identified, attributed, and tracked. Use evidence from Sources 1 and 2.
- Section 2: The Infrastructure Gap - Anchor to content provenance as the technical solution. Explain why machine-readable provenance (C2PA, RSL) is the admission ticket to these marketplaces. Without embedded metadata, content is invisible to attribution engines that calculate publisher payments. Draw the parallel to early web monetization: publishers who adopted ad tags and analytics got paid; those who did not were invisible to the revenue system. Reference how C2PA Section A.7 (text provenance, co-authored by Encypher) enables exactly this capability for text content.
- Section 3: The Litigation Counterargument - Steelman the case for lawsuits: Britannica's suit, the 78M training log discovery order, Supreme Court's Thaler ruling all create important precedent and leverage. But argue that leverage without infrastructure is like winning a judgment you cannot collect. Even if courts rule in publishers' favor, collecting payment requires the same attribution infrastructure the marketplaces need. Use Sources 3 and 5.
- Section 4: The Regulatory Accelerant - EU AI Act Article 50 creates a hard deadline of August 2, 2026 for machine-readable marking of AI-generated content. The Code of Practice (final version June 2026) will likely reference C2PA-compatible standards. This means publishers who build provenance infrastructure now get both marketplace revenue and regulatory compliance. Those who wait face a dual penalty: locked out of revenue and non-compliant with regulation. Use Source 4.
- Closing: Predict that within 12 months, the publishers capturing meaningful AI licensing revenue will not be those who filed the most lawsuits - they will be those who made their content machine-readable first. Call to action: the infrastructure window is open now, but the August 2026 regulatory deadline and marketplace first-mover advantages mean it will not stay open indefinitely. Publishers should be investing in content provenance infrastructure today.
---
