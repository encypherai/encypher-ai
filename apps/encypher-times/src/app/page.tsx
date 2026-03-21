import { getAllArticles, getFeaturedArticle, getArticlesBySection } from "@/lib/content";
import { SECTIONS } from "@/lib/sections";
import { LeadStory } from "@/components/homepage/LeadStory";
import { SidebarStories } from "@/components/homepage/SidebarStories";
import { SectionStrip } from "@/components/homepage/SectionStrip";

export default function HomePage() {
  const allArticles = getAllArticles();
  const featured = getFeaturedArticle() || allArticles[0];
  const remaining = allArticles.filter((a) => a.slug !== featured?.slug);

  // Sidebar: next 3 most recent articles
  const sidebarArticles = remaining.slice(0, 3);

  // Section strips: group remaining articles by section
  const sectionArticles = SECTIONS.map((section) => ({
    section,
    articles: getArticlesBySection(section.slug as "technology" | "policy" | "media" | "analysis" | "opinion"),
  })).filter(({ articles }) => articles.length > 0);

  return (
    <div className="py-6">
      {/* Lead story + sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-8 pb-8 border-b border-rule-light">
        {featured && <LeadStory article={featured} />}
        <SidebarStories articles={sidebarArticles} />
      </div>

      {/* Section strips */}
      {sectionArticles.map(({ section, articles }) => (
        <SectionStrip
          key={section.slug}
          section={section}
          articles={articles}
        />
      ))}
    </div>
  );
}
