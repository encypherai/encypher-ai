(function (global) {
  function byId(id) {
    return document.getElementById(id);
  }

  function showResult(payload) {
    const panel = byId('resultPanel');
    panel.hidden = false;
    byId('resultOutput').textContent = JSON.stringify(payload, null, 2);
  }

  function setButtonBusy(id, busy) {
    const button = byId(id);
    if (button) {
      button.disabled = !!busy;
    }
  }

  function assertSettings(settings) {
    if (!settings.apiKey) {
      throw new Error('Missing API key. Add your Encypher API key in Settings to sign with proof of origin.');
    }
    if (!settings.apiBaseUrl) {
      throw new Error('Missing API base URL. Add the Encypher API base URL in Settings.');
    }
  }

  async function loadProvenanceSummary(text) {
    const visible = global.ProvenanceUtils.stripEmbeddingChars(text || '');
    const hash = global.ProvenanceUtils.hashText(visible);
    const entries = global.EncypherStorage.getProvenanceEntries(hash);

    byId('provenanceSummary').textContent =
      'Visible content hash: ' + hash + ' | Provenance entries: ' + entries.length;

    return { hash, entries };
  }

  async function runSign(mode) {
    const settings = global.EncypherStorage.getUserSettings();
    assertSettings(settings);

    const host = global.EncypherHostAdapter.getHostName();
    const caps = global.HostCapabilities.getHostCapabilities(host);

    if (mode === 'selection' && !caps.canReadSelection) {
      throw new Error('Selection actions are not supported in this host.');
    }
    if (mode === 'document' && !caps.canReadFullDocument) {
      throw new Error('Full-document actions are not supported in this host.');
    }

    const text = mode === 'selection'
      ? await global.EncypherHostAdapter.readSelectionText()
      : await global.EncypherHostAdapter.readFullDocumentText();

    if (!text || !text.trim()) {
      throw new Error('No text found to sign.');
    }

    const visibleText = global.ProvenanceUtils.stripEmbeddingChars(text);
    const visibleHash = global.ProvenanceUtils.hashText(visibleText);

    const existingRuns = global.ProvenanceUtils.extractEmbeddingRuns(text);
    if (existingRuns.length > 0) {
      const mergedFromCurrent = global.ProvenanceUtils.mergeProvenanceEntries(
        global.EncypherStorage.getProvenanceEntries(visibleHash),
        existingRuns,
        global.EncypherStorage.DEFAULTS.maxEntriesPerHash
      );
      await global.EncypherStorage.setProvenanceEntries(visibleHash, mergedFromCurrent);
    }

    const previousEmbeddings = global.EncypherStorage.getProvenanceEntries(visibleHash);
    const signResult = await global.EncypherApi.signContent({
      apiBaseUrl: settings.apiBaseUrl,
      apiKey: settings.apiKey,
      text,
      title: 'Office Content',
      previousEmbeddings,
    });

    if (mode === 'selection') {
      await global.EncypherHostAdapter.replaceSelectionText(signResult.signedText);
    } else {
      await global.EncypherHostAdapter.replaceFullDocumentText(signResult.signedText);
    }

    await loadProvenanceSummary(signResult.signedText);

    return {
      success: true,
      mode,
      host,
      signedLength: signResult.signedText.length,
      previousEmbeddingsCount: previousEmbeddings.length,
      verificationUrl: signResult.verificationUrl,
      message: 'Content signed with cryptographic proof of origin.',
    };
  }

  async function runVerify(mode) {
    const settings = global.EncypherStorage.getUserSettings();
    if (!settings.apiBaseUrl) {
      throw new Error('Missing API base URL. Add the Encypher API base URL in Settings.');
    }

    const host = global.EncypherHostAdapter.getHostName();
    const caps = global.HostCapabilities.getHostCapabilities(host);

    if (mode === 'selection' && !caps.canReadSelection) {
      throw new Error('Selection actions are not supported in this host.');
    }
    if (mode === 'document' && !caps.canReadFullDocument) {
      throw new Error('Full-document actions are not supported in this host.');
    }

    const text = mode === 'selection'
      ? await global.EncypherHostAdapter.readSelectionText()
      : await global.EncypherHostAdapter.readFullDocumentText();

    if (!text || !text.trim()) {
      throw new Error('No text found to verify.');
    }

    const verification = await global.EncypherApi.verifyContent({
      apiBaseUrl: settings.apiBaseUrl,
      text,
    });

    await loadProvenanceSummary(text);

    return {
      success: true,
      mode,
      host,
      valid: verification.valid === true,
      revoked: verification.revoked === true,
      signerName: verification.signer_name || verification.organization_name || '',
      reasonCode: verification.reason_code || '',
      timestamp: verification.timestamp || '',
      message: 'Verification completed against Encypher provenance infrastructure.',
      raw: verification,
    };
  }

  async function refreshUiState() {
    const host = global.EncypherHostAdapter.getHostName();
    const caps = global.HostCapabilities.getHostCapabilities(host);
    const settings = global.EncypherStorage.getUserSettings();

    byId('hostLabel').textContent = host + ' host';
    byId('capabilitiesText').textContent = [
      'Selection read: ' + caps.canReadSelection,
      'Selection replace: ' + caps.canReplaceSelection,
      'Full-doc read: ' + caps.canReadFullDocument,
      'Full-doc replace: ' + caps.canReplaceFullDocument,
    ].join(' | ');

    byId('apiKeyInput').placeholder = settings.apiKey ? 'Saved (enter to replace)' : 'Set API key';
    byId('apiBaseUrlInput').value = settings.apiBaseUrl || '';

    byId('signDocumentBtn').disabled = !caps.canReadFullDocument;
    byId('verifyDocumentBtn').disabled = !caps.canReadFullDocument;

    let currentText = '';
    if (caps.canReadSelection) {
      currentText = await global.EncypherHostAdapter.readSelectionText();
    }
    await loadProvenanceSummary(currentText);
  }

  async function saveSettings() {
    const apiKey = byId('apiKeyInput').value;
    const apiBaseUrl = byId('apiBaseUrlInput').value;

    global.EncypherApi.ensureHttpsEncypherHost(apiBaseUrl);

    const saved = await global.EncypherStorage.saveUserSettings({ apiKey, apiBaseUrl });
    byId('apiKeyInput').value = '';
    return {
      success: true,
      hasApiKey: !!saved.apiKey,
      apiBaseUrl: saved.apiBaseUrl,
    };
  }

  async function clearSettings() {
    await global.EncypherStorage.clearUserSettings();
    byId('apiKeyInput').value = '';
    byId('apiBaseUrlInput').value = global.EncypherStorage.DEFAULTS.apiBaseUrl;
    return { success: true };
  }

  function wireAction(buttonId, action) {
    byId(buttonId).addEventListener('click', async () => {
      setButtonBusy(buttonId, true);
      try {
        const result = await action();
        showResult(result);
        await refreshUiState();
      } catch (error) {
        showResult({ success: false, error: error.message || String(error) });
      } finally {
        setButtonBusy(buttonId, false);
      }
    });
  }

  function init() {
    wireAction('signSelectionBtn', () => runSign('selection'));
    wireAction('verifySelectionBtn', () => runVerify('selection'));
    wireAction('signDocumentBtn', () => runSign('document'));
    wireAction('verifyDocumentBtn', () => runVerify('document'));
    wireAction('saveSettingsBtn', () => saveSettings());
    wireAction('clearSettingsBtn', () => clearSettings());

    refreshUiState().catch((error) => {
      showResult({ success: false, error: error.message || String(error) });
    });
  }

  Office.onReady(() => {
    init();
  });
})(typeof window !== 'undefined' ? window : globalThis);
