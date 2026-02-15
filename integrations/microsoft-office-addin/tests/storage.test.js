const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const storageSource = fs.readFileSync(path.join(__dirname, '../src/storage.js'), 'utf8');

function createSettingsStore() {
  const state = new Map();
  return {
    get: (key) => (state.has(key) ? state.get(key) : undefined),
    set: (key, value) => state.set(key, value),
    remove: (key) => state.delete(key),
    saveAsync: (callback) => callback({ status: 'succeeded' }),
    _state: state,
  };
}

function loadStorageWithOffice(officeContext) {
  const sandbox = {
    window: {
      Office: officeContext,
    },
    Office: officeContext,
    globalThis: {},
  };

  vm.createContext(sandbox);
  vm.runInContext(storageSource, sandbox);

  return sandbox.window.EncypherStorage;
}

test('saveUserSettings uses roamingSettings when available', async () => {
  const roamingSettings = createSettingsStore();
  const documentSettings = createSettingsStore();
  const storage = loadStorageWithOffice({
    context: {
      roamingSettings,
      document: { settings: documentSettings },
    },
    AsyncResultStatus: { Succeeded: 'succeeded' },
  });

  const result = await storage.saveUserSettings({
    apiKey: 'encypher_live_key',
    apiBaseUrl: 'https://api.encypherai.com',
  });

  assert.equal(result.apiKey, 'encypher_live_key');
  assert.equal(result.apiBaseUrl, 'https://api.encypherai.com');
  assert.equal(roamingSettings._state.get('encypher_api_key'), 'encypher_live_key');
  assert.equal(documentSettings._state.get('encypher_api_key'), undefined);
});

test('saveUserSettings falls back to document.settings when roamingSettings is unavailable', async () => {
  const documentSettings = createSettingsStore();
  const storage = loadStorageWithOffice({
    context: {
      document: { settings: documentSettings },
    },
    AsyncResultStatus: { Succeeded: 'succeeded' },
  });

  const result = await storage.saveUserSettings({
    apiKey: 'encypher_live_key',
    apiBaseUrl: 'https://api.encypherai.com',
  });

  assert.equal(result.apiKey, 'encypher_live_key');
  assert.equal(result.apiBaseUrl, 'https://api.encypherai.com');
  assert.equal(documentSettings._state.get('encypher_api_key'), 'encypher_live_key');
  assert.equal(documentSettings._state.get('encypher_api_base_url'), 'https://api.encypherai.com');
});

test('saveUserSettings throws a context error when no Office settings container exists', async () => {
  const storage = loadStorageWithOffice({
    context: {},
    AsyncResultStatus: { Succeeded: 'succeeded' },
  });

  await assert.rejects(
    () => storage.saveUserSettings({ apiKey: 'k', apiBaseUrl: 'https://api.encypherai.com' }),
    /Office settings unavailable\. Open from Office task pane context\./
  );
});
