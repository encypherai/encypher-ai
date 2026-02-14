(function (global) {
  function byId(id) {
    return document.getElementById(id);
  }

  function showResult(payload) {
    const panel = byId('resultPanel');
    panel.hidden = false;
    byId('resultOutput').textContent = JSON.stringify(payload, null, 2);
  }

  function setBusy(id, busy) {
    const el = byId(id);
    if (el) {
      el.disabled = !!busy;
    }
  }

  function assertSettings(settings) {
    if (!settings.apiKey) {
      throw new Error('Missing API key. Save it in Settings.');
    }
    if (!settings.apiBaseUrl) {
      throw new Error('Missing API base URL. Save it in Settings.');
    }
  }

  async function refreshUiState() {
    const mode = global.OutlookAdapter.getModeLabel();
    byId('modeLabel').textContent = mode;

    const settings = global.EmailStorage.getUserSettings();
    byId('apiKeyInput').placeholder = settings.apiKey ? 'Saved (enter to replace)' : 'Set API key';
    byId('apiBaseUrlInput').value = settings.apiBaseUrl || global.EmailStorage.DEFAULTS.apiBaseUrl;

    const bodyText = await global.OutlookAdapter.getBody({ html: false });
    const visible = global.EmailProvenanceUtils.stripEmbeddingChars(bodyText || '');
    const hash = global.EmailProvenanceUtils.hashText(visible);
    const entries = global.EmailStorage.getProvenanceEntries(hash);

    byId('provenanceSummary').textContent = 'Visible hash: ' + hash + ' | Entries: ' + entries.length;
  }

  async function signBody() {
    const settings = global.EmailStorage.getUserSettings();
    assertSettings(settings);

    const plainBody = await global.OutlookAdapter.getBody({ html: false });
    if (!plainBody || !plainBody.trim()) {
      throw new Error('Email body is empty.');
    }

    const visible = global.EmailProvenanceUtils.stripEmbeddingChars(plainBody);
    const visibleHash = global.EmailProvenanceUtils.hashText(visible);

    const vsRuns = global.EmailProvenanceUtils.extractVariationSelectorRuns(plainBody);
    if (vsRuns.length > 0) {
      const existing = global.EmailStorage.getProvenanceEntries(visibleHash);
      const mapped = vsRuns
        .filter((run) => run.bytes && run.bytes.length > 0)
        .map((run) => ({ bytes: run.bytes, timestamp: Date.now(), source: 'outlook-pre-sign' }));
      const merged = existing.concat(mapped).slice(-global.EmailStorage.DEFAULTS.maxEntriesPerHash);
      await global.EmailStorage.setProvenanceEntries(visibleHash, merged);
    }

    const previousEmbeddings = global.EmailStorage.getProvenanceEntries(visibleHash);

    const signResult = await global.EmailApi.signEmailBody({
      apiBaseUrl: settings.apiBaseUrl,
      apiKey: settings.apiKey,
      text: plainBody,
      title: global.OutlookAdapter.getSubject(),
      previousEmbeddings,
    });

    await global.OutlookAdapter.setBody(signResult.signedText, { html: false });
    await refreshUiState();

    return {
      success: true,
      signedLength: signResult.signedText.length,
      previousEmbeddingsCount: previousEmbeddings.length,
      verificationUrl: signResult.verificationUrl,
    };
  }

  async function verifyBody() {
    const settings = global.EmailStorage.getUserSettings();
    if (!settings.apiBaseUrl) {
      throw new Error('Missing API base URL. Save it in Settings.');
    }

    const plainBody = await global.OutlookAdapter.getBody({ html: false });
    if (!plainBody || !plainBody.trim()) {
      throw new Error('Email body is empty.');
    }

    const verifyResult = await global.EmailApi.verifyEmailBody({
      apiBaseUrl: settings.apiBaseUrl,
      text: plainBody,
    });

    await refreshUiState();

    return {
      success: true,
      valid: verifyResult.valid === true,
      revoked: verifyResult.revoked === true,
      signerName: verifyResult.signer_name || verifyResult.organization_name || '',
      reasonCode: verifyResult.reason_code || '',
      timestamp: verifyResult.timestamp || '',
      raw: verifyResult,
    };
  }

  async function saveSettings() {
    const apiKey = byId('apiKeyInput').value;
    const apiBaseUrl = byId('apiBaseUrlInput').value;
    global.EmailApi.ensureAllowedApiUrl(apiBaseUrl);

    const saved = await global.EmailStorage.saveUserSettings({ apiKey, apiBaseUrl });
    byId('apiKeyInput').value = '';

    return {
      success: true,
      hasApiKey: !!saved.apiKey,
      apiBaseUrl: saved.apiBaseUrl,
    };
  }

  async function clearSettings() {
    await global.EmailStorage.clearUserSettings();
    byId('apiKeyInput').value = '';
    byId('apiBaseUrlInput').value = global.EmailStorage.DEFAULTS.apiBaseUrl;
    return { success: true };
  }

  function wire(id, fn) {
    byId(id).addEventListener('click', async () => {
      setBusy(id, true);
      try {
        const result = await fn();
        showResult(result);
      } catch (err) {
        showResult({ success: false, error: err.message || String(err) });
      } finally {
        setBusy(id, false);
      }
    });
  }

  function init() {
    wire('signBtn', signBody);
    wire('verifyBtn', verifyBody);
    wire('saveSettingsBtn', saveSettings);
    wire('clearSettingsBtn', clearSettings);

    refreshUiState().catch((err) => {
      showResult({ success: false, error: err.message || String(err) });
    });
  }

  Office.onReady(() => {
    init();
  });
})(typeof window !== 'undefined' ? window : globalThis);
