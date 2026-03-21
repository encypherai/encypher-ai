import type { SignedArticle } from "@/lib/types";
import { ArticleCard } from "./ArticleCard";

interface SidebarStoriesProps {
  articles: SignedArticle[];
}

export function SidebarStories({ articles }: SidebarStoriesProps) {
  return (
    <aside className="border-t border-rule lg:border-t-0 lg:border-l lg:pl-6 pt-4 lg:pt-0">
      <h3 className="section-label text-ink mb-2">Latest</h3>
      <div>
        {articles.map((article) => (
          <ArticleCard key={article.slug} article={article} compact />
        ))}
      </div>
    </aside>
  );
}
