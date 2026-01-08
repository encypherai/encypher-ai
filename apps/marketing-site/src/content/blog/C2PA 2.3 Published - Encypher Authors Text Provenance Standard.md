---
title: "C2PA 2.3 Published: Encypher Authors Text Provenance Standard"
date: "2026-01-08"
excerpt: "The C2PA 2.3 specification is now live, featuring Section A.7 on Embedding Manifests into Unstructured Text—authored by Encypher. This marks a milestone for text authentication."
author: "Erik Svilich"
image: "/images/blog/c2pa-2-3-published/c2pa-text-standard-header.png"
tags: ["C2PA", "ContentProvenance", "TextAuthenticity", "StandardsAuthority", "Milestone", "Patent"]
---

**By: Erik Svilich, Founder & CEO | Encypher | C2PA Co-Chair**

Today marks a pivotal moment in the history of content authenticity: the **C2PA 2.3 specification is now published**, and with it, **Section A.7: Embedding Manifests into Unstructured Text**—the section I authored as Co-Chair of the C2PA Text Provenance Task Force.

## What This Means

For the first time, there is an **official, global standard** for embedding cryptographic provenance into plain text. This enables:

- **Proof of origin** for any text content—articles, reports, AI outputs
- **Tamper-evident signatures** that survive copy-paste and distribution
- **Interoperability** across platforms, tools, and ecosystems

The specification is live at: [C2PA Section A.7](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#embedding_manifests_into_unstructured_text)

## The Technical Foundation

Section A.7 introduces the `C2PATextManifestWrapper` structure, which uses Unicode variation selectors to embed C2PA manifests invisibly within text. Key elements include:

- **Magic number:** `C2PATXT\0` (0x4332504154585400)
- **Encoding:** Unicode variation selectors (U+FE00-U+FE0F and U+E0100-U+E01EF)
- **Prefix:** Zero-Width No-Break Space (U+FEFF) for forward compatibility
- **Validation:** NFC normalization and byte-offset exclusion handling

This approach ensures that provenance data travels with the text itself—not in a separate file or database.

## From Task Force to Standard

When I joined C2PA as Co-Chair of the Text Provenance Task Force alongside colleagues from Google, BBC, OpenAI, Adobe, and Microsoft, the challenge was clear: **text had no proof of origin**.

Images had EXIF. Videos had container metadata. Documents had embedded signatures. But plain text—the format of AI chatbots, news articles, and most digital communication—had nothing.

We changed that.

## What Comes Next

The standard is published, but our work is accelerating:

### Patent-Pending Enhancements (ENC0100)

Yesterday (January 7, 2026), we filed our first provisional patent application: **"Granular Content Attribution and Related Methods and Systems for Content Attribution, Authentication, and/or Provenance."** This 49-page specification with **83 claims** covers the innovations that extend C2PA beyond document-level authentication:

**Key Covered Innovations:**

1. **Segment-Level Merkle Trees (Claims 1-20):** Hash each sentence → build binary hash tree → generate cryptographic proof of any segment's membership

2. **Distributed Unicode Embedding (Claims 56-66):** Spread metadata across carrier positions (after spaces, punctuation) for resilience against partial deletion

3. **Evidence Generation System (Claims 38-52):** Court-admissible evidence packages with Merkle proofs, timestamps, and blockchain anchors

4. **Two-Layer Architecture (Claims 61-63):** Segment markers within sentences + document manifest at end—dual verification paths

5. **Per-Document Revocation (Claims 53-55):** Bitstring registry enables revoking individual documents without invalidating signing certificates

6. **Similarity Fingerprinting (Claims 72-77):** SimHash/MinHash for paraphrase detection combined with Merkle proofs for cryptographic verification

While C2PA Section A.7 provides the open standard baseline, our patent-pending enhancements enable:

- **Sentence-level granularity** (not just document-level)
- **Court-admissible evidence generation** with Merkle proofs
- **Willful infringement enablement** through formal notice infrastructure
- **Quote integrity verification** to detect AI hallucinations
- **Resilient embedding** that survives partial text deletion

### Syracuse Symposium

On **February 25, 2026**, we're convening the Syracuse Symposium to translate technical standards into market licensing frameworks. Publisher GCs and AI company commercial leads will define the terms of engagement.

### Infrastructure Rollout

Our API and SDKs (Python, TypeScript, Go, Rust) are production-ready. Publishers can implement sentence-level tracking in 30 days. AI labs get one integration for the entire publisher ecosystem.

## The Bigger Picture

Text on the open web has had no cryptographic proof of origin—until now. When content is distributed through B2B licensees, scraped by aggregators, or used to train AI models, ownership has been unprovable. AI companies could claim "we didn't know it was yours."

With C2PA 2.3 and our patent-pending enhancements, that changes. Publishers can:

1. Embed proof directly into text
2. Serve formal notice to AI companies
3. Transform "innocent infringement" into "willful infringement"

This isn't about litigation—it's about infrastructure. Infrastructure for licensing. Infrastructure for attribution. Infrastructure for trust.

## Try It Today

- **Publishers:** [See the Publisher Demo](/publisher-demo)
- **AI Labs:** [See the AI Demo](/ai-demo)
- **Developers:** [GitHub - encypher-ai](https://github.com/encypherai/encypher-ai)

The standard is published. The infrastructure is ready. The economy awaits.

---

*Erik Svilich is Founder & CEO of Encypher Corporation and Co-Chair of the C2PA Text Provenance Task Force. He authored C2PA Section A.7: Embedding Manifests into Unstructured Text.*

#C2PA #ContentProvenance #TextAuthenticity #StandardsAuthority #AIContent #PatentPending
