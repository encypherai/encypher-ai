/**
 * Encypher C2PA Content Detector
 * 
 * Scans the page for C2PA and Encypher text embeddings using Unicode variation selectors.
 * When found, injects verification badges and communicates with the service worker.
 * 
 * Supports two marker types:
 * - C2PA Text Manifest: "C2PATXT\0" (standard C2PA format)
 * - Encypher Marker: "ENCYPHER" (Encypher-specific format)
 */

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

/**
 * Check if a character is a variation selector
 */
function isVariationSelector(codePoint) {
  return (
    (codePoint >= VS_RANGES.VS1_START && codePoint <= VS_RANGES.VS1_END) ||
    (codePoint >= VS_RANGES.VS2_START && codePoint <= VS_RANGES.VS2_END)
  );
}

/**
 * Extract embedded bytes from variation selectors in text
 */
function extractEmbeddedBytes(text) {
  const bytes = [];
  let highNibble = null;
  
  for (const char of text) {
    const codePoint = char.codePointAt(0);
    
    if (codePoint >= VS_RANGES.VS1_START && codePoint <= VS_RANGES.VS1_END) {
      // 4-bit value from VS1 range
      const nibble = codePoint - VS_RANGES.VS1_START;
      if (highNibble === null) {
        highNibble = nibble;
      } else {
        bytes.push((highNibble << 4) | nibble);
        highNibble = null;
      }
    } else if (codePoint >= VS_RANGES.VS2_START && codePoint <= VS_RANGES.VS2_END) {
      // 8-bit value from VS2 range
      bytes.push(codePoint - VS_RANGES.VS2_START);
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

/**
 * Find all text nodes containing variation selectors
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
        
        // Check if text contains variation selectors
        const text = node.textContent || '';
        for (const char of text) {
          if (isVariationSelector(char.codePointAt(0))) {
            return NodeFilter.FILTER_ACCEPT;
          }
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

/**
 * Create and inject a verification badge with Encypher logo
 */
function injectBadge(element, status, details) {
  // Check if badge already exists
  if (element.querySelector('.encypher-badge')) return;
  
  const badge = document.createElement('div');
  badge.className = `encypher-badge encypher-badge--${status}`;
  badge.setAttribute('role', 'button');
  badge.setAttribute('aria-label', `Encypher verified content: ${status}`);
  badge.setAttribute('tabindex', '0');
  
  // Use Encypher logo for verified, status indicators for others
  const statusOverlay = {
    verified: '',
    pending: '<span class="encypher-badge__status">⋯</span>',
    invalid: '<span class="encypher-badge__status">✗</span>',
    revoked: '<span class="encypher-badge__status">⊘</span>',
    error: '<span class="encypher-badge__status">!</span>'
  };
  
  // Format marker type for display
  const markerLabel = details.markerType === 'c2pa' ? 'C2PA' : 
                      details.markerType === 'encypher' ? 'Encypher' : '';
  
  badge.innerHTML = `
    <span class="encypher-badge__icon">${ENCYPHER_LOGO_SVG}</span>
    ${statusOverlay[status] || ''}
    <span class="encypher-badge__tooltip">
      <strong>${status === 'verified' ? 'Verified by Encypher' : status.charAt(0).toUpperCase() + status.slice(1)}</strong>
      ${markerLabel ? `<br>Format: ${markerLabel}` : ''}
      ${details.signer ? `<br>Signed by: ${details.signer}` : ''}
      ${details.organizationId ? `<br>Org ID: ${details.organizationId}` : ''}
      ${details.timestamp ? `<br>Date: ${new Date(details.timestamp).toLocaleDateString()}` : ''}
      ${details.documentId ? `<br>Doc: ${details.documentId}` : ''}
      ${details.error ? `<br>Error: ${details.error}` : ''}
    </span>
  `;
  
  // Click handler to show full details
  badge.addEventListener('click', (e) => {
    e.stopPropagation();
    chrome.runtime.sendMessage({
      type: 'SHOW_DETAILS',
      details: details
    });
  });
  
  // Position the badge
  const computedStyle = window.getComputedStyle(element);
  if (computedStyle.position === 'static') {
    element.style.position = 'relative';
  }
  
  element.appendChild(badge);
  element.classList.add('encypher-verified-content');
}

/**
 * Scan the page for C2PA embeddings
 */
async function scanPage() {
  const nodes = findNodesWithEmbeddings();
  const detections = [];
  
  for (const node of nodes) {
    const text = node.textContent || '';
    const bytes = extractEmbeddedBytes(text);
    
    const markerType = detectMarkerType(bytes);
    if (markerType) {
      const containingBlock = getContainingBlock(node);
      const visibleText = extractVisibleText(text);
      
      detections.push({
        element: containingBlock,
        node: node,
        text: text,
        visibleText: visibleText,
        bytes: Array.from(bytes),
        markerType: markerType
      });
      
      // Show pending badge immediately with marker type
      injectBadge(containingBlock, 'pending', { 
        message: 'Verifying...',
        markerType: markerType
      });
    }
  }
  
  // Notify service worker about detections
  if (detections.length > 0) {
    chrome.runtime.sendMessage({
      type: 'EMBEDDINGS_DETECTED',
      count: detections.length,
      url: window.location.href
    });
    
    // Request verification for each detection
    for (let i = 0; i < detections.length; i++) {
      const detection = detections[i];
      try {
        const response = await chrome.runtime.sendMessage({
          type: 'VERIFY_CONTENT',
          index: i,
          text: detection.text,
          visibleText: detection.visibleText,
          markerType: detection.markerType,
          pageUrl: window.location.href,
          pageTitle: document.title
        });
        
        if (response && response.success) {
          injectBadge(detection.element, 'verified', {
            signer: response.data?.signer_name || response.data?.signer_id,
            timestamp: response.data?.signed_at,
            documentId: response.data?.document_id
          });
        } else if (response && response.revoked) {
          injectBadge(detection.element, 'revoked', {
            error: 'This content has been revoked',
            revokedAt: response.revoked_at
          });
        } else {
          injectBadge(detection.element, 'invalid', {
            error: response?.error || 'Verification failed'
          });
        }
      } catch (error) {
        injectBadge(detection.element, 'error', {
          error: error.message || 'Verification error'
        });
      }
    }
  } else {
    // No embeddings found
    chrome.runtime.sendMessage({
      type: 'NO_EMBEDDINGS',
      url: window.location.href
    });
  }
  
  return detections.length;
}

/**
 * Observe DOM changes for dynamically loaded content
 */
function observeDOM() {
  const observer = new MutationObserver((mutations) => {
    let shouldRescan = false;
    
    for (const mutation of mutations) {
      if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            shouldRescan = true;
            break;
          }
        }
      }
      if (shouldRescan) break;
    }
    
    if (shouldRescan) {
      // Debounce rescans
      clearTimeout(observeDOM.timeout);
      observeDOM.timeout = setTimeout(() => {
        scanPage();
      }, 500);
    }
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}

// Initialize on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    scanPage();
    observeDOM();
  });
} else {
  scanPage();
  observeDOM();
}

// Listen for messages from popup or service worker
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'RESCAN') {
    scanPage().then(count => {
      sendResponse({ count });
    });
    return true; // async response
  }
  
  if (message.type === 'VERIFY_SELECTION') {
    // Verify selected text via context menu
    verifySelectedText(message.text);
    sendResponse({ received: true });
  }
});

/**
 * Verify text selected via context menu
 */
async function verifySelectedText(text) {
  try {
    const response = await chrome.runtime.sendMessage({
      type: 'VERIFY_CONTENT',
      text: text,
      visibleText: text
    });
    
    // Show notification with result
    if (response && response.success) {
      showVerificationNotification('verified', {
        signer: response.data?.signer_name || response.data?.signer_id,
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
    verified: '✓',
    invalid: '✗',
    revoked: '⊘',
    error: '!'
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
      ${details.signer ? `<br>Signed by: ${details.signer}` : ''}
      ${details.error ? `<br>${details.error}` : ''}
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
