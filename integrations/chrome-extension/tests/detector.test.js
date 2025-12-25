/**
 * Unit tests for C2PA content detection
 */

import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert';

// Mock the detector functions for testing
// In a real setup, we'd use a bundler to make these testable

// C2PA Text Manifest magic bytes: "C2PATXT\0"
const C2PA_MAGIC = [0x43, 0x32, 0x50, 0x41, 0x54, 0x58, 0x54, 0x00];

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
  let highNibble = null;
  
  for (const char of text) {
    const codePoint = char.codePointAt(0);
    
    if (codePoint >= VS_RANGES.VS1_START && codePoint <= VS_RANGES.VS1_END) {
      const nibble = codePoint - VS_RANGES.VS1_START;
      if (highNibble === null) {
        highNibble = nibble;
      } else {
        bytes.push((highNibble << 4) | nibble);
        highNibble = null;
      }
    } else if (codePoint >= VS_RANGES.VS2_START && codePoint <= VS_RANGES.VS2_END) {
      bytes.push(codePoint - VS_RANGES.VS2_START);
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

// Helper to create embedded text for testing
function embedBytes(visibleText, bytes) {
  let result = String.fromCodePoint(ZWNBSP);
  let byteIndex = 0;
  
  for (const char of visibleText) {
    result += char;
    
    // Embed one byte after each visible character (simplified)
    if (byteIndex < bytes.length) {
      const byte = bytes[byteIndex];
      // Use VS1 range (4-bit nibbles)
      const highNibble = (byte >> 4) & 0x0F;
      const lowNibble = byte & 0x0F;
      result += String.fromCodePoint(VS_RANGES.VS1_START + highNibble);
      result += String.fromCodePoint(VS_RANGES.VS1_START + lowNibble);
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
  it('should extract bytes from VS1 nibbles', () => {
    // Embed byte 0x43 ('C') using two VS1 characters
    const text = 'A' + String.fromCodePoint(0xFE04) + String.fromCodePoint(0xFE03);
    const bytes = extractEmbeddedBytes(text);
    assert.strictEqual(bytes.length, 1);
    assert.strictEqual(bytes[0], 0x43);
  });

  it('should extract bytes from VS2 range', () => {
    // Embed byte 0x43 using VS2 character
    const text = 'A' + String.fromCodePoint(0xE0100 + 0x43);
    const bytes = extractEmbeddedBytes(text);
    assert.strictEqual(bytes.length, 1);
    assert.strictEqual(bytes[0], 0x43);
  });

  it('should return empty array for plain text', () => {
    const bytes = extractEmbeddedBytes('Hello World');
    assert.strictEqual(bytes.length, 0);
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
