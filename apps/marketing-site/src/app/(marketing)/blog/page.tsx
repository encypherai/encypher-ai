import { Metadata } from 'next';
import Link from 'next/link';
import Image from 'next/image';
import { getAllPosts, getAllTags, getPostsByTag } from '@/lib/blog';
import { getSiteUrl } from '@/lib/env';
import { generateMetadata as buildMetadata } from '@/lib/seo';
import AISummary from '@/components/seo/AISummary';

export async function generateMetadata({ searchParams }: { searchParams: { tag?: string } }): Promise<Metadata> {
  const siteUrl = getSiteUrl();
  const tag = (await Promise.resolve(searchParams))?.tag;
  if (tag) {
    return buildMetadata(
      `Encypher Blog – Tag: ${tag}`,
      `Articles about ${tag} from the authors of the C2PA Text Standard.`,
      `/blog?tag=${encodeURIComponent(tag)}`,
      undefined,
      [tag]
    );
  }
  return buildMetadata(
    'Encypher Blog – Content Intelligence',
    'From the authors of the C2PA text standard: infrastructure for AI content authentication and licensing.',
    '/blog'
  );
}

export default async function BlogPage({ searchParams }: { searchParams: { tag?: string } }) {
  // Using Promise.resolve to handle searchParams properly
  const resolvedParams = await Promise.resolve(searchParams);
  const selectedTag = resolvedParams?.tag || null;
  
  const allPosts = await getAllPosts();
  const posts = selectedTag ? await getPostsByTag(selectedTag) : allPosts;
  const tags = await getAllTags();
  
  // Get the top 10 most popular tags
  const popularTags = tags.slice(0, 10);

  return (
    <div className="container mx-auto px-4 py-12 md:py-16">
      <AISummary
        title="Encypher Blog – Content Intelligence Insights"
        whatWeDo="Insights from the Co-Chair of the C2PA Text Provenance Task Force on AI content authentication, content attribution, and licensing infrastructure. Standard publishes January 8, 2026."
        whoItsFor="Publishers seeking licensing strategies, AI labs exploring compliance, legal professionals interested in content attribution, and developers building with our API and SDKs."
        keyDifferentiator="Written by the team co-chairing C2PA (c2pa.org) with NYT, BBC, AP, Google, OpenAI, Adobe, Microsoft and others - insider perspective on standards development."
        primaryValue="Stay informed on market licensing frameworks, regulatory developments, and technical innovations in cryptographic watermarking."
        pagePath="/blog"
        pageType="CollectionPage"
      />
      <header className="mb-12 text-center">
        <h1 className="text-4xl md:text-5xl font-bold mb-4"> Encypher Blog</h1>
        <p className="text-xl text-muted-foreground">
          <span className="sm:hidden">From the Authors of the C2PA Text Standard</span>
          <span className="hidden sm:inline">From the Authors of the C2PA Text Standard: Building Infrastructure for the AI Content Economy.</span>
        </p>
      </header>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar with popular tags */}
        <aside className="w-full md:w-64 shrink-0">
          <div className="sticky top-24 bg-card rounded-lg border border-border p-6">
            <h2 className="text-xl font-semibold mb-4">Popular Topics</h2>
            
            <div className="space-y-2">
              <div className={`rounded-md px-3 py-2 transition-colors ${!selectedTag ? 'bg-primary/10 text-primary' : 'hover:bg-muted'}`}>
                <Link href="/blog" className="block">
                  All Topics
                </Link>
              </div>
              
              {popularTags.map(({ tag, count }) => (
                <div 
                  key={tag} 
                  className={`rounded-md px-3 py-2 transition-colors ${selectedTag === tag ? 'bg-primary/10 text-primary' : 'hover:bg-muted'}`}
                >
                  <Link href={`/blog?tag=${encodeURIComponent(tag)}`} className="flex justify-between items-center">
                    <span>{tag}</span>
                    <span className="text-xs bg-muted rounded-full px-2 py-1">{count}</span>
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </aside>
        
        {/* Main content */}
        <div className="flex-1">
          {selectedTag && (
            <div className="mb-8 pb-6 border-b border-border">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-semibold">
                  Posts tagged with: <span className="text-primary">{selectedTag}</span>
                </h2>
                <Link href="/blog" className="text-sm text-primary hover:underline">
                  Clear filter
                </Link>
              </div>
            </div>
          )}
          
          <div className="space-y-12">
            {posts.map((post) => (
              <article key={post.slug} className="border-b border-border pb-10 last:border-0">
                <div className="space-y-6">
                  {post.image && (
                    <Link href={`/blog/${post.slug}`} className="block">
                      <div className="relative w-full aspect-video overflow-hidden rounded-lg mb-4">
                        <Image
                          src={post.image}
                          alt={post.title}
                          fill
                          className="object-cover hover:scale-105 transition-transform duration-300"
                          sizes="(max-width: 768px) 100vw, 768px"
                          priority={posts.indexOf(post) < 2}
                        />
                      </div>
                    </Link>
                  )}
                  
                  <div className="flex items-center text-sm text-muted-foreground">
                    <time dateTime={post.date}>{post.formattedDate}</time>
                    {post.author && (
                      <>
                        <span className="mx-2">•</span>
                        <span>{post.author}</span>
                      </>
                    )}
                  </div>
                  
                  <h2 className="text-2xl md:text-3xl font-bold">
                    <Link 
                      href={`/blog/${post.slug}`}
                      className="hover:text-primary transition-colors"
                    >
                      {post.title}
                    </Link>
                  </h2>
                  
                  <p className="text-muted-foreground text-lg">
                    {post.excerpt}
                  </p>
                  
                  {post.tags && post.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {Array.from(new Set(post.tags)).map((tag) => (
                        <Link 
                          key={tag} 
                          href={`/blog?tag=${encodeURIComponent(tag)}`}
                          className="text-xs bg-muted hover:bg-muted/80 text-muted-foreground px-3 py-1 rounded-full transition-colors"
                        >
                          #{tag}
                        </Link>
                      ))}
                    </div>
                  )}
                  
                  <div>
                    <Link 
                      href={`/blog/${post.slug}`}
                      className="text-primary font-medium hover:underline inline-flex items-center"
                    >
                      Read more
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                      </svg>
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </div>
          
          {posts.length === 0 && (
            <div className="text-center py-12">
              <h2 className="text-2xl font-semibold mb-2">No posts found</h2>
              <p className="text-muted-foreground mb-6">
                {selectedTag 
                  ? `No posts found with the tag "${selectedTag}".` 
                  : "Check back soon for new content!"}
              </p>
              {selectedTag && (
                <Link 
                  href="/blog" 
                  className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90"
                >
                  View all posts
                </Link>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
