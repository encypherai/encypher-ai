import { type MetadataRoute } from "next";
import { getAllPostSlugs } from "@/lib/blog";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://encypher.com";
  const now = new Date().toISOString();

  const staticUrls: MetadataRoute.Sitemap = [
    // Core
    { url: `${base}/`, lastModified: now, priority: 1.0 },
    { url: `${base}/platform`, lastModified: now, priority: 0.9 },
    { url: `${base}/pricing`, lastModified: now, priority: 0.9 },
    { url: `${base}/solutions`, lastModified: now, priority: 0.9 },
    // Solutions
    { url: `${base}/solutions/publishers`, lastModified: now, priority: 0.9 },
    { url: `${base}/solutions/ai-companies`, lastModified: now, priority: 0.9 },
    { url: `${base}/solutions/enterprises`, lastModified: now, priority: 0.9 },
    // Landing pages (keyword traffic)
    { url: `${base}/ai-detector`, lastModified: now, priority: 0.8 },
    { url: `${base}/deepfake-detection`, lastModified: now, priority: 0.8 },
    { url: `${base}/ai-copyright-infringement`, lastModified: now, priority: 0.8 },
    // Demo & try
    { url: `${base}/ai-demo`, lastModified: now, priority: 0.8 },
    { url: `${base}/publisher-demo`, lastModified: now, priority: 0.8 },
    { url: `${base}/demo`, lastModified: now, priority: 0.7 },
    // Tools
    { url: `${base}/tools`, lastModified: now, priority: 0.7 },
    { url: `${base}/tools/sign`, lastModified: now, priority: 0.6 },
    { url: `${base}/tools/verify`, lastModified: now, priority: 0.6 },
    { url: `${base}/tools/sign-verify`, lastModified: now, priority: 0.6 },
    // Blog
    { url: `${base}/blog`, lastModified: now, priority: 0.8 },
    // Company & info
    { url: `${base}/company`, lastModified: now, priority: 0.7 },
    { url: `${base}/contact`, lastModified: now, priority: 0.7 },
    { url: `${base}/enterprise`, lastModified: now, priority: 0.8 },
    { url: `${base}/rights-management`, lastModified: now, priority: 0.8 },
    { url: `${base}/licensing`, lastModified: now, priority: 0.6 },
    { url: `${base}/privacy`, lastModified: now, priority: 0.4 },
    { url: `${base}/terms`, lastModified: now, priority: 0.4 },
    // Pillar pages
    { url: `${base}/content-provenance`, lastModified: now, priority: 0.9 },
    { url: `${base}/c2pa-standard`, lastModified: now, priority: 0.9 },
    { url: `${base}/cryptographic-watermarking`, lastModified: now, priority: 0.9 },
    // Glossary
    { url: `${base}/glossary`, lastModified: now, priority: 0.7 },
    // Comparison pages
    { url: `${base}/compare`, lastModified: now, priority: 0.7 },
    { url: `${base}/compare/encypher-vs-synthid`, lastModified: now, priority: 0.7 },
    { url: `${base}/compare/encypher-vs-wordproof`, lastModified: now, priority: 0.7 },
    { url: `${base}/compare/encypher-vs-detection-tools`, lastModified: now, priority: 0.7 },
    { url: `${base}/compare/encypher-vs-tollbit`, lastModified: now, priority: 0.7 },
    { url: `${base}/compare/encypher-vs-prorata`, lastModified: now, priority: 0.7 },
    { url: `${base}/compare/c2pa-vs-blockchain`, lastModified: now, priority: 0.7 },
    { url: `${base}/compare/content-provenance-vs-content-detection`, lastModified: now, priority: 0.7 },
    // Content provenance cluster pages
    { url: `${base}/content-provenance/for-publishers`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/for-ai-companies`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/for-enterprises`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/vs-content-detection`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/vs-blockchain`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/eu-ai-act`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/text`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/images`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/audio-video`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/live-streams`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/verification`, lastModified: now, priority: 0.7 },
    // C2PA cluster pages
    { url: `${base}/c2pa-standard/section-a7`, lastModified: now, priority: 0.7 },
    { url: `${base}/c2pa-standard/implementation-guide`, lastModified: now, priority: 0.7 },
    { url: `${base}/c2pa-standard/members`, lastModified: now, priority: 0.7 },
    { url: `${base}/c2pa-standard/vs-synthid`, lastModified: now, priority: 0.7 },
    { url: `${base}/c2pa-standard/manifest-structure`, lastModified: now, priority: 0.7 },
    { url: `${base}/c2pa-standard/media-types`, lastModified: now, priority: 0.7 },
    // Cryptographic watermarking cluster pages
    { url: `${base}/cryptographic-watermarking/how-it-works`, lastModified: now, priority: 0.7 },
    { url: `${base}/cryptographic-watermarking/vs-statistical-watermarking`, lastModified: now, priority: 0.7 },
    { url: `${base}/cryptographic-watermarking/text`, lastModified: now, priority: 0.7 },
    { url: `${base}/cryptographic-watermarking/survives-distribution`, lastModified: now, priority: 0.7 },
    { url: `${base}/cryptographic-watermarking/legal-implications`, lastModified: now, priority: 0.7 },
    // Industry vertical pages
    { url: `${base}/content-provenance/news-publishers`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/academic-publishing`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/music-industry`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/enterprise-ai`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/legal`, lastModified: now, priority: 0.7 },
    { url: `${base}/content-provenance/government`, lastModified: now, priority: 0.7 },
    // Author pages
    { url: `${base}/authors/erik-svilich`, lastModified: now, priority: 0.5 },
    { url: `${base}/authors/matt-kaminsky`, lastModified: now, priority: 0.5 },
  ];

  // Programmatic format pages
  const formatSlugs = [
    'jpeg', 'png', 'webp', 'tiff', 'avif', 'heic', 'heic-sequence',
    'heif', 'heif-sequence', 'svg', 'dng', 'gif', 'jxl',
    'wav', 'mp3', 'm4a', 'aac', 'flac', 'mpa',
    'mp4', 'mov', 'm4v', 'avi',
    'pdf', 'epub', 'docx', 'odt', 'oxps',
    'otf', 'ttf', 'sfnt',
  ];
  const formatUrls: MetadataRoute.Sitemap = formatSlugs.map(slug => ({
    url: `${base}/content-provenance/${slug}`,
    lastModified: now,
    priority: 0.6,
  }));

  const posts = getAllPostSlugs();
  const postUrls: MetadataRoute.Sitemap = posts.map(({ params: { slug } }) => ({
    url: `${base}/blog/${slug}`,
    lastModified: now,
  }));

  return [...staticUrls, ...formatUrls, ...postUrls];
}
