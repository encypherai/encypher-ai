# PRD: Chrome Extension UX Fix + Online Editor Signing

## Status: COMPLETE
## Current Goal: All tasks complete

## Overview
Fix UX regressions in the Chrome extension popup header (unreadable, missing real logo) and add support for detecting and signing content in online editors like Google Docs and Microsoft Word Online. The editor sign button should use Encypher branding and be optionally toggleable.

## Objectives
- Restore proper Encypher branding in popup header (use real logo icon, readable text)
- Fix content detection/rescan in Google Docs (canvas-based DOM)
- Add in-place signing for Google Docs and MS Word Online
- Use Encypher brand colors throughout editor-signer UI
- Make the in-editor sign button toggleable via settings

## Tasks

### 1.0 Popup Header Fix
- [x] 1.1 Replace generic SVG checkmark with real Encypher icon (PNG) in popup header -- visual
- [x] 1.2 Ensure header text is readable against gradient background -- visual

### 2.0 Google Docs / MS Word Online Detection
- [x] 2.1 Add Google Docs detection (docs.google.com, accessibility layer DOM) -- node --test
- [x] 2.2 Add MS Word Online detection (word.live.com, contenteditable regions) -- node --test
- [x] 2.3 Extract text from Google Docs accessibility layer for scanning -- node --test
- [x] 2.4 Fix Rescan to work with Google Docs DOM structure (scan extra roots) -- node --test

### 3.0 In-Place Sign Button for Online Editors
- [x] 3.1 Add Google Docs sign button (fixed bottom-right, always visible) -- node --test
- [x] 3.2 Add MS Word Online sign button -- node --test
- [x] 3.3 Use Encypher brand colors (#1B2F50, #2A87C4) instead of purple -- visual
- [x] 3.4 Add toggle setting for in-editor sign button (showEditorButtons) -- node --test
- [x] 3.5 Handle text extraction + clipboard fallback for Google Docs -- node --test
- [x] 3.6 Handle text extraction + clipboard fallback for MS Word Online -- node --test

### 4.0 Tests
- [x] 4.1 Unit tests for online editor detection (14 new tests) -- node --test
- [x] 4.2 Extension tests pass: 56/56 (42 existing + 14 new) -- node --test

## Success Criteria
- Popup header shows real Encypher logo icon, readable text
- Rescan works in Google Docs
- Sign button appears in Google Docs and MS Word Online editors
- Sign button uses Encypher branding
- Sign button can be toggled off in settings
- All tests pass

## Completion Notes
- Popup header now uses real Encypher seal icon (encypher_icon_nobg_color.png) with white filter
- Editor-signer CSS rebranded from purple (#6366F1) to Encypher blue (#2A87C4/#1B2F50)
- Google Docs: detects .kix-appview-editor, extracts text from .kix-lineview accessibility layer
- MS Word Online: detects RichText contenteditable and WACViewPanel elements
- Detector scanPage() now scans extra online editor roots for embeddings
- Sign button is fixed bottom-right on Google Docs/Word Online (always visible)
- For online editors, signed text is copied to clipboard (cannot safely mutate their DOM)
- showEditorButtons setting wired to chrome.storage.onChanged for live toggle
- 56 extension tests pass (14 new for online editor detection)
