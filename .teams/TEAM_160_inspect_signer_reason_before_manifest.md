# TEAM_160 — Inspect Tool: Signer Before Manifest + PDF Thumbnail

## Goal
On the marketing-site `/tools/inspect` page:
1. Surface Signer and Reason Code prominently before the full manifest JSON
2. Add PDF first-page thumbnail preview in the file info bar
3. Rewrite fallback view to match the `all_embeddings` collapsible card style

## Changes
- `apps/marketing-site/src/lib/pdfTextExtractor.ts`
  - Added `renderPdfThumbnail()` — renders PDF page 1 to canvas, returns data URL
- `apps/marketing-site/src/components/tools/FileInspectorTool.tsx`
  - Added `pdfThumbnailUrl` state, generated non-blocking during PDF processing
  - File info bar: shows PDF thumbnail when available, falls back to emoji icon
  - `all_embeddings` expanded section: Signer/Reason Code/Timestamp in styled summary card above manifest JSON
  - Fallback section: rewritten as collapsible card matching `all_embeddings` style (header with status badge, expandable content with signer summary → full manifest)

## Status
- [x] Add `renderPdfThumbnail` to pdfTextExtractor.ts — ✅
- [x] Add PDF thumbnail state + generation — ✅
- [x] Signer/Reason before manifest in all_embeddings view — ✅
- [x] Rewrite fallback to match all_embeddings collapsible card style — ✅
- [x] TypeScript compilation clean (no new errors) — ✅
- [x] Visual verification — page loads correctly — ✅
