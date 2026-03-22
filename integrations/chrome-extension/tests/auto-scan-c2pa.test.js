import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

const detectorSource = fs.readFileSync(
  path.resolve(process.cwd(), 'content', 'detector.js'), 'utf8'
);
const serviceWorkerSource = fs.readFileSync(
  path.resolve(process.cwd(), 'background', 'service-worker.js'), 'utf8'
);
const optionsHtml = fs.readFileSync(
  path.resolve(process.cwd(), 'options', 'options.html'), 'utf8'
);
const optionsJs = fs.readFileSync(
  path.resolve(process.cwd(), 'options', 'options.js'), 'utf8'
);

// -----------------------------------------------------------------------
// C2PA Header Detection
// -----------------------------------------------------------------------
describe('detector: _checkC2paHeader delegation', () => {
  it('defines _checkC2paHeader function in detector', () => {
    assert.match(detectorSource, /async function _checkC2paHeader\(imageUrl\)/);
  });

  it('delegates to service worker via CHECK_C2PA_HEADER message', () => {
    assert.match(detectorSource, /CHECK_C2PA_HEADER/);
  });

  it('tracks approximate bandwidth cost (4096 bytes per check)', () => {
    assert.match(detectorSource, /_autoScanBytesUsed\s*\+=\s*4096/);
  });

  it('returns boolean from service worker response', () => {
    assert.match(detectorSource, /response\?\.hasC2pa/);
    assert.match(detectorSource, /return false/);
  });
});

describe('service-worker: _checkC2paHeader implementation', () => {
  it('defines _checkC2paHeader in service worker', () => {
    assert.match(serviceWorkerSource, /async function _checkC2paHeader\(imageUrl\)/);
  });

  it('uses Range request for first 4KB', () => {
    assert.match(serviceWorkerSource, /Range.*bytes=0-/);
    assert.match(serviceWorkerSource, /_C2PA_HEADER_BYTES/);
  });

  it('calls _hasJumbfMarker on fetched bytes', () => {
    assert.match(serviceWorkerSource, /return _hasJumbfMarker\(bytes\)/);
  });
});

// -----------------------------------------------------------------------
// JUMBF Marker Parser
// -----------------------------------------------------------------------
describe('service-worker: _hasJumbfMarker', () => {
  it('defines _hasJumbfMarker function', () => {
    assert.match(serviceWorkerSource, /function _hasJumbfMarker\(bytes\)/);
  });

  it('scans for JPEG APP11 marker (0xFF 0xEB)', () => {
    assert.match(serviceWorkerSource, /0xEB/);
    assert.match(serviceWorkerSource, /APP11/i);
  });

  it('scans for jumb box type in JPEG', () => {
    // 'jumb' = 0x6A 0x75 0x6D 0x62
    assert.match(serviceWorkerSource, /0x6A/);
    assert.match(serviceWorkerSource, /jumb/);
  });

  it('scans for PNG caBX chunk type', () => {
    assert.match(serviceWorkerSource, /caBX/);
  });

  it('detects JPEG by SOI marker (0xFF 0xD8)', () => {
    assert.match(serviceWorkerSource, /0xFF/);
    assert.match(serviceWorkerSource, /0xD8/);
  });

  it('detects PNG by magic bytes (0x89 PNG)', () => {
    assert.match(serviceWorkerSource, /0x89/);
    assert.match(serviceWorkerSource, /0x50/);
  });
});

// -----------------------------------------------------------------------
// Auto-Scan Pipeline
// -----------------------------------------------------------------------
describe('detector: auto-scan pipeline', () => {
  it('defines _autoScanImages function', () => {
    assert.match(detectorSource, /async function _autoScanImages\(\)/);
  });

  it('has configurable scan limit (AUTO_SCAN_MAX_IMAGES = 20)', () => {
    assert.match(detectorSource, /AUTO_SCAN_MAX_IMAGES\s*=\s*20/);
  });

  it('has concurrency limit (AUTO_SCAN_MAX_CONCURRENT = 3)', () => {
    assert.match(detectorSource, /AUTO_SCAN_MAX_CONCURRENT\s*=\s*3/);
  });

  it('calls _autoScanImages after image inventory in scanPage', () => {
    const scanPageStart = detectorSource.indexOf('async function scanPage');
    const scanPageEnd = detectorSource.indexOf('function _scanAudioVideo') > scanPageStart
      ? detectorSource.indexOf('function _scanAudioVideo')
      : detectorSource.indexOf('function observeDOM');
    const scanPageFn = detectorSource.slice(scanPageStart, scanPageEnd);
    assert.match(scanPageFn, /_autoScanImages\(\)/);
  });

  it('checks autoScanImages setting before running', () => {
    assert.match(detectorSource, /autoScanImages/);
  });

  it('uses requestIdleCallback to avoid blocking rendering', () => {
    assert.match(detectorSource, /requestIdleCallback/);
  });

  it('auto-verifies images where C2PA header is detected', () => {
    // After _checkC2paHeader returns true, calls _verifyImageAndBadge
    const autoScanFn = detectorSource.slice(
      detectorSource.indexOf('async function _autoScanImages'),
      detectorSource.indexOf('/**\n * Scan a DOM subtree for audio')
    );
    assert.match(autoScanFn, /_verifyImageAndBadge\(img,\s*src\)/);
  });
});

// -----------------------------------------------------------------------
// Performance and Bandwidth
// -----------------------------------------------------------------------
describe('detector: auto-scan bandwidth and circuit breaker', () => {
  it('tracks total bandwidth with _autoScanBytesUsed', () => {
    assert.match(detectorSource, /let _autoScanBytesUsed\s*=\s*0/);
  });

  it('has bandwidth limit of 10MB (AUTO_SCAN_BANDWIDTH_LIMIT)', () => {
    assert.match(detectorSource, /AUTO_SCAN_BANDWIDTH_LIMIT\s*=\s*10\s*\*\s*1024\s*\*\s*1024/);
  });

  it('stops scanning when bandwidth limit exceeded (circuit breaker)', () => {
    assert.match(detectorSource, /_autoScanBytesUsed\s*>\s*AUTO_SCAN_BANDWIDTH_LIMIT/);
  });

  it('has scan cooldown of 5 minutes', () => {
    assert.match(detectorSource, /AUTO_SCAN_COOLDOWN_MS\s*=\s*5\s*\*\s*60\s*\*\s*1000/);
  });

  it('tracks page cooldown with _autoScanPageCooldown map', () => {
    assert.match(detectorSource, /_autoScanPageCooldown/);
  });

  it('skips images already in verification cache', () => {
    const autoScanFn = detectorSource.slice(
      detectorSource.indexOf('async function _autoScanImages'),
      detectorSource.indexOf('/**\n * Scan a DOM subtree for audio')
    );
    assert.match(autoScanFn, /_imageVerificationState\.has\(src\)/);
  });

  it('resets auto-scan state on RESCAN', () => {
    assert.match(detectorSource, /_autoScanBytesUsed\s*=\s*0/);
    assert.match(detectorSource, /_autoScanPageCooldown\.clear\(\)/);
  });
});

// -----------------------------------------------------------------------
// Options: auto-scan toggle
// -----------------------------------------------------------------------
describe('options: auto-scan images toggle', () => {
  it('has autoScanImages checkbox in options HTML', () => {
    assert.match(optionsHtml, /id="autoScanImages"/);
  });

  it('labels the toggle clearly', () => {
    assert.match(optionsHtml, /Auto-scan images for C2PA provenance/);
  });

  it('options JS reads autoScanImages setting', () => {
    assert.match(optionsJs, /autoScanImages/);
  });

  it('options JS includes autoScanImages in DEFAULT_SETTINGS', () => {
    assert.match(optionsJs, /autoScanImages:\s*true/);
  });

  it('options JS saves autoScanImages on change', () => {
    assert.match(optionsJs, /saveSetting\(['"]autoScanImages['"]/);
  });
});
