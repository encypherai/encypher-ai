# EU AI Act Code of Practice: Patent Position Analysis

**Classification:** CONFIDENTIAL - Erik and IP Counsel Only
**Date:** March 28, 2026
**Related Document:** EU AI Act Code of Practice Public Comment v3.0

---

**ACCESS CONTROL:** This document maps ENC0100 patent claims to EU AI Act Code of Practice requirements. It must not be bundled with the public comment submission, shared beyond Erik and qualified IP counsel, or stored in any location accessible to the broader team. If the public comment draft is circulated for internal review, this appendix must be removed first.

---

## FRAND Risk Assessment

If C2PA becomes the referenced standard in EU regulation, there may be pressure for standard-essential patents to be licensed on FRAND terms.

Our position is protected:

- C2PA Section A.7 covers document-level provenance. That is what we contributed to the standard and what the submission advocates as the baseline.
- ENC0100 claims (sentence-level Merkle trees, fingerprinting, distributed embedding, streaming authentication) go beyond the C2PA standard. They are enhancements, not standard-essential patents.
- The submission draws this line explicitly. It never attributes segment-level capabilities to C2PA.

The discipline: never contribute patent-protected sentence-level claims to the C2PA standard. The standard stays document-level. Our patents cover the granular enhancements that organizations seeking robust compliance will want. That is the moat.

## Key Patent Intersections with Code of Practice

| Code of Practice Concept | ENC0100 Claims | Assessment |
|---|---|---|
| Two-layered marking (metadata + watermarking) | Claims 61-63 (multi-layer authentication) | Our patent covers the architecture the regulation describes |
| Secured metadata for text | Claims 31-44 (manifest embedding via non-rendering Unicode) | Anyone implementing text-specific invisible C2PA embedding likely practices our claims |
| Text watermarking | Claims 56-60 (distributed encoding), Claims 64-66 (ECC) | Text-specific invisible watermarking via Unicode is our patent territory |
| Fingerprinting | Claims 72-77 (LSH + Merkle integration) | If fingerprinting becomes standard practice, our hybrid approach is the strongest patented method |
| Streaming authentication | Claims 46-52 (incremental Merkle construction) | Only patented approach for real-time LLM output signing |
| Detection/verification | Claims 21-30 (evidence generation), Claims 41-44 (verification) | Verification tools will need to practice detection methods we have claimed |
| Editorial review attestation | Claims 21-30 (evidence generation) | Attestation workflow produces cryptographic evidence packages covered by these claims |

## Submission Discipline

The public comment submission (v3.0) was reviewed against these claims to ensure:

1. No specific cryptographic mechanisms named in the submission text (e.g., "Merkle trees" removed from all nine points)
2. Segment-level capabilities described as "technologies that exist today" without naming the architecture
3. C2PA baseline (document-level) clearly separated from proprietary enhancements (segment-level)
4. No language that could be interpreted as contributing patent-protected claims to the C2PA standard
5. Streaming authentication described functionally ("cryptographic authentication structures can be constructed progressively") without naming the specific incremental construction method

## Action Items for IP Counsel

1. Review the full submission text for any remaining patent-to-regulation breadcrumbs
2. Assess FRAND implications if C2PA is designated as the reference standard in the final Code of Practice
3. Monitor other public comments for competitors positioning in the same space
4. Evaluate whether a defensive publication is warranted for any aspects of the technology not covered by ENC0100
