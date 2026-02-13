/**
 * Encypher C2PA Verifier - Popup Script
 */

// DOM elements - Verify tab
const loadingEl = document.getElementById('loading');
const noContentEl = document.getElementById('no-content');
const contentFoundEl = document.getElementById('content-found');
const errorEl = document.getElementById('error');
const errorMessageEl = document.getElementById('error-message');

const verifiedCountEl = document.getElementById('verified-count');
const pendingCountEl = document.getElementById('pending-count');
const invalidCountEl = document.getElementById('invalid-count');
const detailsListEl = document.getElementById('details-list');

const rescanBtn = document.getElementById('rescan-btn');
const settingsBtn = document.getElementById('settings-btn');

// DOM elements - Sign tab
const signTabEl = document.getElementById('sign-tab');
const signNoKeyEl = document.getElementById('sign-no-key');
const signReadyEl = document.getElementById('sign-ready');
const signResultEl = document.getElementById('sign-result');
const signErrorEl = document.getElementById('sign-error');

const signTextEl = document.getElementById('sign-text');
const signTitleEl = document.getElementById('sign-title');
const signBtn = document.getElementById('sign-btn');
const signedOutputEl = document.getElementById('signed-output');
const copySignedBtn = document.getElementById('copy-signed');
const signAnotherBtn = document.getElementById('sign-another');
const signRetryBtn = document.getElementById('sign-retry');
const signErrorMessageEl = document.getElementById('sign-error-message');
const openSettingsBtn = document.getElementById('open-settings');

// DOM elements - Advanced options
const tierBadgeEl = document.getElementById('tier-badge');
const toggleAdvancedBtn = document.getElementById('toggle-advanced');
const advancedPanelEl = document.getElementById('advanced-panel');
const signInvisibleEl = document.getElementById('sign-invisible');
const signDocTypeEl = document.getElementById('sign-doc-type');
const signMerkleEl = document.getElementById('sign-merkle');
const signAttributionEl = document.getElementById('sign-attribution');
const enterpriseFeaturesEl = document.getElementById('enterprise-features');

// DOM elements - Usage meter
const usageMeterEl = document.getElementById('usage-meter');
const usageTextEl = document.getElementById('usage-text');
const usageFillEl = document.getElementById('usage-fill');

const FREE_TIER_LIMIT = 1000;

// DOM elements - Debug tab
const debugTabBtn = document.querySelector('.popup__tab--debug');
const debugTabEl = document.getElementById('debug-tab');
const debugLogsEl = document.getElementById('debug-logs');
const debugCountEl = document.getElementById('debug-count');
const debugRefreshBtn = document.getElementById('debug-refresh');
const debugClearBtn = document.getElementById('debug-clear');
const debugApiUrlEl = document.getElementById('debug-api-url');
const debugFilters = document.querySelectorAll('.debug-panel__filter');

// Account info cache
let accountInfo = null;

// Debug state
let currentDebugFilter = 'all';
let debugAutoRefreshInterval = null;

// Tab elements
const tabs = document.querySelectorAll('.popup__tab');
let currentTab = 'verify';

/**
 * Show a specific state and hide others
 */
function showState(state) {
  loadingEl.hidden = state !== 'loading';
  noContentEl.hidden = state !== 'empty';
  contentFoundEl.hidden = state !== 'found';
  errorEl.hidden = state !== 'error';
}

/**
 * Update the summary counts
 */
function updateCounts(state) {
  verifiedCountEl.textContent = state.verified || 0;
  pendingCountEl.textContent = state.pending || 0;
  invalidCountEl.textContent = state.invalid || 0;
}

/**
 * Render detail items
 */
function renderDetails(details) {
  detailsListEl.innerHTML = '';
  
  if (!details || details.length === 0) {
    return;
  }

  for (const detail of details) {
    const item = document.createElement('div');
    item.className = 'popup__detail-item';
    
    const iconClass = detail.revoked ? 'revoked' : (detail.valid ? 'verified' : 'invalid');
    const iconSymbol = detail.revoked
      ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>'
      : (detail.valid
        ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
        : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>');
    
    item.innerHTML = `
      <div class="popup__detail-icon popup__detail-icon--${iconClass}">${iconSymbol}</div>
      <div class="popup__detail-info">
        <div class="popup__detail-signer">${detail.signer || 'Unknown Signer'}</div>
        <div class="popup__detail-date">${detail.date || 'Date unknown'}</div>
      </div>
    `;
    
    detailsListEl.appendChild(item);
  }
}

/**
 * Get current tab and fetch state
 */
async function loadTabState() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab || !tab.id) {
      showState('error');
      errorMessageEl.textContent = 'Unable to access current tab.';
      return;
    }

    // Get state from service worker
    const state = await chrome.runtime.sendMessage({
      type: 'GET_TAB_STATE',
      tabId: tab.id
    });

    if (!state || state.count === 0) {
      showState('empty');
    } else {
      showState('found');
      updateCounts(state);
      
      // If we have cached details, render them
      if (state.details) {
        renderDetails(state.details);
      }
    }
  } catch (error) {
    console.error('Error loading tab state:', error);
    showState('error');
    errorMessageEl.textContent = error.message || 'Unable to load verification state.';
  }
}

/**
 * Trigger a rescan of the current page
 */
async function rescanPage() {
  showState('loading');
  
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab || !tab.id) {
      showState('error');
      errorMessageEl.textContent = 'Unable to access current tab.';
      return;
    }

    // Send rescan message to content script
    const response = await chrome.tabs.sendMessage(tab.id, { type: 'RESCAN' });
    
    // Wait a moment for verification to complete
    setTimeout(loadTabState, 1000);
  } catch (error) {
    console.error('Error rescanning:', error);
    showState('error');
    errorMessageEl.textContent = 'Unable to scan page. Make sure you\'re on a regular webpage.';
  }
}

/**
 * Switch between tabs
 */
function switchTab(tabName) {
  currentTab = tabName;
  
  // Update tab buttons
  tabs.forEach(tab => {
    tab.classList.toggle('popup__tab--active', tab.dataset.tab === tabName);
  });
  
  // Hide all tab content first
  loadingEl.hidden = true;
  noContentEl.hidden = true;
  contentFoundEl.hidden = true;
  errorEl.hidden = true;
  signTabEl.hidden = true;
  debugTabEl.hidden = true;
  
  // Stop debug auto-refresh when leaving debug tab
  if (debugAutoRefreshInterval) {
    clearInterval(debugAutoRefreshInterval);
    debugAutoRefreshInterval = null;
  }
  
  // Show/hide content
  if (tabName === 'verify') {
    loadTabState();
  } else if (tabName === 'sign') {
    signTabEl.hidden = false;
    checkApiKeyAndShowSignState();
  } else if (tabName === 'debug') {
    debugTabEl.hidden = false;
    loadDebugLogs();
    // Auto-refresh every 2 seconds while debug tab is open
    debugAutoRefreshInterval = setInterval(loadDebugLogs, 2000);
  }
}

/**
 * Check if API key exists and show appropriate sign state
 */
async function checkApiKeyAndShowSignState() {
  try {
    const result = await chrome.storage.local.get({ apiKey: '' });
    
    if (result.apiKey) {
      showSignState('ready');
      // Fetch account info to get tier
      fetchAccountInfo(result.apiKey);
    } else {
      showSignState('no-key');
    }
  } catch (error) {
    console.error('Error checking API key:', error);
    showSignState('no-key');
  }
}

/**
 * Fetch account info to determine tier and features
 */
async function fetchAccountInfo(apiKey) {
  try {
    const response = await chrome.runtime.sendMessage({
      type: 'GET_ACCOUNT_INFO',
      apiKey: apiKey
    });
    
    if (response && response.success) {
      accountInfo = response.data;
      updateTierDisplay(accountInfo);
    }
  } catch (error) {
    console.error('Error fetching account info:', error);
  }
}

/**
 * Update tier badge and feature availability
 */
function updateTierDisplay(info) {
  if (!tierBadgeEl) return;
  
  const tier = (info?.tier || 'free').toLowerCase();
  const isEnterprise = ['enterprise', 'business'].includes(tier);
  
  tierBadgeEl.className = `popup__tier-badge popup__tier-badge--${isEnterprise ? 'enterprise' : 'free'}`;
  tierBadgeEl.innerHTML = `
    <span class="popup__tier-name">${isEnterprise ? 'Enterprise' : 'Free Tier'}</span>
  `;
  
  // Enable enterprise features
  if (signMerkleEl) {
    signMerkleEl.disabled = !isEnterprise;
  }
  if (signAttributionEl) {
    signAttributionEl.disabled = !isEnterprise;
  }
  
  // Hide upgrade prompt for enterprise users
  if (enterpriseFeaturesEl && isEnterprise) {
    enterpriseFeaturesEl.querySelector('.popup__enterprise-link')?.remove();
    enterpriseFeaturesEl.querySelector('.popup__enterprise-badge').textContent = 'ENABLED';
  }
  
  // Update usage meter
  updateUsageMeter(info);
}

/**
 * Update usage meter for free tier (1k/month limit)
 */
function updateUsageMeter(info) {
  if (!usageMeterEl) return;
  
  const usage = info?.usage?.signings_this_month || 0;
  const limit = info?.usage?.monthly_limit || FREE_TIER_LIMIT;
  const tier = (info?.tier || 'free').toLowerCase();
  const isEnterprise = ['enterprise', 'business'].includes(tier);
  
  // Hide meter for enterprise (unlimited)
  if (isEnterprise) {
    usageMeterEl.hidden = true;
    return;
  }
  
  usageMeterEl.hidden = false;
  const pct = Math.min((usage / limit) * 100, 100);
  const remaining = Math.max(limit - usage, 0);
  
  if (usageFillEl) {
    usageFillEl.style.width = `${pct}%`;
    usageFillEl.className = 'popup__usage-fill';
    if (pct >= 90) {
      usageFillEl.classList.add('popup__usage-fill--danger');
    } else if (pct >= 75) {
      usageFillEl.classList.add('popup__usage-fill--warning');
    }
  }
  
  if (usageTextEl) {
    usageTextEl.textContent = `${usage.toLocaleString()} / ${limit.toLocaleString()} signings this month`;
    usageTextEl.className = 'popup__usage-text';
    if (pct >= 90) {
      usageTextEl.classList.add('popup__usage-text--danger');
      usageTextEl.textContent = `${remaining.toLocaleString()} signings remaining`;
    } else if (pct >= 75) {
      usageTextEl.classList.add('popup__usage-text--warning');
      usageTextEl.textContent = `${remaining.toLocaleString()} signings remaining`;
    }
  }
}

/**
 * Show a specific sign state
 */
function showSignState(state) {
  signNoKeyEl.hidden = state !== 'no-key';
  signReadyEl.hidden = state !== 'ready';
  signResultEl.hidden = state !== 'result';
  signErrorEl.hidden = state !== 'error';
}

/**
 * Sign content using the API
 */
async function signContent() {
  const text = signTextEl.value.trim();
  const title = signTitleEl.value.trim();
  
  if (!text) {
    signErrorMessageEl.textContent = 'Please enter text to sign.';
    showSignState('error');
    return;
  }
  
  // Gather advanced options
  const useInvisible = signInvisibleEl?.checked ?? true;
  const docType = signDocTypeEl?.value || 'article';
  const useMerkle = signMerkleEl?.checked && !signMerkleEl?.disabled;
  const useAttribution = signAttributionEl?.checked && !signAttributionEl?.disabled;
  
  // Disable button and show loading
  signBtn.disabled = true;
  signBtn.textContent = 'Signing...';
  
  try {
    const response = await chrome.runtime.sendMessage({
      type: 'SIGN_CONTENT',
      text: text,
      title: title || undefined,
      options: {
        useInvisible,
        documentType: docType,
        useMerkle,
        useAttribution
      }
    });
    
    if (response && response.success) {
      signedOutputEl.value = response.signedText;
      
      // Copy to clipboard
      await navigator.clipboard.writeText(response.signedText);
      
      showSignState('result');
    } else {
      signErrorMessageEl.textContent = response?.error || 'Signing failed. Please try again.';
      showSignState('error');
    }
  } catch (error) {
    console.error('Error signing content:', error);
    signErrorMessageEl.textContent = error.message || 'Unable to sign content.';
    showSignState('error');
  } finally {
    signBtn.disabled = false;
    signBtn.textContent = 'Sign Content';
  }
}

/**
 * Copy signed output to clipboard
 */
async function copySignedOutput() {
  try {
    await navigator.clipboard.writeText(signedOutputEl.value);
    copySignedBtn.textContent = 'Copied!';
    setTimeout(() => {
      copySignedBtn.textContent = 'Copy';
    }, 2000);
  } catch (error) {
    console.error('Error copying:', error);
  }
}

/**
 * Reset sign form for another signing
 */
function resetSignForm() {
  signTextEl.value = '';
  signTitleEl.value = '';
  signedOutputEl.value = '';
  showSignState('ready');
}

/**
 * Open options page
 */
function openSettings() {
  chrome.runtime.openOptionsPage();
}

// Event listeners - Tabs
tabs.forEach(tab => {
  tab.addEventListener('click', () => switchTab(tab.dataset.tab));
});

// Event listeners - Verify tab
rescanBtn.addEventListener('click', rescanPage);
settingsBtn.addEventListener('click', openSettings);

// Event listeners - Sign tab
signBtn?.addEventListener('click', signContent);
copySignedBtn?.addEventListener('click', copySignedOutput);
signAnotherBtn?.addEventListener('click', resetSignForm);
signRetryBtn?.addEventListener('click', () => showSignState('ready'));
openSettingsBtn?.addEventListener('click', openSettings);

// Event listener - Advanced options toggle
toggleAdvancedBtn?.addEventListener('click', () => {
  const isOpen = advancedPanelEl.hidden;
  advancedPanelEl.hidden = !isOpen;
  toggleAdvancedBtn.classList.toggle('open', isOpen);
});

/**
 * TEAM_151: Check if dev mode is active and show debug tab
 */
async function checkDevMode() {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'GET_DEV_MODE' });
    if (response && response.devMode) {
      debugTabBtn.hidden = false;
      
      // Show the current API URL in the debug panel
      const settings = await chrome.storage.sync.get({
        apiBaseUrl: 'https://api.encypherai.com',
        customApiUrl: ''
      });
      const url = settings.apiBaseUrl === 'custom' ? settings.customApiUrl : settings.apiBaseUrl;
      if (debugApiUrlEl) debugApiUrlEl.textContent = url;
    }
  } catch (e) {
    // Not in dev mode or service worker not ready
  }
}

/**
 * TEAM_151: Load and render debug logs from the service worker
 */
async function loadDebugLogs() {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'GET_DEBUG_LOGS' });
    if (!response || !response.logs) return;
    
    const logs = response.logs;
    const filtered = currentDebugFilter === 'all'
      ? logs
      : logs.filter(l => l.level === currentDebugFilter);
    
    renderDebugLogs(filtered);
    debugCountEl.textContent = `${filtered.length} of ${logs.length} entries`;
  } catch (e) {
    console.error('Error loading debug logs:', e);
  }
}

/**
 * TEAM_151: Render log entries into the debug panel
 */
function renderDebugLogs(logs) {
  if (!logs || logs.length === 0) {
    debugLogsEl.innerHTML = '<div class="debug-panel__empty">No logs yet. Interact with the extension to generate logs.</div>';
    return;
  }
  
  const wasScrolledToBottom = debugLogsEl.scrollTop + debugLogsEl.clientHeight >= debugLogsEl.scrollHeight - 20;
  
  debugLogsEl.innerHTML = logs.map(log => {
    const time = new Date(log.timestamp).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const dataAttr = log.data ? ` data-json="${escapeAttr(JSON.stringify(log.data, null, 2))}"` : '';
    const dataLink = log.data ? ' <span class="debug-log__data" data-action="toggle-log-data">+data</span>' : '';
    
    return `<div class="debug-log">
      <span class="debug-log__time">${time}</span>
      <span class="debug-log__level debug-log__level--${log.level}">${log.level}</span>
      <span class="debug-log__cat">[${log.category}]</span>
      <span class="debug-log__msg">${escapeHtmlDebug(log.message)}${dataLink}</span>
    </div>${log.data ? `<div class="debug-log__data-expanded" hidden${dataAttr}></div>` : ''}`;
  }).join('');
  
  // Auto-scroll to bottom if user was already at bottom
  if (wasScrolledToBottom) {
    debugLogsEl.scrollTop = debugLogsEl.scrollHeight;
  }
}

/**
 * TEAM_151: Escape HTML for safe display in debug panel
 */
function escapeHtmlDebug(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * TEAM_151: Escape attribute value
 */
function escapeAttr(text) {
  return text.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// TEAM_151: Event delegation for debug log data toggle (CSP-safe, no inline handlers)
debugLogsEl?.addEventListener('click', (e) => {
  const el = e.target.closest('[data-action="toggle-log-data"]');
  if (!el) return;
  const expanded = el.closest('.debug-log').nextElementSibling;
  if (expanded && expanded.classList.contains('debug-log__data-expanded')) {
    if (expanded.hidden) {
      expanded.textContent = expanded.getAttribute('data-json');
      expanded.hidden = false;
      el.textContent = '-data';
    } else {
      expanded.hidden = true;
      el.textContent = '+data';
    }
  }
});

// Event listeners - Debug tab
debugRefreshBtn?.addEventListener('click', loadDebugLogs);

debugClearBtn?.addEventListener('click', async () => {
  await chrome.runtime.sendMessage({ type: 'CLEAR_DEBUG_LOGS' });
  loadDebugLogs();
});

debugFilters.forEach(btn => {
  btn.addEventListener('click', () => {
    debugFilters.forEach(f => f.classList.remove('debug-panel__filter--active'));
    btn.classList.add('debug-panel__filter--active');
    currentDebugFilter = btn.dataset.level;
    loadDebugLogs();
  });
});

// Initialize
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    loadTabState();
    checkDevMode();
  });
} else {
  loadTabState();
  checkDevMode();
}
