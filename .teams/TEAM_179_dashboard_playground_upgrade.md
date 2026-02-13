# TEAM_179 — Dashboard Playground UX Upgrade

## Status: COMPLETE

## Objective
Upgrade the dashboard API playground to best-in-class UX with recommended defaults and rich signing form.

## Changes Made

### Sign Form (`page.tsx`)
- Added dropdown selectors for segmentation_level, manifest_mode, document_type, embedding_strategy
- Highlighted "Sentence (recommended)" and "Micro ECC + C2PA (recommended)" as best options
- Moved text field to top of form (most important first)
- Added helpful descriptions under each dropdown
- Updated sample content with multi-sentence text demonstrating sentence-level signing

### Response Parsing Fixes (`page.tsx`)
- Fixed sign response summary for unified `/sign` endpoint (data.document.signed_text)
- Show instance_id, merkle_root, segments count in sign summary
- Fixed lastSignedContent extraction for Quick Start flow
- Added helpful text explaining invisible Unicode signatures

### New Features
- Collapsible "How It Works" guide panel: 3-step visual flow (Sign → Publish → Verify)
- Consolidated sign/sign-with-options into single endpoint with options
- Updated verify endpoint to use /verify/advanced (authenticated)
- Improved field documentation

### Request Builder (`playgroundRequestBuilder.mjs`)
- Support for segmentation_level, manifest_mode, embedding_strategy in form → JSON conversion
- Options nested under `options` key in JSON body (matches API schema)
- Bidirectional sync: JSON → form parsing extracts options from nested object

### Endpoints (`playgroundEndpoints.mjs`)
- Updated sign sample with recommended defaults (sentence, micro_ecc_c2pa)
- Better descriptions explaining what each endpoint does for new users
- Verify endpoint now points to /verify/advanced

## Testing
- TypeScript: `tsc --noEmit` clean
- Build: `next build` clean (38.1 kB playground page)
- Browser test: auth service not running, skipped Puppeteer verification

## Git Commit
```
feat(dashboard): upgrade API playground with recommended defaults and rich sign form
```
