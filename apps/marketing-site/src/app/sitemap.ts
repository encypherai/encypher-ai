import fs from "fs";
import path from "path";
import { type MetadataRoute } from "next";
import { getAllPostSlugs } from "@/lib/blog";

const BASE = "https://encypher.com";
const APP_DIR = path.join(process.cwd(), "src/app");

// Routes excluded from the sitemap (redirects, private, utility)
const EXCLUDED = new Set([
  "/auth",
  "/admin",
  "/dashboard",
  "/status",
  "/not-found",
  "/newsletter/unsubscribe",
  // Redirects
  "/ai",
  "/publishers",
  // noindex vanity pages
  "/erik",
  // Embed variants
  "/ai-demo/embed",
  "/publisher-demo/embed",
]);
const EXCLUDED_PREFIXES = ["/auth/", "/admin/", "/(embed)"];

// Priority tiers by route pattern
function getPriority(route: string): number {
  if (route === "/") return 1.0;

  // Core conversion pages
  if (
    ["/platform", "/pricing", "/solutions", "/content-provenance",
     "/c2pa-standard", "/cryptographic-watermarking"].includes(route)
  ) return 0.9;

  // Solutions sub-pages
  if (route.startsWith("/solutions/")) return 0.9;

  // High-value landing pages
  if (
    ["/ai-detector", "/deepfake-detection", "/ai-copyright-infringement",
     "/enterprise", "/rights-management", "/blog", "/try",
     "/ai-demo", "/publisher-demo"].includes(route)
  ) return 0.8;

  // Cluster and compare pages
  if (
    route.startsWith("/content-provenance/") ||
    route.startsWith("/c2pa-standard/") ||
    route.startsWith("/cryptographic-watermarking/") ||
    route.startsWith("/compare")
  ) return 0.7;

  // Company, glossary, contact, demo, tools index
  if (
    ["/company", "/contact", "/glossary", "/demo"].includes(route)
  ) return 0.7;

  // Tools sub-pages
  if (route.startsWith("/tools")) return 0.6;

  // Format pages (added separately, but in case they show up here)
  if (route.match(/^\/content-provenance\/[a-z0-9-]+$/)) return 0.6;

  // Author pages
  if (route.startsWith("/authors/")) return 0.5;

  // Legal
  if (["/privacy", "/terms", "/licensing"].includes(route)) return 0.4;

  return 0.6;
}

/**
 * Walk the app directory and find all routes with page.tsx or page.ts files.
 * Handles Next.js conventions: route groups (), dynamic segments [], etc.
 */
function discoverRoutes(dir: string, prefix = ""): string[] {
  const routes: string[] = [];

  let entries: fs.Dirent[];
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return routes;
  }

  // Check if this directory has a page file
  const hasPage = entries.some(
    (e) => e.isFile() && (e.name === "page.tsx" || e.name === "page.ts")
  );
  if (hasPage && prefix !== "") {
    routes.push(prefix);
  } else if (hasPage && prefix === "") {
    routes.push("/");
  }

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;

    const name = entry.name;

    // Skip non-route directories
    if (name.startsWith("_") || name === "api" || name === "node_modules") continue;

    // Skip dynamic segments (handled separately for formats and blog)
    if (name.startsWith("[")) continue;

    // Route groups: strip the group name from the URL
    const segment = name.startsWith("(") ? "" : `/${name}`;
    const fullPath = path.join(dir, name);
    const newPrefix = `${prefix}${segment}`;

    routes.push(...discoverRoutes(fullPath, newPrefix));
  }

  return routes;
}

// Programmatic format pages
const FORMAT_SLUGS = [
  "jpeg", "png", "webp", "tiff", "avif", "heic", "heic-sequence",
  "heif", "heif-sequence", "svg", "dng", "gif", "jxl",
  "wav", "mp3", "m4a", "aac", "flac", "mpa",
  "mp4", "mov", "m4v", "avi",
  "pdf", "epub", "docx", "odt", "oxps",
  "otf", "ttf", "sfnt",
];

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date().toISOString();

  // Auto-discover all static routes
  const discovered = discoverRoutes(APP_DIR);

  // Filter out excluded routes
  const staticRoutes = discovered.filter((route) => {
    if (EXCLUDED.has(route)) return false;
    return !EXCLUDED_PREFIXES.some((p) => route.startsWith(p));
  });

  const staticUrls: MetadataRoute.Sitemap = staticRoutes.map((route) => ({
    url: `${BASE}${route}`,
    lastModified: now,
    priority: getPriority(route),
  }));

  // Programmatic format pages (dynamic [format] segment)
  const formatUrls: MetadataRoute.Sitemap = FORMAT_SLUGS.map((slug) => ({
    url: `${BASE}/content-provenance/${slug}`,
    lastModified: now,
    priority: 0.6,
  }));

  // Dynamic blog posts
  const posts = getAllPostSlugs();
  const postUrls: MetadataRoute.Sitemap = posts.map(({ params: { slug } }) => ({
    url: `${BASE}/blog/${slug}`,
    lastModified: now,
    priority: 0.6,
  }));

  return [...staticUrls, ...formatUrls, ...postUrls];
}
