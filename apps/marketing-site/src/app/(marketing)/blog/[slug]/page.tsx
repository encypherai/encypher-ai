import { Metadata } from 'next';
import Link from 'next/link';
import Image from 'next/image';
import { notFound } from 'next/navigation';
import { getAllPostSlugs, getPostBySlug } from '@/lib/blog';
import { SocialShare } from '@/components/blog/social-share';
import styles from '../blog.module.css';
import { getSiteUrl } from '@/lib/env';
import Script from 'next/script';
import { getBlogPostSchema } from '@/lib/seo';

// Generate static params for all blog posts
export async function generateStaticParams() {
  const posts = getAllPostSlugs();
  return posts;
}

// Generate metadata for each blog post
export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  // Using Promise.resolve to handle params properly
  const resolvedParams = await Promise.resolve(params);
  const slug = resolvedParams?.slug;
  
  if (!slug) {
    return {
      title: 'Blog Post Not Found',
      description: 'The requested blog post could not be found.'
    };
  }
  
  const post = await getPostBySlug(slug);
  
  if (!post) {
    return {
      title: 'Blog Post Not Found',
      description: 'The requested blog post could not be found.'
    };
  }
  
  const siteUrl = getSiteUrl();

  return {
    title: `${post.title} |  Encypher Blog`,
    description: post.excerpt,
    metadataBase: new URL(siteUrl),
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
      publishedTime: post.date,
      ...(post.image && { 
        images: [
          {
            url: post.image,
            width: 1200,
            height: 675,
            alt: post.title,
          }
        ] 
      }),
      tags: post.tags,
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.excerpt,
      ...(post.image && { images: [post.image] }),
    },
  };
}

export default async function BlogPostPage({
  params,
}: {
  params: { slug: string };
}) {
  // Using Promise.resolve to handle params properly
  const resolvedParams = await Promise.resolve(params);
  const slug = resolvedParams?.slug;
  
  if (!slug) {
    notFound();
  }
  
  const post = await getPostBySlug(slug);

  if (!post) {
    notFound();
  }

  return (
    <article className="container mx-auto px-4 py-12 max-w-4xl">
      <Script
        id="schema-blogpost"
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            getBlogPostSchema({
              title: post.title,
              description: post.excerpt,
              author: post.author || 'Encypher',
              publishDate: post.date,
              imageUrl: post.image,
              url: `${getSiteUrl()}/blog/${post.slug}`,
            })
          ),
        }}
      />
      <Script
        id="schema-breadcrumbs"
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
              {
                "@type": "ListItem",
                "position": 1,
                "name": "Blog",
                "item": `${getSiteUrl()}/blog`
              },
              {
                "@type": "ListItem",
                "position": 2,
                "name": post.title,
                "item": `${getSiteUrl()}/blog/${post.slug}`
              }
            ]
          })
        }}
      />
      <Link 
        href="/blog" 
        className="text-primary hover:underline inline-flex items-center mb-6"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          className="h-4 w-4 mr-1" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M15 19l-7-7 7-7" 
          />
        </svg>
        Back to all posts
      </Link>
      
      <header className="mb-8">
        {post.image && (
          <div className="relative w-full aspect-video mb-8 overflow-hidden rounded-lg">
            <Image
              src={post.image}
              alt={post.title}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, 768px"
              priority
            />
          </div>
        )}
        
        <div className="flex items-center text-sm text-muted-foreground mb-4">
          <time dateTime={post.date}>{post.formattedDate}</time>
          {post.author && (
            <>
              <span className="mx-2">•</span>
              <span>{post.author}</span>
            </>
          )}
        </div>
        
        <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">{post.title}</h1>
        
        <p className="text-xl text-muted-foreground">
          {post.excerpt}
        </p>
        
        <div className="flex flex-wrap items-start justify-between mt-4">
          {post.tags && post.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 flex-1 mr-4">
              {Array.from(new Set(post.tags)).map(tag => (
                <Link 
                  key={tag} 
                  href={`/blog?tag=${encodeURIComponent(tag)}`}
                  className="text-sm bg-muted hover:bg-muted/80 text-muted-foreground px-3 py-1 rounded-full transition-colors"
                >
                  #{tag}
                </Link>
              ))}
            </div>
          )}
          
          <SocialShare 
            url={`/blog/${post.slug}`}
            title={post.title}
            description={post.excerpt}
            className="mt-4 md:mt-0 md:self-end"
          />
        </div>
      </header>
      
      <div 
        className={`prose dark:prose-invert prose-headings:font-semibold prose-a:text-primary max-w-none ${styles.blogContent}`}
        dangerouslySetInnerHTML={{ __html: post.contentHtml || '' }}
      />
      
      <div className="mt-12 pt-6 border-t border-border">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="flex flex-col space-y-4">
            <h3 className="text-sm font-medium text-muted-foreground">Topics</h3>
            <div className="flex flex-wrap gap-2">
              {post.tags && Array.from(new Set(post.tags)).map(tag => (
                <Link 
                  key={tag} 
                  href={`/blog?tag=${encodeURIComponent(tag)}`}
                  className="text-sm bg-muted hover:bg-muted/80 text-muted-foreground px-3 py-1 rounded-full transition-colors"
                >
                  #{tag}
                </Link>
              ))}
            </div>
            
            <div className="mt-auto pt-4">
              <Link 
                href="/blog" 
                className="text-primary hover:underline flex items-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1 rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
                Back to all posts
              </Link>
            </div>
          </div>
          
          <div className="flex flex-col space-y-4 md:items-end">
            <h3 className="text-sm font-medium">Enjoyed this article? Share it!</h3>
            <SocialShare 
              url={`/blog/${post.slug}`}
              title={post.title}
              description={post.excerpt}
            />
          </div>
        </div>
      </div>
    </article>
  );
}
