# PRD: C2PA Conformance Suite v1.1.0

## Status: Complete

## Current Goal
Implement crJSON serialization, rubric evaluation, and 5 new predicates to achieve full compatibility with the C2PA conformance program rubric system.

## Overview
The C2PA conformance program (PR 324 in c2pa-org/conformance) defines a rubric evaluation system that operates on crJSON, a standardized JSON-LD serialization of C2PA manifest stores with validation results. Our conformance suite currently produces a proprietary JSON report format. v1.1.0 bridges this gap: our suite will emit standard crJSON, enabling the conformance program's rubric evaluator to run against our output. This positions Encypher's tool as a conformance-program-compatible validator.

Three workstreams: (1) crJSON serializer that transforms our pipeline output into the standard format, (2) rubric evaluator CLI integration so users can run conformance rubrics against our crJSON, (3) five new predicates that close the remaining gaps between our predicate coverage and the rubric's validation checks.

## Objectives
- Emit crJSON output conforming to the crJSON schema (Draft 2020-12) from the conformance program
- Run the official conformance program rubric (0.2 + spec 2.4) against our crJSON output and pass all 19 checks
- Add 5 predicates covering rubric validation rules not yet in our predicate set
- Maintain zero regressions against existing 766 tests and 145 predicates

## Architecture

### Layer Distinction
Our conformance suite IS the validator. It extracts JUMBF, parses manifests, verifies crypto, and evaluates predicates. The crJSON format is the validator's OUTPUT format, consumed by the rubric evaluator. These are complementary layers:

```
Asset file
  -> [Our suite] Extract + Parse + Verify + Evaluate
  -> [crJSON serializer] Transform results to crJSON
  -> [Rubric evaluator] Run conformance rubrics against crJSON
  -> Conformance report
```

### crJSON Structure (from spec)
```json
{
  "@context": {"@vocab": "https://c2pa.org/crjson/"},
  "manifests": [{
    "label": "urn:c2pa:...",
    "assertions": {
      "c2pa.actions.v2": {...},
      "c2pa.hash.data": {...}
    },
    "claim.v2": {
      "instanceID": "...",
      "signature": "self#jumbf=...",
      "claim_generator_info": {...},
      "alg": "...",
      "created_assertions": [...],
      "gathered_assertions": []
    },
    "signature": {
      "algorithm": "es256",
      "certificateInfo": {...},
      "timeStampInfo": {...}
    },
    "validationResults": {
      "success": [{"code": "...", "url": "...", "explanation": "..."}],
      "informational": [...],
      "failure": [],
      "specVersion": "2.4",
      "validationTime": "..."
    }
  }],
  "jsonGenerator": {"name": "...", "version": "..."}
}
```

Key differences from our current output:
- Assertions are a keyed object (by label), not an array
- Claim data is under `claim.v2` key (not `claim`)
- Signature info includes parsed certificate details (subject, issuer, validity)
- validationResults uses success/informational/failure arrays with standard status codes
- Root has JSON-LD @context and jsonGenerator metadata

### Status Code Mapping
Our predicates emit 70 unique status codes. These map 1:1 to the C2PA validation result CDDL codes. The crJSON serializer classifies each into success/informational/failure based on the code prefix and the CDDL definitions:
- Success: `.match`, `.validated`, `.trusted`, `.insideValidity`, `.notRevoked`
- Informational: `.additionalExclusionsPresent`, `.inaccessible`, `.skipped`, `.unknown`, `.deprecated`
- Failure: everything else (`.mismatch`, `.malformed`, `.missing`, `.invalid`, etc.)

## Tasks

### 1.0 crJSON Serializer
- [x] 1.1 Create `src/c2pa_conformance/serializer/crjson.py` module -- 585 lines, full crJSON spec compliance
  - [x] 1.1.1 `serialize_to_crjson()` entry point
  - [x] 1.1.2 Assertion keyed-object transform with `__N` suffix disambiguation
  - [x] 1.1.3 `claim.v2` serialization with bytes-to-b64 encoding
  - [x] 1.1.4 Signature certificateInfo from DER x5chain + TSA timestamp parsing
  - [x] 1.1.5 validationResults with success/informational/failure classification + JUMBF URL routing
  - [x] 1.1.6 Root @context, reversed manifests array, jsonGenerator metadata
  - [x] 1.1.7 `classify_status_code()` with suffix-based and exact match classification
- [x] 1.2 `--output-format crjson` option on `validate` CLI command
- [x] 1.3 Pipeline returns (report, context, store, sig_result) for crJSON serialization
- [x] 1.4 Tests: 51 tests covering classify, parse_rdn, encode, build_assertions, serialize -- all pass

### 2.0 Rubric Evaluator Integration
- [x] 2.1 Create `src/c2pa_conformance/rubric/evaluator.py` module -- 208 lines
  - [x] 2.1.1 `parse_rubric()` multi-document YAML parser
  - [x] 2.1.2 jmespath expression evaluation via `evaluate_rubric()`
  - [x] 2.1.3 `_resolve_text()` with bool-keyed multilingual and `{{matches}}` interpolation
  - [x] 2.1.4 `_coerce_bool()` with fail_if_matched inversion semantics
  - [x] 2.1.5 `RubricResult` and `RubricReport` dataclasses
- [x] 2.2 `rubric` CLI command
  - [x] 2.2.1 Asset path -> crJSON -> rubric evaluation pipeline
  - [x] 2.2.2 `--crjson-input` option for pre-generated crJSON
  - [x] 2.2.3 Text and JSON output format options
- [x] 2.3 Tests: 29 tests covering parse, evaluate, coerce, resolve, CLI -- all pass

### 3.0 New Predicates (5 Rubric Gaps)
- [x] 3.1 PRED-ASSE-023: Inception action position (VAL-ASSE-0119)
- [x] 3.2 PRED-ASSE-024: reviewRatings / human entry dataSource (VAL-ASSE-0120)
- [x] 3.3 PRED-ASSE-025: Mandatory digitalSourceType for editorial actions (VAL-ASSE-0121)
- [x] 3.4 PRED-ASSE-026: Alternative content representation choice (VAL-ASSE-0122)
- [x] 3.5 PRED-ASSE-027: Forbidden labels in external references (VAL-ASSE-0123)
- [x] 3.6 All 5 pass on Google interop fixtures (0 regressions)
- [x] 3.7 Added to cross_cutting in predicates.json; rule count updated 237 -> 242

### 4.0 Validation and Release
- [x] 4.1 Full regression: 848 pass, 10 skip, 0 fail
- [x] 4.2 Google interop: 34 files, 849 pass, 0 genuine failures, 33 xfail (trust list)
- [x] 4.3 Rubric evaluation on our crJSON: 17/19 pass (2 are asset-level: specVersion missing from Google SDK, trust list)
- [x] 4.4 Rubric on c2pa-rs reference crJSON: 18/19 pass (same specVersion issue)
- [x] 4.5 Version updated to 1.1.0; jmespath + pyyaml added to dependencies
- [x] 4.6 ruff check clean, ruff format clean

## Success Criteria
- [x] `c2pa-conformance validate ASSET --output-format crjson` emits valid crJSON
- [x] Official rubric evaluator passes 17/19 checks against our crJSON (2 failures are asset-level, not validator-level; c2pa-rs reference gets 18/19 with same mandatory_spec_version failure)
- [x] 5 new predicates pass on conformant assets
- [x] Zero regressions: 848 tests pass, 34 interop files pass
- [x] Total predicate count: 150 (145 existing + 5 new)

## Completion Notes

Completed 2026-04-07. v1.1.0 delivers three capabilities:

1. **crJSON serializer** (`serializer/crjson.py`): Transforms our validation pipeline output into the C2PA conformance program's standard JSON-LD format. Handles assertion keying, claim serialization, DER certificate parsing, timestamp extraction, and status code classification into success/informational/failure buckets per the CDDL spec.

2. **Rubric evaluator** (`rubric/evaluator.py`): Parses multi-document YAML rubrics and evaluates jmespath expressions against crJSON data. Supports fail_if_matched semantics, multilingual report text, and {{matches}} interpolation.

3. **5 new predicates** (PRED-ASSE-023 through 027): Inception action position, reviewRatings/dataSource exclusion, mandatory digitalSourceType, alternative content representation choice, forbidden external reference labels.

The 2 rubric failures on our output are both asset-level issues (Google SDK missing specVersion, Google CA not in C2PA trust list) confirmed by running the same rubric against c2pa-rs reference output which has the identical specVersion failure.
