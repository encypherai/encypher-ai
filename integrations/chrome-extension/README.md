# Encypher C2PA Verifier - Chrome Extension

A browser extension that automatically detects and verifies C2PA-signed content on any webpage, displaying trust badges for verified content. Also supports signing content directly from the browser and inline signing in WYSIWYG editors.

## Features

### Verification
- **Auto-Detection**: Scans pages for C2PA and Encypher text embeddings using Unicode variation selectors
- **Verification Badges**: Shows inline badges on verified content blocks
- **Popup Summary**: Quick overview of verified/pending/invalid content on the page
- **Context Menu**: Right-click to verify selected text
- **Caching**: Verification results are cached to avoid redundant API calls
- **Dynamic Content**: Observes DOM changes to detect newly loaded content

### Content Signing
- **Popup Signing**: Sign text directly from the extension popup (requires API key)
- **WYSIWYG Editor Integration**: Floating sign buttons on detected text editors
- **Context Menu Signing**: Right-click to sign selected text or sign & copy to clipboard
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
- **Verification Settings**: Auto-verify, show badges
- **Signing Preferences**: Default document type, invisible embeddings, auto-replace content
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

## Privacy

- Only signed content blocks are sent to the API (not the entire page)
- Verification results are cached locally
- No user tracking or analytics

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

The extension uses no build step — source files are submitted directly. Create a zip of the extension directory (excluding `node_modules/`, `tests/`, and markdown files):

```bash
zip -r encypher-c2pa-verifier.zip . -x 'node_modules/*' 'tests/*' '*.md' 'package*.json'
```

## Configuration

The extension uses these default settings:

- **API Base URL**: `https://api.encypherai.com` (configurable text field in settings)
- **Verification Cache TTL**: 1 hour (local browser cache)
- **Request Timeout**: 10 seconds
- **Free Tier Limit**: 1,000 signings per month

## License

Proprietary - Encypher Corporation. All rights reserved.
