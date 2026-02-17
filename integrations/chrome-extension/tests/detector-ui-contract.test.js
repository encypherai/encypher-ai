import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

const detectorPath = path.resolve(process.cwd(), 'content', 'detector.js');
const detectorSource = fs.readFileSync(detectorPath, 'utf8');

describe('detector UI contract', () => {
  it('defines a compact hover tooltip builder using detail-panel header styling', () => {
    assert.match(detectorSource, /function\s+_buildHoverTooltipHtml\s*\(/);
    assert.match(detectorSource, /encypher-detail-panel__header/);
    assert.match(detectorSource, /Signing Identity/);
    assert.match(detectorSource, /Click for more information/);
  });

  it('defines a click-panel C2PA manifest disclosure section', () => {
    assert.match(detectorSource, /function\s+_buildC2paManifestDisclosure\s*\(/);
    assert.match(detectorSource, /encypher-detail-panel__manifest/);
    assert.match(detectorSource, /View full C2PA manifest/);
    assert.match(detectorSource, /<span class="encypher-detail-panel__label">C2PA Validated<\/span>/);
    assert.match(detectorSource, /external manifest/);
    assert.match(detectorSource, /embedded manifest/);
  });

  it('dedupes detections by element before applying cached or pending badges', () => {
    assert.match(detectorSource, /function\s+_dedupeDetectionsByElement\s*\(/);
    assert.match(detectorSource, /uncached\s*=\s*_dedupeDetectionsByElement\(uncached\)/);
    assert.match(detectorSource, /cached\s*=\s*_dedupeDetectionsByElement\(cached\)/);
  });
});
