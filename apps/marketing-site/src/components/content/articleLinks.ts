import type { RelatedArticle } from './RelatedArticles';

/**
 * Related article relationships for the marketing site.
 * Each key is a page path; its value is the list of related articles to show.
 * Limit to 4 per page to keep the block compact.
 */

// -- C2PA Standard sub-pages --

const c2paShared: RelatedArticle[] = [
  { title: 'C2PA Section A.7: Text Provenance', href: '/c2pa-standard/section-a7' },
  { title: 'C2PA Manifest Structure', href: '/c2pa-standard/manifest-structure' },
  { title: 'C2PA Implementation Guide', href: '/c2pa-standard/implementation-guide' },
  { title: 'C2PA Conformant Products', href: '/c2pa-standard/conformance' },
  { title: 'Supported Media Types', href: '/c2pa-standard/media-types' },
  { title: 'C2PA Members', href: '/c2pa-standard/members' },
  { title: 'Encypher vs SynthID', href: '/c2pa-standard/vs-synthid' },
];

// -- Content Provenance sub-pages --

const cpFormats: RelatedArticle[] = [
  { title: 'Text Provenance', href: '/content-provenance/text' },
  { title: 'Image Provenance', href: '/content-provenance/images' },
  { title: 'Audio and Video Provenance', href: '/content-provenance/audio-video' },
  { title: 'Live Stream Provenance', href: '/content-provenance/live-streams' },
];

const cpAudiences: RelatedArticle[] = [
  { title: 'For Publishers', href: '/content-provenance/for-publishers' },
  { title: 'For Enterprises', href: '/content-provenance/for-enterprises' },
  { title: 'For AI Companies', href: '/content-provenance/for-ai-companies' },
];

const cpVerticals: RelatedArticle[] = [
  { title: 'News Publishers', href: '/content-provenance/news-publishers' },
  { title: 'Enterprise AI', href: '/content-provenance/enterprise-ai' },
  { title: 'Academic Publishing', href: '/content-provenance/academic-publishing' },
  { title: 'Government', href: '/content-provenance/government' },
  { title: 'Legal', href: '/content-provenance/legal' },
  { title: 'Music Industry', href: '/content-provenance/music-industry' },
];

const cpCompliance: RelatedArticle[] = [
  { title: 'EU AI Act Compliance', href: '/content-provenance/eu-ai-act' },
  { title: 'Content Verification', href: '/content-provenance/verification' },
];

// -- Cryptographic Watermarking sub-pages --

const cwShared: RelatedArticle[] = [
  { title: 'How Cryptographic Watermarking Works', href: '/cryptographic-watermarking/how-it-works' },
  { title: 'Survives Distribution', href: '/cryptographic-watermarking/survives-distribution' },
  { title: 'Legal Implications', href: '/cryptographic-watermarking/legal-implications' },
  { title: 'Text Watermarking', href: '/cryptographic-watermarking/text' },
  { title: 'vs Statistical Watermarking', href: '/cryptographic-watermarking/vs-statistical-watermarking' },
];

// Cross-category links
const crossC2paAndCW: RelatedArticle[] = [
  { title: 'C2PA Section A.7', href: '/c2pa-standard/section-a7' },
  { title: 'How Cryptographic Watermarking Works', href: '/cryptographic-watermarking/how-it-works' },
  { title: 'Text Provenance', href: '/content-provenance/text' },
];

/**
 * Get related articles for a given page path.
 * Returns up to 4 articles, excluding the current page.
 */
export function getRelatedArticles(currentPath: string): RelatedArticle[] {
  const pool = articleRelationships[currentPath];
  if (!pool) return [];
  return pool.filter((a) => a.href !== currentPath).slice(0, 4);
}

const articleRelationships: Record<string, RelatedArticle[]> = {
  // C2PA Standard
  '/c2pa-standard/section-a7': [...c2paShared, ...crossC2paAndCW],
  '/c2pa-standard/manifest-structure': [...c2paShared, { title: 'Text Provenance', href: '/content-provenance/text' }],
  '/c2pa-standard/implementation-guide': [...c2paShared, { title: 'Try the Sign/Verify Tool', href: '/tools/sign-verify' }],
  '/c2pa-standard/conformance': [...c2paShared],
  '/c2pa-standard/media-types': [...c2paShared, ...cpFormats],
  '/c2pa-standard/members': [...c2paShared],
  '/c2pa-standard/vs-synthid': [...c2paShared, { title: 'vs Statistical Watermarking', href: '/cryptographic-watermarking/vs-statistical-watermarking' }],

  // Content Provenance - Formats
  '/content-provenance/text': [...cpFormats, ...crossC2paAndCW],
  '/content-provenance/images': [...cpFormats, ...cpAudiences],
  '/content-provenance/audio-video': [...cpFormats, ...cpAudiences],
  '/content-provenance/live-streams': [...cpFormats, ...cpAudiences],

  // Content Provenance - Audiences
  '/content-provenance/for-publishers': [...cpAudiences, ...cpVerticals.slice(0, 2)],
  '/content-provenance/for-enterprises': [...cpAudiences, ...cpCompliance],
  '/content-provenance/for-ai-companies': [...cpAudiences, ...cpCompliance],

  // Content Provenance - Verticals
  '/content-provenance/news-publishers': [...cpVerticals, ...cpAudiences.slice(0, 1)],
  '/content-provenance/enterprise-ai': [...cpVerticals, ...cpCompliance],
  '/content-provenance/academic-publishing': [...cpVerticals, ...cpAudiences.slice(0, 1)],
  '/content-provenance/government': [...cpVerticals, ...cpCompliance],
  '/content-provenance/legal': [...cpVerticals, ...cpCompliance],
  '/content-provenance/music-industry': [...cpVerticals, ...cpFormats.slice(2, 4)],

  // Content Provenance - Compliance and Comparisons
  '/content-provenance/eu-ai-act': [...cpCompliance, ...cpAudiences, { title: 'Legal Implications', href: '/cryptographic-watermarking/legal-implications' }],
  '/content-provenance/verification': [...cpCompliance, ...cpFormats.slice(0, 2), { title: 'Try the Verify Tool', href: '/tools/verify' }],
  '/content-provenance/vs-blockchain': [{ title: 'vs Content Detection', href: '/content-provenance/vs-content-detection' }, ...crossC2paAndCW],
  '/content-provenance/vs-content-detection': [{ title: 'vs Blockchain', href: '/content-provenance/vs-blockchain' }, ...crossC2paAndCW],

  // Cryptographic Watermarking
  '/cryptographic-watermarking/how-it-works': [...cwShared, { title: 'C2PA Section A.7', href: '/c2pa-standard/section-a7' }],
  '/cryptographic-watermarking/survives-distribution': [...cwShared, { title: 'Content Verification', href: '/content-provenance/verification' }],
  '/cryptographic-watermarking/legal-implications': [...cwShared, { title: 'EU AI Act', href: '/content-provenance/eu-ai-act' }],
  '/cryptographic-watermarking/text': [...cwShared, { title: 'Text Provenance', href: '/content-provenance/text' }],
  '/cryptographic-watermarking/vs-statistical-watermarking': [...cwShared, { title: 'Encypher vs SynthID', href: '/c2pa-standard/vs-synthid' }],
};
