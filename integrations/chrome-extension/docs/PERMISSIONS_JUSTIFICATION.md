# Chrome Web Store Permissions Justification -- Encypher Verify v2.0.0

## Host Permissions

### `<all_urls>`
**Required for**: Fetching image, audio, and video bytes from any domain to verify C2PA provenance metadata.

Encypher Verify is a content verification tool that works on any website. To verify media provenance, the extension must:
1. Fetch image bytes (via Range requests for auto-scan, or full fetch for manual verification) from the hosting domain to inspect C2PA/JUMBF metadata embedded in the file.
2. Fetch audio and video bytes from any domain to send to the public verification API.
3. Inject content scripts that detect text-based cryptographic watermarks on any page.

Without `<all_urls>`, the extension cannot verify content on arbitrary websites, which is its core purpose.

### `http://localhost/*` and `http://127.0.0.1/*`
**Required for**: Development and testing only. Stripped from production builds before Chrome Web Store submission.

### `https://api.encypher.com/*` and `https://*.encypher.com/*`
**Required for**: Communicating with the Encypher verification and signing API endpoints.

## Permissions

### `activeTab`
**Required for**: Accessing the current tab to inject content scripts and read page content for verification scanning.

### `storage`
**Required for**: Persisting user settings (auto-scan toggle, verification preferences, signing defaults) via `chrome.storage.sync` and storing the API key securely via `chrome.storage.local`.

### `clipboardWrite`
**Required for**: The "Sign & Copy to Clipboard" context menu feature that signs selected text and copies the signed output to the clipboard.

### `contextMenus`
**Required for**: Adding right-click context menu items:
- "Verify with Encypher" (text selection)
- "Sign with Encypher" (text selection)
- "Sign & Copy to Clipboard" (text selection)
- "Verify image with Encypher" (images)
- "Verify audio with Encypher" (audio)
- "Verify video with Encypher" (video)

### `scripting`
**Required for**: Programmatically injecting toast notifications and verification result overlays into pages when triggered via the context menu or service worker.

## Content Scripts

### `detector.js`
Injected on all pages at `document_start`. Scans text nodes for C2PA/ZWC provenance markers, inventories page images and audio/video elements, runs auto-scan, and responds to verification requests from the popup and context menu.

### `editor-signer.js`
Injected on all pages at `document_start`. Detects supported text editors (Google Docs, ChatGPT, Claude, Gmail, etc.) and adds inline "Sign" buttons for content signing.

### `badge.css` and `editor-signer.css`
Styling for verification badge overlays and editor signing buttons.

### `all_frames: true` and `match_about_blank: true`
Required because many editors and media elements exist inside iframes (e.g., Gmail compose, LinkedIn post editor, embedded video players).

## Web Accessible Resources

### `icons/*`, `content/badge.css`, `content/editor-signer.css`
Required for displaying extension icons and styling within page content (badge overlays, editor buttons).
