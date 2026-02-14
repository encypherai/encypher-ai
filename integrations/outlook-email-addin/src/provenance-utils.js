const VS_RANGES = {
  VS1_START: 0xfe00,
  VS1_END: 0xfe0f,
  VS2_START: 0xe0100,
  VS2_END: 0xe01ef,
};

const ZWNBSP = 0xfeff;
const ZWNJ = 0x200c;
const ZWJ = 0x200d;
const CGJ = 0x034f;
const MVS = 0x180e;
const ZERO_WIDTH_SET = new Set([ZWNJ, ZWJ, CGJ, MVS]);

function isVariationSelector(codePoint) {
  return (
    (codePoint >= VS_RANGES.VS1_START && codePoint <= VS_RANGES.VS1_END) ||
    (codePoint >= VS_RANGES.VS2_START && codePoint <= VS_RANGES.VS2_END)
  );
}

function isZeroWidthBase4Char(codePoint) {
  return ZERO_WIDTH_SET.has(codePoint);
}

function isEmbeddingChar(codePoint) {
  return codePoint === ZWNBSP || isVariationSelector(codePoint) || isZeroWidthBase4Char(codePoint);
}

function stripEmbeddingChars(text) {
  let result = '';
  for (const ch of text || '') {
    const cp = ch.codePointAt(0);
    if (!isEmbeddingChar(cp)) {
      result += ch;
    }
  }
  return result;
}

function extractVariationSelectorRuns(text) {
  const chars = [...(text || '')];
  const runs = [];
  let i = 0;

  while (i < chars.length) {
    const cp = chars[i].codePointAt(0);
    if (!(isVariationSelector(cp) || cp === ZWNBSP)) {
      i += 1;
      continue;
    }

    const start = i;
    const bytes = [];
    while (i < chars.length) {
      const current = chars[i].codePointAt(0);
      if (current >= VS_RANGES.VS1_START && current <= VS_RANGES.VS1_END) {
        bytes.push(current - VS_RANGES.VS1_START);
        i += 1;
        continue;
      }
      if (current >= VS_RANGES.VS2_START && current <= VS_RANGES.VS2_END) {
        bytes.push(current - VS_RANGES.VS2_START + 16);
        i += 1;
        continue;
      }
      if (current === ZWNBSP) {
        i += 1;
        continue;
      }
      break;
    }

    runs.push({ start, end: i, bytes, raw: chars.slice(start, i).join('') });
  }

  return runs;
}

function extractZeroWidthRuns(text) {
  const chars = [...(text || '')];
  const runs = [];
  let i = 0;

  while (i < chars.length) {
    const cp = chars[i].codePointAt(0);
    if (!isZeroWidthBase4Char(cp)) {
      i += 1;
      continue;
    }

    const start = i;
    while (i < chars.length && isZeroWidthBase4Char(chars[i].codePointAt(0))) {
      i += 1;
    }

    runs.push({ start, end: i, length: i - start, raw: chars.slice(start, i).join('') });
  }

  return runs;
}

function hashText(text) {
  let hash = 0;
  for (let i = 0; i < text.length; i += 1) {
    hash = (hash << 5) - hash + text.charCodeAt(i);
    hash |= 0;
  }
  return hash.toString(16);
}

const ProvenanceUtils = {
  VS_RANGES,
  ZWNBSP,
  isVariationSelector,
  isZeroWidthBase4Char,
  isEmbeddingChar,
  stripEmbeddingChars,
  extractVariationSelectorRuns,
  extractZeroWidthRuns,
  hashText,
};

if (typeof globalThis !== 'undefined') {
  globalThis.EmailProvenanceUtils = ProvenanceUtils;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = ProvenanceUtils;
}
