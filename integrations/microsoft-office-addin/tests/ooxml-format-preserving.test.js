const test = require('node:test');
const assert = require('node:assert/strict');

const {
  buildEmbeddingPlan,
  applyEmbeddingPlanToRuns,
  extractVisibleTextFromOoxml,
  applySignedTextToOoxml,
  applyApiEmbeddingPlanToOoxml,
} = require('../src/ooxml-format-preserving');
const { isEmbeddingChar } = require('../src/provenance-utils');

const SAMPLE_OOXML = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<pkg:package xmlns:pkg="http://schemas.microsoft.com/office/2006/xmlPackage">
  <pkg:part pkg:name="/word/document.xml" pkg:contentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml">
    <pkg:xmlData>
      <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
        <w:body>
          <w:p>
            <w:r><w:rPr><w:b/></w:rPr><w:t>Hel</w:t></w:r>
            <w:r><w:t>lo</w:t></w:r>
          </w:p>
          <w:p>
            <w:r><w:t>World</w:t></w:r>
          </w:p>
        </w:body>
      </w:document>
    </pkg:xmlData>
  </pkg:part>
</pkg:package>`;

test('buildEmbeddingPlan builds per-character embedding insertions', () => {
  const visible = 'abc';
  const signed = `a\u{fe00}b\u{fe01}\u{fe02}c`;

  const plan = buildEmbeddingPlan(visible, signed, isEmbeddingChar);

  assert.ok(plan);
  assert.equal(plan.prefix, '');
  assert.equal(plan.suffix, '');
  assert.deepEqual(plan.after, ['\u{fe00}', '\u{fe01}\u{fe02}', '']);
});

test('applyEmbeddingPlanToRuns preserves run boundaries while inserting markers', () => {
  const visible = 'abcdef';
  const signed = `ab\u{fe00}cd\u{fe01}ef`;
  const plan = buildEmbeddingPlan(visible, signed, isEmbeddingChar);
  const runs = ['abc', 'def'];

  const updated = applyEmbeddingPlanToRuns(runs, plan);

  assert.deepEqual(updated, ['ab\u{fe00}c', 'd\u{fe01}ef']);
});

test('buildEmbeddingPlan returns null when visible content does not align', () => {
  const plan = buildEmbeddingPlan('abc', 'abXc', isEmbeddingChar);
  assert.equal(plan, null);
});

test('extractVisibleTextFromOoxml reads text in run order', () => {
  const text = extractVisibleTextFromOoxml(SAMPLE_OOXML);
  assert.equal(text, 'Hello\nWorld');
});

test('applySignedTextToOoxml preserves XML structure and inserts embedding markers into runs', () => {
  const signedText = `Hel\u{fe00}lo\nWo\u{fe01}rld`;
  const next = applySignedTextToOoxml(SAMPLE_OOXML, signedText, isEmbeddingChar);

  assert.ok(next.includes('<w:b/>'));
  assert.ok(next.includes('Hel\u{fe00}</w:t>'));
  assert.ok(next.includes('Wo\u{fe01}rld</w:t>'));
});

test('applyApiEmbeddingPlanToOoxml applies codepoint operations without replacing visible text', () => {
  const plan = {
    index_unit: 'codepoint',
    operations: [
      { insert_after_index: 2, marker: '\u{fe00}' },
      { insert_after_index: 7, marker: '\u{fe01}' },
    ],
  };

  const next = applyApiEmbeddingPlanToOoxml(SAMPLE_OOXML, plan);

  assert.ok(next.includes('<w:b/>'));
  assert.ok(next.includes('Hel\u{fe00}</w:t>'));
  assert.ok(next.includes('Wo\u{fe01}rld</w:t>'));
});
