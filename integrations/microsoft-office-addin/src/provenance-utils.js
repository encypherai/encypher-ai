const VS_RANGES = {
  VS1_START: 0xfe00,
  VS1_END: 0xfe0f,
  VS2_START: 0xe0100,
  VS2_END: 0xe01ef,
};

const ZWNBSP = 0xfeff;

function isVariationSelector(codePoint) {
  return (
    (codePoint >= VS_RANGES.VS1_START && codePoint <= VS_RANGES.VS1_END) ||
    (codePoint >= VS_RANGES.VS2_START && codePoint <= VS_RANGES.VS2_END)
  );
}

function isEmbeddingChar(codePoint) {
  return codePoint === ZWNBSP || isVariationSelector(codePoint);
}

function stripEmbeddingChars(text) {
  let out = '';
  for (const ch of text || '') {
    const cp = ch.codePointAt(0);
    if (!isEmbeddingChar(cp)) {
      out += ch;
    }
  }
  return out;
}

function extractEmbeddingRuns(text) {
  const chars = [...(text || '')];
  const runs = [];
  let i = 0;

  while (i < chars.length) {
    if (!isEmbeddingChar(chars[i].codePointAt(0))) {
      i += 1;
      continue;
    }

    const start = i;
    const bytes = [];

    while (i < chars.length && isEmbeddingChar(chars[i].codePointAt(0))) {
      const cp = chars[i].codePointAt(0);
      if (cp >= VS_RANGES.VS1_START && cp <= VS_RANGES.VS1_END) {
        bytes.push(cp - VS_RANGES.VS1_START);
      } else if (cp >= VS_RANGES.VS2_START && cp <= VS_RANGES.VS2_END) {
        bytes.push(cp - VS_RANGES.VS2_START + 16);
      }
      i += 1;
    }

    runs.push({
      start,
      end: i,
      bytes,
      raw: chars.slice(start, i).join(''),
    });
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

function mergeProvenanceEntries(existingEntries, extractedRuns, maxEntries) {
  const merged = Array.isArray(existingEntries) ? existingEntries.slice() : [];

  for (const run of extractedRuns || []) {
    if (!run.bytes || run.bytes.length === 0) {
      continue;
    }

    merged.push({
      bytes: run.bytes,
      timestamp: Date.now(),
    });
  }

  if (maxEntries && merged.length > maxEntries) {
    return merged.slice(-maxEntries);
  }

  return merged;
}

const ProvenanceUtils = {
  VS_RANGES,
  ZWNBSP,
  isVariationSelector,
  isEmbeddingChar,
  stripEmbeddingChars,
  extractEmbeddingRuns,
  hashText,
  mergeProvenanceEntries,
};

if (typeof globalThis !== 'undefined') {
  globalThis.ProvenanceUtils = ProvenanceUtils;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = ProvenanceUtils;
}
