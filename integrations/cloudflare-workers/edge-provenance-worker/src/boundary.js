/**
 * Article boundary detection module.
 *
 * Finds the article content region within an HTML page using a prioritized
 * detection chain ordered by web prevalence:
 *
 *   P0: Publisher override (ARTICLE_SELECTOR config)
 *   P1: <article> tag (~50%+ of content sites)
 *   P2: CMS content wrapper classes (.entry-content, .gh-content, etc.)
 *   P3: [itemprop="articleBody"] (Schema.org microdata)
 *   P4: <main> / [role="main"]
 *   P5: JSON-LD articleBody
 *   P6: Largest <p> cluster heuristic
 *   P7: Full <body> (last resort)
 *
 * Returns the matched HTML substring and its byte offset within the full HTML,
 * plus which detection method matched (for analytics).
 */

/**
 * @typedef {Object} BoundaryResult
 * @property {string} html - The article HTML substring
 * @property {number} byteOffset - Byte offset of the boundary within full HTML
 * @property {string} selector - Which detection method matched
 * @property {string|null} jsonLdText - Plain text from JSON-LD (when available)
 */

/**
 * CMS content wrapper classes ordered by prevalence.
 * WordPress alone accounts for ~43% of the web.
 */
const CMS_CONTENT_CLASSES = [
  'entry-content',           // WordPress default (classic + block themes)
  'wp-block-post-content',   // WordPress block themes (Twenty Twenty-Four)
  'post-content',            // Jekyll Minima, generic blog themes
  'article-body',            // News publisher convention
  'article-content',         // News publisher convention
  'story-body',              // News publisher convention
  'story-body-text',         // News publisher convention
  'gh-content',              // Ghost CMS (Casper theme)
  'w-richtext',              // Webflow
  'sqs-block-content',       // Squarespace
  'body markup',             // Substack
  'e-content',               // Microformats2 / IndieWeb
  'RichTextStoryBody',       // AP News
];

/**
 * Find article boundary in HTML using the detection chain.
 *
 * @param {string} html - Full HTML response body
 * @param {string|null} overrideSelector - Publisher-configured selector (from env)
 * @returns {BoundaryResult|null}
 */
export function findArticleBoundary(html, overrideSelector) {
  // P0: Publisher override
  if (overrideSelector) {
    const result = matchSelector(html, overrideSelector);
    if (result) return { ...result, selector: `override:${overrideSelector}` };
  }

  // P1: <article> tag
  const articleResult = matchTag(html, 'article');
  if (articleResult) {
    // If multiple <article> tags, pick the one with the most <p> children
    const allArticles = matchAllTags(html, 'article');
    if (allArticles.length > 1) {
      let best = allArticles[0];
      let bestPCount = countTag(best.html, 'p');
      for (let i = 1; i < allArticles.length; i++) {
        const pCount = countTag(allArticles[i].html, 'p');
        if (pCount > bestPCount) {
          best = allArticles[i];
          bestPCount = pCount;
        }
      }
      return { ...best, selector: 'article' };
    }
    return { ...articleResult, selector: 'article' };
  }

  // P2: CMS content wrapper classes
  for (const cls of CMS_CONTENT_CLASSES) {
    const result = matchClass(html, cls);
    if (result) return { ...result, selector: `class:${cls}` };
  }

  // P3: Schema.org microdata
  const itemPropResult = matchAttribute(html, 'itemprop', 'articleBody');
  if (itemPropResult) return { ...itemPropResult, selector: 'itemprop:articleBody' };

  // P4: <main> / [role="main"]
  const mainResult = matchTag(html, 'main');
  if (mainResult) return { ...mainResult, selector: 'main' };

  const roleMainResult = matchAttribute(html, 'role', 'main');
  if (roleMainResult) return { ...roleMainResult, selector: 'role:main' };

  // P5: JSON-LD articleBody
  const jsonLdText = extractJsonLdArticleBody(html);
  if (jsonLdText && jsonLdText.length >= 50) {
    // We have plain text but still need an HTML boundary for marker injection.
    // Fall through to P6/P7 but attach the JSON-LD text for validation.
  }

  // P6: Largest <p> cluster
  const pCluster = findLargestPCluster(html);
  if (pCluster) {
    return {
      ...pCluster,
      selector: 'p-cluster',
      jsonLdText: jsonLdText || null,
    };
  }

  // P7: Full <body>
  const bodyResult = matchTag(html, 'body');
  if (bodyResult) {
    return {
      ...bodyResult,
      selector: 'body',
      jsonLdText: jsonLdText || null,
    };
  }

  return null;
}

/**
 * Extract articleBody from JSON-LD structured data.
 *
 * @param {string} html
 * @returns {string|null}
 */
export function extractJsonLdArticleBody(html) {
  const scriptRe = /<script\s+type\s*=\s*["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;
  let match;
  while ((match = scriptRe.exec(html)) !== null) {
    try {
      const data = JSON.parse(match[1]);
      const body = findArticleBodyInJsonLd(data);
      if (body) return body;
    } catch {
      // Malformed JSON-LD, skip
    }
  }
  return null;
}

/**
 * Recursively search JSON-LD data for articleBody.
 * Handles both flat objects and @graph arrays.
 */
function findArticleBodyInJsonLd(data) {
  if (!data || typeof data !== 'object') return null;

  if (Array.isArray(data)) {
    for (const item of data) {
      const result = findArticleBodyInJsonLd(item);
      if (result) return result;
    }
    return null;
  }

  // Check @graph
  if (data['@graph']) {
    return findArticleBodyInJsonLd(data['@graph']);
  }

  // Check @type for Article variants
  const type = data['@type'];
  const isArticle = type === 'Article'
    || type === 'NewsArticle'
    || type === 'ReportageNewsArticle'
    || type === 'BlogPosting'
    || type === 'TechArticle'
    || type === 'ScholarlyArticle';

  if (isArticle && typeof data.articleBody === 'string' && data.articleBody.length > 0) {
    return data.articleBody;
  }

  return null;
}


// ---------------------------------------------------------------------------
// Regex-based HTML matchers
// ---------------------------------------------------------------------------

/**
 * Match an HTML element by tag name (first occurrence).
 * Uses a simple regex to find opening/closing tag pairs.
 */
function matchTag(html, tagName) {
  const re = new RegExp(
    `<${tagName}\\b[^>]*>([\\s\\S]*?)<\\/${tagName}>`,
    'i',
  );
  const m = html.match(re);
  if (!m) return null;
  return {
    html: m[0],
    byteOffset: m.index,
    jsonLdText: null,
  };
}

/**
 * Match all occurrences of an HTML tag.
 */
function matchAllTags(html, tagName) {
  const re = new RegExp(
    `<${tagName}\\b[^>]*>[\\s\\S]*?<\\/${tagName}>`,
    'gi',
  );
  const results = [];
  let m;
  while ((m = re.exec(html)) !== null) {
    results.push({
      html: m[0],
      byteOffset: m.index,
      jsonLdText: null,
    });
  }
  return results;
}

/**
 * Match an element by class name.
 */
function matchClass(html, className) {
  // Handles class="foo bar entry-content baz"
  const escaped = className.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp(
    `<(\\w+)\\b[^>]*class\\s*=\\s*["'][^"']*\\b${escaped}\\b[^"']*["'][^>]*>([\\s\\S]*?)<\\/\\1>`,
    'i',
  );
  const m = html.match(re);
  if (!m) return null;
  return {
    html: m[0],
    byteOffset: m.index,
    jsonLdText: null,
  };
}

/**
 * Match an element by attribute value.
 */
function matchAttribute(html, attrName, attrValue) {
  const re = new RegExp(
    `<(\\w+)\\b[^>]*${attrName}\\s*=\\s*["']${attrValue}["'][^>]*>([\\s\\S]*?)<\\/\\1>`,
    'i',
  );
  const m = html.match(re);
  if (!m) return null;
  return {
    html: m[0],
    byteOffset: m.index,
    jsonLdText: null,
  };
}

/**
 * Match a publisher-configured selector.
 * Supports: tag name, .class, [attr=value]
 */
function matchSelector(html, selector) {
  if (selector.startsWith('.')) {
    return matchClass(html, selector.slice(1));
  }
  if (selector.startsWith('[')) {
    const attrMatch = selector.match(/\[(\w+)=["']?([^"'\]]+)["']?\]/);
    if (attrMatch) return matchAttribute(html, attrMatch[1], attrMatch[2]);
  }
  return matchTag(html, selector);
}

/**
 * Count occurrences of a tag within HTML.
 */
function countTag(html, tagName) {
  const re = new RegExp(`<${tagName}\\b`, 'gi');
  const matches = html.match(re);
  return matches ? matches.length : 0;
}

/**
 * Find the container with the highest density of <p> tags.
 * Returns null if no container has 5+ paragraphs.
 */
function findLargestPCluster(html) {
  // Try common container tags
  const containers = ['div', 'section', 'main'];
  let bestMatch = null;
  let bestPCount = 4; // minimum threshold

  for (const tag of containers) {
    const allMatches = matchAllTags(html, tag);
    for (const m of allMatches) {
      const pCount = countTag(m.html, 'p');
      if (pCount > bestPCount) {
        bestMatch = m;
        bestPCount = pCount;
      }
    }
  }

  return bestMatch;
}
