/**
 * Encypher C2PA Verifier - Service Worker
 * 
 * Handles API calls to the Encypher verification endpoint.
 * Runs in the background and communicates with content scripts.
 */

import debugLog from './debug-logger.js';

// API configuration (can be overridden by settings)
let API_CONFIG = {
  baseUrl: 'https://api.encypherai.com',
  verifyEndpoint: '/api/v1/verify',
  signEndpoint: '/api/v1/sign',
  analyticsEndpoint: '/api/v1/analytics/discovery',
  accountEndpoint: '/api/v1/account',
  timeout: 10000
};

// Analytics configuration — discovery tracking is always on.
// This reports WHERE embeddings are found (URL + domain) so content owners
// can see where their signed content appears.  Reporter identity is fully
// anonymized (ephemeral session ID, no PII, no browsing history).
const ANALYTICS_CONFIG = {
  batchSize: 10,
  flushIntervalMs: 30000 // 30 seconds
};

// Analytics queue for batching discovery events
const analyticsQueue = [];
let analyticsFlushTimeout = null;

// Load settings on startup
chrome.storage.sync.get({ apiBaseUrl: 'https://api.encypherai.com', customApiUrl: '' }, (result) => {
  if (result.apiBaseUrl === 'custom' && result.customApiUrl) {
    API_CONFIG.baseUrl = result.customApiUrl;
  } else if (result.apiBaseUrl) {
    API_CONFIG.baseUrl = result.apiBaseUrl;
  }
  debugLog.info('init', 'Service worker loaded', { apiBaseUrl: API_CONFIG.baseUrl });
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
  // Use base icons for all states (colored variants not yet created)
  // State is communicated via badge text + badge color below
  const baseIcons = {
    16: 'icons/icon16.png',
    32: 'icons/icon32.png',
    48: 'icons/icon48.png',
    128: 'icons/icon128.png'
  };

  chrome.action.setIcon({
    tabId: tabId,
    path: baseIcons
  }).catch(() => {
    // Tab may have been closed
  });

  // Update badge text
  const badgeText = {
    none: '',
    found: '?',
    verified: 'OK',
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
 * Uses the unified /api/v1/verify endpoint with full C2PA compliance
 */
async function verifyContent(text, options = {}) {
  // Check cache first
  const cacheKey = hashContent(text);
  const cached = verificationCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.result;
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

    // Build request with optional parameters
    const requestBody = { text };
    
    // Add options for paid features (requires API key)
    if (options.includeMerkleProof) {
      requestBody.options = { include_merkle_proof: true };
    }

    // Get API key if available (for enhanced features)
    const { apiKey } = await chrome.storage.local.get({ apiKey: '' });
    const headers = { 'Content-Type': 'application/json' };
    if (apiKey) {
      headers['Authorization'] = `Bearer ${apiKey}`;
    }

    const verifyUrl = `${API_CONFIG.baseUrl}${API_CONFIG.verifyEndpoint}`;
    debugLog.api('verify', `POST ${verifyUrl}`, { bodyLength: text.length, hasApiKey: !!apiKey });

    const response = await fetch(verifyUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestBody),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      debugLog.error('verify', `HTTP ${response.status}`, errorData);
      return {
        success: false,
        error: errorData.error?.message || errorData.detail || `HTTP ${response.status}`,
        status: response.status
      };
    }

    const data = await response.json();
    debugLog.api('verify', 'Response OK', { valid: data.data?.valid, correlationId: data.correlation_id });
    
    // Handle the unified VerifyResponse format
    // Response: { success, data: VerifyVerdict, error, correlation_id }
    const verdict = data.data || {};
    
    const result = {
      success: verdict.valid === true,
      revoked: verdict.revoked || false,
      data: {
        valid: verdict.valid,
        tampered: verdict.tampered,
        reason_code: verdict.reason_code,
        signer_id: verdict.signer_id,
        signer_name: verdict.signer_name || verdict.organization_name,
        organization_id: verdict.organization_id,
        organization_name: verdict.organization_name,
        signed_at: verdict.timestamp,
        // Document info (free)
        document_id: verdict.document?.document_id,
        title: verdict.document?.title,
        author: verdict.document?.author,
        document_type: verdict.document?.document_type,
        // C2PA info (free)
        c2pa_validated: verdict.c2pa?.validated,
        c2pa_validation_type: verdict.c2pa?.validation_type,
        // Licensing info (free)
        license_type: verdict.licensing?.license_type,
        license_url: verdict.licensing?.license_url,
        // Merkle proof (paid - only if requested and authorized)
        merkle_root: verdict.merkle_proof?.root_hash,
        merkle_verified: verdict.merkle_proof?.verified,
        // Status
        revoked: verdict.revoked || false,
        revoked_at: verdict.revoked_at || null
      },
      correlation_id: data.correlation_id,
      error: data.error?.message
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
 * Sign content using the unified Encypher /sign API
 * Features are tier-gated server-side via options
 */
async function signContent(text, title, options = {}) {
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

    // Build unified request body with options object
    const requestBody = {
      text: text,
      document_title: title || undefined,
      options: {
        document_type: options.documentType || 'article',
      }
    };
    
    // Advanced options for professional+ tiers (tier-gated server-side)
    if (options.useMerkle || options.segmentationLevel) {
      requestBody.options.segmentation_level = options.segmentationLevel || 'sentence';
    }
    if (options.useAttribution) {
      requestBody.options.index_for_attribution = true;
    }

    // Always use unified /sign endpoint - features gated by tier server-side
    const signUrl = `${API_CONFIG.baseUrl}${API_CONFIG.signEndpoint}`;
    debugLog.api('sign', `POST ${signUrl}`, { bodyLength: text.length, title, options });

    const response = await fetch(signUrl, {
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
      debugLog.error('sign', `HTTP ${response.status}`, errorData);
      
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
      if (response.status === 403) {
        // Handle tier-gated feature errors
        const errorMsg = errorData.error?.message || errorData.detail?.message || 'Feature not available on your plan.';
        const hint = errorData.error?.hint || '';
        return {
          success: false,
          error: hint ? `${errorMsg} ${hint}` : errorMsg
        };
      }
      
      return {
        success: false,
        error: errorData.error?.message || errorData.detail || `Signing failed: HTTP ${response.status}`
      };
    }

    const data = await response.json();
    debugLog.api('sign', 'Response OK', { documentId: data.data?.document?.document_id, tier: data.meta?.tier });
    
    // Handle new unified response format: { success, data: { document: {...} }, meta: {...} }
    const result = data.data?.document || data.data || data;
    
    return {
      success: true,
      signedText: result.signed_text || result.embedded_content,
      documentId: result.document_id,
      verificationUrl: result.verification_url,
      merkleRoot: result.merkle_root,
      totalSegments: result.total_segments,
      tier: data.meta?.tier,
      featuresUsed: data.meta?.features_used,
      featuresGated: data.meta?.features_gated
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
 * Track embedding discovery for analytics
 * This "phones home" to report where embeddings are found and who owns them
 */
function trackEmbeddingDiscovery(discoveryData) {
  
  const event = {
    timestamp: new Date().toISOString(),
    eventType: 'embedding_discovered',
    pageUrl: discoveryData.pageUrl,
    pageDomain: new URL(discoveryData.pageUrl).hostname,
    pageTitle: discoveryData.pageTitle,
    // Embedding owner info
    signerId: discoveryData.signerId,
    signerName: discoveryData.signerName,
    organizationId: discoveryData.organizationId,
    documentId: discoveryData.documentId,
    originalDomain: discoveryData.originalDomain || null,
    // Verification result
    verified: discoveryData.verified,
    verificationStatus: discoveryData.status,
    markerType: discoveryData.markerType,
    // Context
    embeddingCount: discoveryData.embeddingCount || 1,
    // Extension metadata
    extensionVersion: chrome.runtime.getManifest().version,
    // Anonymized user context (no PII)
    sessionId: getOrCreateSessionId()
  };
  
  analyticsQueue.push(event);
  
  // Flush if batch size reached
  if (analyticsQueue.length >= ANALYTICS_CONFIG.batchSize) {
    flushAnalytics();
  } else {
    // Schedule flush
    scheduleAnalyticsFlush();
  }
}

/**
 * Get or create a session ID for analytics (anonymous, no PII)
 */
function getOrCreateSessionId() {
  if (!getOrCreateSessionId._sessionId) {
    getOrCreateSessionId._sessionId = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  return getOrCreateSessionId._sessionId;
}

/**
 * Schedule analytics flush
 */
function scheduleAnalyticsFlush() {
  if (analyticsFlushTimeout) return;
  
  analyticsFlushTimeout = setTimeout(() => {
    flushAnalytics();
    analyticsFlushTimeout = null;
  }, ANALYTICS_CONFIG.flushIntervalMs);
}

/**
 * Flush analytics queue to server
 */
async function flushAnalytics() {
  if (analyticsQueue.length === 0) return;
  
  const events = analyticsQueue.splice(0, analyticsQueue.length);
  
  try {
    // Get API key if available (for authenticated analytics)
    const { apiKey } = await chrome.storage.local.get({ apiKey: '' });
    
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (apiKey) {
      headers['Authorization'] = `Bearer ${apiKey}`;
    }
    
    const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.analyticsEndpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        events,
        source: 'chrome_extension',
        version: chrome.runtime.getManifest().version
      })
    });
    
    if (!response.ok) {
      // Re-queue events on failure (with limit to prevent memory issues)
      if (analyticsQueue.length < 100) {
        analyticsQueue.push(...events);
      }
      console.warn('Analytics flush failed:', response.status);
    } else {
      console.log(`Analytics: sent ${events.length} discovery events`);
    }
  } catch (error) {
    // Re-queue on network error
    if (analyticsQueue.length < 100) {
      analyticsQueue.push(...events);
    }
    console.warn('Analytics flush error:', error.message);
  }
}

/**
 * Get analytics summary for the current session
 */
function getAnalyticsSummary() {
  return {
    queuedEvents: analyticsQueue.length,
    sessionId: getOrCreateSessionId(),
    enabled: true  // Discovery tracking is always on (non-optional)
  };
}

/**
 * Get account info from the Encypher API
 */
async function getAccountInfo(apiKey) {
  try {
    if (!apiKey) {
      return { success: false, error: 'No API key' };
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

    const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.accountEndpoint}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      return { success: false, error: `HTTP ${response.status}` };
    }

    const data = await response.json();
    
    return {
      success: true,
      data: {
        organizationId: data.organization_id,
        organizationName: data.organization_name,
        tier: data.tier || data.subscription_tier || 'free',
        features: data.features || {},
        usage: data.usage || {}
      }
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Handle messages from content scripts and popup
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const tabId = sender.tab?.id;
  debugLog.msg('sw', `Received: ${message.type}`, { tabId, from: sender.tab?.url?.substring(0, 80) });

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
          const state = tabState.get(tabId) || { verified: 0, invalid: 0, pending: 0, url: message.pageUrl };
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
          
          // Track discovery for analytics (phone home)
          trackEmbeddingDiscovery({
            pageUrl: message.pageUrl || state.url,
            pageTitle: message.pageTitle,
            signerId: result.data?.signer_id,
            signerName: result.data?.signer_name,
            organizationId: result.data?.organization_id,
            documentId: result.data?.document_id,
            originalDomain: result.data?.original_domain || result.data?.signing_domain,
            verified: result.success,
            status: result.success ? 'verified' : (result.revoked ? 'revoked' : 'invalid'),
            markerType: message.markerType
          });
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
      signContent(message.text, message.title, message.options || {}).then(result => {
        sendResponse(result);
      });
      return true; // async response

    case 'GET_ACCOUNT_INFO':
      getAccountInfo(message.apiKey).then(result => {
        sendResponse(result);
      });
      return true; // async response

    case 'CONTENT_DEBUG_LOG':
      // TEAM_151: Forward content script logs into the debug logger
      debugLog[message.level?.toLowerCase() === 'error' ? 'error' :
               message.level?.toLowerCase() === 'warn' ? 'warn' :
               message.level === 'API' ? 'api' :
               message.level === 'MSG' ? 'msg' :
               message.level === 'DEBUG' ? 'debug' : 'info'](
        message.category || 'content',
        message.message || '',
        message.data
      );
      sendResponse({ received: true });
      break;

    case 'GET_DEBUG_LOGS':
      debugLog.getLogs().then(logs => sendResponse({ logs }));
      return true; // async response

    case 'CLEAR_DEBUG_LOGS':
      debugLog.clearLogs().then(() => sendResponse({ cleared: true }));
      return true;

    case 'GET_DEV_MODE':
      debugLog.isDevMode().then(devMode => sendResponse({ devMode }));
      return true;

    case 'SETTINGS_UPDATED':
      // Update API config when settings change
      if (message.setting === 'apiBaseUrl') {
        API_CONFIG.baseUrl = message.value;
        debugLog.info('settings', 'API URL changed', { newUrl: message.value });
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
      analyticsQueue.length = 0;
      sendResponse({ received: true });
      break;

    case 'SET_ANALYTICS_ENABLED':
      // Discovery tracking is non-optional — always enabled.
      // This handler is kept for backward compatibility but is a no-op.
      sendResponse({ received: true, enabled: true });
      break;

    case 'GET_ANALYTICS_SUMMARY':
      sendResponse(getAnalyticsSummary());
      break;

    case 'FLUSH_ANALYTICS':
      flushAnalytics().then(() => {
        sendResponse({ received: true, flushed: true });
      });
      return true; // async response

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

// Create context menus on install
chrome.runtime.onInstalled.addListener(() => {
  // Verify selected text
  chrome.contextMenus.create({
    id: 'verify-selected-text',
    title: 'Verify with Encypher',
    contexts: ['selection']
  });
  
  // Sign selected text (requires API key)
  chrome.contextMenus.create({
    id: 'sign-selected-text',
    title: 'Sign with Encypher',
    contexts: ['selection']
  });
  
  // Separator
  chrome.contextMenus.create({
    id: 'encypher-separator',
    type: 'separator',
    contexts: ['selection']
  });
  
  // Copy signed text
  chrome.contextMenus.create({
    id: 'copy-signed-text',
    title: 'Sign & Copy to Clipboard',
    contexts: ['selection']
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (!info.selectionText) return;
  
  switch (info.menuItemId) {
    case 'verify-selected-text':
      // Send selected text to content script for verification
      try {
        await chrome.tabs.sendMessage(tab.id, {
          type: 'VERIFY_SELECTION',
          text: info.selectionText
        });
      } catch (error) {
        console.error('Error verifying selection:', error);
      }
      break;
      
    case 'sign-selected-text':
      // Send to content script to show signing UI
      try {
        await chrome.tabs.sendMessage(tab.id, {
          type: 'SIGN_SELECTION',
          text: info.selectionText
        });
      } catch (error) {
        console.error('Error signing selection:', error);
      }
      break;
      
    case 'copy-signed-text':
      // Sign and copy to clipboard directly
      try {
        const result = await signContent(info.selectionText);
        if (result.success) {
          // Use offscreen document or inject script to copy
          await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: (text) => {
              navigator.clipboard.writeText(text).then(() => {
                // Show notification
                const notification = document.createElement('div');
                notification.className = 'encypher-notification encypher-notification--success';
                notification.setAttribute('role', 'alert');
                notification.innerHTML = `
                  <div class="encypher-notification__icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></div>
                  <div class="encypher-notification__content">Signed text copied to clipboard!</div>
                `;
                document.body.appendChild(notification);
                setTimeout(() => {
                  notification.style.opacity = '0';
                  setTimeout(() => notification.remove(), 300);
                }, 4000);
              });
            },
            args: [result.signedText]
          });
        } else {
          // Show error notification
          await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: (errorMsg) => {
              const notification = document.createElement('div');
              notification.className = 'encypher-notification encypher-notification--error';
              notification.setAttribute('role', 'alert');
              notification.innerHTML = `
                <div class="encypher-notification__icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></div>
                <div class="encypher-notification__content">${errorMsg}</div>
              `;
              document.body.appendChild(notification);
              setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
              }, 4000);
            },
            args: [result.error || 'Signing failed']
          });
        }
      } catch (error) {
        console.error('Error with sign & copy:', error);
      }
      break;
  }
});

debugLog.info('init', 'Encypher C2PA Verifier service worker initialized');
console.log('Encypher C2PA Verifier service worker initialized');
