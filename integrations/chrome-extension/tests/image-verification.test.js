import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

// Read source files for contract assertions
const serviceWorkerSource = fs.readFileSync(
  path.resolve(process.cwd(), 'background', 'service-worker.js'), 'utf8'
);
const detectorSource = fs.readFileSync(
  path.resolve(process.cwd(), 'content', 'detector.js'), 'utf8'
);
const manifestSource = fs.readFileSync(
  path.resolve(process.cwd(), 'manifest.json'), 'utf8'
);
const manifest = JSON.parse(manifestSource);
const badgeCss = fs.readFileSync(
  path.resolve(process.cwd(), 'content', 'badge.css'), 'utf8'
);
const popupHtml = fs.readFileSync(
  path.resolve(process.cwd(), 'popup', 'popup.html'), 'utf8'
);
const popupJs = fs.readFileSync(
  path.resolve(process.cwd(), 'popup', 'popup.js'), 'utf8'
);

// -----------------------------------------------------------------------
// Manifest permissions
// -----------------------------------------------------------------------
describe('manifest: image verification permissions', () => {
  it('declares <all_urls> in host_permissions for image fetching', () => {
    assert.ok(
      manifest.host_permissions.includes('<all_urls>'),
      'host_permissions must include <all_urls> to fetch arbitrary image bytes'
    );
  });

  it('still includes Encypher API host permissions', () => {
    assert.ok(manifest.host_permissions.includes('https://api.encypher.com/*'));
  });
});

// -----------------------------------------------------------------------
// Service worker: API config and verifyImage
// -----------------------------------------------------------------------
describe('service worker: image verification handler', () => {
  it('defines imageVerifyEndpoint in API_CONFIG', () => {
    assert.match(serviceWorkerSource, /imageVerifyEndpoint\s*:\s*['"]\/api\/v1\/verify\/image['"]/);
  });

  it('has a verifyImage function that fetches image bytes and POSTs base64', () => {
    assert.match(serviceWorkerSource, /async function verifyImage\(imageUrl\)/);
    assert.match(serviceWorkerSource, /image_data:\s*imageData/);
    assert.match(serviceWorkerSource, /mime_type:\s*mimeType/);
  });

  it('enforces a 10MB size limit on images', () => {
    assert.match(serviceWorkerSource, /10\s*\*\s*1024\s*\*\s*1024/);
    assert.match(serviceWorkerSource, /Image exceeds 10MB size limit/);
  });

  it('caches image verification results with same TTL as text', () => {
    // verifyImage uses verificationCache and CACHE_TTL (same as verifyContent)
    assert.match(serviceWorkerSource, /verificationCache\.get\(cacheKey\)/);
    assert.match(serviceWorkerSource, /verificationCache\.set\(cacheKey/);
  });

  it('deduplicates in-flight image verification requests', () => {
    // verifyImage uses verificationInFlight (same as verifyContent)
    assert.match(serviceWorkerSource, /verificationInFlight\.get\(cacheKey\)/);
    assert.match(serviceWorkerSource, /verificationInFlight\.set\(cacheKey/);
  });

  it('retries on transient failure via shouldRetryVerification', () => {
    // The verifyImage function checks shouldRetryVerification
    assert.match(serviceWorkerSource, /shouldRetryVerification\(result\)/);
  });

  it('has a _guessMimeType helper for URL extension fallback', () => {
    assert.match(serviceWorkerSource, /function _guessMimeType\(url\)/);
    assert.match(serviceWorkerSource, /image\/jpeg/);
    assert.match(serviceWorkerSource, /image\/png/);
    assert.match(serviceWorkerSource, /image\/webp/);
  });

  it('returns contentType: image in all result paths', () => {
    // Count occurrences of contentType: 'image' in verifyImage
    const matches = serviceWorkerSource.match(/contentType:\s*['"]image['"]/g);
    assert.ok(matches && matches.length >= 3, 'verifyImage must set contentType on success, error, and timeout paths');
  });
});

// -----------------------------------------------------------------------
// Service worker: VERIFY_MEDIA message handler
// -----------------------------------------------------------------------
describe('service worker: VERIFY_MEDIA message handler', () => {
  it('handles VERIFY_MEDIA messages in onMessage listener', () => {
    assert.match(serviceWorkerSource, /case\s+['"]VERIFY_MEDIA['"]/);
  });

  it('routes to verifyImage for image media type', () => {
    assert.match(serviceWorkerSource, /verifyImage/);
    assert.match(serviceWorkerSource, /verifyAudio/);
    assert.match(serviceWorkerSource, /verifyVideo/);
  });

  it('updates tabState with media verification results', () => {
    assert.match(serviceWorkerSource, /updateTabStateWithVerification\(current,\s*result\)/);
  });

  it('sets contentType and mediaUrl on verification detail', () => {
    assert.match(serviceWorkerSource, /detail\.contentType\s*=\s*mediaType/);
    assert.match(serviceWorkerSource, /detail\.mediaUrl\s*=\s*message\.url/);
  });

  it('uses c2pa marker types for verification details', () => {
    assert.match(serviceWorkerSource, /c2pa_image/);
    assert.match(serviceWorkerSource, /c2pa_audio/);
    assert.match(serviceWorkerSource, /c2pa_video/);
  });
});

// -----------------------------------------------------------------------
// Service worker: context menu
// -----------------------------------------------------------------------
describe('service worker: image context menu', () => {
  it('registers verify-image context menu with image context', () => {
    assert.match(serviceWorkerSource, /id:\s*['"]verify-image['"]/);
    assert.match(serviceWorkerSource, /contexts:\s*\[['"]image['"]\]/);
  });

  it('does not block image context menu clicks with selectionText guard', () => {
    // The handler must check menuItemId before checking selectionText
    const verifyImagePos = serviceWorkerSource.indexOf("'verify-image'");
    const selectionGuardPos = serviceWorkerSource.indexOf("if (!info.selectionText) return;");
    assert.ok(verifyImagePos < selectionGuardPos,
      'verify-image handling must precede selectionText guard');
  });

  it('sends VERIFY_IMAGE_CONTEXT message to content script', () => {
    assert.match(serviceWorkerSource, /type:\s*['"]VERIFY_IMAGE_CONTEXT['"]/);
    assert.match(serviceWorkerSource, /srcUrl:\s*info\.srcUrl/);
  });
});

// -----------------------------------------------------------------------
// Detector: image scanning
// -----------------------------------------------------------------------
describe('detector: image scanning', () => {
  it('defines _processedImages set for deduplication', () => {
    assert.match(detectorSource, /const _processedImages\s*=\s*new Set/);
  });

  it('defines _scanImages function that queries img elements', () => {
    assert.match(detectorSource, /function _scanImages\(root\)/);
    assert.match(detectorSource, /querySelectorAll\(['"]img['"]\)/);
  });

  it('filters out small images below MIN_IMAGE_DIMENSION', () => {
    assert.match(detectorSource, /MIN_IMAGE_DIMENSION/);
  });

  it('skips data: and blob: URIs', () => {
    assert.match(detectorSource, /startsWith\(['"]data:['"]\)/);
    assert.match(detectorSource, /startsWith\(['"]blob:['"]\)/);
  });

  it('skips extension-injected elements', () => {
    assert.match(detectorSource, /\.encypher-badge/);
  });

  it('integrates _scanImages into scanPage', () => {
    // _scanImages must be called within scanPage
    assert.match(detectorSource, /_scanImages\(root\)/);
  });
});

// -----------------------------------------------------------------------
// Detector: image badge injection
// -----------------------------------------------------------------------
describe('detector: image badge injection', () => {
  it('defines injectImageBadge function', () => {
    assert.match(detectorSource, /function injectImageBadge\(imgElement,\s*status,\s*details\)/);
  });

  it('wraps images in encypher-image-badge-wrapper', () => {
    assert.match(detectorSource, /encypher-image-badge-wrapper/);
  });

  it('uses encypher-badge--media CSS modifier', () => {
    assert.match(detectorSource, /encypher-badge--media/);
  });

  it('stores media src in badge dataset for lookup', () => {
    assert.match(detectorSource, /dataset\.encypherMediaSrc/);
  });

  it('supports all badge statuses: verified, pending, invalid, error', () => {
    assert.match(detectorSource, /encypher-badge--\$\{status\}/);
  });
});

// -----------------------------------------------------------------------
// Detector: message handlers for image verification
// -----------------------------------------------------------------------
describe('detector: image verification message handlers', () => {
  it('handles VERIFY_IMAGE_CONTEXT message from context menu', () => {
    assert.match(detectorSource, /message\.type\s*===\s*['"]VERIFY_IMAGE_CONTEXT['"]/);
  });

  it('handles FOCUS_MEDIA message for locate-on-page', () => {
    assert.match(detectorSource, /message\.type\s*===\s*['"]FOCUS_MEDIA['"]/);
  });

  it('handles GET_PAGE_IMAGES message for popup inventory', () => {
    assert.match(detectorSource, /message\.type\s*===\s*['"]GET_PAGE_IMAGES['"]/);
  });

  it('clears image state on RESCAN', () => {
    assert.match(detectorSource, /_processedImages\.clear\(\)/);
    assert.match(detectorSource, /_imageVerificationState\.clear\(\)/);
  });

  it('unwraps image badges on RESCAN to restore original DOM', () => {
    assert.match(detectorSource, /encypher-image-badge-wrapper/);
    assert.match(detectorSource, /wrapper\.remove\(\)/);
  });
});

// -----------------------------------------------------------------------
// Detector: _verifyImageAndBadge flow
// -----------------------------------------------------------------------
describe('detector: _verifyImageAndBadge', () => {
  it('defines _verifyImageAndBadge that sends VERIFY_MEDIA message', () => {
    assert.match(detectorSource, /async function _verifyImageAndBadge/);
    assert.match(detectorSource, /type:\s*['"]VERIFY_MEDIA['"]/);
  });

  it('shows pending badge before verification starts', () => {
    // injectImageBadge with pending should come before sendMessage
    const pendingCall = detectorSource.indexOf("injectImageBadge(imgElement, 'pending'");
    const sendCall = detectorSource.indexOf("type: 'VERIFY_MEDIA'");
    assert.ok(pendingCall > 0 && sendCall > 0);
    assert.ok(pendingCall < sendCall, 'pending badge must be injected before API call');
  });

  it('updates badge with final status after verification completes', () => {
    // After await, injectImageBadge is called with the result status
    assert.match(detectorSource, /injectImageBadge\(imgElement,\s*status,\s*details\)/);
  });

  it('handles errors by showing error badge', () => {
    assert.match(detectorSource, /injectImageBadge\(imgElement,\s*['"]error['"]/);
  });
});

// -----------------------------------------------------------------------
// CSS: image badge styles
// -----------------------------------------------------------------------
describe('badge CSS: image badge styles', () => {
  it('defines .encypher-image-badge-wrapper with position: relative', () => {
    assert.match(badgeCss, /\.encypher-image-badge-wrapper\s*\{/);
    assert.match(badgeCss, /position:\s*relative/);
  });

  it('defines .encypher-badge--media modifier for image badges', () => {
    assert.match(badgeCss, /\.encypher-badge--media\s*\{/);
  });

  it('positions media badge absolutely at top-right', () => {
    assert.match(badgeCss, /position:\s*absolute/);
    assert.match(badgeCss, /top:\s*6px/);
    assert.match(badgeCss, /right:\s*6px/);
  });
});

// -----------------------------------------------------------------------
// Popup: media verification UI
// -----------------------------------------------------------------------
describe('popup: media verification UI', () => {
  it('has a media-section element in popup HTML', () => {
    assert.match(popupHtml, /id="media-section"/);
    assert.match(popupHtml, /id="media-list"/);
  });

  it('popup JS defines renderMediaSection function', () => {
    assert.match(popupJs, /function renderMediaSection\(/);
  });

  it('popup JS defines verifyImageFromPopup function', () => {
    assert.match(popupJs, /async function verifyImageFromPopup\(/);
  });

  it('popup JS defines locateMediaOnPage function', () => {
    assert.match(popupJs, /async function locateMediaOnPage\(/);
  });

  it('popup JS handles c2pa_image marker type label', () => {
    assert.match(popupJs, /c2pa_image/);
    assert.match(popupJs, /C2PA Image/);
  });

  it('popup JS distinguishes image results in detail rendering', () => {
    assert.match(popupJs, /contentType\s*===\s*['"]image['"]/);
  });

  it('popup JS fetches image inventory via GET_PAGE_IMAGES', () => {
    assert.match(popupJs, /type:\s*['"]GET_PAGE_IMAGES['"]/);
  });

  it('sends FOCUS_MEDIA message for image locate-on-page', () => {
    assert.match(popupJs, /type:\s*['"]FOCUS_MEDIA['"]/);
    assert.match(popupJs, /data-action="locate-media"/);
  });
});

// -----------------------------------------------------------------------
// Service worker: audio/video verification endpoints
// -----------------------------------------------------------------------
describe('service worker: audio/video verify endpoints', () => {
  it('defines audioVerifyEndpoint in API_CONFIG', () => {
    assert.match(serviceWorkerSource, /audioVerifyEndpoint:\s*['"]\/api\/v1\/verify\/audio['"]/);
  });

  it('defines videoVerifyEndpoint in API_CONFIG', () => {
    assert.match(serviceWorkerSource, /videoVerifyEndpoint:\s*['"]\/api\/v1\/verify\/video['"]/);
  });

  it('defines verifyAudio function', () => {
    assert.match(serviceWorkerSource, /async function verifyAudio\(audioUrl\)/);
  });

  it('defines verifyVideo function', () => {
    assert.match(serviceWorkerSource, /async function verifyVideo\(videoUrl\)/);
  });

  it('uses FormData for video verification (multipart upload)', () => {
    assert.match(serviceWorkerSource, /new FormData\(\)/);
    assert.match(serviceWorkerSource, /formData\.append\(['"]file['"]/);
  });

  it('enforces 50MB client-side limit for audio', () => {
    assert.match(serviceWorkerSource, /50\s*\*\s*1024\s*\*\s*1024/);
  });

  it('defines MIME type guesser for audio', () => {
    assert.match(serviceWorkerSource, /function _guessAudioMimeType\(url\)/);
  });

  it('defines MIME type guesser for video', () => {
    assert.match(serviceWorkerSource, /function _guessVideoMimeType\(url\)/);
  });
});

// -----------------------------------------------------------------------
// Service worker: audio/video context menus
// -----------------------------------------------------------------------
describe('service worker: audio/video context menus', () => {
  it('registers verify-audio context menu', () => {
    assert.match(serviceWorkerSource, /id:\s*['"]verify-audio['"]/);
    assert.match(serviceWorkerSource, /contexts:\s*\[['"]audio['"]\]/);
  });

  it('registers verify-video context menu', () => {
    assert.match(serviceWorkerSource, /id:\s*['"]verify-video['"]/);
    assert.match(serviceWorkerSource, /contexts:\s*\[['"]video['"]\]/);
  });

  it('sends VERIFY_AUDIO_CONTEXT message for audio context menu', () => {
    assert.match(serviceWorkerSource, /type:\s*['"]VERIFY_AUDIO_CONTEXT['"]/);
  });

  it('sends VERIFY_VIDEO_CONTEXT message for video context menu', () => {
    assert.match(serviceWorkerSource, /type:\s*['"]VERIFY_VIDEO_CONTEXT['"]/);
  });
});

// -----------------------------------------------------------------------
// Detector: audio/video scanning and badges
// -----------------------------------------------------------------------
describe('detector: audio/video scanning', () => {
  it('defines _processedAudioVideo set for deduplication', () => {
    assert.match(detectorSource, /const _processedAudioVideo\s*=\s*new Set/);
  });

  it('defines _audioVideoVerificationState map', () => {
    assert.match(detectorSource, /const _audioVideoVerificationState\s*=\s*new Map/);
  });

  it('defines _scanAudioVideo function', () => {
    assert.match(detectorSource, /function _scanAudioVideo\(root\)/);
  });

  it('queries audio and video elements in scan', () => {
    assert.match(detectorSource, /querySelectorAll\(['"]audio,\s*video['"]\)/);
  });

  it('integrates _scanAudioVideo into scanPage', () => {
    assert.match(detectorSource, /_scanAudioVideo\(root\)/);
  });

  it('defines injectMediaBadge for audio/video elements', () => {
    assert.match(detectorSource, /function injectMediaBadge\(mediaElement,\s*status,\s*details\)/);
  });

  it('wraps media elements in encypher-media-badge-wrapper', () => {
    assert.match(detectorSource, /encypher-media-badge-wrapper/);
  });

  it('defines _verifyMediaAndBadge function', () => {
    assert.match(detectorSource, /async function _verifyMediaAndBadge\(mediaElement,\s*srcUrl,\s*mediaType\)/);
  });

  it('handles VERIFY_AUDIO_CONTEXT message', () => {
    assert.match(detectorSource, /message\.type\s*===\s*['"]VERIFY_AUDIO_CONTEXT['"]/);
  });

  it('handles VERIFY_VIDEO_CONTEXT message', () => {
    assert.match(detectorSource, /message\.type\s*===\s*['"]VERIFY_VIDEO_CONTEXT['"]/);
  });

  it('handles GET_PAGE_MEDIA message for popup inventory', () => {
    assert.match(detectorSource, /message\.type\s*===\s*['"]GET_PAGE_MEDIA['"]/);
  });

  it('clears audio/video state on RESCAN', () => {
    assert.match(detectorSource, /_processedAudioVideo\.clear\(\)/);
    assert.match(detectorSource, /_audioVideoVerificationState\.clear\(\)/);
  });

  it('unwraps media badges on RESCAN', () => {
    assert.match(detectorSource, /encypher-media-badge-wrapper/);
  });
});

// -----------------------------------------------------------------------
// CSS: audio/video badge styles
// -----------------------------------------------------------------------
describe('badge CSS: audio/video badge styles', () => {
  it('defines .encypher-media-badge-wrapper', () => {
    assert.match(badgeCss, /\.encypher-media-badge-wrapper\s*\{/);
  });
});

// -----------------------------------------------------------------------
// Popup: audio/video verification UI
// -----------------------------------------------------------------------
describe('popup: audio/video verification UI', () => {
  it('popup JS handles c2pa_audio marker type label', () => {
    assert.match(popupJs, /c2pa_audio/);
    assert.match(popupJs, /C2PA Audio/);
  });

  it('popup JS handles c2pa_video marker type label', () => {
    assert.match(popupJs, /c2pa_video/);
    assert.match(popupJs, /C2PA Video/);
  });

  it('popup JS defines verifyMediaFromPopup function', () => {
    assert.match(popupJs, /async function verifyMediaFromPopup\(/);
  });

  it('popup JS fetches audio/video inventory via GET_PAGE_MEDIA', () => {
    assert.match(popupJs, /type:\s*['"]GET_PAGE_MEDIA['"]/);
  });

  it('popup JS renders audio/video items with type icon', () => {
    assert.match(popupJs, /popup__media-type-icon/);
  });

  it('popup CSS defines .popup__media-type-icon', () => {
    const popupCss = fs.readFileSync(
      path.resolve(process.cwd(), 'popup', 'popup.css'), 'utf8'
    );
    assert.match(popupCss, /\.popup__media-type-icon\s*\{/);
  });
});

// -----------------------------------------------------------------------
// Phase 3: Automatic C2PA image scanning
// -----------------------------------------------------------------------
describe('service worker: C2PA header detection', () => {
  it('defines _checkC2paHeader function', () => {
    assert.match(serviceWorkerSource, /async function _checkC2paHeader\(imageUrl\)/);
  });

  it('uses Range request for lightweight header check', () => {
    assert.match(serviceWorkerSource, /Range.*bytes=0-/);
  });

  it('defines _hasJumbfMarker for JPEG/PNG parsing', () => {
    assert.match(serviceWorkerSource, /function _hasJumbfMarker\(bytes\)/);
  });

  it('scans JPEG for APP11 marker (0xFF 0xEB)', () => {
    assert.match(serviceWorkerSource, /0xEB/);
  });

  it('scans PNG for caBX chunk', () => {
    assert.match(serviceWorkerSource, /caBX/);
  });

  it('handles CHECK_C2PA_HEADER message', () => {
    assert.match(serviceWorkerSource, /case\s*['"]CHECK_C2PA_HEADER['"]/);
  });
});

describe('detector: auto-scan pipeline', () => {
  it('defines auto-scan configuration constants', () => {
    assert.match(detectorSource, /AUTO_SCAN_MAX_IMAGES\s*=\s*50/);
    assert.match(detectorSource, /AUTO_SCAN_MAX_CONCURRENT\s*=\s*6/);
    assert.match(detectorSource, /AUTO_SCAN_BANDWIDTH_LIMIT/);
    assert.match(detectorSource, /AUTO_SCAN_COOLDOWN_MS/);
  });

  it('defines _autoScanEnabled toggle', () => {
    assert.match(detectorSource, /_autoScanEnabled/);
  });

  it('defines _autoScanImages function', () => {
    assert.match(detectorSource, /function _autoScanImages\(\)/);
  });

  it('respects bandwidth circuit breaker', () => {
    assert.match(detectorSource, /AUTO_SCAN_BANDWIDTH_LIMIT_IMAGES/);
    assert.match(detectorSource, /_autoScanImageBytes/);
  });

  it('respects cooldown period', () => {
    assert.match(detectorSource, /_autoScanPageCooldown/);
    assert.match(detectorSource, /AUTO_SCAN_COOLDOWN_MS/);
  });

  it('uses requestIdleCallback for non-blocking scan', () => {
    assert.match(detectorSource, /requestIdleCallback/);
  });

  it('triggers auto-scan from _scanImages when new images found', () => {
    assert.match(detectorSource, /_autoScanEnabled && newCount > 0/);
  });

  it('delegates C2PA header check to service worker', () => {
    assert.match(detectorSource, /CHECK_C2PA_HEADER/);
  });

  it('auto-verifies images with C2PA headers via _verifyImageAndBadge', () => {
    assert.match(detectorSource, /_verifyImageAndBadge\(img,\s*src\)/);
  });

  it('resets auto-scan state on RESCAN', () => {
    assert.match(detectorSource, /_autoScanImageBytes\s*=\s*0/);
    assert.match(detectorSource, /_autoScanCheckedCount\s*=\s*0/);
    assert.match(detectorSource, /_autoScanPageCooldown\.clear\(\)/);
  });

  it('loads auto-scan setting from chrome.storage.sync', () => {
    assert.match(detectorSource, /autoScanImages/);
  });
});
