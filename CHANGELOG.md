# Changelog

## 3.2.1 (2026-05-02)

### Fixed
- Pass `product_version` through to `claim_generator_info.version` in CBOR
  claim when provided by callers.
- SDK test suite: updated claim builder tests to reflect the parameterized
  API contract for `spec_version` and `product_version`.

## 3.2.0 (2026-05-02)

### Changed
- `embed_metadata()` accepts new optional parameters `spec_version` and
  `product_version`. Callers (e.g. the enterprise API) pass C2PA policy
  constants rather than the SDK hardcoding them. When omitted,
  `claim_generator_info` includes only the `name` field.
- C2PA actions now use the spec-required `"action"` key instead of
  `"label"`. The SDK normalizes incoming actions that use the legacy
  `"label"` key for backward compatibility.
- The auto-generated watermark action changed from the deprecated
  `c2pa.watermarked` to `c2pa.watermarked.bound` (C2PA spec 2.4).
- `build_claim_cbor()` accepts `spec_version` and `product_version` as
  optional keyword arguments. Removed hardcoded `_PRODUCT_NAME`,
  `_PRODUCT_VERSION`, and `_SPEC_VERSION` constants.

### Fixed
- C2PA spec 2.4 rubric conformance: `specVersion` now appears in
  `claim_generator_info` when `spec_version` is provided, satisfying the
  `mandatory_spec_version` rubric trait.
- C2PA spec 2.4 rubric conformance: `no_deprecated_actions` trait now
  passes because `c2pa.watermarked` is replaced by
  `c2pa.watermarked.bound`.

## 3.1.6 (2026-04-28)

- Hard binding HTML-stripping fallback for text verification.

## 3.1.5 (2026-04-27)

- C2PA A.7 soft-binding verification support.

## 3.1.4 (2026-04-26)

- Spec-correct `c2pa.soft-binding` assertion label.

## 3.1.3 (2026-04-25)

- COSE ECDSA raw R||S format for cross-verifier compatibility.
- CBOR tag 18 unwrapping in COSE_Sign1 parsing.
- Detached-payload COSE_Sign1 x5chain extraction.
