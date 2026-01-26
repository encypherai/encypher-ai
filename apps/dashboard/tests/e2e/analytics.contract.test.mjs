import assert from 'node:assert';
import { readFile } from 'node:fs/promises';
import { describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';

const DASHBOARD_ROOT = fileURLToPath(new URL('../../', import.meta.url));

describe('Analytics dashboard (contract)', () => {
  it('includes activity timeline and usage highlight sections', async () => {
    const analyticsPath = `${DASHBOARD_ROOT}/src/app/analytics/page.tsx`;
    const source = await readFile(analyticsPath, 'utf8');

    assert.match(source, /Activity Timeline/i);
    assert.match(source, /Usage Highlights/i);
    assert.match(source, /Response Health/i);
  });

  it('renders descriptive log metadata labels', async () => {
    const activityFeedPath = `${DASHBOARD_ROOT}/src/components/ActivityFeed.tsx`;
    const source = await readFile(activityFeedPath, 'utf8');

    assert.match(source, /Endpoint/i);
    assert.match(source, /Latency/i);
    assert.match(source, /Status/i);
  });
});
