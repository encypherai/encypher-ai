/**
 * Encypher C2PA Verifier - Service Worker
 * 
 * Handles API calls to the Encypher verification endpoint.
 * Runs in the background and communicates with content scripts.
 */

// API configuration (can be overridden by settings)
let API_CONFIG = {
  baseUrl: 'https://api.encypherai.com',
  verifyEndpoint: '/api/v1/verify',
  publicVerifyEndpoint: '/api/v1/public/extract-and-verify',
  signEndpoint: '/api/v1/sign',
  timeout: 10000
};

// Load settings on startup
chrome.storage.sync.get({ apiBaseUrl: 'https://api.encypherai.com', customApiUrl: '' }, (result) => {
  if (result.apiBaseUrl === 'custom' && result.customApiUrl) {
    API_CONFIG.baseUrl = result.customApiUrl;
  } else if (result.apiBaseUrl) {
    API_CONFIG.baseUrl = result.apiBaseUrl;
  }
});

// Cache for verification results (keyed by content hash)
const verificationCache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// Tab state tracking
const tabState = new Map();

/**
 * Simple hash function for caching
 */
function hashContent(text) {
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    const char = text.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash.toString(16);
}

/**
 * Update extension icon based on tab state
 */
function updateIcon(tabId, state) {
  const icons = {
    none: {
      16: 'icons/icon16-gray.png',
      32: 'icons/icon32-gray.png',
      48: 'icons/icon48-gray.png',
      128: 'icons/icon128-gray.png'
    },
    found: {
      16: 'icons/icon16.png',
      32: 'icons/icon32.png',
      48: 'icons/icon48.png',
      128: 'icons/icon128.png'
    },
    verified: {
      16: 'icons/icon16-green.png',
      32: 'icons/icon32-green.png',
      48: 'icons/icon48-green.png',
      128: 'icons/icon128-green.png'
    },
    invalid: {
      16: 'icons/icon16-red.png',
      32: 'icons/icon32-red.png',
      48: 'icons/icon48-red.png',
      128: 'icons/icon128-red.png'
    }
  };

  // Use default icons for now (colored variants can be added later)
  const iconSet = icons[state] || icons.none;
  
  chrome.action.setIcon({
    tabId: tabId,
    path: icons.found // Use default colored icon
  }).catch(() => {
    // Tab may have been closed
  });

  // Update badge text
  const badgeText = {
    none: '',
    found: '?',
    verified: '✓',
    invalid: '!'
  };
  
  chrome.action.setBadgeText({
    tabId: tabId,
    text: badgeText[state] || ''
  }).catch(() => {});

  const badgeColors = {
    none: '#6B7280',
    found: '#F59E0B',
    verified: '#10B981',
    invalid: '#EF4444'
  };

  chrome.action.setBadgeBackgroundColor({
    tabId: tabId,
    color: badgeColors[state] || '#6B7280'
  }).catch(() => {});
}

/**
 * Call the Encypher verification API
 */
async function verifyContent(text) {
  // Check cache first
  const cacheKey = hashContent(text);
  const cached = verificationCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.result;
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

    const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.publicVerifyEndpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        success: false,
        error: errorData.detail || `HTTP ${response.status}`,
        status: response.status
      };
    }

    const data = await response.json();
    
    // Handle the ExtractAndVerifyResponse format
    const result = {
      success: data.valid === true,
      data: {
        valid: data.valid,
        signer_id: data.metadata?.signer_id || data.document?.organization,
        signer_name: data.document?.organization || data.metadata?.signer_id,
        signed_at: data.verified_at || data.metadata?.timestamp,
        document_id: data.document?.document_id,
        title: data.document?.title,
        author: data.document?.author,
        revoked: false, // TODO: check status list
        revoked_at: null
      },
      revoked: false,
      revoked_at: null,
      error: data.error
    };

    // Cache the result
    verificationCache.set(cacheKey, {
      result: result,
      timestamp: Date.now()
    });

    return result;
  } catch (error) {
    if (error.name === 'AbortError') {
      return {
        success: false,
        error: 'Request timed out'
      };
    }
    return {
      success: false,
      error: error.message || 'Network error'
    };
  }
}

/**
 * Sign content using the Encypher API
 */
async function signContent(text, title) {
  try {
    // Get API key from storage
    const { apiKey } = await chrome.storage.local.get({ apiKey: '' });
    
    if (!apiKey) {
      return {
        success: false,
        error: 'No API key configured. Please add your API key in settings.'
      };
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

    const requestBody = {
      text: text,
      document_type: 'article'
    };
    
    if (title) {
      requestBody.document_title = title;
    }

    const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.signEndpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify(requestBody),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      
      if (response.status === 401) {
        return {
          success: false,
          error: 'Invalid API key. Please check your settings.'
        };
      }
      if (response.status === 429) {
        return {
          success: false,
          error: 'Rate limit exceeded. Please try again later.'
        };
      }
      
      return {
        success: false,
        error: errorData.detail || `Signing failed: HTTP ${response.status}`
      };
    }

    const data = await response.json();
    
    return {
      success: true,
      signedText: data.signed_text || data.text,
      documentId: data.document_id,
      signedAt: data.signed_at
    };
  } catch (error) {
    if (error.name === 'AbortError') {
      return {
        success: false,
        error: 'Request timed out'
      };
    }
    return {
      success: false,
      error: error.message || 'Network error'
    };
  }
}

/**
 * Handle messages from content scripts and popup
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const tabId = sender.tab?.id;

  switch (message.type) {
    case 'EMBEDDINGS_DETECTED':
      if (tabId) {
        tabState.set(tabId, {
          count: message.count,
          url: message.url,
          verified: 0,
          invalid: 0,
          pending: message.count
        });
        updateIcon(tabId, 'found');
      }
      sendResponse({ received: true });
      break;

    case 'NO_EMBEDDINGS':
      if (tabId) {
        tabState.set(tabId, {
          count: 0,
          url: message.url
        });
        updateIcon(tabId, 'none');
      }
      sendResponse({ received: true });
      break;

    case 'VERIFY_CONTENT':
      verifyContent(message.text).then(result => {
        // Update tab state
        if (tabId) {
          const state = tabState.get(tabId) || { verified: 0, invalid: 0, pending: 0 };
          state.pending = Math.max(0, (state.pending || 0) - 1);
          if (result.success) {
            state.verified = (state.verified || 0) + 1;
          } else {
            state.invalid = (state.invalid || 0) + 1;
          }
          tabState.set(tabId, state);

          // Update icon based on overall state
          if (state.verified > 0 && state.invalid === 0) {
            updateIcon(tabId, 'verified');
          } else if (state.invalid > 0) {
            updateIcon(tabId, 'invalid');
          }
        }
        sendResponse(result);
      });
      return true; // async response

    case 'GET_TAB_STATE':
      const state = tabState.get(message.tabId) || { count: 0 };
      sendResponse(state);
      break;

    case 'SHOW_DETAILS':
      // Could open a new tab or popup with full details
      console.log('Show details:', message.details);
      sendResponse({ received: true });
      break;

    case 'SIGN_CONTENT':
      signContent(message.text, message.title).then(result => {
        sendResponse(result);
      });
      return true; // async response

    case 'SETTINGS_UPDATED':
      // Update API config when settings change
      if (message.setting === 'apiBaseUrl') {
        API_CONFIG.baseUrl = message.value;
      } else if (message.setting === 'cacheTtl') {
        // Could update cache TTL here
      }
      sendResponse({ received: true });
      break;

    case 'CLEAR_CACHE':
      verificationCache.clear();
      sendResponse({ received: true });
      break;

    case 'SETTINGS_RESET':
      API_CONFIG.baseUrl = 'https://api.encypherai.com';
      verificationCache.clear();
      sendResponse({ received: true });
      break;

    default:
      sendResponse({ error: 'Unknown message type' });
  }

  return false; // sync response (unless we returned true above)
});

// Clean up tab state when tab is closed
chrome.tabs.onRemoved.addListener((tabId) => {
  tabState.delete(tabId);
});

// Clean up cache periodically
setInterval(() => {
  const now = Date.now();
  for (const [key, value] of verificationCache.entries()) {
    if (now - value.timestamp > CACHE_TTL) {
      verificationCache.delete(key);
    }
  }
}, 60000); // Every minute

console.log('Encypher C2PA Verifier service worker initialized');
