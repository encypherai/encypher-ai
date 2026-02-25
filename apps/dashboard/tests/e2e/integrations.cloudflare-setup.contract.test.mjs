import assert from 'node:assert';
import { readFile } from 'node:fs/promises';
import { describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';

const DASHBOARD_ROOT = fileURLToPath(new URL('../../', import.meta.url));

describe('Cloudflare integration setup flow (contract)', () => {
  it('generates and saves a webhook secret immediately when setup starts', async () => {
    const cardPath = `${DASHBOARD_ROOT}/src/app/integrations/CloudflareIntegrationCard.tsx`;
    const source = await readFile(cardPath, 'utf8');

    assert.match(source, /const newSecret = generateSecret\(\);/);
    assert.match(source, /saveMutation\.mutate\(newSecret\);/);
    assert.doesNotMatch(source, /You can also enter your own 16\+ character value\./);
  });

  it('shows webhook URL and secret together in step 1 after setup starts', async () => {
    const cardPath = `${DASHBOARD_ROOT}/src/app/integrations/CloudflareIntegrationCard.tsx`;
    const source = await readFile(cardPath, 'utf8');

    assert.match(source, /Step 1: Copy destination URL and secret/i);
    assert.match(source, /Logpush Destination URL/);
    assert.match(source, /Webhook Secret/);
  });
});
