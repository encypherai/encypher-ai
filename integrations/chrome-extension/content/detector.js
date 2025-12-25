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
 * Create and inject a verification badge
 */
function injectBadge(element, status, details) {
  // Check if badge already exists
  if (element.querySelector('.encypher-badge')) return;
  
  const badge = document.createElement('div');
  badge.className = `encypher-badge encypher-badge--${status}`;
  badge.setAttribute('role', 'button');
  badge.setAttribute('aria-label', `Encypher verified content: ${status}`);
  badge.setAttribute('tabindex', '0');
  
  // Badge icon based on status
  const icons = {
    verified: '✓',
    pending: '⋯',
    invalid: '✗',
    revoked: '⊘',
    error: '!'
  };
  
  // Format marker type for display
  const markerLabel = details.markerType === 'c2pa' ? 'C2PA' : 
                      details.markerType === 'encypher' ? 'Encypher' : '';
  
  badge.innerHTML = `
    <span class="encypher-badge__icon">${icons[status] || '?'}</span>
    <span class="encypher-badge__tooltip">
      <strong>${status === 'verified' ? 'Verified Content' : status.charAt(0).toUpperCase() + status.slice(1)}</strong>
      ${markerLabel ? `<br>Format: ${markerLabel}` : ''}
      ${details.signer ? `<br>Signed by: ${details.signer}` : ''}
      ${details.timestamp ? `<br>Date: ${new Date(details.timestamp).toLocaleDateString()}` : ''}
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
          visibleText: detection.visibleText
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
});
