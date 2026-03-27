(function (global) {
  const SETTINGS_KEYS = {
    apiKey: 'encypher_api_key',
    apiBaseUrl: 'encypher_api_base_url',
    provenancePrefix: 'encypher_provenance_',
    provenanceIndex: 'encypher_provenance_index',
  };

  const DEFAULTS = {
    apiBaseUrl: 'https://api.encypher.com',
    maxEntriesPerHash: 10,
    maxHashes: 50,
  };

  function getSettingsContainer() {
    if (!global.Office || !Office.context) {
      throw new Error('Office settings unavailable. Open from Office task pane context.');
    }

    if (Office.context.roamingSettings) {
      return Office.context.roamingSettings;
    }

    if (Office.context.document && Office.context.document.settings) {
      return Office.context.document.settings;
    }

    throw new Error('Office settings unavailable. Open from Office task pane context.');
  }

  function readSetting(key, fallbackValue) {
    const settings = getSettingsContainer();
    const value = settings.get(key);
    return value === null || value === undefined ? fallbackValue : value;
  }

  function writeSetting(key, value) {
    const settings = getSettingsContainer();
    settings.set(key, value);
    return new Promise((resolve, reject) => {
      settings.saveAsync((result) => {
        if (result.status === Office.AsyncResultStatus.Succeeded) {
          resolve(true);
        } else {
          reject(new Error(result.error && result.error.message ? result.error.message : 'Failed to save settings.'));
        }
      });
    });
  }

  async function saveUserSettings(input) {
    const apiKey = (input.apiKey || '').trim();
    const apiBaseUrl = (input.apiBaseUrl || '').trim();

    const settings = getSettingsContainer();
    if (apiKey) {
      settings.set(SETTINGS_KEYS.apiKey, apiKey);
    }
    if (apiBaseUrl) {
      settings.set(SETTINGS_KEYS.apiBaseUrl, apiBaseUrl);
    }

    await new Promise((resolve, reject) => {
      settings.saveAsync((result) => {
        if (result.status === Office.AsyncResultStatus.Succeeded) {
          resolve();
        } else {
          reject(new Error(result.error && result.error.message ? result.error.message : 'Failed to save settings.'));
        }
      });
    });

    return getUserSettings();
  }

  async function clearUserSettings() {
    const settings = getSettingsContainer();
    settings.remove(SETTINGS_KEYS.apiKey);
    settings.remove(SETTINGS_KEYS.apiBaseUrl);

    await new Promise((resolve, reject) => {
      settings.saveAsync((result) => {
        if (result.status === Office.AsyncResultStatus.Succeeded) {
          resolve();
        } else {
          reject(new Error(result.error && result.error.message ? result.error.message : 'Failed to clear settings.'));
        }
      });
    });

    return getUserSettings();
  }

  function getUserSettings() {
    return {
      apiKey: readSetting(SETTINGS_KEYS.apiKey, ''),
      apiBaseUrl: readSetting(SETTINGS_KEYS.apiBaseUrl, DEFAULTS.apiBaseUrl),
    };
  }

  function provenanceKey(visibleHash) {
    return SETTINGS_KEYS.provenancePrefix + visibleHash;
  }

  function getProvenanceIndex() {
    const raw = readSetting(SETTINGS_KEYS.provenanceIndex, []);
    return Array.isArray(raw) ? raw : [];
  }

  async function setProvenanceIndex(index) {
    const unique = Array.from(new Set(index || []));
    await writeSetting(SETTINGS_KEYS.provenanceIndex, unique);
    return unique;
  }

  function getProvenanceEntries(visibleHash) {
    const raw = readSetting(provenanceKey(visibleHash), []);
    return Array.isArray(raw) ? raw : [];
  }

  async function setProvenanceEntries(visibleHash, entries) {
    const capped = Array.isArray(entries)
      ? entries.slice(-DEFAULTS.maxEntriesPerHash)
      : [];

    const key = provenanceKey(visibleHash);
    await writeSetting(key, capped);

    const index = getProvenanceIndex().filter((item) => item !== key);
    index.push(key);
    await setProvenanceIndex(index);

    await trimProvenanceKeys(index);

    return capped;
  }

  async function trimProvenanceKeys(existingIndex) {
    const settings = getSettingsContainer();
    const keys = Array.isArray(existingIndex) ? existingIndex.slice() : getProvenanceIndex();

    if (keys.length <= DEFAULTS.maxHashes) {
      return;
    }

    const keep = keys.slice(-DEFAULTS.maxHashes);
    const remove = keys.slice(0, keys.length - DEFAULTS.maxHashes);

    remove.forEach((key) => settings.remove(key));
    settings.set(SETTINGS_KEYS.provenanceIndex, keep);

    await new Promise((resolve, reject) => {
      settings.saveAsync((result) => {
        if (result.status === Office.AsyncResultStatus.Succeeded) {
          resolve();
        } else {
          reject(new Error(result.error && result.error.message ? result.error.message : 'Failed to trim provenance keys.'));
        }
      });
    });
  }

  const Storage = {
    SETTINGS_KEYS,
    DEFAULTS,
    getUserSettings,
    saveUserSettings,
    clearUserSettings,
    getProvenanceEntries,
    setProvenanceEntries,
    getProvenanceIndex,
  };

  global.EncypherStorage = Storage;
})(typeof window !== 'undefined' ? window : globalThis);
