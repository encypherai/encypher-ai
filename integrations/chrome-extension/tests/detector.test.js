/**
 * Unit tests for C2PA content detection
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';

// Mock the detector functions for testing
// In a real setup, we'd use a bundler to make these testable

// C2PA Text Manifest magic bytes: "C2PATXT\0"
const C2PA_MAGIC = [0x43, 0x32, 0x50, 0x41, 0x54, 0x58, 0x54, 0x00];

// Encypher magic bytes: "ENCYPHER"
const ENCYPHER_MAGIC = [0x45, 0x4E, 0x43, 0x59, 0x50, 0x48, 0x45, 0x52];

// Unicode variation selector ranges
const VS_RANGES = {
  VS1_START: 0xFE00,
  VS1_END: 0xFE0F,
  VS2_START: 0xE0100,
  VS2_END: 0xE01EF,
};

const ZWNBSP = 0xFEFF;

function isVariationSelector(codePoint) {
  return (
    (codePoint >= VS_RANGES.VS1_START && codePoint <= VS_RANGES.VS1_END) ||
    (codePoint >= VS_RANGES.VS2_START && codePoint <= VS_RANGES.VS2_END)
  );
}

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

function hasC2PAMagic(bytes) {
  if (bytes.length < C2PA_MAGIC.length) return false;
  for (let i = 0; i < C2PA_MAGIC.length; i++) {
    if (bytes[i] !== C2PA_MAGIC[i]) return false;
  }
  return true;
}

function hasEncypherMagic(bytes) {
  if (bytes.length < ENCYPHER_MAGIC.length) return false;
  for (let i = 0; i < ENCYPHER_MAGIC.length; i++) {
    if (bytes[i] !== ENCYPHER_MAGIC[i]) return false;
  }
  return true;
}

function detectMarkerType(bytes) {
  if (hasC2PAMagic(bytes)) return 'c2pa';
  if (hasEncypherMagic(bytes)) return 'encypher';
  return null;
}

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

// Helper to convert a byte to a variation selector (c2pa_text standard)
function byteToVS(byte) {
  if (byte >= 0 && byte <= 15) {
    return String.fromCodePoint(VS_RANGES.VS1_START + byte);
  }
  return String.fromCodePoint(VS_RANGES.VS2_START + (byte - 16));
}

// Helper to create embedded text for testing
function embedBytes(visibleText, bytes) {
  let result = String.fromCodePoint(ZWNBSP);
  let byteIndex = 0;

  for (const char of visibleText) {
    result += char;

    // Embed one byte after each visible character (one VS per byte)
    if (byteIndex < bytes.length) {
      result += byteToVS(bytes[byteIndex]);
      byteIndex++;
    }
  }

  return result;
}

describe('isVariationSelector', () => {
  it('should detect VS1 range characters', () => {
    assert.strictEqual(isVariationSelector(0xFE00), true);
    assert.strictEqual(isVariationSelector(0xFE0F), true);
    assert.strictEqual(isVariationSelector(0xFE08), true);
  });

  it('should detect VS2 range characters', () => {
    assert.strictEqual(isVariationSelector(0xE0100), true);
    assert.strictEqual(isVariationSelector(0xE01EF), true);
    assert.strictEqual(isVariationSelector(0xE0150), true);
  });

  it('should reject non-VS characters', () => {
    assert.strictEqual(isVariationSelector(0x0041), false); // 'A'
    assert.strictEqual(isVariationSelector(0x0020), false); // space
    assert.strictEqual(isVariationSelector(0xFEFF), false); // ZWNBSP
  });
});

describe('extractEmbeddedBytes', () => {
  it('should extract bytes 0-15 from VS1 range', () => {
    // Byte 0x04 via VS1: FE04
    const text = 'A' + String.fromCodePoint(0xFE04);
    const bytes = extractEmbeddedBytes(text);
    assert.strictEqual(bytes.length, 1);
    assert.strictEqual(bytes[0], 0x04);
  });

  it('should extract bytes 16-255 from VS2 range', () => {
    // Byte 0x43 (67) via VS2: E0100 + (0x43 - 16) = E0100 + 51 = E0133
    const text = 'A' + String.fromCodePoint(0xE0100 + (0x43 - 16));
    const bytes = extractEmbeddedBytes(text);
    assert.strictEqual(bytes.length, 1);
    assert.strictEqual(bytes[0], 0x43);
  });

  it('should return empty array for plain text', () => {
    const bytes = extractEmbeddedBytes('Hello World');
    assert.strictEqual(bytes.length, 0);
  });

  it('should handle mixed VS1 and VS2 characters', () => {
    // Byte 0x00 (VS1) + Byte 0xFF (255, VS2: E0100 + 239)
    const text = 'AB' + String.fromCodePoint(0xFE00) + String.fromCodePoint(0xE0100 + 239);
    const bytes = extractEmbeddedBytes(text);
    assert.strictEqual(bytes.length, 2);
    assert.strictEqual(bytes[0], 0x00);
    assert.strictEqual(bytes[1], 0xFF);
  });
});

describe('hasC2PAMagic', () => {
  it('should detect C2PA magic header', () => {
    const bytes = new Uint8Array([0x43, 0x32, 0x50, 0x41, 0x54, 0x58, 0x54, 0x00, 0x01, 0x02]);
    assert.strictEqual(hasC2PAMagic(bytes), true);
  });

  it('should reject non-C2PA content', () => {
    const bytes = new Uint8Array([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]);
    assert.strictEqual(hasC2PAMagic(bytes), false);
  });

  it('should reject too-short content', () => {
    const bytes = new Uint8Array([0x43, 0x32, 0x50]);
    assert.strictEqual(hasC2PAMagic(bytes), false);
  });
});

describe('hasEncypherMagic', () => {
  it('should detect Encypher magic header', () => {
    // "ENCYPHER" = [0x45, 0x4E, 0x43, 0x59, 0x50, 0x48, 0x45, 0x52]
    const bytes = new Uint8Array([0x45, 0x4E, 0x43, 0x59, 0x50, 0x48, 0x45, 0x52, 0x01, 0x02]);
    assert.strictEqual(hasEncypherMagic(bytes), true);
  });

  it('should reject non-Encypher content', () => {
    const bytes = new Uint8Array([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]);
    assert.strictEqual(hasEncypherMagic(bytes), false);
  });

  it('should reject C2PA content as non-Encypher', () => {
    const bytes = new Uint8Array([0x43, 0x32, 0x50, 0x41, 0x54, 0x58, 0x54, 0x00]);
    assert.strictEqual(hasEncypherMagic(bytes), false);
  });
});

describe('detectMarkerType', () => {
  it('should detect C2PA marker type', () => {
    const bytes = new Uint8Array([0x43, 0x32, 0x50, 0x41, 0x54, 0x58, 0x54, 0x00, 0x01]);
    assert.strictEqual(detectMarkerType(bytes), 'c2pa');
  });

  it('should detect Encypher marker type', () => {
    const bytes = new Uint8Array([0x45, 0x4E, 0x43, 0x59, 0x50, 0x48, 0x45, 0x52, 0x01]);
    assert.strictEqual(detectMarkerType(bytes), 'encypher');
  });

  it('should return null for unknown marker', () => {
    const bytes = new Uint8Array([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]);
    assert.strictEqual(detectMarkerType(bytes), null);
  });

  it('should return null for empty bytes', () => {
    const bytes = new Uint8Array([]);
    assert.strictEqual(detectMarkerType(bytes), null);
  });
});

describe('extractVisibleText', () => {
  it('should strip variation selectors', () => {
    const text = 'H' + String.fromCodePoint(0xFE00) + 'i';
    const visible = extractVisibleText(text);
    assert.strictEqual(visible, 'Hi');
  });

  it('should strip ZWNBSP prefix', () => {
    const text = String.fromCodePoint(ZWNBSP) + 'Hello';
    const visible = extractVisibleText(text);
    assert.strictEqual(visible, 'Hello');
  });

  it('should preserve regular text', () => {
    const text = 'Hello World!';
    const visible = extractVisibleText(text);
    assert.strictEqual(visible, 'Hello World!');
  });
});

describe('findWrappers', () => {
  // Replicate the findWrappers logic from detector.js
  function findWrappers(text) {
    const wrappers = [];
    let i = 0;
    const chars = [...text];
    while (i < chars.length) {
      if (chars[i].codePointAt(0) === ZWNBSP) {
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
          wrappers.push({ bytes: new Uint8Array(vsBytes), startIdx, endIdx: i });
        }
      } else {
        i++;
      }
    }
    return wrappers;
  }

  it('should find a C2PA wrapper in text', () => {
    // Build a C2PA wrapper: ZWNBSP + VS-encoded header bytes
    // Header: MAGIC(8) + VERSION(1) + LENGTH(4) = 13 bytes
    // MAGIC = C2PATXT\0 = [0x43, 0x32, 0x50, 0x41, 0x54, 0x58, 0x54, 0x00]
    const headerBytes = [...C2PA_MAGIC, 0x01, 0x00, 0x00, 0x00, 0x04]; // version=1, length=4
    const manifestBytes = [0xDE, 0xAD, 0xBE, 0xEF]; // 4-byte dummy manifest
    const allBytes = [...headerBytes, ...manifestBytes];

    let wrapper = String.fromCodePoint(ZWNBSP);
    for (const b of allBytes) {
      wrapper += byteToVS(b);
    }

    const text = 'Hello world' + wrapper + ' more text';
    const found = findWrappers(text);
    assert.strictEqual(found.length, 1);
    assert.strictEqual(found[0].bytes.length, allBytes.length);
    assert.ok(hasC2PAMagic(found[0].bytes));
    assert.strictEqual(detectMarkerType(found[0].bytes), 'c2pa');
  });

  it('should not find wrappers in plain text', () => {
    const found = findWrappers('Hello World, no embeddings here.');
    assert.strictEqual(found.length, 0);
  });

  it('should ignore ZWNBSP without enough VS chars', () => {
    // ZWNBSP followed by only 3 VS chars (less than 8-byte magic)
    const text = 'A' + String.fromCodePoint(ZWNBSP) + byteToVS(0x43) + byteToVS(0x32) + byteToVS(0x50) + 'B';
    const found = findWrappers(text);
    assert.strictEqual(found.length, 0);
  });
});

describe('findMicroEmbeddings', () => {
  // Replicate the findMicroEmbeddings logic from detector.js
  function findMicroEmbeddings(text) {
    const results = [];
    const chars = [...text];
    let i = 0;
    while (i < chars.length) {
      const cp = chars[i].codePointAt(0);
      if (cp === ZWNBSP) {
        i++;
        while (i < chars.length && isVariationSelector(chars[i].codePointAt(0))) i++;
        continue;
      }
      if (isVariationSelector(cp)) {
        const startIdx = i;
        let vsCount = 0;
        while (i < chars.length) {
          const c = chars[i].codePointAt(0);
          if (isVariationSelector(c)) { vsCount++; i++; }
          else if (c === ZWNBSP) { break; }
          else {
            if (i + 1 < chars.length && isVariationSelector(chars[i + 1].codePointAt(0))) { i++; }
            else { break; }
          }
        }
        if (vsCount >= 4) {
          results.push({ byteCount: vsCount, startIdx, endIdx: i });
        }
      } else { i++; }
    }
    return results;
  }

  it('should detect contiguous VS chars as micro-embedding', () => {
    // 6 VS chars interleaved with visible text (no ZWNBSP prefix)
    const text = 'A' + byteToVS(0x10) + 'B' + byteToVS(0x20) + 'C' + byteToVS(0x30) +
                 'D' + byteToVS(0x40) + 'E' + byteToVS(0x50) + 'F' + byteToVS(0x60);
    const micros = findMicroEmbeddings(text);
    assert.strictEqual(micros.length, 1);
    assert.strictEqual(micros[0].byteCount, 6);
  });

  it('should ignore fewer than 4 VS chars', () => {
    const text = 'A' + byteToVS(0x10) + 'B' + byteToVS(0x20) + 'C';
    const micros = findMicroEmbeddings(text);
    assert.strictEqual(micros.length, 0);
  });

  it('should not detect ZWNBSP-prefixed sequences as micro-embeddings', () => {
    let text = String.fromCodePoint(ZWNBSP);
    for (let i = 0; i < 10; i++) text += byteToVS(i);
    const micros = findMicroEmbeddings(text);
    assert.strictEqual(micros.length, 0);
  });

  it('should detect plain text with no VS as empty', () => {
    const micros = findMicroEmbeddings('Hello World');
    assert.strictEqual(micros.length, 0);
  });
});

describe('embedBytes helper', () => {
  it('should create embeddable text', () => {
    const embedded = embedBytes('Hi', [0x43, 0x32]);
    const bytes = extractEmbeddedBytes(embedded);
    assert.strictEqual(bytes.length, 2);
    assert.strictEqual(bytes[0], 0x43);
    assert.strictEqual(bytes[1], 0x32);
  });

  it('should preserve visible text', () => {
    const embedded = embedBytes('Hello', [0x01, 0x02, 0x03]);
    const visible = extractVisibleText(embedded);
    assert.strictEqual(visible, 'Hello');
  });
});

// ---------------------------------------------------------------------------
// _hasLegacySafeChars helper (mirrors content/detector.js)
// ---------------------------------------------------------------------------

// Replicated here because detector.js is a content script, not an ES module.
const LEGACY_SAFE_STRONG_INDICATORS = new Set([0x034F, 0x180E, 0x200E, 0x200F]);
const _LEGACY_SAFE_MIN_CHARS = 8;

function hasLegacySafeChars(text) {
  let count = 0;
  for (const char of text) {
    if (LEGACY_SAFE_STRONG_INDICATORS.has(char.codePointAt(0))) {
      count++;
      if (count >= _LEGACY_SAFE_MIN_CHARS) return true;
    }
  }
  return false;
}

// Helper: build a string with N legacy-safe indicator chars interspersed in text
function _buildLegacyText(charCode, n) {
  return 'text' + String.fromCodePoint(charCode).repeat(n) + 'end';
}

describe('_hasLegacySafeChars', () => {
  it('returns false for a single LRM (bidi control, not an embedding)', () => {
    // Google language selector appends one LRM per option — must not trigger
    assert.strictEqual(hasLegacySafeChars('Afrikaans\u200E'), false);
  });

  it('returns false for a single RLM (bidi control, not an embedding)', () => {
    assert.strictEqual(hasLegacySafeChars('marked\u200F'), false);
  });

  it('returns false for a few scattered LRM/RLM (legitimate bidi usage)', () => {
    assert.strictEqual(hasLegacySafeChars('\u200EHebrew\u200F text \u200Ewith\u200F bidi'), false);
  });

  it('returns true when >= 8 legacy-safe chars present (real embedding)', () => {
    assert.strictEqual(hasLegacySafeChars(_buildLegacyText(0x200E, 8)), true);
    assert.strictEqual(hasLegacySafeChars(_buildLegacyText(0x034F, 8)), true);
    assert.strictEqual(hasLegacySafeChars(_buildLegacyText(0x180E, 8)), true);
    assert.strictEqual(hasLegacySafeChars(_buildLegacyText(0x200F, 8)), true);
  });

  it('returns false at 7 legacy-safe chars (just under threshold)', () => {
    assert.strictEqual(hasLegacySafeChars(_buildLegacyText(0x200E, 7)), false);
  });

  it('returns true for mixed indicator chars totalling >= 8', () => {
    const mixed = 'signed\u034F\u034F\u180E\u180E\u200E\u200E\u200F\u200Ftext';
    assert.strictEqual(hasLegacySafeChars(mixed), true);
  });

  it('returns false for plain text with no ZWC markers', () => {
    assert.strictEqual(hasLegacySafeChars('Hello, world! No markers here.'), false);
  });

  it('returns false for ZWNJ/ZWJ alone (base-4 ZW chars, not sufficient)', () => {
    // ZWNJ and ZWJ are NOT strong indicators — they appear in normal Unicode text
    assert.strictEqual(hasLegacySafeChars('\u200C\u200D'), false);
  });

  it('returns false for variation selector chars (VS mode, not legacy_safe)', () => {
    const vsText = String.fromCodePoint(0xFE00, 0xFE01, 0xE0100);
    assert.strictEqual(hasLegacySafeChars(vsText), false);
  });
});
