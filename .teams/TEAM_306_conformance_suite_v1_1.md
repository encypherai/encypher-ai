# TEAM_306 - C2PA Conformance Suite v1.1.0

## Session Start
- Date: 2026-04-07
- Agent: Opus
- Objective: Implement v1.1.0 of the conformance suite integrating C2PA conformance program rubric compatibility (crJSON output, rubric evaluation, 5 new predicates)
- Prior sessions: TEAM_300 (core), TEAM_301 (phase 2), TEAM_305 (v1.0.0 format gap closure + interop validation)

## Context
- Conformance suite repo: /home/developer/code/c2pa-conformance-suite
- Reference materials fetched from c2pa-org/conformance PR 324 (in /tmp/)
- Strategic goal: Ship crJSON + rubric integration before telling Sherif, to demonstrate capabilities rather than promise them
- v1.0.0 baseline: 766 tests, 51/52 signed assets passing, 145 predicates, 70 status codes

## Work Log

### Research Phase
- [x] Fetched and analyzed all reference materials from PR 324
- [x] Mapped 5 predicate gaps between rubric and our suite
- [x] Analyzed crJSON schema structure and serialization requirements
- [x] Reviewed rubric evaluator Python script (jmespath-based)
- [x] Mapped our 70 status codes to C2PA validation result CDDL codes

### PRD
- [x] Created PRD at PRDs/CURRENT/PRD_C2PA_Conformance_Suite_v1.1.md

### Implementation
- [x] crJSON serializer: `src/c2pa_conformance/serializer/crjson.py` (585 lines)
- [x] Rubric evaluator: `src/c2pa_conformance/rubric/evaluator.py` (208 lines)
- [x] 5 new predicates: PRED-ASSE-023 through 027 in predicates.json
- [x] CLI: `--output-format crjson` on validate, `rubric` command with --crjson-input
- [x] Pipeline extended: `_run_validation_pipeline` returns (report, context, store, sig_result)
- [x] Dependencies: jmespath>=1.0.0, pyyaml>=6.0 added to pyproject.toml
- [x] Version: 1.1.0

### Verification
- [x] 848 tests pass, 10 skipped, 0 failures (80 new tests)
- [x] Google interop: 34 files, 849 pass, 0 genuine failures, 33 xfail
- [x] Rubric: 17/19 pass on our crJSON, 18/19 on c2pa-rs reference (both fail mandatory_spec_version)
- [x] Lint: ruff check clean, ruff format clean

## Files Modified (c2pa-conformance-suite repo)

### New Files
- `src/c2pa_conformance/serializer/__init__.py` - package init
- `src/c2pa_conformance/serializer/crjson.py` - crJSON serializer
- `src/c2pa_conformance/rubric/__init__.py` - package init
- `src/c2pa_conformance/rubric/evaluator.py` - rubric evaluator
- `tests/test_crjson_rubric.py` - 80 tests for both modules

### Modified Files
- `src/c2pa_conformance/cli.py` - --output-format crjson, rubric command, pipeline return signature
- `src/c2pa_conformance/data/predicates.json` - 5 new PRED-ASSE predicates (023-027)
- `tests/test_kg_integration.py` - rule count 237 -> 242
- `pyproject.toml` - version 1.1.0, jmespath + pyyaml deps

## Suggested Commit Message

```
feat(conformance): v1.1.0 - crJSON serializer, rubric evaluator, 5 new predicates

Add three capabilities to the C2PA conformance suite:

1. crJSON serializer (serializer/crjson.py): Transforms validation
   pipeline output into the C2PA conformance program's standard
   JSON-LD format. Handles assertion keying, claim serialization,
   DER certificate parsing, timestamp extraction, and status code
   classification into success/informational/failure per CDDL spec.

2. Rubric evaluator (rubric/evaluator.py): Parses multi-document
   YAML rubrics from c2pa-org/conformance and evaluates jmespath
   expressions against crJSON. Supports fail_if_matched semantics,
   multilingual report text, and {{matches}} interpolation.

3. Five new predicates (PRED-ASSE-023 through 027): Inception action
   position, reviewRatings/dataSource exclusion, mandatory
   digitalSourceType, alt content representation choice, forbidden
   external reference labels. Total: 150 predicates, 242 rules.

CLI: --output-format crjson on validate command, new rubric command
with --crjson-input option for pre-generated crJSON evaluation.

Verified: 848 tests pass, 34 Google interop files at 0 genuine
failures, rubric 17/19 pass (2 asset-level: Google SDK missing
specVersion, Google CA not in C2PA trust list).
```

## v1.2.0 - Trust Validation Fix (Continued Session)

### Context
Sherif (C2PA conformance lead) identified that Google Pixel assets fail trust validation due to:
1. Expired 30-day signer certs without timestamp-based trust extension
2. Google's private EKU OID not accepted
3. No bundled trust list

### Root Cause Analysis
Three cascading bugs in the crypto verification pipeline:
- **PRED-CRYP-017 (VAL-CRYP-0028)**: Timestamp genTime not used as validation_time for chain validation. When a valid timestamp proves signing during cert validity, the spec mandates using genTime as the reference time.
- **EKU validation**: Only accepted C2PA EKU (1.3.6.1.5.5.7.3.36) and documentSigning (1.3.6.1.5.5.7.3.3). Missing c2pa-claim_signing (1.3.6.1.4.1.62558.2.1), emailProtection (1.3.6.1.5.5.7.3.4), and MS C2PA Signing (1.3.6.1.4.1.311.76.59.1.9) per official store.cfg.
- **No default trust list**: Hardcoded `signingCredential.untrusted` when no `--trust-store` flag supplied.

### Implementation
- [x] `_resolve_validation_time()` in verifier.py: extracts timestamp genTime from COSE before chain validation, uses it as effective_time when genTime falls within leaf cert validity window
- [x] EKU expansion in x509_chain.py: `_ACCEPTED_EKU_OIDS` frozenset aligned with official store.cfg (5 OIDs)
- [x] `default_trust_store()` in trust.py: loads bundled `data/c2pa_trust_list.pem` (27 root CAs)
- [x] CLI updated: pipeline and individual commands use bundled trust list when no `--trust-store` supplied
- [x] .gitignore exception for bundled trust list PEM
- [x] Official store.cfg bundled for reference

### Verification
- [x] 857 tests pass, 6 skipped, 0 regressions (9 new tests)
- [x] TDD: Tests written before implementation (timestamp trust extension, EKU acceptance, bundled trust list)
- [x] Lint clean (ruff check)

### Finding
Google C2PA Root CA G3 is NOT in the published trust list at `verify.contentauthenticity.org/trust/anchors.pem` (still 27 anchors). Sherif said it should be there, so either the PEM is stale or Google's addition is pending publication. The code is ready to validate Google assets as soon as the trust list includes their root CA.

### Suggested Commit Message (already committed and pushed)
```
feat: timestamp-based trust extension, EKU expansion, bundled trust list (v1.2.0)
```
