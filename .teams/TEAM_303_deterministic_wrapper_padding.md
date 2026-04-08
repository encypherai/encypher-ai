# TEAM_303 - Deterministic C2PA Text Wrapper Padding

## Status: COMPLETE

## Objective

Eliminate the hash-binding exclusion-length approximation gap in C2PA text manifests by implementing deterministic wrapper padding. The old approach used an approximate exclusion length because the UTF-8 byte length of VS-encoded bytes varies (3 bytes for 0x00-0x0F, 4 bytes for 0x10-0xFF). Changing the hash changes the byte distribution, which changes the wrapper length, creating a circular dependency.

## Solution: Worst-Case Padding with +6 Margin

Formula: `E_target = 3 + (13 + M) * 4 + 6` where M = manifest byte count.

The +6 margin guarantees the gap between target and actual is always expressible as `3a + 4b` for non-negative integers a, b. Without it, gaps of 1, 2, or 5 would be non-representable for some manifests.

1. Compute `E_target` from manifest byte count (deterministic)
2. Set exclusion length = E_target in hard binding assertion
3. Iterate up to 3 times for CBOR integer width convergence
4. VS-encode the wrapper normally
5. Pad with additional VS characters (0x00 for 3-byte, 0xFF for 4-byte) to reach E_target
6. Decoder accepts `len(raw) >= header_size + manifestLength` (ignores trailing padding)

## Test Results

- c2pa-text Python API: 32/32 passed (11 new padding tests)
- encypher-ai SDK: 161 passed, 7 skipped, 16 xfailed (23 conformance tests, 2 new padding tests)
- enterprise_api C2PA tests: 1/1 passed

## Files Modified

| File | Action |
|------|--------|
| specs-core: `Manifests_Text.adoc` | Add deterministic padding section (local branch `feat/deterministic-text-wrapper-padding`) |
| c2pa-text: `python/src/c2pa_text/__init__.py` | Add `worst_case_wrapper_byte_length`, `encode_wrapper_padded`, `_compute_padding` |
| c2pa-text: `python/tests/test_deterministic_padding.py` | New: 11 tests for padding |
| c2pa-text: `rust/src/lib.rs` | Add `worst_case_wrapper_byte_length`, `encode_wrapper_padded`, `compute_padding` |
| c2pa-text: `typescript/src/index.ts` | Add `worstCaseWrapperByteLength`, `encodeWrapperPadded`, `computePadding` |
| c2pa-text: `go/c2pa_text/c2pa_text.go` | Add `WorstCaseWrapperByteLength`, `EncodeWrapperPadded`, `computePadding` |
| encypher-ai: `interop/c2pa/text_wrapper.py` | Add `encode_wrapper_padded`, `worst_case_wrapper_byte_length`; fix decoder `!=` to `<` |
| encypher-ai: `core/unicode_metadata.py` | Replace approximate exclusion length with deterministic worst-case iteration |
| encypher-ai: `tests/integration/test_c2pa_jumbf_conformance.py` | Add 2 tests: `test_exclusion_length_matches_actual_wrapper_byte_length`, `test_exclusion_length_deterministic_across_content` |
| encypher-ai: `pyproject.toml` | Add `[tool.uv.sources]` for local c2pa-text dev dependency |

## Key Decisions

- Formula: `3 + (13 + M) * 4 + 6` (not `3 + (13 + M) * 4`)
- The +6 margin eliminates all non-representable gap values ({1, 2, 5}) since gap = N_low + 6 >= 6
- Padding uses 0x00 for 3-byte VS chars, 0xFF for 4-byte VS chars, solving `3a + 4b = gap`
- Backward compat: encypher-ai decoder changed from `!=` to `<` to accept padding; c2pa-text decoders already used `>=`
- No version bump: manifestLength tells decoder where manifest ends, padding bytes are ignored
- Overhead: 6 extra bytes per wrapper (~0.3% for typical manifests)

## Suggested Commit Message

```
feat(c2pa-text): add deterministic wrapper padding for exact exclusion lengths

Implement worst-case padding algorithm (E = 3 + (13 + M) * 4 + 6) that
eliminates the hash-avalanche circularity in C2PA text manifest exclusion
lengths. The wrapper is padded with additional VS characters to match the
declared exclusion length exactly.

Changes across all four c2pa-text implementations (Python, Rust, TypeScript,
Go), the encypher-ai SDK embed path, and the C2PA spec draft language.

Refs: TEAM_303
```
