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

async function waitForLoginPage(page, baseUrl) {
  let title = '';
  for (let attempt = 0; attempt < 5; attempt += 1) {
    await page.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded' });
    const h1 = await page.waitForSelector('h1', { timeout: 15_000 });
    title = await h1.evaluate((el) => el.textContent || '');
    if (/sign into your account/i.test(title)) {
      return;
    }
    // TEAM_112: Avoid Puppeteer waitForTimeout in Node test runner.
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  assert.match(title, /sign into your account/i);
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
        GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID || 'test-google-client-id',
        GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET || 'test-google-client-secret',
        GITHUB_CLIENT_ID: process.env.GITHUB_CLIENT_ID || 'test-github-client-id',
        GITHUB_CLIENT_SECRET: process.env.GITHUB_CLIENT_SECRET || 'test-github-client-secret',
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
          new Error(
            `Dashboard dev server exited early with code ${code}. Recent output:\n\n${output}`
          )
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
          new Error(
            `Dashboard dev server did not become ready in time. Recent output:\n\n${output}`
          )
        );
      }
    }, 60_000);
  });
}

describe('Dashboard Playground (smoke)', () => {
  let server;
  let browser;
  let dashboardUrl;

  before(async () => {
    server = await startDashboardDevServer();
    dashboardUrl = server.baseUrl;
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
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

  it('renders the login page', async () => {
    const page = await browser.newPage();
    await waitForLoginPage(page, dashboardUrl);
    await page.close();
  });

  it('redirects /playground to /login when unauthenticated', async () => {
    const page = await browser.newPage();
    await page.goto(`${dashboardUrl}/playground`, { waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => window.location.pathname.startsWith('/login'), {
      timeout: 15_000,
    });
    assert.match(page.url(), /\/login/);
    await page.close();
  });
});
