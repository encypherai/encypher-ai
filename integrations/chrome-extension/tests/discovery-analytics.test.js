import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const EXTENSION_ROOT = path.resolve(__dirname, '..');

describe('Discovery analytics privacy + cross-domain tracking', () => {
  it('sanitizes discovery URLs before upload so query/hash user tokens are excluded', () => {
    const workerPath = path.join(EXTENSION_ROOT, 'background', 'service-worker.js');
    const workerCode = fs.readFileSync(workerPath, 'utf8');

    assert.match(
      workerCode,
      /function\s+sanitizeDiscoveryUrl\(/,
      'Service worker should define a dedicated URL sanitizer for analytics payloads'
    );

    assert.match(
      workerCode,
      /sanitized\.search\s*=\s*''/,
      'Sanitizer should explicitly strip URL query parameters from discovery payloads'
    );

    assert.match(
      workerCode,
      /sanitized\.hash\s*=\s*''/,
      'Sanitizer should explicitly strip URL fragments from discovery payloads'
    );
  });

  it('computes domain mismatch and records mismatch metadata in discovery events', () => {
    const workerPath = path.join(EXTENSION_ROOT, 'background', 'service-worker.js');
    const workerCode = fs.readFileSync(workerPath, 'utf8');

    assert.match(
      workerCode,
      /function\s+deriveDomainMismatch\(/,
      'Service worker should define domain mismatch derivation helper for discovery analytics'
    );

    assert.match(
      workerCode,
      /pageDomain\s*!==\s*originalDomain/,
      'Domain mismatch helper should compare current page domain against original domain'
    );

    assert.match(
      workerCode,
      /domainMismatch:\s*mismatch\.domainMismatch/,
      'Discovery event payload should include the computed domainMismatch flag'
    );

    assert.match(
      workerCode,
      /mismatchReason:\s*mismatch\.reason/,
      'Discovery event payload should include why an event was considered mismatched'
    );
  });

  it('tracks cached detections too so repeat embedding discoveries still phone home', () => {
    const workerPath = path.join(EXTENSION_ROOT, 'background', 'service-worker.js');
    const workerCode = fs.readFileSync(workerPath, 'utf8');

    assert.match(
      workerCode,
      /case\s+'REPORT_CACHED_DETECTION'[\s\S]*trackEmbeddingDiscovery\(/,
      'Cached detection handler should report discovery analytics, not just update popup counts'
    );

    assert.match(
      workerCode,
      /discoverySource:\s*'cached_detection'/,
      'Cached detection analytics events should identify their source as cached_detection'
    );
  });

  it('includes useful non-PII embedding context fields in discovery analytics events', () => {
    const workerPath = path.join(EXTENSION_ROOT, 'background', 'service-worker.js');
    const workerCode = fs.readFileSync(workerPath, 'utf8');

    assert.match(
      workerCode,
      /contentLengthBucket:/,
      'Discovery payload should include a content length bucket for aggregate analysis'
    );

    assert.match(
      workerCode,
      /embeddingByteLength:/,
      'Discovery payload should include embedding byte length signal for quality analytics'
    );

    assert.match(
      workerCode,
      /discoverySource:/,
      'Discovery payload should include the discovery source context'
    );
  });

  it('shows always-on analytics disclosure in options UI instead of a fake toggle', () => {
    const optionsHtmlPath = path.join(EXTENSION_ROOT, 'options', 'options.html');
    const optionsHtml = fs.readFileSync(optionsHtmlPath, 'utf8');
    const optionsJsPath = path.join(EXTENSION_ROOT, 'options', 'options.js');
    const optionsJs = fs.readFileSync(optionsJsPath, 'utf8');

    assert.doesNotMatch(
      optionsHtml,
      /id="analyticsEnabled"/,
      'Options should not display an analytics on/off checkbox when discovery tracking is non-optional'
    );

    assert.match(
      optionsHtml,
      /always\s+on/i,
      'Options should clearly disclose discovery tracking as always on'
    );

    assert.match(
      optionsHtml,
      /no\s+personal\s+data/i,
      'Options should clearly explain that discovery tracking excludes personal user data'
    );

    assert.doesNotMatch(
      optionsJs,
      /SET_ANALYTICS_ENABLED/,
      'Options logic should not attempt to toggle always-on discovery tracking in the service worker'
    );
  });
});
