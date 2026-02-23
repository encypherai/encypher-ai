import { type MetadataRoute } from "next";
import { getAllPostSlugs } from "@/lib/blog";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://encypherai.com";
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
  ];

  const posts = getAllPostSlugs();
  const postUrls: MetadataRoute.Sitemap = posts.map(({ params: { slug } }) => ({
    url: `${base}/blog/${slug}`,
    lastModified: now,
  }));

  return [...staticUrls, ...postUrls];
}
