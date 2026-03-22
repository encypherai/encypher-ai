import { notFound } from "next/navigation";
import Link from "next/link";
import { getAllSlugs, getArticleBySlug, getArticlesBySection } from "@/lib/content";
import { getSectionBySlug } from "@/lib/sections";
import { ArticleBody } from "@/components/article/ArticleBody";
import { Byline } from "@/components/article/Byline";
import { HeroImage } from "@/components/article/HeroImage";
import { AudioPlayer } from "@/components/article/AudioPlayer";
import { VideoPlayer } from "@/components/article/VideoPlayer";
import { ContentIntegrityBox } from "@/components/ui/ContentIntegrityBox";
import { VerifyWidget } from "@/components/ui/VerifyWidget";
import { ArticleCard } from "@/components/homepage/ArticleCard";

export function generateStaticParams() {
  return getAllSlugs().map((slug) => ({ slug }));
}

interface ArticlePageProps {
  params: Promise<{ slug: string }>;
}

export default async function ArticlePage({ params }: ArticlePageProps) {
  const { slug } = await params;
  const article = getArticleBySlug(slug);

  if (!article) {
    notFound();
  }

  const section = getSectionBySlug(article.section);
  const relatedArticles = getArticlesBySection(article.section)
    .filter((a) => a.slug !== article.slug)
    .slice(0, 3);

  return (
    <article className="py-8 pb-24 max-w-[680px] mx-auto">
      {/* Breadcrumb */}
      <nav className="font-[family-name:var(--font-ui)] text-xs text-ink-faint mb-4">
        <Link href="/" className="hover:text-blue-ncs transition-colors">
          Home
        </Link>
        {section && (
          <>
            <span className="mx-1.5">/</span>
            <Link
              href={`/section/${section.slug}`}
              className="hover:text-blue-ncs transition-colors"
            >
              {section.label}
            </Link>
          </>
        )}
      </nav>

      {/* Headline */}
      <h1 className="font-[family-name:var(--font-headline)] text-3xl sm:text-4xl font-black leading-[1.1] text-ink">
        {article.headline}
      </h1>

      {/* Deck */}
      <p className="text-lg text-ink-light mt-3 leading-relaxed">
        {article.deck}
      </p>

      {/* Byline */}
      <div className="mt-4">
        <Byline
          byline={article.byline}
          dateline={article.dateline}
          publishedAt={article.publishedAt}
          updatedAt={article.updatedAt}
          wordCount={article.wordCount}
        />
      </div>

      {/* Hero image */}
      {article.heroImage && <HeroImage image={article.heroImage} />}

      {/* Article body */}
      <ArticleBody
        paragraphs={article.paragraphs}
        signedText={article.signedText}
      />

      {/* Audio player */}
      {article.audio && <AudioPlayer audio={article.audio} />}

      {/* Video player */}
      {article.video && <VideoPlayer video={article.video} />}

      {/* Content integrity box */}
      <ContentIntegrityBox
        documentId={article.documentId}
        signedAt={article.signedAt}
        merkleRoot={article.merkleRoot}
      />

      {/* Verify widget */}
      <div className="my-8 p-5 border border-rule-light rounded">
        <h3 className="font-[family-name:var(--font-ui)] text-sm font-bold text-ink mb-3">
          Verify Any Sentence
        </h3>
        <p className="font-[family-name:var(--font-ui)] text-xs text-ink-muted mb-4">
          Select any sentence or paragraph above, copy it, and paste it here.
          Encypher will confirm who published it, when it was signed, and
          whether a single character has been changed.
        </p>
        <VerifyWidget />
      </div>

      {/* Tags */}
      {article.tags.length > 0 && (
        <div className="my-6 pt-4 border-t border-rule-light">
          <div className="flex flex-wrap gap-2">
            {article.tags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-0.5 bg-newsprint-warm border border-rule-light rounded font-[family-name:var(--font-ui)] text-[0.625rem] text-ink-faint uppercase tracking-wider"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Related articles */}
      {relatedArticles.length > 0 && (
        <div className="mt-10 pt-6 border-t-2 border-rule">
          <h3 className="section-label text-ink mb-4">
            More in {section?.label}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {relatedArticles.map((a) => (
              <ArticleCard key={a.slug} article={a} showImage={false} />
            ))}
          </div>
        </div>
      )}
    </article>
  );
}
