# PRD: Native Editor Plugins — Google Docs Add-on & MS Office Add-in

## Status: DESIGN SPEC (not yet implemented)
## Current Goal: Architecture and design for future implementation

## Overview
Native editor plugins provide deeper integration than the Chrome extension content script approach. They can access the editor's internal document model, handle text replacement natively, and persist across sessions without requiring the extension to be active.

## Google Docs Add-on (Apps Script)

### Architecture
- **Platform**: Google Workspace Add-on (Apps Script)
- **Runtime**: Server-side Apps Script + client-side sidebar/dialog
- **Distribution**: Google Workspace Marketplace

### Key Components

#### 1. Sidebar UI
- Branded Encypher sidebar panel (HTML + CSS)
- "Sign Document" button — signs entire document or selected text
- "Verify Document" button — scans document for embeddings
- Provenance chain display — shows signing history
- Settings: API key, default document type, auto-sign toggle

#### 2. Document Interaction (Apps Script)
```
// getText / replaceText via DocumentApp
const doc = DocumentApp.getActiveDocument();
const body = doc.getBody();
const text = body.getText();

// Replace with signed version
body.setText(signedText);

// Or replace selection only
const selection = doc.getSelection();
if (selection) {
  const elements = selection.getRangeElements();
  // Replace selected text with signed version
}
```

#### 3. API Integration
- Apps Script `UrlFetchApp.fetch()` for Encypher API calls
- API key stored in `PropertiesService.getUserProperties()`
- Sign endpoint: POST /api/v1/sign
- Verify endpoint: POST /api/v1/verify

#### 4. Triggers
- `onOpen` — add menu items ("Encypher" menu)
- `onInstall` — first-time setup wizard
- Optional: `onEdit` trigger for auto-verification (with rate limiting)

#### 5. Permissions
- `https://www.googleapis.com/auth/documents.currentonly` — access current doc
- `https://www.googleapis.com/auth/script.external_request` — API calls

### Advantages over Chrome Extension
- Direct access to DocumentApp API (no DOM scraping)
- Native text replacement (no clipboard workaround)
- Works without Chrome extension installed
- Persists in document's add-on menu
- Can handle rich text formatting preservation

### Limitations
- Apps Script execution time limits (6 min/execution)
- No real-time keystroke interception (no smart backspace)
- Requires Google account authorization
- Marketplace review process

---

## Microsoft Office Add-in (Office.js)

### Architecture
- **Platform**: Office Add-in (Office.js / React)
- **Runtime**: Web-based task pane hosted on Encypher servers
- **Distribution**: Microsoft AppSource / sideloading

### Key Components

#### 1. Task Pane UI
- React-based task pane (branded Encypher)
- Sign / Verify / Provenance panels
- Settings management
- Same UX patterns as Chrome extension popup

#### 2. Document Interaction (Office.js)
```javascript
// Word.js API
await Word.run(async (context) => {
  // Get selected text
  const selection = context.document.getSelection();
  selection.load('text');
  await context.sync();
  const text = selection.text;

  // Replace with signed version
  selection.insertText(signedText, Word.InsertLocation.replace);
  await context.sync();
});

// Get full document text
await Word.run(async (context) => {
  const body = context.document.body;
  body.load('text');
  await context.sync();
  const fullText = body.text;
});
```

#### 3. API Integration
- Standard `fetch()` from task pane to Encypher API
- API key stored in `Office.context.roamingSettings`
- CORS headers required on Encypher API for Office domain

#### 4. Manifest
```xml
<OfficeApp xmlns="http://schemas.microsoft.com/office/appforoffice/1.1" type="TaskPaneApp">
  <Id>encypher-word-addin</Id>
  <Version>1.0.0</Version>
  <ProviderName>Encypher AI</ProviderName>
  <DefaultLocale>en-US</DefaultLocale>
  <Hosts>
    <Host Name="Document" />
  </Hosts>
  <Requirements>
    <Sets>
      <Set Name="WordApi" MinVersion="1.1" />
    </Sets>
  </Requirements>
</OfficeApp>
```

#### 5. Supported Platforms
- Word for Windows (desktop)
- Word for Mac (desktop)
- Word Online (web)
- Word for iPad

### Advantages over Chrome Extension
- Native Word API access (rich text, formatting, styles)
- Works on desktop Word (not just web)
- Cross-platform (Windows, Mac, iPad, web)
- No DOM manipulation needed
- Official Microsoft distribution channel

### Limitations
- Requires hosting the task pane web app
- Office.js API has async/batch execution model
- AppSource review process (weeks)
- No keystroke interception (no smart backspace in desktop Word)

---

## Shared Backend Requirements

Both plugins need:
1. **CORS support** on Encypher API for add-in domains
2. **API key management** — per-user key storage in each platform's settings API
3. **Provenance chain** — same `previous_embeddings` field in sign API
4. **Rate limiting** — per-user rate limits for add-in API calls

## Implementation Priority
1. **Google Docs Add-on** — larger user base, simpler Apps Script platform
2. **MS Office Add-in** — broader platform reach (desktop + web + mobile)

## Estimated Effort
- Google Docs Add-on: ~2-3 weeks (Apps Script + sidebar UI + marketplace submission)
- MS Office Add-in: ~3-4 weeks (React task pane + Office.js + hosting + AppSource submission)
