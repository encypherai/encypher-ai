# Chrome Web Store Listing - Encypher Verify

## Store Listing Information

### Name
Encypher Verify

### Short Description (132 characters max)
Verify and sign Encypher and C2PA-compatible content. See trust badges for verified AI-generated and human-authored content.

### Detailed Description

**Verify Content Authenticity and Provenance**

Encypher Verify helps you identify authentic, signed content on the web. See instant verification badges on articles, social media posts, and any text content that has been signed using Encypher or the C2PA (Coalition for Content Provenance and Authenticity) standard.

**Key Features:**

- **Auto-Detection**: Automatically scans pages for Encypher and C2PA-compatible signed content
- **Verification Badges**: Shows color-coded inline badges (blue = verified, red = invalid, gray = revoked)
- **Content Signing**: Sign your own content directly from the browser (requires API key)
- **Signing Controls**: Choose embedding mode (Standard or Lightweight) and frequency (per sentence, per paragraph, etc.)
- **Context Menu**: Right-click any text and select "Verify with Encypher"
- **WYSIWYG Editor Support**: Floating sign buttons on TinyMCE, CKEditor, Quill, ProseMirror, and more
- **Keyboard Shortcut**: Press Ctrl+Shift+E to sign selected text instantly
- **Usage Tracking**: Free tier includes 1,000 signings/month with visual progress meter
- **Privacy-First**: Only sends signed content blocks for verification, never full pages
- **Offline Detection**: Detects signed content locally before verifying

**How It Works:**

1. **For Readers**: Browse the web normally. When you encounter signed content, you'll see a verification badge showing who signed it and when.

2. **For Authors**: Get an API key from dashboard.encypherai.com, configure it in the extension settings, then use the "Sign" tab to sign text before publishing. Choose Standard mode for full C2PA provenance or Lightweight for a smaller footprint. Set your preferred signing frequency in Settings so every signing surface uses the same defaults.

3. **For Publishers**: Integrate C2PA signing into your workflow to prove content authenticity and combat AI-generated misinformation.

**What is C2PA?**

C2PA (Coalition for Content Provenance and Authenticity) is an open standard developed by Adobe, Microsoft, Intel, BBC, and other industry leaders to combat misinformation by providing cryptographic proof of content origin.

**Privacy & Security:**

- Anonymous signed-content discovery analytics (always on, no personal user identifiers)
- API key stored securely in your browser
- Only signed content blocks are sent for verification
- 1-hour local verification cache (no redundant API calls)
- Open source: github.com/encypherai/encypherai-commercial

**Support:**

- Documentation: encypherai.com/docs
- Issues: github.com/encypherai/encypherai-commercial/issues
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
   - Show webpage with green verification badge
   - Caption: "Instantly verify signed content with color-coded badges"

2. **Popup Interface**
   - Show popup with verification summary
   - Caption: "Quick overview of verified content on the page"

3. **Sign Tab**
   - Show sign interface with text input
   - Caption: "Sign your own content before publishing"

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
"Trust, Verified. Combat misinformation with cryptographic proof."

### Key Benefits

1. **For Readers**: Know what's real. See instant verification of content authenticity.
2. **For Authors**: Prove your work is yours. Sign content to prevent plagiarism and AI impersonation.
3. **For Publishers**: Build trust with readers. Implement C2PA signing across your platform.

### Use Cases

- **Journalism**: Verify news articles and combat fake news
- **Academic**: Prove authorship of research and papers
- **Creative**: Protect original writing, art descriptions, and creative work
- **Legal**: Establish content provenance for legal documents
- **Marketing**: Verify brand-authorized content

## Pricing

**Free Tier**: Unlimited verification (no API key required). 1,000 content signings per month with API key. Standard and Lightweight embedding modes, all frequency levels except per-word.
**Enterprise**: Unlimited verification and signing, per-word embedding frequency, Merkle tree verification, attribution tracking. Contact sales at encypherai.com/contact.

## Support & Links

- **Website**: https://encypherai.com
- **Documentation**: https://encypherai.com/docs/chrome-extension
- **Support Email**: support@encypherai.com
- **GitHub**: https://github.com/encypherai/encypherai-commercial
- **Dashboard**: https://dashboard.encypherai.com

## Version History

### Version 1.0.0 (Initial Release)

**Features:**
- Auto-detection of Encypher and C2PA-compatible signed content
- Verification badges with signer information
- Content signing with API key
- Configurable embedding mode (Standard / Lightweight) and embedding frequency (per sentence, paragraph, etc.)
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
- 42 unit tests, E2E tested with Puppeteer
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
