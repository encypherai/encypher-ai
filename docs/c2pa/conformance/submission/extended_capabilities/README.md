# Extended Capabilities

This section documents two production Encypher capabilities that go beyond the
current C2PA conformance program submission categories. Both are defined in the
C2PA v2.3 specification but are not yet covered by conformance testing.

Evidence files, signed samples, and verification results are included below.
We are happy to help strengthen the conformance program with these capabilities
-- for example, by providing test vectors, verification tooling, or
specification contributions.

---

## 1. Live Video Streaming (Per-Segment C2PA Signing)

**Spec reference**: C2PA v2.3, Section 19 (Live Streaming)

**Description**

Encypher's video stream signing service applies C2PA provenance to live video
at the segment level:

    RTMP ingest -> per-segment C2PA signing -> HLS delivery with manifests

Each segment is signed independently with a `c2pa.livevideo.segment` assertion
containing `sequenceNumber`, `streamId`, and backward `previousManifestId`
chaining via `continuityMethod: "c2pa.manifestId"`. A SHA-256 Merkle tree over
segment manifest hashes provides a finalization root for the complete stream.

**Implementation**

Source: `enterprise_api/app/services/video_stream_signing_service.py`

Pipeline: c2pa-rs (c2pa-python 0.29.0 / c2pa-rs 0.78.4), ECC P-256 / ES256,
SSL.com TSA (RFC 3161).

**Evidence files**

| File | Description |
|------|-------------|
| live_video_streaming_evidence.json | Full session: 3 segments signed, verified, Merkle root finalized |
| signed_stream_segment_0.mp4 | Signed MP4 segment (17,385 bytes) with c2pa.livevideo.segment assertion |

**Results summary**

- 3 segments signed (segment 0: 17,385 bytes, segments 1-2: 17,451 bytes)
- All 3 segments verified valid (c2pa-python Reader)
- Merkle root: sha256:d500354c92eccbc900d95909190ea97448dcd1d0e31fd13ef11f6512b6c7bef2
- Backward manifest chaining verified across all segments
- Certificate: CN=Encypher Conformance Test Cert, O=Encypher Corporation

---

## 2. Unstructured Text Provenance (C2PA Text Manifests)

**Spec reference**: C2PA v2.3, Manifests_Text.adoc

**Description**

Encypher embeds C2PA-compatible manifests in plain text using Unicode Variation
Selectors (U+FE00-FE0F, U+E0100-E01EF) as defined in Manifests_Text.adoc.
This allows content provenance for text that has no binary file container --
web pages, messaging platforms, social media posts, and AI-generated text output.

**Implementation**

Source: `encypher` Python SDK (`UnicodeMetadata.embed_metadata()`)

Pipeline: Ed25519 COSE_Sign1 signing, Unicode Variation Selector embedding,
hard binding via content hash.

**Evidence files**

| File | Description |
|------|-------------|
| text_c2pa_evidence.json | Sign, verify, and tamper detection results |
| signed_text_sample.txt | Signed text file with embedded C2PA manifest (1,656 chars, 1,410 embedded) |

**Results summary**

- Original text: 246 characters
- Signed text: 1,656 characters (1,410 invisible variation selector characters embedded)
- Verification: PASS (signature valid, signer_id recovered, hard binding verified)
- Tamper detection: PASS (modified text correctly rejected with hash mismatch)
- Claim generator: Encypher Enterprise API/2.0
- Actions: c2pa.created
- Custom assertions: com.encypher.provenance
- Hard binding: enabled (content hash integrity)

---

## Contact

If the C2PA working group is interested in test vectors, specification drafts,
or implementation contributions for either capability, please contact
conformance@encypher.com.

We can also provide access to our File Inspector verification tool
(https://encypher.com/tools/file-inspector) for testing manifests produced
by any implementation against our verifier.
