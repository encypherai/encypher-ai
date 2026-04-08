# TEAM_302 - C2PA Text JUMBF Conformance Fix

## Session Start
- Date: 2026-04-07
- Agent: Opus
- Objective: Fix the text signing pipeline in the AGPL encypher-ai SDK to produce conformant JUMBF manifest stores instead of a proprietary JSON envelope.

## Context
- TEAM_300 identified the conformance issue: text signing produces `{"cbor_payload":"...","cose_sign1":"...","format":"c2pa","signer_id":"..."}` in a fake jumb box instead of proper JUMBF box hierarchy
- The enterprise API already has a conformant JUMBF builder at `enterprise_api/app/utils/jumbf.py`
- The c2pa-text foundational library (VS encoding/decoding) is correct
- The fix is in the AGPL SDK (`encypher-ai/`), not the enterprise API
- Strategy analysis confirms: reference implementation must ship conformant output

## Plan
See /home/developer/.claude/plans/clever-juggling-dove.md

## Progress
- [x] Phase 1: New SDK modules (JUMBF builder/parser, claim v2 builder, exports)
- [x] Phase 2: Rewrite embed path - single-pass JUMBF manifest store construction
- [x] Phase 3: Update verify path with dual-format detection (JUMBF + legacy JSON)
- [x] Phase 4: Deprecate old serialize/deserialize_jumbf_payload
- [x] Phase 5: Update downstream consumers (enterprise_api, verification-service)
- [x] Phase 6: Tests (31 unit + 21 conformance integration + existing tests updated)

## Key Decisions

### VS Encoding Non-Determinism (Convergence Loop Removal)
The original convergence loop oscillated because VS encoding maps different byte values to different UTF-8 lengths (3 or 4 bytes). Old JSON format was ASCII (deterministic), new JUMBF has raw binary (non-deterministic). Hash avalanche prevents any fixed-point solution.

**Solution:** Remove convergence loop. Hard binding assertion stores approximate exclusion length. Verifier uses measured wrapper byte range from `find_wrapper_info_bytes()`. Start offset is exact (used for segment extraction in page-chrome scenarios). This decouples hash computation (measured) from segment extraction (assertion's start).

### com.encypher.signer + com.encypher.context Assertions
Signer ID and C2PA context URL are stored as dedicated assertions in the JUMBF manifest store (replacing the JSON envelope fields). This maintains backward compatibility with the verification interface.

### claim_label Field
The extracted `claim_label` is set to the literal `"c2pa.claim.v2"` (the claim version identifier), not the manifest's JUMBF URN label. This matches the semantic expectation of downstream consumers.

## Files Modified

| File | Action |
|------|--------|
| `encypher-ai/encypher/interop/c2pa/jumbf.py` | **New** - ISO 19566-5 JUMBF builder/parser |
| `encypher-ai/encypher/interop/c2pa/c2pa_claim.py` | **New** - C2PA claim v2 builder |
| `encypher-ai/encypher/interop/c2pa/__init__.py` | Updated exports |
| `encypher-ai/encypher/core/unicode_metadata.py` | Rewrote embed + updated verify + extract |
| `encypher-ai/encypher/core/payloads.py` | Deprecated serialize/deserialize_jumbf_payload |
| `enterprise_api/app/services/verification_logic.py` | Dual-format COSE extraction |
| `services/verification-service/app/api/v1/endpoints.py` | Dual-format via _extract_cose_and_signer_from_manifest |
| `enterprise_api/tests/test_c2pa_text_exclusions_byte_offsets.py` | Updated for JUMBF format |
| `encypher-ai/tests/interop/test_jumbf.py` | **New** - 19 JUMBF unit tests |
| `encypher-ai/tests/interop/test_c2pa_claim.py` | **New** - 12 claim builder tests |
| `encypher-ai/tests/integration/test_c2pa_jumbf_conformance.py` | **New** - 21 conformance integration tests |
| `encypher-ai/tests/integration/test_c2pa.py` | Updated label checks |
| `encypher-ai/tests/integration/test_c2pa_text_embedding.py` | Updated label + exclusion checks |

## Test Results
- SDK: 159 passed, 7 skipped, 16 xfailed
- Enterprise API (C2PA-related): 306 passed, 4 skipped
- Lint: ruff check clean, ruff format applied

## Suggested Commit Message

```
feat(sdk): produce conformant C2PA JUMBF manifest stores for text signing

The text signing pipeline previously produced a proprietary JSON envelope
inside a bare jumb box, which did not conform to the C2PA manifest store
structure specified in ISO 19566-5.

This commit rewrites the embed path to produce a proper JUMBF box
hierarchy: manifest store -> manifest -> {assertion store, claim v2,
COSE_Sign1 signature}. The verify path uses dual-format detection
(conformant JUMBF first, legacy JSON fallback) for backward
compatibility.

Key changes:
- New SDK modules: jumbf.py (builder/parser), c2pa_claim.py (claim v2)
- Single-pass embed (no convergence loop; approximate exclusion length
  in assertion, verifier uses measured wrapper byte range)
- Dual-format detection in SDK, enterprise API, and verification service
- Deprecated serialize/deserialize_jumbf_payload in payloads.py
- 52 new tests (19 JUMBF unit + 12 claim unit + 21 conformance integration)

Closes conformance issue identified by TEAM_300.
```
