import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-lg w-full text-center">
        <div className="bg-card rounded-2xl shadow-lg border border-border p-8">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-muted flex items-center justify-center">
            <svg className="w-10 h-10 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>

          <h1 className="text-4xl font-bold text-foreground mb-2">404</h1>
          <p className="text-lg text-muted-foreground mb-8">
            This page does not exist or has been moved.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              href="/"
              className="px-6 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:opacity-90 transition-opacity"
            >
              Back to Dashboard
            </Link>
            <Link
              href="/docs"
              className="px-6 py-3 bg-muted text-muted-foreground font-medium rounded-lg hover:bg-muted/80 transition-colors"
            >
              View Documentation
            </Link>
          </div>

          <div className="mt-8 pt-6 border-t border-border">
            <p className="text-sm text-muted-foreground mb-3">Quick links</p>
            <div className="flex flex-wrap gap-2 justify-center">
              <Link href="/playground" className="text-sm text-accent hover:underline">API Playground</Link>
              <span className="text-muted-foreground">|</span>
              <Link href="/api-keys" className="text-sm text-accent hover:underline">API Keys</Link>
              <span className="text-muted-foreground">|</span>
              <Link href="/integrations" className="text-sm text-accent hover:underline">Integrations</Link>
              <span className="text-muted-foreground">|</span>
              <Link href="/settings" className="text-sm text-accent hover:underline">Settings</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
