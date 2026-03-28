/**
 * E2E test: Playground auto-session auth
 *
 * Verifies that when a user is logged in, the playground:
 * 1. Auto-selects "session" auth (not "custom")
 * 2. Shows the collapsed "Authenticated" badge
 * 3. Shows the "Change method" link
 * 4. Does NOT show the auth form by default
 * 5. Can expand auth to switch methods
 * 6. Has the correct option order (Auto Session first)
 */
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

  const session = {
    user: {
      name: 'Test User',
      email: 'test@encypher.com',
      accessToken: 'test-access-token',
      tier: 'free',
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
      await jsonRespond(request, { success: true, data: [{ id: 'org_test', name: 'Test Org', tier: 'free', subscription_status: 'active', created_at: new Date().toISOString() }], error: null });
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/keys`)) {
      await jsonRespond(request, []);
      return;
    }

    if (method === 'GET' && url.startsWith(`${apiBase}/analytics/usage`)) {
      await jsonRespond(request, { total_api_calls: 0, total_documents_signed: 0, total_verifications: 0, success_rate: 0, avg_response_time_ms: 0 });
      return;
    }

    await request.continue();
  });
}

describe('Playground session auth (auto-auth)', () => {
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

  it('auto-selects session auth and shows Authenticated badge when logged in', async () => {
    const page = await browser.newPage();
    await installApiMocks(page, server.baseUrl);

    await page.goto(`${server.baseUrl}/playground`, { waitUntil: 'networkidle2', timeout: 30_000 });

    // Wait for the page to hydrate and the playground heading to appear
    await page.waitForSelector('h1', { timeout: 15_000 });
    const h1Text = await page.$eval('h1', (el) => el.textContent || '');
    assert.match(h1Text, /api playground/i, 'Should be on the playground page');

    // Verify the "Authenticated" badge is visible (session auth auto-selected)
    const authBadge = await page.waitForSelector('span.rounded-full', { timeout: 10_000 });
    const badgeText = await authBadge.evaluate((el) => el.textContent || '');
    assert.match(badgeText, /authenticated/i, 'Should show Authenticated badge');

    // Verify the "Change method" link is visible (collapsed auth card)
    const changeMethodLink = await page.$('button');
    const allButtons = await page.$$eval('button', (buttons) =>
      buttons.map((b) => b.textContent || '')
    );
    const hasChangeMethod = allButtons.some((t) => /change method/i.test(t));
    assert.ok(hasChangeMethod, 'Should show "Change method" link when auth is collapsed');

    // Verify the auth method select is NOT visible (collapsed state)
    // Check that no select has "session" as a selected value with "Auto" option text
    const authSelectVisible = await page.evaluate(() => {
      const selects = Array.from(document.querySelectorAll('select'));
      return selects.some((s) =>
        Array.from(s.options).some((o) => o.value === 'session' && /auto/i.test(o.textContent || ''))
      );
    });
    assert.strictEqual(authSelectVisible, false, 'Auth method select should be hidden when session is active and collapsed');

    await page.close();
  });

  it('expands auth card when "Change method" is clicked', async () => {
    const page = await browser.newPage();
    await installApiMocks(page, server.baseUrl);

    await page.goto(`${server.baseUrl}/playground`, { waitUntil: 'networkidle2', timeout: 30_000 });
    await page.waitForSelector('h1', { timeout: 15_000 });

    // Click "Change method"
    const changeMethodBtn = await page.evaluateHandle(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.find((b) => /change method/i.test(b.textContent || ''));
    });
    assert.ok(changeMethodBtn, '"Change method" button should exist');
    await changeMethodBtn.click();

    // Wait for the select to appear
    await page.waitForSelector('select', { timeout: 5_000 });

    // Verify the select has "Auto (Session)" as the selected value
    const selectedValue = await page.$eval('select', (el) => el.value);
    assert.strictEqual(selectedValue, 'session', 'Select should have "session" as value');

    // Verify option order: Auto (Session) is first
    const options = await page.$$eval('select option', (opts) =>
      opts.map((o) => ({ value: o.value, text: o.textContent }))
    );
    assert.strictEqual(options[0].value, 'session', 'First option should be "session"');
    assert.match(options[0].text, /auto.*session/i, 'First option text should be "Auto (Session)"');

    await page.close();
  });

  it('shows guided tour with Sign step first when session is active', async () => {
    const page = await browser.newPage();
    await installApiMocks(page, server.baseUrl);

    await page.goto(`${server.baseUrl}/playground`, { waitUntil: 'networkidle2', timeout: 30_000 });
    await page.waitForSelector('h1', { timeout: 15_000 });

    // The tour banner should say "Sign -> Verify" (not "API Key -> Sign -> Verify")
    const tourTitle = await page.$$eval('h3', (elements) =>
      elements.map((el) => el.textContent || '')
    );
    const guidedTourTitle = tourTitle.find((t) => /guided tour/i.test(t));
    assert.ok(guidedTourTitle, 'Should have a guided tour title');
    assert.ok(
      !guidedTourTitle.includes('API Key'),
      'Tour title should NOT mention API Key when session is active'
    );
    assert.match(guidedTourTitle, /sign/i, 'Tour title should mention Sign');

    await page.close();
  });
});
