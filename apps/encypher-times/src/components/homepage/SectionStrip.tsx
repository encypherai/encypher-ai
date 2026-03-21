import Link from "next/link";
import type { SignedArticle } from "@/lib/types";
import type { Section } from "@/lib/sections";
import { ArticleCard } from "./ArticleCard";

interface SectionStripProps {
  section: Section;
  articles: SignedArticle[];
}

export function SectionStrip({ section, articles }: SectionStripProps) {
  if (articles.length === 0) return null;

  return (
    <section className="py-6">
      {/* Section header */}
      <div className="flex items-center justify-between mb-4 rule-section pt-3">
        <h2 className={`section-label ${section.accentColor} mt-2`}>
          {section.label}
        </h2>
        <Link
          href={`/section/${section.slug}`}
          className="font-[family-name:var(--font-ui)] text-xs text-ink-faint hover:text-blue-ncs transition-colors mt-2"
        >
          See all
        </Link>
      </div>

      {/* Articles grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {articles.slice(0, 3).map((article) => (
          <ArticleCard key={article.slug} article={article} />
        ))}
      </div>
    </section>
  );
}
