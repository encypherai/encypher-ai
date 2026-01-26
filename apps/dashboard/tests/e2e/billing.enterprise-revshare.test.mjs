import assert from 'node:assert';
import { readFile } from 'node:fs/promises';
import { describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';

const DASHBOARD_ROOT = fileURLToPath(new URL('../../', import.meta.url));

describe('Dashboard Billing (enterprise rev share)', () => {
  it('does not display the enterprise revenue share string in the billing page source', async () => {
    const billingPagePath = `${DASHBOARD_ROOT}/src/app/billing/page.tsx`;
    const source = await readFile(billingPagePath, 'utf8');

    assert.doesNotMatch(source, /80%\s+you\s*\/\s*20%\s+Encypher/i);
  });

  it('does not display coalition rev-share percentages for self-serve tiers in the billing page source', async () => {
    const billingPagePath = `${DASHBOARD_ROOT}/src/app/billing/page.tsx`;
    const source = await readFile(billingPagePath, 'utf8');

    assert.doesNotMatch(source, /65\s*%\s*\/?\s*35\s*%/i);
    assert.doesNotMatch(source, /70\s*%\s*\/?\s*30\s*%/i);
    assert.doesNotMatch(source, /75\s*%\s*\/?\s*25\s*%/i);
  });
});
