# C2PA 2.3 Conformance Checklist (Enterprise API)

**Owner**: TEAM_142
**Scope**: Enterprise API + encypher-ai core
**Status**: Drafted for submission evidence bundle

## 1. Program & Security Requirements
- [x] Document signer identity model (Private Credential Store). See `docs/c2pa/COMPLIANCE.md`.
- [x] Describe certificate lifecycle + revocation handling. See `enterprise_api/docs/KEY_MANAGEMENT_READINESS.md` and revocation endpoints.
- [x] Provide security review checklist reference. See `enterprise_api/docs/SECURITY_REVIEW_CHECKLIST.md`.
- [x] Provide threat model reference. See `enterprise_api/docs/THREAT_MODEL.md`.
- [x] Provide data integrity/auditability reference. See `enterprise_api/docs/DATA_INTEGRITY_AUDITABILITY.md`.

## 2. Manifest Construction (v2.3)
- [x] `@context` uses `https://c2pa.org/schemas/v2.3/c2pa.jsonld`.
- [x] `claim_label` uses `c2pa.claim.v2`.
- [x] Actions assertion uses `c2pa.actions.v2` and includes `c2pa.created` + `c2pa.watermarked`.
- [x] Ingredient assertion uses `c2pa.ingredient.v3` when prior manifests exist.
- [x] Metadata assertion uses `c2pa.metadata` with JSON-LD payload.
- [x] Hard binding (`c2pa.hash.data.v1`) with byte-level exclusions.
- [x] Soft binding (`c2pa.soft_binding.v1`) over CBOR payload. Implemented for audio via `audio-watermark-service` (method: `encypher.spread_spectrum_audio.v1`), video via `video-watermark-service` (method: `encypher.spread_spectrum_video.v1`), and image via `image-service` TrustMark neural watermark (method: `encypher.trustmark_neural.v1`).
- [x] Composite multi-media manifest: `/sign/rich` creates an article-level manifest with `c2pa.ingredient.v3` references for each signed media file (image, audio, video). Each ingredient carries its own C2PA manifest and hard binding. The composite manifest binds all ingredients under one `instance_id` with a deterministic `manifest_hash`, satisfying C2PA Section 9.8 (Ingredients) for multi-media provenance chains.

## 3. Verification Behavior
- [x] Validator accepts v2.3 contexts and actions v2 (see `enterprise_api/app/services/c2pa_validator.py`).
- [x] Extract-and-verify resolves signer_id from action agents and validates signature.
- [x] Hard binding verification uses byte offsets from manifest exclusions.

## 4. Tests & Evidence
- [x] Unit tests: `enterprise_api/tests/test_c2pa_validator.py`.
- [x] Integration tests: `enterprise_api/tests/test_c2pa_conformance_sign_verify.py`.
- [x] Byte offset regression: `enterprise_api/tests/test_c2pa_text_exclusions_byte_offsets.py`.
- [x] Extract/verify metadata: `enterprise_api/tests/test_public_extract_and_verify_minimal_uuid.py`.
- [x] Lint/type checks: `uv run ruff check .` + `uv run mypy .`.
- [x] Security audit: `uv run pip-audit` (skips non-PyPI internal packages).

## 5. Submission Artifacts
- [x] Capture CLI output for test/lint/audit runs and attach to evidence bundle.
- [x] Provide product description + architecture summary for submission.
- [x] Provide link list to supporting docs (COMPLIANCE, THREAT_MODEL, etc.).
