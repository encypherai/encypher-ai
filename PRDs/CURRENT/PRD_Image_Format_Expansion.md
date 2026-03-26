# PRD: C2PA Image Format Expansion

**Status**: In Progress
**Current Goal**: Expand C2PA still image signing to all 13 conformance formats
**Team**: TEAM_276

## Overview

Expand the Enterprise API's C2PA still image signing support from 4 formats (JPEG, PNG, WebP, TIFF) to all 13 formats required by the C2PA Conformance Program intake form. The c2pa-python Rust SDK already supports all formats for JUMBF manifest embedding -- our work is validation, EXIF handling, and schema updates.

## Objectives

- Support all 13 C2PA conformance still image MIME types for signing
- Centralize format configuration in a single registry (SSOT)
- Handle formats Pillow can't open via magic-byte validation + direct passthrough to c2pa-python
- Add pillow-heif for HEIC/HEIF family support
- Maintain privacy guarantees (EXIF stripping where applicable)
- Full test coverage for all new formats

## Architecture: Three-Tier Format Handling

- **Tier A (Pillow native)**: JPEG, PNG, WebP, TIFF, GIF -- full Pillow validation + EXIF strip
- **Tier B (Plugin-backed)**: HEIC, HEIF, HEIC-sequence, HEIF-sequence, AVIF -- pillow-heif plugin + Pillow native AVIF
- **Tier C (Bypass)**: SVG, JXL, DNG -- magic-byte validation only, pass raw bytes to c2pa-python

## Tasks

### 1.0 Foundation: Format Registry (SSOT)
- [x] 1.1 Create `enterprise_api/app/utils/image_format_registry.py` -- pytest
- [x] 1.2 Replace duplicated SUPPORTED_MIME_TYPES in rich_sign_schemas.py and image_utils.py -- pytest
- [x] 1.3 Write tests for format registry -- pytest (37 tests)

### 2.0 Magic Byte Validation (Tier C)
- [x] 2.1 Add magic byte signatures to registry (SVG, DNG, JXL) -- pytest
- [x] 2.2 Add `validate_magic_bytes()` function in registry -- pytest
- [x] 2.3 Write tests for magic byte validation -- pytest (13 tests)

### 3.0 EXIF Stripping Expansion
- [x] 3.1 Refactor `strip_exif` into tier-aware dispatcher -- pytest
- [x] 3.2 Add GIF to Pillow re-encode path (via registry) -- pytest
- [x] 3.3 Register pillow-heif plugin via `ensure_heif_plugin()` -- pytest
- [x] 3.4 Write tests for EXIF stripping per format -- pytest

### 4.0 Validation Pipeline
- [x] 4.1 Refactor `validate_image` for tier-aware dispatch (Pillow vs magic bytes) -- pytest
- [x] 4.2 SVG validation via magic bytes (XML start detection) -- pytest
- [x] 4.3 Write tests for validation per format -- pytest

### 5.0 Dependencies
- [x] 5.1 `uv add pillow-heif>=0.18.0` -- installed pillow-heif==1.3.0
- [ ] 5.2 Verify Pillow AVIF support (>=12.1.1 bundled)

### 6.0 Signing Service Updates
- [x] 6.1 strip_exif bypasses Tier C, validate_image handles all tiers -- pytest
- [x] 6.2 Guard compute_phash for non-raster formats (returns 0 for Tier C) -- pytest
- [ ] 6.3 Write signing integration tests for all new formats (c2pa.Builder.sign roundtrip)

### 7.0 Schema/API Updates
- [x] 7.1 Update rich_sign_schemas.py to use registry -- pytest
- [x] 7.2 Update unified_verify_service.py _IMAGE_MIMES -- pytest
- [x] 7.3 Write schema validation tests -- pytest

### 8.0 Test Fixtures
- [x] 8.1 Test generators for GIF, SVG, DNG header, JXL header -- pytest
- [ ] 8.2 HEIC/HEIF test fixtures with pillow-heif
- [ ] 8.3 AVIF test fixture

## Success Criteria

- All 13 MIME types accepted by the signing API
- c2pa-python successfully embeds JUMBF manifests for each format
- EXIF stripping works for Tier A/B, documented bypass for Tier C
- All tests pass (unit + integration)
- No regressions in existing JPEG/PNG/WebP/TIFF signing

## Test Results

- 234 unit tests passing (67 new + 167 existing)
- Zero regressions
- Lint clean (ruff)

## Notes

- DNG: EXIF preservation is intentional (raw sensor metadata is the point)
- SVG: No EXIF, no pHash, no dimension validation. Document XSS caveat.
- JXL: Tier C because Pillow JXL support requires libjxl system library
- Sequence formats (heic-sequence, heif-sequence): structurally same container, MIME-level distinction
