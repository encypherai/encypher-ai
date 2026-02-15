import assert from 'node:assert';
import { readFile } from 'node:fs/promises';
import { describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';

const DASHBOARD_ROOT = fileURLToPath(new URL('../../', import.meta.url));

describe('Dashboard Billing (subscription endpoint intent)', () => {
  it('uses organization/session tier as plan source of truth and does not eagerly fetch legacy subscription endpoint', async () => {
    const billingPagePath = `${DASHBOARD_ROOT}/src/app/billing/page.tsx`;
    const source = await readFile(billingPagePath, 'utf8');

    assert.match(source, /const\s+organizationTier\s*=\s*activeOrganization\?\.tier/);
    assert.match(source, /const\s+rawTier\s*=\s*subscriptionTier\s*\|\|\s*organizationTier\s*\|\|\s*'free'/);
    assert.doesNotMatch(source, /apiClient\.getSubscription\(accessToken\)/);
  });
});
