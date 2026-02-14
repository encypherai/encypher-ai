# TEAM_192 - Chrome Extension UX Fix + Online Editor Signing

## Status: COMPLETE

## Summary
Fix popup header branding regression, fix Rescan in Google Docs, and add in-place signing for online editors (Google Docs, MS Word Online) with a branded Encypher sign button.

## Key Issues
1. Popup header uses generic SVG checkmark instead of real Encypher logo — unreadable gradient
2. Rescan doesn't work in Google Docs (DOM structure differs from normal pages)
3. No in-place signing support for Google Docs or Microsoft Word Online

## Changes Made

### Popup Header Fix
- Replaced generic SVG checkmark circle with real Encypher seal icon (`encypher_icon_nobg_color.png`)
- Applied `filter: brightness(0) invert(1)` to make dark icon white on gradient background
- Increased title font-weight to 700 and font-size to 16px for readability

### Editor-Signer Rebranding
- Replaced all purple/indigo colors (`#6366F1`/`#4F46E5`/`#4338CA`) with Encypher brand colors (`#2A87C4`/`#1B2F50`)
- Affects: sign button, signing UI modal, notification toasts, focus rings, checkboxes

### Google Docs Support
- `detectOnlinePlatform()`: detects `docs.google.com/document/` URLs
- `getOnlineEditorElement()`: finds `.kix-appview-editor` or `.kix-page-content-wrapper`
- `detectEditorType()`: recognizes Google Docs elements
- `getEditorText()`: extracts text from `.kix-lineview` accessibility layer spans
- `setEditorText()`: copies signed text to clipboard (cannot safely mutate Google Docs DOM)
- `_getOnlineEditorRoots()` in detector.js: scans Google Docs accessibility layer for embeddings on Rescan

### MS Word Online Support
- Detects `word.live.com`, `*.officeapps.live.com`, SharePoint Doc.aspx URLs
- Finds `[data-content-type="RichText"][contenteditable="true"]` or `.WACViewPanel_EditingElement`
- Text extraction via `innerText`, clipboard fallback for setting text

### Sign Button UX
- On Google Docs / MS Word Online: button is fixed bottom-right, always visible
- On regular editors: button appears on focus, hides on blur (existing behavior)
- `showEditorButtons` setting wired to `chrome.storage.onChanged` for live toggle
- Settings loaded on init; buttons removed when disabled

## Test Results
- **Extension tests**: 56/56 pass (42 existing + 14 new for online editor detection)
- New test suites: Online Platform Detection, Google Docs Editor Detection, MS Word Online Editor Detection, Google Docs Text Extraction, Online Editor Set Text (Clipboard Fallback)

## Files Changed
- `popup/popup.html` — Replace SVG checkmark with real Encypher icon PNG
- `popup/popup.css` — Update logo icon styles (white filter, readable title)
- `content/editor-signer.js` — Add Google Docs + MS Word Online detection, text extraction, clipboard fallback, settings toggle, always-visible button for online editors
- `content/editor-signer.css` — Rebrand from purple to Encypher blue (#2A87C4/#1B2F50)
- `content/detector.js` — Add `_getOnlineEditorRoots()` for scanning Google Docs/Word Online accessibility layers on Rescan
- `tests/editor-signer.test.js` — Add 14 new tests for online editor detection
- `PRDs/CURRENT/PRD_Chrome_Extension_UX_Editor_Signing.md` — NEW PRD (complete)

## Suggested Git Commit Message
```
feat(extension): fix popup branding + add Google Docs/Word Online signing

- Replace generic SVG checkmark with real Encypher seal icon in popup header
- Rebrand editor-signer UI from purple to Encypher blue (#2A87C4/#1B2F50)
- Add Google Docs detection via .kix-appview-editor accessibility layer
- Add MS Word Online detection via RichText contenteditable / WACViewPanel
- Fix Rescan in Google Docs by scanning extra online editor DOM roots
- Add always-visible fixed sign button for online editors (bottom-right)
- Copy signed text to clipboard for online editors (cannot mutate their DOM)
- Wire showEditorButtons setting to chrome.storage.onChanged for live toggle
- Add 14 new tests for online editor detection (56/56 total)
```
