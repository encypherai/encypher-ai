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
    const iconSymbol = detail.revoked ? '⊘' : (detail.valid ? '✓' : '✗');
    
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
  
  // Show/hide content
  if (tabName === 'verify') {
    signTabEl.hidden = true;
    loadTabState();
  } else if (tabName === 'sign') {
    // Hide verify states
    loadingEl.hidden = true;
    noContentEl.hidden = true;
    contentFoundEl.hidden = true;
    errorEl.hidden = true;
    
    // Show sign tab
    signTabEl.hidden = false;
    checkApiKeyAndShowSignState();
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
    } else {
      showSignState('no-key');
    }
  } catch (error) {
    console.error('Error checking API key:', error);
    showSignState('no-key');
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
  
  // Disable button and show loading
  signBtn.disabled = true;
  signBtn.textContent = 'Signing...';
  
  try {
    const response = await chrome.runtime.sendMessage({
      type: 'SIGN_CONTENT',
      text: text,
      title: title || undefined
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
    signBtn.textContent = '✍ Sign Content';
  }
}

/**
 * Copy signed output to clipboard
 */
async function copySignedOutput() {
  try {
    await navigator.clipboard.writeText(signedOutputEl.value);
    copySignedBtn.textContent = '✓ Copied!';
    setTimeout(() => {
      copySignedBtn.textContent = '📋 Copy';
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

// Initialize
document.addEventListener('DOMContentLoaded', loadTabState);
