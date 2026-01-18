import assert from 'node:assert';
import { readFile } from 'node:fs/promises';
import { describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';

const DASHBOARD_ROOT = fileURLToPath(new URL('../../', import.meta.url));

describe('Settings domain claims (contract)', () => {
  it('includes domain claim copy in settings page source', async () => {
    const settingsPath = `${DASHBOARD_ROOT}/src/app/settings/page.tsx`;
    const source = await readFile(settingsPath, 'utf8');

    assert.match(source, /Organization domains/i);
    assert.match(source, /Domain claims/i);
    assert.match(source, /Request verification/i);
  });
});
