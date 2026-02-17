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
      name: 'Audit Tester',
      email: 'audit@test.local',
      accessToken: 'test-access-token',
      tier: 'enterprise',
    },
    expires: '2099-01-01T00:00:00.000Z',
  };

  const secret = process.env.NEXTAUTH_SECRET || 'test-secret';
  const token = await encode({
    token: {
      sub: 'user_audit',
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
      await respondJson({ success: true, data: { is_super_admin: true }, error: null });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/organizations`)) {
      await respondJson({
        success: true,
        data: [
          {
            id: 'org_demo',
            name: 'Demo Org',
            slug: 'demo-org',
            email: 'ops@demo.org',
            tier: 'enterprise',
            max_seats: 10,
            subscription_status: 'active',
            created_at: '2026-01-01T00:00:00Z',
          },
        ],
        error: null,
      });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/analytics/activity/audit-events/alerts`)) {
      await respondJson({
        total_requests: 3,
        failure_requests: 1,
        critical_failures: 1,
        failure_rate: 33.33,
        top_error_codes: [
          { error_code: 'E_VERIFY', count: 1 },
        ],
        period_start: '2026-02-10T00:00:00Z',
        period_end: '2026-02-16T00:00:00Z',
      });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/analytics/activity/audit-events`)) {
      await respondJson({
        items: [
          {
            id: 'metric_1',
            type: 'api_call',
            description: 'Request failed with status 500',
            timestamp: '2026-02-16T00:00:00Z',
            metadata: {
              status: 500,
              endpoint: '/api/v1/verify',
              method: 'POST',
              api_key: 'ency_abc123',
              request_id: 'req_123',
              error_code: 'E_VERIFY',
              error_message: 'Verification failed',
              error_details: 'Manifest parsing error',
              error_stack: 'Traceback (most recent call last): ...',
              severity: 'critical',
              event_type: 'verify.failed',
              actor_type: 'api_key',
              actor_id: 'key_123',
            },
          },
        ],
        total: 1,
        page: 1,
        limit: 25,
      });
      return;
    }

    await request.continue();
  });
}

describe('audit logs telemetry smoke', () => {
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

  it('renders API-key filter and rich failure details', { timeout: 120_000 }, async () => {
    const page = await browser.newPage();
    await installMocks(page, server.baseUrl);

    await page.goto(`${server.baseUrl}/audit-logs`, { waitUntil: 'domcontentloaded', timeout: 30_000 });

    await page.waitForSelector('text/All API keys', { timeout: 20_000 });
    await page.waitForSelector('text/Failures only (4xx/5xx)', { timeout: 20_000 });
    await page.waitForSelector('text/Severities', { timeout: 20_000 });
    await page.waitForSelector('text/Event Types', { timeout: 20_000 });
    await page.waitForSelector('text/Date Range: Last 30 Days', { timeout: 20_000 });
    await page.waitForSelector('text/Only failures with stack trace', { timeout: 20_000 });
    await page.waitForSelector('text/Save current view', { timeout: 20_000 });
    await page.waitForSelector('text/Request ID:', { timeout: 20_000 });
    await page.waitForSelector('text/Error message:', { timeout: 20_000 });
    await page.waitForSelector('text/Stack trace', { timeout: 20_000 });
    await page.waitForSelector('text/Correlate by request ID', { timeout: 20_000 });

    const content = await page.content();
    assert.match(content, /ency_abc123/);
    assert.match(content, /Verification failed/);

    await page.close();
  });
});
