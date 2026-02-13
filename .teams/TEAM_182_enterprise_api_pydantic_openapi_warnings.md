# TEAM_182 — Enterprise API Pydantic/OpenAPI Warning Fixes

## Status: COMPLETE

## Summary
Fixed two startup warnings in the enterprise API container:

### Bug 1: Pydantic V2 `schema_extra` deprecation warning
- **Root cause**: `merkle.py` and `provisioning.py` used old Pydantic V1 `class Config: schema_extra` instead of V2 `json_schema_extra`
- **Fix**: Renamed `schema_extra` → `json_schema_extra` in all `Config` classes across both files (7 occurrences total)
- **Files**: `enterprise_api/app/schemas/merkle.py`, `enterprise_api/app/schemas/provisioning.py`

### Bug 2: Duplicate Operation ID warning for `proxy_organizations`
- **Root cause**: `api_route` with multiple HTTP methods (GET/POST/PUT/PATCH/DELETE/OPTIONS) generates one OpenAPI operation per method, causing duplicate operation IDs
- **Fix**: Added `include_in_schema=False` to both proxy routes — these are internal forwarding routes to the auth service and should not appear in the OpenAPI docs
- **File**: `enterprise_api/app/routers/organizations_proxy.py`

## Verification
- All three modified files pass `py_compile`
- No remaining `schema_extra` (without `json_` prefix) in the enterprise_api app code
- `admin.py`, `api_response.py`, `sign_schemas.py`, `request_models.py`, `response_models.py` already used the correct `json_schema_extra`

## Git Commit Message Suggestion
```
fix(enterprise-api): resolve Pydantic V2 and OpenAPI startup warnings

- Rename schema_extra → json_schema_extra in merkle.py and provisioning.py
  (7 occurrences across Config classes) to fix Pydantic V2 deprecation warning
- Add include_in_schema=False to organizations proxy routes to eliminate
  duplicate Operation ID warning for OPTIONS method
```
