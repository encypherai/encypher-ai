/**
 * Tests for the VS256 marker detection utility.
 *
 * These tests verify client-side marker detection without requiring
 * any server-side infrastructure or node_modules beyond Jest.
 */

import {
  detectMarkers,
  stripMarkers,
  segmentText,
  summarizeMarkers,
  type DetectedMarker,
  type MarkerSummary,
} from '@/lib/marker-detector';

// ---------------------------------------------------------------------------
// Helpers — build VS256 encoded strings in JS (mirrors Python vs256_crypto)
// ---------------------------------------------------------------------------

const VS_BMP_START = 0xfe00;
const VS_SUPP_START = 0xe0100;

function byteToVs(byte: number): string {
  if (byte < 16) return String.fromCodePoint(VS_BMP_START + byte);
  return String.fromCodePoint(VS_SUPP_START + byte - 16);
}

function bytesToVs(bytes: number[]): string {
  return bytes.map(byteToVs).join('');
}

/** Build a fake micro marker (36 VS chars): magic(4) + uuid(16) + hmac(16) */
function buildMicroMarker(uuidBytes?: number[], hmacBytes?: number[]): string {
  const magic = [239, 240, 241, 242];
  const uuid = uuidBytes || Array.from({ length: 16 }, (_, i) => i);
  const hmac = hmacBytes || Array.from({ length: 16 }, (_, i) => i + 100);
  return bytesToVs([...magic, ...uuid, ...hmac]);
}

/** Build a fake micro_ecc marker (44 VS chars): magic(4) + uuid(16) + hmac(16) + rs(8) */
function buildMicroEccMarker(
  uuidBytes?: number[],
  hmacBytes?: number[],
  rsBytes?: number[]
): string {
  const magic = [239, 240, 241, 242];
  const uuid = uuidBytes || Array.from({ length: 16 }, (_, i) => i);
  const hmac = hmacBytes || Array.from({ length: 16 }, (_, i) => i + 100);
  const rs = rsBytes || Array.from({ length: 8 }, (_, i) => i + 200);
  return bytesToVs([...magic, ...uuid, ...hmac, ...rs]);
}

/** Build a short VS block that doesn't match any known format */
function buildUnknownVsBlock(length: number): string {
  const magic = [239, 240, 241, 242];
  const payload = Array.from({ length: length - 4 }, (_, i) => i % 256);
  return bytesToVs([...magic, ...payload]);
}

// ---------------------------------------------------------------------------
// detectMarkers
// ---------------------------------------------------------------------------

describe('detectMarkers', () => {
  it('returns empty array for plain text', () => {
    const markers = detectMarkers('Hello world. This is plain text.');
    expect(markers).toHaveLength(0);
  });

  it('detects a single micro marker (36 chars)', () => {
    const marker = buildMicroMarker();
    const text = `First sentence.${marker} Second sentence.`;
    const detected = detectMarkers(text);

    expect(detected).toHaveLength(1);
    expect(detected[0].type).toBe('micro');
    expect(detected[0].charCount).toBe(36);
    expect(detected[0].uuid).toBeTruthy();
    expect(detected[0].hmac).toBeTruthy();
    expect(detected[0].rsParity).toBeNull();
  });

  it('detects a single micro_ecc marker (44 chars)', () => {
    const marker = buildMicroEccMarker();
    const text = `First sentence.${marker} Second sentence.`;
    const detected = detectMarkers(text);

    expect(detected).toHaveLength(1);
    expect(detected[0].type).toBe('micro_ecc');
    expect(detected[0].charCount).toBe(44);
    expect(detected[0].uuid).toBeTruthy();
    expect(detected[0].hmac).toBeTruthy();
    expect(detected[0].rsParity).toBeTruthy();
  });

  it('detects multiple markers in multi-sentence text', () => {
    const m1 = buildMicroMarker();
    const m2 = buildMicroMarker(
      Array.from({ length: 16 }, () => 0xaa),
      Array.from({ length: 16 }, () => 0xbb)
    );
    const m3 = buildMicroEccMarker();

    const text = `Sentence one.${m1} Sentence two.${m2} Sentence three.${m3}`;
    const detected = detectMarkers(text);

    expect(detected).toHaveLength(3);
    expect(detected[0].type).toBe('micro');
    expect(detected[1].type).toBe('micro');
    expect(detected[2].type).toBe('micro_ecc');

    // Indices should be sequential
    expect(detected[0].index).toBe(0);
    expect(detected[1].index).toBe(1);
    expect(detected[2].index).toBe(2);
  });

  it('correctly parses UUID from marker bytes', () => {
    // UUID bytes: 0x01234567-89ab-cdef-0123-456789abcdef
    const uuidBytes = [0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef, 0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef];
    const marker = buildMicroMarker(uuidBytes);
    const text = `Test.${marker}`;
    const detected = detectMarkers(text);

    expect(detected).toHaveLength(1);
    expect(detected[0].uuid).toBe('01234567-89ab-cdef-0123-456789abcdef');
  });

  it('returns associated text for each marker', () => {
    const m1 = buildMicroMarker();
    const m2 = buildMicroMarker(Array.from({ length: 16 }, () => 0xff));
    const text = `Hello world.${m1} Goodbye world.${m2}`;
    const detected = detectMarkers(text);

    expect(detected).toHaveLength(2);
    expect(detected[0].associatedText).toBe('Hello world.');
    expect(detected[1].associatedText).toBe('Goodbye world.');
  });

  it('adjacent markers with no gap merge into one VS block', () => {
    const m1 = buildMicroMarker();
    const m2 = buildMicroEccMarker();
    // No visible chars between them — they form one contiguous VS block
    const text = `${m1}${m2}`;
    const detected = detectMarkers(text);
    expect(detected).toHaveLength(1); // merged into single block
  });

  it('markers separated by a space are detected individually', () => {
    const m1 = buildMicroMarker();
    const m2 = buildMicroEccMarker();
    const text = `${m1} ${m2}`;
    const detected = detectMarkers(text);
    expect(detected).toHaveLength(2);
    expect(detected[0].type).toBe('micro');
    expect(detected[1].type).toBe('micro_ecc');
  });

  it('classifies unknown-length magic-prefixed blocks as unknown', () => {
    // 4 magic + 20 payload = 24 chars (not 36 or 44)
    const block = buildUnknownVsBlock(24);
    const text = `Test.${block}`;
    const detected = detectMarkers(text);

    expect(detected).toHaveLength(1);
    expect(detected[0].type).toBe('unknown');
  });
});

// ---------------------------------------------------------------------------
// stripMarkers
// ---------------------------------------------------------------------------

describe('stripMarkers', () => {
  it('returns plain text unchanged', () => {
    expect(stripMarkers('Hello world.')).toBe('Hello world.');
  });

  it('removes micro markers from text', () => {
    const marker = buildMicroMarker();
    const text = `Hello.${marker} World.`;
    expect(stripMarkers(text)).toBe('Hello. World.');
  });

  it('removes multiple markers', () => {
    const m1 = buildMicroMarker();
    const m2 = buildMicroEccMarker();
    const text = `A.${m1} B.${m2} C.`;
    expect(stripMarkers(text)).toBe('A. B. C.');
  });

  it('handles text that is only markers', () => {
    const marker = buildMicroMarker();
    expect(stripMarkers(marker)).toBe('');
  });
});

// ---------------------------------------------------------------------------
// segmentText
// ---------------------------------------------------------------------------

describe('segmentText', () => {
  it('returns single text segment for plain text', () => {
    const segments = segmentText('Hello world.');
    expect(segments).toHaveLength(1);
    expect(segments[0].type).toBe('text');
    expect(segments[0].content).toBe('Hello world.');
  });

  it('interleaves text and marker segments', () => {
    const marker = buildMicroMarker();
    const text = `First.${marker} Second.`;
    const segments = segmentText(text);

    // Should be: text("First."), marker, text(" Second.")
    expect(segments.length).toBeGreaterThanOrEqual(2);

    const textSegments = segments.filter((s) => s.type === 'text');
    const markerSegments = segments.filter((s) => s.type === 'marker');

    expect(textSegments.length).toBeGreaterThanOrEqual(1);
    expect(markerSegments).toHaveLength(1);
    expect(markerSegments[0].marker).toBeDefined();
    expect(markerSegments[0].marker!.type).toBe('micro');
  });

  it('handles multiple markers correctly', () => {
    const m1 = buildMicroMarker();
    const m2 = buildMicroEccMarker();
    const text = `A.${m1} B.${m2} C.`;
    const segments = segmentText(text);

    const markerSegments = segments.filter((s) => s.type === 'marker');
    expect(markerSegments).toHaveLength(2);
  });
});

// ---------------------------------------------------------------------------
// summarizeMarkers
// ---------------------------------------------------------------------------

describe('summarizeMarkers', () => {
  it('returns zero counts for empty array', () => {
    const summary = summarizeMarkers([]);
    expect(summary.total).toBe(0);
    expect(summary.micro).toBe(0);
    expect(summary.microEcc).toBe(0);
  });

  it('counts marker types correctly', () => {
    const m1 = buildMicroMarker();
    const m2 = buildMicroMarker(Array.from({ length: 16 }, () => 0xaa));
    const m3 = buildMicroEccMarker();
    const text = `A.${m1} B.${m2} C.${m3}`;
    const markers = detectMarkers(text);
    const summary = summarizeMarkers(markers);

    expect(summary.total).toBe(3);
    expect(summary.micro).toBe(2);
    expect(summary.microEcc).toBe(1);
    expect(summary.basic).toBe(0);
    expect(summary.c2pa).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// Edge cases
// ---------------------------------------------------------------------------

describe('edge cases', () => {
  it('handles empty string', () => {
    expect(detectMarkers('')).toHaveLength(0);
    expect(stripMarkers('')).toBe('');
    expect(segmentText('')).toHaveLength(1);
  });

  it('handles emoji text (which uses VS16 / U+FE0F)', () => {
    // Emoji variation selectors are single chars (VS1-VS16), not contiguous blocks of 4+
    // They should NOT be detected as markers
    const text = 'Hello 👋\uFE0F world!';
    const markers = detectMarkers(text);
    // A single VS char is below the min_length threshold of 4
    expect(markers).toHaveLength(0);
  });

  it('handles unicode text with markers', () => {
    const marker = buildMicroMarker();
    const text = `日本語のテスト。${marker} 中文测试。`;
    const detected = detectMarkers(text);

    expect(detected).toHaveLength(1);
    expect(detected[0].type).toBe('micro');
    expect(stripMarkers(text)).toBe('日本語のテスト。 中文测试。');
  });

  it('preserves marker start/end indices correctly', () => {
    const marker = buildMicroMarker();
    const prefix = 'Hello.';
    const text = `${prefix}${marker} World.`;
    const detected = detectMarkers(text);

    expect(detected).toHaveLength(1);
    expect(detected[0].startIndex).toBe(prefix.length);
    // endIndex should be startIndex + number of JS char units in the marker
    expect(detected[0].endIndex).toBeGreaterThan(detected[0].startIndex);
  });
});
