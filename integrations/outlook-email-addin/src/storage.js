(function (global) {
  const SETTINGS_KEYS = {
    apiKey: 'encypher_email_api_key',
    apiBaseUrl: 'encypher_email_api_base_url',
    provenancePrefix: 'encypher_email_provenance_',
    provenanceIndex: 'encypher_email_provenance_index',
  };

  const DEFAULTS = {
    apiBaseUrl: 'https://api.encypherai.com',
    maxEntriesPerHash: 10,
    maxHashes: 50,
  };

  function assertRoamingSettings() {
    if (!global.Office || !Office.context || !Office.context.roamingSettings) {
      throw new Error('Outlook roaming settings unavailable.');
    }
    return Office.context.roamingSettings;
  }

  function getSetting(key, fallback) {
    const settings = assertRoamingSettings();
    const value = settings.get(key);
    return value === null || value === undefined ? fallback : value;
  }

  function saveAsync() {
    const settings = assertRoamingSettings();
    return new Promise((resolve, reject) => {
      settings.saveAsync((result) => {
        if (result.status === Office.AsyncResultStatus.Succeeded) {
          resolve(true);
        } else {
          reject(new Error(result.error && result.error.message ? result.error.message : 'Failed to save Outlook settings.'));
        }
      });
    });
  }

  function getUserSettings() {
    return {
      apiKey: getSetting(SETTINGS_KEYS.apiKey, ''),
      apiBaseUrl: getSetting(SETTINGS_KEYS.apiBaseUrl, DEFAULTS.apiBaseUrl),
    };
  }

  async function saveUserSettings(input) {
    const settings = assertRoamingSettings();
    const apiKey = (input.apiKey || '').trim();
    const apiBaseUrl = (input.apiBaseUrl || '').trim();

    if (apiKey) {
      settings.set(SETTINGS_KEYS.apiKey, apiKey);
    }
    if (apiBaseUrl) {
      settings.set(SETTINGS_KEYS.apiBaseUrl, apiBaseUrl);
    }

    await saveAsync();
    return getUserSettings();
  }

  async function clearUserSettings() {
    const settings = assertRoamingSettings();
    settings.remove(SETTINGS_KEYS.apiKey);
    settings.remove(SETTINGS_KEYS.apiBaseUrl);
    await saveAsync();
    return getUserSettings();
  }

  function provenanceKey(hash) {
    return SETTINGS_KEYS.provenancePrefix + hash;
  }

  function getProvenanceIndex() {
    const index = getSetting(SETTINGS_KEYS.provenanceIndex, []);
    return Array.isArray(index) ? index : [];
  }

  function getProvenanceEntries(hash) {
    const raw = getSetting(provenanceKey(hash), []);
    return Array.isArray(raw) ? raw : [];
  }

  async function setProvenanceEntries(hash, entries) {
    const settings = assertRoamingSettings();
    const key = provenanceKey(hash);

    const capped = Array.isArray(entries)
      ? entries.slice(-DEFAULTS.maxEntriesPerHash)
      : [];

    settings.set(key, capped);

    const index = getProvenanceIndex().filter((k) => k !== key);
    index.push(key);

    const keep = index.slice(-DEFAULTS.maxHashes);
    const remove = index.slice(0, index.length - DEFAULTS.maxHashes);

    remove.forEach((k) => settings.remove(k));
    settings.set(SETTINGS_KEYS.provenanceIndex, keep);

    await saveAsync();
    return capped;
  }

  const EmailStorage = {
    SETTINGS_KEYS,
    DEFAULTS,
    getUserSettings,
    saveUserSettings,
    clearUserSettings,
    getProvenanceEntries,
    setProvenanceEntries,
    getProvenanceIndex,
  };

  global.EmailStorage = EmailStorage;
})(typeof window !== 'undefined' ? window : globalThis);
