# TEAM_088: Marketing Site C2PA Text Embedding Compliance

## Status: In Progress

## Goal
Ensure the marketing-site sign tool uses the actual C2PA-compliant `C2PATextManifestWrapper` embedding technique per the spec in `docs/c2pa/Manifests_Text.txt`.

## Findings
- Backend (enterprise API) already uses C2PA-compliant embedding via `c2pa_text.encode_wrapper()`
- Marketing-site proxies to enterprise API and gets back properly wrapped text
- **Gap 1**: Marketing-site has no `c2pa-text` dependency — no client-side wrapper detection
- **Gap 2**: `buildSignBasicRequest()` doesn't explicitly request C2PA text embedding format
- **Gap 3**: No client-side validation that signed text contains a valid `C2PATextManifestWrapper`

## Changes
1. Add `c2pa-text` as a dependency to the marketing-site
2. Update `buildSignBasicRequest()` to explicitly request C2PA text embedding
3. Add client-side `C2PATextManifestWrapper` detection in the sign output and verify input
4. Add tests for C2PA wrapper detection
