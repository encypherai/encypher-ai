import { describe, it, expect } from 'vitest';
import {
  extractText,
  extractFragments,
  applyEmbeddingPlan,
  embedEmbeddingPlanIntoHtml,
  embedSignedText,
  extractTextForVerify,
  isVsChar,
  isVsOrWhitespace,
  splitChars,
  stripC2paEmbeddings,
  detectC2paEmbeddings,
  extractBookmarkText,
  extractCalloutText,
  extractToggleText,
} from '../src/html-utils';

describe('html-utils', () => {
  // =========================================================================
  // extractText
  // =========================================================================
  describe('extractText', () => {
    it('extracts text from simple paragraphs', () => {
      const html = '<p>Hello world.</p><p>Second paragraph.</p>';
      expect(extractText(html)).toBe('Hello world. Second paragraph.');
    });

    it('extracts text from headings', () => {
      const html = '<h1>Title</h1><p>Body text here.</p>';
      expect(extractText(html)).toBe('Title Body text here.');
    });

    it('extracts text from nested inline elements', () => {
      const html = '<p>This is <strong>bold</strong> and <em>italic</em> text.</p>';
      expect(extractText(html)).toBe('This is bold and italic text.');
    });

    it('extracts text from lists', () => {
      const html = '<ul><li>Item one</li><li>Item two</li><li>Item three</li></ul>';
      const result = extractText(html);
      expect(result).toContain('Item one');
      expect(result).toContain('Item two');
      expect(result).toContain('Item three');
    });

    it('extracts text from tables', () => {
      const html = '<table><tr><td>Cell A</td><td>Cell B</td></tr><tr><td>Cell C</td><td>Cell D</td></tr></table>';
      const result = extractText(html);
      expect(result).toContain('Cell A');
      expect(result).toContain('Cell B');
      expect(result).toContain('Cell C');
      expect(result).toContain('Cell D');
    });

    it('extracts text from blockquotes', () => {
      const html = '<blockquote><p>A wise quote.</p></blockquote>';
      expect(extractText(html)).toBe('A wise quote.');
    });

    it('skips script and style elements', () => {
      const html = '<p>Visible text.</p><script>var x = 1;</script><style>.foo{}</style><p>More text.</p>';
      const result = extractText(html);
      expect(result).toBe('Visible text. More text.');
      expect(result).not.toContain('var x');
      expect(result).not.toContain('.foo');
    });

    it('skips img, video, audio elements', () => {
      const html = '<p>Before image.</p><img src="test.jpg" alt="test"><p>After image.</p>';
      expect(extractText(html)).toBe('Before image. After image.');
    });

    it('handles empty HTML', () => {
      expect(extractText('')).toBe('');
    });

    it('handles whitespace-only HTML', () => {
      expect(extractText('<p>   </p>')).toBe('');
    });

    it('collapses multiple whitespace', () => {
      const html = '<p>Hello    world   with   spaces.</p>';
      expect(extractText(html)).toBe('Hello world with spaces.');
    });

    it('skips Ghost image cards', () => {
      const html = `
        <p>Before image.</p>
        <figure class="kg-card kg-image-card">
          <img src="photo.jpg" alt="Photo">
          <figcaption>Caption text</figcaption>
        </figure>
        <p>After image.</p>
      `;
      const result = extractText(html);
      expect(result).toContain('Before image.');
      expect(result).toContain('After image.');
      expect(result).not.toContain('Caption text');
    });

    it('skips Ghost embed cards', () => {
      const html = `
        <p>Before embed.</p>
        <figure class="kg-card kg-embed-card">
          <iframe src="https://youtube.com/embed/123"></iframe>
        </figure>
        <p>After embed.</p>
      `;
      const result = extractText(html);
      expect(result).toBe('Before embed. After embed.');
    });

    it('skips Ghost code cards', () => {
      const html = `
        <p>Before code.</p>
        <div class="kg-card kg-code-card">
          <pre><code>const x = 1;</code></pre>
        </div>
        <p>After code.</p>
      `;
      expect(extractText(html)).toBe('Before code. After code.');
    });

    it('skips plain pre/code content without Ghost card classes', () => {
      const html = '<pre><code>const x = 1;</code></pre><p>After</p>';
      expect(extractText(html)).toBe('After');
    });

    it('skips Ghost gallery cards', () => {
      const html = `
        <p>Before gallery.</p>
        <figure class="kg-card kg-gallery-card">
          <div class="kg-gallery-container">
            <img src="a.jpg"><img src="b.jpg">
          </div>
        </figure>
        <p>After gallery.</p>
      `;
      const result = extractText(html);
      expect(result).toBe('Before gallery. After gallery.');
    });

    it('extracts text from Ghost callout cards', () => {
      const html = `
        <div class="kg-card kg-callout-card kg-callout-card-blue">
          <div class="kg-callout-emoji">💡</div>
          <div class="kg-callout-text">This is an important note.</div>
        </div>
      `;
      const result = extractText(html);
      expect(result).toContain('This is an important note.');
    });

    it('extracts text from Ghost toggle cards', () => {
      const html = `
        <div class="kg-card kg-toggle-card" data-kg-toggle-state="close">
          <div class="kg-toggle-heading">
            <h4 class="kg-toggle-heading-text">FAQ Question</h4>
          </div>
          <div class="kg-toggle-content">
            <p>This is the answer to the FAQ.</p>
          </div>
        </div>
      `;
      const result = extractText(html);
      expect(result).toContain('FAQ Question');
      expect(result).toContain('This is the answer to the FAQ.');
    });

    it('handles complex Ghost post with mixed content', () => {
      const html = `
        <h2>Article Title</h2>
        <p>Introduction paragraph with <strong>bold</strong> text.</p>
        <figure class="kg-card kg-image-card">
          <img src="hero.jpg" alt="Hero">
        </figure>
        <p>Second paragraph after the image.</p>
        <blockquote>A meaningful quote.</blockquote>
        <ul>
          <li>Point one</li>
          <li>Point two</li>
        </ul>
        <div class="kg-card kg-callout-card">
          <div class="kg-callout-text">Important callout text.</div>
        </div>
        <p>Conclusion paragraph.</p>
      `;
      const result = extractText(html);
      expect(result).toContain('Article Title');
      expect(result).toContain('Introduction paragraph with bold text.');
      expect(result).toContain('Second paragraph after the image.');
      expect(result).toContain('A meaningful quote.');
      expect(result).toContain('Point one');
      expect(result).toContain('Point two');
      expect(result).toContain('Important callout text.');
      expect(result).toContain('Conclusion paragraph.');
      // Should NOT contain image alt text
      expect(result).not.toContain('Hero');
    });

    it('handles migrated lexical/mobiledoc-style mixed wrappers safely', () => {
      const html = `
        <!--kg-card-begin: markdown-->
        <p>Rendered markdown text survives migration.</p>
        <!--kg-card-end: markdown-->
        <div class="kg-card kg-callout-card">
          <div class="kg-callout-text"><span data-lexical-text="true">Lexical callout text.</span></div>
        </div>
        <div class="kg-card kg-html-card"><div>Raw html-card source must be skipped.</div></div>
      `;

      const result = extractText(html);
      expect(result).toContain('Rendered markdown text survives migration.');
      expect(result).toContain('Lexical callout text.');
      expect(result).not.toContain('Raw html-card source must be skipped.');
    });

    it('handles malformed html without crashing and preserves visible text', () => {
      const html = '<div><p>Start <strong>bold<p>Next line &amp; trailing';
      const result = extractText(html);
      expect(result).toContain('Start');
      expect(result).toContain('bold');
      expect(result).toContain('Next line & trailing');
    });

    it('skips source=html wrapped Ghost html-card content', () => {
      const html = `
        <p>Before.</p>
        <!--kg-card-begin: html-->
        <p>Do not sign this raw html card text.</p>
        <!--kg-card-end: html-->
        <p>After.</p>
      `;

      const result = extractText(html);
      expect(result).toContain('Before.');
      expect(result).toContain('After.');
      expect(result).not.toContain('Do not sign this raw html card text.');
    });
  });

  // =========================================================================
  // extractFragments
  // =========================================================================
  describe('extractFragments', () => {
    it('extracts text fragments with byte offsets', () => {
      const html = '<p>Hello</p><p>World</p>';
      const frags = extractFragments(html);
      expect(frags.length).toBe(2);
      expect(frags[0].rawText).toBe('Hello');
      expect(frags[1].rawText).toBe('World');
    });

    it('skips script content', () => {
      const html = '<p>Text</p><script>alert("hi")</script><p>More</p>';
      const frags = extractFragments(html);
      expect(frags.length).toBe(2);
      expect(frags[0].rawText).toBe('Text');
      expect(frags[1].rawText).toBe('More');
    });

    it('skips HTML comments', () => {
      const html = '<p>Before</p><!-- comment --><p>After</p>';
      const frags = extractFragments(html);
      expect(frags.length).toBe(2);
      expect(frags[0].rawText).toBe('Before');
      expect(frags[1].rawText).toBe('After');
    });

    it('handles empty HTML', () => {
      expect(extractFragments('')).toEqual([]);
    });

    it('handles HTML with no text', () => {
      expect(extractFragments('<img src="test.jpg">')).toEqual([]);
    });

    it('skips text inside source=html wrapped Ghost html-card comments', () => {
      const html = '<p>Before</p><!--kg-card-begin: html--><p>Skip me</p><!--kg-card-end: html--><p>After</p>';
      const frags = extractFragments(html);
      expect(frags.length).toBe(2);
      expect(frags[0].rawText).toBe('Before');
      expect(frags[1].rawText).toBe('After');
    });
  });

  // =========================================================================
  // Unicode VS helpers
  // =========================================================================
  describe('isVsChar', () => {
    it('detects VS1 (U+FE00)', () => {
      expect(isVsChar('\uFE00')).toBe(true);
    });

    it('detects VS16 (U+FE0F)', () => {
      expect(isVsChar('\uFE0F')).toBe(true);
    });

    it('detects ZWNBSP (U+FEFF)', () => {
      expect(isVsChar('\uFEFF')).toBe(true);
    });

    it('rejects normal characters', () => {
      expect(isVsChar('A')).toBe(false);
      expect(isVsChar(' ')).toBe(false);
      expect(isVsChar('0')).toBe(false);
    });
  });

  describe('isVsOrWhitespace', () => {
    it('detects VS chars', () => {
      expect(isVsOrWhitespace('\uFE00')).toBe(true);
    });

    it('detects whitespace', () => {
      expect(isVsOrWhitespace(' ')).toBe(true);
      expect(isVsOrWhitespace('\t')).toBe(true);
      expect(isVsOrWhitespace('\n')).toBe(true);
    });

    it('detects NBSP', () => {
      expect(isVsOrWhitespace('\u00A0')).toBe(true);
    });

    it('rejects normal characters', () => {
      expect(isVsOrWhitespace('A')).toBe(false);
    });
  });

  describe('splitChars', () => {
    it('splits ASCII string', () => {
      expect(splitChars('abc')).toEqual(['a', 'b', 'c']);
    });

    it('handles emoji (surrogate pairs)', () => {
      const chars = splitChars('a😀b');
      expect(chars).toEqual(['a', '😀', 'b']);
    });

    it('handles empty string', () => {
      expect(splitChars('')).toEqual([]);
    });
  });

  describe('applyEmbeddingPlan', () => {
    it('applies marker insertions using codepoint indices', () => {
      const markerA = '\uFE00';
      const markerB = '\uFE01';
      const result = applyEmbeddingPlan('Hello', {
        index_unit: 'codepoint',
        operations: [
          { insert_after_index: 0, marker: markerA },
          { insert_after_index: 4, marker: markerB },
        ],
      });

      expect(result).toBe(`H${markerA}ello${markerB}`);
    });

    it('supports insertion before first visible character with index -1', () => {
      const marker = '\uFE00';
      const result = applyEmbeddingPlan('abc', {
        index_unit: 'codepoint',
        operations: [{ insert_after_index: -1, marker }],
      });

      expect(result).toBe(`${marker}abc`);
    });

    it('returns null when operation index is out of bounds', () => {
      const result = applyEmbeddingPlan('abc', {
        index_unit: 'codepoint',
        operations: [{ insert_after_index: 3, marker: '\uFE00' }],
      });

      expect(result).toBeNull();
    });

    it('returns null for unsupported index units', () => {
      const result = applyEmbeddingPlan('abc', {
        index_unit: 'byte',
        operations: [{ insert_after_index: 0, marker: '\uFE00' }],
      });

      expect(result).toBeNull();
    });
  });

  describe('embedEmbeddingPlanIntoHtml', () => {
    it('inserts markers by codepoint index across paragraph boundaries', () => {
      const markerA = '\uFE00';
      const markerB = '\uFE01\uFE02';
      const html = '<p>Hello world.</p><p>Next sentence.</p>';
      const result = embedEmbeddingPlanIntoHtml(html, {
        index_unit: 'codepoint',
        operations: [
          { insert_after_index: 11, marker: markerA },
          { insert_after_index: 26, marker: markerB },
        ],
      });

      expect(result).toContain(`world.${markerA}</p>`);
      expect(result).toContain(`sentence.${markerB}</p>`);
      expect(result).toContain('<p>Hello');
      expect(result).toContain('<p>Next');
    });

    it('supports insertion before the first visible character via index -1', () => {
      const marker = '\uFE00';
      const html = '<p>Hello world.</p>';
      const result = embedEmbeddingPlanIntoHtml(html, {
        index_unit: 'codepoint',
        operations: [{ insert_after_index: -1, marker }],
      });

      expect(result).toContain(`<p>${marker}Hello world.</p>`);
    });

    it('returns null for out-of-range insertion indices', () => {
      const html = '<p>Hello world.</p>';
      const result = embedEmbeddingPlanIntoHtml(html, {
        index_unit: 'codepoint',
        operations: [{ insert_after_index: 999, marker: '\uFE00' }],
      });

      expect(result).toBeNull();
    });

    it('does not insert markers into skipped kg-code-card text when duplicate visible text exists', () => {
      const marker = '\uFE00';
      const html = '<div class="kg-card kg-code-card"><pre><code>Hello world.</code></pre></div><p>Hello world.</p>';

      const result = embedEmbeddingPlanIntoHtml(html, {
        index_unit: 'codepoint',
        operations: [{ insert_after_index: 11, marker }],
      });

      expect(result).toContain('<code>Hello world.</code>');
      expect(result).toContain(`<p>Hello world.${marker}</p>`);
    });

    it('supports codepoint insertion around ZWJ grapheme sequences', () => {
      const marker = '\uFE00';
      const visible = 'Family 👨‍👩‍👧‍👦 rocks.';
      const html = `<p>${visible}</p>`;
      const result = embedEmbeddingPlanIntoHtml(html, {
        index_unit: 'codepoint',
        operations: [{ insert_after_index: splitChars(visible).length - 1, marker }],
      });

      expect(result).toContain(`rocks.${marker}</p>`);
      expect(result).toContain('👨‍👩‍👧‍👦');
    });
  });

  describe('stripC2paEmbeddings', () => {
    it('strips VS chars', () => {
      const text = 'Hello\uFE00\uFE01 World\uFEFF';
      expect(stripC2paEmbeddings(text)).toBe('Hello World');
    });

    it('preserves normal text', () => {
      expect(stripC2paEmbeddings('Hello World')).toBe('Hello World');
    });
  });

  describe('detectC2paEmbeddings', () => {
    it('returns zero for plain text', () => {
      const result = detectC2paEmbeddings('Hello World');
      expect(result.count).toBe(0);
      expect(result.positions).toEqual([]);
    });
  });

  // =========================================================================
  // embedSignedText
  // =========================================================================
  describe('embedSignedText', () => {
    it('embeds signed text back into simple HTML', () => {
      const html = '<p>Hello world.</p>';
      const signed = 'Hello world.';
      const result = embedSignedText(html, signed);
      expect(result).toContain('Hello world.');
      expect(result).toContain('<p>');
      expect(result).toContain('</p>');
    });

    it('preserves HTML structure', () => {
      const html = '<h1>Title</h1><p>Body text.</p>';
      const signed = 'Title Body text.';
      const result = embedSignedText(html, signed);
      expect(result).toContain('<h1>');
      expect(result).toContain('</h1>');
      expect(result).toContain('<p>');
      expect(result).toContain('</p>');
    });

    it('returns signed text when no fragments found', () => {
      const html = '';
      const signed = 'Just text';
      expect(embedSignedText(html, signed)).toBe('Just text');
    });

    it('embeds markers correctly when HTML contains named entities', () => {
      const html = '<p>As Co-Chair &mdash; proof.</p><p>Next sentence.</p>';
      const signed = `As Co-Chair — proof.\uFE00 Next sentence.\uFE01\uFE02`;

      const result = embedSignedText(html, signed);

      // Marker for first sentence should remain in first paragraph.
      expect(result).toContain('proof.\uFE00</p>');
      // Marker for second sentence should remain in second paragraph.
      expect(result).toContain('sentence.\uFE01\uFE02</p>');
    });

    it('does not embed into source=html wrapped Ghost html-card text when duplicated', () => {
      const html =
        '<!--kg-card-begin: html--><p>Hello world.</p><!--kg-card-end: html-->'
        + '<p>Hello world.</p>';
      const signed = 'Hello world.\uFE01';

      const result = embedSignedText(html, signed);

      expect(result).toContain('<!--kg-card-begin: html--><p>Hello world.</p><!--kg-card-end: html-->');
      expect(result).toContain('<p>Hello world.\uFE01</p>');
    });

    it('preserves Unicode grapheme clusters while embedding markers', () => {
      const html = '<p>Emoji family 👨‍👩‍👧‍👦 stays intact.</p>';
      const signed = 'Emoji family 👨‍👩‍👧‍👦 stays intact.\uFE01';
      const result = embedSignedText(html, signed);

      expect(result).toContain('👨‍👩‍👧‍👦');
      expect(result).toContain('intact.\uFE01</p>');
    });
  });

  // =========================================================================
  // extractTextForVerify
  // =========================================================================
  describe('extractTextForVerify', () => {
    it('extracts text preserving structure', () => {
      const html = '<p>Hello world.</p><p>Second paragraph.</p>';
      const result = extractTextForVerify(html);
      expect(result).toContain('Hello world.');
      expect(result).toContain('Second paragraph.');
    });

    it('handles empty HTML', () => {
      expect(extractTextForVerify('')).toBe('');
    });
  });

  // =========================================================================
  // Ghost card-specific extractors
  // =========================================================================
  describe('extractBookmarkText', () => {
    it('extracts title and description from bookmark cards', () => {
      const html = `
        <figure class="kg-card kg-bookmark-card">
          <a class="kg-bookmark-container" href="https://example.com">
            <div class="kg-bookmark-content">
              <div class="kg-bookmark-title">Bookmark Title</div>
              <div class="kg-bookmark-description">Bookmark description text.</div>
            </div>
          </a>
        </figure>
      `;
      const result = extractBookmarkText(html);
      expect(result).toContain('Bookmark Title');
      expect(result).toContain('Bookmark description text.');
    });
  });

  describe('extractCalloutText', () => {
    it('extracts text from callout cards', () => {
      const html = `
        <div class="kg-card kg-callout-card">
          <div class="kg-callout-emoji">💡</div>
          <div class="kg-callout-text">Important note here.</div>
        </div>
      `;
      expect(extractCalloutText(html)).toBe('Important note here.');
    });
  });

  describe('extractToggleText', () => {
    it('extracts heading and content from toggle cards', () => {
      const html = `
        <div class="kg-card kg-toggle-card">
          <div class="kg-toggle-heading">
            <h4 class="kg-toggle-heading-text">Toggle Heading</h4>
          </div>
          <div class="kg-toggle-content">
            <p>Toggle body content.</p>
          </div>
        </div>
      `;
      const result = extractToggleText(html);
      expect(result).toContain('Toggle Heading');
      expect(result).toContain('Toggle body content.');
    });
  });
});
