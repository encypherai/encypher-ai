import Link from "next/link";
import type { SignedArticle } from "@/lib/types";
import { getSectionBySlug } from "@/lib/sections";
import { estimateReadingTime } from "@/lib/utils";

interface LeadStoryProps {
  article: SignedArticle;
}

export function LeadStory({ article }: LeadStoryProps) {
  const section = getSectionBySlug(article.section);

  return (
    <article className="group">
      {/* Hero image */}
      {article.heroImage && (
        <Link href={`/article/${article.slug}`} className="block mb-4">
          <div className="aspect-[16/9] bg-newsprint-warm overflow-hidden">
            <img
              src={`/signed-media/${article.heroImage.filename}`}
              alt={article.heroImage.alt}
              className="w-full h-full object-cover group-hover:scale-[1.01] transition-transform duration-500"
            />
          </div>
          {article.heroImage.caption && (
            <p className="font-[family-name:var(--font-ui)] text-xs text-ink-faint mt-1.5">
              {article.heroImage.caption}{" "}
              <span className="italic">{article.heroImage.credit}</span>
            </p>
          )}
        </Link>
      )}

      {/* Section label */}
      {section && (
        <span className={`section-label ${section.accentColor}`}>
          {section.label}
        </span>
      )}

      {/* Headline */}
      <Link href={`/article/${article.slug}`} className="block mt-2">
        <h2 className="font-[family-name:var(--font-headline)] text-2xl sm:text-3xl lg:text-4xl font-black leading-[1.1] text-ink group-hover:text-blue-ncs transition-colors">
          {article.headline}
        </h2>
      </Link>

      {/* Deck */}
      <p className="text-lg text-ink-light mt-3 leading-relaxed">
        {article.deck}
      </p>

      {/* Byline */}
      <div className="font-[family-name:var(--font-ui)] text-xs text-ink-faint mt-3 flex items-center gap-2">
        <span>{article.byline}</span>
        <span aria-hidden="true">|</span>
        <span>{article.dateline}</span>
        <span aria-hidden="true">|</span>
        <span>{estimateReadingTime(article.wordCount)}</span>
      </div>
    </article>
  );
}
