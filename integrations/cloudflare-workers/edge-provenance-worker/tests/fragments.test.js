import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { extractFragments, assembleText, decodeHtmlEntities, hashText } from '../src/fragments.js';

describe('extractFragments', () => {
  it('extracts text from simple HTML', () => {
    const frags = extractFragments('<p>Hello world</p>');
    assert.equal(frags.length, 1);
    assert.equal(frags[0].rawText, 'Hello world');
  });

  it('extracts multiple fragments', () => {
    const frags = extractFragments('<p>First</p><p>Second</p>');
    assert.equal(frags.length, 2);
    assert.equal(frags[0].rawText, 'First');
    assert.equal(frags[1].rawText, 'Second');
  });

  it('skips script content', () => {
    const frags = extractFragments('<p>Visible</p><script>hidden();</script><p>Also visible</p>');
    assert.equal(frags.length, 2);
    assert.equal(frags[0].rawText, 'Visible');
    assert.equal(frags[1].rawText, 'Also visible');
  });

  it('skips style content', () => {
    const frags = extractFragments('<p>Text</p><style>.cls{color:red}</style>');
    assert.equal(frags.length, 1);
  });

  it('skips code content', () => {
    const frags = extractFragments('<p>Text</p><code>const x = 1;</code><p>More</p>');
    assert.equal(frags.length, 2);
  });

  it('preserves inline element text', () => {
    const frags = extractFragments('<p>Hello <em>world</em> today</p>');
    // Fragments between tags: "Hello ", "world", " today"
    assert.ok(frags.length >= 2);
    const text = assembleText(frags);
    assert.ok(text.includes('Hello'));
    assert.ok(text.includes('world'));
    assert.ok(text.includes('today'));
  });

  it('tracks byte offsets correctly', () => {
    const html = '<p>ABC</p>';
    const frags = extractFragments(html);
    assert.equal(frags.length, 1);
    assert.equal(frags[0].byteOffset, 3); // after "<p>"
    assert.equal(frags[0].byteLength, 3); // "ABC"
  });

  it('handles HTML comments', () => {
    const frags = extractFragments('<p>Before</p><!-- comment --><p>After</p>');
    assert.equal(frags.length, 2);
  });

  it('handles empty input', () => {
    const frags = extractFragments('');
    assert.equal(frags.length, 0);
  });

  it('handles whitespace-only text nodes', () => {
    const frags = extractFragments('<div>  </div><p>Text</p>');
    assert.equal(frags.length, 1);
    assert.equal(frags[0].rawText, 'Text');
  });

  it('handles entities in fragments', () => {
    const frags = extractFragments('<p>Tom &amp; Jerry</p>');
    assert.equal(frags.length, 1);
    assert.equal(frags[0].rawText, 'Tom &amp; Jerry');
    // Raw text still has entity; decoding happens in assembleText
    const text = assembleText(frags);
    assert.equal(text, 'Tom & Jerry');
  });
});

describe('assembleText', () => {
  it('joins fragments with spaces', () => {
    const frags = [
      { rawText: 'First paragraph.', byteOffset: 0, byteLength: 0 },
      { rawText: 'Second paragraph.', byteOffset: 0, byteLength: 0 },
    ];
    assert.equal(assembleText(frags), 'First paragraph. Second paragraph.');
  });

  it('trims and normalizes whitespace', () => {
    const frags = [
      { rawText: '  Hello   world  ', byteOffset: 0, byteLength: 0 },
    ];
    assert.equal(assembleText(frags), 'Hello world');
  });

  it('skips empty fragments', () => {
    const frags = [
      { rawText: '  ', byteOffset: 0, byteLength: 0 },
      { rawText: 'Content', byteOffset: 0, byteLength: 0 },
    ];
    assert.equal(assembleText(frags), 'Content');
  });
});

describe('decodeHtmlEntities', () => {
  it('decodes named entities', () => {
    assert.equal(decodeHtmlEntities('&amp;'), '&');
    assert.equal(decodeHtmlEntities('&lt;'), '<');
    assert.equal(decodeHtmlEntities('&gt;'), '>');
    assert.equal(decodeHtmlEntities('&quot;'), '"');
    assert.equal(decodeHtmlEntities('&nbsp;'), '\u00A0');
  });

  it('decodes decimal numeric entities', () => {
    assert.equal(decodeHtmlEntities('&#8212;'), '\u2014'); // em dash
    assert.equal(decodeHtmlEntities('&#65;'), 'A');
  });

  it('decodes hex numeric entities', () => {
    assert.equal(decodeHtmlEntities('&#x2014;'), '\u2014'); // em dash
    assert.equal(decodeHtmlEntities('&#x41;'), 'A');
  });

  it('leaves unknown entities unchanged', () => {
    assert.equal(decodeHtmlEntities('&unknown;'), '&unknown;');
  });
});

describe('hashText', () => {
  it('returns sha256-prefixed hash', async () => {
    const hash = await hashText('hello');
    assert.ok(hash.startsWith('sha256:'));
    assert.equal(hash.length, 71);
  });

  it('is deterministic', async () => {
    const h1 = await hashText('test');
    const h2 = await hashText('test');
    assert.equal(h1, h2);
  });

  it('differs for different input', async () => {
    const h1 = await hashText('foo');
    const h2 = await hashText('bar');
    assert.notEqual(h1, h2);
  });
});
