/**
 * Encypher Verify - Service Worker
 * 
 * Handles API calls to the Encypher verification endpoint.
 * Runs in the background and communicates with content scripts.
 */

import debugLog from './debug-logger.js';
import { resolveSignedText, withEmbeddingPlanRequest } from './signing-utils.js';
import {
  appendVerificationDetail,
  buildVerificationDetail,
  getIconStateForTab,
  resolveSigningIdentity,
  shouldRetryVerification,
  updateTabStateWithVerification,
} from './verification-utils.js';

// API configuration (can be overridden by settings)
let API_CONFIG = {
  baseUrl: 'https://api.encypherai.com',
  dashboardBaseUrl: 'https://dashboard.encypherai.com',
  verifyEndpoint: '/api/v1/verify',
  signEndpoint: '/api/v1/sign',
  provisioningEndpoint: '/api/v1/provisioning/auto-provision',
  analyticsEndpoint: '/api/v1/analytics/discovery',
  accountEndpoint: '/api/v1/account',
  timeout: 10000
};

function deriveDashboardBaseUrl(apiBaseUrl) {
  try {
    const parsed = new URL(apiBaseUrl);
    if (parsed.hostname.startsWith('api.')) {
      parsed.hostname = `dashboard.${parsed.hostname.slice(4)}`;
    } else if (parsed.hostname === 'localhost' || parsed.hostname === '127.0.0.1') {
      parsed.port = parsed.port || '3000';
    }
    parsed.pathname = '';
    parsed.search = '';
    parsed.hash = '';
    return parsed.toString().replace(/\/$/, '');
  } catch {
    return 'https://dashboard.encypherai.com';
  }
}

async function handleDashboardApiKeyHandoff(message, sender) {
  const senderUrl = sender?.url || '';
  if (!isTrustedExternalSender(senderUrl)) {
    return { success: false, error: 'Untrusted handoff origin.' };
  }

  const apiKey = String(message?.apiKey || '').trim();
  if (!isPlausibleApiKey(apiKey)) {
    return { success: false, error: 'Invalid API key payload from dashboard.' };
  }

  const accountResult = await getAccountInfo(apiKey);
  if (!accountResult?.success || !accountResult?.data) {
    return { success: false, error: accountResult?.error || 'API key validation failed during dashboard handoff.' };
  }

  await chrome.storage.local.set({ apiKey });
  await chrome.storage.sync.set({
    extensionSetupStatus: 'completed',
    onboardingSource: 'dashboard_handoff',
    onboardingCompletedAt: new Date().toISOString(),
  });

  _accountInfoCache = {
    apiKey,
    data: accountResult.data,
    expiresAt: Date.now() + ACCOUNT_INFO_CACHE_TTL_MS,
  };

  const identity = accountResult.data.publisherDisplayName || accountResult.data.organizationName || 'your organization';
  return { success: true, source: 'dashboard_handoff', identity };
}

chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  if (message?.type !== 'DASHBOARD_API_KEY_HANDOFF') {
    sendResponse({ success: false, error: 'Unknown external message type.' });
    return false;
  }

  handleDashboardApiKeyHandoff(message, sender).then((result) => {
    sendResponse(result);
  }).catch((error) => {
    sendResponse({ success: false, error: error?.message || 'Dashboard handoff failed.' });
  });

  return true;
});

function buildDashboardAuthUrl(mode = 'login', provider = '') {
  const authPath = mode === 'signup' ? '/signup' : '/login';
  const dashboardBase = API_CONFIG.dashboardBaseUrl || deriveDashboardBaseUrl(API_CONFIG.baseUrl);
  const callbackUrl = new URL(`${dashboardBase}/extension-handoff`);
  callbackUrl.searchParams.set('source', 'chrome_extension');
  callbackUrl.searchParams.set('extensionId', chrome.runtime.id);

  const url = new URL(`${dashboardBase}${authPath}`);
  url.searchParams.set('source', 'chrome_extension');
  url.searchParams.set('extensionId', chrome.runtime.id);
  url.searchParams.set('callbackUrl', callbackUrl.toString());
  if (provider) {
    url.searchParams.set('provider', provider);
  }
  return url.toString();
}

function isPlausibleApiKey(value) {
  const key = String(value || '').trim();
  return key.length >= 16 && (key.startsWith('ency_') || key.startsWith('demo_'));
}

function isTrustedExternalSender(senderUrl) {
  if (!senderUrl) return false;
  try {
    const origin = new URL(senderUrl).origin;
    return (
      /^https:\/\/([a-z0-9-]+\.)*encypherai\.com$/i.test(origin) ||
      /^http:\/\/localhost(?::\d+)?$/i.test(origin) ||
      /^http:\/\/127\.0\.0\.1(?::\d+)?$/i.test(origin)
    );
  } catch {
    return false;
  }
}

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
const ACCOUNT_INFO_CACHE_TTL_MS = 5 * 60 * 1000;
let _accountInfoCache = {
  apiKey: null,
  data: null,
  expiresAt: 0,
};

// Load settings on startup
chrome.storage.sync.get({ apiBaseUrl: 'https://api.encypherai.com', customApiUrl: '' }, (result) => {
  if (result.apiBaseUrl === 'custom' && result.customApiUrl) {
    API_CONFIG.baseUrl = result.customApiUrl;
  } else if (result.apiBaseUrl) {
    API_CONFIG.baseUrl = result.apiBaseUrl;
  }
  API_CONFIG.dashboardBaseUrl = deriveDashboardBaseUrl(API_CONFIG.baseUrl);
  debugLog.info('init', 'Service worker loaded', { apiBaseUrl: API_CONFIG.baseUrl });
});

async function _getCachedAccountInfo(apiKey) {
  if (!apiKey) return null;

  if (
    _accountInfoCache.apiKey === apiKey &&
    _accountInfoCache.data &&
    Date.now() < _accountInfoCache.expiresAt
  ) {
    return _accountInfoCache.data;
  }

  const accountResponse = await getAccountInfo(apiKey);
  if (accountResponse?.success && accountResponse.data) {
    _accountInfoCache = {
      apiKey,
      data: accountResponse.data,
      expiresAt: Date.now() + ACCOUNT_INFO_CACHE_TTL_MS,
    };
    return accountResponse.data;
  }

  return null;
}

/**
 * Optional onboarding flow for extension users:
 * create tracked account + provision API key.
 */
async function autoProvisionExtensionUser(email) {
  try {
    const normalizedEmail = (email || '').trim().toLowerCase();
    if (!normalizedEmail || !normalizedEmail.includes('@')) {
      return { success: false, error: 'A valid email is required.' };
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

    const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.provisioningEndpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: normalizedEmail,
        source: 'api',
        source_metadata: {
          integration: 'chrome_extension',
          extension_version: chrome.runtime.getManifest().version
        },
        tier: 'free',
        auto_activate: true
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const detail = errorData.detail || errorData.error || `HTTP ${response.status}`;
      return { success: false, error: `Setup failed: ${detail}` };
    }

    const payload = await response.json();
    const provisionedKey = payload?.api_key?.api_key || payload?.api_key || '';

    if (!provisionedKey) {
      return { success: false, error: 'Setup completed but no API key was returned.' };
    }

    await chrome.storage.local.set({ apiKey: provisionedKey });
    await chrome.storage.sync.set({
      extensionSetupStatus: 'completed',
      onboardingEmail: normalizedEmail,
      onboardingCompletedAt: new Date().toISOString()
    });

    return { success: true, apiKey: provisionedKey };
  } catch (error) {
    if (error.name === 'AbortError') {
      return { success: false, error: 'Setup timed out. Please try again.' };
    }
    return { success: false, error: error.message || 'Setup failed due to a network error.' };
  }
}

// Cache for verification results (keyed by content hash)
const verificationCache = new Map();
const verificationInFlight = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// Tab state tracking
const tabState = new Map();

// Polling-oriented messages that are expected at high frequency from popup UI.
// Logging these as MSG entries creates self-generated noise in the debug tab.
const NOISY_DEBUG_MESSAGE_TYPES = new Set([
  'GET_DEBUG_LOGS',
  'GET_TAB_STATE',
]);

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
    revoked: 'RVK',
    mixed: 'MIX',
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
    revoked: '#8B5CF6',
    mixed: '#0EA5E9',
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

  // De-duplicate concurrent verification requests for identical content
  const inFlight = verificationInFlight.get(cacheKey);
  if (inFlight) {
    return inFlight;
  }

  const runVerification = async () => {
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
      
      let accountInfo = null;
      if (apiKey) {
        accountInfo = await _getCachedAccountInfo(apiKey);
      }

      const signingIdentity = resolveSigningIdentity({
        data: {
          signing_identity: verdict.signing_identity,
          publisher_display_name: verdict.publisher_display_name,
          signer_id: verdict.signer_id,
          signer_name: verdict.signer_name || verdict.organization_name,
          organization_id: verdict.organization_id,
          organization_name: verdict.organization_name,
        },
        accountInfo,
      });

      return {
        success: verdict.valid === true,
        revoked: verdict.revoked || false,
        data: {
          valid: verdict.valid,
          tampered: verdict.tampered,
          reason_code: verdict.reason_code,
          signer_id: verdict.signer_id,
          signer_name: verdict.signer_name || verdict.organization_name,
          signing_identity: signingIdentity || null,
          publisher_display_name: verdict.publisher_display_name || accountInfo?.publisherDisplayName || null,
          organization_id: verdict.organization_id,
          organization_name: verdict.organization_name,
          signed_at: verdict.timestamp,
          // Document info (free)
          document_id: verdict.document?.document_id,
          verification_url: verdict.document?.verification_url || verdict.verification_url || null,
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
  };

  const verifyPromise = (async () => {
    let result = await runVerification();
    if (!result.success && shouldRetryVerification(result)) {
      debugLog.info('verify', 'Retrying verification request after transient failure', {
        status: result.status,
        error: result.error
      });
      result = await runVerification();
    }

    // Cache final result (including invalid/revoked) to avoid API spam
    verificationCache.set(cacheKey, {
      result,
      timestamp: Date.now()
    });

    return result;
  })();

  verificationInFlight.set(cacheKey, verifyPromise);
  try {
    return await verifyPromise;
  } finally {
    verificationInFlight.delete(cacheKey);
  }
}

/**
 * Sign content using the unified Encypher /sign API
 * Features are tier-gated server-side via options
 */
async function signContent(text, title, options = {}) {
  try {
    const signMethod = String(options.signMethod || 'standard').toLowerCase();
    if (signMethod === 'merkle') {
      options.useMerkle = true;
      options.useAttribution = false;
    } else if (signMethod === 'attribution') {
      options.useAttribution = true;
      options.useMerkle = false;
    }

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
      options: withEmbeddingPlanRequest({
        document_type: options.documentType || 'article',
      })
    };

    // Embedding technique (manifest_mode)
    // TEAM_166: Normalize legacy + new values to unified micro mode + flags.
    const requestedMode = String(options.manifestMode || '').toLowerCase();
    if (requestedMode === 'basic') {
      requestBody.options.manifest_mode = 'full';
    } else {
      requestBody.options.manifest_mode = 'micro';

      // Legacy modes (backward compatibility for persisted extension settings)
      if (requestedMode === 'micro_c2pa') {
        requestBody.options.ecc = false;
      } else if (requestedMode === 'micro_ecc') {
        requestBody.options.embed_c2pa = false;
      } else if (requestedMode === 'micro') {
        // Unified default: ecc=true, embed_c2pa=true
      }

      // New extension-specific shortcuts
      if (requestedMode === 'micro_no_ecc') {
        requestBody.options.ecc = false;
      }
      if (requestedMode === 'micro_no_embed_c2pa') {
        requestBody.options.embed_c2pa = false;
      }
    }

    // Segmentation level
    if (options.segmentationLevel) {
      requestBody.options.segmentation_level = options.segmentationLevel;
    } else if (options.useMerkle) {
      requestBody.options.segmentation_level = 'sentence';
    }

    if (options.useAttribution) {
      requestBody.options.index_for_attribution = true;
    }
    if (options.previousEmbeddings && options.previousEmbeddings.length > 0) {
      requestBody.options.previous_embeddings = options.previousEmbeddings;
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
    const signedText = resolveSignedText({ visibleText: text, result });
    if (!signedText) {
      return {
        success: false,
        error: 'Signing response did not include signed text or a valid embedding plan'
      };
    }
    
    return {
      success: true,
      signedText,
      embeddingPlan: result.embedding_plan || null,
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

function _extractAccountPayload(raw) {
  if (!raw || typeof raw !== 'object') return {};
  return raw.data && typeof raw.data === 'object' ? raw.data : raw;
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
    const accountPayload = _extractAccountPayload(data);
    const organizationName = accountPayload.organization_name || accountPayload.name || accountPayload.organization?.name || null;
    const publisherDisplayName = accountPayload.publisher_display_name || accountPayload.display_name || accountPayload.publisher?.display_name || null;
    
    return {
      success: true,
      data: {
        organizationId: accountPayload.organization_id || accountPayload.organizationId || null,
        organizationName,
        publisherDisplayName,
        anonymousPublisher: Boolean(accountPayload.anonymous_publisher ?? accountPayload.publisher?.anonymous_publisher),
        tier: accountPayload.tier || accountPayload.subscription_tier || 'free',
        features: accountPayload.features || {},
        usage: accountPayload.usage || {}
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
  if (!NOISY_DEBUG_MESSAGE_TYPES.has(message.type)) {
    debugLog.msg('sw', `Received: ${message.type}`, { tabId, from: sender.tab?.url?.substring(0, 80) });
  }

  switch (message.type) {
    case 'EMBEDDINGS_DETECTED':
      if (tabId) {
        tabState.set(tabId, {
          count: message.count,
          url: message.url,
          verified: 0,
          invalid: 0,
          revoked: 0,
          details: [],
          pending: typeof message.pending === 'number' ? message.pending : message.count
        });
        updateIcon(tabId, 'found');
      }
      sendResponse({ received: true });
      break;

    case 'NO_EMBEDDINGS':
      if (tabId) {
        const existing = tabState.get(tabId);
        const hasExistingDetections = Boolean(
          (existing?.count || 0) > 0 || (Array.isArray(existing?.details) && existing.details.length > 0)
        );
        if (!hasExistingDetections) {
          tabState.set(tabId, {
            count: 0,
            url: message.url
          });
          updateIcon(tabId, 'none');
        }
      }
      sendResponse({ received: true });
      break;

    case 'REPORT_CACHED_DETECTION':
      if (tabId) {
        const current = tabState.get(tabId) || {
          count: 0,
          verified: 0,
          invalid: 0,
          revoked: 0,
          pending: 0,
          details: [],
          url: message.pageUrl,
        };

        const detectionId = message.detectionId || null;
        const hasDetail = detectionId
          ? (Array.isArray(current.details) && current.details.some((d) => d?.detectionId === detectionId))
          : false;

        if (!hasDetail) {
          const status = String(message.status || '').toLowerCase();
          if (status === 'verified') {
            current.verified += 1;
          } else if (status === 'revoked') {
            current.revoked += 1;
          } else if (status === 'invalid' || status === 'error') {
            current.invalid += 1;
          }

          const raw = message.details || {};
          const detail = {
            valid: status === 'verified',
            revoked: status === 'revoked',
            detectionId,
            signingIdentity: raw.signingIdentity || null,
            signer: raw.signer || 'Unknown signer',
            date: raw.timestamp || raw.revokedAt || null,
            markerType: raw.markerType || message.markerType || 'unknown',
            documentId: raw.documentId || null,
            verificationUrl: raw.verificationUrl || null,
            reason: raw.error || null,
          };
          current.details = appendVerificationDetail(current.details, detail);
        }

        current.url = message.pageUrl || current.url;
        current.count = Math.max(
          current.count || 0,
          current.verified + current.invalid + current.revoked + current.pending
        );
        tabState.set(tabId, current);
        updateIcon(tabId, getIconStateForTab(current));
      }
      sendResponse({ received: true });
      break;

    case 'VERIFY_CONTENT':
      verifyContent(message.text).then(result => {
        // Update tab state
        if (tabId) {
          const current = tabState.get(tabId) || {
            verified: 0,
            invalid: 0,
            revoked: 0,
            pending: 0,
            details: [],
            url: message.pageUrl
          };
          const state = updateTabStateWithVerification(current, result);
          state.url = message.pageUrl || state.url;

          const detail = buildVerificationDetail({
            markerType: message.markerType,
            result,
            detectionId: message.detectionId || null,
          });
          state.details = appendVerificationDetail(state.details, detail);

          tabState.set(tabId, state);

          // Update icon based on overall state
          updateIcon(tabId, getIconStateForTab(state));
          
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

    case 'GET_TAB_STATE': {
      const state = tabState.get(message.tabId) || { count: 0, verified: 0, invalid: 0, revoked: 0, pending: 0, details: [] };
      sendResponse(state);
      break;
    }

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

    case 'AUTO_PROVISION_EXTENSION_USER':
      autoProvisionExtensionUser(message.email).then(result => {
        sendResponse(result);
      });
      return true; // async response

    case 'OPEN_DASHBOARD_AUTH': {
      const authUrl = buildDashboardAuthUrl(message.mode, message.provider);
      chrome.tabs.create({ url: authUrl }).then(() => {
        sendResponse({ success: true, url: authUrl });
      }).catch((error) => {
        sendResponse({ success: false, error: error?.message || 'Could not open dashboard auth.' });
      });
      return true;
    }

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
        API_CONFIG.dashboardBaseUrl = deriveDashboardBaseUrl(message.value);
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
      API_CONFIG.dashboardBaseUrl = deriveDashboardBaseUrl(API_CONFIG.baseUrl);
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
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    chrome.storage.sync.set({ extensionSetupStatus: 'not_started' }).catch(() => {});
  }

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

const CONTEXT_SCRIPT_FILES = ['content/detector.js', 'content/editor-signer.js'];

function isRecoverableMessagingError(error) {
  const message = String(error?.message || '');
  return (
    message.includes('Receiving end does not exist') ||
    message.includes('Could not establish connection') ||
    message.includes('The message port closed before a response was received') ||
    message.includes('Extension context invalidated') ||
    message.includes('Extension disconnected') ||
    message.includes('No receiver acknowledgement')
  );
}

async function showPageToast(tabId, message, variant = 'info') {
  try {
    await chrome.scripting.executeScript({
      target: { tabId },
      func: (msg, type) => {
        const toast = document.createElement('div');
        toast.className = `encypher-notification encypher-notification--${type}`;
        toast.setAttribute('role', 'alert');
        toast.textContent = msg;
        document.body.appendChild(toast);
        setTimeout(() => {
          toast.style.opacity = '0';
          setTimeout(() => toast.remove(), 220);
        }, 1800);
      },
      args: [message, variant]
    });
  } catch (error) {
    // Best-effort UX hint only.
  }
}

async function sendFrameMessageWithFallback(tabId, frameId, payload, options = {}) {
  const requestedFrameId = Number.isInteger(frameId) ? frameId : 0;
  const attempts = requestedFrameId === 0 ? [0] : [requestedFrameId, 0];
  const requireAck = options.requireAck === true;

  for (const candidateFrameId of attempts) {
    try {
      const response = await chrome.tabs.sendMessage(tabId, payload, { frameId: candidateFrameId });
      if (!requireAck || response?.received === true) {
        return response;
      }
      throw new Error(`No receiver acknowledgement for ${payload?.type || 'message'}`);
    } catch (error) {
      if (!isRecoverableMessagingError(error)) {
        throw error;
      }

      try {
        await chrome.scripting.executeScript({
          target: { tabId, frameIds: [candidateFrameId] },
          files: CONTEXT_SCRIPT_FILES
        });
      } catch {
        // Continue to retry sendMessage even if explicit injection is not permitted.
      }

      try {
        const retryResponse = await chrome.tabs.sendMessage(tabId, payload, { frameId: candidateFrameId });
        if (!requireAck || retryResponse?.received === true) {
          return retryResponse;
        }
        throw new Error(`No receiver acknowledgement for ${payload?.type || 'message'}`);
      } catch (retryError) {
        if (!isRecoverableMessagingError(retryError)) {
          throw retryError;
        }
      }
    }
  }

  throw new Error('Could not establish connection to page content');
}

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (!info.selectionText) return;
  if (!tab?.id) return;
  const targetFrameId = Number.isInteger(info.frameId) ? info.frameId : 0;
  
  switch (info.menuItemId) {
    case 'verify-selected-text':
      // Send selected text to content script for verification
      try {
        await sendFrameMessageWithFallback(tab.id, targetFrameId, {
          type: 'VERIFY_SELECTION',
          text: info.selectionText,
          pageUrl: tab.url || '',
          pageTitle: tab.title || ''
        }, {
          requireAck: true
        });
      } catch (error) {
        console.error('Error verifying selection:', error);
        await showPageToast(tab.id, 'Unable to verify selected text in this frame', 'error');
      }
      break;
      
    case 'sign-selected-text':
      // Send to content script to show signing UI
      try {
        await showPageToast(tab.id, 'Signing selected text...', 'info');
        await sendFrameMessageWithFallback(tab.id, targetFrameId, {
          type: 'SIGN_SELECTION',
          text: info.selectionText
        }, {
          requireAck: true
        });
      } catch (error) {
        console.error('Error signing selection:', error);
        await showPageToast(tab.id, 'Unable to sign selected text. Try popup Sign tab.', 'error');
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

debugLog.info('init', 'Encypher Verify service worker initialized');
console.log('Encypher Verify service worker initialized');
