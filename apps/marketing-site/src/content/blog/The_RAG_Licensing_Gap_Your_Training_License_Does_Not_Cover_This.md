---
title: "The RAG Licensing Gap: Your Training License Does Not Cover This"
date: "2026-02-23"
excerpt: "RAG inference creates separate copyright liability from training. Courts and the US Copyright Office now treat retrieval-based AI outputs as distinct legal acts requiring their own licenses."
author: "Encypher Team"
image: "/images/blog/The_RAG_Licensing_Gap_Your_Training_License_Does_Not_Cover_This.png"
tags: ["AI Copyright", "Publisher Licensing", "Content Provenance", "C2PA", "Legal Analysis", "AI Companies", "Publisher Strategy", "AI Governance"]
---

AI companies that spent tens of millions on training-data licenses may have solved the wrong problem. In November 2025, a federal judge in the Southern District of New York [ruled](https://www.loeb.com/en/insights/publications/2025/11/advanced-local-media-llc--v-cohere-inc) that an AI company's RAG-generated summaries can constitute direct copyright infringement -- even when those summaries differ in tone, length, and style from the original articles. The court was not evaluating training. It was evaluating what happens at inference time, when a RAG system retrieves a publisher's article and serves a summary to the user. That is a separate legal act. And for most AI companies running RAG pipelines today, it is an entirely unlicensed one.

The training-data licensing wave of 2023-2024 created a false sense of security. Companies signed deals. Headlines declared the copyright wars resolved. But those deals covered one thing: the right to include content in training datasets. They did not cover the right to retrieve that same content in real time and summarize it in response to a user query. Training and inference are two different legal acts, with two different fair use analyses, requiring two different licenses. The gap between them is where the next wave of litigation is already landing.

## Training vs. Inference: Two Different Legal Acts

The US Copyright Office made this distinction explicit. In its [Part 3 Report on Generative AI](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-3-Generative-AI-Training-Report-Pre-Publication-Version.pdf), published in 2025, the Office stated that RAG "involves the reproduction of copyrighted works" and that RAG output is "less likely to be transformative where the purpose is to generate outputs that summarize or provide abridged versions of retrieved copyrighted works, such as news articles."

Read that carefully. The Copyright Office is drawing a bright line. Training a model on copyrighted content may qualify as transformative use -- the model learns statistical patterns, not specific articles. Courts can debate that. But when a RAG system retrieves a specific article and produces a summary of that specific article in response to a user query, the transformativeness argument collapses. The output is doing exactly what the original did: delivering the substance of the reporting to a reader. The fact that it is shorter or rephrased does not make it transformative. It makes it a substitute.

This distinction has enormous practical consequences. A company that licensed the right to include the Washington Post's archive in its training data has not licensed the right to retrieve a Washington Post article at inference time and serve a condensed version to a user. Those are different rights. They require different agreements.

The contractual record confirms this. As [A Media Operator reported](https://www.amediaoperator.com/analysis/questions-mount-around-openais-licensing-deals-with-publishers/), the Washington Post's initial deal with OpenAI "does not mention using The Post's content for training" -- it specifically covers RAG-style summaries and attribution in ChatGPT responses. Training licenses and inference licenses are separate instruments. OpenAI understood this. Most of the industry did not.

## The Litigation Map Has Shifted

If RAG were legally safe, you would expect the companies building RAG-first products to face less litigation than the companies training massive models on scraped data. The opposite is happening.

Perplexity AI -- a company whose core product is RAG-based web retrieval, not large-scale model training -- has become one of the most sued AI companies in the space. In October 2024, [Dow Jones and NYP Holdings filed suit](https://www.cnbc.com/2024/10/21/murdoch-firms-dow-jones-and-new-york-post-sue-perplexity-ai.html) alleging that Perplexity's RAG index "copies works as inputs" and that its response outputs "contain full or partial verbatim reproductions" of copyrighted articles. That was the first major RAG-specific lawsuit. It was not the last. By the end of 2025, Perplexity faced additional suits from the New York Times, Encyclopedia Britannica, Merriam-Webster, and multiple international publishers.

Cohere -- another company whose RAG feature is central to its enterprise product -- was hit with the Advance Local Media suit that produced the November 2025 ruling. Judge McMahon denied Cohere's motion to dismiss, finding that publishers plausibly stated claims for direct copyright infringement based on RAG-generated summaries. The court noted that some outputs lifted several paragraphs verbatim from source articles.

The [Copyright Alliance's 2025 litigation tracker](https://copyrightalliance.org/ai-copyright-lawsuit-developments-2025/) documents the shift: over 70 AI copyright lawsuits were active in 2025, and "in a number of new cases, plaintiffs focused specifically on RAG technology as a separate vector of infringement." Forbes, Conde Nast, the LA Times, The Atlantic, and The Guardian all filed RAG-specific claims.

This is the counter-intuitive reality. Companies that deliberately avoided training on copyrighted data -- choosing instead to retrieve and summarize at query time -- are now facing the same copyright exposure that training-heavy models faced. The "safe" approach turned out to be a different kind of unsafe.

## The Counterargument: Fair Use Still Applies to RAG

The strongest counterargument is that fair use is not dead for RAG. And that is true -- to a point.

Where a RAG system synthesizes information across many sources to produce a genuinely new analysis, fair use remains plausible. The Copyright Office acknowledged that non-commercial research uses of retrieved content could qualify. And in practice, many RAG queries produce outputs that are factual syntheses, not summaries of individual articles. A user asking "What is the current inflation rate?" is not requesting a substitute for any single article.

Some publisher deals also implicitly cover RAG. Axios and The Guardian have agreements with OpenAI that appear to span both training and response attribution. A well-drafted license can cover both uses.

But these arguments have two problems.

First, the deals that cover RAG were negotiated by a handful of publishers with the leverage to demand comprehensive terms. The vast majority of publishers whose content appears in RAG pipelines have no deal at all. And the vast majority of companies running RAG products -- not just the OpenAIs and Perplexities, but every enterprise deploying a RAG-powered internal tool -- have licensed nothing.

Second, the fair use argument works only for genuinely transformative synthesis. It does not work for what RAG systems most commonly do with news content: retrieve a single article and summarize it. The Copyright Office was explicit on this point. Courts are following. Judge McMahon did not need to see every Cohere output to deny the motion to dismiss -- she just needed to see that some outputs were substitutive summaries. At scale, any RAG system retrieving news content will produce substitutive summaries. The question is not whether it happens but how often.

## The Audit Trail Vacuum

There is a deeper structural problem that neither side of the debate has solved: nobody can prove what happened.

When a RAG system retrieves content and generates a response, there is no standard record of which source was retrieved, at what time, under what license terms, or how much of the original appeared in the output. The retrieval is ephemeral. The vector search is logged nowhere. The generated response is served and forgotten.

This hurts defendants. In the Cohere case, the court ruled against the company at the motion-to-dismiss stage based on a handful of examples. At trial, Cohere will need to demonstrate that its RAG system operated responsibly across millions of queries. Without a retrieval log, it cannot.

Some argue the audit trail vacuum helps defendants too -- if plaintiffs cannot reconstruct what was retrieved, they cannot prove infringement at scale. This is technically true. But courts are already showing they do not need complete evidence to let cases proceed. The standard at the motion-to-dismiss stage is plausibility, not proof. And judges are finding RAG infringement claims plenty plausible. At trial, the absence of records is more likely to be treated as spoliation or willful ignorance than as a defense.

The parallel to web server access logs is instructive. In early internet litigation, companies that failed to maintain access logs found themselves unable to defend against claims about what content was served and to whom. The standard response was not "we cannot prove it did not happen" but rather "why did you not keep records?" Courts are heading toward the same expectation for RAG retrieval.

Both plaintiffs and defendants need a retrieval record. Right now, neither has one.

## What Encypher Sees From the Inside

We co-authored Section A.7 of the C2PA specification -- the only published standard for embedding cryptographic provenance into unstructured text. That standard was developed with input from Google, OpenAI, Adobe, Microsoft, the New York Times, BBC, and AP through the C2PA consortium. We sit at the table where these problems are being solved.

From that position, we see the RAG licensing gap as fundamentally an infrastructure problem. The legal question -- whether RAG infringes -- is being answered by courts right now, and the answer is increasingly "yes, in many cases." The contractual question -- whether companies need separate inference licenses -- is being answered by the deals publishers are already structuring. What remains unsolved is the technical question: how do you build a RAG system that can demonstrate, cryptographically, what it retrieved, when, from which source, and under what terms?

C2PA text provenance provides exactly this mechanism. A RAG pipeline instrumented with C2PA can attach a signed manifest to every retrieval event -- recording the source, the timestamp, the licensing status of the retrieved content, and the relationship between the retrieved material and the generated output. That manifest is cryptographically signed and tamper-evident. It travels with the output. It can be verified by any party -- publisher, regulator, or court.

This is the difference between a compliance posture and a liability posture. A company that cannot produce retrieval records is in a liability posture: every query is a potential infringement it cannot disprove. A company that maintains signed provenance records for every retrieval is in a compliance posture: it can demonstrate responsible use, source by source, query by query.

## The Window Is Closing

The Copyright Office report came out in May 2025. The Cohere ruling came in November 2025. Over 70 lawsuits are active. The legal framework is crystallizing fast.

AI companies and enterprises running RAG products need two things. First, proper inference licenses -- separate from and in addition to any training-data agreements. That is a contract problem, and publishers are increasingly willing to negotiate. Second, a provenance record of every retrieval -- a cryptographic audit trail that proves what was retrieved, when, and under what terms. That is a technical infrastructure problem.

The companies that build this infrastructure now will be able to defend themselves when -- not if -- their RAG operations come under legal scrutiny. The companies that do not will find themselves in the same position as the early AI training companies: unable to explain what they did with other people's content, facing courts that are running out of patience for the "we did not know" defense.

The training-data licensing wave was a $100 million lesson in solving the wrong problem first. The RAG licensing gap is the real exposure. The question is whether the industry learns from the first mistake or repeats it.
