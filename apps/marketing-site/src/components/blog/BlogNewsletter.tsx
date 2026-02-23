'use client';

import { useState } from 'react';

export function BlogNewsletter() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email) return;

    setStatus('loading');
    setErrorMsg('');

    try {
      const res = await fetch('/api/newsletter/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source: 'blog' }),
      });
      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Subscription failed.');
      }

      setStatus('success');
    } catch (err) {
      setStatus('error');
      setErrorMsg(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
    }
  }

  return (
    <div className="my-12 rounded-xl border border-border bg-muted/40 px-6 py-8 sm:px-10">
      {status === 'success' ? (
        <div className="text-center">
          <p className="text-lg font-semibold">You&apos;re in.</p>
          <p className="mt-1 text-muted-foreground">
            We&apos;ll send the next post straight to your inbox.
          </p>
        </div>
      ) : (
        <>
          <div className="mb-5">
            <p className="text-base font-semibold">Get the weekly Encypher briefing</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Analysis of AI copyright, content provenance, and publisher rights - written from
              inside the C2PA standard-setting process. No filler.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
            <input
              type="email"
              required
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={status === 'loading'}
              className="flex-1 rounded-md border border-input bg-background px-4 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={status === 'loading' || !email}
              className="rounded-md bg-primary px-5 py-2 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50 whitespace-nowrap"
            >
              {status === 'loading' ? 'Subscribing...' : 'Subscribe'}
            </button>
          </form>

          {status === 'error' && (
            <p className="mt-3 text-sm text-destructive">{errorMsg}</p>
          )}
        </>
      )}
    </div>
  );
}
