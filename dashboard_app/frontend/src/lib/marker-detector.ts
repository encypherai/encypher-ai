/**
 * VS256 Marker Detection Utility
 *
 * Client-side detection of invisible Encypher markers embedded in text.
 * Detects both micro (36-char) and micro_ecc (44-char) VS256 signatures,
 * as well as longer "basic" format VS blocks (JSON payloads) and C2PA wrappers.
 *
 * This module does NOT perform cryptographic verification — it only locates
 * marker positions so the UI can highlight them. Actual verification is done
 * server-side via the /api/v1/verify/advanced endpoint.
 */

// ---------------------------------------------------------------------------
// VS256 Alphabet Constants
// ---------------------------------------------------------------------------

const VS_BMP_START = 0xfe00; // VS1  (U+FE00)
const VS_BMP_END = 0xfe0f; // VS16 (U+FE0F)
const VS_SUPP_START = 0xe0100; // VS17 (U+E0100)
const VS_SUPP_END = 0xe01ef; // VS256 (U+E01EF)

// Magic prefix byte values: 239, 240, 241, 242
const MAGIC_BYTES = [239, 240, 241, 242];

function isVariationSelector(codePoint: number): boolean {
  return (
    (codePoint >= VS_BMP_START && codePoint <= VS_BMP_END) ||
    (codePoint >= VS_SUPP_START && codePoint <= VS_SUPP_END)
  );
}

function vsToByte(codePoint: number): number | null {
  if (codePoint >= VS_BMP_START && codePoint <= VS_BMP_END) {
    return codePoint - VS_BMP_START; // 0-15
  }
  if (codePoint >= VS_SUPP_START && codePoint <= VS_SUPP_END) {
    return codePoint - VS_SUPP_START + 16; // 16-255
  }
  return null;
}

// ---------------------------------------------------------------------------
// Marker Types
// ---------------------------------------------------------------------------

export type MarkerType = 'micro' | 'micro_ecc' | 'basic' | 'c2pa' | 'unknown';

export interface DetectedMarker {
  /** Character index where the marker starts in the original text */
  startIndex: number;
  /** Character index where the marker ends (exclusive) */
  endIndex: number;
  /** Number of VS characters in this marker */
  charCount: number;
  /** Detected marker type */
  type: MarkerType;
  /** Raw decoded bytes (for display purposes) */
  decodedBytes: number[];
  /** UUID hex string if this is a micro/micro_ecc marker */
  uuid: string | null;
  /** HMAC hex string if this is a micro/micro_ecc marker */
  hmac: string | null;
  /** RS parity hex string if this is a micro_ecc marker */
  rsParity: string | null;
  /** The visible text sentence this marker is associated with (preceding text) */
  associatedText: string;
  /** Index of this marker among all detected markers */
  index: number;
}

// ---------------------------------------------------------------------------
// Core Detection
// ---------------------------------------------------------------------------

/**
 * Find all contiguous VS blocks in the text.
 * Returns raw blocks with start/end indices and decoded byte values.
 */
function findAllVsBlocks(
  text: string
): Array<{ start: number; end: number; bytes: number[] }> {
  const blocks: Array<{ start: number; end: number; bytes: number[] }> = [];
  let i = 0;

  while (i < text.length) {
    const cp = text.codePointAt(i);
    if (cp === undefined) break;

    if (isVariationSelector(cp)) {
      const blockStart = i;
      const decodedBytes: number[] = [];

      while (i < text.length) {
        const innerCp = text.codePointAt(i);
        if (innerCp === undefined) break;
        const byteVal = vsToByte(innerCp);
        if (byteVal !== null) {
          decodedBytes.push(byteVal);
          // Supplementary plane chars are 2 JS char units (surrogate pair)
          i += innerCp > 0xffff ? 2 : 1;
        } else {
          break;
        }
      }

      if (decodedBytes.length >= 4) {
        blocks.push({ start: blockStart, end: i, bytes: decodedBytes });
      }
    } else {
      // Advance past this character (handle surrogate pairs)
      i += cp > 0xffff ? 2 : 1;
    }
  }

  return blocks;
}

/**
 * Check if a byte array starts with the VS256 magic prefix.
 */
function hasMagicPrefix(bytes: number[]): boolean {
  if (bytes.length < 4) return false;
  return (
    bytes[0] === MAGIC_BYTES[0] &&
    bytes[1] === MAGIC_BYTES[1] &&
    bytes[2] === MAGIC_BYTES[2] &&
    bytes[3] === MAGIC_BYTES[3]
  );
}

/**
 * Convert a byte array to a hex string.
 */
function bytesToHex(bytes: number[]): string {
  return bytes.map((b) => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Classify a VS block into a marker type based on its structure.
 */
function classifyBlock(bytes: number[]): MarkerType {
  if (!hasMagicPrefix(bytes)) {
    // No magic prefix — could be a basic format (JSON) or C2PA wrapper
    if (bytes.length > 100) {
      // Try to detect if it's a JSON payload (basic format)
      try {
        const str = new TextDecoder().decode(new Uint8Array(bytes));
        const trimmed = str.replace(/^\ufeff/, '');
        JSON.parse(trimmed);
        return 'basic';
      } catch {
        return 'c2pa';
      }
    }
    return 'unknown';
  }

  const payloadLen = bytes.length - 4; // subtract magic prefix
  if (payloadLen === 32) return 'micro'; // 16 UUID + 16 HMAC
  if (payloadLen === 40) return 'micro_ecc'; // 16 UUID + 16 HMAC + 8 RS
  return 'unknown';
}

/**
 * Extract UUID, HMAC, and RS parity from a micro/micro_ecc marker's bytes.
 */
function parseMarkerPayload(
  bytes: number[],
  type: MarkerType
): { uuid: string | null; hmac: string | null; rsParity: string | null } {
  if (type !== 'micro' && type !== 'micro_ecc') {
    return { uuid: null, hmac: null, rsParity: null };
  }

  const payload = bytes.slice(4); // skip magic prefix
  const uuidBytes = payload.slice(0, 16);
  const hmacBytes = payload.slice(16, 32);
  const rsBytes = type === 'micro_ecc' ? payload.slice(32, 40) : [];

  // Format UUID with dashes: 8-4-4-4-12
  const uuidHex = bytesToHex(uuidBytes);
  const uuid = [
    uuidHex.slice(0, 8),
    uuidHex.slice(8, 12),
    uuidHex.slice(12, 16),
    uuidHex.slice(16, 20),
    uuidHex.slice(20, 32),
  ].join('-');

  return {
    uuid,
    hmac: bytesToHex(hmacBytes),
    rsParity: rsBytes.length > 0 ? bytesToHex(rsBytes) : null,
  };
}

/**
 * Get the visible text preceding a marker (the sentence it's associated with).
 * Looks backward from the marker start to find the preceding sentence.
 */
function getAssociatedText(
  text: string,
  markerStart: number,
  prevMarkerEnd: number
): string {
  const segment = text.slice(prevMarkerEnd, markerStart);
  // Strip any remaining VS characters and trim
  const clean = segment.replace(
    /[\uFE00-\uFE0F]|[\uDB40][\uDD00-\uDDEF]/g,
    ''
  );
  return clean.trim();
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Detect all Encypher markers in the given text.
 *
 * Returns an array of DetectedMarker objects with position, type, and
 * parsed payload information. Does NOT verify signatures — that requires
 * a server-side call.
 */
export function detectMarkers(text: string): DetectedMarker[] {
  const blocks = findAllVsBlocks(text);
  const markers: DetectedMarker[] = [];

  let prevEnd = 0;

  for (let idx = 0; idx < blocks.length; idx++) {
    const block = blocks[idx];
    const type = classifyBlock(block.bytes);
    const { uuid, hmac, rsParity } = parseMarkerPayload(block.bytes, type);
    const associatedText = getAssociatedText(text, block.start, prevEnd);

    markers.push({
      startIndex: block.start,
      endIndex: block.end,
      charCount: block.bytes.length,
      type,
      decodedBytes: block.bytes,
      uuid,
      hmac,
      rsParity,
      associatedText,
      index: idx,
    });

    prevEnd = block.end;
  }

  return markers;
}

/**
 * Strip all invisible VS characters from text, returning clean visible text.
 */
export function stripMarkers(text: string): string {
  let result = '';
  let i = 0;

  while (i < text.length) {
    const cp = text.codePointAt(i);
    if (cp === undefined) break;

    if (!isVariationSelector(cp)) {
      result += String.fromCodePoint(cp);
    }
    i += cp > 0xffff ? 2 : 1;
  }

  return result;
}

/**
 * Build an array of text segments interleaved with marker positions.
 * Used by the UI to render formatted text with marker icons.
 */
export interface TextSegment {
  type: 'text' | 'marker';
  content: string; // visible text for 'text', empty for 'marker'
  marker?: DetectedMarker;
}

export function segmentText(text: string): TextSegment[] {
  const markers = detectMarkers(text);
  if (markers.length === 0) {
    return [{ type: 'text', content: stripMarkers(text) }];
  }

  const segments: TextSegment[] = [];
  let prevEnd = 0;

  for (const marker of markers) {
    // Text before this marker
    if (marker.startIndex > prevEnd) {
      const textBefore = text.slice(prevEnd, marker.startIndex);
      const clean = stripMarkers(textBefore);
      if (clean) {
        segments.push({ type: 'text', content: clean });
      }
    }

    // The marker itself
    segments.push({ type: 'marker', content: '', marker });

    prevEnd = marker.endIndex;
  }

  // Text after the last marker
  if (prevEnd < text.length) {
    const remaining = text.slice(prevEnd);
    const clean = stripMarkers(remaining);
    if (clean) {
      segments.push({ type: 'text', content: clean });
    }
  }

  return segments;
}

/**
 * Summary statistics for detected markers.
 */
export interface MarkerSummary {
  total: number;
  micro: number;
  microEcc: number;
  basic: number;
  c2pa: number;
  unknown: number;
}

export function summarizeMarkers(markers: DetectedMarker[]): MarkerSummary {
  return {
    total: markers.length,
    micro: markers.filter((m) => m.type === 'micro').length,
    microEcc: markers.filter((m) => m.type === 'micro_ecc').length,
    basic: markers.filter((m) => m.type === 'basic').length,
    c2pa: markers.filter((m) => m.type === 'c2pa').length,
    unknown: markers.filter((m) => m.type === 'unknown').length,
  };
}
