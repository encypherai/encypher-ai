# Blog Content Calendar

Publishing cadence: Monday (technical depth) and Thursday (market/regulatory/use-case).
Launch date: April 7, 2026.

---

## Technical Depth Posts (Monday cadence)

### 1. Content Provenance Is Not Content Detection: The Technical Distinction
- **Publish date:** 2026-04-07
- **Pillar:** /content-provenance
- **Cluster:** /compare/content-provenance-vs-content-detection
- **Summary:** Detection asks whether content was AI-generated, a statistical question with known false positive rates. Provenance answers who created content and provides cryptographic proof, a deterministic question with a binary answer. The two tools solve different problems for different audiences.

### 2. 31 Media Types, One Standard: Inside Encypher's v2.0.0 API
- **Publish date:** 2026-04-14
- **Pillar:** /c2pa-standard/media-types
- **Cluster:** /content-provenance/verification
- **Summary:** The v2.0.0 API unifies provenance signing across 13 image formats, 6 audio formats, 4 video formats, 5 document formats, and 3 font formats under a single /sign/media endpoint. Each format receives a C2PA manifest embedded via JUMBF containers with COSE signatures, with free verification available for all 31 types.

### 3. How C2PA Manifests Are Embedded in JPEG Files
- **Publish date:** 2026-04-21
- **Pillar:** /c2pa-standard/manifest-structure
- **Cluster:** /content-provenance/images
- **Summary:** JPEG files carry C2PA manifests in a dedicated APP11 marker segment using JUMBF container structure. The manifest binds to image pixels via a content hash, so any manipulation that changes pixel data invalidates the cryptographic signature and surfaces during verification.

### 4. Merkle Trees for Content: How Sentence-Level Attribution Works
- **Publish date:** 2026-04-28
- **Pillar:** /content-provenance/text
- **Cluster:** /cryptographic-watermarking/text
- **Summary:** A Merkle tree built over individual sentences lets any subset of a document be verified independently. Removing or modifying a sentence changes that leaf's hash, which invalidates the path to the root and proves tampering without requiring the full original document.

### 5. Live Stream Provenance: Per-Segment C2PA Manifests Explained
- **Publish date:** 2026-05-05
- **Pillar:** /content-provenance/live-streams
- **Cluster:** /c2pa-standard/media-types
- **Summary:** C2PA 2.3 Section 19 defines per-segment manifests for CMAF streams, where each HLS or DASH chunk carries its own signed manifest that back-links to the previous segment. The chain makes any edited or replaced segment detectable during replay verification.

### 6. Cryptographic Watermarking vs. Statistical Watermarking: A Technical Comparison
- **Publish date:** 2026-05-12
- **Pillar:** /cryptographic-watermarking/vs-statistical-watermarking
- **Cluster:** /compare/encypher-vs-synthid
- **Summary:** Cryptographic watermarking embeds a signed, verifiable identity token into content at creation. Statistical watermarking (SynthID's approach) shifts the token distribution of AI outputs so the originating model can recognize them. The two approaches differ in durability, reversibility, and the type of question each answers.

### 7. How Free Verification Works Across 31 Media Types
- **Publish date:** 2026-05-19
- **Pillar:** /content-provenance/verification
- **Cluster:** /c2pa-standard/media-types
- **Summary:** Encypher's public verification API accepts any of 31 MIME types, requires no authentication, and returns provenance data including signer identity, content hash status, and manifest chain validity. The endpoint is designed for integration into CMS platforms, browser extensions, and automated pipelines.

### 8. JUMBF Containers and COSE Signatures: The Structure of a C2PA Manifest
- **Publish date:** 2026-05-26
- **Pillar:** /c2pa-standard/manifest-structure
- **Cluster:** /c2pa-standard/section-a7
- **Summary:** A C2PA manifest is a JUMBF (JPEG Universal Metadata Box Format) container holding a set of COSE (CBOR Object Signing and Encryption) signed assertions. Understanding the container structure explains why manifests can be embedded in media files without altering perceived content and why the cryptographic binding covers the original bytes.

### 9. Why Blockchain Timestamping Is Not Content Provenance
- **Publish date:** 2026-06-02
- **Pillar:** /content-provenance/vs-blockchain
- **Cluster:** /compare/c2pa-vs-blockchain
- **Summary:** Blockchain timestamping records that a content hash existed at a point in time, which proves prior existence. It does not embed identity into the content itself, so the proof cannot travel with the content through distribution channels or survive format conversion. Embedded provenance travels with every copy.

### 10. Perceptual Hashing for Images: Finding Derivatives of Signed Content
- **Publish date:** 2026-06-09
- **Pillar:** /content-provenance/images
- **Cluster:** /cryptographic-watermarking/how-it-works
- **Summary:** A cryptographic content hash fails on any pixel change, which is intentional for tamper detection. A perceptual hash (pHash) matches images that are visually similar despite resizing, cropping, or re-encoding, enabling rights holders to discover derivative uses of originally signed images at scale.

---

## Market / Regulatory / Use-Case Posts (Thursday cadence)

### 11. The EU AI Act Requires Content Provenance by August 2026. Here Is What That Means.
- **Publish date:** 2026-04-09
- **Pillar:** /content-provenance/eu-ai-act
- **Cluster:** /content-provenance/for-enterprises
- **Summary:** Article 50 of the EU AI Act mandates machine-readable disclosure for AI-generated content, with GPAI model providers subject to transparency requirements from August 2, 2026. Content provenance infrastructure built on C2PA provides a compliant mechanism for both content creators and AI system operators.

### 12. Content Provenance for Academic Publishers: Protecting Research Integrity
- **Publish date:** 2026-04-16
- **Pillar:** /content-provenance/for-publishers
- **Cluster:** /content-provenance/academic-publishing
- **Summary:** Peer-reviewed journals face two distinct problems: AI-generated submissions that misrepresent research authorship, and unauthorized reproduction of published work in AI training datasets. Sentence-level provenance addresses both by attaching verifiable authorship to original text and establishing a formal notice baseline for downstream use.

### 13. The Three Layers of Content Protection: Access Control, Provenance, Attribution
- **Publish date:** 2026-04-23
- **Pillar:** /content-provenance
- **Cluster:** /content-provenance/for-publishers
- **Summary:** Access control (paywalls, robots.txt) governs who can read content but cannot follow it after distribution. Provenance embeds identity into the content itself so it travels through any channel. Attribution converts provenance data into a licensing record, closing the loop between distribution and compensation.

### 14. From Innocent Infringement to Willful: How Formal Notice Changes the Legal Calculus
- **Publish date:** 2026-04-30
- **Pillar:** /cryptographic-watermarking/legal-implications
- **Cluster:** /content-provenance/for-publishers
- **Summary:** Under copyright law, actual knowledge of ownership converts innocent infringement into willful infringement, raising statutory damages from $750 to $150,000 per work. Embedded provenance markers constitute constructive notice at the moment of scraping, eliminating the "we didn't know" defense that has shielded AI training pipelines.

### 15. Why Audio Provenance Matters: Podcasts, Music, and the AI Training Pipeline
- **Publish date:** 2026-05-07
- **Pillar:** /content-provenance/audio-video
- **Cluster:** /content-provenance/music-industry
- **Summary:** Audio content enters AI training pipelines through transcription services, which strip original metadata and deliver clean text with no rights signal attached. Embedding C2PA provenance into the original audio file before transcription creates a persistent rights record that survives the format conversion step.

### 16. Content Provenance for News Publishers: The AP, Reuters, and BBC Precedent
- **Publish date:** 2026-05-14
- **Pillar:** /content-provenance/for-publishers
- **Cluster:** /content-provenance/news-publishers
- **Summary:** AP, Reuters, and BBC distribute content through wire services to thousands of downstream outlets, each of which re-publishes with varying attribution. Embedded provenance makes every copy of a wire story traceable to its origin regardless of how the downstream outlet attributes the source or whether metadata is stripped from the file.

### 17. Video Provenance in the Age of Deepfakes: Why Detection Is Not Enough
- **Publish date:** 2026-05-21
- **Pillar:** /content-provenance/audio-video
- **Cluster:** /compare/content-provenance-vs-content-detection
- **Summary:** Deepfake detection models flag synthetic faces with varying confidence thresholds. A provenance-first approach skips the inference question entirely: a video with a valid C2PA manifest from a known camera or studio is genuine by the standard of cryptographic proof, regardless of what detection models output.

### 18. The Document Provenance Gap: PDFs, EPUBs, and Legal Filings
- **Publish date:** 2026-05-28
- **Pillar:** /content-provenance
- **Cluster:** /c2pa-standard/media-types
- **Summary:** PDFs support digital signatures but those signatures authenticate the signer's identity, not content authorship or training data rights. C2PA manifests embedded in PDF, EPUB, and DOCX files add a content provenance layer distinct from digital signatures, covering the rights and attribution questions that document signing was never designed to answer.

### 19. What Publishers Need to Know About the C2PA Conformance Program
- **Publish date:** 2026-06-04
- **Pillar:** /c2pa-standard
- **Cluster:** /c2pa-standard/members
- **Summary:** The C2PA conformance program tests whether implementations correctly produce and consume C2PA manifests according to the specification. Publishers selecting content provenance vendors should require conformance testing results rather than accepting self-reported C2PA compatibility claims.

### 20. Machine-Readable Rights: How Content Licensing Becomes Automated
- **Publish date:** 2026-06-11
- **Pillar:** /content-provenance
- **Cluster:** /content-provenance/for-ai-companies
- **Summary:** Rights information embedded in provenance manifests can specify permitted uses, licensing terms, and attribution requirements in a structured format that AI systems can parse at ingestion time. This shifts content licensing from a post-hoc negotiation after infringement to a pre-ingestion signal that AI pipelines can act on without human review.
