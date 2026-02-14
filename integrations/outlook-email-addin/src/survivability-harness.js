const { stripEmbeddingChars, extractVariationSelectorRuns, extractZeroWidthRuns } = require('./provenance-utils');

const ZWNJ = '\u200C';
const VS1 = '\uFE00';
const VS_SUPP = String.fromCodePoint(0xE0100);
const MICRO_ECC_MAGIC = [
  String.fromCodePoint(0xE018F),
  String.fromCodePoint(0xE0190),
  String.fromCodePoint(0xE0191),
  String.fromCodePoint(0xE0192),
].join('');

function generateMicroEccMarker(length = 44) {
  const magicLen = [...MICRO_ECC_MAGIC].length;
  const payloadLen = Math.max(0, length - magicLen);
  const chars = [VS1, VS_SUPP];
  let payload = '';
  for (let i = 0; i < payloadLen; i += 1) {
    payload += chars[i % chars.length];
  }
  return MICRO_ECC_MAGIC + payload;
}

function generateZeroWidthMarker(length = 132) {
  return ZWNJ.repeat(length);
}

function embedBeforePunctuation(text, marker) {
  return text.replace(/([.!?])$/, marker + '$1');
}

function transformIdentity(text) {
  return text;
}

function transformUnicodeNfc(text) {
  return text.normalize('NFC');
}

function transformStripSupplementaryVS(text) {
  return [...text]
    .filter((ch) => {
      const cp = ch.codePointAt(0);
      return !(cp >= 0xE0100 && cp <= 0xE01EF);
    })
    .join('');
}

function transformStripVariationSelectors(text) {
  return [...text]
    .filter((ch) => {
      const cp = ch.codePointAt(0);
      return !((cp >= 0xFE00 && cp <= 0xFE0F) || (cp >= 0xE0100 && cp <= 0xE01EF));
    })
    .join('');
}

function transformStripFormatControls(text) {
  // Typical aggressive sanitizer behavior against Cf invisibles.
  return text
    .replace(/[\u200C\u200D\u200B\u200E\u200F\u2060\u180E\uFEFF]/g, '')
    .replace(/[\u034F]/g, '');
}

function analyze(text) {
  return {
    visibleText: stripEmbeddingChars(text),
    variationRuns: extractVariationSelectorRuns(text),
    zeroWidthRuns: extractZeroWidthRuns(text),
  };
}

function runSurvivabilityMatrix(baseVisibleText) {
  const visible = baseVisibleText || 'Email body sentence for survivability testing.';

  const microEccEmbedded = embedBeforePunctuation(visible, generateMicroEccMarker());
  const zeroWidthEmbedded = embedBeforePunctuation(visible, generateZeroWidthMarker());

  const processors = {
    identity: transformIdentity,
    unicode_nfc: transformUnicodeNfc,
    strip_supplementary_vs: transformStripSupplementaryVS,
    strip_all_variation_selectors: transformStripVariationSelectors,
    strip_format_controls: transformStripFormatControls,
  };

  const matrix = {};

  for (const [name, processor] of Object.entries(processors)) {
    const microOut = processor(microEccEmbedded);
    const zwOut = processor(zeroWidthEmbedded);

    const microAnalysis = analyze(microOut);
    const zwAnalysis = analyze(zwOut);
    const microLongest = microAnalysis.variationRuns.reduce((max, run) => Math.max(max, run.end - run.start), 0);
    const zwLongest = zwAnalysis.zeroWidthRuns.reduce((max, run) => Math.max(max, run.length), 0);

    matrix[name] = {
      micro_ecc_c2pa: {
        variationRunCount: microAnalysis.variationRuns.length,
        longestVariationRunLength: microLongest,
        survives: microLongest >= 44,
      },
      zero_width: {
        zeroWidthRunCount: zwAnalysis.zeroWidthRuns.length,
        longestZeroWidthRunLength: zwLongest,
        survives: zwLongest >= 128,
      },
    };
  }

  return {
    baseVisibleText: visible,
    matrix,
  };
}

module.exports = {
  generateMicroEccMarker,
  generateZeroWidthMarker,
  runSurvivabilityMatrix,
  transformIdentity,
  transformUnicodeNfc,
  transformStripSupplementaryVS,
  transformStripVariationSelectors,
  transformStripFormatControls,
};
