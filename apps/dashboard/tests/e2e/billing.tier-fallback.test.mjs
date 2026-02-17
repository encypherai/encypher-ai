import assert from 'node:assert';
import { readFile } from 'node:fs/promises';
import { describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';

const DASHBOARD_ROOT = fileURLToPath(new URL('../../', import.meta.url));

describe('Dashboard Billing (tier fallback)', () => {
  it('includes logic to refresh billing data after checkout and ignore unknown tiers', async () => {
    const billingPagePath = `${DASHBOARD_ROOT}/src/app/billing/page.tsx`;
    const source = await readFile(billingPagePath, 'utf8');

    assert.match(source, /useSearchParams\s*\(/);
    assert.match(source, /success|upgrade/);
    assert.match(source, /subscription\.tier\s*!==\s*'unknown'/);
    assert.match(source, /\['starter',\s*'free',\s*'basic'\]\.includes\(rawTier\)/);
    assert.match(source, /unknown/i);
  });
});
