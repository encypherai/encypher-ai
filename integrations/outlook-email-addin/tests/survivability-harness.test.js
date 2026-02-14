const test = require('node:test');
const assert = require('node:assert/strict');

const {
  runSurvivabilityMatrix,
  generateMicroEccMarker,
  generateZeroWidthMarker,
} = require('../src/survivability-harness');

test('marker generators produce expected lengths', () => {
  assert.equal([...generateMicroEccMarker()].length, 44);
  assert.equal([...generateZeroWidthMarker()].length, 132);
});

test('survivability matrix keeps both methods under identity transform', () => {
  const report = runSurvivabilityMatrix('Email test sentence.');
  assert.equal(report.matrix.identity.micro_ecc_c2pa.survives, true);
  assert.equal(report.matrix.identity.zero_width.survives, true);
});

test('supplementary VS stripping harms micro_ecc more than zero-width', () => {
  const report = runSurvivabilityMatrix('Email test sentence.');
  assert.equal(report.matrix.strip_supplementary_vs.zero_width.survives, true);
});

test('format-control stripping removes zero-width markers', () => {
  const report = runSurvivabilityMatrix('Email test sentence.');
  assert.equal(report.matrix.strip_format_controls.zero_width.survives, false);
});

test('variation-selector stripping removes micro_ecc markers', () => {
  const report = runSurvivabilityMatrix('Email test sentence.');
  assert.equal(report.matrix.strip_all_variation_selectors.micro_ecc_c2pa.survives, false);
});
