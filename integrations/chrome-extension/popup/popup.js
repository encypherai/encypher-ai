/**
 * Encypher Verify - Popup Script
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
const revokedCountEl = document.getElementById('revoked-count');
const detailsListEl = document.getElementById('details-list');
const verifySignCtaEl = document.getElementById('verify-sign-cta');

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
const signEmbeddingTechniqueEl = document.getElementById('sign-embedding-technique');
const signSegmentationLevelEl = document.getElementById('sign-segmentation-level');
const signBtn = document.getElementById('sign-btn');
const signedOutputEl = document.getElementById('signed-output');
const copySignedBtn = document.getElementById('copy-signed');
const signAnotherBtn = document.getElementById('sign-another');
const signRetryBtn = document.getElementById('sign-retry');
const signErrorMessageEl = document.getElementById('sign-error-message');
const signIdentityEl = document.getElementById('sign-identity');
const onboardingStatusEl = document.getElementById('onboarding-status');
const onboardingDashboardLoginBtn = document.getElementById('onboarding-dashboard-login');
const onboardingDashboardSignupBtn = document.getElementById('onboarding-dashboard-signup');
const onboardingDashboardGoogleBtn = document.getElementById('onboarding-dashboard-google');
const onboardingDashboardGithubBtn = document.getElementById('onboarding-dashboard-github');
const onboardingDashboardPasskeyBtn = document.getElementById('onboarding-dashboard-passkey');

// DOM elements - Advanced options
const tierBadgeEl = document.getElementById('tier-badge');
const toggleAdvancedBtn = document.getElementById('toggle-advanced');
const advancedPanelEl = document.getElementById('advanced-panel');
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
let currentTabId = null;

// Debug state
let currentDebugFilter = 'all';
let debugAutoRefreshInterval = null;

// Tab elements
const tabs = document.querySelectorAll('.popup__tab');

const DEFAULT_SIGN_SETTINGS = {
  defaultDocumentType: 'article',
  defaultDocType: 'article',
  defaultEmbeddingTechnique: 'micro_no_embed_c2pa',
  defaultSegmentationLevel: 'document',
};

function normalizeEmbeddingTechnique(value) {
  const mode = String(value || '').toLowerCase();
  if (mode === 'micro_ecc_c2pa' || mode === 'micro') return 'micro';
  if (mode === 'micro_legacy_safe') return 'micro_legacy_safe';
  if (mode === 'micro_ecc' || mode === 'micro_no_embed_c2pa') return 'micro_no_embed_c2pa';
  return 'micro_no_embed_c2pa';
}

/**
 * Show a specific state and hide others
 */
function showState(state) {
  loadingEl.hidden = state !== 'loading';
  noContentEl.hidden = state !== 'empty';
  contentFoundEl.hidden = state !== 'found';
  errorEl.hidden = state !== 'error';
}

function enforceSignMethodByTier(info) {
  const tier = (info?.tier || 'free').toLowerCase();
  const isEnterprise = ['enterprise', 'business'].includes(tier);

  if (signMerkleEl) signMerkleEl.disabled = !isEnterprise;
  if (signAttributionEl) signAttributionEl.disabled = !isEnterprise;

  // Disable "Word (Enterprise)" segmentation option for non-enterprise
  if (signSegmentationLevelEl) {
    [...signSegmentationLevelEl.options].forEach((option) => {
      if (option.value === 'word') {
        option.disabled = !isEnterprise;
      }
    });
    if (!isEnterprise && signSegmentationLevelEl.value === 'word') {
      signSegmentationLevelEl.value = 'sentence';
    }
  }
}

async function loadSignDefaults() {
  try {
    const settings = await chrome.storage.sync.get(DEFAULT_SIGN_SETTINGS);
    if (signDocTypeEl) signDocTypeEl.value = settings.defaultDocumentType || settings.defaultDocType || 'article';
    if (signEmbeddingTechniqueEl) {
      signEmbeddingTechniqueEl.value = normalizeEmbeddingTechnique(settings.defaultEmbeddingTechnique || 'micro_no_embed_c2pa');
    }
    if (signSegmentationLevelEl) signSegmentationLevelEl.value = settings.defaultSegmentationLevel || 'document';
    enforceSignMethodByTier(accountInfo);
  } catch (error) {
    // Keep in-UI defaults when storage read fails.
  }
}

function _isPlausibleApiKey(value) {
  const key = String(value || '').trim();
  return key.length >= 16 && (key.startsWith('ency_') || key.startsWith('demo_'));
}

async function openDashboardAuth(mode, provider = '') {
  try {
    const response = await chrome.runtime.sendMessage({
      type: 'OPEN_DASHBOARD_AUTH',
      mode,
      provider,
    });
    if (!response?.success) {
      throw new Error(response?.error || 'Unable to open dashboard auth flow.');
    }
    onboardingStatusEl.textContent = 'Dashboard opened. Complete sign-in and your extension will connect automatically.';
    onboardingStatusEl.className = 'popup__onboarding-status popup__onboarding-status--neutral';
  } catch (error) {
    onboardingStatusEl.textContent = error?.message || 'Unable to open Dashboard auth flow.';
    onboardingStatusEl.className = 'popup__onboarding-status popup__onboarding-status--error';
  }
}


function switchToSignTab() {
  switchTab('sign');
}

/**
 * Update the summary counts
 */
function updateCounts(state) {
  verifiedCountEl.textContent = state.verified || 0;
  pendingCountEl.textContent = state.pending || 0;
  invalidCountEl.textContent = state.invalid || 0;
  revokedCountEl.textContent = state.revoked || 0;
}

function formatDetailDate(rawDate) {
  if (!rawDate) return 'Date unknown';
  const parsed = new Date(rawDate);
  if (Number.isNaN(parsed.getTime())) {
    return rawDate;
  }
  return parsed.toLocaleString();
}

function markerTypeLabel(markerType) {
  const marker = String(markerType || '').toLowerCase();
  if (marker === 'c2pa') return 'C2PA';
  if (marker === 'c2pa_image') return 'C2PA Image';
  if (marker === 'c2pa_audio') return 'C2PA Audio';
  if (marker === 'c2pa_video') return 'C2PA Video';
  if (marker === 'c2pa_document') return 'C2PA Document';
  if (marker === 'encypher') return 'Encypher';
  if (marker === 'micro') return 'Micro';
  return 'Unknown';
}

function _mediaTypeLabel(detail) {
  const ct = String(detail?.contentType || '').toLowerCase();
  if (ct === 'audio') return 'Audio';
  if (ct === 'video') return 'Video';
  if (ct === 'document') return 'Document';
  const mt = String(detail?.markerType || '').toLowerCase();
  if (mt === 'c2pa_audio') return 'Audio';
  if (mt === 'c2pa_video') return 'Video';
  if (mt === 'c2pa_document') return 'Document';
  return 'Image';
}

function buildVerificationLink(documentId) {
  if (!documentId) return null;
  return `https://api.encypher.com/api/v1/public/verify/${encodeURIComponent(documentId)}`;
}

function safeExternalUrl(urlValue) {
  if (!urlValue) return null;
  try {
    const parsed = new URL(String(urlValue));
    if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
      return parsed.toString();
    }
  } catch {
    return null;
  }
  return null;
}

async function locateEmbeddingOnPage(detectionId) {
  if (!detectionId || !currentTabId) return;

  try {
    const response = await chrome.tabs.sendMessage(currentTabId, {
      type: 'FOCUS_EMBEDDING',
      detectionId,
    });

    if (!response?.found) {
      await rescanPage();
    }
  } catch (error) {
    console.error('Error locating embedding:', error);
  }
}

async function locateMediaOnPage(mediaUrl) {
  if (!mediaUrl || !currentTabId) return;

  try {
    await chrome.tabs.sendMessage(currentTabId, {
      type: 'FOCUS_MEDIA',
      mediaUrl,
    });
  } catch (error) {
    console.error('Error locating media:', error);
  }
}

async function verifyImageFromPopup(srcUrl) {
  if (!srcUrl || !currentTabId) return;

  try {
    await chrome.tabs.sendMessage(currentTabId, {
      type: 'VERIFY_IMAGE_CONTEXT',
      srcUrl,
    });
    // Reload state after a delay to pick up the result
    setTimeout(loadTabState, 2000);
  } catch (error) {
    console.error('Error verifying image from popup:', error);
  }
}

async function verifyMediaFromPopup(srcUrl, mediaType) {
  if (!srcUrl || !currentTabId) return;

  const messageType = mediaType === 'audio' ? 'VERIFY_AUDIO_CONTEXT' : 'VERIFY_VIDEO_CONTEXT';
  try {
    await chrome.tabs.sendMessage(currentTabId, {
      type: messageType,
      srcUrl,
    });
    setTimeout(loadTabState, 3000);
  } catch (error) {
    console.error(`Error verifying ${mediaType} from popup:`, error);
  }
}

async function verifyDocumentFromPopup(srcUrl) {
  if (!srcUrl || !currentTabId) return;

  try {
    await chrome.tabs.sendMessage(currentTabId, {
      type: 'VERIFY_DOCUMENT_CONTEXT',
      srcUrl,
    });
    setTimeout(loadTabState, 3000);
  } catch (error) {
    console.error('Error verifying document from popup:', error);
  }
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
    const statusLabel = detail.revoked ? 'Revoked' : (detail.valid ? 'Verified' : 'Invalid');
    const isMedia = detail.contentType === 'image' || detail.contentType === 'audio' || detail.contentType === 'video' || detail.contentType === 'document' || detail.markerType === 'c2pa_image' || detail.markerType === 'c2pa_audio' || detail.markerType === 'c2pa_video' || detail.markerType === 'c2pa_document';
    const markerLabel = markerTypeLabel(detail.markerType);
    const detailDate = formatDetailDate(detail.date);
    const verificationUrl = safeExternalUrl(detail.verificationUrl) || safeExternalUrl(buildVerificationLink(detail.documentId));
    const verificationLinkHtml = verificationUrl
      ? `<a class="popup__detail-link" href="${verificationUrl}" target="_blank" rel="noopener noreferrer">View verification</a>`
      : '';
    const locateButtonHtml = isMedia && detail.mediaUrl
      ? `<button class="popup__detail-action" type="button" data-action="locate-media" data-media-url="${detail.mediaUrl}">Locate on page</button>`
      : (detail.detectionId
        ? `<button class="popup__detail-action" type="button" data-action="locate-embedding" data-detection-id="${detail.detectionId}">Locate on page</button>`
        : '');
    const iconSymbol = detail.revoked
      ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>'
      : (detail.valid
        ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
        : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>');

    item.innerHTML = `
      <div class="popup__detail-icon popup__detail-icon--${iconClass}">${iconSymbol}</div>
      <div class="popup__detail-info">
        <div class="popup__detail-signer">${detail.signer || 'Unknown Signer'}</div>
        <div class="popup__detail-date">${detailDate}</div>
        <div class="popup__detail-meta">${isMedia ? _mediaTypeLabel(detail) + ' · ' : ''}${statusLabel} · ${markerLabel}</div>
        ${locateButtonHtml}
        ${verificationLinkHtml}
      </div>
    `;

    const locateButton = item.querySelector('[data-action="locate-embedding"]');
    if (locateButton) {
      locateButton.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        locateEmbeddingOnPage(detail.detectionId);
      });
    }

    const locateMediaButton = item.querySelector('[data-action="locate-media"]');
    if (locateMediaButton) {
      locateMediaButton.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        locateMediaOnPage(detail.mediaUrl);
      });
    }

    detailsListEl.appendChild(item);
  }
}

/**
 * Render the media (images, audio, video, documents) section in the popup verify tab
 */
function renderMediaSection(imageData, audioVideoData, documentData) {
  const mediaSectionEl = document.getElementById('media-section');
  const mediaListEl = document.getElementById('media-list');
  if (!mediaSectionEl || !mediaListEl) return;

  const imageTotal = imageData?.total || 0;
  const avTotal = audioVideoData?.total || 0;
  const docTotal = documentData?.total || 0;
  const totalMedia = imageTotal + avTotal + docTotal;

  if (totalMedia === 0) {
    mediaSectionEl.hidden = true;
    return;
  }

  mediaSectionEl.hidden = false;
  const titleEl = mediaSectionEl.querySelector('.popup__media-title');
  if (titleEl) {
    titleEl.textContent = `Media on page (${totalMedia})`;
  }

  mediaListEl.innerHTML = '';

  // Show up to 10 images
  const images = (imageData?.images || []).slice(0, 10);
  for (const img of images) {
    const item = document.createElement('div');
    item.className = 'popup__media-item';

    const statusClass = img.status === 'verified' ? 'verified'
      : img.status === 'invalid' ? 'invalid'
      : img.status === 'error' ? 'invalid'
      : 'pending';

    const statusLabel = img.status
      ? (img.status === 'verified' ? 'Verified' : (img.status === 'error' ? 'Error' : 'Invalid'))
      : 'Not verified';

    const filename = img.src.split('/').pop().split('?')[0].slice(0, 30) || 'image';

    const actionHtml = img.status
      ? `<span class="popup__media-status popup__media-status--${statusClass}">${statusLabel}</span>`
      : `<button class="popup__media-verify-btn" type="button" data-action="verify-image" data-src="${img.src}">Verify</button>`;

    item.innerHTML = `
      <img class="popup__media-thumb" src="${img.src}" alt="" width="32" height="32">
      <span class="popup__media-name" title="${img.src}">${filename}</span>
      ${actionHtml}
    `;

    const verifyBtn = item.querySelector('[data-action="verify-image"]');
    if (verifyBtn) {
      verifyBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        verifyImageFromPopup(img.src);
        verifyBtn.textContent = '...';
        verifyBtn.disabled = true;
      });
    }

    mediaListEl.appendChild(item);
  }

  // Show audio/video entries
  const avItems = (audioVideoData?.media || []).slice(0, 10);
  for (const av of avItems) {
    const item = document.createElement('div');
    item.className = 'popup__media-item';

    const statusClass = av.status === 'verified' ? 'verified'
      : av.status === 'invalid' ? 'invalid'
      : av.status === 'error' ? 'invalid'
      : 'pending';

    const statusLabel = av.status
      ? (av.status === 'verified' ? 'Verified' : (av.status === 'error' ? 'Error' : 'Invalid'))
      : 'Not verified';

    const filename = av.src.split('/').pop().split('?')[0].slice(0, 30) || av.mediaType;
    const typeIcon = av.mediaType === 'audio' ? '&#x266B;' : '&#x25B6;';

    const actionHtml = av.status
      ? `<span class="popup__media-status popup__media-status--${statusClass}">${statusLabel}</span>`
      : `<button class="popup__media-verify-btn" type="button" data-action="verify-media" data-src="${av.src}" data-media-type="${av.mediaType}">Verify</button>`;

    item.innerHTML = `
      <span class="popup__media-type-icon">${typeIcon}</span>
      <span class="popup__media-name" title="${av.src}">${filename}</span>
      ${actionHtml}
    `;

    const verifyBtn = item.querySelector('[data-action="verify-media"]');
    if (verifyBtn) {
      verifyBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        verifyMediaFromPopup(av.src, av.mediaType);
        verifyBtn.textContent = '...';
        verifyBtn.disabled = true;
      });
    }

    // Add locate button if verified
    if (av.status && av.status !== 'pending') {
      const locateBtn = document.createElement('button');
      locateBtn.className = 'popup__media-verify-btn';
      locateBtn.type = 'button';
      locateBtn.dataset.action = 'locate-media';
      locateBtn.textContent = 'Locate';
      locateBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        locateMediaOnPage(av.src);
      });
      item.appendChild(locateBtn);
    }

    mediaListEl.appendChild(item);
  }

  // Show document entries
  const docItems = (documentData?.documents || []).slice(0, 10);
  for (const doc of docItems) {
    const item = document.createElement('div');
    item.className = 'popup__media-item';

    const statusClass = doc.status === 'verified' ? 'verified'
      : doc.status === 'invalid' ? 'invalid'
      : doc.status === 'error' ? 'invalid'
      : 'pending';

    const statusLabel = doc.status
      ? (doc.status === 'verified' ? 'Verified' : (doc.status === 'error' ? 'Error' : 'Invalid'))
      : 'Not verified';

    const filename = doc.src.split('/').pop().split('?')[0].slice(0, 30) || 'document';
    const typeIcon = '&#x1F4C4;';

    const actionHtml = doc.status
      ? `<span class="popup__media-status popup__media-status--${statusClass}">${statusLabel}</span>`
      : `<button class="popup__media-verify-btn" type="button" data-action="verify-document" data-src="${doc.src}">Verify</button>`;

    item.innerHTML = `
      <span class="popup__media-type-icon">${typeIcon}</span>
      <span class="popup__media-name" title="${doc.src}">${filename}</span>
      ${actionHtml}
    `;

    const verifyBtn = item.querySelector('[data-action="verify-document"]');
    if (verifyBtn) {
      verifyBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        verifyDocumentFromPopup(doc.src);
        verifyBtn.textContent = '...';
        verifyBtn.disabled = true;
      });
    }

    if (doc.status && doc.status !== 'pending') {
      const locateBtn = document.createElement('button');
      locateBtn.className = 'popup__media-verify-btn';
      locateBtn.type = 'button';
      locateBtn.dataset.action = 'locate-media';
      locateBtn.textContent = 'Locate';
      locateBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        locateMediaOnPage(doc.src);
      });
      item.appendChild(locateBtn);
    }

    mediaListEl.appendChild(item);
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
    currentTabId = tab.id;

    // Show "Set up free signing" CTA only when the user has no API key
    if (verifySignCtaEl) {
      const { apiKey } = await chrome.storage.local.get({ apiKey: '' });
      verifySignCtaEl.closest('.popup__verify-cta').hidden = Boolean(apiKey);
    }

    // Get state from service worker
    const state = await chrome.runtime.sendMessage({
      type: 'GET_TAB_STATE',
      tabId: tab.id
    });

    const hasDetails = Array.isArray(state.details) && state.details.length > 0;

    // Fetch image inventory from content script
    let imageData = null;
    try {
      imageData = await chrome.tabs.sendMessage(tab.id, { type: 'GET_PAGE_IMAGES' });
    } catch { /* content script may not be ready */ }

    // Fetch audio/video inventory from content script
    let audioVideoData = null;
    try {
      audioVideoData = await chrome.tabs.sendMessage(tab.id, { type: 'GET_PAGE_MEDIA' });
    } catch { /* content script may not be ready */ }

    // Fetch document inventory from content script
    let documentData = null;
    try {
      documentData = await chrome.tabs.sendMessage(tab.id, { type: 'GET_PAGE_DOCUMENTS' });
    } catch { /* content script may not be ready */ }

    const hasImages = imageData && imageData.total > 0;
    const hasAudioVideo = audioVideoData && audioVideoData.total > 0;
    const hasDocuments = documentData && documentData.total > 0;

    if (!state || (state.count === 0 && !hasDetails && !hasImages && !hasAudioVideo && !hasDocuments)) {
      showState('empty');
    } else {
      showState('found');
      updateCounts(state);

      // If we have cached details, render them
      if (state.details) {
        renderDetails(state.details);
      }

      // Render media section (images, audio, video, documents)
      renderMediaSection(imageData, audioVideoData, documentData);
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
    await chrome.tabs.sendMessage(tab.id, { type: 'RESCAN' });

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
    const syncState = await chrome.storage.sync.get({ extensionSetupStatus: 'not_started' });
    await loadSignDefaults();

    if (result.apiKey) {
      showSignState('ready');
      // Fetch account info to get tier
      fetchAccountInfo(result.apiKey);
    } else {
      showSignState('no-key');
      if (onboardingStatusEl && syncState.extensionSetupStatus === 'completed') {
        onboardingStatusEl.textContent = 'Setup is marked complete. Add or refresh your API key in Settings.';
        onboardingStatusEl.className = 'popup__onboarding-status popup__onboarding-status--neutral';
      }
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
      updateSignIdentity(accountInfo);
    }
  } catch (error) {
    console.error('Error fetching account info:', error);
  }
}

function updateSignIdentity(info) {
  if (!signIdentityEl) return;
  const publisherDisplayName = info?.publisherDisplayName;
  const signerName = publisherDisplayName || info?.organizationName || 'your organization';
  signIdentityEl.textContent = `Signing as: ${signerName}`;
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
  enforceSignMethodByTier(info);

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

  // Gather options
  const docType = signDocTypeEl?.value || 'article';
  const manifestMode = signEmbeddingTechniqueEl?.value || 'micro_no_embed_c2pa';
  const segmentationLevel = signSegmentationLevelEl?.value || 'document';
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
        manifestMode,
        segmentationLevel,
        documentType: docType,
        useMerkle,
        useAttribution
      }
    });

    if (response && response.success && response.signedText) {
      signedOutputEl.value = response.signedText;

      // Copy to clipboard
      await navigator.clipboard.writeText(response.signedText);

      showSignState('result');
    } else {
      signErrorMessageEl.textContent = response?.error || 'Signing failed. No signed content was returned.';
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
onboardingDashboardLoginBtn?.addEventListener('click', () => openDashboardAuth('login'));
onboardingDashboardSignupBtn?.addEventListener('click', () => openDashboardAuth('signup'));
onboardingDashboardGoogleBtn?.addEventListener('click', () => openDashboardAuth('login', 'google'));
onboardingDashboardGithubBtn?.addEventListener('click', () => openDashboardAuth('login', 'github'));
onboardingDashboardPasskeyBtn?.addEventListener('click', () => openDashboardAuth('login', 'passkey'));
verifySignCtaEl?.addEventListener('click', switchToSignTab);

// Event listener - Advanced options toggle
toggleAdvancedBtn?.addEventListener('click', () => {
  const isOpen = advancedPanelEl.hidden;
  advancedPanelEl.hidden = !isOpen;
  toggleAdvancedBtn.classList.toggle('open', isOpen);
});

signMerkleEl?.addEventListener('change', () => {
  if (signMerkleEl.checked && signAttributionEl) signAttributionEl.checked = false;
});

signAttributionEl?.addEventListener('change', () => {
  if (signAttributionEl.checked && signMerkleEl) signMerkleEl.checked = false;
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
        apiBaseUrl: 'https://api.encypher.com',
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

document.getElementById('debug-reload')?.addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  await chrome.runtime.sendMessage({ type: 'DEV_RELOAD', tabId: tab?.id ?? null });
});

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
    loadSignDefaults();
    loadTabState();
    checkDevMode();
  });
} else {
  loadSignDefaults();
  loadTabState();
  checkDevMode();
}
