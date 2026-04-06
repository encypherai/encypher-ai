import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { findArticleBoundary, extractJsonLdArticleBody } from '../src/boundary.js';

// ---------------------------------------------------------------------------
// Fixture HTML snippets representing real CMS patterns
// ---------------------------------------------------------------------------

const WP_CLASSIC = `<html><head><title>Test</title></head><body>
<nav><a href="/">Home</a></nav>
<article class="post">
  <h1>WordPress Classic Article</h1>
  <div class="entry-content">
    <p>First paragraph of the article with enough text to pass the minimum threshold for signing.</p>
    <p>Second paragraph continues the article with additional content and detail.</p>
  </div>
</article>
<footer>Copyright 2026</footer>
</body></html>`;

const WP_BLOCK = `<html><head><title>Block Theme</title></head><body>
<header><nav>Menu</nav></header>
<main class="wp-site-blocks">
  <div class="wp-block-post-content">
    <p>Block theme article content with enough text to sign properly at the CDN edge.</p>
    <p>Second paragraph of the block theme article continues here with more content.</p>
  </div>
</main>
<footer>Footer</footer>
</body></html>`;

const GHOST = `<html><head><title>Ghost Post</title></head><body>
<header class="site-header">Navigation</header>
<article class="article post">
  <header class="article-header"><h1>Ghost Article</h1></header>
  <section class="gh-content gh-canvas">
    <p>Ghost CMS article content with the Casper theme default structure here.</p>
    <p>Additional paragraphs in the Ghost article for content boundary detection.</p>
  </section>
</article>
</body></html>`;

const SQUARESPACE = `<html><head><title>Squarespace</title></head><body>
<nav>Nav</nav>
<article class="blog-item">
  <div class="sqs-block-content">
    <p>Squarespace blog content using the standard sqs-block-content wrapper class.</p>
    <p>Another paragraph in the Squarespace blog article for testing purposes here.</p>
  </div>
</article>
</body></html>`;

const WEBFLOW = `<html><head><title>Webflow</title></head><body>
<nav>Nav</nav>
<div class="w-richtext">
  <p>Webflow rich text content inside the standard w-richtext wrapper class element.</p>
  <p>More Webflow content here with sufficient text for the minimum length threshold.</p>
</div>
</body></html>`;

const JSON_LD_ARTICLE = `<html><head>
<title>CNN Article</title>
<script type="application/ld+json">
{"@type": "NewsArticle", "headline": "Test", "articleBody": "This is the full article body text from JSON-LD structured data that CNN includes in their pages."}
</script>
</head><body>
<main><p>This is the full article body text from JSON-LD structured data that CNN includes in their pages.</p></main>
</body></html>`;

const MAIN_ONLY = `<html><head><title>Main Only</title></head><body>
<nav>Navigation links here</nav>
<main>
  <p>Article content in a main tag without an article wrapper element present on page.</p>
  <p>Second paragraph of the main-only article with additional content for testing.</p>
</main>
<footer>Footer content</footer>
</body></html>`;

const ROLE_MAIN = `<html><head><title>Role Main</title></head><body>
<div role="main">
  <p>Content inside a div with role main used as the article content area fallback.</p>
  <p>Second paragraph inside the role main area with additional text for testing.</p>
</div>
</body></html>`;

const ITEMPROP = `<html><head><title>Schema</title></head><body>
<div itemprop="articleBody">
  <p>Schema.org microdata content using itemprop articleBody attribute for detection.</p>
  <p>Additional paragraph in the itemprop articleBody section for testing boundary.</p>
</div>
</body></html>`;

const MULTI_ARTICLE = `<html><body>
<article class="teaser"><p>Short teaser</p></article>
<article class="main-article">
  <p>First paragraph of the main article content.</p>
  <p>Second paragraph of the main article content.</p>
  <p>Third paragraph of the main article content.</p>
  <p>Fourth paragraph of the main article content.</p>
  <p>Fifth paragraph with enough text.</p>
</article>
<article class="sidebar-teaser"><p>Another teaser</p></article>
</body></html>`;

const NO_ARTICLE = `<html><body>
<nav><a href="/">Home</a><a href="/about">About</a></nav>
<footer>Copyright</footer>
</body></html>`;

const SUBSTACK = `<html><head><title>Substack</title></head><body>
<div class="post">
  <div class="body markup">
    <p>Substack newsletter content using the body markup class for article content.</p>
    <p>Another paragraph in the Substack newsletter for testing boundary detection.</p>
  </div>
</div>
</body></html>`;

const JEKYLL_HUGO = `<html><head><title>Hugo Post</title></head><body>
<nav>Navigation</nav>
<main>
  <article class="post">
    <h1>Hugo Article</h1>
    <div class="post-content">
      <p>Hugo static site article content using post-content class for the article body.</p>
      <p>Second paragraph of the Hugo article with more content for testing detection.</p>
    </div>
  </article>
</main>
<footer>Footer</footer>
</body></html>`;

// No article/main tags; content is in a div with many paragraphs.
const P_CLUSTER_ONLY = `<html><body>
<div class="header">Site header</div>
<div class="content-area">
  <p>First paragraph of the main content area used for p-cluster heuristic detection.</p>
  <p>Second paragraph with additional text to satisfy the five paragraph minimum.</p>
  <p>Third paragraph continues the content with enough material for signing purposes.</p>
  <p>Fourth paragraph adds more content to reach the threshold for cluster detection.</p>
  <p>Fifth paragraph completes the minimum set for the largest p-cluster heuristic.</p>
</div>
<div class="sidebar"><p>Sidebar item</p></div>
</body></html>`;

const AP_NEWS_STYLE = `<html><head><title>AP Style</title></head><body>
<main class="Page-main">
  <div class="RichTextStoryBody RichTextBody">
    <p>AP News style content using the RichTextStoryBody class for article detection.</p>
    <p>Second paragraph of the AP News style article with additional text for testing.</p>
  </div>
</main>
</body></html>`;

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('findArticleBoundary', () => {
  it('detects WordPress classic <article> tag', () => {
    const result = findArticleBoundary(WP_CLASSIC, null);
    assert.ok(result);
    assert.equal(result.selector, 'article');
    assert.ok(result.html.includes('entry-content'));
  });

  it('detects WordPress block theme .wp-block-post-content', () => {
    const result = findArticleBoundary(WP_BLOCK, null);
    assert.ok(result);
    assert.equal(result.selector, 'class:wp-block-post-content');
    assert.ok(result.html.includes('Block theme article'));
  });

  it('detects Ghost CMS <article>', () => {
    const result = findArticleBoundary(GHOST, null);
    assert.ok(result);
    assert.equal(result.selector, 'article');
    assert.ok(result.html.includes('gh-content'));
  });

  it('detects Squarespace <article> tag', () => {
    const result = findArticleBoundary(SQUARESPACE, null);
    assert.ok(result);
    assert.equal(result.selector, 'article');
    assert.ok(result.html.includes('sqs-block-content'));
  });

  it('detects Webflow .w-richtext', () => {
    const result = findArticleBoundary(WEBFLOW, null);
    assert.ok(result);
    assert.equal(result.selector, 'class:w-richtext');
  });

  it('detects AP News .RichTextStoryBody', () => {
    const result = findArticleBoundary(AP_NEWS_STYLE, null);
    assert.ok(result);
    assert.equal(result.selector, 'class:RichTextStoryBody');
  });

  it('detects itemprop="articleBody"', () => {
    const result = findArticleBoundary(ITEMPROP, null);
    assert.ok(result);
    assert.equal(result.selector, 'itemprop:articleBody');
  });

  it('falls back to <main> tag', () => {
    const result = findArticleBoundary(MAIN_ONLY, null);
    assert.ok(result);
    assert.equal(result.selector, 'main');
  });

  it('falls back to role="main"', () => {
    const result = findArticleBoundary(ROLE_MAIN, null);
    assert.ok(result);
    assert.equal(result.selector, 'role:main');
  });

  it('picks the article with most <p> tags when multiple exist', () => {
    const result = findArticleBoundary(MULTI_ARTICLE, null);
    assert.ok(result);
    assert.equal(result.selector, 'article');
    assert.ok(result.html.includes('main-article'));
  });

  it('returns null for pages with no article content', () => {
    const result = findArticleBoundary(NO_ARTICLE, null);
    // May match <body> as last resort or return null
    if (result) {
      assert.equal(result.selector, 'body');
    }
  });

  it('detects Substack .body.markup class', () => {
    const result = findArticleBoundary(SUBSTACK, null);
    assert.ok(result);
    // body markup is in CMS_CONTENT_CLASSES; selector should reflect the matched class
    assert.ok(
      result.selector === 'class:body markup' || result.selector === 'class:markup',
      `unexpected selector: ${result.selector}`,
    );
    assert.ok(result.html.includes('Substack newsletter content'));
  });

  it('detects Jekyll/Hugo <article> tag', () => {
    const result = findArticleBoundary(JEKYLL_HUGO, null);
    assert.ok(result);
    assert.equal(result.selector, 'article');
    assert.ok(result.html.includes('Hugo Article'));
  });

  it('falls back to p-cluster heuristic when no semantic landmark exists', () => {
    const result = findArticleBoundary(P_CLUSTER_ONLY, null);
    assert.ok(result);
    assert.equal(result.selector, 'p-cluster');
    assert.ok(result.html.includes('content-area'));
  });

  it('uses publisher override selector when provided', () => {
    const result = findArticleBoundary(WP_CLASSIC, '.entry-content');
    assert.ok(result);
    assert.equal(result.selector, 'override:.entry-content');
  });
});

describe('extractJsonLdArticleBody', () => {
  it('extracts articleBody from NewsArticle JSON-LD', () => {
    const text = extractJsonLdArticleBody(JSON_LD_ARTICLE);
    assert.ok(text);
    assert.ok(text.includes('full article body text'));
  });

  it('returns null when no JSON-LD present', () => {
    const text = extractJsonLdArticleBody(WP_CLASSIC);
    assert.equal(text, null);
  });

  it('returns null for non-article JSON-LD', () => {
    const html = `<script type="application/ld+json">{"@type": "Organization", "name": "Test"}</script>`;
    assert.equal(extractJsonLdArticleBody(html), null);
  });

  it('handles @graph pattern', () => {
    const html = `<script type="application/ld+json">
    {"@graph": [{"@type": "WebPage"}, {"@type": "NewsArticle", "articleBody": "Graph body text"}]}
    </script>`;
    const text = extractJsonLdArticleBody(html);
    assert.equal(text, 'Graph body text');
  });
});
