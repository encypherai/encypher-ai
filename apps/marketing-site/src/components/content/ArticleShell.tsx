import { ArticleTOC } from './ArticleTOC';
import { RelatedArticles } from './RelatedArticles';
import { getRelatedArticles } from './articleLinks';

interface ArticleShellProps {
  children: React.ReactNode;
  /** Current page path, e.g. "/c2pa-standard/section-a7" */
  path: string;
}

/**
 * Wrapper for article pages that adds:
 * - Sticky sidebar table of contents (xl+ screens)
 * - Related articles block above the existing CTA
 *
 * Usage: replace the outer <div className="container mx-auto px-4 py-16 max-w-4xl">
 * with <ArticleShell path="/c2pa-standard/section-a7">.
 */
export function ArticleShell({ children, path }: ArticleShellProps) {
  const related = getRelatedArticles(path);

  return (
    <div className="container mx-auto px-4 py-16 max-w-5xl xl:max-w-6xl">
      <div className="xl:flex xl:gap-10">
        <div className="max-w-4xl flex-1 min-w-0">
          {children}
          {related.length > 0 && <RelatedArticles articles={related} className="mb-8" />}
        </div>
        <ArticleTOC />
      </div>
    </div>
  );
}
