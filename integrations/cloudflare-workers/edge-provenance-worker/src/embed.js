/**
 * Embedding plan application module.
 *
 * Ported from ghost-provenance/src/html-utils.ts embedEmbeddingPlanIntoHtml().
 * Maps codepoint-indexed embedding plan operations to byte offsets in HTML,
 * then splices invisible VS marker bytes at the correct positions.
 *
 * Uses TextEncoder/TextDecoder instead of Node.js Buffer.
 */

import { extractFragments, assembleText, decodeHtmlEntities } from './fragments.js';

const encoder = new TextEncoder();
const decoder = new TextDecoder();

/**
 * Split a string into an array of Unicode codepoints (handles surrogate pairs).
 *
 * @param {string} str
 * @returns {string[]}
 */
export function splitChars(str) {
  return [...str];
}

/**
 * Check if a character is a Unicode Variation Selector or ZWNBSP.
 *
 * @param {string} ch
 * @returns {boolean}
 */
export function isVsChar(ch) {
  const cp = ch.codePointAt(0);
  if (cp === undefined) return false;
  return (cp >= 0xFE00 && cp <= 0xFE0F)
    || (cp >= 0xE0100 && cp <= 0xE01EF)
    || cp === 0xFEFF;
}

/**
 * Check if an HTML response already contains VS marker embeddings.
 *
 * @param {string} text - Extracted article text
 * @returns {boolean}
 */
export function hasExistingMarkers(text) {
  for (const ch of text) {
    if (isVsChar(ch)) return true;
  }
  return false;
}

/**
 * Decode raw text fragment with byte offset tracking.
 * Handles HTML entities and maps each decoded character to its byte range.
 *
 * @param {string} rawText
 * @returns {Array<{ch: string, startByte: number, endByte: number}>}
 */
function decodeRawTextWithByteOffsets(rawText) {
  const mapped = [];
  let i = 0;
  let consumedBytes = 0;

  while (i < rawText.length) {
    // Handle HTML entities
    if (rawText[i] === '&') {
      const semi = rawText.indexOf(';', i + 1);
      if (semi !== -1) {
        const token = rawText.slice(i, semi + 1);
        const decoded = decodeHtmlEntities(token);
        if (decoded !== token) {
          const tokenBytes = encoder.encode(token).byteLength;
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
    const chBytes = encoder.encode(ch).byteLength;
    const startByte = consumedBytes;
    const endByte = consumedBytes + chBytes;
    mapped.push({ ch, startByte, endByte });
    consumedBytes = endByte;
    i += ch.length;
  }

  return mapped;
}

/**
 * Apply an embedding plan to HTML by inserting markers at computed byte offsets.
 *
 * This is the core algorithm ported from Ghost's embedEmbeddingPlanIntoHtml.
 * It maps codepoint indices (from the API's embedding plan) to absolute byte
 * offsets in the HTML, then splices marker characters at those offsets.
 *
 * @param {string} boundaryHtml - HTML content of the article boundary region
 * @param {number} boundaryByteOffset - Byte offset of boundaryHtml within full page HTML
 * @param {Object} plan - Embedding plan from the API
 * @param {string} plan.index_unit - Always "codepoint"
 * @param {Array<{insert_after_index: number, marker: string}>} plan.operations
 * @param {string} fullHtml - The complete page HTML
 * @returns {string|null} Modified full HTML with markers, or null on failure
 */
export function applyEmbeddingPlan(boundaryHtml, boundaryByteOffset, plan, fullHtml) {
  if (!plan) return null;
  if (plan.index_unit && plan.index_unit !== 'codepoint') return null;

  const operations = plan.operations || [];
  if (operations.length === 0) return fullHtml;

  // Step 1: Get the visible text from the boundary HTML
  const fragments = extractFragments(boundaryHtml);
  const visibleText = assembleText(fragments);
  const visibleChars = splitChars(visibleText);
  if (visibleChars.length === 0) return null;

  // Step 2: Build codepoint-to-absolute-byte-offset map
  const insertionOffsetByVisibleIndex = new Map();
  let firstVisibleStartByteAbs = null;
  let previousVisibleEndByteAbs = null;
  let visibleCursor = 0;

  for (const fragment of fragments) {
    const mapped = decodeRawTextWithByteOffsets(fragment.rawText);
    const normalized = [];

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

    // Trim leading/trailing whitespace
    while (normalized.length > 0 && normalized[0].ch === ' ') normalized.shift();
    while (normalized.length > 0 && normalized[normalized.length - 1].ch === ' ') normalized.pop();

    if (normalized.length === 0) continue;

    // Skip whitespace in visible text between fragments
    while (visibleCursor < visibleChars.length && visibleChars[visibleCursor] === ' ') {
      if (previousVisibleEndByteAbs !== null) {
        insertionOffsetByVisibleIndex.set(visibleCursor, previousVisibleEndByteAbs);
      }
      visibleCursor++;
    }

    for (const item of normalized) {
      if (visibleCursor >= visibleChars.length) return null;

      const targetChar = visibleChars[visibleCursor];
      const equivalent = item.ch === targetChar
        || (item.ch === '\u00A0' && targetChar === ' ')
        || (item.ch === ' ' && targetChar === '\u00A0');

      if (!equivalent) return null;

      // Absolute byte offset within boundaryHtml
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

  // Handle trailing whitespace
  while (visibleCursor < visibleChars.length && visibleChars[visibleCursor] === ' ') {
    if (previousVisibleEndByteAbs !== null) {
      insertionOffsetByVisibleIndex.set(visibleCursor, previousVisibleEndByteAbs);
    }
    visibleCursor++;
  }

  if (visibleCursor !== visibleChars.length) return null;
  if (firstVisibleStartByteAbs === null) return null;

  // Step 3: Validate all operations
  for (const op of operations) {
    if (!op || typeof op.insert_after_index !== 'number' || !Number.isInteger(op.insert_after_index)) {
      return null;
    }
    if (typeof op.marker !== 'string' || op.marker.length === 0) return null;
    if (op.insert_after_index < -1 || op.insert_after_index >= visibleChars.length) return null;
  }

  // Step 4: Group markers by byte offset
  const markersByOffset = new Map();
  for (const op of operations) {
    const byteOffset = op.insert_after_index === -1
      ? firstVisibleStartByteAbs
      : insertionOffsetByVisibleIndex.get(op.insert_after_index);

    if (byteOffset === undefined) return null;

    // Convert to absolute offset within fullHtml
    const absOffset = boundaryByteOffset + byteOffset;

    const existing = markersByOffset.get(absOffset) || [];
    existing.push(op.marker);
    markersByOffset.set(absOffset, existing);
  }

  // Step 5: Insert markers in reverse byte order
  const insertions = [...markersByOffset.entries()]
    .map(([byteOffset, markers]) => ({ byteOffset, marker: markers.join('') }))
    .sort((a, b) => b.byteOffset - a.byteOffset);

  let result = encoder.encode(fullHtml);
  for (const { byteOffset, marker } of insertions) {
    const markerBuf = encoder.encode(marker);
    const newBuf = new Uint8Array(result.length + markerBuf.length);
    newBuf.set(result.subarray(0, byteOffset), 0);
    newBuf.set(markerBuf, byteOffset);
    newBuf.set(result.subarray(byteOffset), byteOffset + markerBuf.length);
    result = newBuf;
  }

  return decoder.decode(result);
}
