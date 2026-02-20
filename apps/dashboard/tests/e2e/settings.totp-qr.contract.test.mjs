import assert from 'node:assert';
import { readFile } from 'node:fs/promises';
import { describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';

const DASHBOARD_ROOT = fileURLToPath(new URL('../../', import.meta.url));

describe('Settings TOTP QR setup (contract)', () => {
  it('includes QR-based authenticator setup guidance in settings page source', async () => {
    const settingsPath = `${DASHBOARD_ROOT}/src/app/settings/page.tsx`;
    const source = await readFile(settingsPath, 'utf8');

    assert.match(source, /Scan this QR code with Google Authenticator/i);
    assert.match(source, /otpauth URI/i);
  });
});
