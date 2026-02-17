/**
 * Encypher Verify - Options Page Script
 */

// DOM elements
const apiKeyInput = document.getElementById('apiKey');
const toggleApiKeyBtn = document.getElementById('toggleApiKey');
const saveApiKeyBtn = document.getElementById('saveApiKey');
const apiKeyStatus = document.getElementById('apiKeyStatus');
const publisherIdentityEl = document.getElementById('publisherIdentity');

const autoVerifyCheckbox = document.getElementById('autoVerify');
const showBadgesCheckbox = document.getElementById('showBadges');

const apiBaseUrlInput = document.getElementById('apiBaseUrl');
const cacheTtlInput = document.getElementById('cacheTtl');

const clearCacheBtn = document.getElementById('clearCache');
const resetSettingsBtn = document.getElementById('resetSettings');

// Signing settings
const defaultInvisibleCheckbox = document.getElementById('defaultInvisible');
const autoReplaceContentCheckbox = document.getElementById('autoReplaceContent');
const defaultDocTypeSelect = document.getElementById('defaultDocType');
const defaultEmbeddingTechniqueSelect = document.getElementById('defaultEmbeddingTechnique');
const defaultSegmentationLevelSelect = document.getElementById('defaultSegmentationLevel');
const showEditorButtonsCheckbox = document.getElementById('showEditorButtons');

// Analytics settings
const analyticsEnabledCheckbox = document.getElementById('analyticsEnabled');
const analyticsStatusEl = document.getElementById('analyticsStatus');
const extensionSetupStatusSelect = document.getElementById('extensionSetupStatus');
const setupStatusHint = document.getElementById('setupStatusHint');

// Default settings
const DEFAULT_SETTINGS = {
  apiKey: '',
  autoVerify: true,
  showBadges: true,
  apiBaseUrl: 'https://api.encypherai.com',
  customApiUrl: '',
  cacheTtl: 5,
  // Signing defaults
  defaultInvisible: true,
  autoReplaceContent: true,
  defaultDocType: 'article',
  defaultEmbeddingTechnique: 'micro_ecc_c2pa',
  defaultSegmentationLevel: 'sentence',
  showEditorButtons: true,
  // Analytics
  analyticsEnabled: true,
  extensionSetupStatus: 'not_started'
};

/**
 * Load settings from storage
 */
async function loadSettings() {
  try {
    const result = await chrome.storage.sync.get(DEFAULT_SETTINGS);
    
    // API Key (stored locally for security)
    const localResult = await chrome.storage.local.get({ apiKey: '' });

    if (localResult.apiKey) {
      apiKeyInput.value = localResult.apiKey;
      apiKeyStatus.textContent = 'API key saved';
      apiKeyStatus.className = 'options__hint options__hint--success';
      await loadPublisherIdentity(localResult.apiKey);
    } else if (publisherIdentityEl) {
      publisherIdentityEl.textContent = 'Signing as: add an API key to load your publisher identity.';
    }
    
    // Verification settings
    autoVerifyCheckbox.checked = result.autoVerify;
    showBadgesCheckbox.checked = result.showBadges;
    
    // Advanced settings
    const savedUrl = result.apiBaseUrl === 'custom' 
      ? (result.customApiUrl || DEFAULT_SETTINGS.apiBaseUrl)
      : (result.apiBaseUrl || DEFAULT_SETTINGS.apiBaseUrl);
    apiBaseUrlInput.value = savedUrl;
    
    cacheTtlInput.value = result.cacheTtl;
    
    // Signing settings
    if (defaultInvisibleCheckbox) defaultInvisibleCheckbox.checked = result.defaultInvisible;
    if (autoReplaceContentCheckbox) autoReplaceContentCheckbox.checked = result.autoReplaceContent;
    if (defaultDocTypeSelect) defaultDocTypeSelect.value = result.defaultDocType;
    if (defaultEmbeddingTechniqueSelect) defaultEmbeddingTechniqueSelect.value = result.defaultEmbeddingTechnique || 'micro_ecc_c2pa';
    if (defaultSegmentationLevelSelect) defaultSegmentationLevelSelect.value = result.defaultSegmentationLevel || 'sentence';
    if (showEditorButtonsCheckbox) showEditorButtonsCheckbox.checked = result.showEditorButtons;
    
    // Analytics settings
    if (analyticsEnabledCheckbox) analyticsEnabledCheckbox.checked = result.analyticsEnabled;
    if (extensionSetupStatusSelect) {
      extensionSetupStatusSelect.value = result.extensionSetupStatus || 'not_started';
      updateSetupStatusHint(extensionSetupStatusSelect.value);
    }
    updateAnalyticsStatus();
  } catch (error) {
    console.error('Error loading settings:', error);
  }
}

function updateSetupStatusHint(status) {
  if (!setupStatusHint) return;

  if (status === 'completed') {
    setupStatusHint.textContent = 'Setup is marked complete. You can still replace the API key manually.';
    setupStatusHint.className = 'options__hint options__hint--success';
    return;
  }

  setupStatusHint.textContent = 'Optional login setup marks your extension as tracked for adoption metrics.';
  setupStatusHint.className = 'options__hint';
}

function renderPublisherIdentity(account) {
  if (!publisherIdentityEl) return;
  const publisherDisplayName = account?.publisherDisplayName;
  const signerName = publisherDisplayName || account.organizationName || 'your organization';
  publisherIdentityEl.textContent = `Signing as: ${signerName}`;
}

async function loadPublisherIdentity(apiKey) {
  if (!publisherIdentityEl) return;

  if (!apiKey) {
    publisherIdentityEl.textContent = 'Signing as: add an API key to load your publisher identity.';
    return;
  }

  try {
    const response = await chrome.runtime.sendMessage({
      type: 'GET_ACCOUNT_INFO',
      apiKey
    });

    if (response?.success && response.data) {
      renderPublisherIdentity(response.data);
      return;
    }
  } catch (error) {
    // Ignore account lookup failure and show fallback identity hint.
  }

  publisherIdentityEl.textContent = 'Signing as: unable to load publisher identity.';
}

/**
 * Update analytics status display
 */
async function updateAnalyticsStatus() {
  try {
    const summary = await chrome.runtime.sendMessage({ type: 'GET_ANALYTICS_SUMMARY' });
    if (analyticsStatusEl && summary) {
      analyticsStatusEl.textContent = summary.enabled 
        ? `Analytics enabled (${summary.queuedEvents} events queued)`
        : 'Analytics disabled';
    }
  } catch (e) {
    // Ignore errors
  }
}

/**
 * Save a setting to storage
 */
async function saveSetting(key, value, useLocal = false) {
  try {
    const storage = useLocal ? chrome.storage.local : chrome.storage.sync;
    await storage.set({ [key]: value });
    return true;
  } catch (error) {
    console.error(`Error saving ${key}:`, error);
    return false;
  }
}

/**
 * Validate API key format
 */
function validateApiKey(key) {
  if (!key) return { valid: false, error: 'API key is required' };
  if (!key.startsWith('ency_') && !key.startsWith('demo_')) {
    return { valid: false, error: 'API key should start with "ency_"' };
  }
  if (key.length < 20) {
    return { valid: false, error: 'API key is too short' };
  }
  return { valid: true };
}

function normalizeAccountPayload(data) {
  if (!data || typeof data !== 'object') return {};
  return data?.data || data;
}

/**
 * Test API key by making a request
 */
async function testApiKey(apiKey) {
  try {
    const baseUrl = getEffectiveApiUrl();
    const response = await fetch(`${baseUrl}/api/v1/account`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      const accountPayload = normalizeAccountPayload(data);
      const organization = accountPayload.organization_name || accountPayload.name || accountPayload.organization?.name || 'your organization';
      return { valid: true, organization };
    } else if (response.status === 401) {
      return { valid: false, error: 'Invalid API key' };
    } else {
      return { valid: false, error: `API error: ${response.status}` };
    }
  } catch (error) {
    return { valid: false, error: 'Could not connect to API' };
  }
}

/**
 * Get effective API URL based on settings
 */
function getEffectiveApiUrl() {
  const url = apiBaseUrlInput.value.trim();
  return url || DEFAULT_SETTINGS.apiBaseUrl;
}

// Event listeners

// Toggle API key visibility
toggleApiKeyBtn.addEventListener('click', () => {
  const isPassword = apiKeyInput.type === 'password';
  apiKeyInput.type = isPassword ? 'text' : 'password';
  toggleApiKeyBtn.textContent = isPassword ? 'Hide' : 'Show';
});

// Save API key
saveApiKeyBtn.addEventListener('click', async () => {
  const apiKey = apiKeyInput.value.trim();
  
  // Validate format
  const validation = validateApiKey(apiKey);
  if (!validation.valid) {
    apiKeyStatus.textContent = validation.error;
    apiKeyStatus.className = 'options__hint options__hint--error';
    return;
  }
  
  // Show testing status
  apiKeyStatus.textContent = 'Testing API key...';
  apiKeyStatus.className = 'options__hint';
  saveApiKeyBtn.disabled = true;
  
  // Test the key
  const testResult = await testApiKey(apiKey);
  
  if (testResult.valid) {
    // Save to local storage (more secure than sync)
    await saveSetting('apiKey', apiKey, true);
    await saveSetting('extensionSetupStatus', 'completed');
    apiKeyStatus.textContent = `Connected as ${testResult.organization}`;
    apiKeyStatus.className = 'options__hint options__hint--success';
    await loadPublisherIdentity(apiKey);
    if (extensionSetupStatusSelect) {
      extensionSetupStatusSelect.value = 'completed';
      updateSetupStatusHint('completed');
    }
    
    // Notify service worker
    chrome.runtime.sendMessage({ type: 'API_KEY_UPDATED', hasKey: true });
  } else {
    apiKeyStatus.textContent = testResult.error;
    apiKeyStatus.className = 'options__hint options__hint--error';
    if (publisherIdentityEl) {
      publisherIdentityEl.textContent = 'Signing as: add an API key to load your publisher identity.';
    }
  }
  
  saveApiKeyBtn.disabled = false;
});

// Auto-verify toggle
autoVerifyCheckbox.addEventListener('change', async () => {
  await saveSetting('autoVerify', autoVerifyCheckbox.checked);
  chrome.runtime.sendMessage({ 
    type: 'SETTINGS_UPDATED', 
    setting: 'autoVerify', 
    value: autoVerifyCheckbox.checked 
  });
});

// Show badges toggle
showBadgesCheckbox.addEventListener('change', async () => {
  await saveSetting('showBadges', showBadgesCheckbox.checked);
  chrome.runtime.sendMessage({ 
    type: 'SETTINGS_UPDATED', 
    setting: 'showBadges', 
    value: showBadgesCheckbox.checked 
  });
});

// API base URL change
apiBaseUrlInput.addEventListener('blur', async () => {
  const url = apiBaseUrlInput.value.trim();
  if (!url) {
    apiBaseUrlInput.value = DEFAULT_SETTINGS.apiBaseUrl;
  }
  const effectiveUrl = url || DEFAULT_SETTINGS.apiBaseUrl;
  await saveSetting('apiBaseUrl', effectiveUrl);
  chrome.runtime.sendMessage({ 
    type: 'SETTINGS_UPDATED', 
    setting: 'apiBaseUrl', 
    value: effectiveUrl 
  });
});

// Cache TTL change
cacheTtlInput.addEventListener('change', async () => {
  const ttl = parseInt(cacheTtlInput.value, 10);
  if (ttl >= 1 && ttl <= 60) {
    await saveSetting('cacheTtl', ttl);
    chrome.runtime.sendMessage({ 
      type: 'SETTINGS_UPDATED', 
      setting: 'cacheTtl', 
      value: ttl 
    });
  }
});

// Clear cache
clearCacheBtn.addEventListener('click', async () => {
  chrome.runtime.sendMessage({ type: 'CLEAR_CACHE' });
  clearCacheBtn.textContent = 'Cache Cleared!';
  setTimeout(() => {
    clearCacheBtn.textContent = 'Clear Verification Cache';
  }, 2000);
});

// Signing settings event listeners
defaultInvisibleCheckbox?.addEventListener('change', async () => {
  await saveSetting('defaultInvisible', defaultInvisibleCheckbox.checked);
  chrome.runtime.sendMessage({ 
    type: 'SETTINGS_UPDATED', 
    setting: 'defaultInvisible', 
    value: defaultInvisibleCheckbox.checked 
  });
});

autoReplaceContentCheckbox?.addEventListener('change', async () => {
  await saveSetting('autoReplaceContent', autoReplaceContentCheckbox.checked);
  chrome.runtime.sendMessage({ 
    type: 'SETTINGS_UPDATED', 
    setting: 'autoReplaceContent', 
    value: autoReplaceContentCheckbox.checked 
  });
});

defaultDocTypeSelect?.addEventListener('change', async () => {
  await saveSetting('defaultDocType', defaultDocTypeSelect.value);
  chrome.runtime.sendMessage({ 
    type: 'SETTINGS_UPDATED', 
    setting: 'defaultDocType', 
    value: defaultDocTypeSelect.value 
  });
});

defaultEmbeddingTechniqueSelect?.addEventListener('change', async () => {
  await saveSetting('defaultEmbeddingTechnique', defaultEmbeddingTechniqueSelect.value);
  chrome.runtime.sendMessage({
    type: 'SETTINGS_UPDATED',
    setting: 'defaultEmbeddingTechnique',
    value: defaultEmbeddingTechniqueSelect.value
  });
});

defaultSegmentationLevelSelect?.addEventListener('change', async () => {
  await saveSetting('defaultSegmentationLevel', defaultSegmentationLevelSelect.value);
  chrome.runtime.sendMessage({
    type: 'SETTINGS_UPDATED',
    setting: 'defaultSegmentationLevel',
    value: defaultSegmentationLevelSelect.value
  });
});

showEditorButtonsCheckbox?.addEventListener('change', async () => {
  await saveSetting('showEditorButtons', showEditorButtonsCheckbox.checked);
  chrome.runtime.sendMessage({ 
    type: 'SETTINGS_UPDATED', 
    setting: 'showEditorButtons', 
    value: showEditorButtonsCheckbox.checked 
  });
});

extensionSetupStatusSelect?.addEventListener('change', async () => {
  await saveSetting('extensionSetupStatus', extensionSetupStatusSelect.value);
  updateSetupStatusHint(extensionSetupStatusSelect.value);
});

// Analytics settings event listener
analyticsEnabledCheckbox?.addEventListener('change', async () => {
  await saveSetting('analyticsEnabled', analyticsEnabledCheckbox.checked);
  chrome.runtime.sendMessage({ 
    type: 'SET_ANALYTICS_ENABLED', 
    enabled: analyticsEnabledCheckbox.checked 
  });
  updateAnalyticsStatus();
});

// Reset settings
resetSettingsBtn.addEventListener('click', async () => {
  if (confirm('Are you sure you want to reset all settings? This will also remove your API key.')) {
    await chrome.storage.sync.clear();
    await chrome.storage.local.clear();
    chrome.runtime.sendMessage({ type: 'SETTINGS_RESET' });
    location.reload();
  }
});

// Initialize
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadSettings);
} else {
  loadSettings();
}
