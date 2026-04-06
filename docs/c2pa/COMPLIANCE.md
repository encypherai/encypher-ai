# Encypher C2PA Compliance Reference

This document maps Encypher's implementation to the C2PA Technical Specification 2.3.

## Quick Links to C2PA Specification

- [C2PA Specification 2.3](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html)
- [C2PA Implementation Guidance 2.3](https://spec.c2pa.org/specifications/specifications/2.3/guidance/Guidance.html)
- [C2PA Security Considerations](https://spec.c2pa.org/specifications/specifications/2.3/specs/Security_Considerations.html)
- [C2PA Trust Lists](https://spec.c2pa.org/conformance-explorer/)

---

## Text Manifest Embedding (C2PATextManifestWrapper)

Encypher implements the `C2PATextManifestWrapper` specification for embedding C2PA manifests in unstructured text.

| Spec Requirement | Spec Reference | Encypher Implementation | Status |
|------------------|----------------|-------------------------|--------|
| Magic number `C2PATXT\0` | [Manifests_Text.adoc §Syntax](docs/c2pa/Manifests_Text.adoc) | `encypher.interop.c2pa.text_wrapper` | ✅ Compliant |
| Version = 1 | §Syntax | Implemented | ✅ Compliant |
| Byte-to-VS mapping (U+FE00-U+FE0F, U+E0100-U+E01EF) | §Byte-to-Variation-Selector | `text_wrapper.py` | ✅ Compliant |
| ZWNBSP (U+FEFF) prefix | §Placement Rules | Implemented | ✅ Compliant |
| Placement at end of visible text | §Placement Rules | Implemented | ✅ Compliant |
| NFC normalization before hashing | §Normalization | `text_hashing.py:46-49` | ✅ Compliant |
| `c2pa.hash.data` with `exclusions` field | §Content Binding | `unicode_metadata.py:864-870` | ✅ Compliant |
| Single contiguous wrapper block | §Placement Rules | Implemented | ✅ Compliant |
| JUMBF container inside wrapper | §Definition | Implemented | ✅ Compliant |

**Implementation Files:**
- `encypher-ai/encypher/interop/c2pa/text_wrapper.py`
- `encypher-ai/encypher/interop/c2pa/text_hashing.py`
- `encypher-ai/encypher/core/unicode_metadata.py`

---

## Trust Model

Encypher implements the **Private Credential Store** model per [C2PA §14.4.3](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_trust_lists).

| Concept | Spec Reference | Encypher Implementation |
|---------|----------------|-------------------------|
| Trust Anchor | §14.4 | Organization public keys stored in DB |
| Credential Lookup | §14.4.3 | `GET /api/v1/public/c2pa/trust-anchors/{signer_id}` |
| Signature Verification | §14.3 | Ed25519 signature verification |
| Signer Identity | §14.3.5 | `signer_id` extracted from manifest |

**Validation States (per §14.3):**
- **Well-Formed**: Manifest parses correctly ✅
- **Valid**: Signature verifies against known public key ✅
- **Trusted**: Requires C2PA Trust List (via SSL.com partnership) 🔧 Planned

---

## Assertions

Encypher supports the following C2PA assertion types:

| Assertion Label | Spec Reference | Purpose |
|-----------------|----------------|---------|
| `c2pa.created` | [§8.2](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#_c2pa_created) | Creation timestamp and source type |
| `c2pa.actions.v2` | [§8.3](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#_c2pa_actions_v2) | Action history |
| `c2pa.hash.data.v1` | [§8.4](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#_c2pa_hash_data_v1) | Content binding (hard binding) |
| `c2pa.soft_binding.v1` | [§8.5](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#_c2pa_soft_binding_v1) | Soft binding for watermarks (implemented: audio spread-spectrum via `audio-watermark-service`; video spread-spectrum via `video-watermark-service`; image TrustMark neural via `image-service`) |
| `c2pa.training-mining.v1` | [§8.6](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#_c2pa_training_mining_v1) | AI training/mining permissions |
| `c2pa.watermarked` | §8.3 (action) | Watermark embedding action |
| `c2pa.ingredient.v3` | [§9.8](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#_ingredients) | Provenance chain |
| `c2pa.metadata` | [§9.10](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#_metadata_assertion) | JSON-LD metadata |
| `com.encypher.rights.v1` | Custom | Document-level rights metadata |
| `com.encypher.rights.v2` | Custom | Segment-level rights (maps segment indices to rights profiles) |

**Composite multi-media manifests (`/sign/rich`):** The `/sign/rich` endpoint creates an article-level C2PA manifest that binds text, images, audio, and video under one `instance_id` with a deterministic `manifest_hash`. Each signed media item (image, audio, video) appears as a `c2pa.ingredient.v3` reference in the composite manifest; each ingredient carries its own fully-formed C2PA manifest and hard binding. This satisfies C2PA Section 9.8 (Ingredients) for multi-media provenance chains.

---

## Cryptographic Algorithms

| Algorithm | Spec Reference | Encypher Implementation |
|-----------|----------------|-------------------------|
| Ed25519 | [§15.2](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#_signature_algorithms) | Primary signing algorithm |
| SHA-256 | §15.3 | Content hashing |
| COSE Sign1 | [§15.4](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#_cose_sign1) | Signature container format |
| CBOR | §15.5 | Manifest serialization |

---

## Time Stamp Authority (TSA)

| Requirement | Spec Reference | Encypher Status |
|-------------|----------------|-----------------|
| RFC 3161 compliance | [§15.8](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#_time_stamp_authority) | 🔧 Planned (optional feature) |
| TSA Trust List | §14.4.2 | 🔧 Planned (DigiCert/SSL.com) |
| `sigTst2` COSE header | §15.8.2 | 🔧 Planned |

**Note:** TSA is strongly recommended but not required per C2PA spec. Encypher plans to offer TSA as an optional premium feature.

---

## API Endpoints

### Public C2PA Endpoints

| Endpoint | Purpose | Spec Alignment |
|----------|---------|----------------|
| `POST /api/v1/public/c2pa/validate-manifest` | Validate manifest structure | Non-cryptographic validation |
| `POST /api/v1/public/c2pa/create-manifest` | Create manifest from text | Manifest generation |
| `GET /api/v1/public/c2pa/trust-anchors/{signer_id}` | Lookup signer public key | Private Credential Store (§14.4.3) |
| `POST /api/v1/public/prebid/sign` | Auto-provenance signing for Prebid ad impressions (rate-limited) | Manifest generation for programmatic ad content |
| `GET /api/v1/public/prebid/status/{domain}` | Check Prebid signing status for a domain | Trust anchor lookup (§14.4.3) |
| `GET /api/v1/public/prebid/manifest/{record_id}` | Retrieve manifest for a signed Prebid record | Manifest retrieval |

### Authenticated Endpoints

| Endpoint | Purpose | Spec Alignment |
|----------|---------|----------------|
| `POST /api/v1/sign` | Sign text with C2PA manifest | Full C2PA embedding |
| `POST /api/v1/verify` | Verify C2PA manifest in text | §14.3 validation |
| `POST /api/v1/enterprise/audio/sign` | Sign audio with C2PA manifest (WAV, MP3, M4A) | Appendix A.3.4, A.3.7, A.5 |
| `POST /api/v1/enterprise/audio/verify` | Verify C2PA manifest in audio; returns `watermark_detected`, `watermark_payload`, `watermark_confidence` alongside C2PA results | §14.3 validation + §8.5 soft-binding |
| `POST /api/v1/enterprise/video/sign` | Sign video with C2PA manifest (MP4, MOV, M4V, AVI) | Appendix A.5, A.3 |
| `POST /api/v1/enterprise/video/verify` | Verify C2PA manifest in video; returns `watermark_detected`, `watermark_payload`, `watermark_confidence` alongside C2PA results | §14.3 validation + §8.5 soft-binding |
| `POST /api/v1/sign/rich` | Create composite multi-media manifest binding text + images + audio + video via `c2pa.ingredient.v3` | §9.8 Ingredients, composite manifest |
| `POST /api/v1/enterprise/video/stream/start` | Start live stream signing session | §19 (live video) |
| `POST /api/v1/enterprise/video/stream/{id}/segment` | Sign individual stream segment | §19 Method 1 |
| `POST /api/v1/enterprise/video/stream/{id}/finalize` | Finalize stream, compute Merkle root | §19 |

---

## Binary Media Embedding (c2pa-python)

Image and audio signing use `c2pa-python` (Python bindings for `c2pa-rs`) which handles container-specific JUMBF embedding internally. The library abstracts away the binary format details:

| Format | Container | C2PA Binding Mechanism | Spec Reference |
|--------|-----------|------------------------|----------------|
| JPEG | JFIF/Exif | APP11 marker segment | Appendix A.1 |
| PNG | PNG | `caBX` chunk | Appendix A.2 |
| WAV | RIFF | `C2PA` chunk | Appendix A.3.4 |
| MP3 | ID3v2 | GEOB frame (`application/x-c2pa-manifest-store`) | Appendix A.3.7 |
| M4A/AAC | ISO BMFF | `uuid` box (C2PA UUID) | Appendix A.5 |
| MP4/MOV/M4V | ISO BMFF | `uuid` box (C2PA UUID) | Appendix A.5 |
| AVI | RIFF | `C2PA` chunk | Appendix A.3 |

**Implementation files:**
- Shared signer: `enterprise_api/app/utils/c2pa_signer.py`
- Shared manifest builder: `enterprise_api/app/utils/c2pa_manifest.py`
- Shared verifier: `enterprise_api/app/utils/c2pa_verifier_core.py`
- Audio signing: `enterprise_api/app/services/audio_signing_service.py`
- Audio watermarking: `services/audio-watermark-service/app/services/spread_spectrum.py`
- Video watermarking: `services/video-watermark-service/` (port 8012, `encypher.spread_spectrum_video.v1`)
- Shared ECC: `services/shared/spread_spectrum_ecc.py` (RS(32,8) + rate-1/3 K=7 convolutional + soft Viterbi, method `rs32_8_conv_r3_k7`)
- Segment rights: `enterprise_api/app/services/segment_rights_utils.py`
- Video signing: `enterprise_api/app/services/video_signing_service.py`
- Video stream signing: `enterprise_api/app/services/video_stream_signing_service.py`
- Image signing: `enterprise_api/app/services/image_signing_service.py`

---

## Roadmap

| Feature | Status | Spec Reference |
|---------|--------|----------------|
| SSL.com C2PA certificates | Q1 2026 | C2PA Trust List integration |
| TSA integration | Q1 2026 | §15.8 |
| Image signing | Shipped (Feb 2026) | Appendix A.1-A.3 |
| Audio signing (WAV, MP3, M4A) | Shipped (Mar 2026) | Appendix A.3.4, A.3.7, A.5 |
| Audio soft-binding watermark (`c2pa.soft_binding.v1`) | Shipped (Apr 2026) | §8.5 |
| Video signing (MP4, MOV, M4V, AVI) | Shipped (Mar 2026) | Appendix A.5, A.3 |
| Video soft-binding watermark (`encypher.spread_spectrum_video.v1`) | Shipped (Apr 2026) | §8.5 |
| Live video stream signing | Shipped (Mar 2026) | Section 19 |
| PDF signing | Planned | Appendix A.4 |

---

## Compliance Audit Log

| Date | Auditor | Scope | Result |
|------|---------|-------|--------|
| Dec 2025 | TEAM_009 | Text manifest embedding | ✅ 100% compliant |
| Dec 2025 | TEAM_009 | NFC normalization | ✅ Verified |
| Dec 2025 | TEAM_009 | Exclusions field | ✅ Verified |
| Mar 2026 | TEAM_265 | Audio C2PA signing (WAV, MP3, M4A) | ✅ Implemented |
| Mar 2026 | TEAM_265 | Shared C2PA modules (signer, manifest, verifier) | ✅ Refactored |
| Mar 2026 | TEAM_266 | Video C2PA signing (MP4, MOV, M4V, AVI) | ✅ Implemented |
| Mar 2026 | TEAM_266 | Live video stream signing (C2PA 2.3 Section 19) | ✅ Implemented |
| Apr 2026 | TEAM_289 | Audio soft-binding watermark (`c2pa.soft_binding.v1`) | ✅ Implemented |
| Apr 2026 | TEAM_289 | Segment-level rights (`com.encypher.rights.v2`) | ✅ Implemented |
| Apr 2026 | TEAM_294 | Video soft-binding watermark (`encypher.spread_spectrum_video.v1`) | ✅ Implemented |
| Apr 2026 | TEAM_294 | Concatenated ECC for audio and video watermarks (`rs32_8_conv_r3_k7`) | ✅ Implemented |

---

## References

1. [C2PA Technical Specification 2.3](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html)
2. [C2PA Implementation Guidance 2.3](https://spec.c2pa.org/specifications/specifications/2.3/guidance/Guidance.html)
3. [C2PA Conformance Program](https://c2pa.org/conformance/)
4. [Content Authenticity Initiative](https://contentauthenticity.org/)
5. [RFC 3161 - Time-Stamp Protocol](https://www.ietf.org/rfc/rfc3161.txt)
