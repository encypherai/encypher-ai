---
title: "EU AI Act Article 53: Why Robots.txt Is Not Enough for Publishers"
date: "2026-02-23"
excerpt: "EU AI Act Article 53 demands machine-readable rights reservation. Two December 2025 court rulings confirm robots.txt does not qualify. Publishers need content-level signals now."
author: "Encypher Team"
image: "/images/blog/EU_AI_Act_Article_53_Why_Robots_txt_Is_Not_Enough_for_Publishers.png"
tags: ["EU AI Act", "Publisher Strategy", "C2PA", "Content Provenance", "AI Training Data", "Copyright Law", "AI Copyright", "Content Authentication", "Legal Analysis"]
---

Publishers are betting their EU AI Act compliance on a mechanism that two courts - on two continents - just declared legally meaningless. In December 2025, a US federal court [ruled](https://law.justia.com/cases/federal/district-courts/new-york/nysdce/1:2025cv04315/643043/302/) that robots.txt is no more enforceable than a "keep off the grass" sign. Days later, a German appellate court [confirmed](https://www.twobirds.com/en/insights/2025/germany/higher-regional-court-hamburg-confirms-ai-training-was-permitted-(kneschke-v,-d-,-laion)) that a natural-language opt-out on a website fails the machine-readable standard required under EU copyright law. Meanwhile, [Article 53 of the EU AI Act](https://artificialintelligenceact.eu/article/53/) - which has been binding since August 2, 2025 - requires AI model providers to identify and comply with machine-readable rights reservations. Robots.txt does not meet that standard. Publishers who treat it as their compliance strategy have no enforceable rights reservation on any of their content.

## The Clause That Actually Matters: Article 53, Not Article 50

Most publisher-focused coverage of the EU AI Act zeroes in on Article 50 - the provision requiring AI companies to label their outputs as AI-generated. That matters for transparency. But it does not govern the question publishers should be asking: can AI companies legally use my content to train their models?

That question is answered by Article 53(1)(c). It requires providers of general-purpose AI models to "put in place a policy to comply with Union law on copyright and related rights, and in particular to identify and comply with, including through state of the art technologies, a reservation of rights expressed pursuant to Article 4(3) of Directive (EU) 2019/790."

Read that clause carefully. It does not say "respect robots.txt." It says AI providers must identify and comply with a reservation of rights - and must use state-of-the-art technologies to do so. That reservation must be expressed in a machine-readable format that satisfies Article 4(3) of the DSM Directive. The obligation is not aspirational. It has been enforceable since August 2, 2025. Every general-purpose AI model provider serving the EU market is already subject to it.

## Why Robots.txt Fails on Both Sides of the Atlantic

### The US: "Keep Off the Grass"

In Ziff Davis v. OpenAI, Judge Stein of the Southern District of New York [dismissed the DMCA circumvention claim](https://law.justia.com/cases/federal/district-courts/new-york/nysdce/1:2025cv04315/643043/302/) based on robots.txt. His reasoning was blunt: robots.txt files instructing web crawlers to refrain from scraping certain content do not "effectively control" access to that content any more than a sign requesting that visitors "keep off the grass" effectively controls access to a lawn.

Under US law, ignoring robots.txt is not circumvention. It is not a technological protection measure. It is a polite request - and nothing more.

### Germany: Natural Language Is Not Machine-Readable

The Hanseatic Higher Regional Court in Hamburg reached a parallel conclusion from a different legal framework. In [Kneschke v. LAION](https://www.twobirds.com/en/insights/2025/germany/higher-regional-court-hamburg-confirms-ai-training-was-permitted-(kneschke-v,-d-,-laion)), the court found that photographer Robert Kneschke's text-based opt-out - a natural-language statement on his website - did not constitute an effective reservation of rights under the DSM Directive's text and data mining exceptions. The court stated that "machine interpretability" is what matters: a statement that cannot be parsed by an automated crawler is insufficient.

This is the critical point. Even under EU law, where machine-readable opt-outs are explicitly recognized as legally binding, the mechanism must actually be machine-readable. A paragraph of text on your terms-of-service page does not qualify.

### The Structural Problem

A [Clifford Chance analysis](https://www.cliffordchance.com/insights/resources/blogs/ip-insights/2025/10/copyright-compliance-under-the-eu-ai-act-for-gpai-model-providers.html) of Article 53 compliance identifies the deeper issue: "The robots.txt file applies at the domain and URL level rather than to individual works/files, and it is not possible to apply the standard to prevent some uses but not others - for example, you cannot apply the standard to prevent use of a particular copyright work for AI model training but allow all other uses."

Robots.txt is a location-based, domain-level signal. It tells crawlers not to visit a URL. It says nothing about the rights attached to the content at that URL. It cannot distinguish between blocking search engine indexing and reserving copyright for AI training purposes. And the moment your content leaves your server - shared via email, reposted on another platform, served through an API - the robots.txt signal vanishes entirely.

Article 53 requires a rights reservation that travels with the content. Robots.txt cannot do that.

## The Commission Is Deciding the Standard Right Now

Between December 2025 and January 2026, the European Commission ran a [stakeholder consultation](https://digital-strategy.ec.europa.eu/en/consultations/commission-launches-consultation-protocols-reserving-rights-text-and-data-mining-under-ai-act-and) to identify which machine-readable protocols will be officially recognized under Article 53. The Commission sought "machine-readable, standardised protocols that can be implemented consistently and interoperably across different media, languages, and sectors."

That [consultation](https://digital-strategy.ec.europa.eu/en/consultations/commission-launches-consultation-protocols-reserving-rights-text-and-data-mining-under-ai-act-and) put eight candidate protocols on the table: robots.txt (IETF RFC 9309), TDM Reservation Protocol (TDMRep), C2PA TDM Assertions, AI.txt, Spawning AI Do Not Train registry, JPEG Trust core foundation v2, TDM.ai protocol (Liccium), and Open Rights Data Exchange (Valunode). The Commission will publish a list of "generally agreed" protocols, to be reviewed at least every two years.

This is the process that will determine what actually counts as a valid rights reservation under EU law. And most publishers did not know it was happening, let alone participate.

### The Counterargument - and Why It Falls Short

Defenders of the status quo point out that robots.txt is already embedded in the GPAI Code of Practice. Signatories have committed to respect it. That is true - and it is beside the point. The Code of Practice establishes a floor, not a ceiling. The Commission's consultation exists precisely because the Commission recognizes that robots.txt alone is insufficient. The consultation document explicitly asks for protocols that work at the individual-work level, because location-based protocols have the structural gaps that courts are already exploiting.

There is also a fair point that C2PA TDM Assertions are not yet part of the C2PA core specification - they are an extension pattern, not a ratified standard. Publishers who rely on C2PA for Article 53 compliance will need the extension to be formally adopted. But the direction is clear: the Commission is looking for content-level, per-work, machine-readable signals. The approved list will favor protocols that satisfy that requirement. Robots.txt, by design, cannot.

## What Encypher Sees From the Inside

We co-chair the C2PA Text Provenance Task Force and authored Section A.7 of the C2PA specification, published in January 2026. That section defines how authentication manifests - including rights metadata - can be embedded directly into unstructured text. This work was developed inside the [C2PA consortium](https://c2pa.org), whose members include major AI companies, publishers, and platform providers.

From our seat at the standard-setting table, the trajectory is unambiguous. The Commission's consultation asked for protocols that are machine-readable, per-work, and interoperable across media types. Content-level cryptographic signals - metadata embedded in the text itself, traveling with every copy, readable by automated systems - are the only class of mechanism that satisfies both the legal requirement and the practical reality that content moves off your server the moment you publish it.

The distinction Clifford Chance draws between "location-based protocols" and "unit-based protocols with metadata tags" maps directly to the technical architecture we have been building. A domain-level instruction that disappears when content is shared is not the same as a per-work signal that persists through every copy, every repost, every API response. We built text provenance tooling because we saw this gap from inside the standards process - and the legal landscape is now confirming what the technical architecture has always implied.

Publishers who implement content-level rights signals now - before the Commission finalizes the approved-protocol list - accomplish two things. First, they establish documentary evidence of machine-readable rights reservation that satisfies Article 53's requirements regardless of which specific protocols make the final list. Second, they ensure that every piece of content they publish carries an enforceable signal, not just the content sitting on their own servers.

## The Window Is Closing

The Commission's consultation closed in January 2026. The next formal review of the approved-protocol list is at least two years away. Publishers who wait for the final list before acting will spend those two years without enforceable rights reservation on any content already in the wild.

The question is not whether to implement machine-readable rights signals. Article 53 already requires it. The question is whether to do it now - before the next wave of general-purpose AI model training begins - or after, when the content has already been ingested without any machine-readable reservation attached.

Every day a publisher operates with robots.txt as their only signal is a day their content enters the training pipeline with no enforceable rights claim. The courts have spoken. The Commission has asked for better tools. The obligation is already binding. Act accordingly.
