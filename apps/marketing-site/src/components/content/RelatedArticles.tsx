import Link from 'next/link';

export interface RelatedArticle {
  title: string;
  href: string;
  description?: string;
}

interface RelatedArticlesProps {
  articles: RelatedArticle[];
  className?: string;
}

export function RelatedArticles({ articles, className = '' }: RelatedArticlesProps) {
  if (articles.length === 0) return null;

  return (
    <section className={`border-t pt-8 ${className}`}>
      <h2 className="text-xl font-bold mb-4">Related</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {articles.map((article) => (
          <Link
            key={article.href}
            href={article.href}
            className="group block border border-border rounded-lg p-4 hover:bg-muted/30 transition-colors"
          >
            <p className="text-sm font-medium group-hover:text-foreground transition-colors">
              {article.title}
            </p>
            {article.description && (
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                {article.description}
              </p>
            )}
          </Link>
        ))}
      </div>
    </section>
  );
}
