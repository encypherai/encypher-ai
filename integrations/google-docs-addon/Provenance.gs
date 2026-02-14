var VS_RANGES_ = {
  VS1_START: 0xfe00,
  VS1_END: 0xfe0f,
  VS2_START: 0xe0100,
  VS2_END: 0xe01ef,
};
var ZWNBSP_ = 0xfeff;

function isVariationSelector_(codePoint) {
  return (
    (codePoint >= VS_RANGES_.VS1_START && codePoint <= VS_RANGES_.VS1_END) ||
    (codePoint >= VS_RANGES_.VS2_START && codePoint <= VS_RANGES_.VS2_END)
  );
}

function isEmbeddingChar_(codePoint) {
  return codePoint === ZWNBSP_ || isVariationSelector_(codePoint);
}

function stripEmbeddingChars_(text) {
  var result = '';
  var chars = Array.from(text || '');
  for (var i = 0; i < chars.length; i += 1) {
    var cp = chars[i].codePointAt(0);
    if (!isEmbeddingChar_(cp)) {
      result += chars[i];
    }
  }
  return result;
}

function hashText_(text) {
  var hash = 0;
  for (var i = 0; i < text.length; i += 1) {
    hash = (hash << 5) - hash + text.charCodeAt(i);
    hash |= 0;
  }
  return String(hash.toString(16));
}

function extractEmbeddingRuns_(text) {
  var chars = Array.from(text || '');
  var runs = [];
  var i = 0;

  while (i < chars.length) {
    var cp = chars[i].codePointAt(0);
    if (!isEmbeddingChar_(cp)) {
      i += 1;
      continue;
    }

    var start = i;
    var bytes = [];
    while (i < chars.length && isEmbeddingChar_(chars[i].codePointAt(0))) {
      var current = chars[i].codePointAt(0);
      if (current >= VS_RANGES_.VS1_START && current <= VS_RANGES_.VS1_END) {
        bytes.push(current - VS_RANGES_.VS1_START);
      } else if (current >= VS_RANGES_.VS2_START && current <= VS_RANGES_.VS2_END) {
        bytes.push(current - VS_RANGES_.VS2_START + 16);
      }
      i += 1;
    }

    runs.push({
      start: start,
      end: i,
      bytes: bytes,
      raw: chars.slice(start, i).join(''),
    });
  }

  return runs;
}

function provenanceKeyForHash_(visibleHash) {
  return ENCYPHER_CONFIG.PROPERTY_DOC_PROVENANCE_PREFIX + visibleHash;
}

function getProvenanceForHash_(visibleHash) {
  var docProps = getDocumentProperties_();
  var raw = docProps.getProperty(provenanceKeyForHash_(visibleHash));
  if (!raw) {
    return [];
  }
  try {
    var parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    return [];
  }
}

function storeProvenanceRuns_(visibleHash, runs, metadata) {
  if (!runs || runs.length === 0) {
    return;
  }

  var entries = getProvenanceForHash_(visibleHash);
  var now = new Date().toISOString();
  for (var i = 0; i < runs.length; i += 1) {
    if (!runs[i].bytes || runs[i].bytes.length === 0) {
      continue;
    }
    entries.push({
      bytes: runs[i].bytes,
      timestamp: now,
      source: metadata && metadata.source ? metadata.source : 'unknown',
      userEmail: Session.getActiveUser().getEmail() || '',
    });
  }

  if (entries.length > ENCYPHER_CONFIG.MAX_PROVENANCE_ENTRIES_PER_HASH) {
    entries = entries.slice(-ENCYPHER_CONFIG.MAX_PROVENANCE_ENTRIES_PER_HASH);
  }

  var docProps = getDocumentProperties_();
  docProps.setProperty(provenanceKeyForHash_(visibleHash), JSON.stringify(entries));

  trimDocumentProvenanceKeys_();
}

function trimDocumentProvenanceKeys_() {
  var docProps = getDocumentProperties_();
  var all = docProps.getProperties();
  var keys = Object.keys(all).filter(function(key) {
    return key.indexOf(ENCYPHER_CONFIG.PROPERTY_DOC_PROVENANCE_PREFIX) === 0;
  });

  if (keys.length <= ENCYPHER_CONFIG.MAX_PROVENANCE_KEYS_PER_DOC) {
    return;
  }

  var keyTimes = keys.map(function(key) {
    var entries;
    try {
      entries = JSON.parse(all[key] || '[]');
    } catch (err) {
      entries = [];
    }
    var last = entries.length > 0 ? entries[entries.length - 1] : null;
    var ts = last && last.timestamp ? new Date(last.timestamp).getTime() : 0;
    return { key: key, ts: ts };
  });

  keyTimes.sort(function(a, b) {
    return a.ts - b.ts;
  });

  var deleteCount = keyTimes.length - ENCYPHER_CONFIG.MAX_PROVENANCE_KEYS_PER_DOC;
  for (var i = 0; i < deleteCount; i += 1) {
    docProps.deleteProperty(keyTimes[i].key);
  }
}
