---
title: "EU AI Act Article 50: Why Single-Layer AI Marking Will Fail Compliance"
date: "2026-03-31"
excerpt: "EU AI Act Article 50 compliance requires two marking layers minimum. Organizations building metadata-only or watermark-only solutions face a gap the Code of Practice makes clear."
author: "Encypher Team"
image: "/images/blog/EU_AI_Act_Article_50_Why_Single_Layer_AI_Marking_Will_Fail_Compliance.png"
tags: ["EU AI Act", "Content Provenance", "C2PA", "AI Governance", "Content Authentication", "AI Watermarking", "AI Companies"]
---

A compliance team at a mid-sized AI company reads Article 50 of the EU AI Act, notes the requirement to mark outputs "in a machine-readable format," and commissions a metadata tagging system. Another team at a publisher reads the same article, focuses on "detectable as artificially generated," and integrates an audio watermarking tool. Both believe they are on track for the August 2, 2026 enforcement deadline. The European Commission's own [Code of Practice on Marking and Labelling of AI-Generated Content](https://digital-strategy.ec.europa.eu/en/library/commission-publishes-second-draft-code-practice-marking-and-labelling-ai-generated-content), published in its Second Draft on March 5, 2026, says both are wrong. No single marking technique is sufficient. The requirement is at least two layers, and the Commission has spelled out which two.

*This post discusses legal developments for informational purposes only and does not constitute legal advice. Encypher is a technology company, not a law firm. Consult qualified legal counsel for advice specific to your situation.*

## What Article 50 Actually Requires

The [statutory text](https://artificialintelligenceact.eu/article/50/) is broad. Article 50(2) requires providers of AI systems that generate synthetic content to "ensure that the outputs of the AI system are marked in a machine-readable format and detectable as artificially generated or manipulated." The solutions must be "effective, interoperable, robust and reliable as far as this is technically feasible." Article 50(4) adds a separate obligation for deployers: disclosure when content is AI-generated, particularly for text published on matters of public interest.

Most compliance summaries stop there and treat the requirement as a single obligation that any machine-readable marking technique can satisfy. The Code of Practice does not.

The Commission's Second Draft [specifies](https://www.kennedyslaw.com/en/thought-leadership/article/2026/the-eu-ai-act-s-draft-code-of-practice-on-marking-and-labelling-of-ai-generated-content-what-providers-and-deployers-need-to-know/) a "revised two-layered marking approach involving secured metadata and watermarking, optional fingerprinting and logging, and protocols for detection and verification." The two mandatory layers are explicit: digitally signed metadata that records whether content is AI-generated or AI-manipulated, and imperceptible watermarking techniques interwoven within the content itself. The Code states that providers must implement "at least two layers of machine-readable active marking" and that "no single marking technique is sufficient to meet the requirements of Article 50 on its own."

The Code is structured in two sections. [Section 1](https://www.hsfkramer.com/notes/ip/2026-03/transparency-obligations-for-ai-generated-content-under-the-eu-ai-act-from-principle-to-practice) covers provider obligations under Article 50(2), the marking and detection requirements. Section 2 covers deployer obligations under Article 50(4), the labelling and disclosure requirements. Organizations that sign the final Code receive a presumption of compliance with Article 50. Organizations that do not sign must independently demonstrate equivalent measures, a higher burden of proof that amounts to showing regulators you arrived at the same destination by a different route.

## Why Single-Layer Solutions Fail

Each marking technique has a characteristic failure mode, and the Commission designed the two-layer requirement to address both.

Metadata alone, even when digitally signed and standards-compliant, is fragile against content transformation. A screenshot strips file-level metadata. A social media upload reformats the file and discards embedded provenance records. A copy-paste operation into a new document severs the chain entirely. The Commission's Code acknowledges this vulnerability. Metadata provides structured, interoperable provenance information, the kind that downstream systems can read and verify programmatically. But it does not survive the transformations that content routinely undergoes.

Watermarking alone presents the opposite problem. An imperceptible signal embedded in the content can survive screenshots, reformatting, and partial extraction, precisely because it is woven into the content rather than attached to the file. But a watermark by itself carries limited structured information. It can signal that content was AI-generated. It cannot, on its own, provide the interoperable verification chain that regulators and downstream consumers need: who generated it, when, under what model, with what provenance history.

The two-layer requirement exists because metadata and watermarking compensate for each other's weaknesses. Metadata provides the structured provenance record. Watermarking provides survivability when that record is stripped. Together they satisfy the Code's demand for marking that is both machine-readable and detectable across the range of conditions content encounters in practice.

The C2PA standard, which we co-chair the Text Provenance Task Force for, provides the metadata layer. A C2PA manifest is a digitally signed, document-level provenance record that meets the Code's first mandatory requirement: structured metadata recording whether content is AI-generated, who produced it, and what tools were involved. C2PA operates at the document level, authenticating a document as a whole with an interoperable manifest that any compliant verifier can read.

The second layer, imperceptible marking that survives content transformation, requires technology that operates below the document level. For text content specifically, Encypher's proprietary sentence-level embedding provides this. By binding provenance markers to individual text segments rather than to the document container, the marking persists through copy-paste, reformatting, and partial extraction. A fragment of the content suffices to detect the provenance signal, which is precisely the property the Code's watermarking requirement describes.

## The Counterargument and Where It Falls Short

Three objections to this analysis deserve direct engagement.

First, the Code of Practice is voluntary, not legally binding. This is true in the narrow sense. Organizations can demonstrate compliance with Article 50 through equivalent measures without signing the Code. But voluntary codes that create presumptions of compliance have a way of becoming de facto mandates. The GDPR's codes of conduct established the same pattern: not legally required, but treated by regulators and courts as the benchmark for what adequate measures look like. When the AI Office begins enforcement in August 2026, the first question will be whether an organization followed the Code. The second question, for those that did not, will be whether their alternative is genuinely equivalent. The GDPR precedent suggests that regulators will treat the Code's two-layer approach as the minimum benchmark, and departures from it will require detailed technical justification.

Second, the "technically feasible" qualifier in Article 50 gives organizations room to argue that multi-layered marking is not feasible for their specific content type or use case. Text does present genuine technical challenges for watermarking that do not apply to images or video. But the Code's explicit multi-layer mandate narrows this argument considerably. The Commission is not leaving "technically feasible" undefined. It is specifying, through the Code, what feasible implementation looks like. An organization arguing that text watermarking is not feasible will need to explain that position to a regulator whose own Code of Practice presumes it is, and whose Second Draft was informed by evidence that such techniques already exist in production systems.

Third, the Code is still in draft form and could change before finalization. This is technically correct and increasingly unlikely to matter. The multi-layered marking requirement survived from the First Draft to the Second Draft. The Second Draft refined the approach rather than abandoning it. The [feedback period closed on March 30, 2026](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content). The Commission expects to finalize the Code in early June. Two drafts, one public feedback cycle, and a consistent direction all point toward the multi-layer requirement remaining in the final version.

## The Timeline Math

The remaining question is implementation timeline, not regulatory direction.

The feedback period on the Second Draft closed yesterday. The final Code is expected in early June 2026. Enforcement begins August 2, 2026. Organizations that have not begun multi-layer implementation face a sequence that leaves little margin: final requirements confirmed in June, enforcement two months later.

Large AI providers with dedicated compliance engineering teams can absorb this timeline. The sharper problem sits with mid-market AI deployers, enterprise software companies whose products generate text, and publishers who need to both mark their own AI-assisted content and verify the provenance of content they receive. These organizations often have compliance teams that are still evaluating single-layer solutions, unaware that the Code of Practice has already moved past them.

Three steps apply regardless of where an organization sits in this landscape. First, audit the current marking approach against the two-layer requirement. If the compliance plan involves metadata without watermarking, or watermarking without structured metadata, it does not meet the Code's baseline. Second, evaluate content provenance solutions that combine C2PA metadata with imperceptible marking. These are the two specific layers the Code describes. Third, prepare for the presumption-of-compliance framework. Signing the Code is the most direct path to demonstrating compliance. Not signing it means building and defending an equivalence argument that regulators have no obligation to accept.

The Commission has stated what Article 50 compliance looks like. The gap between the statutory text and the Code of Practice catches organizations that treat the two as interchangeable. The statute requires machine-readable marking. The Code specifies two distinct layers to achieve it. C2PA metadata combined with sentence-level imperceptible marking satisfies both.
