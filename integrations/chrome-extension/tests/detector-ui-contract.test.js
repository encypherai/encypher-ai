import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

const detectorPath = path.resolve(process.cwd(), 'content', 'detector.js');
const detectorSource = fs.readFileSync(detectorPath, 'utf8');

describe('detector UI contract', () => {
  it('defines a global hover tooltip system mounted on body to escape stacking contexts', () => {
    assert.match(detectorSource, /function\s+_getGlobalTooltip\s*\(/);
    assert.match(detectorSource, /function\s+_showBadgeTooltip\s*\(/);
    assert.match(detectorSource, /function\s+_hideBadgeTooltip\s*\(/);
    assert.match(detectorSource, /function\s+_attachBadgeTooltip\s*\(/);
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

  it('tracks in-flight verifications by textHash so DOM-expanded elements subscribe to the existing promise instead of getting a stuck pending badge', () => {
    assert.match(detectorSource, /_verificationInFlight/);
    assert.match(detectorSource, /_verificationInFlight\.has\(detection\.textHash\)/);
    assert.match(detectorSource, /_verificationInFlight\.set\(detection\.textHash/);
    assert.match(detectorSource, /_verificationInFlight\.delete\(detection\.textHash\)/);
  });

  it('resolves pending badges on newly-expanded elements when an in-flight verification for the same hash completes', () => {
    assert.match(detectorSource, /_pendingElementsByHash/);
    assert.match(detectorSource, /_pendingElementsByHash\.get\(/);
    assert.match(detectorSource, /_pendingElementsByHash\.set\(/);
  });

  it('sweeps orphaned pending badges on hidden ancestors after verification completes (cross-hash LinkedIn see-more case)', () => {
    assert.match(detectorSource, /function\s+_sweepOrphanedPendingBadges\s*\(/);
    assert.match(detectorSource, /display.*none|visibility.*hidden/);
    assert.match(detectorSource, /_sweepOrphanedPendingBadges\(\)/);
    assert.match(detectorSource, /_pendingBadgesByHash/);
  });
});
