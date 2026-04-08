# TEAM_304 - C2PA Knowledge Graph Full Predicate Expansion

## Session Start
- Date: 2026-04-07
- Agent: Opus
- Objective: Expand predicates.json from 45 predicates (67/237 rules) to full coverage of all 237 v2.4 validation rules
- Repo: /home/developer/code/c2pa-knowledge-graph

## Context
- Current: 45 predicates covering 67 rules (28.3% coverage)
- Target: ~200+ predicates covering all 237 rules (100% coverage)
- Uncovered phases: trust (2), timestamp (8), ingredient (15), content (11 of 17), structural (26 of 37), cryptographic (40), assertion (68 of 118)

## Plan
Work smallest phases first, validate with test suite after each batch:
1. Trust (2 rules) - DONE
2. Timestamp (8 rules) - DONE
3. Ingredient (15 rules) - DONE
4. Content (11 remaining rules) - DONE
5. Structural (26 remaining rules) - DONE
6. Cryptographic (40 rules) - DONE
7. Assertion (68 remaining rules) - DONE

## Completed Work

### Predicate Generation (4 parallel agents)
- [x] Batch 1: Trust + Timestamp + Ingredient (25 rules -> 13 predicates)
  - PRED-TRUS-001: claim signature validity window
  - PRED-TIME-001 through PRED-TIME-004: timestamp lookup, mapping, well-formedness, ingredient ignoring
  - PRED-INGR-001 through PRED-INGR-008: attribution warnings, redacted assertions, hashed URIs, recursive validation, hard binding, BMFF hash
- [x] Batch 2: Structural (26 rules -> 19 predicates)
  - PRED-STRU-001 through PRED-STRU-019: custom status codes, multiple stores, manifest location, claim fields, icon validation, OCSP chain (signer/CA/online), revocation, segment lengths
- [x] Batch 3: Cryptographic (40 rules -> 25 predicates)
  - PRED-CRYP-001 through PRED-CRYP-025: validation results format, signature URI resolution, credential validation, algorithm checks, trust chain, sigTst/sigTst2 timestamp, OCSP decoding, iat header, session keys
- [x] Batch 4: Assertion + Content (79 rules -> 43 predicates)
  - PRED-ASSE-001 through PRED-ASSE-029: ingredient validation, hashedURI, redaction, assertion label validation, alternative content representation, external data, ingredient fields, hard binding, multi-asset fallback
  - PRED-ABMF-001 through PRED-ABMF-004: BMFF hash match/fallback, merkle tree, auxiliary boxes
  - PRED-ABOX-001 through PRED-ABOX-006: boxes hash validation, exclusion ranges, multi-asset fallback
  - PRED-AMLT-001 through PRED-AMLT-004: multi-asset iteration, locator validation, hash verification
  - PRED-CONT-001 through PRED-CONT-007: multi-part content, playback validation, pad field ignoring, box hash algorithm, hash processing

### Merge and Validation
- [x] Status code corrections (16 codes fixed to match metadata.json)
- [x] All 22 predicate tests passing
- [x] All 172 repo tests passing

### Final Results
- **145 predicates** (up from 45)
- **237/237 rules formalized** (100%, up from 67/237 = 28.3%)
- **100% test vector coverage** (all predicates have passing and failing vectors)
- Format family additions: video_bmff +4, boxes_hash +6, multi_asset +4
- Cross-cutting additions: +86 predicates (from 6 to 92)

## Architecture Decisions
1. Phase-specific predicates (trust, timestamp, ingredient, structural, cryptographic) placed in cross_cutting since they are format-agnostic
2. Format-specific assertion rules placed in existing format families (video_bmff, boxes_hash, multi_asset)
3. Predicate ID prefixes by phase: PRED-TRUS, PRED-TIME, PRED-INGR, PRED-STRU, PRED-CRYP, PRED-ASSE, PRED-ABMF, PRED-ABOX, PRED-AMLT, PRED-CONT
4. Related rules grouped into single predicates where they form complementary halves (e.g., success/failure pairs)

## Suggested Commit Message

```
data(v2.4): expand predicates.json to 100% rule coverage (237/237)

Add 100 new conformance predicates covering all previously uncovered
C2PA v2.4 validation rules. Coverage increases from 28.3% (67/237) to
100% (237/237).

New predicate phases:
- Trust (1 predicate, 2 rules): certificate validity window
- Timestamp (4 predicates, 8 rules): TST lookup, mapping, well-formedness
- Ingredient (8 predicates, 15 rules): recursive validation, redaction, hard binding
- Structural (19 predicates, 26 rules): manifest store, claim fields, OCSP chain
- Cryptographic (25 predicates, 40 rules): signature, trust chain, timestamps, OCSP
- Assertion (29 predicates, 68 rules): hashedURI, alternative content, ingredients
- Content (7 predicates, 11 rules): multi-part, playback, pad fields, box hash alg
- Format-specific (14 predicates): BMFF hash, boxes hash, multi-asset hash

All 172 tests passing. All 145 predicates have test vectors with passing
and failing cases. Status codes validated against KG metadata.
```

## Phase 2: v1 Release Prep and Interoperability

### Interoperability Audit Findings
- 22 of 73 unique ops in predicates.json were NOT implemented in conformance suite engine.py (silent pass-through)
- No sync mechanism between repos (broken default CLI path)
- Zero integration tests loading real KG predicates
- KG repo still at v0.1.0/Alpha with no CI

### Fixes Applied

#### Conformance Suite (c2pa-conformance-suite)
- [x] Implemented 22 missing operators in engine.py (check_status, compare, conditional, validate_structure, validate_format, check_revocation, validate_certificate, verify_signature, validate_timestamp, is_array, sum_field, regex_match, one_of_exclusive, any_of, traverse, resolve_reference, resolve_uri, check_location, find_certificate, count_manifest_stores, fetch_remote_manifest, collect_ocsp_responses)
- [x] Engine now handles 72 operators (was 50), 100% of ops in predicates.json
- [x] Bundled predicates.json as package data (src/c2pa_conformance/data/)
- [x] Fixed CLI default path to use bundled copy
- [x] Added sync script (scripts/sync_predicates.sh)
- [x] Added 11 KG integration tests (operator coverage, loading, evaluation, rule coverage)
- [x] 739 tests passing (was 728), lint clean

#### Knowledge Graph (c2pa-knowledge-graph)
- [x] Bumped version to 1.0.0, classifier to Production/Stable
- [x] Updated README (145 predicates, 100% coverage)
- [x] Added predicates artifact to spec-version.json
- [x] Added CI workflow (pytest + ruff + mypy, Python 3.11/3.12/3.13)
- [x] Added JSON Schema for predicates.json (schemas/predicate-schema.json)
- [x] 172 tests passing

### Phase 3: Legal Entity + CI for Conformance Suite

#### Entity Name Update (both repos)
- [x] c2pa-knowledge-graph: LICENSE, NOTICE, README.md, pyproject.toml -> "Encypher Corporation"
- [x] c2pa-conformance-suite: LICENSE, NOTICE, README.md, pyproject.toml -> "Encypher Corporation"

#### CI Workflow for Conformance Suite
- [x] Created .github/workflows/ci.yml (ruff + pytest, Python 3.11/3.12/3.13, uv)
- [x] Local ruff: all checks passed
- [x] Local pytest: 739 passed (4 skipped - require c2patool binary)
- [x] GitHub Actions: billing issue on encypherai org prevents runs (not a code issue)

#### Remote Cleanup
- [x] Updated conformance suite remote to encypherai/c2pa-conformance-suite.git

### Session End Checklist
- [x] Tests pass (both repos)
- [x] Builds clean (lint clean in conformance suite; KG has pre-existing long-line warnings)
- [x] PRD updated
- [x] Team file updated
- [x] All changes committed and pushed

### Suggested Commit Messages (already committed and pushed)

**c2pa-knowledge-graph:**
```
chore: update legal entity name to Encypher Corporation
```

**c2pa-conformance-suite:**
```
chore: update legal entity to Encypher Corporation, add CI workflow
```

### Note for Next Session
- GitHub Actions billing on the encypherai org needs attention - CI runs fail with "recent account payments have failed or your spending limit needs to be increased"
- KG repo CI also fails at lint step due to pre-existing ruff violations (long lines, unsorted imports in ir_builder.py, asciidoc.py, turtle.py). A cleanup pass or ruff line-length config bump would fix this.
