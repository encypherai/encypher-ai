# Enterprise API Contract & Client Readiness

**Status**: Drafted for production readiness review
**Scope**: OpenAPI contract review, versioning policy, SDK readiness, docs completeness
**Owners**: API Engineering + Developer Experience

## 1. OpenAPI Contract Review (PRD 6.1)
### Versioning Policy
- **SemVer** for API contract versions.
- **Major** version for breaking changes (endpoint removal, response schema changes).
- **Minor** version for additive, backward-compatible changes.
- **Patch** version for documentation corrections.

### Backward Compatibility
- Deprecate endpoints before removal with 90‑day notice.
- Maintain deprecated endpoints until next major release.
- Use explicit deprecation markers in OpenAPI schema.

### Review Checklist
- OpenAPI diff against last release.
- Verify tags and summaries match documentation.
- Confirm internal-only endpoints remain gated.
- Validate request/response examples for new endpoints.

## 2. SDK Readiness (PRD 6.2)
### Generation Flow
- Source of truth: `sdk/openapi.internal.json`.
- SDK generation: `python sdk/generate_sdk.py`.
- Output SDKs: Python/TypeScript/Go/Rust.

### Release Checklist
- Regenerate SDKs with every OpenAPI change.
- Run SDK unit tests + linting.
- Verify error parity with API error codes.
- Publish release notes with breaking changes.

## 3. Documentation Completeness (PRD 6.3)
Required documentation:
- Public verification flow and signature requirements.
- Error codes and response schema reference.
- API key authentication + scopes.
- Rate limit behavior and headers.

## 4. Usage Analytics & Reporting (PRD 6.4)
- Usage endpoints must expose per‑org usage and quota consumption.
- Monthly usage reports are required for enterprise customers.
- Exportable usage reports in CSV/JSON.

## 5. References
- `enterprise_api/docs/API.md`
- `docs/api/ERROR_CODES.md`
- `sdk/generate_sdk.py`
