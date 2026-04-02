import { type MetadataRoute } from "next";

// AI crawlers that should have full access
const AI_CRAWLERS = [
  "GPTBot",
  "ChatGPT-User",
  "anthropic-ai",
  "Claude-Web",
  "Cohere-ai",
  "CCBot",
  "PerplexityBot",
  "Google-Extended",
  "Bytespider",
  "FacebookBot",
  "Applebot-Extended",
  "Meta-ExternalAgent",
];

const DISALLOWED = [
  "/api/",
  "/dashboard/",
  "/admin/",
  "/auth/",
  "/_next/",
  "/login/",
  "/register/",
  "/forgot-password/",
  "/reset-password/",
];

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      // Default: allow everything except private areas
      {
        userAgent: "*",
        allow: "/",
        disallow: DISALLOWED,
      },
      // Explicit full access for AI crawlers
      ...AI_CRAWLERS.map((crawler) => ({
        userAgent: crawler,
        allow: ["/", "/llms.txt", "/llms-full.txt"],
      })),
    ],
    sitemap: "https://encypher.com/sitemap.xml",
  };
}
