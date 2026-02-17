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

  it('audit logs page is wired for API telemetry troubleshooting', async () => {
    const auditLogsPath = `${DASHBOARD_ROOT}/src/app/audit-logs/page.tsx`;
    const source = await readFile(auditLogsPath, 'utf8');

    assert.match(source, /\/analytics\/activity\/audit-events/);
    assert.match(source, /API key/i);
    assert.match(source, /Stack trace|Error details|Request ID|Severity/i);
    assert.match(source, /Export CSV|Export JSON/i);
    assert.match(source, /Failure Rate|Critical Failures|Top Error Codes/i);
    assert.match(source, /Date Range|Last 24 Hours|Last 7 Days|Last 30 Days|Custom Range/i);
    assert.match(source, /Event Types|Severities/i);
    assert.match(source, /Only failures with stack trace/i);
    assert.match(source, /Saved Views|Save current view/i);
  });
});
