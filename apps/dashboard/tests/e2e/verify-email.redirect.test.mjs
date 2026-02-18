import assert from 'node:assert';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { describe, it } from 'node:test';

const VERIFY_EMAIL_PAGE = fileURLToPath(
  new URL('../../src/app/auth/verify-email/page.tsx', import.meta.url)
);

describe('Verify email auto-login redirect', () => {
  it('uses redirect-based NextAuth sign-in (not redirect:false JSON mode)', async () => {
    const source = await readFile(VERIFY_EMAIL_PAGE, 'utf8');

    assert.match(source, /callbackUrl:\s*'\/'/);
    assert.doesNotMatch(source, /redirect:\s*false/);
  });
});
