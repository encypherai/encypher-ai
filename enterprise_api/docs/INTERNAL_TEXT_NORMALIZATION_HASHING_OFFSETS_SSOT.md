# INTERNAL — Text Normalization, Hashing, and Offset Semantics (SSOT)

## Status
Internal-only SSOT for `enterprise_api`. Do not copy into public OpenAPI descriptions.

## Scope
This document defines authoritative engineering semantics for:
- Text normalization
- Integrity hashing inputs
- Offset semantics used for signing/verification and API responses

## Normalization (Text)
- All text that participates in signing, verification, or integrity hashing MUST be normalized using Unicode **NFC**.
- Normalization is applied **before** converting to bytes.

## Byte Encoding
- All byte-level operations MUST use UTF-8.

## Integrity Hashing (SSOT)
- **Integrity hashes are computed over:** `utf-8` bytes of **NFC-normalized** text.
- **Case sensitivity:** Integrity hashing is **case-sensitive**. No lowercasing/case-folding is applied.

### Implemented locations
- Merkle leaf hashes:
  - `enterprise_api/app/utils/merkle/hashing.py::compute_leaf_hash`
- `/sign` hashes:
  - `enterprise_api/app/utils/sentence_parser.py::compute_text_hash`
  - `enterprise_api/app/utils/sentence_parser.py::compute_sentence_hash`

## Offset Semantics (SSOT)

### General rule
- Any offset/span that is used for C2PA hard-binding, wrapper exclusion ranges, or “what exactly was signed” MUST be interpreted as **UTF-8 byte offsets** into **NFC-normalized** text.

### API response fields
- Multi-embedding verification surfaces `text_span` fields.
- `text_span` represents a half-open range `(start, end)` of **UTF-8 byte offsets**.

### Character indices vs byte offsets
- Some internal utilities may use Python character indices for UI slicing or convenience; these MUST NOT be reused as byte offsets.

## Notes
- Public API documentation should describe `text_span` as byte offsets (UTF-8) without exposing internal normalization/hard-binding rules.
