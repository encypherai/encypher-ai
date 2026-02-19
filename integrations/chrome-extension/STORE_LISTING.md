# Chrome Web Store Listing - Encypher Verify

## Store Listing Information

### Name
Encypher Verify

### Short Description (132 characters max)
Verify who authored any text on the web. Sign your own content with invisible cryptographic watermarks that survive copy-paste.

### Detailed Description

**Verify Authorship. Sign with Invisible Proof.**

Encypher Verify helps you see who authored text across the web and confirm proof of origin instantly. It surfaces verified authorship inline on articles, social posts, and other text content while letting you sign your own writing with invisible cryptographic watermarks.

**Key Features:**

- **Auto-Detection**: Automatically scans pages for embedded proof-of-origin markers
- **Inline Verification Status**: Shows color-coded verified authorship status inline (blue = verified, red = invalid, gray = revoked)
- **Content Signing**: Sign your own content directly from the browser (requires API key)
- **Signing Controls**: Choose proof mode (embedded or compact) and frequency (per sentence, per paragraph, etc.)
- **Context Menu**: Right-click any text and select "Verify with Encypher"
- **WYSIWYG Editor Support**: Floating sign buttons on TinyMCE, CKEditor, Quill, ProseMirror, and more
- **Keyboard Shortcut**: Press Ctrl+Shift+E to sign selected text instantly
- **Usage Tracking**: Free tier includes 1,000 signings/month with visual progress meter
- **Privacy-First**: Only sends candidate text blocks for verification, never full pages
- **Offline Detection**: Detects embedded proof locally before verifying

**How It Works:**

1. **For Readers**: Browse normally. When proof is present, you see verified authorship inline with signer and timestamp details.

2. **For Authors**: Get an API key from dashboard.encypherai.com, configure it in settings, then use the Sign tab to add invisible cryptographic watermarks before publishing. Choose embedded proof for portability or compact proof for a smaller payload. Set your preferred signing frequency once and reuse it everywhere.

3. **For Publishers**: Add proof of origin to your editorial workflow so every update can be traced, verified, and audited.

**Why this is different**

Encypher embeds proof directly in text with invisible cryptographic watermarks that survive copy-paste and normal distribution workflows.

**Privacy & Security:**

- Anonymous signed-content discovery analytics (always on, no personal user identifiers)
- API key stored securely in your browser
- Only candidate text blocks are sent for verification
- 1-hour local verification cache (no redundant API calls)

**Support:**

- Documentation: encypherai.com/docs
- Email: support@encypherai.com

### Category
**Primary**: Productivity
**Secondary**: Developer Tools

### Language
English

### Privacy Policy URL
https://encypherai.com/privacy

(Or include PRIVACY.md content directly if required)

## Visual Assets

### Extension Icon (Required Sizes)

- **16x16**: `icons/icon16.png` [ready]
- **32x32**: `icons/icon32.png` [ready]
- **48x48**: `icons/icon48.png` [ready]
- **128x128**: `icons/icon128.png` [ready]

### Promotional Images (Required)

#### Small Promo Tile (440x280)
**Description**: Extension icon with "Encypher Verify" text
**File**: `store-assets/promo-small-440x280.png`
**Status**: Ready

#### Large Promo Tile (920x680)
**Description**: Screenshot of extension in action with verification badges
**File**: `store-assets/promo-large-920x680.png`
**Status**: Ready

#### Marquee Promo Tile (1400x560)
**Description**: Hero image showing verification workflow
**File**: `store-assets/promo-marquee-1400x560.png`
**Status**: Ready

### Screenshots (Required: 1-5 screenshots, 1280x800 or 640x400)

1. **Verification in Action**
   - Show webpage with verified authorship marker
   - Caption: "Instantly verify who authored text with inline proof of origin"

2. **Popup Interface**
   - Show popup with verification summary
   - Caption: "Quick overview of verified content on the page"

3. **Sign Tab**
   - Show sign interface with text input
   - Caption: "Sign your own content with invisible cryptographic watermarks"

4. **Options Page**
   - Show settings with API key configuration
   - Caption: "Configure API key and verification preferences"

5. **Context Menu**
   - Show right-click menu with "Verify with Encypher"
   - Caption: "Verify any selected text with a right-click"

**Files**:
- `store-assets/screenshot-1-verification-badges.png`
- `store-assets/screenshot-2-popup-interface.png`
- `store-assets/screenshot-3-options-page.png`

**Status**: Ready (3 screenshots captured)

## Promotional Copy

### Tagline
"Verify who authored any text on the web. Sign your own content with invisible cryptographic watermarks that survive copy-paste."

### Key Benefits

1. **For Readers**: Verify who authored any text in seconds.
2. **For Authors**: Sign your own content with invisible proof that survives copy-paste.
3. **For Publishers**: Deploy sentence-level verification across editorial workflows.

### Use Cases

- **Journalism**: Verify news articles and combat fake news
- **Academic**: Prove authorship of research and papers
- **Creative**: Protect original writing, art descriptions, and creative work
- **Legal**: Establish content provenance for legal documents
- **Marketing**: Verify brand-authorized content

## Pricing

**Free Tier**: Unlimited verification (no API key required). 1,000 content signings per month with API key. Embedded and compact proof modes, all frequency levels except per-word.
**Enterprise**: Unlimited verification and signing, per-word embedding frequency, Merkle tree verification, attribution tracking. Contact sales at encypherai.com/contact.

## Support & Links

- **Website**: https://encypherai.com
- **Documentation**: https://encypherai.com/docs/chrome-extension
- **Support Email**: support@encypherai.com
- **Dashboard**: https://dashboard.encypherai.com

## Version History

### Version 1.0.0 (Initial Release)

**Features:**
- Auto-detection of embedded proof-of-origin markers
- Inline verified authorship status with signer information
- Content signing with API key
- Configurable proof mode (Embedded / Compact) and embedding frequency (per sentence, paragraph, etc.)
- Context menu verification and signing
- Keyboard shortcut signing (Ctrl+Shift+E)
- WYSIWYG editor integration with floating sign buttons
- Options page for configuration
- Privacy-first design (no tracking)

**Technical:**
- Manifest V3
- Service worker architecture
- Secure API key storage
- 1-hour local verification cache
- 156 unit tests, E2E tested with Puppeteer
- Brand-consistent SVG icons (no emojis)
- Free/Enterprise tier support with usage tracking

## Submission Checklist

### Required Items

- [x] Extension package (.zip)
- [x] Detailed description
- [x] Privacy policy
- [x] Small promo tile (440x280)
- [x] Screenshots (1280x800, 3 captured)
- [x] Category selection
- [x] Support email

### Optional Items

- [x] Large promo tile (920x680)
- [x] Marquee promo tile (1400x560)
- [ ] Video demo (YouTube link)
- [ ] Additional screenshots

### Pre-Submission Testing

- [x] Test on clean Chrome profile
- [x] Verify all permissions are necessary
- [x] Test signing flow end-to-end
- [x] Test verification on multiple sites
- [x] Check all links in description
- [x] Spell check all copy

## Post-Launch

### Marketing

- [ ] Announce on Twitter/X
- [ ] Blog post on encypherai.com
- [ ] Submit to Product Hunt
- [ ] Share in C2PA community
- [ ] Email existing users

### Monitoring

- [ ] Set up Chrome Web Store analytics
- [ ] Monitor user reviews
- [ ] Track installation metrics
- [ ] Collect user feedback

### Iteration

- [ ] Plan v1.1 features based on feedback
- [ ] Address any reported bugs
- [ ] Improve based on user requests
