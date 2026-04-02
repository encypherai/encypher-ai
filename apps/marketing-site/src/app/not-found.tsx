import Link from 'next/link';

export default function NotFound() {
  return (
    <>
      <main className="min-h-[70vh] flex items-center justify-center px-4">
        <div className="max-w-lg w-full text-center">
          <h1 className="text-6xl font-bold text-foreground mb-4">404</h1>
          <p className="text-xl text-muted-foreground mb-8">
            This page does not exist or has been moved.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center mb-12">
            <Link
              href="/"
              className="px-6 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:opacity-90 transition-opacity"
            >
              Back to Home
            </Link>
            <Link
              href="/try"
              className="px-6 py-3 bg-muted text-muted-foreground font-medium rounded-lg hover:bg-muted/80 transition-colors"
            >
              Try Encypher
            </Link>
          </div>

          <div className="border-t border-border pt-8">
            <p className="text-sm text-muted-foreground mb-4">Looking for something specific?</p>
            <div className="flex flex-wrap gap-x-4 gap-y-2 justify-center">
              <Link href="/platform" className="text-sm text-accent hover:underline">Platform</Link>
              <Link href="/pricing" className="text-sm text-accent hover:underline">Pricing</Link>
              <Link href="/content-provenance" className="text-sm text-accent hover:underline">Content Provenance</Link>
              <Link href="/solutions/publishers" className="text-sm text-accent hover:underline">For Publishers</Link>
              <Link href="/enterprise" className="text-sm text-accent hover:underline">Enterprise</Link>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
