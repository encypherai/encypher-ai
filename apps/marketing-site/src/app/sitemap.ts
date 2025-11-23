import { type MetadataRoute } from "next";
import { getAllPostSlugs } from "@/lib/blog";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://encypherai.com";
  const now = new Date().toISOString();

  const staticUrls: MetadataRoute.Sitemap = [
    { url: `${base}/`, lastModified: now },
    { url: `${base}/tools`, lastModified: now },
    { url: `${base}/tools/encode`, lastModified: now },
    { url: `${base}/tools/decode`, lastModified: now },
    { url: `${base}/tools/encode-decode`, lastModified: now },
    { url: `${base}/demo`, lastModified: now },
    { url: `${base}/ai-demo`, lastModified: now },
    { url: `${base}/publisher-demo`, lastModified: now },
    { url: `${base}/ai`, lastModified: now },
    { url: `${base}/publishers`, lastModified: now },
    { url: `${base}/enterprises`, lastModified: now },
    { url: `${base}/company`, lastModified: now },
    { url: `${base}/privacy`, lastModified: now },
    { url: `${base}/terms`, lastModified: now },
    { url: `${base}/licensing`, lastModified: now },
    { url: `${base}/blog`, lastModified: now },
    { url: `${base}/ai-detector`, lastModified: now },
    { url: `${base}/deepfake-detection`, lastModified: now },
    { url: `${base}/ai-copyright-infringement`, lastModified: now },
  ];

  const posts = getAllPostSlugs();
  const postUrls: MetadataRoute.Sitemap = posts.map(({ params: { slug } }) => ({
    url: `${base}/blog/${slug}`,
    lastModified: now,
  }));

  return [...staticUrls, ...postUrls];
}
