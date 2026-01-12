/**
 * Tests for c2pa-text TypeScript implementation
 */
import { embedManifest, extractManifest, encodeWrapper } from './index';

// Test data - minimal valid JUMBF box
const TEST_MANIFEST = new Uint8Array([0x00, 0x00, 0x00, 0x10, 0x6a, 0x75, 0x6d, 0x62, 0x00, 0x00, 0x00, 0x08, 0x63, 0x32, 0x70, 0x61]);
const TEST_TEXT = 'Hello, World!';

describe('c2pa-text', () => {
  describe('embedManifest', () => {
    it('should embed manifest into text', () => {
      const result = embedManifest(TEST_TEXT, TEST_MANIFEST);
      expect(result).toContain(TEST_TEXT);
      expect(result.length).toBeGreaterThan(TEST_TEXT.length);
    });

    it('should handle empty text', () => {
      const result = embedManifest('', TEST_MANIFEST);
      expect(result.length).toBeGreaterThan(0);
    });
  });

  describe('extractManifest', () => {
    it('should extract manifest from embedded text', () => {
      const embedded = embedManifest(TEST_TEXT, TEST_MANIFEST);
      const result = extractManifest(embedded);
      
      expect(result).not.toBeNull();
      if (result) {
        expect(result.manifest).toEqual(TEST_MANIFEST);
        expect(result.cleanText).toBe(TEST_TEXT);
        expect(result.offset).toBeDefined();
        expect(result.length).toBeDefined();
      }
    });

    it('should return null for plain text', () => {
      const result = extractManifest(TEST_TEXT);
      expect(result).toBeNull();
    });
  });

  describe('encodeWrapper', () => {
    it('should encode manifest bytes to wrapper string', () => {
      const wrapper = encodeWrapper(TEST_MANIFEST);
      // Wrapper should start with ZWNBSP
      expect(wrapper.charCodeAt(0)).toBe(0xFEFF);
      expect(wrapper.length).toBeGreaterThan(1);
    });
  });

  describe('roundtrip', () => {
    it('should preserve manifest through embed/extract cycle', () => {
      const embedded = embedManifest(TEST_TEXT, TEST_MANIFEST);
      const result = extractManifest(embedded);
      
      expect(result).not.toBeNull();
      if (result) {
        expect(result.manifest).toEqual(TEST_MANIFEST);
        expect(result.cleanText).toBe(TEST_TEXT);
      }
    });

    it('should handle unicode text', () => {
      const unicodeText = 'Hello 世界! 🌍';
      const embedded = embedManifest(unicodeText, TEST_MANIFEST);
      const result = extractManifest(embedded);
      
      expect(result).not.toBeNull();
      if (result) {
        expect(result.manifest).toEqual(TEST_MANIFEST);
        // NFC normalization may change the text slightly
        expect(result.cleanText.normalize('NFC')).toBe(unicodeText.normalize('NFC'));
      }
    });
  });
});
