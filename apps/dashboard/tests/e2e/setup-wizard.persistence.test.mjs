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
        server.close(() => reject(new Error('Failed to acquire free port')));
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
        reject(new Error(`Dashboard dev server exited with code ${code}.\n${output}`));
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
        reject(new Error(`Dashboard dev server did not become ready in time.\n${output}`));
      }
    }, 60_000);
  });
}

async function installMocks(page, dashboardUrl) {
  const apiBase = `${dashboardUrl}/api/v1`;
  const session = {
    user: {
      name: 'Setup Tester',
      email: 'setup@test.local',
      accessToken: 'test-access-token',
      tier: 'free',
    },
    expires: '2099-01-01T00:00:00.000Z',
  };

  const secret = process.env.NEXTAUTH_SECRET || 'test-secret';
  const token = await encode({
    token: {
      sub: 'user_setup',
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

  let setupStatusCalls = 0;

  await page.setRequestInterception(true);
  page.on('request', async (request) => {
    const url = request.url();
    const method = request.method();

    const respondJson = async (body, status = 200) => {
      await request.respond({
        status,
        contentType: 'application/json',
        body: JSON.stringify(body),
      });
    };

    if (method === 'GET' && url.includes('/api/auth/session')) {
      await respondJson(session);
      return;
    }

    if (url.includes('/api/auth/')) {
      if (method === 'GET' && url.includes('/api/auth/providers')) {
        await respondJson({ credentials: { id: 'credentials', name: 'credentials', type: 'credentials' } });
        return;
      }
      if (method === 'GET' && url.includes('/api/auth/csrf')) {
        await respondJson({ csrfToken: 'csrf' });
        return;
      }
      await respondJson({});
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/auth/admin/is-super-admin`)) {
      await respondJson({ success: true, data: { is_super_admin: false }, error: null });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/auth/setup-status`)) {
      setupStatusCalls += 1;
      if (setupStatusCalls === 1) {
        await respondJson({
          success: true,
          data: {
            setup_completed: false,
            setup_completed_at: null,
            account_type: null,
            display_name: null,
          },
          error: null,
        });
        return;
      }

      // Simulate transient bad payload on a later refetch
      await respondJson({ success: true, data: null, error: null });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/auth/onboarding-status`)) {
      await respondJson({
        success: true,
        data: {
          steps: [],
          completed_count: 0,
          total_count: 0,
          all_completed: true,
          dismissed: true,
          completed_at: null,
        },
        error: null,
      });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/organizations`)) {
      await respondJson({
        success: true,
        data: [
          {
            id: 'org_setup',
            name: 'Setup Org',
            slug: 'setup-org',
            email: 'setup@test.local',
            tier: 'free',
            max_seats: 1,
            subscription_status: 'active',
            created_at: '2026-01-01T00:00:00Z',
          },
        ],
        error: null,
      });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/analytics/usage`)) {
      await respondJson({
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

    if (method === 'GET' && url.startsWith(`${apiBase}/keys`)) {
      await respondJson([]);
      return;
    }

    await request.continue();
  });

  return {
    getSetupStatusCalls: () => setupStatusCalls,
  };
}

describe('setup wizard persistence', () => {
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
    if (browser) await browser.close();
    if (server?.proc) server.proc.kill('SIGTERM');
  });

  it('keeps the setup wizard visible on display-name step across transient setup-status payload issues', { timeout: 180_000 }, async () => {
    const page = await browser.newPage();
    const mocks = await installMocks(page, server.baseUrl);

    await page.goto(`${server.baseUrl}/`, { waitUntil: 'domcontentloaded', timeout: 30_000 });

    await page.waitForSelector('text/Welcome to Encypher', { timeout: 20_000 });
    await page.click('text/Independent creator');
    await page.waitForSelector('text/Your name or pen name', { timeout: 20_000 });

    // Make the setup-status query stale then trigger a focus refetch.
    await page.evaluate(() => {
      const realNow = Date.now.bind(Date);
      // @ts-ignore - test-only override
      window.__realDateNow = realNow;
      Date.now = () => realNow() + 120_000;
    });

    const bgPage = await browser.newPage();
    await bgPage.goto('about:blank');
    await bgPage.bringToFront();
    await page.bringToFront();

    await page.evaluate(() => {
      window.dispatchEvent(new Event('focus'));
      document.dispatchEvent(new Event('visibilitychange'));
    });

    await page.waitForFunction(() => document.body.innerText.includes('Your name or pen name'), {
      timeout: 20_000,
    });

    assert.ok(mocks.getSetupStatusCalls() >= 2, 'expected setup-status to be called at least twice');

    await bgPage.close();
    await page.close();
  });
});
