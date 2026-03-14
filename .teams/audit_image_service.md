# Audit: services/image-service/

Date: 2026-03-14
Scope: /home/developer/code/encypherai-commercial/services/image-service/
Excluded: .venv/, node_modules/
Skills applied in order: unix-agent-design -> simplify -> security-review

---

## 1. Unix Agent Design Audit

### Summary

The image-service is a three-endpoint FastAPI HTTP microservice (POST /api/v1/watermark, POST /api/v1/detect, GET /health). It is not an MCP server or CLI agent, so the 10 criteria apply to its HTTP handler surfaces. The service had solid fundamentals (graceful degradation, structured responses, per-request timing in body) but failed on navigation errors (bare error strings), unused size config (overflow guard defined but never enforced), missing image type guard before PIL, no response metadata footer on error paths, and duplicate service-availability + base64-decode logic woven into both handlers.

### Scorecard (before fixes)

| Route | Nav Errors | Overflow | Binary Guard | Footer | Help L1 | Help L0 | Stderr | Two-Layer | Surface | Chains |
|---|---|---|---|---|---|---|---|---|---|---|
| POST /watermark | FAIL | FAIL | PARTIAL | FAIL | PARTIAL | PARTIAL | PASS | PARTIAL | PASS | FAIL |
| POST /detect | FAIL | FAIL | PARTIAL | FAIL | PARTIAL | PARTIAL | PASS | PARTIAL | PASS | FAIL |
| GET /health | N/A | N/A | N/A | FAIL | N/A | N/A | N/A | N/A | PASS | FAIL |

### Key Findings

**1. Navigation errors (FAIL)**
- `watermark.py:36` (pre-fix): `detail="Invalid base64 image data"` - no next-step hint.
- `watermark.py:29-31`: 503 `"TrustMark model not available"` - no pointer to `GET /health`.
- `watermark.py:45`: 500 `"Watermark encoding failed"` - no next-step hint.
- All three error strings were enriched during the simplify phase (see Section 2).

**2. Overflow mode (FAIL)**
- `config.py:11`: `MAX_IMAGE_SIZE_BYTES = 10_485_760` defined but never imported or used in any router or service. A 50 MB base64-encoded payload will be fully decoded into memory and passed to PIL before any error.
- Recommendation (not yet implemented): enforce `MAX_IMAGE_SIZE_BYTES` in `_decode_image_b64()` after the decode, returning HTTP 413 with a clear message.

**3. Binary guard (PARTIAL)**
- `base64.b64decode(..., validate=True)` catches malformed base64 (good).
- After decode, bytes flow directly into `PIL.Image.open()` with no magic-byte pre-check. A crafted non-image payload (executable, archive) triggers an opaque PIL exception that surfaces as `500: Watermark encoding/detection failed`.
- Recommendation (not yet implemented): check `image_bytes[:4]` against JPEG (`\xff\xd8\xff`), PNG (`\x89PNG`), WEBP (`RIFF`+`WEBP`) signatures before calling PIL; return 400 with a typed message on mismatch.

**4. Metadata footer (FAIL)**
- Success responses include `processing_time_ms` as a body field (good), but this is business data, not a presentation-layer footer.
- HTTP error responses (400, 500, 503) carry no timing or status token.
- Recommendation: add FastAPI middleware adding `X-Processing-Time-Ms` to all responses.

**5. Progressive help L1 (PARTIAL)**
- Pydantic 422 responses describe failing fields (good).
- Manual 400 for bad base64 now includes example guidance (fixed in simplify phase).

**6. Progressive help L0 (PARTIAL)**
- FastAPI docstrings surface in OpenAPI (`/docs`). Docstrings now enumerate error codes.

**7. Stderr attachment (PASS)**
- `logger.exception(...)` used on 500 paths. Stacks are logged server-side; not exposed to callers (correct for a public-facing service).

**8. Two-layer separation (PARTIAL -> improved)**
- Business logic is in `trustmark_service.py` (good).
- Before fix: both handlers duplicated the decode/timing pattern.
- After fix: `_get_service()` and `_decode_image_b64()` helpers extracted (see Section 2).

**9. Tool surface area (PASS)**
- 3 routes total (watermark, detect, health). Well within the <=5 threshold.

**10. Chain composition (FAIL)**
- No composition supported. Each POST is fully isolated. Acceptable for an internal microservice; composition belongs at the enterprise-api layer.

### Remaining Gaps (not fixed - out of scope for refactor-only session)
- Enforce `MAX_IMAGE_SIZE_BYTES` in `_decode_image_b64()`.
- Add image magic-byte guard before `PIL.Image.open()`.
- Add FastAPI middleware for `X-Processing-Time-Ms` response header on all paths.

---

## 2. Simplify Review

### Changes Made

All 19 tests passed before and after every change. Ruff lint and format were applied and passed.

#### 2.1 `app/services/trustmark_service.py`

**_mime_to_pil_format dict rebuilt per call (efficiency)**
- Before: `mapping = {...}` dict literal constructed inside `_mime_to_pil_format()` on every call.
- After: Promoted to module-level constant `_MIME_TO_PIL: dict[str, str]`.

**Magic numbers for bit manipulation (quality)**
- Before: `format(msg_int, "0100b")[:100]` and `secret[:100]` scattered across encode/decode.
- After: Named constants `_WATERMARK_BITS = 100` and `_BIN_FORMAT = f"0{_WATERMARK_BITS + 4}b"` used at both call sites.

**`Optional[str]` -> `str | None` (quality / reuse)**
- Before: `from typing import Optional` with `Optional[str]` and `Optional[object]` in return types and type annotations.
- After: Replaced with Python 3.11 union syntax `str | None` and `object | None`. `from typing import Optional` import removed.

**Encode confidence sentinel clarified (quality)**
- Before: `confidence` return value of `1.0` for encode was undocumented and misleading.
- After: Docstring explicitly states `confidence is always 1.0 for encode (TrustMark does not score encode quality)`.

**Stale doc comment removed (quality)**
- Before: Docstring referenced `optional-requirements.txt in this directory` (file does not exist).
- After: That line removed.

#### 2.2 `app/routers/watermark.py`

**Duplicate service availability guard (reuse)**
- Before: Identical 5-line guard block copy-pasted into both `watermark_image` and `detect_watermark`.
- After: Extracted to `_get_service(request: Request) -> TrustMarkService`. Single definition, two call sites.

**Duplicate base64 decode block (reuse)**
- Before: Identical try/except base64 decode block copy-pasted into both handlers.
- After: Extracted to `_decode_image_b64(image_b64: str) -> bytes`. Single definition, two call sites.

**Navigation hints added to all error detail strings (nav errors)**
- 503: now includes `"Check GET /health for model status."`
- 400: now includes `"Send standard base64-encoded bytes of a JPEG, PNG, or WEBP image."`
- 500: now includes `"Check server logs."`

**Bare except swallowing base64 error silently (quality)**
- Before: `except Exception:` with no logging on the base64 decode failure.
- After: `logger.debug("base64 decode failed: %s", exc)` added; exception chained with `from exc`.

**Docstrings enriched with error code table (help L0/L1)**
- Both handlers now have a structured `Errors:` section listing 400/503/500.

**`DetectRequest` field descriptions added (quality / consistency)**
- Before: `image_b64` and `mime_type` on `DetectRequest` had no `Field(...)` descriptions.
- After: Both fields use `Field(...)` with the same descriptions as `WatermarkRequest`.

#### 2.3 `app/schemas/watermark_schemas.py`

- `Optional[str]` -> `str | None` on `DetectResponse.message_bits`.
- `from typing import Optional` import removed.
- `DetectRequest` fields now use `Field(...)` with descriptions (consistency with `WatermarkRequest`).

#### 2.4 `app/main.py`

**Module-level `trustmark_service` global removed (quality)**
- Before: A `global trustmark_service` declaration and module-level `trustmark_service: TrustMarkService | None = None` existed "for tests" but tests already use `app.state.trustmark_service` directly.
- After: Global removed. Local variable `svc` used inside `lifespan()` and assigned to `app.state.trustmark_service`.

### Items Reviewed but Not Changed

- `message_bits` hex validation: `int(message_bits, 16)` will raise `ValueError` for non-hex chars (the Pydantic schema enforces only length). The resulting 500 is not a security issue for this internal service. Adding a hex pattern validator would be an improvement but is not a simplify concern.
- `PIL.Image.open()` with no magic-byte pre-check: noted in unix-agent-design; left for a dedicated security hardening task.
- `MAX_IMAGE_SIZE_BYTES` not enforced: noted in unix-agent-design; left for a dedicated task.

---

## 3. Security Review

### Summary

No HIGH or MEDIUM confidence security vulnerabilities were found in the `services/image-service/` code. The changes made during this session are refactoring in nature (helper extraction, type annotation modernization, dead-code removal, error message enrichment) and do not introduce new attack surfaces.

### Data Flow Analysis

| Input | Path | Risk |
|---|---|---|
| `image_b64` (str) | `base64.b64decode(validate=True)` -> `PIL.Image.open()` | base64 validated; PIL parsing is a dependency risk (CVEs handled separately) |
| `mime_type` (str) | `dict.get(mime_type.lower(), "JPEG")` | Safe dict lookup; no injection path |
| `message_bits` (str) | Pydantic: exactly 26 chars; `int(..., 16)` | Non-hex raises ValueError -> 500; not exploitable |

### Evaluated Candidates (all filtered out)

**PIL Image.open() with untrusted bytes**
- `trustmark_service.py:87,116`: PIL has had CVEs for malformed image parsing. These are library-version issues managed by `uv` dependency updates, not a code vulnerability introduced here. Confidence: 0.5 (excluded per "outdated third-party libraries" rule).

**No authentication on endpoints**
- This is an internal microservice; authentication is expected at the gateway/enterprise-api layer. Not a vulnerability introduced by these changes.

**`message_bits` non-hex characters -> ValueError -> 500**
- Pydantic enforces exactly 26 chars. Non-hex chars cause `int(message_bits, 16)` to raise, returning 500. Impact: caller gets an unhelpful error. Not exploitable for unauthorized access or data breach. Confidence: 0.3.

**`MAX_IMAGE_SIZE_BYTES` not enforced**
- This is a DOS/resource exhaustion finding, explicitly excluded from scope.

### Security Verdict

No vulnerabilities meeting the >80% confidence threshold were identified. The refactoring session improved error message quality and reduced code duplication without introducing new attack surfaces.

---

## 4. Remaining Recommendations (Future Work)

These were identified but not implemented during this session (out of scope for a refactor-only audit):

1. **Enforce `MAX_IMAGE_SIZE_BYTES`** in `_decode_image_b64()` after decode, returning HTTP 413 with a navigation hint. The config value exists (`config.py:11`) but is unused.

2. **Add image magic-byte guard** before `PIL.Image.open()`: check first 4 bytes against JPEG (`\xff\xd8\xff`), PNG (`\x89PNG`), WEBP (`RIFF...WEBP`). Return HTTP 400 with `"Unsupported image format. Send JPEG, PNG, or WEBP."` on mismatch.

3. **Add hex-only validator to `message_bits`** in `WatermarkRequest`: use a Pydantic `pattern` constraint (`^[0-9a-fA-F]{26}$`) to catch non-hex input at the schema layer before it reaches `int(..., 16)` in the service.

4. **Add response timing middleware**: a single FastAPI middleware adding `X-Processing-Time-Ms` to all responses (including errors) would satisfy Unix Agent Design criterion 4 (metadata footer) without touching individual handlers.

---

## 5. Test Status

- 19/19 tests passed before and after all changes.
- Ruff lint: all checks passed.
- Ruff format: 4 files reformatted; all files clean after formatting.

```
19 passed in 0.24s
```

---

## 6. Files Changed

| File | Changes |
|---|---|
| `app/services/trustmark_service.py` | Module-level MIME constant, named bit-width constants, `str | None` types, stale doc removed |
| `app/routers/watermark.py` | `_get_service()` and `_decode_image_b64()` helpers extracted; error messages enriched; docstrings with error tables |
| `app/schemas/watermark_schemas.py` | `str | None` on DetectResponse; Field descriptions on DetectRequest |
| `app/main.py` | Module-level `trustmark_service` global removed |
| `pyproject.toml` | `ruff` added to dev dependencies |
