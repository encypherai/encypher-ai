import assert from 'node:assert';
import { readFile } from 'node:fs/promises';
import { access } from 'node:fs/promises';
import { describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';

const DASHBOARD_ROOT = fileURLToPath(new URL('../../', import.meta.url));

describe('Integrations page (contract)', () => {
  it('surfaces WordPress plugin setup and direct download actions', async () => {
    const integrationsPath = `${DASHBOARD_ROOT}/src/app/integrations/page.tsx`;
    const source = await readFile(integrationsPath, 'utf8');

    assert.match(source, /name:\s*'WordPress'/i);
    assert.match(source, /Download plugin/i);
    assert.match(source, /\/downloads\/encypher-provenance-1\.0\.0-beta\.zip/i);
  });

  it('bundles the beta zip under dashboard public downloads', async () => {
    const zipPath = `${DASHBOARD_ROOT}/public/downloads/encypher-provenance-1.0.0-beta.zip`;
    await access(zipPath);
  });
});
