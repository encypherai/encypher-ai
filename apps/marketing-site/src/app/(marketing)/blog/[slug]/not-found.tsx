import Link from 'next/link';

export default function BlogNotFound() {
  return (
    <div className="container mx-auto px-4 py-24 text-center">
      <h1 className="text-4xl font-bold mb-4">Blog Post Not Found</h1>
      <p className="text-xl text-muted-foreground mb-8">
        Sorry, the blog post you&apos;re looking for doesn&apos;t exist or has been moved.
      </p>
      <Link 
        href="/blog" 
        className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow hover:bg-primary/90"
      >
        Back to Blog
      </Link>
    </div>
  );
}
