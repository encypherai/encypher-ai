/**
 * Fragment extraction module.
 *
 * Ported from ghost-provenance/src/html-utils.ts extractFragments().
 * Walks HTML at the byte level, tracking tag boundaries, and returns
 * text runs between tags with their byte offsets.
 *
 * Uses TextEncoder/TextDecoder instead of Node.js Buffer for
 * Cloudflare Workers compatibility.
 */

const encoder = new TextEncoder();
const decoder = new TextDecoder();

/**
 * Elements whose content is never visible text.
 */
const SKIP_TAGS = new Set([
  'script', 'style', 'noscript', 'svg', 'math', 'code', 'pre',
  'video', 'audio', 'canvas', 'iframe', 'object', 'embed',
  'source', 'track', 'picture', 'template', 'img', 'input',
  'select', 'textarea', 'button', 'map', 'area', 'link',
  'meta', 'base', 'head', 'title',
]);

/**
 * Self-closing HTML elements.
 */
const VOID_TAGS = new Set([
  'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
  'link', 'meta', 'param', 'source', 'track', 'wbr',
]);

/**
 * Block-level elements that introduce paragraph boundaries.
 */
export const BLOCK_TAGS = new Set([
  'address', 'article', 'aside', 'blockquote', 'dd', 'details',
  'dialog', 'div', 'dl', 'dt', 'fieldset', 'figcaption', 'figure',
  'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header',
  'hgroup', 'hr', 'li', 'main', 'nav', 'ol', 'p', 'pre', 'section',
  'summary', 'table', 'ul', 'tr', 'td', 'th', 'thead', 'tbody',
  'tfoot', 'br',
]);

/**
 * @typedef {Object} TextFragment
 * @property {number} byteOffset - Byte offset within the input HTML
 * @property {number} byteLength - Byte length of the raw text
 * @property {string} rawText - The raw text content (may contain entities)
 */

/**
 * Extract text fragments from HTML with byte offsets.
 *
 * @param {string} html - HTML string to extract from
 * @returns {TextFragment[]}
 */
export function extractFragments(html) {
  const buf = encoder.encode(html);
  const len = buf.length;
  const fragments = [];
  let i = 0;
  let inIgnoredRegion = false;
  let ignoredDepth = 0;

  while (i < len) {
    if (inIgnoredRegion) {
      if (buf[i] === 0x3C) { // '<'
        const tagEnd = indexOf(buf, 0x3E, i + 1); // '>'
        if (tagEnd === -1) { i = len; continue; }

        const tagContent = decoder.decode(buf.subarray(i, tagEnd + 1)).toLowerCase();
        const isEndTag = /^<\s*\//.test(tagContent);
        const isSelfClosing = /\/\s*>$/.test(tagContent)
          || isVoidTag(tagContent);

        if (isEndTag) {
          ignoredDepth -= 1;
          if (ignoredDepth <= 0) {
            inIgnoredRegion = false;
            ignoredDepth = 0;
          }
        } else if (!isSelfClosing) {
          ignoredDepth += 1;
        }
        i = tagEnd + 1;
        continue;
      }
      i += 1;
      continue;
    }

    // HTML comments
    if (buf[i] === 0x3C && i + 3 < len
      && buf[i + 1] === 0x21 && buf[i + 2] === 0x2D && buf[i + 3] === 0x2D) {
      const endMarker = findBytes(buf, [0x2D, 0x2D, 0x3E], i + 4); // '-->'
      i = endMarker === -1 ? len : endMarker + 3;
      continue;
    }

    // Tag
    if (buf[i] === 0x3C) {
      const tagEnd = indexOf(buf, 0x3E, i + 1);
      if (tagEnd === -1) { i = len; continue; }

      const tagContent = decoder.decode(buf.subarray(i, tagEnd + 1)).toLowerCase();
      const skipTagMatch = tagContent.match(/^<\s*(script|style|noscript|svg|math|code|pre)\b/);
      const isSelfClosing = /\/\s*>$/.test(tagContent) || isVoidTag(tagContent);

      if (skipTagMatch && !isSelfClosing) {
        inIgnoredRegion = true;
        ignoredDepth = 1;
        i = tagEnd + 1;
        continue;
      }

      i = tagEnd + 1;
      continue;
    }

    // Text content - collect until next '<'
    const textStart = i;
    while (i < len && buf[i] !== 0x3C) {
      i++;
    }
    const textLen = i - textStart;
    const rawText = decoder.decode(buf.subarray(textStart, textStart + textLen));

    if (rawText.trim() !== '') {
      fragments.push({
        byteOffset: textStart,
        byteLength: textLen,
        rawText,
      });
    }
  }

  return fragments;
}

/**
 * Decode common HTML entities.
 *
 * @param {string} str
 * @returns {string}
 */
export function decodeHtmlEntities(str) {
  let result = str
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#039;/g, "'")
    .replace(/&apos;/g, "'")
    .replace(/&#x27;/g, "'")
    .replace(/&#x2F;/g, '/')
    .replace(/&nbsp;/g, '\u00A0')
    .replace(/&ndash;/g, '\u2013')
    .replace(/&mdash;/g, '\u2014')
    .replace(/&lsquo;/g, '\u2018')
    .replace(/&rsquo;/g, '\u2019')
    .replace(/&ldquo;/g, '\u201C')
    .replace(/&rdquo;/g, '\u201D')
    .replace(/&hellip;/g, '\u2026')
    .replace(/&bull;/g, '\u2022');

  // Decimal numeric entities: &#8212;
  result = result.replace(/&#(\d+);/g, (_m, dec) => {
    const cp = parseInt(dec, 10);
    return Number.isFinite(cp) ? String.fromCodePoint(cp) : _m;
  });

  // Hex numeric entities: &#x2014;
  result = result.replace(/&#x([0-9a-fA-F]+);/g, (_m, hex) => {
    const cp = parseInt(hex, 16);
    return Number.isFinite(cp) ? String.fromCodePoint(cp) : _m;
  });

  return result;
}

/**
 * Assemble visible text from fragments.
 * Mirrors Ghost extractText(): decode entities, normalize whitespace,
 * join with spaces.
 *
 * @param {TextFragment[]} fragments
 * @returns {string}
 */
export function assembleText(fragments) {
  const parts = [];
  for (const { rawText } of fragments) {
    const decoded = decodeHtmlEntities(rawText);
    const normalized = decoded.replace(/\s+/g, ' ').trim();
    if (normalized !== '') {
      parts.push(normalized);
    }
  }
  return parts.join(' ');
}

/**
 * SHA-256 hash of text content via Web Crypto API.
 *
 * @param {string} text
 * @returns {Promise<string>} "sha256:" + 64 hex chars
 */
export async function hashText(text) {
  const data = encoder.encode(text);
  const hashBuf = await crypto.subtle.digest('SHA-256', data);
  const hashArr = new Uint8Array(hashBuf);
  let hex = '';
  for (const b of hashArr) {
    hex += b.toString(16).padStart(2, '0');
  }
  return `sha256:${hex}`;
}


// ---------------------------------------------------------------------------
// Byte-level helpers
// ---------------------------------------------------------------------------

function indexOf(buf, byte, start) {
  for (let i = start; i < buf.length; i++) {
    if (buf[i] === byte) return i;
  }
  return -1;
}

function findBytes(buf, pattern, start) {
  const pLen = pattern.length;
  for (let i = start; i <= buf.length - pLen; i++) {
    let found = true;
    for (let j = 0; j < pLen; j++) {
      if (buf[i + j] !== pattern[j]) { found = false; break; }
    }
    if (found) return i;
  }
  return -1;
}

function isVoidTag(tagContent) {
  const m = tagContent.match(/^<\s*(\w+)/);
  return m ? VOID_TAGS.has(m[1]) : false;
}
