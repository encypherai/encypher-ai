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
const badgeCss = fs.readFileSync(
  path.resolve(process.cwd(), 'content', 'badge.css'), 'utf8'
);
const popupJs = fs.readFileSync(
  path.resolve(process.cwd(), 'popup', 'popup.js'), 'utf8'
);

// -----------------------------------------------------------------------
// Service worker: API config for audio/video
// -----------------------------------------------------------------------
describe('service worker: audio/video API config', () => {
  it('defines audioVerifyEndpoint in API_CONFIG', () => {
    assert.match(serviceWorkerSource, /audioVerifyEndpoint\s*:\s*['"]\/api\/v1\/verify\/audio['"]/);
  });

  it('defines videoVerifyEndpoint in API_CONFIG', () => {
    assert.match(serviceWorkerSource, /videoVerifyEndpoint\s*:\s*['"]\/api\/v1\/verify\/video['"]/);
  });
});

// -----------------------------------------------------------------------
// Service worker: verifyAudio handler
// -----------------------------------------------------------------------
describe('service worker: audio verification handler', () => {
  it('has a verifyAudio function that fetches audio bytes and POSTs base64', () => {
    assert.match(serviceWorkerSource, /async function verifyAudio\(audioUrl\)/);
    assert.match(serviceWorkerSource, /audio_data:\s*audioData/);
    assert.match(serviceWorkerSource, /mime_type:\s*mimeType/);
  });

  it('enforces a 50MB size limit on audio', () => {
    assert.match(serviceWorkerSource, /50\s*\*\s*1024\s*\*\s*1024/);
    assert.match(serviceWorkerSource, /Audio exceeds 50MB size limit/);
  });

  it('returns contentType: audio in all result paths', () => {
    const matches = serviceWorkerSource.match(/contentType:\s*['"]audio['"]/g);
    assert.ok(matches && matches.length >= 3, 'verifyAudio must set contentType on success, error, and timeout paths');
  });

  it('has a _guessAudioMimeType helper', () => {
    assert.match(serviceWorkerSource, /function _guessAudioMimeType\(url\)/);
    assert.match(serviceWorkerSource, /audio\/wav/);
    assert.match(serviceWorkerSource, /audio\/mpeg/);
    assert.match(serviceWorkerSource, /audio\/mp4/);
  });

  it('caches audio verification results', () => {
    // verifyAudio uses verificationCache (same pattern as verifyImage)
    const audioFnStart = serviceWorkerSource.indexOf('async function verifyAudio');
    const audioFnEnd = serviceWorkerSource.indexOf('async function verifyVideo');
    const audioFn = serviceWorkerSource.slice(audioFnStart, audioFnEnd);
    assert.match(audioFn, /verificationCache\.get\(cacheKey\)/);
    assert.match(audioFn, /verificationCache\.set\(cacheKey/);
  });
});

// -----------------------------------------------------------------------
// Service worker: verifyVideo handler
// -----------------------------------------------------------------------
describe('service worker: video verification handler', () => {
  it('has a verifyVideo function that fetches video bytes', () => {
    assert.match(serviceWorkerSource, /async function verifyVideo\(videoUrl\)/);
  });

  it('enforces a 50MB client-side size limit on video', () => {
    // The verifyVideo function checks 50MB
    const videoFnStart = serviceWorkerSource.indexOf('async function verifyVideo');
    const videoFn = serviceWorkerSource.slice(videoFnStart);
    assert.match(videoFn, /Video exceeds 50MB size limit/);
  });

  it('uses multipart/form-data for video upload', () => {
    assert.match(serviceWorkerSource, /new FormData\(\)/);
    assert.match(serviceWorkerSource, /formData\.append\(['"]file['"]/);
    assert.match(serviceWorkerSource, /formData\.append\(['"]mime_type['"]/);
  });

  it('returns contentType: video in all result paths', () => {
    const matches = serviceWorkerSource.match(/contentType:\s*['"]video['"]/g);
    assert.ok(matches && matches.length >= 3, 'verifyVideo must set contentType on success, error, and timeout paths');
  });

  it('has a _guessVideoMimeType helper', () => {
    assert.match(serviceWorkerSource, /function _guessVideoMimeType\(url\)/);
    assert.match(serviceWorkerSource, /video\/mp4/);
    assert.match(serviceWorkerSource, /video\/quicktime/);
  });

  it('has a _videoExtFromMime helper for filenames', () => {
    assert.match(serviceWorkerSource, /function _videoExtFromMime\(mimeType\)/);
  });
});

// -----------------------------------------------------------------------
// Service worker: VERIFY_MEDIA routes by mediaType
// -----------------------------------------------------------------------
describe('service worker: VERIFY_MEDIA message routing', () => {
  it('routes VERIFY_MEDIA by mediaType field', () => {
    assert.match(serviceWorkerSource, /message\.mediaType/);
  });

  it('calls verifyAudio for audio mediaType', () => {
    assert.match(serviceWorkerSource, /verifyAudio/);
  });

  it('calls verifyVideo for video mediaType', () => {
    assert.match(serviceWorkerSource, /verifyVideo/);
  });

  it('uses c2pa_audio markerType for audio verification', () => {
    assert.match(serviceWorkerSource, /c2pa_audio/);
  });

  it('uses c2pa_video markerType for video verification', () => {
    assert.match(serviceWorkerSource, /c2pa_video/);
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
// Detector: audio/video scanning
// -----------------------------------------------------------------------
describe('detector: audio/video scanning', () => {
  it('defines _processedAudioVideo set for deduplication', () => {
    assert.match(detectorSource, /const _processedAudioVideo\s*=\s*new Set/);
  });

  it('defines _audioVideoVerificationState map', () => {
    assert.match(detectorSource, /const _audioVideoVerificationState\s*=\s*new Map/);
  });

  it('defines _scanAudioVideo function that queries audio and video elements', () => {
    assert.match(detectorSource, /function _scanAudioVideo\(root\)/);
    assert.match(detectorSource, /querySelectorAll\(['"]audio, video['"]\)/);
  });

  it('extracts source from <source> children', () => {
    assert.match(detectorSource, /querySelector\(['"]source['"]\)/);
  });

  it('skips data: and blob: URIs', () => {
    // Already tested for images, verify audio/video scan also skips
    const avFn = detectorSource.slice(
      detectorSource.indexOf('function _scanAudioVideo'),
      detectorSource.indexOf('function injectMediaBadge')
    );
    assert.match(avFn, /startsWith\(['"]data:['"]\)/);
    assert.match(avFn, /startsWith\(['"]blob:['"]\)/);
  });

  it('integrates _scanAudioVideo into scanPage', () => {
    assert.match(detectorSource, /_scanAudioVideo\(root\)/);
  });
});

// -----------------------------------------------------------------------
// Detector: audio/video badge injection
// -----------------------------------------------------------------------
describe('detector: audio/video badge injection', () => {
  it('defines injectMediaBadge function', () => {
    assert.match(detectorSource, /function injectMediaBadge\(mediaElement,\s*status,\s*details\)/);
  });

  it('wraps elements in encypher-media-badge-wrapper', () => {
    assert.match(detectorSource, /encypher-media-badge-wrapper/);
  });

  it('uses encypher-badge--media CSS modifier', () => {
    // Already used by image badges too
    assert.match(detectorSource, /encypher-badge--media/);
  });

  it('tracks mediaType in badge dataset', () => {
    assert.match(detectorSource, /dataset\.encypherMediaSrc/);
  });
});

// -----------------------------------------------------------------------
// Detector: _verifyMediaAndBadge flow
// -----------------------------------------------------------------------
describe('detector: _verifyMediaAndBadge', () => {
  it('defines _verifyMediaAndBadge that sends VERIFY_MEDIA with mediaType', () => {
    assert.match(detectorSource, /async function _verifyMediaAndBadge/);
    assert.match(detectorSource, /type:\s*['"]VERIFY_MEDIA['"]/);
    assert.match(detectorSource, /mediaType/);
  });

  it('shows pending badge before verification starts', () => {
    const pendingCall = detectorSource.indexOf("injectMediaBadge(mediaElement, 'pending'");
    const sendCall = detectorSource.indexOf("type: 'VERIFY_MEDIA'", pendingCall);
    assert.ok(pendingCall > 0 && sendCall > 0);
    assert.ok(pendingCall < sendCall, 'pending badge must be injected before API call');
  });
});

// -----------------------------------------------------------------------
// Detector: audio/video message handlers
// -----------------------------------------------------------------------
describe('detector: audio/video message handlers', () => {
  it('handles VERIFY_AUDIO_CONTEXT message', () => {
    assert.match(detectorSource, /message\.type\s*===\s*['"]VERIFY_AUDIO_CONTEXT['"]/);
  });

  it('handles VERIFY_VIDEO_CONTEXT message', () => {
    assert.match(detectorSource, /message\.type\s*===\s*['"]VERIFY_VIDEO_CONTEXT['"]/);
  });

  it('handles GET_PAGE_MEDIA message for audio/video inventory', () => {
    assert.match(detectorSource, /message\.type\s*===\s*['"]GET_PAGE_MEDIA['"]/);
  });

  it('clears audio/video state on RESCAN', () => {
    assert.match(detectorSource, /_processedAudioVideo\.clear\(\)/);
    assert.match(detectorSource, /_audioVideoVerificationState\.clear\(\)/);
  });

  it('unwraps media badges on RESCAN', () => {
    assert.match(detectorSource, /encypher-media-badge-wrapper/);
  });

  it('FOCUS_MEDIA checks audio/video state as well as image state', () => {
    assert.match(detectorSource, /_audioVideoVerificationState\.get\(message\.mediaUrl\)/);
  });
});

// -----------------------------------------------------------------------
// CSS: media badge wrapper
// -----------------------------------------------------------------------
describe('badge CSS: audio/video badge styles', () => {
  it('defines .encypher-media-badge-wrapper', () => {
    assert.match(badgeCss, /\.encypher-media-badge-wrapper\s*\{/);
  });
});

// -----------------------------------------------------------------------
// Popup: audio/video support
// -----------------------------------------------------------------------
describe('popup: audio/video verification UI', () => {
  it('handles c2pa_audio marker type label', () => {
    assert.match(popupJs, /c2pa_audio/);
    assert.match(popupJs, /C2PA Audio/);
  });

  it('handles c2pa_video marker type label', () => {
    assert.match(popupJs, /c2pa_video/);
    assert.match(popupJs, /C2PA Video/);
  });

  it('defines verifyMediaFromPopup function', () => {
    assert.match(popupJs, /async function verifyMediaFromPopup\(/);
  });

  it('fetches audio/video inventory via GET_PAGE_MEDIA', () => {
    assert.match(popupJs, /type:\s*['"]GET_PAGE_MEDIA['"]/);
  });

  it('sends VERIFY_AUDIO_CONTEXT for audio verification from popup', () => {
    assert.match(popupJs, /VERIFY_AUDIO_CONTEXT/);
  });

  it('sends VERIFY_VIDEO_CONTEXT for video verification from popup', () => {
    assert.match(popupJs, /VERIFY_VIDEO_CONTEXT/);
  });

  it('distinguishes audio/video in detail rendering', () => {
    assert.match(popupJs, /contentType\s*===\s*['"]audio['"]/);
    assert.match(popupJs, /contentType\s*===\s*['"]video['"]/);
  });

  it('renders audio/video entries in media section', () => {
    assert.match(popupJs, /data-action="verify-media"/);
    assert.match(popupJs, /data-media-type/);
  });
});
