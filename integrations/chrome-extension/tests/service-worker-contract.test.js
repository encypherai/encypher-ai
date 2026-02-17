import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

const serviceWorkerPath = path.resolve(process.cwd(), 'background', 'service-worker.js');
const serviceWorkerSource = fs.readFileSync(serviceWorkerPath, 'utf8');

describe('service worker verify payload contract', () => {
  it('passes through C2PA assertions for click-panel manifest disclosure', () => {
    assert.match(serviceWorkerSource, /c2pa_assertions\s*:\s*verdict\.c2pa\?\.assertions/);
  });

  it('requests account quota and maps c2pa_signatures metrics into usage fields for popup meter', () => {
    assert.match(serviceWorkerSource, /quotaEndpoint\s*:\s*['"]\/api\/v1\/account\/quota['"]/);
    assert.match(serviceWorkerSource, /usageEndpoint\s*:\s*['"]\/api\/v1\/usage['"]/);
    assert.match(serviceWorkerSource, /c2pa_signatures/);
    assert.match(serviceWorkerSource, /used\)/);
    assert.match(serviceWorkerSource, /limit\)/);
    assert.match(serviceWorkerSource, /signings_this_month\s*:/);
    assert.match(serviceWorkerSource, /monthly_limit\s*:/);
    assert.match(serviceWorkerSource, /usage:\s*quotaUsage\s*\|\|\s*accountUsage/);
  });
});
