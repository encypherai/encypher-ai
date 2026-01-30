import assert from 'node:assert';
import { spawn } from 'node:child_process';
import { createServer } from 'node:net';
import { after, before, describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';

import puppeteer from 'puppeteer';
import { encode } from 'next-auth/jwt';

const DASHBOARD_ROOT = fileURLToPath(new URL('../../', import.meta.url));

function getFreePort() {
  return new Promise((resolve, reject) => {
    const server = createServer();
    server.unref();
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      if (!address || typeof address === 'string') {
        server.close(() => reject(new Error('Failed to acquire a free port')));
        return;
      }
      const port = address.port;
      server.close(() => resolve(port));
    });
  });
}

function startDashboardDevServer() {
  return new Promise(async (resolve, reject) => {
    const requestedPort = process.env.DASHBOARD_E2E_PORT || String(await getFreePort());
    const baseUrl = `http://localhost:${requestedPort}`;
    const nextBin = `${DASHBOARD_ROOT}/node_modules/.bin/next`;
    console.log(`[e2e] Starting dashboard dev server on ${baseUrl}`);
    const proc = spawn(nextBin, ['dev', '-p', requestedPort], {
      cwd: DASHBOARD_ROOT,
      env: {
        ...process.env,
        NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET || 'test-secret',
        NEXTAUTH_URL: process.env.NEXTAUTH_URL || baseUrl,
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || `${baseUrl}/api/v1`,
        NEXT_PUBLIC_DISABLE_COOKIE_CONSENT: 'true',
        NEXT_PUBLIC_E2E_TEST: process.env.NEXT_PUBLIC_E2E_TEST || 'true',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let ready = false;
    let output = '';

    const appendOutput = (chunk) => {
      output += chunk.toString();
      if (output.length > 50_000) {
        output = output.slice(-50_000);
      }
    };

    const onData = (data) => {
      const text = data.toString();
      appendOutput(text);
      if (process.env.E2E_DEBUG) {
        console.log(`[e2e][next] ${text.trim()}`);
      }

      if (!ready && /(ready|started server|local:)/i.test(text)) {
        ready = true;
        cleanup();
        console.log('[e2e] Dashboard dev server ready');
        resolve({ proc, baseUrl });
      }
    };

    const onExit = (code) => {
      if (!ready) {
        cleanup();
        reject(new Error(`Dashboard dev server exited early with code ${code}. Recent output:\n\n${output}`));
      }
    };

    const onError = (err) => {
      if (!ready) {
        cleanup();
        reject(new Error(`Dashboard dev server spawn failed: ${err.message}`));
      }
    };

    const cleanup = () => {
      proc.stdout?.off('data', onData);
      proc.stderr?.off('data', onData);
      proc.off('exit', onExit);
      proc.off('error', onError);
    };

    proc.stdout?.on('data', onData);
    proc.stderr?.on('data', onData);
    proc.on('exit', onExit);
    proc.on('error', onError);

    setTimeout(() => {
      if (!ready) {
        cleanup();
        proc.kill('SIGTERM');
        reject(new Error(`Dashboard dev server did not become ready in time. Recent output:\n\n${output}`));
      }
    }, 60_000);
  });
}

async function installApiMocks(page, dashboardUrl) {
  const apiBase = `${dashboardUrl}/api/v1`;
  const testOrg = {
    id: 'org_trial',
    name: 'Trial Org',
    slug: null,
    email: 'billing@trial-org.test',
    tier: 'business',
    max_seats: 5,
    subscription_status: 'active',
    created_at: new Date().toISOString(),
  };

  const seatInfo = {
    used: 0,
    active: 0,
    pending: 0,
    max: 5,
    available: 5,
    unlimited: false,
  };

  const invitations = [
    {
      id: 'inv_1',
      email: 'pending@trial-org.test',
      role: 'member',
      status: 'pending',
      expires_at: new Date(Date.now() + 86400000).toISOString(),
      created_at: new Date().toISOString(),
      tier: 'business',
      trial_months: 3,
    },
  ];

  const session = {
    user: {
      name: 'Trial Admin',
      email: 'admin@trial-org.test',
      accessToken: 'test-access-token',
      tier: 'business',
    },
    expires: '2099-01-01T00:00:00.000Z',
  };

  const secret = process.env.NEXTAUTH_SECRET || 'test-secret';
  const token = await encode({
    token: {
      sub: 'user_trial_admin',
      email: session.user.email,
      name: session.user.name,
      accessToken: session.user.accessToken,
      tier: session.user.tier,
    },
    secret,
  });

  await page.setCookie({
    name: 'next-auth.session-token',
    value: token,
    url: dashboardUrl,
    httpOnly: true,
  });
  console.log('[e2e] Session cookie set');

  const jsonRespond = async (request, body, status = 200) => {
    await request.respond({
      status,
      contentType: 'application/json',
      body: JSON.stringify(body),
    });
  };

  let resolveInvitePayload;
  let invitePayloadResolved = false;
  const invitePayloadPromise = new Promise((resolve) => {
    resolveInvitePayload = (payload) => {
      if (invitePayloadResolved) {
        return;
      }
      invitePayloadResolved = true;
      resolve(payload);
    };
  });
  page.once('close', () => {
    if (resolveInvitePayload) {
      resolveInvitePayload(null);
    }
  });
  console.log('[e2e] Enabling request interception');
  try {
    await Promise.race([
      page.setRequestInterception(true),
      new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Timed out enabling request interception')), 5_000);
      }),
    ]);
  } catch (error) {
    console.error('[e2e] Failed to enable request interception', error);
    throw error;
  }
  console.log('[e2e] Request interception enabled');
  page.on('request', async (request) => {
    const url = request.url();
    const method = request.method();
    if (process.env.E2E_DEBUG) {
      console.log(`[e2e][request] ${method} ${url}`);
    }

    if (method === 'GET' && url.includes('/api/auth/session')) {
      await jsonRespond(request, session);
      return;
    }

    if (url.includes('/api/auth/')) {
      if (method === 'GET' && url.includes('/api/auth/providers')) {
        await jsonRespond(request, { credentials: { id: 'credentials', name: 'credentials', type: 'credentials' } });
        return;
      }
      if (method === 'GET' && url.includes('/api/auth/csrf')) {
        await jsonRespond(request, { csrfToken: 'csrf' });
        return;
      }
      await jsonRespond(request, {});
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/auth/admin/is-super-admin`)) {
      await jsonRespond(request, { success: true, data: { is_super_admin: true }, error: null });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/organizations`)) {
      await jsonRespond(request, { success: true, data: [testOrg], error: null });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/organizations/${testOrg.id}/seats`)) {
      await jsonRespond(request, { success: true, data: seatInfo, error: null });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/organizations/${testOrg.id}/members`)) {
      await jsonRespond(request, { success: true, data: [], error: null });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/organizations/${testOrg.id}/invitations`)) {
      await jsonRespond(request, { success: true, data: invitations, error: null });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/keys?organization_id=${testOrg.id}`)) {
      await jsonRespond(request, []);
      return;
    }

    if (method === 'POST' && url.startsWith(`${apiBase}/organizations/${testOrg.id}/invitations`)) {
      const body = request.postData() || '{}';
      console.log(`[e2e] Captured invite payload: ${body}`);
      resolveInvitePayload(JSON.parse(body));
      await jsonRespond(request, { success: true, data: { id: 'inv_new' }, error: null });
      return;
    }

    await request.continue();
  });

  return { invitePayloadPromise };
}

describe('team invite trial flow', () => {
  let server;
  let browser;

  before(async () => {
    server = await startDashboardDevServer();
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    });
  });

  after(async () => {
    if (browser) {
      await browser.close();
    }
    if (server?.proc) {
      server.proc.kill('SIGTERM');
    }
  });

  it('sends tiered trial invites for super admins', { timeout: 120_000 }, async () => {
    const page = await browser.newPage();
    console.log('[e2e] Installing API mocks');
    const { invitePayloadPromise } = await installApiMocks(page, server.baseUrl);
    console.log('[e2e] API mocks ready');

    page.on('console', (message) => {
      console.log(`[e2e][console] ${message.type()}: ${message.text()}`);
    });
    page.on('pageerror', (error) => {
      console.log(`[e2e][pageerror] ${error.message}`);
    });
    page.on('requestfailed', (request) => {
      const failure = request.failure();
      console.log(`[e2e][requestfailed] ${request.method()} ${request.url()} ${failure?.errorText || ''}`);
    });

    console.log('[e2e] Navigating to team page');
    await page.goto(`${server.baseUrl}/team`, { waitUntil: 'domcontentloaded', timeout: 30_000 });
    await page.waitForFunction(() => {
      const text = document.body?.textContent || '';
      return text.includes('Trial: business');
    }, { timeout: 15_000 });
    const content = await page.content();
    assert.match(content, /Trial: business/i);

    console.log('[e2e] Opening invite form');
    await page.waitForSelector('[data-testid="invite-email"]', { timeout: 15_000 });

    await page.waitForSelector('[data-testid="invite-submit"]', { timeout: 15_000 });
    await page.waitForSelector('[data-testid="invite-tier"]', { timeout: 15_000 });

    console.log('[e2e] Filling invite form');
    await page.type('[data-testid="invite-email"]', 'new@trial-org.test');
    await page.select('[data-testid="invite-role"]', 'member');
    await page.select('[data-testid="invite-tier"]', 'business');
    await page.type('[data-testid="invite-trial-months"]', '3');

    console.log('[e2e] Submitting invite form');
    await page.click('[data-testid="invite-submit"]');

    const payload = await Promise.race([
      invitePayloadPromise,
      new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Timed out waiting for invite payload')), 20_000);
      }),
    ]);
    assert.ok(payload, 'Invite payload was not captured.');
    assert.equal(payload.email, 'new@trial-org.test');
    assert.equal(payload.role, 'member');
    assert.equal(payload.tier, 'business');
    assert.equal(payload.trial_months, 3);

    await page.close();
  });
});
