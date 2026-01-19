import assert from 'node:assert';
import { spawn } from 'node:child_process';
import { createServer } from 'node:net';
import { after, before, describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';

import puppeteer from 'puppeteer';

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

async function waitForSignupForm(page, baseUrl) {
  let lastError;
  for (let attempt = 0; attempt < 4; attempt += 1) {
    try {
      await page.goto(`${baseUrl}/signup`, { waitUntil: 'domcontentloaded' });
      await page.waitForSelector('input#name', { timeout: 10_000 });
      return;
    } catch (err) {
      lastError = err;
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }
  throw lastError;
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
        reject(
          new Error(`Dashboard dev server exited early with code ${code}. Recent output:\n\n${output}`)
        );
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
        reject(
          new Error(`Dashboard dev server did not become ready in time. Recent output:\n\n${output}`)
        );
      }
    }, 60_000);
  });
}

describe('Signup validation (client)', () => {
  let server;
  let browser;
  let dashboardUrl;

  before(async () => {
    server = await startDashboardDevServer();
    dashboardUrl = server.baseUrl;
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

  it('rejects URL-like names before submit', async () => {
    const page = await browser.newPage();
    await waitForSignupForm(page, dashboardUrl);
    await page.evaluate(() => {
      window.__signupRequests = 0;
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (input, init) => {
        const url = typeof input === 'string' ? input : input?.url;
        if (url && url.includes('/auth/signup')) {
          window.__signupRequests += 1;
          return new Response(JSON.stringify({ success: false, error: { message: 'blocked' } }), {
            status: 400,
            headers: { 'Content-Type': 'application/json' },
          });
        }
        return originalFetch(input, init);
      };
    });
    await page.waitForSelector('input#name');
    await page.waitForSelector('input#email');
    await page.type('input#name', 'Visit https://evil.test now');
    await page.type('input#email', 'user@example.com');
    await page.type('input#password', 'SecurePass123!');
    await page.type('input#confirmPassword', 'SecurePass123!');
    await page.click('button[type="submit"]');

    const errorBanner = await page.waitForSelector('[data-testid="signup-error"]', { timeout: 10_000 });
    const errorText = await errorBanner.evaluate((el) => el.textContent || '');
    assert.match(errorText, /Name cannot contain URLs/i);
    const signupRequests = await page.evaluate(() => window.__signupRequests);
    assert.equal(signupRequests, 0);
    await page.close();
  });

  it('sanitizes HTML name before submit', async () => {
    const page = await browser.newPage();
    await waitForSignupForm(page, dashboardUrl);
    let resolvePayload;
    const payloadPromise = new Promise((resolve) => {
      resolvePayload = resolve;
    });
    await page.setRequestInterception(true);
    page.on('request', (request) => {
      if (request.url().includes('/auth/signup')) {
        let payload = {};
        try {
          payload = JSON.parse(request.postData() || '{}');
        } catch {
          payload = {};
        }
        // TEAM_112: capture sanitized payload submitted to the API.
        resolvePayload(payload);
        request.respond({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              id: 'user_test',
              email: payload.email,
              name: payload.name,
              verification_email_sent: true,
            },
            error: null,
          }),
        });
      } else {
        request.continue();
      }
    });
    await page.waitForSelector('input#name');
    await page.waitForSelector('input#email');
    await page.type('input#name', '<b>Jane Doe</b>');
    await page.type('input#email', 'user@example.com');
    await page.type('input#password', 'SecurePass123!');
    await page.type('input#confirmPassword', 'SecurePass123!');
    await page.click('button[type="submit"]');
    const payload = await payloadPromise;
    assert.ok(payload);
    assert.equal(payload.name, 'Jane Doe');
    assert.equal(payload.email, 'user@example.com');
    await page.close();
  });
});
