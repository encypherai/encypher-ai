const test = require('node:test');
const assert = require('node:assert/strict');

const { getHostCapabilities } = require('../src/host-capabilities');

test('word host supports selection and full-document actions', () => {
  const caps = getHostCapabilities('Word');
  assert.equal(caps.canReadSelection, true);
  assert.equal(caps.canReplaceSelection, true);
  assert.equal(caps.canReadFullDocument, true);
  assert.equal(caps.canReplaceFullDocument, true);
});

test('excel host supports selection actions and no full-document replace', () => {
  const caps = getHostCapabilities('Excel');
  assert.equal(caps.canReadSelection, true);
  assert.equal(caps.canReplaceSelection, true);
  assert.equal(caps.canReadFullDocument, false);
  assert.equal(caps.canReplaceFullDocument, false);
});

test('powerpoint host supports selection actions and no full-document replace', () => {
  const caps = getHostCapabilities('PowerPoint');
  assert.equal(caps.canReadSelection, true);
  assert.equal(caps.canReplaceSelection, true);
  assert.equal(caps.canReadFullDocument, false);
  assert.equal(caps.canReplaceFullDocument, false);
});

test('unknown host returns safe defaults', () => {
  const caps = getHostCapabilities('Outlook');
  assert.equal(caps.canReadSelection, false);
  assert.equal(caps.canReplaceSelection, false);
  assert.equal(caps.canReadFullDocument, false);
  assert.equal(caps.canReplaceFullDocument, false);
});
