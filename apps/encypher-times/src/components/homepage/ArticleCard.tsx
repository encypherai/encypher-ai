import Link from "next/link";
import type { SignedArticle } from "@/lib/types";
import { formatDateShort, estimateReadingTime } from "@/lib/utils";
import { getSectionBySlug } from "@/lib/sections";

interface ArticleCardProps {
  article: SignedArticle;
  showImage?: boolean;
  compact?: boolean;
}

export function ArticleCard({
  article,
  showImage = true,
  compact = false,
}: ArticleCardProps) {
  const section = getSectionBySlug(article.section);

  if (compact) {
    return (
      <article className="py-3 border-b border-rule-light last:border-b-0">
        <Link href={`/article/${article.slug}`} className="group block">
          {section && (
            <span className={`section-label ${section.accentColor}`}>
              {section.label}
            </span>
          )}
          <h3 className="font-[family-name:var(--font-headline)] text-base font-bold leading-snug mt-1 text-ink group-hover:text-blue-ncs transition-colors">
            {article.headline}
          </h3>
          <p className="font-[family-name:var(--font-ui)] text-xs text-ink-faint mt-1">
            {formatDateShort(article.publishedAt)}
          </p>
        </Link>
      </article>
    );
  }

  return (
    <article className="group">
      {showImage && article.heroImage && (
        <Link href={`/article/${article.slug}`} className="block mb-3">
          <div className="aspect-[16/10] bg-newsprint-warm rounded overflow-hidden">
            <img
              src={`/signed-media/${article.heroImage.filename}`}
              alt={article.heroImage.alt}
              className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-300"
            />
          </div>
        </Link>
      )}

      {section && (
        <span className={`section-label ${section.accentColor}`}>
          {section.label}
        </span>
      )}

      <Link href={`/article/${article.slug}`} className="block mt-1.5">
        <h3 className="font-[family-name:var(--font-headline)] text-lg sm:text-xl font-bold leading-snug text-ink group-hover:text-blue-ncs transition-colors">
          {article.headline}
        </h3>
      </Link>

      <p className="text-sm text-ink-light mt-2 leading-relaxed line-clamp-3">
        {article.teaser}
      </p>

      <div className="font-[family-name:var(--font-ui)] text-xs text-ink-faint mt-2 flex items-center gap-2">
        <span>{article.byline}</span>
        <span aria-hidden="true">|</span>
        <span>{estimateReadingTime(article.wordCount)}</span>
      </div>
    </article>
  );
}
