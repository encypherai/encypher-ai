# Encypher C2PA Verifier - Chrome Extension

A browser extension that automatically detects and verifies C2PA-signed content on any webpage, displaying trust badges for verified content. Also supports signing content directly from the browser.

## Features

- **Auto-Detection**: Scans pages for C2PA and Encypher text embeddings using Unicode variation selectors
- **Verification Badges**: Shows inline badges on verified content blocks
- **Popup Summary**: Quick overview of verified/pending/invalid content on the page
- **Content Signing**: Sign text directly from the extension popup (requires API key)
- **Options Page**: Configure API key, base URL, and verification settings
- **Caching**: Verification results are cached to avoid redundant API calls
- **Dynamic Content**: Observes DOM changes to detect newly loaded content

## Installation (Development)

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome-extension` directory

## Project Structure

```
chrome-extension/
├── manifest.json           # Extension manifest (Manifest V3)
├── background/
│   └── service-worker.js   # Background service worker for API calls
├── content/
│   ├── detector.js         # Content script for C2PA detection
│   └── badge.css           # Styles for verification badges
├── popup/
│   ├── popup.html          # Extension popup UI (Verify + Sign tabs)
│   ├── popup.css           # Popup styles
│   └── popup.js            # Popup logic
├── options/
│   ├── options.html        # Settings page
│   ├── options.css         # Settings styles
│   └── options.js          # Settings logic
├── icons/                  # Extension icons
└── tests/
    ├── detector.test.js    # Unit tests
    ├── e2e/                # Puppeteer E2E tests
    └── fixtures/           # Test HTML pages
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
| Verified | Green ✓ | Content signature is valid |
| Pending | Yellow ⋯ | Verification in progress |
| Invalid | Red ✗ | Signature verification failed |
| Revoked | Purple ⊘ | Content has been revoked |
| Error | Gray ! | Verification error occurred |

## API Endpoints Used

- `POST /api/v1/public/verify` - Public verification endpoint (no auth required)

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
# Run unit tests
npm test

# Run E2E tests with Puppeteer
npm run test:e2e
```

### Building for Production

```bash
npm run build
```

This creates a `dist/` folder ready for Chrome Web Store submission.

## Configuration

The extension uses these default settings:

- **API Base URL**: `https://api.encypherai.com`
- **Cache TTL**: 5 minutes
- **Request Timeout**: 10 seconds

## License

Proprietary - Encypher Corporation. All rights reserved.
