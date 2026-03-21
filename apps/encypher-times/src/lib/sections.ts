export interface Section {
  slug: string;
  label: string;
  accentColor: string;
}

export const SECTIONS: Section[] = [
  { slug: "technology", label: "Technology", accentColor: "text-section-technology" },
  { slug: "policy", label: "Policy", accentColor: "text-section-policy" },
  { slug: "media", label: "Media & Trust", accentColor: "text-section-media" },
  { slug: "analysis", label: "Analysis", accentColor: "text-section-analysis" },
  { slug: "opinion", label: "Opinion", accentColor: "text-section-opinion" },
];

export function getSectionBySlug(slug: string): Section | undefined {
  return SECTIONS.find((s) => s.slug === slug);
}
