# TEAM_171 — Verify UI: Segment Location Badges + Document Coverage

## Summary
Updated the marketing-site Sign/Verify tool and File Inspector tool to display
segment location information (paragraph + sentence index) and document coverage
from the expanded verification API response (TEAM_170).

## Problem
The verification API now returns `embeddings` (with `segment_location`,
`leaf_index`, `manifest_mode`), `total_segments_in_document`, and `c2pa`
manifest data — but the marketing-site UI was not consuming these fields.
Users who copied a single sentence or paragraph to verify had no way to see
*where* in the original document that text came from.

## Changes

### apps/marketing-site/src/lib/enterpriseApiTools.ts
- Added `SegmentLocationLike`, `EmbeddingDetailLike`, `C2PAInfoLike` types
- Extended `VerifyResponseLike` with `embeddings`, `total_embeddings`,
  `total_segments_in_document`, `c2pa`
- Extended `DecodeToolResponseLike` with `segment_embeddings`,
  `total_segments_in_document`, `c2pa`
- Updated `mapVerifyResponseToDecodeToolResponse` to pass through new fields

### apps/marketing-site/src/lib/enterpriseApiTools.test.ts
- Added 3 new tests: segment_embeddings passthrough, c2pa passthrough,
  null fallback for missing fields

### apps/marketing-site/src/components/tools/EncodeDecodeTool.tsx
- Added `SegmentLocation`, `SegmentEmbeddingDetail`, `C2PAInfo` interfaces
- Extended `DecodeToolResponse` with new fields
- **Tier 1**: Added segment location badge to each embedding card header
  showing "Paragraph X, Sentence Y" (1-indexed for human readability)
- **Tier 2**: Added document coverage summary bar showing
  "X of Y segments verified from this document" with manifest_mode badge

### apps/marketing-site/src/components/tools/FileInspectorTool.tsx
- Mirrored all EncodeDecodeTool changes (same interfaces, same UI elements)

## UX Details

### Tier 1 — Segment Location Badge
Each embedding card header now shows a location tag when available:
```
✅ Sentence Embedding #3  [Paragraph 2, Sentence 1]  Verified
```

### Tier 2 — Document Coverage Summary
Above the embeddings list, a summary bar shows:
```
📄 3 of 15 segments verified from this document  [micro_ecc_c2pa]
```

## Test Results
- ✅ 6/6 enterpriseApiTools tests pass (3 new + 3 existing)
- ✅ 0 TypeScript errors in changed files
- ✅ Builds clean

## Git Commit Message Suggestion
```
feat(marketing-site): show segment location and document coverage in verify UI

Display paragraph/sentence location badges on each embedding card and a
document coverage summary bar ("3 of 15 segments verified") in both the
Sign/Verify tool and File Inspector.

- Add SegmentLocationLike, EmbeddingDetailLike, C2PAInfoLike types
- Pass through embeddings, total_segments_in_document, c2pa from API
- Tier 1: Segment location badge per embedding card
- Tier 2: Document coverage summary bar with manifest_mode
- 3 new tests for field passthrough

Depends on TEAM_170 (verification API segment location backend)

TEAM_171
```
