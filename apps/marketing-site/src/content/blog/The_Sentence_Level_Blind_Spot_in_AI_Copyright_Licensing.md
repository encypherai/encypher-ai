---
title: "The Sentence-Level Blind Spot in AI Copyright Licensing"
date: "2026-02-23"
excerpt: "AI copyright licensing tracks rights at the article level. Courts and LLM memorization research confirm infringement happens at the sentence level. That gap is a liability."
author: "Encypher Team"
image: "/images/blog/The_Sentence_Level_Blind_Spot_in_AI_Copyright_Licensing.png"
tags: ["AI Copyright", "Content Provenance", "C2PA", "Publisher Licensing", "Content Authentication", "Legal Analysis", "AI Training Data", "Publisher Strategy"]
---

A Munich court examined nine song lyrics - individually, one by one - and [ordered OpenAI to cease reproduction of each one](https://cms-lawnow.com/en/ealerts/2025/12/gema-vs.-openai-munich-regional-court-i-issues-landmark-copyright-decision). Not per album. Not per artist catalog. Per lyric. That is the unit of infringement analysis courts are now applying. The publisher equivalent of a lyric is the paragraph. The sentence. And every rights registry, collective license, and opt-out mechanism in the AI copyright ecosystem today operates at the article or URL level - a granularity that cannot reach where courts are actually looking. Publishers are building licensing infrastructure for a unit of measurement that does not match how infringement is litigated, how memorization works, or how damages will be calculated. That is the blind spot. Closing it requires sentence-level attribution, and the technical standard to do it already exists.

## The Granularity Gap

The licensing market forming around AI training operates at one level: the article. Copyright Clearance Center launched its [AI Systems Training License](https://www.businesswire.com/news/home/20250304583503/en/CCC-Announces-AI-Systems-Training-License-for-the-External-Use-of-Copyrighted-Works-Coming-Soon) in March 2025, covering a broad repertory of works across science, technology, medicine, humanities, and news. The license is granted and tracked at the work level: articles, papers, and books identified by DOI or URL. Direct licensing deals between publishers and AI companies follow the same model. Robots.txt and opt-out registries operate at the URL or domain level. The entire infrastructure assumes the article is the atomic unit of rights.

It is not.

When GEMA sued OpenAI over song lyrics, the court did not ask whether ChatGPT had been trained on GEMA's catalog. It asked whether ChatGPT could reproduce specific lyrics - short texts individually authored and individually copyrighted. The court found that "simple user prompts led ChatGPT to reproduce substantial parts of the original lyrics almost verbatim," rejected OpenAI's text-and-data-mining defense, and awarded damages per work. The infringement analysis happened at sub-collection granularity. For news publishers, the analog is not the article. It is the paragraph. The sentence.

The CCC license does not account for this. A sentence extracted from a licensed article and reproduced verbatim in an LLM output carries no license status as a fragment. The license covers the work. It does not follow the sentence. If a model memorizes and reproduces three sentences from a licensed article, the CCC framework has no mechanism to track, attribute, or govern that specific reproduction.

That is the licensing gap. Nobody has closed it.

## What the Memorization Research Confirms

The gap would be theoretical if LLMs did not memorize specific passages. They do.

In January 2026, Ahmed et al. published ["Extracting Books from Production Language Models"](https://arxiv.org/abs/2601.02671), testing four production LLMs - Claude 3.7 Sonnet, GPT-4.1, Gemini 2.5 Pro, and Grok 3 - for their ability to reproduce copyrighted text. The results were definitive. Gemini 2.5 Pro reproduced Harry Potter passages with 76.8% near-verbatim recall without any jailbreaking. Grok 3 hit 70.3%. Jailbroken Claude 3.7 Sonnet output entire books with 95.8% near-verbatim recall. All four models reproduced "large portions of memorized copyrighted material."

The mechanism matters for the licensing question. A model does not store "the content of this article" as an abstract unit. It stores high-frequency token sequences - sentences, phrases, passages. Memorization is a sentence-level phenomenon. The model has no concept of an article boundary. It memorizes spans.

This means the actual unit of infringement risk - the thing a model can reproduce, and the thing a court will eventually trace - is the sentence or passage. Article-level licensing cannot reach it. Article-level evidence cannot prove it. A publisher who can only say "this article was in the training data" has not answered the question courts are asking: which specific passages were reproduced, and can you prove they are yours?

## How Courts Are Already Framing the Question

The evidentiary standard emerging in US litigation confirms the direction.

In January 2026, US District Judge Sidney Stein affirmed an order compelling OpenAI to produce a [20 million-log sample of ChatGPT conversations](https://natlawreview.com/article/openai-loses-privacy-gambit-20-million-chatgpt-logs-likely-headed-copyright) - specifically to find "conversations in which the plaintiffs' copyrighted works may have been reproduced in whole or in part." The discovery target is passage reproduction within conversations. Not which articles were scraped. Not which URLs appeared in the training data. Passages reproduced in outputs.

The New York Times's strongest evidence at the pleading stage was not a list of scraped URLs. It was specific verbatim paragraphs - near-exact reproductions of individual passages from Times articles, surfaced in ChatGPT outputs. That is what got the case past a motion to dismiss. That is the evidentiary bar.

The counterargument is that article-level proof might be enough to establish liability in some cases. In the narrowest sense, that is true: demonstrating that a copyrighted work appeared in training data is relevant evidence. But it is not enough to establish damages at scale, and it is not enough to survive a fair use defense that argues the model learned general patterns rather than specific texts. When OpenAI argues that its model extracted statistical patterns and did not copy specific expression - and it will argue exactly this - the publisher's response must be specific passages, not general URLs. Sentence-level evidence is what converts a liability finding into a calibrated damages award.

Without it, a publisher can prove their article was scraped. They cannot prove what was reproduced. That distinction is the difference between winning a ruling and collecting meaningful damages.

## The Counterargument and Why It Fails

Three objections arise consistently.

First: copyright in a news article attaches to the whole work, not individual sentences. Sentences below a creativity threshold may not be independently copyrightable, making sentence-level attribution legally unnecessary. This confuses two different questions. The copyrightability question - whether an isolated sentence merits protection - is separate from the evidence question. Even if individual sentences lack independent copyright protection, sentence-level provenance is the mechanism by which a publisher proves which portions of a copyrighted work were reproduced verbatim. That is the exact evidentiary standard applied in both Munich and New York. Courts are not asking whether a single sentence is copyrightable. They are asking whether specific sentences were copied from a copyrighted work. Different question. Different infrastructure requirement.

Second: article-level licensing is the only practical scale. Requiring sentence-level attribution for every piece of content would impose impossible operational burdens. This assumes sentence-level attribution is an editorial workflow change. It is not. The C2PA specification defines an infrastructure-level embedding mechanism. A publisher's content management system embeds credentials at publish time. Individual journalists do not act. The operational overhead is comparable to adding a canonical URL tag - a one-time CMS integration, not a per-article editorial step.

Third: LLM memorization of specific passages is edge-case behavior that providers can patch out. The January 2026 research tested current production models with guardrails enabled and found near-verbatim extraction without jailbreaking on two of four models. Memorization is a training artifact, not a guardrail failure. It cannot be patched without retraining. It is not an edge case. It is how the technology works.

## What Encypher Sees From the Inside

We co-chair the C2PA Text Provenance Task Force. We authored Section A.7 of the [C2PA 2.3 specification](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html), published January 8, 2026 - the only open standard for embedding cryptographically signed content credentials into unstructured text. The specification was reviewed by Google, OpenAI, Adobe, Microsoft, the New York Times, the BBC, and the Associated Press through the C2PA consortium.

Section A.7 addresses the granularity gap directly. It defines a mechanism for embedding a C2PA manifest - containing publisher identity, licensing terms, and creation metadata - at the sentence or span level within a plaintext document, using Unicode variation selectors. The credential is not metadata attached to a URL. It is embedded in the text itself. It travels with the fragment after copy-paste, syndication, RSS distribution, or ingestion into a training pipeline.

This is what changes the evidentiary calculus. When a court orders discovery of "passages reproduced in whole or in part," a publisher with C2PA-embedded text can produce a cryptographically signed chain linking a reproduced sentence back to its original publication, its author, and its licensing terms. A publisher without it must reconstruct that chain manually - if they can reconstruct it at all.

The standard is published. The technical barrier is gone. The remaining question is adoption timing: whether publishers embed provenance signals at the sentence level before courts start demanding that evidence, or scramble to build the infrastructure after the fact. Building under litigation pressure is more expensive. It always is.

## The Window Is Open

The publishers who will define the next phase of AI copyright litigation are not the ones with the most expensive lawyers. They are the ones embedding provenance at the sentence level today - so that when a court orders discovery of reproduced passages, they have a systematic, cryptographically verifiable answer rather than a manual reconstruction effort.

Every major precedent in the last six months points the same direction. Munich awarded damages per passage. New York ordered discovery of passage-level reproductions. Memorization research confirmed that production LLMs store and reproduce specific sentences. The licensing infrastructure being built by the largest rights organizations does not operate at that level.

The gap between where courts are looking and where publishers are building is the central unforced error in AI copyright strategy today. The C2PA standard that closes the gap exists. The question is timing. The window to build sentence-level attribution infrastructure before the next round of major rulings is open now. It will not stay open.
