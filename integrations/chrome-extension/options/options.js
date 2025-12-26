/**
 * Encypher C2PA Verifier - Options Page Script
 */

// DOM elements
const apiKeyInput = document.getElementById('apiKey');
const toggleApiKeyBtn = document.getElementById('toggleApiKey');
const saveApiKeyBtn = document.getElementById('saveApiKey');
const apiKeyStatus = document.getElementById('apiKeyStatus');

const autoVerifyCheckbox = document.getElementById('autoVerify');
const showBadgesCheckbox = document.getElementById('showBadges');

const apiBaseUrlSelect = document.getElementById('apiBaseUrl');
const customUrlField = document.getElementById('customUrlField');
const customApiUrlInput = document.getElementById('customApiUrl');
const cacheTtlInput = document.getElementById('cacheTtl');

const clearCacheBtn = document.getElementById('clearCache');
const resetSettingsBtn = document.getElementById('resetSettings');

// Default settings
const DEFAULT_SETTINGS = {
  apiKey: '',
  autoVerify: true,
  showBadges: true,
  apiBaseUrl: 'https://api.encypherai.com',
  customApiUrl: '',
  cacheTtl: 5
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
      apiKeyStatus.textContent = '✓ API key saved';
      apiKeyStatus.className = 'options__hint options__hint--success';
    }
    
    // Verification settings
    autoVerifyCheckbox.checked = result.autoVerify;
    showBadgesCheckbox.checked = result.showBadges;
    
    // Advanced settings
    if (result.apiBaseUrl === 'custom' || 
        (result.apiBaseUrl !== 'https://api.encypherai.com' && 
         result.apiBaseUrl !== 'http://localhost:9000')) {
      apiBaseUrlSelect.value = 'custom';
      customUrlField.hidden = false;
      customApiUrlInput.value = result.customApiUrl || result.apiBaseUrl;
    } else {
      apiBaseUrlSelect.value = result.apiBaseUrl;
    }
    
    cacheTtlInput.value = result.cacheTtl;
  } catch (error) {
    console.error('Error loading settings:', error);
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
      return { valid: true, organization: data.organization_name };
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
  if (apiBaseUrlSelect.value === 'custom') {
    return customApiUrlInput.value || DEFAULT_SETTINGS.apiBaseUrl;
  }
  return apiBaseUrlSelect.value;
}

// Event listeners

// Toggle API key visibility
toggleApiKeyBtn.addEventListener('click', () => {
  const isPassword = apiKeyInput.type === 'password';
  apiKeyInput.type = isPassword ? 'text' : 'password';
  toggleApiKeyBtn.textContent = isPassword ? '🙈' : '👁';
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
    apiKeyStatus.textContent = `✓ Connected as ${testResult.organization}`;
    apiKeyStatus.className = 'options__hint options__hint--success';
    
    // Notify service worker
    chrome.runtime.sendMessage({ type: 'API_KEY_UPDATED', hasKey: true });
  } else {
    apiKeyStatus.textContent = testResult.error;
    apiKeyStatus.className = 'options__hint options__hint--error';
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
apiBaseUrlSelect.addEventListener('change', async () => {
  const value = apiBaseUrlSelect.value;
  customUrlField.hidden = value !== 'custom';
  
  if (value !== 'custom') {
    await saveSetting('apiBaseUrl', value);
    chrome.runtime.sendMessage({ 
      type: 'SETTINGS_UPDATED', 
      setting: 'apiBaseUrl', 
      value: value 
    });
  }
});

// Custom API URL change
customApiUrlInput.addEventListener('blur', async () => {
  const url = customApiUrlInput.value.trim();
  if (url) {
    await saveSetting('apiBaseUrl', 'custom');
    await saveSetting('customApiUrl', url);
    chrome.runtime.sendMessage({ 
      type: 'SETTINGS_UPDATED', 
      setting: 'apiBaseUrl', 
      value: url 
    });
  }
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
document.addEventListener('DOMContentLoaded', loadSettings);
