'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000/api/v1'
    : 'https://api.encypherai.com/api/v1');

type State = 'loading' | 'success' | 'error';

function VerifyDomainContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token') ?? '';

  const [state, setState] = useState<State>('loading');

  useEffect(() => {
    if (!token) {
      setState('error');
      return;
    }

    const url = `${API_BASE_URL}/organizations/domain-claims/verify-email?token=${encodeURIComponent(token)}`;
    fetch(url)
      .then((res) => {
        if (res.ok) {
          setState('success');
        } else {
          setState('error');
        }
      })
      .catch(() => setState('error'));
  }, [token]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-columbia-blue/20 via-background to-background px-4">
      <div className="w-full max-w-md rounded-2xl bg-card shadow-2xl border border-border p-8 flex flex-col gap-6">
        <div className="flex justify-center">
          <Image
            src="/assets/encypher_full_logo_color.svg"
            alt="Encypher"
            width={140}
            height={36}
            priority
          />
        </div>

        {state === 'loading' && (
          <div className="text-center space-y-3">
            <div className="w-8 h-8 border-2 border-blue-ncs border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-sm text-muted-foreground">Confirming your request&hellip;</p>
          </div>
        )}

        {state === 'success' && (
          <div className="space-y-4">
            <div className="flex flex-col items-center gap-3 text-center">
              <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                <svg className="w-6 h-6 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h1 className="text-xl font-semibold">Email confirmed</h1>
              <p className="text-sm text-muted-foreground">
                Your domain request has been logged.
              </p>
            </div>
            <div className="rounded-lg border border-border bg-muted/50 p-4 text-sm text-muted-foreground space-y-2">
              <p className="font-medium text-foreground">Next step: add your DNS TXT record</p>
              <p>
                The DNS setup instructions were sent to the email you provided. Add the TXT record
                to your DNS provider, then click <strong>Verify DNS</strong> in your dashboard settings
                to complete verification.
              </p>
            </div>
            <Link
              href="/settings?tab=organization"
              className="flex w-full items-center justify-center rounded-lg bg-blue-ncs text-white font-medium py-2.5 px-4 hover:opacity-90 transition-opacity"
            >
              Go to Settings
            </Link>
          </div>
        )}

        {state === 'error' && (
          <div className="space-y-4">
            <div className="flex flex-col items-center gap-3 text-center">
              <div className="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h1 className="text-xl font-semibold">Link invalid or expired</h1>
              <p className="text-sm text-muted-foreground">
                This link is invalid or has already been used.
              </p>
            </div>
            <Link
              href="/settings?tab=organization"
              className="flex w-full items-center justify-center rounded-lg bg-blue-ncs text-white font-medium py-2.5 px-4 hover:opacity-90 transition-opacity"
            >
              Go to Settings
            </Link>
          </div>
        )}
      </div>
    </main>
  );
}

export default function VerifyDomainPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center">
          <div className="w-8 h-8 border-2 border-blue-ncs border-t-transparent rounded-full animate-spin" />
        </main>
      }
    >
      <VerifyDomainContent />
    </Suspense>
  );
}
