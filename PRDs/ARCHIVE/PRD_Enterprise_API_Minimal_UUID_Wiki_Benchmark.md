# Enterprise API Minimal UUID Wiki Benchmark

**Status:** ✅ Completed  
**Current Goal:** ✅ Complete — 500-article minimal_uuid benchmark + verification sampling

## Overview

We need to validate the new minimal_uuid mode against a corpus of open-source wiki articles. This includes confirming hashing, database records, Merkle trees, minimal UUID embeddings, and C2PA manifests across a 500-article batch.

## Objectives

- Reuse the existing wiki dataset tooling for batch execution.
- Add a minimal_uuid + C2PA manifest batch run with verification checks.
- Capture measurable outputs to confirm expected artifacts (hashes, DB refs, manifests).

## Tasks

### 1.0 Dataset Runner Updates

- [x] 1.1 Review existing wiki dataset scripts and choose the best integration point.
- [x] 1.2 Add minimal_uuid + C2PA manifest batch run option (500 articles).
- [x] 1.3 Add verification sampling and reporting for embeddings + manifests.

### 2.0 Validation Artifacts

- [x] 2.1 Persist outputs (embedded content + response metadata) for inspection.
- [x] 2.2 Add summary metrics: failures, missing manifest, missing UUID pointer.

### 3.0 Testing & Validation

- [x] 3.1 Unit tests passing — ✅ pytest
- [x] 3.2 Batch run (500 articles) — ✅ manual
- [x] 3.3 Verification sampling (extract & verify) — ✅ manual

## Success Criteria

- 500-article run completes with recorded metadata artifacts.
- No missing per-segment UUID pointers or document-level manifests (unless disabled).
- Verification sampling confirms extract-and-verify passes for embeddings.
- All tests passing with verification markers.

## Completion Notes

- Ran minimal_uuid batch on 500 wiki articles using demo key.
- Extract-and-verify sampling completed for 50 embedded outputs (50/50 valid after signer-id + manifest UUID lookup fixes).
- Outputs saved under outputs/minimal_uuid_outputs.
