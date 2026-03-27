# Encypher Verify - Chrome Extension

A browser extension that helps people verify who authored text on the web and sign their own content with invisible cryptographic watermarks that survive copy-paste.

## User Journeys

- See `USER_JOURNEYS.md` for documented end-to-end flows for:
  - Reader / Verifier (no account)
  - Publisher / Creator (onboarded signing)
  - validation matrix and test commands

## D2 Workflow Views

- [Verification flow](./docs/verification-flow.d2) — shows detector scanning, service-worker verification, cache checks, and badge state updates.
- [Inline signing flow](./docs/inline-signing-flow.d2) — shows hosted/floating editor controls, signing UI, `POST /api/v1/sign`, and DOM-safe replacement.
- [Dashboard auth handoff](../../docs/diagrams/workflows/dashboard-extension-auth-handoff.d2) — shows optional onboarding from popup/options through dashboard approval into local credential storage.

## Features

### Verification
- **Auto-Detection**: Scans pages for Encypher and C2PA-compatible content provenance embeddings using Unicode variation selectors
- **Inline Verification Status**: Shows verified authorship markers directly in page content
- **Popup Summary**: Quick overview of verified/pending/invalid content on the page
- **Context Menu**: Right-click to verify selected text
- **Caching**: Verification results are cached to avoid redundant API calls
- **Dynamic Content**: Observes DOM changes to detect newly loaded content

### Content Signing
- **Popup Signing**: Sign text directly from the extension popup (requires API key)
- **Optional Login Onboarding**: Set up a tracked free account from the popup to auto-provision an API key
- **WYSIWYG Editor Integration**: Hosted or floating sign buttons on detected text editors that open the signing UI
- **Context Menu Signing**: Right-click to sign selected text or sign & copy to clipboard
- **Keyboard Shortcut**: Alt+Shift+S to sign selected text in any editor
- **Embedding Mode**: Choose between Minimal (recommended, server-stored proof) and Embedded signing
- **Embedding Frequency**: Control how often signatures are embedded (entire content, per section, per paragraph, per sentence, or per word)
- **Advanced Options**: Document type, invisible embeddings, Merkle tree (Enterprise), attribution tracking (Enterprise)
- **Tier-Aware**: Free tier (1,000 signings/month) and Enterprise (unlimited) with usage tracking

### Supported Editors
The extension automatically detects and adds signing capabilities to:
- Generic `contenteditable` elements
- `<textarea>` elements
- TinyMCE
- CKEditor (4 & 5)
- Quill
- ProseMirror / Tiptap
- Draft.js (React)
- Medium Editor
- Froala
- Summernote

### Settings
- **API Key Management**: Securely store and test your API key
- **Setup State Tracking**: Mark extension setup as complete/not started, independent of manual API key override
- **Verification Settings**: Auto-verify, show badges
- **Signing Preferences**: Default embedding mode, embedding frequency, document type, invisible embeddings, auto-replace content
- **Advanced**: Custom API URL, cache duration

## Installation (Development)

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome-extension` directory

## Project Structure

```
chrome-extension/
├── manifest.json              # Extension manifest (Manifest V3)
├── background/
│   └── service-worker.js      # Background service worker for API calls
├── content/
│   ├── detector.js            # Content script for C2PA detection
│   ├── badge.css              # Styles for verification badges
│   ├── editor-signer.js       # WYSIWYG editor detection and signing
│   └── editor-signer.css      # Styles for editor signing UI
├── popup/
│   ├── popup.html             # Extension popup UI (Verify + Sign tabs)
│   ├── popup.css              # Popup styles
│   └── popup.js               # Popup logic
├── options/
│   ├── options.html           # Settings page
│   ├── options.css            # Settings styles
│   └── options.js             # Settings logic
├── icons/                     # Extension icons
└── tests/
    ├── detector.test.js       # Unit tests
    ├── editor-signer.test.js  # Editor signer tests
    ├── e2e/                   # Puppeteer E2E tests
    └── fixtures/              # Test HTML pages
```

## How It Works

### Detection

1. Content script (`detector.js`) scans the page for text containing Unicode variation selectors
2. Extracts embedded bytes and checks for C2PA magic header (`C2PATXT\0`)
3. When found, injects a "pending" badge and requests verification

### Verification

1. Service worker receives verification request from content script
2. Calls Encypher public verification API with the signed content
3. Returns verification result (valid/invalid/revoked)
4. Content script updates badge to reflect status

### Signing

1. User enters or selects text to sign (popup, editor button, context menu, or Alt+Shift+S)
2. A modal or form collects signing options:
   - **Embedding Mode** controls the signature format sent to the API:
     - *Minimal* (`micro_no_embed_c2pa`): keeps compact invisible markers while storing the full proof server-side. Recommended default for compatibility.
     - *Embedded* (`micro`): keeps invisible markers and embeds C2PA provenance data directly into the signed text.
   - **Embedding Frequency** controls how the text is segmented for signing (`segmentation_level`):
     - *Entire content* (`document`): one signature for the whole text.
     - *Per section / paragraph / sentence / word*: progressively finer granularity. More frequent embeddings increase resilience to partial edits but add more invisible characters.
     - Default is *Entire content*, which maximizes cross-editor compatibility.
3. Service worker sends `POST /api/v1/sign` with the selected signing options, including compact/minimal defaults and `segmentation_level` in request options
4. Signed text is inserted back into the editor (DOM-preserving when possible) or copied to clipboard

### Badge States

| State | Color | Meaning |
|-------|-------|---------|
| Verified | Azure Blue | Content signature is valid |
| Pending | Amber | Verification in progress |
| Invalid | Red | Signature verification failed |
| Revoked | Gray | Content has been revoked |
| Error | Gray | Verification error occurred |

## API Endpoints Used

### Public (No Auth Required)
- `POST /api/v1/verify` - Verify signed content (C2PA details free, Merkle proof requires API key)
- `GET /api/v1/public/verify/{ref_id}` - Verify by reference ID
- `POST /api/v1/public/verify/batch` - Batch verify embeddings
- `POST /api/v1/public/c2pa/validate-manifest` - Validate manifest structure
- `GET /api/v1/public/c2pa/trust-anchors/{signer_id}` - Lookup trust anchor

### Authenticated (API Key Required)
- `POST /api/v1/sign` - Sign content with C2PA manifest (features gated by tier via options)
- `GET /api/v1/account` - Get account info and tier

### Optional Onboarding Provisioning
- `POST /api/v1/provisioning/auto-provision` - Create a tracked free account and return a provisioned API key for extension onboarding

## Privacy

- Only signed content blocks are sent to the API (not the entire page)
- Verification results are cached locally
- Discovery analytics may be sent for signed-content detection events
- Optional onboarding setup can associate extension activity with a user-provided email for adoption metrics

## Development

### Prerequisites

- Node.js 18+
- Chrome browser

### Testing

```bash
# Run unit tests (42 tests)
npm test

# Run E2E tests with Puppeteer
npm run test:e2e
```

### Building for Chrome Web Store

Create the production package with the repo build script:

```bash
npm run build
```

This produces `dist/encypher-verify-v<version>.zip` with localhost permissions stripped from the packaged `manifest.json`.

## Configuration

The extension uses these default settings:

- **API Base URL**: `https://api.encypher.com` (configurable text field in settings)
- **Default Embedding Mode**: Minimal (`micro_no_embed_c2pa`)
- **Default Embedding Frequency**: Entire content (`document`)
- **Verification Cache TTL**: 1 hour (local browser cache)
- **Request Timeout**: 10 seconds
- **Free Tier Limit**: 1,000 signings per month

Signing defaults are persisted in `chrome.storage.sync` and pre-fill every signing surface (popup, inline modal, context menu, keyboard shortcut). Users can override per-signing from the popup or the inline editor modal.

## License

Proprietary - Encypher Corporation. All rights reserved.
