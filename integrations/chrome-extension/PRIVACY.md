# Privacy Policy - Encypher C2PA Verifier

**Last Updated:** February 13, 2026

## Overview

The Encypher C2PA Verifier is a browser extension that helps you verify the authenticity of content on the web. We are committed to protecting your privacy and being transparent about what data we collect and how we use it.

## What We Collect

### Data Collected Locally (Never Sent to Servers)

- **Extension Settings**: Your preferences (auto-verify, show badges, API base URL)
- **API Key**: Stored locally in your browser's secure storage (never transmitted except to the API you configure)
- **Verification Cache**: Temporary cache of verification results (cleared after 1 hour)

### Data Sent to Encypher API (Only When Verifying Content)

When you verify content (either automatically or manually), we send:

- **Signed Content Block**: Only the specific text block containing the C2PA signature
- **No Full Page Content**: We never send the entire webpage
- **No Browsing History**: We don't track which pages you visit
- **No Personal Information**: We don't collect names, emails, or other personal data

### Content Discovery Tracking (Always Active)

When the extension verifies signed content on a page, we report a **discovery event** to the Encypher analytics service. This is a core product feature that cannot be disabled. It allows content owners (organizations that signed the content) to see where their content appears across the web.

Each discovery event includes:

- **Page URL and domain**: Where the signed content was found
- **Page title**: The title of the page containing the content
- **Signer information**: The organization that originally signed the content (extracted from the signature, not from you)
- **Verification result**: Whether the content was verified, invalid, or revoked
- **Anonymized session ID**: A random, ephemeral identifier that resets each browser session. This is NOT tied to your identity, account, or browsing history.

What discovery tracking does NOT collect:

- Your name, email, or any personal information
- Your browsing history or pages without signed content
- Your IP address is not stored (used only for rate limiting)
- Any information that could identify you as an individual

### Data Sent When Signing Content

When you use the "Sign" feature with your API key:

- **Text to Sign**: The text you explicitly choose to sign
- **Optional Title**: If you provide one
- **API Key**: Sent securely via HTTPS to authenticate your request

## What We Don't Collect

- Browsing history
- Full page content
- Personal information (name, email, etc.)
- Location data
- Device information
- Cookies or tracking pixels

## How We Use Data

### Verification

- Verification requests are sent to the Encypher API to check if content signatures are valid
- Results are cached locally for 1 hour to avoid redundant requests
- No verification data is stored permanently on our servers

### Signing

- When you sign content, it's processed by the Encypher API and returned to you
- Signed content metadata (document ID, timestamp) may be stored for audit purposes
- Your API key is used only to authenticate your requests

## Data Storage

### Local Storage (In Your Browser)

- Extension settings
- API key (encrypted by Chrome's storage API)
- Temporary verification cache (1 hour TTL)

### Server Storage (Encypher API)

- Signed content metadata (document ID, signer ID, timestamp)
- API usage logs (for rate limiting and billing)
- No personal information unless you explicitly include it in signed content

## Third-Party Services

### Encypher API

- **Purpose**: Content verification and signing
- **Data Shared**: Signed content blocks, API key for authentication
- **Privacy Policy**: https://encypherai.com/privacy

### No Other Third Parties

We do not share data with any other third-party services, analytics providers, or advertisers.

## Your Rights

### Access and Control

- **View Settings**: Open extension options to see your configuration
- **Delete API Key**: Remove your API key at any time via settings
- **Clear Cache**: Clear verification cache via settings
- **Uninstall**: Removing the extension deletes all local data

### Data Deletion

- **Local Data**: Automatically deleted when you uninstall the extension
- **Server Data**: Contact support@encypherai.com to request deletion of signed content metadata

## Security

### How We Protect Your Data

- **HTTPS Only**: All API communication uses encrypted HTTPS
- **Secure Storage**: API keys stored using Chrome's secure storage API
- **Discovery Tracking Only**: We only track where signed content is found (not your browsing history). No cookies or tracking scripts.
- **Minimal Permissions**: Extension requests only necessary permissions

### API Key Security

- Stored locally in Chrome's encrypted storage
- Never logged or transmitted to third parties
- Only sent to the API endpoint you configure
- You can delete it at any time

## Children's Privacy

This extension is not intended for children under 13. We do not knowingly collect data from children.

## Changes to This Policy

We may update this privacy policy from time to time. Changes will be reflected in the "Last Updated" date above. Continued use of the extension after changes constitutes acceptance of the updated policy.

## Contact Us

If you have questions about this privacy policy or our data practices:

- **Email**: support@encypherai.com
- **Website**: https://encypherai.com/privacy
- **GitHub Issues**: https://github.com/encypherai/encypherai-commercial/issues

## Open Source

This extension is open source. You can review the code to verify our privacy claims:

- **Repository**: https://github.com/encypherai/encypherai-commercial
- **Extension Code**: `/integrations/chrome-extension/`

## Summary

**What we collect:** Signed content blocks you verify, text you sign, and anonymous discovery events (page URL + signer info) when signed content is found.

**What we don't collect:** Browsing history, full page content, personal information, or any data that identifies you.

**Why discovery tracking:** It lets content owners know where their signed content appears across the web, helping detect unauthorized copying.

**Your control:** You can delete your API key, clear cache, and uninstall at any time to remove all local data. Discovery events are fully anonymized and cannot be traced back to you.
