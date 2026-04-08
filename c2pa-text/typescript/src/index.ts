/**
 * C2PA Text Manifest Wrapper Reference Implementation.
 *
 * Validation:
 *   Use validateManifest() to check manifest structure before embedding.
 *   This helps catch issues early and provides detailed diagnostics.
 */

// Re-export validation utilities
export {
  ValidationCode,
  ValidationIssue,
  ValidationResult,
  validateManifest,
  validateJumbfStructure,
  validateWrapperBytes,
} from './validator';

// Constants
const MAGIC = new Uint8Array([0x43, 0x32, 0x50, 0x41, 0x54, 0x58, 0x54, 0x00]); // "C2PATXT\0"
const VERSION = 1;
const HEADER_SIZE = 13; // 8 (Magic) + 1 (Version) + 4 (Length)
const ZWNBSP = '\uFEFF';

// Variation Selectors
const VS_START = 0xFE00;
const VS_END = 0xFE0F;
const VS_SUP_START = 0xE0100;
const VS_SUP_END = 0xE01EF;

/**
 * Convert a byte to a Variation Selector string.
 */
function byteToVs(byte: number): string {
  if (byte >= 0 && byte <= 15) {
    return String.fromCodePoint(VS_START + byte);
  } else if (byte >= 16 && byte <= 255) {
    return String.fromCodePoint(VS_SUP_START + (byte - 16));
  }
  throw new Error("Byte out of range 0-255");
}

/**
 * Convert a Variation Selector codepoint to a byte.
 */
function vsToByte(codepoint: number): number | null {
  if (codepoint >= VS_START && codepoint <= VS_END) {
    return codepoint - VS_START;
  }
  if (codepoint >= VS_SUP_START && codepoint <= VS_SUP_END) {
    return (codepoint - VS_SUP_START) + 16;
  }
  return null;
}

/**
 * Encode raw bytes into a C2PA Text Manifest Wrapper string.
 */
export function encodeWrapper(manifestBytes: Uint8Array): string {
  // create header: Magic (8) + Version (1) + Length (4, Big Endian)
  const header = new Uint8Array(HEADER_SIZE);
  header.set(MAGIC, 0);
  header[8] = VERSION;

  // Write length (Big Endian)
  const len = manifestBytes.length;
  header[9] = (len >>> 24) & 0xFF;
  header[10] = (len >>> 16) & 0xFF;
  header[11] = (len >>> 8) & 0xFF;
  header[12] = len & 0xFF;

  let result = ZWNBSP;

  // Encode header
  for (let i = 0; i < header.length; i++) {
    result += byteToVs(header[i]);
  }

  // Encode body
  for (let i = 0; i < manifestBytes.length; i++) {
    result += byteToVs(manifestBytes[i]);
  }

  return result;
}

/**
 * Compute the deterministic target UTF-8 byte length of a padded wrapper
 * for a manifest of `manifestByteCount` bytes.
 *
 * Formula: `3 + (13 + M) * 4 + 6`
 */
export function worstCaseWrapperByteLength(manifestByteCount: number): number {
  return 3 + (HEADER_SIZE + manifestByteCount) * 4 + 6;
}

/**
 * Compute padding bytes whose VS encoding totals exactly `gap` UTF-8 bytes.
 */
function computePadding(gap: number): number[] {
  if (gap === 0) return [];
  for (let b = Math.floor(gap / 4); b >= 0; b--) {
    const remainder = gap - 4 * b;
    if (remainder >= 0 && remainder % 3 === 0) {
      const a = remainder / 3;
      return [...Array(a).fill(0x00), ...Array(b).fill(0xFF)];
    }
  }
  throw new Error(`Cannot pad ${gap} UTF-8 bytes with 3-byte and 4-byte VS characters`);
}

/**
 * Encode a C2PA Text Manifest Wrapper and pad to an exact UTF-8 byte length.
 *
 * Decoders use `manifestLength` to extract the manifest and ignore trailing
 * padding bytes.
 */
export function encodeWrapperPadded(manifestBytes: Uint8Array, targetByteLength: number): string {
  const base = encodeWrapper(manifestBytes);
  const actual = new TextEncoder().encode(base).length;
  if (targetByteLength < actual) {
    throw new Error(`targetByteLength (${targetByteLength}) is smaller than actual wrapper byte length (${actual})`);
  }
  const gap = targetByteLength - actual;
  if (gap === 0) return base;
  const padding = computePadding(gap);
  return base + padding.map(byteToVs).join('');
}

/**
 * Embed a C2PA manifest into text.
 * Normalizes the text to NFC before embedding.
 */
export function embedManifest(text: string, manifestBytes: Uint8Array): string {
  return text.normalize('NFC') + encodeWrapper(manifestBytes);
}

/**
 * Extract a C2PA manifest from text.
 * Returns null if no valid wrapper is found.
 */
export function extractManifest(text: string): { manifest: Uint8Array, cleanText: string, offset: number, length: number } | null {
  // Simple regex scan is tricky with JS regex for surrogate pairs (VS_SUP).
  // We'll iterate manually or use a pattern.
  // Pattern: ZWNBSP + (VS chars)+

  const vsPattern = /^\ufeff([\ufe00-\ufe0f\udb40\udd00-\udb40\uddef]+)/u;

  // Find wrapper. We look for ZWNBSP followed by VS chars.
  // Since it can be anywhere (but usually end), we search.

  // Let's scan for ZWNBSP
  let matchIndex = -1;
  let matchLength = 0;
  let decodedBytes: number[] = [];

  // We iterate through the string to find potential starts
  for (let i = 0; i < text.length; i++) {
    if (text[i] === ZWNBSP) {
      // Potential start. Check subsequent chars.
      const potentialBytes: number[] = [];
      let j = i + 1;

      while (j < text.length) {
        const code = text.codePointAt(j);
        if (code === undefined) break;

        const byte = vsToByte(code);
        if (byte === null) {
            // End of sequence
            break;
        }

        potentialBytes.push(byte);
        // Advance index (1 or 2 depending on surrogate pair)
        j += (code > 0xFFFF) ? 2 : 1;
      }

      if (potentialBytes.length >= HEADER_SIZE) {
        // Check Header
        let validHeader = true;
        for(let k=0; k<8; k++) {
            if(potentialBytes[k] !== MAGIC[k]) validHeader = false;
        }
        if (potentialBytes[8] !== VERSION) validHeader = false;

        if (validHeader) {
            // Check Length
            const len = (potentialBytes[9] << 24) | (potentialBytes[10] << 16) | (potentialBytes[11] << 8) | potentialBytes[12];

            if (potentialBytes.length >= HEADER_SIZE + len) {
                // Found it!
                matchIndex = i;
                matchLength = j - i; // Total char length
                // Extract just the manifest bytes
                decodedBytes = potentialBytes.slice(HEADER_SIZE, HEADER_SIZE + len);

                // Check for second occurrence (spec req)
                break;
            }
        }
      }
    }
  }

  if (matchIndex === -1) {
      return null;
  }

  const manifest = new Uint8Array(decodedBytes);

  // Remove wrapper
  const pre = text.substring(0, matchIndex);
  const post = text.substring(matchIndex + matchLength);
  const cleanText = (pre + post).normalize('NFC');

  return { manifest, cleanText, offset: matchIndex, length: matchLength };
}
