(function (global) {
  const RUN_TEXT_REGEX = /(<w:t(?:\s[^>]*)?>)([\s\S]*?)(<\/w:t>)/g;
  const PARAGRAPH_REGEX = /<w:p\b[\s\S]*?<\/w:p>/g;

  function decodeXmlText(text) {
    return (text || '')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&apos;/g, "'")
      .replace(/&amp;/g, '&');
  }

  function encodeXmlText(text) {
    return (text || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function readRunTextsFromOoxml(ooxml) {
    const runs = [];
    let match;
    while ((match = RUN_TEXT_REGEX.exec(ooxml || '')) !== null) {
      runs.push(decodeXmlText(match[2]));
    }
    return runs;
  }

  function buildOoxmlTextModel(ooxml) {
    const runTexts = [];
    const paragraphs = [];
    let paragraphMatch;

    while ((paragraphMatch = PARAGRAPH_REGEX.exec(ooxml || '')) !== null) {
      const paragraphXml = paragraphMatch[0];
      const paragraphRunIndices = [];
      const paragraphRunRegex = /(<w:t(?:\s[^>]*)?>)([\s\S]*?)(<\/w:t>)/g;
      let runMatch;

      while ((runMatch = paragraphRunRegex.exec(paragraphXml)) !== null) {
        paragraphRunIndices.push(runTexts.length);
        runTexts.push(decodeXmlText(runMatch[2]));
      }

      if (paragraphRunIndices.length > 0) {
        paragraphs.push(paragraphRunIndices);
      }
    }

    if (runTexts.length === 0) {
      return {
        runTexts,
        visibleText: '',
        anchors: [],
      };
    }

    const chars = [];
    const anchors = [];

    for (let p = 0; p < paragraphs.length; p += 1) {
      const runIndices = paragraphs[p];
      for (const runIndex of runIndices) {
        let offset = 0;
        for (const ch of [...(runTexts[runIndex] || '')]) {
          offset += 1;
          chars.push(ch);
          anchors.push({ runIndex, offset });
        }
      }

      if (p < paragraphs.length - 1) {
        const lastRunIndex = runIndices[runIndices.length - 1];
        const lastRunLength = [...(runTexts[lastRunIndex] || '')].length;
        chars.push('\n');
        anchors.push({ runIndex: lastRunIndex, offset: lastRunLength });
      }
    }

    return {
      runTexts,
      visibleText: chars.join(''),
      anchors,
    };
  }

  function buildEmbeddingPlan(visibleText, signedText, isEmbeddingCharFn) {
    const visibleChars = [...(visibleText || '')];
    const signedChars = [...(signedText || '')];
    const after = Array(visibleChars.length).fill('');

    let visibleIndex = 0;
    let pending = '';
    let prefix = '';

    for (const ch of signedChars) {
      const cp = ch.codePointAt(0);
      if (isEmbeddingCharFn(cp)) {
        pending += ch;
        continue;
      }

      if (visibleIndex >= visibleChars.length || ch !== visibleChars[visibleIndex]) {
        return null;
      }

      if (visibleIndex === 0) {
        prefix += pending;
      } else if (pending) {
        after[visibleIndex - 1] += pending;
      }

      pending = '';
      visibleIndex += 1;
    }

    if (visibleIndex !== visibleChars.length) {
      return null;
    }

    return {
      prefix,
      suffix: pending,
      after,
    };
  }

  function applyEmbeddingPlanToRuns(runTexts, plan) {
    if (!plan || !Array.isArray(plan.after)) {
      return null;
    }

    const nextRuns = [];
    let visibleIndex = 0;
    let pendingPrefix = plan.prefix || '';

    for (const runText of runTexts || []) {
      let out = '';
      for (const ch of [...(runText || '')]) {
        out += pendingPrefix + ch;
        pendingPrefix = '';
        out += plan.after[visibleIndex] || '';
        visibleIndex += 1;
      }
      nextRuns.push(out);
    }

    if (visibleIndex !== plan.after.length) {
      return null;
    }

    if (nextRuns.length === 0) {
      return [pendingPrefix + (plan.suffix || '')];
    }

    nextRuns[nextRuns.length - 1] += pendingPrefix + (plan.suffix || '');
    return nextRuns;
  }

  function applyEmbeddingPlanWithAnchors(runTexts, plan, anchors) {
    if (!plan || !Array.isArray(plan.after) || !Array.isArray(anchors) || plan.after.length !== anchors.length) {
      return null;
    }

    if (!Array.isArray(runTexts) || runTexts.length === 0) {
      return null;
    }

    const inserts = Array.from({ length: runTexts.length }, () => new Map());

    const appendInsert = (runIndex, offset, value) => {
      if (!value) {
        return;
      }
      const map = inserts[runIndex];
      map.set(offset, (map.get(offset) || '') + value);
    };

    for (let i = 0; i < anchors.length; i += 1) {
      const marker = plan.after[i] || '';
      if (!marker) {
        continue;
      }
      const anchor = anchors[i];
      appendInsert(anchor.runIndex, anchor.offset, marker);
    }

    const firstAnchor = anchors[0];
    const lastAnchor = anchors[anchors.length - 1];
    if (firstAnchor) {
      appendInsert(firstAnchor.runIndex, 0, plan.prefix || '');
    }
    if (lastAnchor) {
      appendInsert(lastAnchor.runIndex, lastAnchor.offset, plan.suffix || '');
    }

    return runTexts.map((runText, runIndex) => {
      const chars = [...(runText || '')];
      const map = inserts[runIndex];
      let out = map.get(0) || '';
      for (let i = 0; i < chars.length; i += 1) {
        out += chars[i];
        const offset = i + 1;
        out += map.get(offset) || '';
      }
      return out;
    });
  }

  function extractVisibleTextFromOoxml(ooxml) {
    const model = buildOoxmlTextModel(ooxml);
    return model.visibleText;
  }

  function applySignedTextToOoxml(ooxml, signedText, isEmbeddingCharFn) {
    const model = buildOoxmlTextModel(ooxml);
    const runTexts = model.runTexts;
    if (runTexts.length === 0) {
      throw new Error('Unable to locate OOXML text runs for formatting-preserving signing.');
    }

    const visibleText = model.visibleText;
    const plan = buildEmbeddingPlan(visibleText, signedText, isEmbeddingCharFn);
    if (!plan) {
      throw new Error('Signed text does not align with visible OOXML text.');
    }

    const nextRuns = applyEmbeddingPlanWithAnchors(runTexts, plan, model.anchors);
    if (!nextRuns) {
      throw new Error('Unable to project signed embedding markers onto OOXML runs.');
    }

    let runIndex = 0;
    return (ooxml || '').replace(RUN_TEXT_REGEX, (full, openTag, runText, closeTag) => {
      const replacement = nextRuns[runIndex] || '';
      runIndex += 1;
      return openTag + encodeXmlText(replacement) + closeTag;
    });
  }

  function applyApiEmbeddingPlanToOoxml(ooxml, apiEmbeddingPlan) {
    const model = buildOoxmlTextModel(ooxml);
    const runTexts = model.runTexts;
    if (runTexts.length === 0) {
      throw new Error('Unable to locate OOXML text runs for formatting-preserving signing.');
    }

    if (!apiEmbeddingPlan || apiEmbeddingPlan.index_unit !== 'codepoint' || !Array.isArray(apiEmbeddingPlan.operations)) {
      throw new Error('Invalid API embedding plan payload.');
    }

    const after = Array(model.anchors.length).fill('');
    let prefix = '';
    let suffix = '';

    for (const operation of apiEmbeddingPlan.operations) {
      if (!operation || typeof operation.insert_after_index !== 'number' || typeof operation.marker !== 'string') {
        throw new Error('Invalid API embedding plan operation.');
      }

      if (operation.insert_after_index < -1 || operation.insert_after_index > model.anchors.length - 1) {
        throw new Error('API embedding plan operation index is out of bounds.');
      }

      if (operation.insert_after_index === -1) {
        prefix += operation.marker;
      } else if (operation.insert_after_index === model.anchors.length - 1) {
        after[operation.insert_after_index] += operation.marker;
      } else {
        after[operation.insert_after_index] += operation.marker;
      }
    }

    const plan = {
      prefix,
      suffix,
      after,
    };

    const nextRuns = applyEmbeddingPlanWithAnchors(runTexts, plan, model.anchors);
    if (!nextRuns) {
      throw new Error('Unable to project API embedding plan markers onto OOXML runs.');
    }

    let runIndex = 0;
    return (ooxml || '').replace(RUN_TEXT_REGEX, (full, openTag, runText, closeTag) => {
      const replacement = nextRuns[runIndex] || '';
      runIndex += 1;
      return openTag + encodeXmlText(replacement) + closeTag;
    });
  }

  const OoxmlFormatPreserving = {
    buildEmbeddingPlan,
    applyEmbeddingPlanToRuns,
    extractVisibleTextFromOoxml,
    applySignedTextToOoxml,
    applyApiEmbeddingPlanToOoxml,
  };

  if (typeof globalThis !== 'undefined') {
    globalThis.EncypherOoxmlFormatting = OoxmlFormatPreserving;
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = OoxmlFormatPreserving;
  }
})(typeof window !== 'undefined' ? window : globalThis);
