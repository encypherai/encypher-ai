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
    const proc = spawn(nextBin, ['dev', '-p', requestedPort], {
      cwd: DASHBOARD_ROOT,
      env: {
        ...process.env,
        NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET || 'test-secret',
        NEXTAUTH_URL: process.env.NEXTAUTH_URL || baseUrl,
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || `${baseUrl}/api/v1`,
        NEXT_PUBLIC_DISABLE_COOKIE_CONSENT: 'true',
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

      if (!ready && /(ready|started server|local:)/i.test(text)) {
        ready = true;
        cleanup();
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
    id: 'org_test',
    name: 'Test Org',
    slug: null,
    email: 'test@encypherai.com',
    tier: 'starter',
    max_seats: 1,
    subscription_status: 'active',
    created_at: new Date().toISOString(),
  };

  const keys = [
    {
      id: 'key_1',
      name: 'Key One',
      fingerprint: 'abc12345',
      permissions: ['sign', 'verify', 'read'],
      created_at: new Date().toISOString(),
      last_used_at: null,
      is_revoked: false,
      user_id: 'user_test',
      created_by: 'user_test',
    },
    {
      id: 'key_2',
      name: 'Key Two',
      fingerprint: 'def67890',
      permissions: ['sign', 'verify', 'read'],
      created_at: new Date().toISOString(),
      last_used_at: null,
      is_revoked: false,
      user_id: 'user_test',
      created_by: 'user_test',
    },
  ];

  const session = {
    user: {
      name: 'Test User',
      email: 'test@encypherai.com',
      accessToken: 'test-access-token',
    },
    expires: '2099-01-01T00:00:00.000Z',
  };

  const secret = process.env.NEXTAUTH_SECRET || 'test-secret';
  const token = await encode({
    token: {
      sub: 'user_test',
      email: session.user.email,
      name: session.user.name,
      accessToken: session.user.accessToken,
    },
    secret,
  });

  await page.setCookie({
    name: 'next-auth.session-token',
    value: token,
    url: dashboardUrl,
    httpOnly: true,
  });

  const jsonRespond = async (request, body, status = 200) => {
    await request.respond({
      status,
      contentType: 'application/json',
      body: JSON.stringify(body),
    });
  };

  await page.setRequestInterception(true);
  page.on('request', async (request) => {
    const url = request.url();
    const method = request.method();

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

    if (method === 'GET' && url.startsWith(`${apiBase}/organizations`)) {
      await jsonRespond(request, { success: true, data: [testOrg], error: null });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/keys`)) {
      await jsonRespond(request, keys);
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/analytics/usage`)) {
      await jsonRespond(request, {
        total_api_calls: 0,
        total_documents_signed: 0,
        total_verifications: 0,
        success_rate: 0,
        avg_response_time_ms: 0,
        period_start: '1970-01-01T00:00:00.000Z',
        period_end: '1970-01-01T00:00:00.000Z',
      });
      return;
    }

    await request.continue();
  });
}

describe('Dashboard API keys overview consistency', () => {
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

  it('uses organization-scoped key list on overview and api-keys page', async () => {
    const page = await browser.newPage();
    await installApiMocks(page, server.baseUrl);

    const waitForOrgScopedKeysRequest = () =>
      page.waitForRequest(
        (request) =>
          request.method() === 'GET' &&
          request.url().includes('/api/v1/keys') &&
          request.url().includes('organization_id=org_test'),
        { timeout: 30_000 }
      );

    await Promise.all([
      waitForOrgScopedKeysRequest(),
      page.goto(`${server.baseUrl}/`, { waitUntil: 'domcontentloaded' }),
    ]);

    await Promise.all([
      waitForOrgScopedKeysRequest(),
      page.goto(`${server.baseUrl}/api-keys`, { waitUntil: 'domcontentloaded' }),
    ]);

    await page.close();
  });
});
