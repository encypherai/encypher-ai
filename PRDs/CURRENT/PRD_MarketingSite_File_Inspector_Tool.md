# PRD: Marketing Site File Inspector Tool

## Status: Complete
## Current Goal: Build drag-and-drop file inspector for text file verification

## Overview
Add a new "Inspect" tool to the marketing site that allows users to drag-and-drop or browse for text files, read their content client-side, and verify them against the existing verification API. Inspired by Adobe Content Authenticity's Inspect UI.

## Objectives
- Provide a visual drag-and-drop file upload zone for text files
- Read file content client-side (no server-side file upload needed)
- Send extracted text to existing `/api/tools/verify` endpoint
- Display verification results using existing `DecodeToolResponse` rendering
- Support common text file formats: .txt, .md, .html, .json, .xml, .csv, .log, .rtf, .tex

## Tasks
- [x] 1.0 Create TEAM_152 file
- [x] 1.1 Create PRD
- [x] 2.0 Create FileInspectorTool component — ✅ tsc ✅ puppeteer
  - [x] 2.1 Drag-and-drop zone with visual feedback
  - [x] 2.2 File type validation (text files only)
  - [x] 2.3 Client-side file reading via File.text() API
  - [x] 2.4 Integration with existing verify API
  - [x] 2.5 Verification results display (reuse existing patterns)
- [x] 3.0 Create /tools/inspect page — ✅ puppeteer
- [x] 4.0 Register in tools config — ✅ puppeteer
- [x] 5.0 Write tests — ✅ jest (17 tests)
  - [x] 5.1 Unit tests for fileInspector.ts utilities
  - [x] 5.2 Browser verification via puppeteer preview

## Success Criteria
- Users can drag-and-drop or browse for text files
- File content is read and verified against the API
- Results display verification status, manifests, and embedding details
- Supported formats are clearly listed
- UI matches the quality of existing tools pages
