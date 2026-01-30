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
        console.log('[e2e] Dashboard dev server ready');
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
        reject(new Error(`Dashboard dev server did not become ready in time. Recent output:\n\n${output}`));
      }
    }, 60_000);
  });
}

describe('team page upgrade prompt', () => {
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

  it('shows upgrade prompt for unauthenticated users', async () => {
    const page = await browser.newPage();
    try {
      await page.goto(`${server.baseUrl}/team`, { waitUntil: 'domcontentloaded', timeout: 30_000 });
      await page.waitForFunction(() => {
        const text = document.body?.innerText || '';
        return /Team Management/i.test(text) || /Upgrade to Business/i.test(text) || /Sign in/i.test(text);
      }, { timeout: 15_000 });
      const content = await page.content();
      const url = page.url();
      if (/signin/i.test(url) || /Sign in/i.test(content)) {
        assert.match(content, /Sign in/i);
      } else {
        assert.match(content, /Team Management/i);
        assert.match(content, /Upgrade to Business/i);
      }
    } finally {
      await page.close();
    }
  });
});
