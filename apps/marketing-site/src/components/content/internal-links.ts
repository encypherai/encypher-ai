/**
 * Internal link configuration for contextual keyword-rich anchor text.
 * Use these mappings when adding contextual links to pages and blog posts.
 *
 * Convention: first mention of each key term per page should be a link
 * to its canonical destination.
 */
export const internalLinks = {
  // Pillar pages
  'content provenance': '/content-provenance',
  'Content Provenance': '/content-provenance',
  'C2PA': '/c2pa-standard',
  'C2PA standard': '/c2pa-standard',
  'C2PA 2.3': '/c2pa-standard',
  'cryptographic watermarking': '/cryptographic-watermarking',
  'Cryptographic watermarking': '/cryptographic-watermarking',

  // Cluster pages
  'Section A.7': '/c2pa-standard/section-a7',
  'C2PA Section A.7': '/c2pa-standard/section-a7',
  'EU AI Act': '/content-provenance/eu-ai-act',
  'willful infringement': '/cryptographic-watermarking/legal-implications',
  'quote integrity': '/content-provenance/verification',

  // Comparison pages
  'SynthID': '/compare/encypher-vs-synthid',
  'WordProof': '/compare/encypher-vs-wordproof',

  // Glossary
  'C2PA manifest': '/glossary#c2pa-manifest',
  'Merkle tree': '/glossary#merkle-tree-authentication',
  'JUMBF': '/glossary#jumbf',
  'formal notice': '/glossary#formal-notice',

  // Tools and demos
  'verify': '/tools/verify',
  'sign': '/tools/sign',
} as const;

/** Get the canonical URL for a key term */
export function getInternalLinkUrl(term: string): string | undefined {
  return (internalLinks as Record<string, string>)[term];
}
