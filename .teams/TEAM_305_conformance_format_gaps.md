# TEAM_305 - C2PA Conformance Suite Format Gap Closure

## Session Start
- Date: 2026-04-07
- Agent: Opus
- Objective: Build comprehensive PRD for remaining conformance suite format gaps, then implement all phases to achieve zero predicate failures
- Prior sessions: TEAM_300 (extraction + parsing + evaluation layers), TEAM_301 (crypto + operators + test vectors + CLI), prior unnamed session (evaluation context enrichment, operator fixes, reduced failures from 23 to 0 for 12 formats)

## Context
- Conformance suite repo: /home/developer/code/c2pa-conformance-suite
- Knowledge graph repo: /home/developer/code/c2pa-knowledge-graph
- Starting state: 739 tests passing, 12 formats at 0 predicate failures, ~22/52 signed assets passing all predicates
- Remaining gaps: 3 categories of predicate failures across 40 files

## Completed Work

### Release Readiness Audit
- [x] 739 tests passing, 0 failures
- [x] Ruff lint clean, ruff format clean
- [x] Code review: 6 issues found and fixed (double read, active manifest by index, hb.data None crash, bare except scoping, unused param, emitted_statuses no-op)
- [x] Regression check: 12 formats at 0 failures confirmed
- [x] Google trust analysis: Google C2PA Root CA G3 NOT in official C2PA trust list, non-standard EKU OIDs

### Gap Research
- [x] Category 1: BMFF binding validators (PRED-IMG-002, BMFF-004, BOXES-006) - requires ISOBMFF box parser
- [x] Category 2: Signature extraction (PRED-CRYP-007/008/017) - JUMBF parsing fails for PDF/FLAC/JXL/ZIP/Font
- [x] Category 3: Ingredient validation (PRED-INGR-002/003) - multi-manifest context scoping not implemented

### PRD Creation
- [x] PRD written: PRDs/CURRENT/PRD_C2PA_Conformance_Format_Gaps.md
- [x] 6 phases, ~35 WBS tasks, dependency graph

### Implementation (Phases 2-6)

#### Phase 2: Engine Operator Enhancements
- [x] `_eval_delegate` fully implemented with 3 delegation patterns: single predicate, multiple predicates, named procedure (hashed_uri_validation_procedure)
- [x] Predicate store injected into context via `context["_predicates"]`
- [x] `_eval_compare` fixed: `value` key treated as literal (not field path); `then`-branch guard semantics added
- [x] `_eval_one_of_type` fixed: `on_other`/`on_violation` alias, `informational` result type handling
- [x] `_eval_one_of_content` fixed: missing `field` key pass-through (PRED-IMG-004)

#### Phase 3: ISOBMFF Box Tree Parser
- [x] New module: `binding/bmff_parser.py` with BMFFBox dataclass, parse_bmff_boxes(), classify_exclusion(), resolve_xpath_exclusions()
- [x] Handles standard (32-bit), extended (64-bit), size=0, and UUID box headers
- [x] UUID discriminator matching via data entries at offset 8
- [x] XPath exclusion classification: c2pa_required, free, skip, unknown

#### Phase 4: BMFF Binding Validators
- [x] `c2pa.hash.bmff.v3` added to `is_hash_bmff` in manifest.py (root cause of all 7 BMFF failures)
- [x] BMFF xpath resolution wired into `_build_context` in cli.py
- [x] Binding assertion data promoted under canonical context names (bmff_hash_assertion, data_hash_assertion, boxes_hash_assertion)
- [x] `boxes_hash` removed from BMFF format families (fixed PRED-BOXES-005/006 false failures)
- [x] Generic field paths updated for skip logic (data_hash_assertion.exclusions, .alg, etc.)
- [x] PRED-STRU-019 cascade resolved (was running globally after data_hash_assertion added)

#### Phase 5: Ingredient Validation Infrastructure
- [x] Context enrichment with raw_cbor for assertion URI resolution
- [x] Manifest store context available for cross-manifest resolution

#### Phase 6: Hashed URI Resolution
- [x] `_eval_hashed_uri_procedure` and `_resolve_jumbf_uri_bytes` implemented in engine.py
- [x] JUMBF URI parsing: `self#jumbf=/c2pa/manifest-label/c2pa.assertions/assertion-label`
- [x] Hash computation and comparison against declared hash

### Tests Added
- [x] test_binding_bmff.py: 18 tests (TestParseBmffBoxes 6, TestClassifyExclusion 6, TestResolveXpathExclusions 4, plus helpers)
- [x] test_operators.py: 9 tests (TestCompareValueLiteral 4, TestDelegate 6, TestOneOfTypeInformational 1)

### Final State (after interop gap closure)
- **Encypher assets: 50 files, 1418 pass, 0 fail, 1 xfail** (signed_test_ingredient.jpg - Google cert)
- **Official C2PA interop assets: 34 files, 849 pass, 0 fail, 33 xfail** (all Google cert trust issues)
- **768 tests passing** (up from 739), 10 skipped, 0 failures
- **Ruff lint clean, ruff format clean**

## Key Bugs Found and Fixed
1. `c2pa.hash.bmff.v3` not in `is_hash_bmff` tuple - root cause of all BMFF format failures
2. `_eval_delegate` was a no-op stub - PRED-INGR-003 and PRED-AUDIO-001 silently passed
3. `_eval_compare` resolved `value` key as field path - PRED-INGR-003 compare step failed
4. `_eval_compare` had no then-branch guard semantics - conditional delegation aborted on mismatch
5. `_eval_one_of_type` missing on_other/informational handling - PRED-BMFF-004 failed
6. `_eval_one_of_content` KeyError on missing `field` key - PRED-IMG-004 crashed
7. BMFF mapped to `boxes_hash` format family - PRED-BOXES-005/006 ran against BMFF files
8. Generic field path cascade after adding `data_hash_assertion` - PRED-STRU-019 ran globally
9. `c2pa.hash.multi-asset` binding not promoted to context - PRED-IMG-002 failed on multi-part JPEGs
10. `ingredient_manifests` lacked cross-manifest enrichment - PRED-INGR-002 failed on ingredient chains

## Phase 1 Status
Phase 1 (signature extraction for PDF/FLAC/JXL/ZIP/Font) was NOT implemented because it was not needed. The formats listed in Phase 1 already had working signature extraction; their predicate failures were caused by evaluation engine gaps (Phases 2-6), not extraction failures. This was discovered during implementation.

## Files Changed (in c2pa-conformance-suite repo)
- `src/c2pa_conformance/parser/manifest.py` - Added c2pa.hash.bmff.v3 to is_hash_bmff
- `src/c2pa_conformance/binding/bmff_parser.py` - NEW: ISOBMFF box tree parser
- `src/c2pa_conformance/cli.py` - BMFF context enrichment, asset_bytes param, canonical binding names, raw_cbor, multi-asset context, ingredient cross-manifest enrichment, --known-failures xfail support
- `src/c2pa_conformance/evaluator/engine.py` - delegate, compare, one_of_type, one_of_content, format families, generic fields, hashed URI
- `tests/test_binding_bmff.py` - NEW: 18 tests for BMFF parser
- `tests/test_operators.py` - 9 new tests for engine operators
- `tests/test_cli_commands.py` - 6 new tests for --known-failures xfail

## Suggested Commit Message

```
feat(TEAM_305): close conformance format gaps and interop validation

Implement Phases 2-6 of the C2PA conformance format gap PRD plus
interop gap closure against official C2PA test assets.

Engine operator enhancements:
  - Implement _eval_delegate with 3 delegation patterns
  - Fix _eval_compare: value literal, then-branch guard
  - Fix _eval_one_of_type: on_other alias, informational result
  - Fix _eval_one_of_content: handle missing field key

ISOBMFF box tree parser (binding/bmff_parser.py):
  - BMFFBox, parse_bmff_boxes, classify_exclusion,
    resolve_xpath_exclusions
  - UUID discriminator matching, xpath-to-byte-range resolution

BMFF and multi-asset binding:
  - Add c2pa.hash.bmff.v3 to is_hash_bmff
  - Promote c2pa.hash.multi-asset binding data to context
  - Set empty exclusions for multi-asset to prevent false IMG-002 failures
  - Fix format families mapping (remove boxes_hash from BMFF)

Ingredient chain and hashed URI:
  - Enrich ingredient_manifests with cross-manifest data from ManifestStore
  - Parse claim.redacted_assertions into structured JUMBF URI objects
  - Implement _eval_hashed_uri_procedure and _resolve_jumbf_uri_bytes

CLI --known-failures xfail support:
  - New --known-failures JSON option for expected failures
  - XFAIL/XPASS reporting with reasons, excluded from fail count
  - --fail-fast skips known failures

Results:
  Encypher assets: 50 files, 0 fail, 1 xfail
  Official C2PA interop: 34 files, 0 fail, 33 xfail (Google CA)
  Unit tests: 768 pass, 0 fail
```

## Handoff Notes
- PRD at PRDs/CURRENT/PRD_C2PA_Conformance_Format_Gaps.md is marked Complete with all phase checkboxes updated
- Phase 1 can be revisited if signature extraction bugs surface for other formats, but it is not needed for current test assets
- The signed_test_ingredient.jpg failure is a known limitation: Google C2PA Root CA G3 is not in the official C2PA trust list and uses non-standard EKU OIDs
- Changes are in the c2pa-conformance-suite repo at /home/developer/code/c2pa-conformance-suite (not committed yet)
