#!/usr/bin/env node
/**
 * Generate Chrome Web Store promotional images and screenshots.
 * Uses Puppeteer to render HTML templates and capture them as PNGs.
 *
 * Usage: node scripts/generate-store-assets.js
 * Output: store-assets/ directory
 */

import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT_DIR = path.join(__dirname, '..', 'store-assets');

// Brand colors
const DEEP_NAVY = '#1B2F50';
const AZURE_BLUE = '#2A87C4';
const LIGHT_SKY = '#B7D5ED';
const CYBER_TEAL = '#00CED1';
const NEUTRAL_GRAY = '#A7AFBC';

// Load real brand assets from marketing-site/public
const MARKETING_PUBLIC = path.join(__dirname, '..', '..', '..', 'apps', 'marketing-site', 'public');

const LOGO_COLOR_PNG_B64 = fs.readFileSync(path.join(MARKETING_PUBLIC, 'assets', 'logo.png')).toString('base64');
const LOGO_WHITE_PNG_B64 = fs.readFileSync(path.join(MARKETING_PUBLIC, 'encypher_full_logo_white.png')).toString('base64');
const CHECK_WHITE_SVG = fs.readFileSync(path.join(MARKETING_PUBLIC, 'encypher_check_white.svg'), 'utf-8');

const LOGO_COLOR_PNG_URI = `data:image/png;base64,${LOGO_COLOR_PNG_B64}`;
const LOGO_WHITE_PNG_URI = `data:image/png;base64,${LOGO_WHITE_PNG_B64}`;

// Clean SVGs for inline embedding (strip XML declaration and Inkscape metadata)
function cleanSvg(raw) {
  return raw
    .replace(/<\?xml[^?]*\?>\s*/g, '')
    .replace(/<!--[\s\S]*?-->\s*/g, '')
    .replace(/\s*xmlns:inkscape="[^"]*"/g, '')
    .replace(/\s*xmlns:sodipodi="[^"]*"/g, '')
    .replace(/\s*inkscape:[a-z-]+="[^"]*"/g, '')
    .replace(/\s*sodipodi:[a-z-]+="[^"]*"/g, '')
    .replace(/<sodipodi:namedview[\s\S]*?\/>\s*/g, '');
}

const CHECK_WHITE_INLINE = cleanSvg(CHECK_WHITE_SVG);

// Shared CSS
const BASE_CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;800;900&family=Roboto:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
`;

// ─── Article Page (for screenshot 1) ───
function articlePageHTML() {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><style>
${BASE_CSS}
body {
  background: #f8f9fa;
  font-family: 'Inter', sans-serif;
  color: ${DEEP_NAVY};
}
.chrome-bar {
  background: #dee1e6;
  height: 72px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 8px;
}
.chrome-dots {
  display: flex; gap: 6px; margin-right: 12px;
}
.chrome-dots span {
  width: 12px; height: 12px; border-radius: 50%;
}
.chrome-dots .red { background: #ff5f57; }
.chrome-dots .yellow { background: #ffbd2e; }
.chrome-dots .green { background: #28c840; }
.chrome-url-bar {
  flex: 1;
  background: white;
  border-radius: 20px;
  height: 36px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  font-size: 13px;
  color: #5f6368;
  font-family: 'Roboto', sans-serif;
}
.chrome-url-bar .lock {
  color: #188038;
  margin-right: 8px;
  font-size: 14px;
}
.ext-icon {
  width: 28px; height: 28px; border-radius: 4px;
  background: linear-gradient(135deg, ${DEEP_NAVY}, ${AZURE_BLUE});
  display: flex; align-items: center; justify-content: center;
  margin-left: 8px;
  position: relative;
}
.ext-icon svg { width: 18px; height: 18px; color: white; }
.ext-badge {
  position: absolute; top: -4px; right: -6px;
  background: ${AZURE_BLUE};
  color: white;
  font-size: 8px;
  font-weight: 700;
  padding: 1px 4px;
  border-radius: 4px;
  font-family: 'Roboto', sans-serif;
}
.article-container {
  max-width: 720px;
  margin: 0 auto;
  padding: 48px 32px 64px;
}
.masthead {
  text-align: center;
  border-bottom: 3px double ${DEEP_NAVY};
  padding-bottom: 16px;
  margin-bottom: 32px;
}
.masthead-name {
  font-family: 'Playfair Display', serif;
  font-weight: 900;
  font-size: 42px;
  letter-spacing: 2px;
  color: ${DEEP_NAVY};
  text-transform: uppercase;
}
.masthead-tagline {
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: ${NEUTRAL_GRAY};
  margin-top: 4px;
}
.masthead-date {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  color: ${NEUTRAL_GRAY};
  margin-top: 8px;
  border-top: 1px solid #e0e0e0;
  padding-top: 8px;
}
.article-category {
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: ${AZURE_BLUE};
  margin-bottom: 12px;
}
h1 {
  font-family: 'Playfair Display', serif;
  font-weight: 800;
  font-size: 36px;
  line-height: 1.2;
  color: ${DEEP_NAVY};
  margin-bottom: 16px;
}
.article-meta {
  font-size: 13px;
  color: ${NEUTRAL_GRAY};
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.article-meta .author {
  font-weight: 600;
  color: ${DEEP_NAVY};
}
.article-body p {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  line-height: 1.75;
  color: #374151;
  margin-bottom: 20px;
  overflow: visible;
}
.article-body {
  overflow: visible;
}
.article-body p:first-child::first-letter {
  font-family: 'Playfair Display', serif;
  font-size: 56px;
  font-weight: 700;
  float: left;
  line-height: 1;
  margin-right: 8px;
  margin-top: 4px;
  color: ${DEEP_NAVY};
}
/* Verification badge */
.encypher-badge-inline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, ${LIGHT_SKY}, ${AZURE_BLUE});
  box-shadow: 0 1px 4px rgba(27,47,80,0.2);
  vertical-align: middle;
  margin-left: 6px;
  cursor: pointer;
  position: relative;
  overflow: visible;
  z-index: 50;
}
.encypher-badge-inline svg {
  width: 13px; height: 13px; color: white;
}
/* Standalone tooltip — fixed position, not nested in inline elements */
.floating-tooltip {
  position: fixed;
  background: ${DEEP_NAVY};
  color: white;
  padding: 10px 14px;
  border-radius: 8px;
  font-family: 'Roboto', sans-serif;
  font-size: 12px;
  white-space: nowrap;
  box-shadow: 0 4px 16px rgba(27,47,80,0.3);
  z-index: 9999;
}
.floating-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: ${DEEP_NAVY};
}
.floating-tooltip .tt-status {
  color: ${CYBER_TEAL};
  font-weight: 700;
  margin-bottom: 2px;
}
.floating-tooltip .tt-signer {
  color: ${LIGHT_SKY};
}
</style></head><body>
<div class="chrome-bar">
  <div class="chrome-dots"><span class="red"></span><span class="yellow"></span><span class="green"></span></div>
  <div class="chrome-url-bar">
    <span class="lock">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
    </span>
    encyphertimes.com/ai-content-authenticity
  </div>
  <div class="ext-icon">
    <span style="display:inline-flex;align-items:center;height:18px;width:18px;">${CHECK_WHITE_INLINE.replace(/<svg/, '<svg style="height:18px;width:18px;"')}</span>
    <span class="ext-badge">OK</span>
  </div>
</div>
<div class="article-container">
  <div class="masthead">
    <div class="masthead-name">The Encypher Times</div>
    <div class="masthead-tagline">Trusted journalism, cryptographically verified</div>
    <div class="masthead-date">Thursday, February 13, 2026 &nbsp;&bull;&nbsp; Vol. I, No. 1</div>
  </div>
  <div class="article-category">Technology</div>
  <h1>The Rise of Content Authenticity: How C2PA Is Changing Digital Trust</h1>
  <div class="article-meta">
    <span class="author">By Sarah Chen</span>
    <span>&bull;</span>
    <span>6 min read</span>
    <span>&bull;</span>
    <span>February 13, 2026</span>
  </div>
  <div class="article-body">
    <p>In an era where AI-generated content is becoming indistinguishable from human writing, the need for verifiable content provenance has never been more urgent. The Coalition for Content Provenance and Authenticity (C2PA) standard, backed by Adobe, Microsoft, and the BBC, offers a cryptographic solution that is rapidly gaining adoption across newsrooms and publishing platforms worldwide.<span class="encypher-badge-inline" id="badge1"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span></p>
    <p>Publishers who adopt C2PA signing give their readers a simple visual signal: a verification badge that confirms the content was authored by the claimed source and has not been tampered with since publication. This is not just about combating misinformation &mdash; it is about building a foundation of trust in the digital information ecosystem.<span class="encypher-badge-inline"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span></p>
    <p>Early adopters report that readers engage more deeply with verified content, spending an average of 23% more time on articles that display provenance badges. The technology works silently in the background, embedding cryptographic signatures using Unicode variation selectors that are invisible to the naked eye.</p>
  </div>
</div>
</body></html>`;
}

// ─── Popup Screenshot (for screenshot 2) ───
function popupScreenshotHTML() {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><style>
${BASE_CSS}
body {
  background: #e8eaed;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  font-family: 'Roboto', sans-serif;
}
.popup-frame {
  width: 360px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.15), 0 2px 8px rgba(0,0,0,0.08);
  overflow: hidden;
}
.popup-header {
  background: linear-gradient(135deg, ${DEEP_NAVY}, #243d66);
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.popup-logo { height: 22px; color: white; }
.popup-logo img { height: 22px; width: auto; }
.popup-title {
  color: white;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.popup-tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
}
.popup-tab {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  font-size: 13px;
  font-weight: 500;
  color: ${NEUTRAL_GRAY};
  cursor: pointer;
}
.popup-tab.active {
  color: ${AZURE_BLUE};
  border-bottom: 2px solid ${AZURE_BLUE};
  font-weight: 600;
}
.popup-content { padding: 20px; }
.popup-stat-row {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}
.popup-stat {
  flex: 1;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}
.popup-stat-num {
  font-size: 24px;
  font-weight: 700;
  color: ${DEEP_NAVY};
}
.popup-stat-label {
  font-size: 11px;
  color: ${NEUTRAL_GRAY};
  margin-top: 2px;
}
.popup-stat.verified .popup-stat-num { color: ${AZURE_BLUE}; }
.popup-stat.pending .popup-stat-num { color: #f59e0b; }
.popup-detail-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
}
.popup-detail-icon {
  width: 28px; height: 28px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.popup-detail-icon.verified {
  background: ${AZURE_BLUE}15;
  color: ${AZURE_BLUE};
}
.popup-detail-icon svg { width: 14px; height: 14px; }
.popup-detail-signer {
  font-size: 13px;
  font-weight: 500;
  color: ${DEEP_NAVY};
}
.popup-detail-date {
  font-size: 11px;
  color: ${NEUTRAL_GRAY};
}
.popup-btn {
  display: block;
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 16px;
}
.popup-btn-primary {
  background: ${AZURE_BLUE};
  color: white;
}
.usage-section { margin-top: 16px; }
.usage-label {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: ${NEUTRAL_GRAY};
  margin-bottom: 6px;
}
.usage-bar {
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}
.usage-fill {
  height: 100%;
  width: 12%;
  background: linear-gradient(90deg, ${AZURE_BLUE}, ${CYBER_TEAL});
  border-radius: 3px;
}
/* Caption */
.caption {
  text-align: center;
  margin-top: 24px;
  font-size: 16px;
  font-weight: 500;
  color: ${DEEP_NAVY};
  font-family: 'Inter', sans-serif;
}
</style></head><body>
<div>
<div class="popup-frame">
  <div class="popup-header">
    <div class="popup-logo"><img src="${LOGO_WHITE_PNG_URI}" style="height:22px;width:auto;" /></div>
  </div>
  <div class="popup-tabs">
    <div class="popup-tab active">Verify</div>
    <div class="popup-tab">Sign</div>
  </div>
  <div class="popup-content">
    <div class="popup-stat-row">
      <div class="popup-stat verified">
        <div class="popup-stat-num">3</div>
        <div class="popup-stat-label">Verified</div>
      </div>
      <div class="popup-stat pending">
        <div class="popup-stat-num">1</div>
        <div class="popup-stat-label">Pending</div>
      </div>
      <div class="popup-stat">
        <div class="popup-stat-num">0</div>
        <div class="popup-stat-label">Invalid</div>
      </div>
    </div>
    <div class="popup-detail-item">
      <div class="popup-detail-icon verified">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      </div>
      <div>
        <div class="popup-detail-signer">The Encypher Times</div>
        <div class="popup-detail-date">Feb 13, 2026 &bull; C2PA Text Manifest</div>
      </div>
    </div>
    <div class="popup-detail-item">
      <div class="popup-detail-icon verified">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      </div>
      <div>
        <div class="popup-detail-signer">Reuters News Agency</div>
        <div class="popup-detail-date">Feb 12, 2026 &bull; Encypher Format</div>
      </div>
    </div>
    <div class="popup-detail-item">
      <div class="popup-detail-icon verified">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      </div>
      <div>
        <div class="popup-detail-signer">Associated Press</div>
        <div class="popup-detail-date">Feb 11, 2026 &bull; C2PA Text Manifest</div>
      </div>
    </div>
    <button class="popup-btn popup-btn-primary">Rescan Page</button>
    <div class="usage-section">
      <div class="usage-label">
        <span>Free tier: 120 / 1,000 signings</span>
        <span>12%</span>
      </div>
      <div class="usage-bar"><div class="usage-fill"></div></div>
    </div>
  </div>
</div>
<div class="caption">Quick overview of verified content on the page</div>
</div>
</body></html>`;
}

// ─── Options Page Screenshot (for screenshot 3) ───
function optionsScreenshotHTML() {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><style>
${BASE_CSS}
body {
  background: #f8f9fa;
  font-family: 'Roboto', sans-serif;
  color: ${DEEP_NAVY};
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
}
.options-frame {
  width: 560px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.1);
  padding: 32px;
}
.options-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
}
.options-logo { width: 32px; height: 32px; color: ${DEEP_NAVY}; }
.options-title {
  font-size: 20px;
  font-weight: 700;
  color: ${DEEP_NAVY};
}
.options-section {
  margin-bottom: 24px;
}
.options-section h2 {
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: ${NEUTRAL_GRAY};
  margin-bottom: 12px;
}
.options-field {
  margin-bottom: 16px;
}
.options-field label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
  color: ${DEEP_NAVY};
}
.options-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 13px;
  font-family: 'Roboto', sans-serif;
  color: ${DEEP_NAVY};
  background: white;
}
.options-input:focus {
  outline: none;
  border-color: ${AZURE_BLUE};
  box-shadow: 0 0 0 3px ${AZURE_BLUE}20;
}
.options-hint {
  font-size: 11px;
  color: #22c55e;
  margin-top: 4px;
  font-weight: 500;
}
.options-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
}
.options-row-label {
  font-size: 13px;
  font-weight: 500;
}
.options-toggle {
  width: 40px; height: 22px;
  background: ${AZURE_BLUE};
  border-radius: 11px;
  position: relative;
}
.options-toggle::after {
  content: '';
  position: absolute;
  width: 18px; height: 18px;
  background: white;
  border-radius: 50%;
  top: 2px; right: 2px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.options-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  background: linear-gradient(135deg, ${AZURE_BLUE}, ${DEEP_NAVY});
  color: white;
}
.caption {
  text-align: center;
  margin-top: 24px;
  font-size: 16px;
  font-weight: 500;
  color: ${DEEP_NAVY};
  font-family: 'Inter', sans-serif;
}
</style></head><body>
<div>
<div class="options-frame">
  <div class="options-header">
    <div class="options-logo"><img src="${LOGO_COLOR_PNG_URI}" style="height:26px;width:auto;" /></div>
  </div>
  <div class="options-section">
    <h2>API Key</h2>
    <div class="options-field">
      <label>Enterprise API Key</label>
      <div style="display:flex;gap:8px">
        <input class="options-input" type="password" value="enc_live_sk_7f3a9b2c..." style="flex:1" readonly>
        <button class="options-btn" style="padding:10px 16px;font-size:12px">Save</button>
      </div>
      <div class="options-hint">Connected as The Encypher Times</div>
    </div>
  </div>
  <div class="options-section">
    <h2>Verification</h2>
    <div class="options-row">
      <span class="options-row-label">Auto-verify on page load</span>
      <div class="options-toggle"></div>
    </div>
    <div class="options-row">
      <span class="options-row-label">Show verification badges</span>
      <div class="options-toggle"></div>
    </div>
  </div>
  <div class="options-section">
    <h2>Advanced</h2>
    <div class="options-field">
      <label>API Base URL</label>
      <input class="options-input" value="https://api.encypherai.com" readonly>
    </div>
    <div class="options-field">
      <label>Cache Duration (minutes)</label>
      <input class="options-input" type="number" value="60" readonly style="width:100px">
    </div>
  </div>
</div>
<div class="caption">Configure API key and verification preferences</div>
</div>
</body></html>`;
}

// ─── Small Promo Tile (440x280) ───
function smallPromoHTML() {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><style>
${BASE_CSS}
body {
  width: 440px; height: 280px;
  background: linear-gradient(135deg, ${DEEP_NAVY} 0%, #243d66 50%, ${AZURE_BLUE} 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-family: 'Roboto', sans-serif;
  overflow: hidden;
  position: relative;
}
/* Subtle pattern */
body::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 80% 20%, ${CYBER_TEAL}15 0%, transparent 50%),
              radial-gradient(circle at 20% 80%, ${AZURE_BLUE}20 0%, transparent 50%);
}
.content { position: relative; z-index: 1; text-align: center; }
.logo-icon { width: 56px; height: 56px; color: white; margin-bottom: 16px; }
.title {
  font-size: 22px;
  font-weight: 700;
  color: white;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}
.subtitle {
  font-size: 13px;
  color: ${LIGHT_SKY};
  font-weight: 400;
  max-width: 320px;
}
.badge-row {
  display: flex;
  gap: 8px;
  margin-top: 20px;
  justify-content: center;
}
.feature-badge {
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 16px;
  padding: 4px 12px;
  font-size: 11px;
  color: white;
  font-weight: 500;
}
</style></head><body>
<div class="content">
  <div class="logo-icon"><img src="${LOGO_WHITE_PNG_URI}" style="height:48px;width:auto;" /></div>
  <div class="title">C2PA Verifier</div>
  <div class="subtitle">Verify and sign content authenticity on any webpage</div>
  <div class="badge-row">
    <span class="feature-badge">C2PA Standard</span>
    <span class="feature-badge">Free to Use</span>
    <span class="feature-badge">Privacy-First</span>
  </div>
</div>
</body></html>`;
}

// ─── Large Promo Tile (920x680) ───
function largePromoHTML() {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><style>
${BASE_CSS}
body {
  width: 920px; height: 680px;
  background: linear-gradient(160deg, ${DEEP_NAVY} 0%, #1e3a5f 40%, ${AZURE_BLUE} 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Roboto', sans-serif;
  overflow: hidden;
  position: relative;
}
body::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 70% 30%, ${CYBER_TEAL}12 0%, transparent 60%),
              radial-gradient(ellipse at 30% 70%, ${AZURE_BLUE}15 0%, transparent 60%);
}
.layout {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 48px;
  padding: 0 56px;
}
.left { flex: 1; }
.right { flex: 1; display: flex; justify-content: center; }
.logo-icon { width: 48px; height: 48px; color: white; margin-bottom: 20px; }
.title {
  font-size: 32px;
  font-weight: 700;
  color: white;
  line-height: 1.2;
  margin-bottom: 12px;
}
.subtitle {
  font-size: 15px;
  color: ${LIGHT_SKY};
  line-height: 1.6;
  margin-bottom: 28px;
  max-width: 380px;
}
.features {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.feature {
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
  font-size: 14px;
  font-weight: 500;
}
.feature-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: ${CYBER_TEAL};
  flex-shrink: 0;
}
/* Mock article card */
.mock-article {
  width: 340px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  overflow: hidden;
  transform: rotate(-2deg);
}
.mock-article-header {
  padding: 20px 24px 12px;
}
.mock-article-pub {
  font-family: 'Playfair Display', serif;
  font-size: 18px;
  font-weight: 800;
  color: ${DEEP_NAVY};
  margin-bottom: 8px;
}
.mock-article-title {
  font-family: 'Playfair Display', serif;
  font-size: 15px;
  font-weight: 700;
  color: ${DEEP_NAVY};
  line-height: 1.3;
  margin-bottom: 8px;
}
.mock-article-text {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.6;
  padding: 0 24px 20px;
}
.mock-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: ${AZURE_BLUE}12;
  border: 1px solid ${AZURE_BLUE}30;
  border-radius: 6px;
  padding: 6px 12px;
  margin: 0 24px 16px;
  font-size: 11px;
  color: ${AZURE_BLUE};
  font-weight: 600;
}
.mock-badge svg { width: 14px; height: 14px; }
</style></head><body>
<div class="layout">
  <div class="left">
    <div class="logo-icon"><img src="${LOGO_WHITE_PNG_URI}" style="height:48px;width:auto;" /></div>
    <div class="title">Trust, Verified.</div>
    <div class="subtitle">See instant verification badges on signed content. Combat misinformation with cryptographic proof of authorship.</div>
    <div class="features">
      <div class="feature"><div class="feature-dot"></div>Auto-detect C2PA signed content</div>
      <div class="feature"><div class="feature-dot"></div>Sign your own content from the browser</div>
      <div class="feature"><div class="feature-dot"></div>Works on any webpage, privacy-first</div>
      <div class="feature"><div class="feature-dot"></div>Free verification, no account needed</div>
    </div>
  </div>
  <div class="right">
    <div class="mock-article">
      <div class="mock-article-header">
        <div class="mock-article-pub">The Encypher Times</div>
        <div class="mock-article-title">The Rise of Content Authenticity: How C2PA Is Changing Digital Trust</div>
      </div>
      <div class="mock-badge">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        Verified &mdash; Signed by The Encypher Times
      </div>
      <div class="mock-article-text">
        In an era where AI-generated content is becoming indistinguishable from human writing, the need for verifiable content provenance has never been more urgent...
      </div>
    </div>
  </div>
</div>
</body></html>`;
}

// ─── Marquee Promo Tile (1400x560) ───
function marqueePromoHTML() {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><style>
${BASE_CSS}
body {
  width: 1400px; height: 560px;
  background: linear-gradient(135deg, ${DEEP_NAVY} 0%, #1e3a5f 35%, ${AZURE_BLUE} 100%);
  display: flex;
  align-items: center;
  font-family: 'Roboto', sans-serif;
  overflow: hidden;
  position: relative;
}
body::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 75% 40%, ${CYBER_TEAL}10 0%, transparent 50%),
              radial-gradient(ellipse at 25% 60%, ${AZURE_BLUE}12 0%, transparent 50%);
}
.layout {
  position: relative; z-index: 1;
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0 80px;
  gap: 64px;
}
.left { flex: 1; }
.center { flex: 0 0 auto; }
.right { flex: 1; display: flex; justify-content: flex-end; }
.logo-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}
.logo-icon { width: 44px; height: 44px; color: white; }
.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: white;
  letter-spacing: 1px;
}
.title {
  font-size: 40px;
  font-weight: 700;
  color: white;
  line-height: 1.15;
  margin-bottom: 16px;
  max-width: 480px;
}
.title span { color: ${CYBER_TEAL}; }
.subtitle {
  font-size: 16px;
  color: ${LIGHT_SKY};
  line-height: 1.6;
  max-width: 440px;
  margin-bottom: 28px;
}
.cta-row { display: flex; gap: 12px; }
.cta {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.cta-primary {
  background: white;
  color: ${DEEP_NAVY};
}
.cta-secondary {
  background: rgba(255,255,255,0.12);
  color: white;
  border: 1px solid rgba(255,255,255,0.25);
}
/* Three floating cards */
.cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.float-card {
  background: white;
  border-radius: 10px;
  padding: 14px 18px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  display: flex;
  align-items: center;
  gap: 12px;
  width: 300px;
}
.float-card:nth-child(1) { transform: translateX(20px); }
.float-card:nth-child(3) { transform: translateX(20px); }
.fc-icon {
  width: 32px; height: 32px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.fc-icon.verified { background: ${AZURE_BLUE}15; color: ${AZURE_BLUE}; }
.fc-icon svg { width: 16px; height: 16px; }
.fc-pub {
  font-size: 13px;
  font-weight: 600;
  color: ${DEEP_NAVY};
}
.fc-status {
  font-size: 11px;
  color: ${NEUTRAL_GRAY};
}
</style></head><body>
<div class="layout">
  <div class="left">
    <div class="logo-row">
      <img src="${LOGO_WHITE_PNG_URI}" style="height:32px;width:auto;" />
    </div>
    <div class="title">Verify Content.<br><span>Build Trust.</span></div>
    <div class="subtitle">The Chrome extension that detects and verifies C2PA-signed content on any webpage. See who authored it, when, and whether it's been tampered with.</div>
    <div class="cta-row">
      <div class="cta cta-primary">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
        Add to Chrome — Free
      </div>
      <div class="cta cta-secondary">Learn More</div>
    </div>
  </div>
  <div class="right">
    <div class="cards">
      <div class="float-card">
        <div class="fc-icon verified">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <div>
          <div class="fc-pub">The Encypher Times</div>
          <div class="fc-status">Verified &bull; C2PA Text Manifest</div>
        </div>
      </div>
      <div class="float-card">
        <div class="fc-icon verified">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <div>
          <div class="fc-pub">Reuters News Agency</div>
          <div class="fc-status">Verified &bull; Encypher Format</div>
        </div>
      </div>
      <div class="float-card">
        <div class="fc-icon verified">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <div>
          <div class="fc-pub">Associated Press</div>
          <div class="fc-status">Verified &bull; C2PA Text Manifest</div>
        </div>
      </div>
    </div>
  </div>
</div>
</body></html>`;
}

// ─── Main ───
async function main() {
  // Create output directory
  if (!fs.existsSync(OUT_DIR)) {
    fs.mkdirSync(OUT_DIR, { recursive: true });
  }

  console.log('Launching Puppeteer...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--font-render-hinting=none'],
  });

  const assets = [
    // Screenshots (1280x800)
    {
      name: 'screenshot-1-verification-badges',
      html: articlePageHTML(),
      width: 1280,
      height: 800,
      description: 'Verification in Action',
    },
    {
      name: 'screenshot-2-popup-interface',
      html: popupScreenshotHTML(),
      width: 1280,
      height: 800,
      description: 'Popup Interface',
    },
    {
      name: 'screenshot-3-options-page',
      html: optionsScreenshotHTML(),
      width: 1280,
      height: 800,
      description: 'Options Page',
    },
    // Promo tiles
    {
      name: 'promo-small-440x280',
      html: smallPromoHTML(),
      width: 440,
      height: 280,
      description: 'Small Promo Tile',
    },
    {
      name: 'promo-large-920x680',
      html: largePromoHTML(),
      width: 920,
      height: 680,
      description: 'Large Promo Tile',
    },
    {
      name: 'promo-marquee-1400x560',
      html: marqueePromoHTML(),
      width: 1400,
      height: 560,
      description: 'Marquee Promo Tile',
    },
  ];

  for (const asset of assets) {
    console.log(`  Generating ${asset.description} (${asset.width}x${asset.height})...`);
    const page = await browser.newPage();
    await page.setViewport({ width: asset.width, height: asset.height, deviceScaleFactor: 2 });
    await page.setContent(asset.html, { waitUntil: 'networkidle0' });
    // Wait for fonts to load
    await page.evaluate(() => document.fonts.ready);
    await new Promise((r) => setTimeout(r, 500));

    // For the article screenshot, inject a floating tooltip near badge1
    if (asset.name === 'screenshot-1-verification-badges') {
      await page.evaluate(() => {
        const badge = document.getElementById('badge1');
        if (!badge) return;
        const rect = badge.getBoundingClientRect();
        const tooltip = document.createElement('div');
        tooltip.className = 'floating-tooltip';
        tooltip.innerHTML = '<div class="tt-status">Verified Content</div><div class="tt-signer">Signed by: The Encypher Times</div>';
        // Place offscreen first to measure
        tooltip.style.visibility = 'hidden';
        document.body.appendChild(tooltip);
        const ttRect = tooltip.getBoundingClientRect();
        // Position above the badge with 10px gap
        tooltip.style.left = (rect.left + rect.width / 2 - ttRect.width / 2) + 'px';
        tooltip.style.top = (rect.top - ttRect.height - 14) + 'px';
        tooltip.style.visibility = 'visible';
      });
      await new Promise((r) => setTimeout(r, 100));
    }

    const outPath = path.join(OUT_DIR, `${asset.name}.png`);
    await page.screenshot({ path: outPath, type: 'png' });
    console.log(`    -> ${outPath}`);
    await page.close();
  }

  await browser.close();
  console.log(`\nDone! ${assets.length} assets generated in ${OUT_DIR}`);
}

main().catch((err) => {
  console.error('Error:', err);
  process.exit(1);
});
