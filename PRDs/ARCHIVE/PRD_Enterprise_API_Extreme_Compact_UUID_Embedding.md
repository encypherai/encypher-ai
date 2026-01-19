# PRD — Enterprise API Extreme Compact UUID Embedding

## Status
Complete

## Current Goal
Define and implement the `minimal_uuid` manifest mode that embeds a UUID-only signed pointer to the manifest repository.

## Overview
The current `lightweight_uuid` mode embeds a UUID pointer using `metadata_format="manifest"`, which includes additional fields and C2PA-style metadata. We need a new extreme-compact mode that uses the smallest possible signed payload with our existing `encypher-ai` encoding (Unicode variation selectors). The payload must remain a reliable, signed pointer back to our database where the full manifest is stored.

## Objectives
- Add a new manifest mode (`minimal_uuid`) that embeds only a signed UUID pointer.
- Preserve NFC normalization and UTF-8 byte-span semantics from existing advanced signing flow.
- Keep API schemas, tier gating, and documentation aligned with the new mode.
- Provide tests validating round-trip signing/verification and minimal payload behavior.

## Tasks

### 1.0 Requirements & Design
- [x] 1.1 Confirm manifest mode name and behavior (UUID-only payload, signed, file-end embedding).
- [x] 1.2 Define payload schema (UUID-only manifest_uuid).
- [x] 1.3 Update PRD goal/overview if naming or payload scope changes.

### 2.0 Tests (TDD)
- [x] 2.1 Add integration test for `/api/v1/sign/advanced` using new manifest mode and asserting NFC normalization + byte spans.
- [x] 2.2 Add assertions verifying minimal payload fields in extracted manifest metadata.

### 3.0 Implementation
- [x] 3.1 Add manifest mode to `EncodeWithEmbeddingsRequest` schema validation.
- [x] 3.2 Add tier gating in embedding executor for the new mode.
- [x] 3.3 Implement new mode in `EmbeddingService` with `metadata_format="basic"` and UUID-only payload.
- [x] 3.4 Update enterprise API docs if manifest modes are documented.

### 4.0 Testing & Validation
- [x] 4.1 Unit/integration tests passing — ✅ pytest
- [x] 4.2 Lint clean — ✅ ruff

## Success Criteria
- New manifest mode embeds a signed UUID-only payload with `UnicodeMetadata` and stores full manifest in the DB.
- Existing `lightweight_uuid` behavior remains unchanged.
- New tests pass and confirm NFC normalization + byte-span semantics.
- `uv run ruff check .` and `uv run pytest` pass for `enterprise_api`.

## Completion Notes
- Delivered `minimal_uuid` manifest mode with UUID-only signed payload and file-end embedding.
- Added schema + tier gating support and documented manifest modes.
- Tests: ✅ pytest (targeted) ✅ ruff
