import { parse, HTMLElement, TextNode, NodeType } from 'node-html-parser';

/**
 * HTML utility functions for Ghost CMS content.
 *
 * Mirrors the architecture of the WordPress HtmlParser class
 * (class-encypher-provenance-html-parser.php) but handles Ghost-specific
 * content structures. Ghost stores content as Lexical JSON internally
 * but exposes HTML via the Admin API.
 *
 * Key operations:
 * 1. Extract plain text from HTML (for signing via Enterprise API)
 * 2. Extract text fragments with byte offsets (for embedding signed text back)
 * 3. Embed signed text (with invisible VS markers) back into HTML text nodes
 * 4. Extract text for verification (preserving VS markers)
 * 5. Handle Ghost tags/cards (bookmark, gallery, callout, toggle, etc.)
 */

// Block-level elements that introduce paragraph/line breaks in extracted text.
const BLOCK_ELEMENTS = new Set([
  // Sectioning
  'address', 'article', 'aside', 'body', 'footer', 'header', 'main',
  'nav', 'section',
  // Heading
  'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hgroup',
  // Flow / grouping
  'blockquote', 'dd', 'details', 'dialog', 'div', 'dl', 'dt',
  'fieldset', 'figcaption', 'figure', 'form', 'hr', 'legend',
  'menu', 'ol', 'p', 'pre', 'search', 'summary', 'ul',
  // List items
  'li',
  // Table
  'caption', 'col', 'colgroup', 'table', 'thead', 'tbody', 'tfoot',
  'tr', 'td', 'th',
  // Line break
  'br',
]);

// Elements whose content is never visible text and should be skipped entirely.
const SKIP_ELEMENTS = new Set([
  'script', 'style', 'noscript', 'svg', 'math', 'video', 'audio',
  'code', 'pre',
  'canvas', 'iframe', 'object', 'embed', 'source', 'track', 'picture',
  'template', 'img', 'input', 'select', 'textarea', 'button',
  'map', 'area', 'link', 'meta', 'base', 'head', 'title',
]);

// Ghost Koenig editor card classes that contain no user-authored text.
// Ghost renders cards as HTML with specific class names.
const GHOST_SKIP_CARD_CLASSES = new Set([
  'kg-image-card',
  'kg-gallery-card',
  'kg-video-card',
  'kg-audio-card',
  'kg-file-card',
  'kg-embed-card',
  'kg-button-card',
  'kg-header-card',    // may have text but it's decorative hero
  'kg-signup-card',
  'kg-product-card',
  'kg-nft-card',
  'kg-code-card',      // code blocks — skip like wp:code
  'kg-html-card',      // raw HTML — skip like wp:html
]);

// Ghost card classes that DO contain user-authored text to sign.
const GHOST_TEXT_CARD_CLASSES = new Set([
  'kg-bookmark-card',  // has title + description text
  'kg-callout-card',   // has callout text
  'kg-toggle-card',    // has heading + content text
  'kg-blockquote-alt', // alternative blockquote style
]);

// Ghost Admin API `source=html` content can contain literal wrapper comments
// that mark an HTML card region. We must ignore wrapped payload during
// extraction/embedding so we never sign or mutate raw html-card internals.
const GHOST_HTML_CARD_WRAPPER_RE =
  /<!--\s*kg-card-begin:\s*html\s*-->[\s\S]*?<!--\s*kg-card-end:\s*html\s*-->/giu;

function stripGhostHtmlCardWrappedRegions(html: string): string {
  if (!html) return html;
  return html.replace(GHOST_HTML_CARD_WRAPPER_RE, '');
}

// =========================================================================
// Unicode Variation Selector helpers
// =========================================================================

/**
 * Check if a character is a Unicode Variation Selector or ZWNBSP (U+FEFF).
 */
export function isVsChar(ch: string): boolean {
  const cp = ch.codePointAt(0);
  if (cp === undefined) return false;
  return (cp >= 0xFE00 && cp <= 0xFE0F)
    || (cp >= 0xE0100 && cp <= 0xE01EF)
    || cp === 0xFEFF;
}

/**
 * Check if a character is a VS char or any whitespace (including NBSP).
 */
export function isVsOrWhitespace(ch: string): boolean {
  if (isVsChar(ch)) return true;
  return ch === ' ' || ch === '\t' || ch === '\n' || ch === '\r' || ch === '\u00A0';
}

/**
 * Split a string into an array of Unicode characters (handles surrogate pairs).
 */
export function splitChars(str: string): string[] {
  return [...str];
}

export interface EmbeddingPlanOperation {
  insert_after_index: number;
  marker: string;
}

export interface EmbeddingPlan {
  index_unit?: string;
  operations?: EmbeddingPlanOperation[];
}

/**
 * Apply index-based embedding operations to visible text.
 *
 * Returns null when the plan is invalid (unsupported index_unit,
 * malformed operation, or out-of-range insertion index).
 */
export function applyEmbeddingPlan(visibleText: string, plan: EmbeddingPlan | null | undefined): string | null {
  if (!plan) return null;
  if (plan.index_unit && plan.index_unit !== 'codepoint') return null;

  const operations = plan.operations || [];
  const chars = splitChars(visibleText || '');

  // Apply from right-to-left so insert indices remain stable.
  const sorted = [...operations].sort((a, b) => b.insert_after_index - a.insert_after_index);
  for (const op of sorted) {
    if (!op || typeof op.insert_after_index !== 'number' || !Number.isInteger(op.insert_after_index)) {
      return null;
    }
    if (typeof op.marker !== 'string' || op.marker.length === 0) {
      return null;
    }
    if (op.insert_after_index < -1 || op.insert_after_index >= chars.length) {
      return null;
    }

    const insertAt = op.insert_after_index + 1;
    chars.splice(insertAt, 0, op.marker);
  }

  return chars.join('');
}

/**
 * Strip all C2PA embeddings (VS chars and ZWNBSP) from content.
 */
export function stripC2paEmbeddings(content: string): string {
  return content.replace(/[\uFE00-\uFE0F\u{E0100}-\u{E01EF}\uFEFF]/gu, '');
}

/**
 * Detect C2PA embeddings in text.
 * Scans for C2PA text wrapper magic bytes encoded in Unicode variation selectors.
 */
export function detectC2paEmbeddings(text: string): { count: number; positions: number[] } {
  // C2PA magic: "C2PATXT\0" = 0x43 0x32 0x50 0x41 0x54 0x58 0x54 0x00
  const magicBytes = [0x43, 0x32, 0x50, 0x41, 0x54, 0x58, 0x54, 0x00];
  const magicChars = magicBytes.map(b => {
    if (b < 16) {
      return String.fromCodePoint(0xFE00 + b);
    }
    return String.fromCodePoint(0xE0100 + (b - 16));
  }).join('');

  const positions: number[] = [];
  let offset = 0;
  while (true) {
    const pos = text.indexOf(magicChars, offset);
    if (pos === -1) break;
    positions.push(pos);
    offset = pos + magicChars.length;
  }

  return { count: positions.length, positions };
}

// =========================================================================
// 1. Extract plain text from HTML (for signing)
// =========================================================================

/**
 * Check if a Ghost card element should be skipped (non-text content).
 */
function isGhostSkipCard(el: HTMLElement): boolean {
  const cls = el.getAttribute('class') || '';
  for (const skipClass of GHOST_SKIP_CARD_CLASSES) {
    if (cls.includes(skipClass)) return true;
  }
  return false;
}

/**
 * Check if a Ghost card element contains user-authored text.
 */
function isGhostTextCard(el: HTMLElement): boolean {
  const cls = el.getAttribute('class') || '';
  for (const textClass of GHOST_TEXT_CARD_CLASSES) {
    if (cls.includes(textClass)) return true;
  }
  return false;
}

/**
 * Recursively walk DOM nodes collecting text content.
 * Block elements insert newline boundaries. Skip elements are ignored.
 * Ghost card elements are handled based on their class.
 */
function walkDomForText(node: HTMLElement | TextNode, chunks: string[]): void {
  if (node.nodeType === NodeType.TEXT_NODE) {
    const text = (node as TextNode).rawText;
    if (text.trim() !== '') {
      chunks.push(text);
    } else if (text && chunks.length > 0 && !chunks[chunks.length - 1].endsWith('\n')) {
      chunks.push(' ');
    }
    return;
  }

  if (node.nodeType !== NodeType.ELEMENT_NODE) return;

  const el = node as HTMLElement;
  const tag = el.tagName?.toLowerCase() || '';

  if (SKIP_ELEMENTS.has(tag)) return;

  // Handle Ghost card elements
  if (tag === 'div' || tag === 'figure') {
    if (isGhostSkipCard(el)) return;
    // Ghost text cards: process their text content normally
  }

  const isBlock = BLOCK_ELEMENTS.has(tag);

  if (isBlock && chunks.length > 0 && chunks[chunks.length - 1] !== '\n') {
    chunks.push('\n');
  }

  for (const child of el.childNodes) {
    walkDomForText(child as HTMLElement | TextNode, chunks);
  }

  if (isBlock && chunks.length > 0 && chunks[chunks.length - 1] !== '\n') {
    chunks.push('\n');
  }
}

/**
 * Extract plain text from Ghost HTML post content.
 *
 * Strips HTML tags, Ghost card elements (images, embeds, code blocks),
 * and non-text elements. Preserves paragraph structure as spaces
 * (matching the API's signing pipeline which joins segments with spaces).
 *
 * Handles Ghost-specific elements:
 * - kg-image-card, kg-gallery-card, kg-video-card etc. → skipped
 * - kg-bookmark-card, kg-callout-card, kg-toggle-card → text extracted
 * - Standard HTML (p, h1-h6, blockquote, ul/ol/li, table) → text extracted
 *
 * @param html Ghost post HTML content
 * @returns Plain text suitable for the /sign API
 */
export function extractText(html: string): string {
  const sanitizedHtml = stripGhostHtmlCardWrappedRegions(html);
  const root = parse(sanitizedHtml);
  const chunks: string[] = [];
  walkDomForText(root as unknown as HTMLElement, chunks);

  const raw = chunks.join('');
  const lines = raw.split('\n');
  const cleaned: string[] = [];
  for (const line of lines) {
    const normalized = line.replace(/[ \t]+/g, ' ').trim();
    if (normalized !== '') {
      cleaned.push(normalized);
    }
  }

  return cleaned.join(' ');
}

// =========================================================================
// 2. Extract text fragments with byte offsets (for embedding)
// =========================================================================

interface TextFragment {
  byteOffset: number;
  byteLength: number;
  rawText: string;
}

/**
 * Extract text fragments from HTML with their byte offsets.
 *
 * Finds runs of text between HTML tags and comments, returning each
 * fragment's byte offset, byte length, and raw text content.
 * Skips content inside script/style/noscript/svg tags.
 */
export function extractFragments(html: string): TextFragment[] {
  const fragments: TextFragment[] = [];
  const buf = Buffer.from(html, 'utf-8');
  const len = buf.length;
  let i = 0;
  let inGhostHtmlCardWrapper = false;
  let inIgnoredRegion = false;
  let ignoredDepth = 0;

  // We work at the byte level for correct offset tracking
  while (i < len) {
    // Skip everything inside Ghost source=html card wrappers while preserving
    // original offsets for text outside the wrapper block.
    if (inGhostHtmlCardWrapper) {
      if (
        i + 3 < len
        && buf[i] === 0x3C
        && buf[i + 1] === 0x21
        && buf[i + 2] === 0x2D
        && buf[i + 3] === 0x2D
      ) {
        const endMarker = Buffer.from('-->', 'utf-8');
        const end = buf.indexOf(endMarker, i + 4);
        if (end === -1) {
          i = len;
          continue;
        }

        const commentContent = buf.subarray(i + 4, end).toString('utf-8').toLowerCase();
        if (commentContent.includes('kg-card-end: html')) {
          inGhostHtmlCardWrapper = false;
        }
        i = end + 3;
        continue;
      }

      i++;
      continue;
    }

    if (inIgnoredRegion) {
      if (buf[i] === 0x3C) { // '<'
        const tagEnd = buf.indexOf(0x3E, i + 1); // '>'
        if (tagEnd === -1) {
          i = len;
          continue;
        }

        const tagContent = buf.subarray(i, tagEnd + 1).toString('utf-8').toLowerCase();
        const isEndTag = /^<\s*\//.test(tagContent);
        const isSelfClosing = /\/\s*>$/.test(tagContent)
          || /^<\s*(area|base|br|col|embed|hr|img|input|link|meta|param|source|track|wbr)\b/.test(tagContent);

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

    if (buf[i] === 0x3C) { // '<'
      // Skip HTML comments (<!-- ... -->)
      if (i + 3 < len && buf[i + 1] === 0x21 && buf[i + 2] === 0x2D && buf[i + 3] === 0x2D) {
        const endMarker = Buffer.from('-->', 'utf-8');
        const end = buf.indexOf(endMarker, i + 4);
        if (end !== -1) {
          const commentContent = buf.subarray(i + 4, end).toString('utf-8').toLowerCase();
          if (commentContent.includes('kg-card-begin: html')) {
            inGhostHtmlCardWrapper = true;
          }
          i = end + 3;
        } else {
          i = len;
        }
        continue;
      }

      // Parse the tag
      const tagEnd = buf.indexOf(0x3E, i + 1); // '>'
      if (tagEnd === -1) {
        i = len;
        continue;
      }

      const tagContent = buf.subarray(i, tagEnd + 1).toString('utf-8').toLowerCase();

      const skipTagMatch = tagContent.match(/^<\s*(script|style|noscript|svg|math|code|pre)\b/);
      const classAttrMatch = tagContent.match(/class\s*=\s*("([^"]*)"|'([^']*)')/);
      const classNames = (classAttrMatch?.[2] || classAttrMatch?.[3] || '').split(/\s+/).filter(Boolean);
      const hasSkipClass = classNames.some((cls) => GHOST_SKIP_CARD_CLASSES.has(cls));
      const isSelfClosing = /\/\s*>$/.test(tagContent)
        || /^<\s*(area|base|br|col|embed|hr|img|input|link|meta|param|source|track|wbr)\b/.test(tagContent);

      if ((skipTagMatch || hasSkipClass) && !isSelfClosing) {
        inIgnoredRegion = true;
        ignoredDepth = 1;
        i = tagEnd + 1;
        continue;
      }

      i = tagEnd + 1;
      continue;
    }

    // Text content — collect until next '<'
    const textStart = i;
    while (i < len && buf[i] !== 0x3C) {
      i++;
    }
    const textLen = i - textStart;
    const rawText = buf.subarray(textStart, textStart + textLen).toString('utf-8');

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

// =========================================================================
// 3. Embed signed text back into HTML
// =========================================================================

/**
 * Decode common HTML entities in a string.
 */
function decodeHtmlEntities(str: string): string {
  const decodedNamed = str
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#039;/g, "'")
    .replace(/&apos;/g, "'")
    .replace(/&#x27;/g, "'")
    .replace(/&#x2F;/g, '/')
    .replace(/&nbsp;/g, '\u00A0')
    .replace(/&ndash;/g, '–')
    .replace(/&mdash;/g, '—')
    .replace(/&lsquo;/g, '‘')
    .replace(/&rsquo;/g, '’')
    .replace(/&ldquo;/g, '“')
    .replace(/&rdquo;/g, '”')
    .replace(/&hellip;/g, '…')
    .replace(/&bull;/g, '•');

  return decodedNamed
    // Decimal numeric entities: &#8212;
    .replace(/&#(\d+);/g, (_m, dec) => {
      const cp = Number.parseInt(dec, 10);
      return Number.isFinite(cp) ? String.fromCodePoint(cp) : _m;
    })
    // Hex numeric entities: &#x2014;
    .replace(/&#x([0-9a-fA-F]+);/g, (_m, hex) => {
      const cp = Number.parseInt(hex, 16);
      return Number.isFinite(cp) ? String.fromCodePoint(cp) : _m;
    })
    ;
}

interface MappedChar {
  ch: string;
  startByte: number;
  endByte: number;
}

function decodeRawTextWithByteOffsets(rawText: string): MappedChar[] {
  const mapped: MappedChar[] = [];
  let i = 0;
  let consumedBytes = 0;

  while (i < rawText.length) {
    if (rawText[i] === '&') {
      const semi = rawText.indexOf(';', i + 1);
      if (semi !== -1) {
        const token = rawText.slice(i, semi + 1);
        const decoded = decodeHtmlEntities(token);
        if (decoded !== token) {
          const tokenBytes = Buffer.byteLength(token, 'utf-8');
          const startByte = consumedBytes;
          const endByte = consumedBytes + tokenBytes;
          const decodedChars = splitChars(decoded);
          for (const ch of decodedChars) {
            mapped.push({ ch, startByte, endByte });
          }
          consumedBytes = endByte;
          i = semi + 1;
          continue;
        }
      }
    }

    const cp = rawText.codePointAt(i);
    if (cp === undefined) break;
    const ch = String.fromCodePoint(cp);
    const chBytes = Buffer.byteLength(ch, 'utf-8');
    const startByte = consumedBytes;
    const endByte = consumedBytes + chBytes;
    mapped.push({ ch, startByte, endByte });
    consumedBytes = endByte;
    i += ch.length;
  }

  return mapped;
}

/**
 * Embed markers from an embedding plan directly into original HTML text nodes.
 *
 * This avoids reconstructing full signed text and instead inserts markers by
 * codepoint index into the existing HTML byte stream.
 *
 * Returns null when mapping or plan validation fails.
 */
export function embedEmbeddingPlanIntoHtml(html: string, plan: EmbeddingPlan | null | undefined): string | null {
  if (!plan) return null;
  if (plan.index_unit && plan.index_unit !== 'codepoint') return null;

  const operations = plan.operations || [];
  if (operations.length === 0) return html;

  const visibleText = extractText(html);
  const visibleChars = splitChars(visibleText);
  if (visibleChars.length === 0) return null;

  const fragments = extractFragments(html);

  const insertionOffsetByVisibleIndex = new Map<number, number>();
  let firstVisibleStartByteAbs: number | null = null;
  let previousVisibleEndByteAbs: number | null = null;
  let visibleCursor = 0;

  for (const fragment of fragments) {
    const mapped = decodeRawTextWithByteOffsets(fragment.rawText);
    const normalized: MappedChar[] = [];

    for (const item of mapped) {
      if (/\s/u.test(item.ch)) {
        const last = normalized[normalized.length - 1];
        if (!last) continue;
        if (last.ch === ' ') {
          last.endByte = item.endByte;
        } else {
          normalized.push({ ch: ' ', startByte: item.startByte, endByte: item.endByte });
        }
      } else {
        normalized.push({ ...item });
      }
    }

    while (normalized.length > 0 && normalized[0].ch === ' ') {
      normalized.shift();
    }
    while (normalized.length > 0 && normalized[normalized.length - 1].ch === ' ') {
      normalized.pop();
    }

    if (normalized.length === 0) {
      continue;
    }

    while (visibleCursor < visibleChars.length && visibleChars[visibleCursor] === ' ') {
      if (previousVisibleEndByteAbs !== null) {
        insertionOffsetByVisibleIndex.set(visibleCursor, previousVisibleEndByteAbs);
      }
      visibleCursor++;
    }

    for (const item of normalized) {
      if (visibleCursor >= visibleChars.length) {
        return null;
      }

      const targetChar = visibleChars[visibleCursor];
      const equivalent = item.ch === targetChar
        || (item.ch === '\u00A0' && targetChar === ' ')
        || (item.ch === ' ' && targetChar === '\u00A0');

      if (!equivalent) {
        return null;
      }

      const startByteAbs = fragment.byteOffset + item.startByte;
      const endByteAbs = fragment.byteOffset + item.endByte;
      if (firstVisibleStartByteAbs === null) {
        firstVisibleStartByteAbs = startByteAbs;
      }

      insertionOffsetByVisibleIndex.set(visibleCursor, endByteAbs);
      previousVisibleEndByteAbs = endByteAbs;
      visibleCursor++;
    }
  }

  while (visibleCursor < visibleChars.length && visibleChars[visibleCursor] === ' ') {
    if (previousVisibleEndByteAbs !== null) {
      insertionOffsetByVisibleIndex.set(visibleCursor, previousVisibleEndByteAbs);
    }
    visibleCursor++;
  }

  if (visibleCursor !== visibleChars.length) return null;
  if (firstVisibleStartByteAbs === null) return null;

  for (const op of operations) {
    if (!op || typeof op.insert_after_index !== 'number' || !Number.isInteger(op.insert_after_index)) {
      return null;
    }
    if (typeof op.marker !== 'string' || op.marker.length === 0) {
      return null;
    }
    if (op.insert_after_index < -1 || op.insert_after_index >= visibleChars.length) {
      return null;
    }
  }

  const markersByOffset = new Map<number, string[]>();
  for (const op of operations) {
    const byteOffset = op.insert_after_index === -1
      ? firstVisibleStartByteAbs
      : insertionOffsetByVisibleIndex.get(op.insert_after_index);

    if (byteOffset === undefined) {
      return null;
    }

    const existing = markersByOffset.get(byteOffset) || [];
    existing.push(op.marker);
    markersByOffset.set(byteOffset, existing);
  }

  const insertions = [...markersByOffset.entries()]
    .map(([byteOffset, markers]) => ({ byteOffset, marker: markers.join('') }))
    .sort((a, b) => b.byteOffset - a.byteOffset);

  let result = Buffer.from(html, 'utf-8');
  for (const { byteOffset, marker } of insertions) {
    const markerBuf = Buffer.from(marker, 'utf-8');
    result = Buffer.concat([
      result.subarray(0, byteOffset),
      markerBuf,
      result.subarray(byteOffset),
    ]);
  }

  return result.toString('utf-8');
}

/**
 * Embed signed text (with invisible VS markers) back into HTML text nodes.
 *
 * Uses a byte-level approach to avoid DOM serialization mangling
 * invisible Unicode characters.
 *
 * Algorithm:
 * 1. Extract text fragments from the HTML (byte offsets)
 * 2. For each fragment, normalize (decode entities, collapse whitespace)
 * 3. Match normalized fragment against the signed text sequentially
 * 4. Replace the raw HTML fragment with the signed chunk (preserving leading WS)
 * 5. Apply replacements in reverse byte order to preserve offsets
 *
 * @param html   Original Ghost post HTML
 * @param signed Signed plain text from the Enterprise API (contains invisible VS markers)
 * @returns HTML with invisible markers embedded in text nodes
 */
export function embedSignedText(html: string, signed: string): string {
  const fragments = extractFragments(html);

  if (fragments.length === 0) {
    return signed;
  }

  const signedChars = splitChars(signed);
  const signedLen = signedChars.length;
  let cursor = 0;

  const replacements: Array<{ byteOffset: number; byteLength: number; replacement: string }> = [];
  let lastFragIdx: number | null = null;

  for (let fragIdx = 0; fragIdx < fragments.length; fragIdx++) {
    const { byteOffset, byteLength, rawText } = fragments[fragIdx];

    // Normalize fragment: decode HTML entities, collapse whitespace
    const decoded = decodeHtmlEntities(rawText);
    const normalized = decoded.replace(/\s+/gu, ' ').trim();
    if (normalized === '') continue;

    // Collect inter-fragment VS chars and whitespace gap
    let gapVs = '';
    while (cursor < signedLen && isVsOrWhitespace(signedChars[cursor])) {
      if (isVsChar(signedChars[cursor])) {
        gapVs += signedChars[cursor];
      }
      cursor++;
    }

    // Match visible text, skipping embedded VS chars in the signed text
    const matchStart = cursor;
    const normChars = splitChars(normalized);
    let ti = 0;
    let si = cursor;
    const normLen = normChars.length;

    while (si < signedLen && ti < normLen) {
      const ch = signedChars[si];
      if (isVsChar(ch)) {
        si++;
        continue;
      }
      if (ch === normChars[ti]) {
        ti++;
        si++;
      } else if (ch === '\u00A0' && normChars[ti] === ' ') {
        ti++;
        si++;
      } else if (normChars[ti] === '\u00A0' && ch === ' ') {
        ti++;
        si++;
      } else {
        break;
      }
    }

    if (ti !== normLen) {
      // No match — attach gap VS chars to previous fragment
      if (gapVs !== '' && lastFragIdx !== null) {
        const prev = replacements.find((_, idx) => idx === replacements.length - 1);
        if (prev) prev.replacement += gapVs;
      }
      continue;
    }

    // Consume trailing VS chars after the matched text
    while (si < signedLen && isVsChar(signedChars[si])) {
      si++;
    }

    // Extract the signed chunk (visible text + embedded VS markers)
    const signedChunk = signedChars.slice(matchStart, si).join('');
    cursor = si;

    // Preserve original leading whitespace from the raw HTML text
    const leadingWsMatch = rawText.match(/^(\s+)/u);
    const leadingWs = leadingWsMatch ? leadingWsMatch[1] : '';

    const replacement = leadingWs + gapVs + signedChunk;
    replacements.push({ byteOffset, byteLength, replacement });
    lastFragIdx = fragIdx;
  }

  // Append any remaining VS chars (tail of C2PA manifest) to the last replacement
  let remainingVs = '';
  while (cursor < signedLen) {
    if (isVsChar(signedChars[cursor])) {
      remainingVs += signedChars[cursor];
    }
    cursor++;
  }
  if (remainingVs !== '' && replacements.length > 0) {
    replacements[replacements.length - 1].replacement += remainingVs;
  }

  // Apply replacements in reverse byte-offset order to preserve positions
  const sorted = [...replacements].sort((a, b) => b.byteOffset - a.byteOffset);
  const buf = Buffer.from(html, 'utf-8');
  let result = buf;

  for (const { byteOffset, byteLength, replacement } of sorted) {
    const repBuf = Buffer.from(replacement, 'utf-8');
    result = Buffer.concat([
      result.subarray(0, byteOffset),
      repBuf,
      result.subarray(byteOffset + byteLength),
    ]);
  }

  return result.toString('utf-8');
}

// =========================================================================
// 4. Extract text for verification (preserving VS markers)
// =========================================================================

/**
 * Extract plain text from HTML for verification, preserving VS markers.
 *
 * Unlike extractText() (which may strip invisible Unicode chars),
 * this method works at the byte level via extractFragments().
 * It strips HTML tags while keeping all VS characters intact —
 * critical for C2PA content hash matching.
 */
export function extractTextForVerify(html: string): string {
  const fragments = extractFragments(html);
  if (fragments.length === 0) return '';

  const parts: string[] = [];
  for (const { rawText } of fragments) {
    const decoded = decodeHtmlEntities(rawText);
    const chars = splitChars(decoded);
    const resultChars: string[] = [];
    let lastWasWs = false;

    for (const ch of chars) {
      if (isVsChar(ch)) {
        resultChars.push(ch);
        lastWasWs = false;
      } else if (/\s/u.test(ch)) {
        if (!lastWasWs) {
          resultChars.push(' ');
          lastWasWs = true;
        }
      } else {
        resultChars.push(ch);
        lastWasWs = false;
      }
    }

    const content = resultChars.join('').trim();
    if (content !== '') {
      parts.push(content);
    }
  }

  return parts.join(' ');
}

// =========================================================================
// 5. Ghost-specific tag/card handling
// =========================================================================

/**
 * Extract text content from Ghost bookmark cards.
 * Bookmark cards render as <figure class="kg-card kg-bookmark-card">
 * with title and description inside.
 */
export function extractBookmarkText(html: string): string {
  const root = parse(html);
  const bookmarks = root.querySelectorAll('.kg-bookmark-card');
  const texts: string[] = [];

  for (const bm of bookmarks) {
    const title = bm.querySelector('.kg-bookmark-title');
    const desc = bm.querySelector('.kg-bookmark-description');
    if (title) texts.push(title.textContent.trim());
    if (desc) texts.push(desc.textContent.trim());
  }

  return texts.join(' ');
}

/**
 * Extract text content from Ghost callout cards.
 * Callout cards render as <div class="kg-card kg-callout-card ...">
 */
export function extractCalloutText(html: string): string {
  const root = parse(html);
  const callouts = root.querySelectorAll('.kg-callout-card');
  const texts: string[] = [];

  for (const co of callouts) {
    const textEl = co.querySelector('.kg-callout-text');
    if (textEl) texts.push(textEl.textContent.trim());
  }

  return texts.join(' ');
}

/**
 * Extract text content from Ghost toggle cards.
 * Toggle cards render as <div class="kg-card kg-toggle-card">
 * with heading and content sections.
 */
export function extractToggleText(html: string): string {
  const root = parse(html);
  const toggles = root.querySelectorAll('.kg-toggle-card');
  const texts: string[] = [];

  for (const tg of toggles) {
    const heading = tg.querySelector('.kg-toggle-heading-text');
    const content = tg.querySelector('.kg-toggle-content');
    if (heading) texts.push(heading.textContent.trim());
    if (content) texts.push(content.textContent.trim());
  }

  return texts.join(' ');
}

/**
 * Extract all user-visible text from Ghost HTML, including text from
 * Ghost-specific card types (bookmarks, callouts, toggles).
 * This is the main entry point for text extraction before signing.
 */
export function extractAllText(html: string): string {
  return extractText(html);
}
