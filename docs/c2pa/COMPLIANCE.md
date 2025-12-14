# Encypher C2PA Compliance Reference

This document maps Encypher's implementation to the C2PA Technical Specification 2.2.

## Quick Links to C2PA Specification

- [C2PA Specification 2.2](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html)
- [C2PA Implementation Guidance](https://spec.c2pa.org/specifications/specifications/2.2/guidance/Guidance.html)
- [C2PA Security Considerations](https://spec.c2pa.org/specifications/specifications/2.0/security/Security_Considerations.html)
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
| `c2pa.created` | [§8.2](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_c2pa_created) | Creation timestamp and source type |
| `c2pa.actions.v1` | [§8.3](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_c2pa_actions_v1) | Action history |
| `c2pa.hash.data.v1` | [§8.4](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_c2pa_hash_data_v1) | Content binding (hard binding) |
| `c2pa.soft_binding.v1` | [§8.5](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_c2pa_soft_binding_v1) | Soft binding for watermarks |
| `c2pa.training-mining.v1` | [§8.6](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_c2pa_training_mining_v1) | AI training/mining permissions |
| `c2pa.watermarked` | §8.3 (action) | Watermark embedding action |

---

## Cryptographic Algorithms

| Algorithm | Spec Reference | Encypher Implementation |
|-----------|----------------|-------------------------|
| Ed25519 | [§15.2](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_signature_algorithms) | Primary signing algorithm |
| SHA-256 | §15.3 | Content hashing |
| COSE Sign1 | [§15.4](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_cose_sign1) | Signature container format |
| CBOR | §15.5 | Manifest serialization |

---

## Time Stamp Authority (TSA)

| Requirement | Spec Reference | Encypher Status |
|-------------|----------------|-----------------|
| RFC 3161 compliance | [§15.8](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_time_stamp_authority) | 🔧 Planned (optional feature) |
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

### Authenticated Endpoints

| Endpoint | Purpose | Spec Alignment |
|----------|---------|----------------|
| `POST /api/v1/sign` | Sign text with C2PA manifest | Full C2PA embedding |
| `POST /api/v1/verify` | Verify C2PA manifest in text | §14.3 validation |

---

## Future Roadmap

| Feature | Target | Spec Reference |
|---------|--------|----------------|
| SSL.com C2PA certificates | Q1 2026 | C2PA Trust List integration |
| TSA integration | Q1 2026 | §15.8 |
| PDF signing | Q2 2026 | Appendix A.4 |
| Image signing | Q3 2026 | Appendix A.1-A.3 |

---

## Compliance Audit Log

| Date | Auditor | Scope | Result |
|------|---------|-------|--------|
| Dec 2025 | TEAM_009 | Text manifest embedding | ✅ 100% compliant |
| Dec 2025 | TEAM_009 | NFC normalization | ✅ Verified |
| Dec 2025 | TEAM_009 | Exclusions field | ✅ Verified |

---

## References

1. [C2PA Technical Specification 2.2](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html)
2. [C2PA Implementation Guidance 2.2](https://spec.c2pa.org/specifications/specifications/2.2/guidance/Guidance.html)
3. [C2PA Conformance Program](https://c2pa.org/conformance/)
4. [Content Authenticity Initiative](https://contentauthenticity.org/)
5. [RFC 3161 - Time-Stamp Protocol](https://www.ietf.org/rfc/rfc3161.txt)
