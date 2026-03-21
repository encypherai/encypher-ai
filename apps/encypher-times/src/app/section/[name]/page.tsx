import { notFound } from "next/navigation";
import { SECTIONS, getSectionBySlug } from "@/lib/sections";
import { getArticlesBySection } from "@/lib/content";
import type { SectionSlug } from "@/lib/types";
import { ArticleCard } from "@/components/homepage/ArticleCard";
import { LeadStory } from "@/components/homepage/LeadStory";

export function generateStaticParams() {
  return SECTIONS.map((s) => ({ name: s.slug }));
}

interface SectionPageProps {
  params: Promise<{ name: string }>;
}

export default async function SectionPage({ params }: SectionPageProps) {
  const { name } = await params;
  const section = getSectionBySlug(name);

  if (!section) {
    notFound();
  }

  const articles = getArticlesBySection(name as SectionSlug);

  if (articles.length === 0) {
    notFound();
  }

  const lead = articles[0];
  const rest = articles.slice(1);

  return (
    <div className="py-6">
      {/* Section header */}
      <div className="rule-heavy pt-3 mb-6">
        <h1
          className={`font-[family-name:var(--font-headline)] text-2xl sm:text-3xl font-black ${section.accentColor}`}
        >
          {section.label}
        </h1>
      </div>

      {/* Lead story */}
      <div className="mb-8 pb-8 border-b border-rule-light">
        <LeadStory article={lead} />
      </div>

      {/* Remaining articles */}
      {rest.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {rest.map((article) => (
            <ArticleCard key={article.slug} article={article} />
          ))}
        </div>
      )}
    </div>
  );
}
