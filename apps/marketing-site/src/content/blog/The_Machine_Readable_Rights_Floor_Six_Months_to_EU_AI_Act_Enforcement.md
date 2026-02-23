---
title: "The Machine-Readable Rights Floor: Six Months to EU AI Act Enforcement"
date: "2026-02-23"
excerpt: "Hamburg court established a machine-readable rights floor for TDM opt-outs. Publishers have six months before EU AI Act enforcement hardens the standard."
author: "Encypher Team"
image: "/images/blog/The_Machine_Readable_Rights_Floor_Six_Months_to_EU_AI_Act_Enforcement.png"
tags: ["EU AI Act", "Publisher Licensing", "Content Provenance", "C2PA", "AI Copyright", "Content Authentication", "Publisher Strategy", "Legal Analysis"]
---

A German photographer wrote "no automated programs" on his website, sued an AI training dataset for scraping his images, and lost. Not because German copyright law failed him - it explicitly allows rightsholders to opt out of text and data mining. He lost because his opt-out was a sentence on a webpage instead of a machine-readable signal. The Hanseatic Higher Regional Court in Hamburg [ruled on December 10, 2025](https://www.insidetechlaw.com/blog/2025/12/machine-readable-opt-outs-and-ai-training-hamburg-court-clarifies-copyright-exceptions) that this is not enough. That ruling established a machine-readable rights floor - the minimum technical standard a publisher must meet to have an enforceable TDM opt-out under EU law. Most publishers have not reached it. They have roughly six months before the EU AI Act's enforcement framework hardens that floor into permanent infrastructure.

## What the Hamburg Court Actually Decided

The case - Kneschke v. LAION (OLG Hamburg, 5 U 104/24) - turned on Section 44b of the German Copyright Act, which implements Article 4(3) of the EU's DSM Directive. That directive allows anyone to mine lawfully accessible content unless the rightsholder has "expressly reserved" the right "in an appropriate manner, such as machine-readable means."

Kneschke had reserved his rights. He said so on his website, in plain language. The court ruled that was not enough.

The key holding: machine-readability is not a subjective standard. It is assessed against the technology available at the time of the copyright-relevant act. In 2021, when LAION scraped the images, no machine could parse a natural-language clause buried in a terms-of-service page and determine that it constituted a TDM reservation. The opt-out did not exist in any form a crawler could detect. So legally, it did not exist at all.

This is the rights floor. A publisher who has not expressed their TDM reservation in a format that automated systems can detect, parse, and act on has not expressed a reservation. Full stop.

Expert commentary on the ruling draws an important [further distinction](https://legalblogs.wolterskluwer.com/copyright-blog/laion-round-2-machine-readable-but-still-not-actionable-the-lack-of-progress-on-tdm-opt-outs-part-1/): machine-readable is not the same as machine-actionable. A signal that a crawler can technically parse but that AI training pipelines routinely ignore - HTML meta tags, for instance - may satisfy the letter of "machine-readable" while failing the spirit. The court's standard points toward something stricter: the signal must be technically implementable in a way that crawlers and training pipelines can detect and honor at scale. Most current publisher implementations, including metadata in HTML headers that LLM crawlers routinely ignore, fall short of that standard.

## The Window That Is Closing

The Hamburg ruling is a German court interpreting an EU-wide directive. Article 4(3) of the DSM Directive applies identically across all 27 member states. The ruling is not technically binding outside Hamburg's jurisdiction, but it interprets the same legal text that governs every TDM opt-out in Europe. It is the most authoritative judicial statement on what "machine-readable" means under EU copyright law.

The regulatory machinery is moving in the same direction.

On December 1, 2025, the European Commission [launched a stakeholder consultation](https://digital-strategy.ec.europa.eu/en/consultations/commission-launches-consultation-protocols-reserving-rights-text-and-data-mining-under-ai-act-and) to identify and standardize the exact machine-readable protocols that GPAI providers must respect under the EU AI Act. That consultation closed on January 23, 2026. The Commission will publish a list of generally agreed, technically implementable protocols - and that list will become the de facto legal benchmark for what counts as a valid opt-out.

Meanwhile, the GPAI Code of Practice - [finalized in July 2025](https://www.lw.com/en/insights/eu-ai-act-gpai-model-obligations-in-force-and-final-gpai-code-of-practice-in-place) - commits signatories to "identify and comply with appropriate machine-readable protocols used to express rights reservations." The behavioral obligations under the EU AI Act have been in force since August 2, 2025. Article 50 transparency requirements begin August 2, 2026.

Here is what that timeline means in practice: the protocols are being decided right now. The compliance infrastructure GPAI providers build will be shaped by the Commission's final protocol list. Publishers who are not using a protocol on that list when it is published will discover - after the window closes - that their opt-out does not qualify.

The enforcement trajectory is not speculative. We have a direct precedent in GDPR. When GDPR took effect in May 2018, regulators [issued only 16 fines in the first year](https://termly.io/resources/articles/biggest-gdpr-fines/), most below EUR 100,000. By 2023, a single year produced EUR 2.1 billion in penalties, anchored by Meta's EUR 1.2 billion fine. Cumulative GDPR fines reached approximately EUR 5.88 billion by January 2025. The five-year ramp from negligible enforcement to billion-euro fines followed a consistent pattern: initial grace period, test-case fines establishing precedent, then systematic enforcement against non-compliant organizations.

The EU AI Act [mirrors this enforcement structure](https://artificialintelligenceact.eu/article/101/). Article 101 sets fines for GPAI providers at up to 3% of total worldwide annual turnover or EUR 15 million, whichever is higher. Enforcement is centralized in the EU AI Office - a single body focused entirely on AI, not a distributed network of national regulators that took years to coordinate under GDPR. The enforcement ramp will be faster this time.

## The Counterargument - and Why It Does Not Hold

The strongest objection from publishers is practical: deploying machine-readable rights infrastructure is technically complex and expensive. The GPAI Code of Practice is voluntary. The fines land on AI companies, not on publishers. Why spend money on infrastructure when the enforcement pressure falls on someone else?

This argument gets the incentive structure exactly backwards.

The Code of Practice being voluntary does not make Article 53's copyright compliance obligation voluntary. That obligation is statutory. Every GPAI provider serving the EU market must comply with machine-readable opt-outs regardless of whether they signed the Code. Non-signatories simply do not get the safe-harbor benefit that Code adherence provides - they face the full force of Article 101 penalties with no procedural shield.

The enforcement leverage runs from publisher to AI company. When a publisher deploys a valid machine-readable opt-out, every GPAI provider that ignores it is in violation of Article 53. The publisher's opt-out is the trigger for enforcement. Without a valid opt-out, there is nothing to enforce. The publisher who has not deployed machine-readable infrastructure has not opted out. AI companies can train on that publisher's content without payment, without permission, and without legal consequence.

That is not a theoretical risk. It is the Hamburg court's holding.

And the complexity argument is one the industry has heard before. In 2016 and 2017, organizations argued that GDPR cookie consent was technically burdensome and operationally impractical. Then regulators imposed hundreds of millions in fines for consent violations, and a compliance industry materialized overnight. The question was never whether compliance infrastructure was complex. It was whether the cost of building it was lower than the cost of not having it. For GDPR, the answer was obvious by 2019. For the EU AI Act's TDM requirements, the Hamburg court just made it obvious now.

## What Encypher Sees From the Inside

We co-chair the C2PA Text Provenance Task Force. We authored Section A.7 of the C2PA specification, published January 8, 2026 - the only standard for embedding authentication manifests into unstructured text. We sit in the rooms where these protocols are being defined, and we see a gap between what the law now requires and what publishers have actually deployed.

The Hamburg court's standard - and the Commission's consultation - point toward a specific technical requirement: a rights signal that is not just machine-readable but machine-actionable. That means a signal that survives copying. One that cannot be stripped by a crawler. One that is cryptographically bound to the content itself, not to the URL where the content happens to live. One that an automated system can detect and interpret without human intervention.

Robots.txt fails this test. It is a domain-level signal that disappears the moment content leaves the server. HTML meta tags fail it. They can be stripped in transit, and most AI training pipelines do not parse them. Natural-language terms of service fail it. The Hamburg court said so explicitly.

C2PA text provenance meets the machine-actionable standard. It embeds a cryptographically signed manifest directly into the text content - the rights assertion travels with the content regardless of where it is copied, shared, or ingested. A GPAI provider's training pipeline encounters the content and the provenance signal together, because they are the same artifact. The signal cannot be accidentally stripped. It cannot be separated from the content it governs. When the Commission publishes its protocol list, the architecture that survives scrutiny will be the one that embeds rights signals at the content level, not the domain level.

This is what machine-actionable looks like in practice. Not a request posted at the boundary of your domain. A rights signal woven into the content itself.

## The Decision Publishers Face Now

Publishers have a binary choice in the next six months.

Deploy machine-readable rights infrastructure before August 2026, while the Commission is still finalizing the protocol list, and you are inside the consultation window. Your protocol can be on the list. Your opt-out will be valid from day one of systematic enforcement. You will have standing to trigger Article 53 liability against any GPAI provider that trains on your content without permission.

Wait, and you will be implementing against a standard you had no hand in shaping. Your content will have been ingested into training datasets during the gap - with no enforceable opt-out to contest it retroactively.

The GDPR parallel tells us what comes next. Test-case enforcement actions against mid-tier GPAI providers in 2026 and 2027. Escalating fines as precedent consolidates. Systematic enforcement by 2028 and 2029. The publishers who will benefit from that enforcement wave are the ones whose machine-readable opt-outs are already in place when the first test case lands.

The Hamburg court drew the floor. The Commission is standardizing it. The only question left is whether your rights infrastructure will be there when enforcement begins.
