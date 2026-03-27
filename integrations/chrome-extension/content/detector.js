/**
 * Encypher Verify - Content Detector
 *
 * Scans the page for C2PA and Encypher text embeddings using Unicode variation selectors.
 * When found, injects verification badges and communicates with the service worker.
 *
 * Key design principles:
 * - Only hit the verification API when a valid embedding (C2PA/Encypher magic bytes) is found
 * - Deduplicate: never re-verify the same content (tracked by content hash)
 * - MutationObserver scans only newly added DOM nodes, not the full page
 * - Debounce mutations for infinite-scroll pages (LinkedIn, Twitter, etc.)
 *
 * Supports two marker types:
 * - C2PA Text Manifest: "C2PATXT\0" (standard C2PA format)
 * - Encypher Marker: "ENCYPHER" (Encypher-specific format)
 */

// TEAM_151: Lightweight content script logger (sends to service worker storage)
function _debugLog(level, category, message, data) {
  try {
    chrome.runtime.sendMessage({
      type: 'CONTENT_DEBUG_LOG',
      level, category, message, data
    }).catch(() => {});
  } catch { /* ignore if extension context invalidated */ }
}

// C2PA Text Manifest magic bytes: "C2PATXT\0"
const C2PA_MAGIC = [0x43, 0x32, 0x50, 0x41, 0x54, 0x58, 0x54, 0x00];

// Encypher magic bytes: "ENCYPHER"
const ENCYPHER_MAGIC = [0x45, 0x4E, 0x43, 0x59, 0x50, 0x48, 0x45, 0x52];

// Unicode variation selector ranges used for embedding
const VS_RANGES = {
  // FE00-FE0F: Variation Selectors (16 values, 4 bits each)
  VS1_START: 0xFE00,
  VS1_END: 0xFE0F,
  // E0100-E01EF: Variation Selectors Supplement (240 values)
  VS2_START: 0xE0100,
  VS2_END: 0xE01EF,
};

// Zero-width no-break space (prefix marker)
const ZWNBSP = 0xFEFF;

// Local browser cache: stores verification results keyed by text hash.
// Entries persist for CACHE_TTL_MS (1 hour) or until manual rescan / page reload.
// This prevents re-hitting the API when a user scrolls up and down a page.
const CACHE_TTL_MS = 60 * 60 * 1000; // 1 hour
const _verificationCache = new Map(); // hash → { result, details, timestamp }
const _floatingBadgeByElement = new WeakMap();
const _detectionIdByElement = new WeakMap();
let _detectionSequence = 0;

// Track which DOM elements already have badges to avoid duplicate processing.
// Uses Set (not WeakSet) so it can be cleared on RESCAN.
const _processedElements = new Set();

// Track processed images (by src URL) to avoid duplicate scanning/verification.
const _processedImages = new Set();
// Map image src -> { element, detectionId, status, details }
const _imageVerificationState = new Map();

// Track processed audio/video elements (by src URL) to avoid duplicates.
const _processedAudioVideo = new Set();
// Map media src -> { element, detectionId, status, details, mediaType }
const _audioVideoVerificationState = new Map();

// Track in-flight verifications by textHash → Promise<{status, details}>.
// When a DOM expansion (e.g. LinkedIn "see more") reveals a new element whose
// content is already being verified, the new element subscribes to the existing
// promise instead of starting a duplicate API call and getting a stuck pending badge.
const _verificationInFlight = new Map();

// Elements waiting for an in-flight verification result, keyed by textHash.
// When the in-flight promise resolves, all registered elements get their badge updated.
const _pendingElementsByHash = new Map();

// Pending badge DOM nodes keyed by textHash.
// When a verification for a given hash completes (possibly on a different element
// than the one that originally got the pending badge — e.g. LinkedIn truncated vs
// expanded element), we remove any orphaned pending badges for the same hash.
const _pendingBadgesByHash = new Map();

// Guard against extension context invalidation (e.g. after extension reload)
let _extensionContextValid = true;

function _isDisconnectedMessageError(err) {
  const message = String(err?.message || '');
  return (
    message.includes('Extension context invalidated') ||
    message.includes('Extension disconnected') ||
    message.includes('Receiving end does not exist') ||
    message.includes('Could not establish connection') ||
    message.includes('The message port closed before a response was received')
  );
}

function _isContextInvalidatedError(err) {
  return String(err?.message || '').includes('Extension context invalidated');
}

/**
 * Simple string hash for deduplication (not cryptographic)
 */
function _hashText(text) {
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    const char = text.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit int
  }
  return hash.toString(36);
}

function _getOrCreateDetectionId(element, textHash) {
  const existing = _detectionIdByElement.get(element);
  if (existing) return existing;

  _detectionSequence += 1;
  const id = `${textHash}-${_detectionSequence.toString(36)}`;
  _detectionIdByElement.set(element, id);
  try {
    element.dataset.encypherDetectionId = id;
  } catch {
    // Defensive: some hosts may block dataset writes on special nodes.
  }
  return id;
}

function _focusEmbeddingById(detectionId) {
  if (!detectionId) return false;
  const escaped = (typeof CSS !== 'undefined' && typeof CSS.escape === 'function')
    ? CSS.escape(detectionId)
    : String(detectionId).replace(/\\/g, '\\\\').replace(/"/g, '\\"');
  const target = document.querySelector(`[data-encypher-detection-id="${escaped}"]`);
  if (!target) return false;

  target.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' });
  const previousTransition = target.style.transition;
  const previousOutline = target.style.outline;
  const previousOutlineOffset = target.style.outlineOffset;
  target.style.transition = 'outline 0.2s ease';
  target.style.outline = '2px solid rgba(42, 135, 196, 0.85)';
  target.style.outlineOffset = '2px';
  setTimeout(() => {
    target.style.outline = previousOutline;
    target.style.outlineOffset = previousOutlineOffset;
    target.style.transition = previousTransition;
  }, 1800);
  return true;
}

/**
 * Safe wrapper around chrome.runtime.sendMessage.
 * Handles extension disconnect races and retries once when possible.
 */
async function _safeSendMessage(message) {
  if (!_extensionContextValid) return null;
  try {
    return await chrome.runtime.sendMessage(message);
  } catch (err) {
    if (!_isDisconnectedMessageError(err)) {
      return null;
    }

    if (_isContextInvalidatedError(err)) {
      _extensionContextValid = false;
      _debugLog('WARN', 'detector', 'Extension context invalidated — stopping messaging');
      return null;
    }

    // Service worker can be suspended/restarted; retry once before surfacing an error badge.
    try {
      await new Promise(resolve => setTimeout(resolve, 120));
      return await chrome.runtime.sendMessage(message);
    } catch (retryErr) {
      if (_isContextInvalidatedError(retryErr)) {
        _extensionContextValid = false;
      }
      return null;
    }
  }
}

/**
 * Get a cached verification result if it exists and hasn't expired.
 */
function _getCachedResult(textHash) {
  const entry = _verificationCache.get(textHash);
  if (!entry) return null;
  if (Date.now() - entry.timestamp > CACHE_TTL_MS) {
    _verificationCache.delete(textHash);
    return null;
  }
  return entry;
}

/**
 * Check if a character is a variation selector
 */
function isVariationSelector(codePoint) {
  return (
    (codePoint >= VS_RANGES.VS1_START && codePoint <= VS_RANGES.VS1_END) ||
    (codePoint >= VS_RANGES.VS2_START && codePoint <= VS_RANGES.VS2_END)
  );
}

// Legacy-safe (base-6 ZWC) char set: ZWNJ ZWJ CGJ MVS LRM RLM
// CGJ (0x034F) and MVS (0x180E) are the rarest of these in legitimate text;
// LRM (0x200E) / RLM (0x200F) are the discriminating chars vs base-4 ZW.
const LEGACY_SAFE_CHARS = new Set([0x200C, 0x200D, 0x034F, 0x180E, 0x200E, 0x200F]);

function _hasLegacySafeChars(text) {
  for (const char of text) {
    const cp = char.codePointAt(0);
    // CGJ, MVS, LRM, RLM are strong indicators — much rarer than ZWNJ/ZWJ in normal text
    if (cp === 0x034F || cp === 0x180E || cp === 0x200E || cp === 0x200F) {
      return true;
    }
  }
  return false;
}

/**
 * Extract embedded bytes from variation selectors in text.
 *
 * Uses the c2pa_text standard encoding where each VS maps to one byte:
 *   VS1 (FE00-FE0F) → bytes 0-15
 *   VS2 (E0100-E01EF) → bytes 16-255
 */
function extractEmbeddedBytes(text) {
  const bytes = [];

  for (const char of text) {
    const codePoint = char.codePointAt(0);

    if (codePoint >= VS_RANGES.VS1_START && codePoint <= VS_RANGES.VS1_END) {
      // Bytes 0-15 from VS1 range
      bytes.push(codePoint - VS_RANGES.VS1_START);
    } else if (codePoint >= VS_RANGES.VS2_START && codePoint <= VS_RANGES.VS2_END) {
      // Bytes 16-255 from VS2 range
      bytes.push((codePoint - VS_RANGES.VS2_START) + 16);
    }
  }

  return new Uint8Array(bytes);
}

/**
 * Check if bytes start with C2PA magic
 */
function hasC2PAMagic(bytes) {
  if (bytes.length < C2PA_MAGIC.length) return false;
  for (let i = 0; i < C2PA_MAGIC.length; i++) {
    if (bytes[i] !== C2PA_MAGIC[i]) return false;
  }
  return true;
}

/**
 * Check if bytes start with Encypher magic
 */
function hasEncypherMagic(bytes) {
  if (bytes.length < ENCYPHER_MAGIC.length) return false;
  for (let i = 0; i < ENCYPHER_MAGIC.length; i++) {
    if (bytes[i] !== ENCYPHER_MAGIC[i]) return false;
  }
  return true;
}

/**
 * Detect marker type from bytes
 * @returns {string|null} 'c2pa', 'encypher', or null if no valid marker
 */
function detectMarkerType(bytes) {
  if (hasC2PAMagic(bytes)) return 'c2pa';
  if (hasEncypherMagic(bytes)) return 'encypher';
  return null;
}

function _getStatusMetadata(status) {
  const normalized = String(status || 'unknown');
  const labels = {
    verified: 'Verified',
    invalid: 'Invalid Signature',
    revoked: 'Revoked',
    error: 'Error',
    pending: 'Verifying...'
  };
  const colors = {
    verified: '#00CED1',
    invalid: '#EF4444',
    revoked: '#A7AFBC',
    error: '#6B7280',
    pending: '#B7D5ED'
  };
  return {
    key: normalized,
    label: labels[normalized] || normalized,
    color: colors[normalized] || '#6B7280'
  };
}

function _markerTypeLabel(markerType, compact = false) {
  if (compact) {
    return markerType === 'c2pa' ? 'C2PA'
      : markerType === 'encypher' ? 'Encypher'
      : markerType === 'micro' ? 'Micro-Embedding'
      : '';
  }
  return markerType === 'c2pa' ? 'C2PA Text Manifest'
    : markerType === 'encypher' ? 'Encypher Format'
    : markerType === 'micro' ? 'Encypher Micro-Embedding'
    : 'Unknown';
}

function _buildC2paManifestDisclosure(details) {
  const manifest = details.c2paManifest;
  const assertions = details.c2paAssertions;
  const hasManifest = manifest && typeof manifest === 'object';
  const hasAssertions = Array.isArray(assertions) && assertions.length > 0;
  if (!hasManifest && !hasAssertions) {
    return '';
  }

  let payload = hasManifest ? manifest : { assertions };
  if (!hasManifest && hasAssertions && details.c2paValidated !== undefined) {
    payload = {
      validated: !!details.c2paValidated,
      validation_type: details.c2paValidationType || null,
      assertions
    };
  }

  const serialized = _escapeHtml(JSON.stringify(payload, null, 2));
  return `<div class="encypher-detail-panel__manifest">
    <details>
      <summary>View full C2PA manifest</summary>
      <pre>${serialized}</pre>
    </details>
  </div>`;
}

function _buildHoverTooltipHtml({ details, status }) {
  const statusMeta = _getStatusMetadata(status);
  const signingIdentity = _resolveSigningIdentity(details);
  const identityValue = signingIdentity ? _escapeHtml(signingIdentity) : 'Unknown signer';

  return `<span class="encypher-badge__tooltip" role="status" aria-live="polite">
    <div class="encypher-badge__tooltip-card">
      <div class="encypher-detail-panel__header">
        <span class="encypher-detail-panel__logo">${ENCYPHER_LOGO_SVG}</span>
        <span class="encypher-detail-panel__title">Encypher Verification</span>
      </div>
      <div class="encypher-badge__tooltip-body">
        <div class="encypher-badge__tooltip-row">
          <span class="encypher-badge__tooltip-label">Status</span>
          <span class="encypher-badge__tooltip-value" style="color:${statusMeta.color};font-weight:600">${_escapeHtml(statusMeta.label)}</span>
        </div>
        <div class="encypher-badge__tooltip-row">
          <span class="encypher-badge__tooltip-label">Signing Identity</span>
          <span class="encypher-badge__tooltip-value">${identityValue}</span>
        </div>
        <div class="encypher-badge__tooltip-hint">Click for more information</div>
      </div>
    </div>
  </span>`;
}

function _dedupeDetectionsByElement(detections) {
  const unique = [];
  const seen = new Set();
  for (const detection of detections || []) {
    const element = detection?.element;
    if (!element || seen.has(element)) {
      continue;
    }
    seen.add(element);
    unique.push(detection);
  }
  return unique;
}

/**
 * Extract wrapper bytes from a ZWNBSP-prefixed contiguous VS sequence.
 * C2PA wrappers are: ZWNBSP + contiguous variation selectors.
 * Returns array of { bytes, startIdx, endIdx } for each wrapper found.
 */
function findWrappers(text) {
  const wrappers = [];
  let i = 0;
  const chars = [...text]; // proper codepoint iteration

  while (i < chars.length) {
    if (chars[i].codePointAt(0) === ZWNBSP) {
      // Found ZWNBSP prefix, collect contiguous VS chars
      const startIdx = i;
      i++;
      const vsBytes = [];
      while (i < chars.length && isVariationSelector(chars[i].codePointAt(0))) {
        const cp = chars[i].codePointAt(0);
        if (cp >= VS_RANGES.VS1_START && cp <= VS_RANGES.VS1_END) {
          vsBytes.push(cp - VS_RANGES.VS1_START);
        } else if (cp >= VS_RANGES.VS2_START && cp <= VS_RANGES.VS2_END) {
          vsBytes.push((cp - VS_RANGES.VS2_START) + 16);
        }
        i++;
      }
      if (vsBytes.length >= C2PA_MAGIC.length) {
        wrappers.push({
          bytes: new Uint8Array(vsBytes),
          startIdx,
          endIdx: i
        });
      }
    } else {
      i++;
    }
  }
  return wrappers;
}

/**
 * Check if a text node contains any variation selectors or ZWNBSP (fast check)
 */
function _hasVariationSelectors(text) {
  for (const char of text) {
    const cp = char.codePointAt(0);
    if (isVariationSelector(cp) || cp === ZWNBSP) {
      return true;
    }
  }
  return false;
}

/**
 * Detect micro-embeddings: contiguous runs of VS chars (possibly interleaved
 * with visible base chars) that do NOT start with a ZWNBSP prefix and do NOT
 * match any known magic bytes. These are lightweight UUID/fingerprint embeddings.
 * Returns array of { byteCount, startIdx, endIdx } for each run found.
 */
function findMicroEmbeddings(text) {
  const results = [];
  const chars = [...text];
  let i = 0;

  while (i < chars.length) {
    const cp = chars[i].codePointAt(0);
    // Skip ZWNBSP-prefixed sequences (handled by findWrappers)
    if (cp === ZWNBSP) {
      i++;
      while (i < chars.length && isVariationSelector(chars[i].codePointAt(0))) i++;
      continue;
    }

    if (isVariationSelector(cp)) {
      // Found a VS char not preceded by ZWNBSP — start of a micro-embedding
      const startIdx = i;
      let vsCount = 0;
      while (i < chars.length) {
        const c = chars[i].codePointAt(0);
        if (isVariationSelector(c)) {
          vsCount++;
          i++;
        } else if (c === ZWNBSP) {
          break; // Don't merge into a wrapper sequence
        } else {
          // Visible char — peek ahead to see if more VS chars follow
          if (i + 1 < chars.length && isVariationSelector(chars[i + 1].codePointAt(0))) {
            i++; // skip the visible char, continue collecting
          } else {
            break;
          }
        }
      }
      // Minimum threshold: at least 4 VS chars to be considered a micro-embedding
      // (avoids false positives from legitimate font variation selectors)
      if (vsCount >= 4) {
        results.push({ byteCount: vsCount, startIdx, endIdx: i });
      }
    } else {
      i++;
    }
  }
  return results;
}

/**
 * Find all text nodes containing variation selectors within a root element
 */
function findNodesWithEmbeddings(root = document.body) {
  const walker = document.createTreeWalker(
    root,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: (node) => {
        // Skip script, style, and hidden elements
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;

        const tagName = parent.tagName.toLowerCase();
        if (['script', 'style', 'noscript', 'template'].includes(tagName)) {
          return NodeFilter.FILTER_REJECT;
        }

        // Check if text contains variation selectors or legacy-safe ZWC chars
        const text = node.textContent || '';
        if (_hasVariationSelectors(text) || _hasLegacySafeChars(text)) {
          return NodeFilter.FILTER_ACCEPT;
        }
        return NodeFilter.FILTER_REJECT;
      }
    }
  );

  const nodes = [];
  let node;
  while ((node = walker.nextNode())) {
    nodes.push(node);
  }
  return nodes;
}

/**
 * Extract the visible text (without variation selectors) from embedded content
 */
function extractVisibleText(text) {
  let result = '';
  for (const char of text) {
    const codePoint = char.codePointAt(0);
    if (!isVariationSelector(codePoint) && codePoint !== ZWNBSP) {
      result += char;
    }
  }
  return result;
}

/**
 * Find the containing block element for a text node
 */
function getContainingBlock(node) {
  let element = node.parentElement;
  while (element) {
    const display = window.getComputedStyle(element).display;
    if (display === 'block' || display === 'flex' || display === 'grid' ||
        element.tagName === 'P' || element.tagName === 'DIV' ||
        element.tagName === 'ARTICLE' || element.tagName === 'SECTION') {
      return element;
    }
    element = element.parentElement;
  }
  return node.parentElement;
}

/**
 * Encypher logo SVG for badge (checkmark icon)
 */
const ENCYPHER_LOGO_SVG = `<svg viewBox="0 0 264.58334 264.58333" xmlns="http://www.w3.org/2000/svg">
  <g transform="translate(141.02291,94.720831)">
    <path d="m 0,0 c 0,232.574 -188.539,421.113 -421.113,421.113 -232.574,0 -421.113,-188.539 -421.113,-421.113 0,-232.574 188.539,-421.113 421.113,-421.113 C -188.539,-421.113 0,-232.574 0,0 m -67.453,353 c 23.979,-23.981 10.797,-65.451 27.768,-92.817 18.974,-30.597 65.954,-33.172 79.076,-65.368 C 53.507,160.182 17.509,121.532 36.361,78.293 46.971,53.959 71.864,40.212 78.136,13.025 88.284,-30.962 46.909,-46.485 34.258,-81.182 c -15.204,-41.698 18.268,-74.005 5.128,-109.592 -10.999,-29.792 -41.748,-34.508 -64.249,-51.817 -35.197,-27.075 -17.661,-69.425 -38.048,-103.822 -23.241,-39.214 -88.417,-7.654 -119.92,-50.318 -15.57,-21.086 -19.66,-51.992 -47.602,-62.02 -37.141,-13.33 -73.918,26.168 -115.134,8.091 -25.387,-11.134 -41.467,-42.977 -71.635,-41.973 -40.694,1.354 -55.371,38.519 -90.549,46.161 -35.155,7.637 -70.921,-23.265 -105.134,-10.989 -29.976,10.755 -32.05,49.686 -54.486,68.033 -46.355,37.908 -104.624,-4.252 -121.466,74.566 -4.219,19.744 -3.26,41.357 -14.786,58.725 -18.598,28.025 -60.437,30.204 -75.202,61.504 -17.044,36.132 21.018,75.308 2.157,118.229 -9.922,22.582 -34.649,37.243 -40.879,61.005 -14.493,55.272 39.927,66.145 45.429,111.924 3.779,31.436 -14.077,58.522 -11.085,85.886 3.876,35.449 42.672,41.122 65.628,60.762 35.771,30.604 19.345,55.434 33.486,91.613 19.578,50.093 74.036,25.042 109.571,50.348 25.488,18.151 33.168,62.191 60.342,73.785 35.996,15.359 70.975,-19.554 106.446,-12.299 28.968,5.924 48.503,41.024 76.508,44.721 48.251,6.372 61.706,-38.856 102.102,-45.992 33.437,-5.906 59.88,20.108 92.391,16.301 38.545,-4.512 40.264,-55.377 66.904,-74.961 30.814,-22.653 78.673,-9.989 102.372,-33.689" style="fill:currentColor;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="matrix(0.26489337,0,0,-0.26868826,102.67706,37.461479)"/>
    <path d="m 0,0 c -83.528,-5.076 -162.357,-38.8 -224.157,-94.394 -158.015,-142.145 -166.457,-385.295 -21.94,-540.428 165.409,-177.56 446.282,-154.97 588.662,38.19 84.213,114.248 95.688,274.838 27.221,399.718 C 297.105,-64.347 150.152,9.124 0,0 M 5.205,23.285 C 143.817,30.151 272.03,-27.605 356.728,-136.46 456.427,-264.595 466.08,-451.411 376.376,-587.884 263.962,-758.908 71.908,-818.956 -121.656,-750.26 c -32.852,11.659 -77.116,41.147 -104.929,62.729 -96.585,74.95 -157.627,226.56 -144.421,347.923 6.569,60.365 23.33,122.486 56.048,173.515 71.625,111.712 185.876,182.726 320.163,189.378" style="fill:currentColor;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="matrix(0.26489337,0,0,-0.26868826,-17.287041,-63.64331)"/>
    <path d="m 0,0 c 29.751,29.632 61.152,66.947 92.627,93.729 8.727,7.426 13.408,10.728 25.56,6.146 16.328,-6.156 45.296,-50.829 60.057,-63.748 2.451,-4.138 2.004,-9.397 -0.391,-13.439 -87.041,-90.36 -177.441,-177.881 -267.071,-265.566 -20.595,-20.148 -44.143,-48.328 -65.711,-65.836 -10.684,-8.674 -16.474,-8.656 -27.14,0 l -193.453,193.451 c -5.327,5.857 -6.63,16.108 -1.906,22.6 21.521,18.741 40.871,44.559 62.52,62.579 10.895,9.068 18.62,9.015 29.722,-0.002 36.955,-34.62 71.913,-79.106 110.22,-111.604 3.871,-3.284 10.239,-8.849 15.195,-9.415 13.191,-1.507 37.453,29.815 46.694,39.13 C -75.711,-74.315 -37.573,-37.422 0,0" style="fill:currentColor;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="matrix(0.26489337,0,0,-0.26868826,26.73424,8.5562629)"/>
    <path d="m 0,0 c -0.216,0.126 -1.012,2.659 -2.026,3.71 -54.348,56.357 -145.316,79.861 -221.695,68.13 -72.555,-11.143 -128.881,-46.55 -174.916,-102.365 -117.608,-142.594 -43.035,-367.034 132.52,-416.806 113.594,-32.204 209.023,-4.247 287.25,82.155 53.615,59.218 77.446,146.726 59.953,225.052 0.463,2.527 14.054,16.355 15.468,14.84 16.044,-65.162 5.842,-132.859 -21.313,-193.404 -36.108,-80.507 -143.607,-155.591 -232.049,-160.015 -159.635,-7.985 -288.716,89.134 -312.403,248.714 -17.045,114.837 39.58,227.12 138.491,285.019 91.096,53.324 197.675,49.923 288.862,-0.821 C -34.567,50.151 15.294,16.303 15.289,12.073 12.155,9.902 3.731,-2.182 0,0" style="fill:currentColor;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="matrix(0.26489337,0,0,-0.26868826,39.878672,-14.24062)"/>
  </g>
</svg>`;
globalThis.ENCYPHER_LOGO_SVG = ENCYPHER_LOGO_SVG;

/**
 * Escape HTML to prevent XSS in badge detail panel
 */
function _escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function _isOpaqueIdentity(value) {
  if (!value) return false;
  return /^(org_|usr_|user_)[a-z0-9-]+$/i.test(String(value).trim());
}

function _buildIdentityFromId(idValue) {
  if (!idValue) return null;
  const raw = String(idValue).trim();
  if (!raw) return null;
  const compact = raw.replace(/^(org_|usr_|user_)/i, '');
  const suffix = compact.length > 12 ? `${compact.slice(0, 12)}...` : compact;
  return `Organization ${suffix}`;
}

function _resolveSigningIdentity(details) {
  const explicitIdentity = String(details.signingIdentity || '').trim();
  if (explicitIdentity && !_isOpaqueIdentity(explicitIdentity)) return explicitIdentity;

  const signerName = String(details.signer || '').trim();
  if (signerName && !_isOpaqueIdentity(signerName)) return signerName;

  const orgName = String(details.organizationName || '').trim();
  if (orgName && !_isOpaqueIdentity(orgName)) return orgName;

  return _buildIdentityFromId(details.organizationId || details.signerId);
}

function _safeExternalUrl(value) {
  if (!value) return null;
  try {
    const parsed = new URL(String(value));
    if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
      return parsed.toString();
    }
  } catch {
    return null;
  }
  return null;
}

function _isEditableSurface(element) {
  if (!element || element.nodeType !== Node.ELEMENT_NODE) return false;
  if (element.isContentEditable) return true;
  if (element.closest?.('[contenteditable="true"], textarea, input')) return true;
  if (element.closest?.('.ql-editor, .ck-editor__editable, .cke_editable, .mce-content-body, .tox-edit-area, .CodeMirror, .cm-editor, .ace_editor, .kix-appview-editor, .kix-page-content-wrapper, [data-content-type="RichText"], .WACViewPanel_EditingElement')) return true;
  return false;
}

/**
 * Returns true when this content script is running inside an iframe whose
 * body IS the email/document content (e.g. Zoho Mail compose frame).
 * In these frames, appending anything to document.body would pollute the email.
 */
function _isEditableBodyFrame() {
  return window !== window.top && document.body?.contentEditable === 'true';
}

/**
 * Returns the document.body to use for floating badge / panel mounts.
 * For editable-body iframes we mount on the parent frame body so badges
 * never touch the email content. Returns null for cross-origin parents.
 */
function _getBadgeMountRoot() {
  if (_isEditableBodyFrame()) {
    try { return window.parent.document.body; } catch (e) { /* cross-origin */ }
    return null;
  }
  return document.body;
}

/**
 * Returns the iframe's bounding-rect offset within the parent viewport,
 * used to convert element positions from the iframe coordinate space to
 * the parent-frame coordinate space when mounting badges on the parent body.
 */
function _getIframeOffset() {
  if (!_isEditableBodyFrame()) return { x: 0, y: 0 };
  try {
    const rect = window.frameElement?.getBoundingClientRect();
    return rect ? { x: rect.left, y: rect.top } : { x: 0, y: 0 };
  } catch (e) { return { x: 0, y: 0 }; }
}

function _positionFloatingBadge(badge, anchor) {
  const rect = anchor.getBoundingClientRect();
  const { x: iframeX, y: iframeY } = _getIframeOffset();
  const badgeWidth = 30;
  const vpWin = _isEditableBodyFrame() ? (() => { try { return window.parent; } catch(e) { return window; } })() : window;
  const viewportWidth = vpWin.innerWidth || document.documentElement.clientWidth || 0;
  const scrollX = _isEditableBodyFrame() ? (vpWin.scrollX || 0) : window.scrollX;
  const scrollY = _isEditableBodyFrame() ? (vpWin.scrollY || 0) : window.scrollY;
  const top = Math.max(scrollY + rect.top + iframeY - 10, scrollY + 8);
  let left = scrollX + rect.right + iframeX + 6;

  if (left + badgeWidth > scrollX + viewportWidth - 8) {
    left = Math.max(scrollX + rect.left + iframeX - badgeWidth - 6, scrollX + 8);
  }

  badge.style.position = 'absolute';
  badge.style.top = `${top}px`;
  badge.style.left = `${left}px`;
  badge.style.zIndex = '2147483000';
}

/**
 * Close any open detail panels (searches both current frame and parent frame)
 */
function _closeDetailPanels() {
  const roots = [document];
  try { if (_isEditableBodyFrame()) roots.push(window.parent.document); } catch (e) {}
  for (const d of roots) {
    d.querySelectorAll('.encypher-detail-panel').forEach(p => p.remove());
    d.querySelectorAll('.encypher-badge--panel-open').forEach(b => b.classList.remove('encypher-badge--panel-open'));
  }
}

/**
 * Show a rich detail panel anchored to a badge element
 */
function _showDetailPanel(badge, details) {
  // Close any existing panels first
  _closeDetailPanels();

  // Suppress hover tooltip while panel is open
  badge.classList.add('encypher-badge--panel-open');

  const panel = document.createElement('div');
  panel.className = 'encypher-detail-panel';

  const statusMeta = _getStatusMetadata(details._status || 'unknown');
  const markerLabel = _markerTypeLabel(details.markerType);

  let rows = '';

  // Status row
  rows += `<div class="encypher-detail-panel__row">
    <span class="encypher-detail-panel__label">Status</span>
    <span class="encypher-detail-panel__value" style="color:${statusMeta.color};font-weight:600">${_escapeHtml(statusMeta.label)}</span>
  </div>`;

  // Format
  rows += `<div class="encypher-detail-panel__row">
    <span class="encypher-detail-panel__label">Format</span>
    <span class="encypher-detail-panel__value">${_escapeHtml(markerLabel)}</span>
  </div>`;

  // Signing identity (prefer explicit signer identity, avoid raw opaque IDs in UI)
  const signingIdentity = _resolveSigningIdentity(details);
  if (signingIdentity) {
    rows += `<div class="encypher-detail-panel__row">
      <span class="encypher-detail-panel__label">Signing Identity</span>
      <span class="encypher-detail-panel__value">${_escapeHtml(signingIdentity)}</span>
    </div>`;
  }

  // Signer — only show if it's a human-readable name (not an ID like org_xxx or usr_xxx)
  const signerDisplay = details.signer;
  const signerIsId = signerDisplay && /^(org_|usr_|user_)[a-z0-9-]+$/i.test(signerDisplay);
  if (signerDisplay && !signerIsId) {
    rows += `<div class="encypher-detail-panel__row">
      <span class="encypher-detail-panel__label">Signed by</span>
      <span class="encypher-detail-panel__value">${_escapeHtml(signerDisplay)}</span>
    </div>`;
  }

  // Timestamp
  if (details.timestamp) {
    const date = new Date(details.timestamp);
    const formatted = isNaN(date.getTime()) ? details.timestamp : date.toLocaleString();
    rows += `<div class="encypher-detail-panel__row">
      <span class="encypher-detail-panel__label">Signed at</span>
      <span class="encypher-detail-panel__value">${_escapeHtml(formatted)}</span>
    </div>`;
  }

  // Document ID
  if (details.documentId) {
    rows += `<div class="encypher-detail-panel__row">
      <span class="encypher-detail-panel__label">Document</span>
      <span class="encypher-detail-panel__value encypher-detail-panel__mono">${_escapeHtml(details.documentId)}</span>
    </div>`;
  }

  // Verification URL
  const verificationUrl = _safeExternalUrl(details.verificationUrl);
  if (verificationUrl) {
    rows += `<div class="encypher-detail-panel__row">
      <span class="encypher-detail-panel__label">Verification</span>
      <span class="encypher-detail-panel__value"><a href="${_escapeHtml(verificationUrl)}" target="_blank" rel="noopener">Open verification record</a></span>
    </div>`;
  }

  // Document title
  if (details.title) {
    rows += `<div class="encypher-detail-panel__row">
      <span class="encypher-detail-panel__label">Title</span>
      <span class="encypher-detail-panel__value">${_escapeHtml(details.title)}</span>
    </div>`;
  }

  // Document type
  if (details.documentType) {
    rows += `<div class="encypher-detail-panel__row">
      <span class="encypher-detail-panel__label">Type</span>
      <span class="encypher-detail-panel__value">${_escapeHtml(details.documentType)}</span>
    </div>`;
  }

  // C2PA validation
  if (details.c2paValidated !== undefined) {
    let c2paSource = 'no';
    if (details.c2paValidated) {
      c2paSource = details.c2paValidationType === 'db_backed_manifest'
        ? 'external manifest'
        : 'embedded manifest';
    }
    rows += `<div class="encypher-detail-panel__row">
      <span class="encypher-detail-panel__label">C2PA Validated</span>
      <span class="encypher-detail-panel__value">${details.c2paValidated ? 'Yes' : 'No'} (${_escapeHtml(c2paSource)})</span>
    </div>`;
  }
  rows += _buildC2paManifestDisclosure(details);

  // License
  if (details.licenseType) {
    rows += `<div class="encypher-detail-panel__row">
      <span class="encypher-detail-panel__label">License</span>
      <span class="encypher-detail-panel__value">${_escapeHtml(details.licenseType)}</span>
    </div>`;
  }

  // Error
  if (details.error) {
    rows += `<div class="encypher-detail-panel__row">
      <span class="encypher-detail-panel__label">Error</span>
      <span class="encypher-detail-panel__value" style="color:#EF4444">${_escapeHtml(details.error)}</span>
    </div>`;
  }

  // Revoked at
  if (details.revokedAt) {
    const date = new Date(details.revokedAt);
    const formatted = isNaN(date.getTime()) ? details.revokedAt : date.toLocaleString();
    rows += `<div class="encypher-detail-panel__row">
      <span class="encypher-detail-panel__label">Revoked at</span>
      <span class="encypher-detail-panel__value" style="color:#8B5CF6">${_escapeHtml(formatted)}</span>
    </div>`;
  }

  panel.innerHTML = `
    <div class="encypher-detail-panel__header">
      <span class="encypher-detail-panel__logo">${ENCYPHER_LOGO_SVG}</span>
      <span class="encypher-detail-panel__title">Encypher Verification</span>
      <button class="encypher-detail-panel__close" aria-label="Close">&times;</button>
    </div>
    <div class="encypher-detail-panel__body">${rows}</div>
    <div class="encypher-detail-panel__footer">
      <a href="https://encypher.com" target="_blank" rel="noopener">encypher.com</a>
    </div>
  `;

  // Close button handler
  panel.querySelector('.encypher-detail-panel__close').addEventListener('click', (e) => {
    e.stopPropagation();
    panel.remove();
    badge.classList.remove('encypher-badge--panel-open');
  });

  // Mount on the safe root (parent frame body for editable-body iframes)
  const mountRoot = _getBadgeMountRoot();
  if (!mountRoot) return; // cross-origin editable-body frame; can't mount safely
  const mountDoc = mountRoot.ownerDocument || document;
  const mountWin = mountDoc.defaultView || window;

  // Close on outside click — listen on the document that owns the panel
  const closeOnOutsideClick = (e) => {
    if (!panel.contains(e.target) && !badge.contains(e.target)) {
      panel.remove();
      badge.classList.remove('encypher-badge--panel-open');
      mountDoc.removeEventListener('click', closeOnOutsideClick, true);
    }
  };
  setTimeout(() => mountDoc.addEventListener('click', closeOnOutsideClick, true), 0);

  // Position relative to badge, accounting for iframe offset
  mountRoot.appendChild(panel);
  const { x: iframeX, y: iframeY } = _getIframeOffset();
  const badgeRect = badge.getBoundingClientRect();
  const panelRect = panel.getBoundingClientRect();

  let top = badgeRect.bottom + iframeY + mountWin.scrollY + 8;
  let left = badgeRect.right + iframeX + mountWin.scrollX - panelRect.width;

  // Keep panel within viewport
  if (left < 8) left = 8;
  if (left + panelRect.width > mountWin.innerWidth - 8) {
    left = mountWin.innerWidth - panelRect.width - 8;
  }
  if (top + panelRect.height > mountWin.innerHeight + mountWin.scrollY - 8) {
    top = badgeRect.top + iframeY + mountWin.scrollY - panelRect.height - 8;
  }

  panel.style.top = `${top}px`;
  panel.style.left = `${left}px`;
}

/**
 * Create and inject a verification badge with Encypher logo
 */
function injectBadge(element, status, details) {
  const editableSurface = _isEditableSurface(element);

  // Remove existing badge so status updates (pending → verified) work
  const existingInlineBadge = element.querySelector('.encypher-badge');
  const existingFloatingBadge = _floatingBadgeByElement.get(element);
  const existingBadge = editableSurface ? existingFloatingBadge : existingInlineBadge;
  if (existingBadge) {
    // If the new status is 'pending' and a non-pending badge already exists, keep it
    if (status === 'pending' && !existingBadge.classList.contains('encypher-badge--pending')) {
      return;
    }
    existingBadge.remove();
    if (editableSurface) {
      _floatingBadgeByElement.delete(element);
    }
  }

  const badge = document.createElement('div');
  badge.className = `encypher-badge encypher-badge--${status}`;
  badge.setAttribute('role', 'button');
  badge.setAttribute('aria-label', `Encypher verified content: ${status}`);
  badge.setAttribute('tabindex', '0');

  // Use Encypher logo for verified, status indicators for others
  const statusOverlay = {
    verified: '',
    pending: '<span class="encypher-badge__status">&#x22EF;</span>',
    invalid: '<span class="encypher-badge__status">&#x2717;</span>',
    revoked: '<span class="encypher-badge__status">&#x2298;</span>',
    error: '<span class="encypher-badge__status">!</span>'
  };

  badge.innerHTML = `
    <span class="encypher-badge__icon">${ENCYPHER_LOGO_SVG}</span>
    ${statusOverlay[status] || ''}
    ${_buildHoverTooltipHtml({ details, status })}
  `;

  // Store full details on the badge for the click handler
  const fullDetails = { ...details, _status: status };

  // Click handler to show rich detail panel
  badge.addEventListener('click', (e) => {
    e.stopPropagation();
    e.preventDefault();
    _showDetailPanel(badge, fullDetails);
  });

  // Keyboard accessibility
  badge.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      _showDetailPanel(badge, fullDetails);
    }
  });

  // In an editable-body iframe (e.g. Zoho Mail compose), document.body IS the
  // email content, so we must never append badges there. Use the parent-frame
  // body for all badge mounts; if the parent is cross-origin, skip entirely.
  const mountRoot = _getBadgeMountRoot();

  if (editableSurface || _isEditableBodyFrame()) {
    if (!mountRoot) return; // cross-origin; can't mount safely
    _positionFloatingBadge(badge, element);
    badge.dataset.encypherFloating = 'true';
    mountRoot.appendChild(badge);
    _floatingBadgeByElement.set(element, badge);
    return;
  }

  // Append badge inline at the end of the element for non-editable content.
  element.appendChild(badge);
  element.classList.add('encypher-verified-content');
}

/**
 * Detect embeddings in text nodes within a root element.
 * Checks for:
 *   1. C2PA wrappers (ZWNBSP + VS sequence with magic bytes)
 *   2. Legacy Encypher format (scattered VS with magic bytes)
 *   3. Micro-embeddings (contiguous VS runs without magic bytes — UUID/fingerprint)
 *
 * Returns { uncached, cached } where cached detections already have results
 * from the local browser cache and don't need an API call.
 */
function _detectEmbeddings(root = document.body) {
  const nodes = findNodesWithEmbeddings(root);
  const uncached = [];
  const cached = [];
  const queuedElements = new Set();

  for (const node of nodes) {
    const text = node.textContent || '';
    const containingBlock = getContainingBlock(node);

    // Skip if this element already has a badge (already processed)
    if (_processedElements.has(containingBlock) || queuedElements.has(containingBlock)) {
      continue;
    }

    // Compute a hash for deduplication and cache lookup
    const textHash = _hashText(text);

    // Check local browser cache first (1-hour TTL)
    const cachedEntry = _getCachedResult(textHash);
    if (cachedEntry) {
      cached.push({
        element: containingBlock,
        detectionId: _getOrCreateDetectionId(containingBlock, textHash),
        textHash,
        cachedStatus: cachedEntry.status,
        cachedDetails: cachedEntry.details
      });
      queuedElements.add(containingBlock);
      continue;
    }

    let found = false;

    // 1. Find ZWNBSP-prefixed wrapper sequences (standard C2PA text wrapper format)
    const wrappers = findWrappers(text);
    for (const wrapper of wrappers) {
      const markerType = detectMarkerType(wrapper.bytes);
      if (markerType) {
        const visibleText = extractVisibleText(text);
        uncached.push({
          element: containingBlock, node, text, textHash, visibleText,
          detectionId: _getOrCreateDetectionId(containingBlock, textHash),
          bytes: Array.from(wrapper.bytes), markerType
        });
        queuedElements.add(containingBlock);
        found = true;
        break; // Only take the first valid wrapper per text node
      }
    }

    // 2. Fallback: non-wrapper VS embeddings (legacy Encypher format)
    if (!found && wrappers.length === 0) {
      const bytes = extractEmbeddedBytes(text);
      const markerType = detectMarkerType(bytes);
      if (markerType) {
        if (markerType === 'c2pa' && wrappers.length === 0) {
          _debugLog('DEBUG', 'detector', 'Skipping non-wrapper C2PA fallback candidate', {
            textHash,
            byteLength: bytes.length
          });
          continue;
        }
        const visibleText = extractVisibleText(text);
        uncached.push({
          element: containingBlock, node, text, textHash, visibleText,
          detectionId: _getOrCreateDetectionId(containingBlock, textHash),
          bytes: Array.from(bytes), markerType
        });
        queuedElements.add(containingBlock);
        found = true;
      }
    }

    // 3. Micro-embeddings: contiguous VS runs without magic bytes (UUID/fingerprint)
    if (!found) {
      const micros = findMicroEmbeddings(text);
      if (micros.length > 0) {
        const visibleText = extractVisibleText(text);
        // Extract the raw bytes for the largest micro-embedding
        const largest = micros.reduce((a, b) => a.byteCount > b.byteCount ? a : b);
        const bytes = extractEmbeddedBytes(text);
        uncached.push({
          element: containingBlock, node, text, textHash, visibleText,
          detectionId: _getOrCreateDetectionId(containingBlock, textHash),
          bytes: Array.from(bytes),
          markerType: 'micro',
          microCount: micros.length,
          microBytes: largest.byteCount
        });
        queuedElements.add(containingBlock);
        found = true;
      }
    }

    // 4. Legacy-safe (base-6 ZWC) embeddings: CGJ/MVS/LRM/RLM chars present.
    // No client-side marker parsing needed — send full text to the API.
    if (!found && _hasLegacySafeChars(text)) {
      const visibleText = extractVisibleText(text);
      uncached.push({
        element: containingBlock, node, text, textHash, visibleText,
        detectionId: _getOrCreateDetectionId(containingBlock, textHash),
        bytes: [],
        markerType: 'legacy_safe',
      });
      queuedElements.add(containingBlock);
    }
  }

  return { uncached, cached };
}

/**
 * Build badge details from an API response for a detection.
 */
function _buildBadgeDetails(response, markerType) {
  if (response && response.success) {
    const signerName = response.data?.signer_name || null;
    const orgName = response.data?.organization_name || null;
    const signerDisplay = (signerName && !_isOpaqueIdentity(signerName))
      ? signerName
      : ((orgName && !_isOpaqueIdentity(orgName)) ? orgName : null);
    return {
      status: 'verified',
      details: {
        signingIdentity: response.data?.signing_identity || response.data?.publisher_display_name || null,
        signer: signerDisplay,
        signerId: response.data?.signer_id,
        organizationName: response.data?.organization_name,
        organizationId: response.data?.organization_id,
        timestamp: response.data?.signed_at,
        documentId: response.data?.document_id,
        verificationUrl: response.data?.verification_url,
        originalDomain: response.data?.original_domain || response.data?.signing_domain || null,
        signingDomain: response.data?.signing_domain || response.data?.original_domain || null,
        title: response.data?.title,
        documentType: response.data?.document_type,
        c2paValidated: response.data?.c2pa_validated,
        c2paValidationType: response.data?.c2pa_validation_type,
        c2paManifest: response.data?.c2pa_manifest,
        c2paAssertions: response.data?.c2pa_assertions,
        licenseType: response.data?.license_type,
        markerType,
      }
    };
  } else if (response && response.revoked) {
    const signerName = response.data?.signer_name || null;
    const orgName = response.data?.organization_name || null;
    const signerDisplay = (signerName && !_isOpaqueIdentity(signerName))
      ? signerName
      : ((orgName && !_isOpaqueIdentity(orgName)) ? orgName : null);
    return {
      status: 'revoked',
      details: {
        error: 'This content has been revoked',
        revokedAt: response.data?.revoked_at || response.revoked_at,
        signingIdentity: response.data?.signing_identity || response.data?.publisher_display_name || null,
        signer: signerDisplay,
        signerId: response.data?.signer_id,
        organizationName: response.data?.organization_name,
        organizationId: response.data?.organization_id,
        c2paManifest: response.data?.c2pa_manifest,
        c2paAssertions: response.data?.c2pa_assertions,
        verificationUrl: response.data?.verification_url,
        originalDomain: response.data?.original_domain || response.data?.signing_domain || null,
        signingDomain: response.data?.signing_domain || response.data?.original_domain || null,
        markerType
      }
    };
  } else {
    return {
      status: 'invalid',
      details: {
        error: response?.error || 'Verification failed',
        markerType
      }
    };
  }
}

/**
 * Remove pending badges that are inside elements no longer visible to the user.
 * LinkedIn (and similar SPAs) hide the truncated element when "see more" is clicked
 * but keep it in the DOM, leaving its pending badge stuck. This sweep removes any
 * pending badge whose closest ancestor is hidden (display:none / visibility:hidden /
 * aria-hidden) or whose containing element is no longer connected.
 */
function _sweepOrphanedPendingBadges() {
  const pendingBadges = document.querySelectorAll('.encypher-badge--pending');
  for (const badge of pendingBadges) {
    if (!badge.isConnected) {
      badge.remove();
      continue;
    }
    // Walk ancestors to check for hidden containers
    let el = badge.parentElement;
    let hidden = false;
    while (el && el !== document.body) {
      const style = window.getComputedStyle(el);
      if (
        style.display === 'none' ||
        style.visibility === 'hidden' ||
        el.getAttribute('aria-hidden') === 'true'
      ) {
        hidden = true;
        break;
      }
      el = el.parentElement;
    }
    if (hidden) {
      badge.remove();
    }
  }
}

/**
 * Apply a completed verification result to all elements waiting on a given textHash.
 * Called after the primary verification resolves to update any DOM-expanded siblings.
 */
function _resolveWaitingElements(textHash, status, details) {
  const waiting = _pendingElementsByHash.get(textHash);
  if (!waiting) return;
  _pendingElementsByHash.delete(textHash);
  for (const el of waiting) {
    if (el.isConnected) {
      injectBadge(el, status, { ...details });
    }
  }
}

/**
 * Verify a list of detections against the API and inject badges.
 * Uses _safeSendMessage to handle extension context invalidation.
 * Stores results in the local browser cache (1-hour TTL).
 *
 * In-flight deduplication: if a verification for the same textHash is already
 * running (e.g. a LinkedIn "see more" expansion revealed a new element while the
 * truncated version was still being verified), the new element subscribes to the
 * existing promise instead of starting a duplicate API call. This prevents the
 * stuck "Verifying..." pending badge that would otherwise never resolve.
 */
async function _verifyDetections(detections) {
  if (detections.length === 0) return;

  for (const detection of detections) {
    // Mark as processed immediately to prevent duplicate work
    _processedElements.add(detection.element);

    // If a verification for this exact hash is already in-flight (e.g. the page
    // expanded a truncated section while we were verifying the truncated version),
    // subscribe this element to the existing promise and skip a new API call.
    if (_verificationInFlight.has(detection.textHash)) {
      injectBadge(detection.element, 'pending', {
        message: 'Verifying...',
        markerType: detection.markerType
      });
      const existing = _pendingElementsByHash.get(detection.textHash) || new Set();
      existing.add(detection.element);
      _pendingElementsByHash.set(detection.textHash, existing);
      _debugLog('DEBUG', 'detector', `Subscribed element to in-flight verification (hash=${detection.textHash})`);
      continue;
    }

    // Show pending badge
    const markerLabel = detection.markerType === 'micro' ? 'micro-embedding' : detection.markerType;
    _debugLog('INFO', 'detector', `Verifying ${markerLabel} (${detection.bytes.length} bytes)`);
    injectBadge(detection.element, 'pending', {
      message: 'Verifying...',
      markerType: detection.markerType
    });
    // Track the pending badge so we can remove it if verification completes on a
    // different element (e.g. LinkedIn expands the section after the pending badge
    // was injected on the truncated element).
    {
      const pendingBadge = detection.element.querySelector('.encypher-badge--pending');
      if (pendingBadge) {
        const existing = _pendingBadgesByHash.get(detection.textHash) || new Set();
        existing.add(pendingBadge);
        _pendingBadgesByHash.set(detection.textHash, existing);
      }
    }

    // Build the verification promise and register it as in-flight
    const verifyPromise = (async () => {
      try {
        const response = await Promise.race([
          _safeSendMessage({
            type: 'VERIFY_CONTENT',
            detectionId: detection.detectionId,
            text: detection.text,
            visibleText: detection.visibleText,
            markerType: detection.markerType,
            pageUrl: window.location.href,
            pageDomain: window.location.hostname,
            pageTitle: document.title,
            discoverySource: 'page_scan',
            embeddingCount: 1,
            visibleTextLength: detection.visibleText?.length || 0,
            embeddingByteLength: detection.bytes?.length || 0,
          }),
          new Promise((resolve) => setTimeout(() => resolve(null), 15000)),
        ]);

        if (!response) {
          const errDetails = { error: 'Extension disconnected', markerType: detection.markerType };
          injectBadge(detection.element, 'error', errDetails);
          return { status: 'error', details: errDetails };
        }

        const { status, details } = _buildBadgeDetails(response, detection.markerType);
        details.detectionId = detection.detectionId;
        details.visibleTextLength = detection.visibleText?.length || 0;
        details.embeddingByteLength = detection.bytes?.length || 0;

        // Store in local browser cache
        _verificationCache.set(detection.textHash, {
          status,
          details,
          timestamp: Date.now()
        });

        injectBadge(detection.element, status, details);
        return { status, details };
      } catch (error) {
        const errDetails = { error: error.message || 'Verification error', markerType: detection.markerType };
        injectBadge(detection.element, 'error', errDetails);
        return { status: 'error', details: errDetails };
      }
    })();

    _verificationInFlight.set(detection.textHash, verifyPromise);

    const result = await verifyPromise;

    _verificationInFlight.delete(detection.textHash);

    // Remove any orphaned pending badges for this hash (e.g. the truncated element
    // that LinkedIn hid when the user clicked "see more" — its pending badge would
    // otherwise remain stuck since verification completed on the expanded element).
    const orphanedPending = _pendingBadgesByHash.get(detection.textHash);
    if (orphanedPending) {
      for (const orphan of orphanedPending) {
        if (orphan.isConnected && orphan.classList.contains('encypher-badge--pending')) {
          orphan.remove();
        }
      }
      _pendingBadgesByHash.delete(detection.textHash);
    }

    // Sweep any remaining pending badges that are inside hidden/invisible ancestors.
    // This catches the cross-hash case: LinkedIn truncated element has a different
    // textHash than the expanded element, so hash-based cleanup above won't find it,
    // but the truncated element is now display:none so the sweep removes it.
    _sweepOrphanedPendingBadges();

    _resolveWaitingElements(detection.textHash, result.status, result.details);
  }
}

// ---------------------------------------------------------------------------
// Image scanning and verification (Phase 1 -- on-demand)
// ---------------------------------------------------------------------------

const MIN_IMAGE_DIMENSION = 50;
const AUTO_SCAN_MAX_IMAGES = 20;
const AUTO_SCAN_MAX_CONCURRENT = 3;
const AUTO_SCAN_BANDWIDTH_LIMIT = 10 * 1024 * 1024; // 10MB per page
const AUTO_SCAN_COOLDOWN_MS = 5 * 60 * 1000; // 5 minutes

let _autoScanBytesUsed = 0;
let _autoScanEnabled = true;
let _autoScanCheckedCount = 0;
let _autoScanPageCooldown = new Map(); // url -> timestamp

// Load auto-scan setting from storage
try {
  chrome.storage.sync.get({ autoScanImages: true }, (result) => {
    _autoScanEnabled = result.autoScanImages !== false;
  });
} catch { /* storage may not be available in tests */ }

/**
 * Scan a DOM subtree for images, build an inventory, and trigger
 * automatic C2PA header checks for newly discovered images.
 * Returns the count of newly discovered images.
 */
function _scanImages(root) {
  const imgs = (root || document.body).querySelectorAll('img');
  let newCount = 0;
  for (const img of imgs) {
    const src = img.src || img.currentSrc;
    if (!src) continue;
    // Skip tiny images (icons, spacers), data URIs, and extension-injected images
    if (src.startsWith('data:') || src.startsWith('blob:')) continue;
    if (img.closest('.encypher-badge, .encypher-detail-panel')) continue;
    if ((img.naturalWidth || img.width) > 0 && (img.naturalWidth || img.width) < MIN_IMAGE_DIMENSION) continue;
    if ((img.naturalHeight || img.height) > 0 && (img.naturalHeight || img.height) < MIN_IMAGE_DIMENSION) continue;
    if (_processedImages.has(src)) continue;

    _processedImages.add(src);
    newCount++;
  }

  // Trigger auto-scan after inventory is updated
  if (_autoScanEnabled && newCount > 0) {
    _autoScanImages();
  }

  return newCount;
}

/**
 * Inject a floating verification badge over an image element.
 * Images are void elements so the badge is appended to a wrapper.
 */
function injectImageBadge(imgElement, status, details) {
  const src = imgElement.src || imgElement.currentSrc;
  if (!src) return;

  // Remove existing badge for this image
  const existingWrapper = imgElement.closest('.encypher-image-badge-wrapper');
  if (existingWrapper) {
    const existing = existingWrapper.querySelector('.encypher-badge');
    if (existing) {
      if (status === 'pending' && !existing.classList.contains('encypher-badge--pending')) return;
      existing.remove();
    }
  }

  const badge = document.createElement('div');
  badge.className = `encypher-badge encypher-badge--${status} encypher-badge--media`;
  badge.setAttribute('role', 'button');
  badge.setAttribute('aria-label', `Encypher image verification: ${status}`);
  badge.setAttribute('tabindex', '0');
  badge.dataset.encypherMediaSrc = src;

  const statusOverlay = {
    verified: '',
    pending: '<span class="encypher-badge__status">&#x22EF;</span>',
    invalid: '<span class="encypher-badge__status">&#x2717;</span>',
    revoked: '<span class="encypher-badge__status">&#x2298;</span>',
    error: '<span class="encypher-badge__status">!</span>'
  };

  badge.innerHTML = `
    <span class="encypher-badge__icon">${ENCYPHER_LOGO_SVG}</span>
    ${statusOverlay[status] || ''}
  `;

  const fullDetails = { ...details, _status: status };

  badge.addEventListener('click', (e) => {
    e.stopPropagation();
    e.preventDefault();
    _showDetailPanel(badge, fullDetails);
  });
  badge.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      _showDetailPanel(badge, fullDetails);
    }
  });

  // Wrap the image if not already wrapped
  let wrapper = imgElement.closest('.encypher-image-badge-wrapper');
  if (!wrapper) {
    wrapper = document.createElement('span');
    wrapper.className = 'encypher-image-badge-wrapper';
    // Preserve the image's display flow
    const computedDisplay = window.getComputedStyle(imgElement).display;
    wrapper.style.display = (computedDisplay === 'block') ? 'block' : 'inline-block';
    wrapper.style.position = 'relative';
    imgElement.parentNode.insertBefore(wrapper, imgElement);
    wrapper.appendChild(imgElement);
  }

  wrapper.appendChild(badge);

  // Update tracking
  _imageVerificationState.set(src, {
    element: imgElement,
    detectionId: details?.detectionId || null,
    status,
    details: fullDetails,
  });
}

/**
 * Verify an image by URL via the service worker and inject a badge.
 */
async function _verifyImageAndBadge(imgElement, srcUrl) {
  const detectionId = `img-${++_detectionSequence}`;

  injectImageBadge(imgElement, 'pending', { detectionId });

  try {
    const result = await chrome.runtime.sendMessage({
      type: 'VERIFY_MEDIA',
      url: srcUrl,
      detectionId,
      pageUrl: window.location.href,
    });

    const status = result?.success ? 'verified' : (result?.error ? 'error' : 'invalid');
    const details = {
      detectionId,
      valid: result?.success || false,
      signer: null,
      date: result?.data?.verified_at || null,
      overall_status: result?.data?.overall_status || null,
      c2pa_manifest: result?.data?.c2pa_manifest || null,
      cryptographically_verified: result?.data?.cryptographically_verified || false,
      hash: result?.data?.hash || null,
      document_id: result?.data?.document_id || null,
      error: result?.error || null,
    };

    injectImageBadge(imgElement, status, details);
  } catch (error) {
    injectImageBadge(imgElement, 'error', { detectionId, error: error?.message || 'Verification failed' });
  }
}

/**
 * Check if an image URL likely contains a C2PA JUMBF manifest.
 * Delegates to the service worker which can do cross-origin Range requests.
 * Returns true if C2PA indicators are found.
 */
async function _checkC2paHeader(imageUrl) {
  try {
    const response = await chrome.runtime.sendMessage({
      type: 'CHECK_C2PA_HEADER',
      url: imageUrl,
    });
    _autoScanBytesUsed += 4096; // Approximate Range request cost
    return response?.hasC2pa === true;
  } catch {
    return false;
  }
}

/**
 * Run the auto-scan pipeline on inventoried images.
 * Uses lightweight Range requests to detect C2PA headers, then auto-verifies
 * images that likely have manifests.
 */
async function _autoScanImages() {
  if (!_autoScanEnabled) return;

  // Cooldown: don't rescan same page within 5 minutes
  const pageUrl = window.location.href;
  const lastScan = _autoScanPageCooldown.get(pageUrl);
  if (lastScan && Date.now() - lastScan < AUTO_SCAN_COOLDOWN_MS) return;
  _autoScanPageCooldown.set(pageUrl, Date.now());

  // Load setting
  try {
    const settings = await chrome.storage.sync.get({ autoScanImages: true });
    if (!settings.autoScanImages) return;
  } catch { return; }

  // Collect unverified images up to the limit
  const candidates = [];
  for (const src of _processedImages) {
    if (_imageVerificationState.has(src)) continue; // Already verified
    if (candidates.length >= AUTO_SCAN_MAX_IMAGES) break;
    candidates.push(src);
  }

  if (candidates.length === 0) return;

  _debugLog('INFO', 'detector', `Auto-scan: checking ${candidates.length} images for C2PA headers`);

  // Process in batches with concurrency limit
  let active = 0;
  const queue = [...candidates];

  const processNext = async () => {
    while (queue.length > 0 && active < AUTO_SCAN_MAX_CONCURRENT) {
      // Circuit breaker: stop if bandwidth limit exceeded
      if (_autoScanBytesUsed > AUTO_SCAN_BANDWIDTH_LIMIT) {
        _debugLog('WARN', 'detector', `Auto-scan: bandwidth limit reached (${_autoScanBytesUsed} bytes), stopping`);
        return;
      }

      const src = queue.shift();
      if (!src || _imageVerificationState.has(src)) continue;

      active++;

      try {
        const hasC2pa = await _checkC2paHeader(src);
        if (hasC2pa) {
          _debugLog('INFO', 'detector', `Auto-scan: C2PA header detected in ${src.slice(0, 80)}`);
          const img = document.querySelector(`img[src="${CSS.escape(src)}"]`);
          if (img) {
            _verifyImageAndBadge(img, src);
          }
        }
      } catch {
        // Skip failed header checks
      } finally {
        active--;
      }
    }
  };

  // Use requestIdleCallback to avoid blocking rendering
  const runBatch = () => {
    if (queue.length === 0) return;
    if (typeof requestIdleCallback === 'function') {
      requestIdleCallback(() => {
        processNext().then(() => {
          if (queue.length > 0) runBatch();
        });
      });
    } else {
      setTimeout(() => {
        processNext().then(() => {
          if (queue.length > 0) runBatch();
        });
      }, 100);
    }
  };

  runBatch();
}

/**
 * Scan a DOM subtree for audio and video elements and build an inventory.
 * Does NOT auto-verify -- elements are verified on-demand via context menu or popup.
 * Returns the count of newly discovered audio/video elements.
 */
function _scanAudioVideo(root) {
  const elements = (root || document.body).querySelectorAll('audio, video');
  let newCount = 0;
  for (const el of elements) {
    // Get source URL from src attribute or first <source> child
    let src = el.src || el.currentSrc;
    if (!src) {
      const sourceChild = el.querySelector('source');
      if (sourceChild) src = sourceChild.src;
    }
    if (!src) continue;
    if (src.startsWith('data:') || src.startsWith('blob:')) continue;
    if (el.closest('.encypher-badge, .encypher-detail-panel')) continue;
    if (_processedAudioVideo.has(src)) continue;

    _processedAudioVideo.add(src);
    newCount++;
  }
  return newCount;
}

/**
 * Inject a floating verification badge over an audio or video element.
 * For video: overlay at top-right corner (same as image).
 * For audio: inline badge next to audio controls.
 */
function injectMediaBadge(mediaElement, status, details) {
  const src = mediaElement.src || mediaElement.currentSrc || (() => {
    const s = mediaElement.querySelector('source');
    return s ? s.src : '';
  })();
  if (!src) return;

  const mediaType = mediaElement.tagName.toLowerCase(); // 'audio' or 'video'

  // Remove existing badge for this element
  const existingWrapper = mediaElement.closest('.encypher-media-badge-wrapper');
  if (existingWrapper) {
    const existing = existingWrapper.querySelector('.encypher-badge');
    if (existing) {
      if (status === 'pending' && !existing.classList.contains('encypher-badge--pending')) return;
      existing.remove();
    }
  }

  const badge = document.createElement('div');
  badge.className = `encypher-badge encypher-badge--${status} encypher-badge--media`;
  badge.setAttribute('role', 'button');
  badge.setAttribute('aria-label', `Encypher ${mediaType} verification: ${status}`);
  badge.setAttribute('tabindex', '0');
  badge.dataset.encypherMediaSrc = src;

  const statusOverlay = {
    verified: '',
    pending: '<span class="encypher-badge__status">&#x22EF;</span>',
    invalid: '<span class="encypher-badge__status">&#x2717;</span>',
    revoked: '<span class="encypher-badge__status">&#x2298;</span>',
    error: '<span class="encypher-badge__status">!</span>'
  };

  badge.innerHTML = `
    <span class="encypher-badge__icon">${ENCYPHER_LOGO_SVG}</span>
    ${statusOverlay[status] || ''}
  `;

  const fullDetails = { ...details, _status: status, mediaType };

  badge.addEventListener('click', (e) => {
    e.stopPropagation();
    e.preventDefault();
    _showDetailPanel(badge, fullDetails);
  });
  badge.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      _showDetailPanel(badge, fullDetails);
    }
  });

  // Wrap the element
  let wrapper = mediaElement.closest('.encypher-media-badge-wrapper');
  if (!wrapper) {
    wrapper = document.createElement('div');
    wrapper.className = 'encypher-media-badge-wrapper';
    wrapper.style.position = 'relative';
    const computedDisplay = window.getComputedStyle(mediaElement).display;
    wrapper.style.display = (computedDisplay === 'inline') ? 'inline-block' : computedDisplay;
    mediaElement.parentNode.insertBefore(wrapper, mediaElement);
    wrapper.appendChild(mediaElement);
  }

  wrapper.appendChild(badge);

  // Update tracking
  _audioVideoVerificationState.set(src, {
    element: mediaElement,
    detectionId: details?.detectionId || null,
    status,
    details: fullDetails,
    mediaType,
  });
}

/**
 * Verify an audio/video element by URL via the service worker and inject a badge.
 */
async function _verifyMediaAndBadge(mediaElement, srcUrl, mediaType) {
  const detectionId = `${mediaType}-${++_detectionSequence}`;

  injectMediaBadge(mediaElement, 'pending', { detectionId });

  try {
    const result = await chrome.runtime.sendMessage({
      type: 'VERIFY_MEDIA',
      mediaType,
      url: srcUrl,
      detectionId,
      pageUrl: window.location.href,
    });

    const status = result?.success ? 'verified' : (result?.error ? 'error' : 'invalid');
    const details = {
      detectionId,
      valid: result?.success || false,
      signer: result?.data?.signer || null,
      date: result?.data?.verified_at || null,
      c2pa_manifest_valid: result?.data?.c2pa_manifest_valid || false,
      c2pa_instance_id: result?.data?.c2pa_instance_id || null,
      manifest_data: result?.data?.manifest_data || null,
      error: result?.error || null,
    };

    injectMediaBadge(mediaElement, status, details);
  } catch (error) {
    injectMediaBadge(mediaElement, 'error', { detectionId, error: error?.message || 'Verification failed' });
  }
}

/**
 * Scan the page (or a subtree) for C2PA embeddings and verify them.
 * Uses local browser cache to avoid re-hitting the API for already-verified content.
 * Only hits the API when valid magic bytes are found locally and no cache entry exists.
 */
async function scanPage(root = document.body) {
  _debugLog('INFO', 'detector', `Scanning ${root === document.body ? 'page' : 'subtree'}: ${window.location.href}`);

  let { uncached, cached } = _detectEmbeddings(root);

  // On Google Docs / MS Word Online, also scan platform-specific content layers
  // that may not be reachable from a normal body TreeWalker.
  if (root === document.body) {
    const extraRoots = _getOnlineEditorRoots();
    for (const extraRoot of extraRoots) {
      const extra = _detectEmbeddings(extraRoot);
      uncached = uncached.concat(extra.uncached);
      cached = cached.concat(extra.cached);
    }
  }

  uncached = _dedupeDetectionsByElement(uncached);
  cached = _dedupeDetectionsByElement(cached);
  const uncachedElements = new Set(uncached.map(entry => entry.element));
  cached = cached.filter(entry => !uncachedElements.has(entry.element));

  // Apply cached results immediately (no API call needed)
  for (const entry of cached) {
    _processedElements.add(entry.element);
    const cachedDetails = { ...(entry.cachedDetails || {}), detectionId: entry.detectionId };
    injectBadge(entry.element, entry.cachedStatus, cachedDetails);
    _safeSendMessage({
      type: 'REPORT_CACHED_DETECTION',
      detectionId: entry.detectionId,
      status: entry.cachedStatus,
      details: cachedDetails,
      markerType: cachedDetails.markerType,
      pageUrl: window.location.href,
      pageDomain: window.location.hostname,
      pageTitle: document.title,
      discoverySource: 'cached_detection',
      embeddingCount: 1,
      visibleTextLength: cachedDetails.visibleTextLength,
      embeddingByteLength: cachedDetails.embeddingByteLength,
    });
    _debugLog('DEBUG', 'detector', `Cache hit: ${entry.cachedStatus} (hash=${entry.textHash})`);
  }

  const totalFound = uncached.length + cached.length;
  _debugLog('INFO', 'detector', `Scan complete: ${totalFound} embeddings (${cached.length} cached, ${uncached.length} new)`);

  if (totalFound > 0) {
    _safeSendMessage({
      type: 'EMBEDDINGS_DETECTED',
      count: totalFound,
      pending: uncached.length,
      url: window.location.href,
    });
  }

  if (uncached.length > 0) {
    await _verifyDetections(uncached);
  } else if (totalFound === 0 && root === document.body && _verificationCache.size === 0) {
    // Only send NO_EMBEDDINGS on initial full-page scan with zero results
    _debugLog('DEBUG', 'detector', 'No embeddings found on page');
    _safeSendMessage({
      type: 'NO_EMBEDDINGS',
      url: window.location.href
    });
  }

  // Scan images (inventory + auto-scan for C2PA headers)
  const newImages = _scanImages(root);
  if (newImages > 0) {
    _debugLog('INFO', 'detector', `Image scan: ${newImages} new images inventoried (${_processedImages.size} total)`);
    // Trigger auto-scan after inventory (non-blocking)
    _autoScanImages();
  }

  // Scan audio/video elements (inventory only -- on-demand verification)
  const newAudioVideo = _scanAudioVideo(root);
  if (newAudioVideo > 0) {
    _debugLog('INFO', 'detector', `Audio/video scan: ${newAudioVideo} new elements inventoried (${_processedAudioVideo.size} total)`);
  }

  return totalFound;
}

/**
 * Return additional DOM roots to scan for online editor platforms.
 * Google Docs renders text in an accessibility layer that may be in a
 * separate subtree from the main body content.
 */
function _getOnlineEditorRoots() {
  const roots = [];
  const hostname = window.location.hostname;
  const pathname = window.location.pathname;

  // Google Docs: accessibility / screen-reader text layer
  if (hostname === 'docs.google.com' && pathname.startsWith('/document/')) {
    // The .kix-appview-editor contains the accessibility text spans
    const kixEditor = document.querySelector('.kix-appview-editor');
    if (kixEditor) roots.push(kixEditor);
    // Also try individual page content wrappers
    document.querySelectorAll('.kix-page-content-wrapper').forEach(el => {
      if (!kixEditor || !kixEditor.contains(el)) roots.push(el);
    });
  }

  // MS Word Online: contenteditable surface
  if (hostname === 'word.live.com' || hostname.endsWith('.officeapps.live.com') ||
      (hostname.endsWith('.sharepoint.com') && pathname.includes('/_layouts/15/Doc.aspx'))) {
    const surface = document.querySelector('[data-content-type="RichText"][contenteditable="true"]') ||
                    document.querySelector('.WACViewPanel_EditingElement') ||
                    document.querySelector('#WACViewPanel [contenteditable="true"]');
    if (surface) roots.push(surface);
  }

  return roots;
}

/**
 * Observe DOM changes for dynamically loaded content (infinite scroll, lazy load).
 * Only scans newly added subtrees, not the full page.
 */
function observeDOM() {
  let pendingNodes = [];
  let debounceTimer = null;
  let pendingInputRoots = [];
  let inputDebounceTimer = null;

  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === 'childList') {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            pendingNodes.push(node);
          }
        }
      } else if (mutation.type === 'characterData') {
        // In-place edits in contenteditable/WYSIWYG often update text nodes
        // without adding/removing elements.
        const parent = mutation.target?.parentElement;
        if (parent) {
          pendingNodes.push(parent);
        }
      }
    }

    if (pendingNodes.length > 0) {
      // Debounce: wait for mutations to settle (handles rapid infinite-scroll loads)
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const nodesToScan = pendingNodes;
        pendingNodes = [];

        // Scan only the newly added subtrees
        for (const node of nodesToScan) {
          if (node.isConnected) {
            scanPage(node);
          }
        }
      }, 500);
    }
  });

  observer.observe(document.body, {
    childList: true,
    characterData: true,
    subtree: true
  });

  // Input-driven edits (e.g. WYSIWYG typing) don't always produce childList
  // mutations in a way that gives us useful roots. Listen for input events and
  // rescan the active editable subtree.
  document.addEventListener('input', (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;

    const editableRoot = target.closest(
      '[contenteditable="true"], textarea, input, .ql-editor, .ck-editor__editable, .cke_editable, .mce-content-body, .tox-edit-area, .CodeMirror, .cm-editor, .ace_editor, .kix-appview-editor, .kix-page-content-wrapper, [data-content-type="RichText"], .WACViewPanel_EditingElement'
    ) || target;

    pendingInputRoots.push(editableRoot);
    clearTimeout(inputDebounceTimer);
    inputDebounceTimer = setTimeout(() => {
      const roots = pendingInputRoots;
      pendingInputRoots = [];
      for (const root of roots) {
        if (root?.isConnected) {
          scanPage(root);
        }
      }
    }, 450);
  }, true);
}

// Initialize after page load without blocking rendering.
// requestIdleCallback defers scanning until the browser is idle.
function _initDetector() {
  const startScan = () => {
    scanPage();
    observeDOM();
  };
  // Use requestIdleCallback if available (defers to idle time, doesn't block paint)
  if (typeof requestIdleCallback === 'function') {
    requestIdleCallback(startScan, { timeout: 2000 });
  } else {
    setTimeout(startScan, 100);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', _initDetector);
} else {
  _initDetector();
}

// Listen for messages from popup or service worker
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'RESCAN') {
    // Force rescan: clear all dedup state so everything is re-checked
    _verificationCache.clear();
    _processedElements.clear();
    _processedImages.clear();
    _imageVerificationState.clear();
    _processedAudioVideo.clear();
    _audioVideoVerificationState.clear();
    _autoScanBytesUsed = 0;
    _autoScanCheckedCount = 0;
    _autoScanPageCooldown.clear();
    document.querySelectorAll('.encypher-badge').forEach(b => b.remove());
    document.querySelectorAll('.encypher-image-badge-wrapper').forEach(wrapper => {
      // Unwrap: move image back out, remove wrapper
      const img = wrapper.querySelector('img');
      if (img && wrapper.parentNode) {
        wrapper.parentNode.insertBefore(img, wrapper);
        wrapper.remove();
      }
    });
    document.querySelectorAll('.encypher-media-badge-wrapper').forEach(wrapper => {
      const media = wrapper.querySelector('audio, video');
      if (media && wrapper.parentNode) {
        wrapper.parentNode.insertBefore(media, wrapper);
        wrapper.remove();
      }
    });
    document.querySelectorAll('.encypher-verified-content').forEach(el => {
      el.classList.remove('encypher-verified-content');
    });
    scanPage().then(count => {
      sendResponse({ count });
    });
    return true; // async response
  }

  if (message.type === 'VERIFY_SELECTION') {
    // Verify selected text via context menu
    verifySelectedText(message.text, {
      pageUrl: message.pageUrl,
      pageTitle: message.pageTitle,
      markerType: message.markerType || 'selection'
    });
    sendResponse({ received: true });
  }

  if (message.type === 'FOCUS_EMBEDDING') {
    const found = _focusEmbeddingById(message.detectionId);
    sendResponse({ found });
  }

  // Image verification triggered by context menu
  if (message.type === 'VERIFY_IMAGE_CONTEXT') {
    const srcUrl = message.srcUrl;
    if (srcUrl) {
      const img = document.querySelector(`img[src="${CSS.escape(srcUrl)}"]`);
      if (img) {
        _verifyImageAndBadge(img, srcUrl);
      }
    }
    sendResponse({ received: true });
  }

  // Audio verification triggered by context menu
  if (message.type === 'VERIFY_AUDIO_CONTEXT') {
    const srcUrl = message.srcUrl;
    if (srcUrl) {
      const el = document.querySelector(`audio[src="${CSS.escape(srcUrl)}"], audio source[src="${CSS.escape(srcUrl)}"]`);
      const audioEl = el?.tagName === 'SOURCE' ? el.closest('audio') : el;
      if (audioEl) {
        _verifyMediaAndBadge(audioEl, srcUrl, 'audio');
      }
    }
    sendResponse({ received: true });
  }

  // Video verification triggered by context menu
  if (message.type === 'VERIFY_VIDEO_CONTEXT') {
    const srcUrl = message.srcUrl;
    if (srcUrl) {
      const el = document.querySelector(`video[src="${CSS.escape(srcUrl)}"], video source[src="${CSS.escape(srcUrl)}"]`);
      const videoEl = el?.tagName === 'SOURCE' ? el.closest('video') : el;
      if (videoEl) {
        _verifyMediaAndBadge(videoEl, srcUrl, 'video');
      }
    }
    sendResponse({ received: true });
  }

  // Focus on a verified media element (from popup "Locate on page")
  if (message.type === 'FOCUS_MEDIA') {
    const entry = _imageVerificationState.get(message.mediaUrl) || _audioVideoVerificationState.get(message.mediaUrl);
    if (entry?.element?.isConnected) {
      entry.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      const origOutline = entry.element.style.outline;
      entry.element.style.outline = '3px solid rgba(42, 135, 196, 0.85)';
      setTimeout(() => { entry.element.style.outline = origOutline; }, 2000);
      sendResponse({ found: true });
    } else {
      sendResponse({ found: false });
    }
  }

  // Return image inventory for popup
  if (message.type === 'GET_PAGE_IMAGES') {
    const images = [];
    for (const [src, state] of _imageVerificationState.entries()) {
      images.push({
        src,
        detectionId: state.detectionId,
        status: state.status,
        details: state.details,
      });
    }
    // Also include unverified inventoried images
    for (const src of _processedImages) {
      if (!_imageVerificationState.has(src)) {
        images.push({ src, detectionId: null, status: null, details: null });
      }
    }
    sendResponse({ images, total: _processedImages.size });
  }

  // Return audio/video inventory for popup
  if (message.type === 'GET_PAGE_MEDIA') {
    const media = [];
    for (const [src, state] of _audioVideoVerificationState.entries()) {
      media.push({
        src,
        mediaType: state.mediaType,
        detectionId: state.detectionId,
        status: state.status,
        details: state.details,
      });
    }
    for (const src of _processedAudioVideo) {
      if (!_audioVideoVerificationState.has(src)) {
        // Determine type from the element
        const el = document.querySelector(`audio[src="${CSS.escape(src)}"], video[src="${CSS.escape(src)}"], source[src="${CSS.escape(src)}"]`);
        const tag = el?.tagName === 'SOURCE' ? el.closest('audio, video')?.tagName : el?.tagName;
        media.push({ src, mediaType: (tag || 'video').toLowerCase(), detectionId: null, status: null, details: null });
      }
    }
    sendResponse({ media, total: _processedAudioVideo.size });
  }
});

/**
 * Verify text selected via context menu
 */
async function verifySelectedText(text, context = {}) {
  try {
    const response = await _safeSendMessage({
      type: 'VERIFY_CONTENT',
      text: text,
      visibleText: text,
      markerType: context.markerType || 'selection',
      pageUrl: context.pageUrl || window.location.href,
      pageDomain: window.location.hostname,
      pageTitle: context.pageTitle || document.title,
      discoverySource: 'selection_verify',
      embeddingCount: 1,
      visibleTextLength: text?.length || 0,
      embeddingByteLength: null,
    });

    if (!response) {
      showVerificationNotification('error', {
        error: 'Extension disconnected. Reload page and try again.'
      });
      return;
    }

    if (response && response.success) {
      showVerificationNotification('verified', {
        signer: response.data?.signer_name || response.data?.signer_id,
        organizationName: response.data?.organization_name,
        timestamp: response.data?.signed_at
      });
    } else if (response && response.revoked) {
      showVerificationNotification('revoked', {
        error: 'This content has been revoked'
      });
    } else {
      showVerificationNotification('invalid', {
        error: response?.error || 'Verification failed'
      });
    }
  } catch (error) {
    showVerificationNotification('error', {
      error: error.message || 'Verification error'
    });
  }
}

/**
 * Show a temporary notification for verification result
 */
function showVerificationNotification(status, details) {
  const notification = document.createElement('div');
  notification.className = `encypher-notification encypher-notification--${status}`;
  notification.setAttribute('role', 'alert');

  const icons = {
    verified: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    invalid: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    revoked: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>',
    error: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'
  };

  const messages = {
    verified: 'Verified Content',
    invalid: 'Invalid Signature',
    revoked: 'Content Revoked',
    error: 'Verification Error'
  };

  notification.innerHTML = `
    <div class="encypher-notification__icon">${icons[status] || '?'}</div>
    <div class="encypher-notification__content">
      <strong>${messages[status]}</strong>
      ${details.signer ? `<br>Signed by: ${_escapeHtml(details.signer)}` : ''}
      ${details.organizationName ? `<br>Org: ${_escapeHtml(details.organizationName)}` : ''}
      ${details.error ? `<br>${_escapeHtml(details.error)}` : ''}
    </div>
  `;

  document.body.appendChild(notification);

  // Auto-remove after 5 seconds
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 5000);
}
