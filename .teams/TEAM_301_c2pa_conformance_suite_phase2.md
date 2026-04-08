# TEAM_301 - C2PA Conformance Suite Phase 2

## Session Start
- Date: 2026-04-07
- Agent: Opus
- Objective: Create comprehensive PRD for remaining conformance suite work, then implement all phases using parallel agent teams
- Prior session: TEAM_300 (extraction + parsing + evaluation layers, 171 tests, 112/112 real files)

## Context
- Conformance suite repo: /home/developer/code/c2pa-conformance-suite
- Knowledge graph repo: /home/developer/code/c2pa-knowledge-graph
- Starting state: 17 extractors, JUMBF/CBOR parser, manifest parser, predicate evaluator (40+ noop operators), test PKI, 171 tests passing
- Major gaps at start: crypto verification (48 rules), runtime operators (40+ noops), test vectors, ingredient resolver, c2pa-tool comparison

## Completed Work

### Phase 1: PRD Creation
- [x] Research: explored both repos exhaustively (codebase structure, predicates.json schema, validation-rules.json coverage)
- [x] Research: inventoried all 237 validation rules by phase
- [x] PRD written: 11 phases (12.0-22.0), ~100 WBS tasks, dependency graph, operator status table

### Phase 2: Implementation (3 parallel batches)

#### Batch 1 - Crypto Foundation (4 parallel agents)
- [x] COSE_Sign1 decoder (crypto/cose.py) - 24 tests
- [x] X.509 chain validator (crypto/x509_chain.py) - 37 tests
- [x] Trust anchor store (crypto/trust.py)
- [x] Content hashing + exclusions (crypto/hashing.py) - 32 tests
- [x] Data hash verifier (binding/data_hash.py)
- [x] 17 new operator implementations in engine.py - 63 tests

#### Batch 2 - Integration + Binding + Ingredients (4 parallel agents)
- [x] Crypto verifier orchestration (crypto/verifier.py) - 24 integration tests
- [x] CLI crypto pipeline wiring (cli.py steps 2.5, 2.75)
- [x] BMFF hash verifier + Merkle tree (binding/bmff_hash.py) - 21 tests
- [x] Boxes hash verifier (binding/boxes_hash.py)
- [x] Collection hash verifier (binding/collection_hash.py) - 24 tests
- [x] Text hash verifier + structured text (binding/text_hash.py)
- [x] Ingredient resolver (parser/ingredient.py) - 40 tests

#### Batch 3 - Builder + OCSP/TSA + Comparison (3 parallel agents)
- [x] COSE signer (builder/cose_signer.py) - ES256/384/512, PS256/384/512, Ed25519
- [x] JUMBF box builder (builder/jumbf_builder.py) - standard/XLBox, superbox, cbor/json
- [x] Manifest store builder (builder/manifest_builder.py) - full JUMBF manifest assembly
- [x] Builder tests (test_builder.py) - 46 tests, round-trip build->parse->verify
- [x] OCSP response parser (crypto/ocsp.py) - parse/check_revocation/validate_freshness
- [x] Timestamp decoder (crypto/timestamp.py) - parse_tst_header/validate/extract_gen_time
- [x] OCSP + Timestamp tests (test_ocsp_timestamp.py) - 35 tests
- [x] Comparison runner (compare/runner.py) - c2pa-tool executor
- [x] Normalizer (compare/normalizer.py) - status code classification
- [x] Diff engine (compare/diff.py) - agreement/divergence/suite_only/tool_only
- [x] Report generator (compare/report.py) - JSON + text
- [x] Comparison tests (test_compare.py) - 34 tests

#### Batch 4 - c2pa-tool Compatibility (single agent, continuation session)
- [x] Salted assertion box hashing (manifest_builder.py) - SHA256 over JUMD+content matches c2pa-rs calc_assertion_box_hash
- [x] JUMD salt support (jumbf_builder.py) - c2sh box, toggle 0x13, build_superbox_from_parts
- [x] COSE Sig_structure fix - empty external_aad, claim bytes as payload (matching c2pa-rs)
- [x] x5chain in protected header (C2PA v2, text label "x5chain")
- [x] Claim v2 pad field for c2pa.hash.data assertion
- [x] c2pa-tool integration tests (test_integration_c2patool.py) - 4 tests
- [x] Multi-manifest store tests (test_multi_manifest.py) - 5 tests

### Final Results
- **732 tests passing** (up from 171)
- **Lint clean** (ruff check)
- **All 47 operators LIVE** (up from 13)
- **All 7 binding types** implemented
- **Full crypto stack**: COSE decode -> signature verify -> chain validate -> trust evaluate -> OCSP -> timestamp
- **c2pa-tool validates our manifests**: claimSignature.validated, assertion.hashedURI.match, assertion.dataHash.match

## Architecture Decisions
1. Used cbor2 (not pycose) for COSE decoding - full control over detached payload pattern
2. ECDSA signature format: COSE raw r||s converted to DER for cryptography lib via encode_dss_signature
3. Trust anchor matching: subject + SubjectPublicKeyInfo bytes (not serial number)
4. DER scanning (tag 0x18) for GeneralizedTime extraction instead of full ASN.1 parsing
5. Comparison framework is c2pa-tool-optional (graceful degradation when not installed)

## Files Created (TEAM_301)

### Source
- `src/c2pa_conformance/crypto/cose.py`
- `src/c2pa_conformance/crypto/x509_chain.py`
- `src/c2pa_conformance/crypto/trust.py`
- `src/c2pa_conformance/crypto/hashing.py`
- `src/c2pa_conformance/crypto/verifier.py`
- `src/c2pa_conformance/crypto/ocsp.py`
- `src/c2pa_conformance/crypto/timestamp.py`
- `src/c2pa_conformance/binding/data_hash.py`
- `src/c2pa_conformance/binding/bmff_hash.py`
- `src/c2pa_conformance/binding/boxes_hash.py`
- `src/c2pa_conformance/binding/collection_hash.py`
- `src/c2pa_conformance/binding/text_hash.py`
- `src/c2pa_conformance/builder/cose_signer.py`
- `src/c2pa_conformance/builder/jumbf_builder.py`
- `src/c2pa_conformance/builder/manifest_builder.py`
- `src/c2pa_conformance/parser/ingredient.py`
- `src/c2pa_conformance/compare/runner.py`
- `src/c2pa_conformance/compare/normalizer.py`
- `src/c2pa_conformance/compare/diff.py`
- `src/c2pa_conformance/compare/report.py`

### Modified
- `src/c2pa_conformance/evaluator/engine.py` (all 47 operators LIVE)
- `src/c2pa_conformance/cli.py` (crypto pipeline, suite/compare/generate-vectors commands)

### Tests
- `tests/test_cose.py` (24)
- `tests/test_x509_chain.py` (37)
- `tests/test_hashing.py` (32)
- `tests/test_operators.py` (63)
- `tests/test_operators_advanced.py` (90)
- `tests/test_crypto_integration.py` (24)
- `tests/test_binding_bmff.py` (21)
- `tests/test_binding_collection.py` (24)
- `tests/test_ingredient.py` (40)
- `tests/test_ocsp_timestamp.py` (35)
- `tests/test_builder.py` (46)
- `tests/test_compare.py` (34)
- `tests/test_embedders.py` (17)
- `tests/test_vectors.py` (48)
- `tests/test_cli_commands.py` (15, 2 skip)

## Remaining Work (for next session)
1. **22.0 Knowledge Graph Expansion** - separate repo, 170 more predicates needed (increases rule coverage 67->237)

## Key Technical Decisions (Batch 4)

1. **Salted assertion hashing**: c2pa-rs computes assertion ref hashes as SHA256(JUMD_box_with_salt + CBOR_content_box), where a random 16-byte salt is embedded in the JUMD via a c2sh box (toggle byte 0x13). Without salt, SHA256(raw_cbor) matches c2pa-rs's `is_old_assertion()` check and triggers PrereleaseError. The salt is stored in the assertion JUMD, not in the claim CBOR.

2. **COSE Sig_structure**: C2PA uses detached payload format. The Sig_structure is `["Signature1", protected_bytes, b"", claim_cbor]` where external_aad is empty and the claim bytes are the payload. Our original implementation had these reversed.

3. **x5chain placement**: C2PA v2 requires x5chain in the protected header. c2pa-rs only checks the unprotected header for the text label "x5chain" (not integer 33), so placing x5chain in the protected header with text label is the correct approach.

4. **Claim v2 format**: Uses `claim_generator_info` (dict, not list), `created_assertions` (not `assertions`), relative JUMBF URIs, top-level `alg`, `instanceID`, label `c2pa.claim.v2`.

## Files Created/Modified (Batch 4)

### Created
- `src/c2pa_conformance/builder/two_pass.py` - Two-pass signing
- `tests/test_two_pass.py` - 24 tests
- `tests/test_multi_manifest.py` - 5 tests
- `tests/test_integration_c2patool.py` - 4 tests

### Modified
- `src/c2pa_conformance/builder/jumbf_builder.py` - salt support, c2sh box, build_superbox_from_parts
- `src/c2pa_conformance/builder/manifest_builder.py` - salted assertion hashing, ManifestSpec, build_multi_manifest_store, claim v2 format
- `src/c2pa_conformance/builder/cose_signer.py` - x5chain in protected header, correct Sig_structure format
- `src/c2pa_conformance/crypto/cose.py` - x5chain from protected/unprotected headers, correct Sig_structure
- `src/c2pa_conformance/parser/jumbf.py` - corrected all C2PA type UUIDs, toggle byte 0x03
- `src/c2pa_conformance/parser/manifest.py` - claim v2 property support (claim_generator_info, assertion_refs)
- `src/c2pa_conformance/vectors/definitions.py` - content_bound, ingredient_chain fields
- `src/c2pa_conformance/vectors/generator.py` - content-bound and ingredient vector generation
- `tests/test_builder.py` - updated for protected header x5chain
- `tests/test_cose.py` - updated for protected header x5chain, correct Sig_structure
- `tests/test_crypto_integration.py` - updated for protected header x5chain, correct Sig_structure
- `tests/test_vectors.py` - updated definition count and categories

## Suggested Commit Message

```
feat(conformance): c2pa-tool compatible manifests, two-pass signing, ingredients

Complete the C2PA conformance test suite with full c2pa-tool compatibility.
Test count: 171 -> 732 (all passing, lint clean). c2pa-tool validates our
manifests: claimSignature.validated, assertion.hashedURI.match, assertion.dataHash.match.

c2pa-tool compatibility fixes:
- Salted assertion box hashing (SHA256 over JUMD+content, c2sh salt box)
- Correct COSE Sig_structure (empty external_aad, claim as payload)
- x5chain in protected header with text label (C2PA v2)
- Claim v2 format (claim_generator_info, created_assertions, relative URIs)
- All C2PA type UUIDs corrected to match spec/c2pa-rs
- c2pa.hash.data pad field for DataHash deserialization

New capabilities:
- Two-pass signing (build_bound_manifest) for content-bound manifests
- Multi-manifest store builder for ingredient chains
- JPEG/PNG container embedding with correct exclusion ranges
- 4 c2pa-tool integration tests verifying end-to-end compatibility
```
