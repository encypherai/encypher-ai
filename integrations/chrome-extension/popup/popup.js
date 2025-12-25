/**
 * Encypher C2PA Verifier - Popup Script
 */

// DOM elements
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

// Event listeners
rescanBtn.addEventListener('click', rescanPage);

// Initialize
document.addEventListener('DOMContentLoaded', loadTabState);
