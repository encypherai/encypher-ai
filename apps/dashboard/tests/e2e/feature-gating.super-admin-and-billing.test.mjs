import assert from 'node:assert';
import { readFile } from 'node:fs/promises';
import { describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';

const DASHBOARD_ROOT = fileURLToPath(new URL('../../', import.meta.url));

describe('dashboard feature gating (super-admin + billing)', () => {
  it('shows a non-free label for enterprise plans without a fixed recurring amount', async () => {
    const billingPagePath = `${DASHBOARD_ROOT}/src/app/billing/page.tsx`;
    const source = await readFile(billingPagePath, 'utf8');

    assert.match(source, /const\s+currentPriceLabel\s*=/);
    assert.match(source, /currentTier\s*===\s*'enterprise'/);
    assert.match(source, /Custom/i);
  });

  it('allows super admins to pass audit-log feature gating', async () => {
    const auditLogsPagePath = `${DASHBOARD_ROOT}/src/app/audit-logs/page.tsx`;
    const source = await readFile(auditLogsPagePath, 'utf8');

    assert.match(source, /isSuperAdmin\s*===\s*true/);
    assert.match(source, /const\s+hasAuditFeature\s*=\s*.*userTier\s*===\s*'enterprise'.*\|\|.*isSuperAdmin\s*===\s*true/s);
  });

  it('keeps enterprise nav items visible for super admins', async () => {
    const layoutPath = `${DASHBOARD_ROOT}/src/components/layout/DashboardLayout.tsx`;
    const source = await readFile(layoutPath, 'utf8');

    assert.match(source, /!item\.enterpriseOnly\s*\|\|\s*isEnterprise\s*\|\|\s*isAdmin/);
  });
});
