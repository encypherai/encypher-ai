'use client';

import { Suspense, useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useSearchParams } from 'next/navigation';
import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from '@encypher/design-system';

const API_BASE =
  (process.env.NEXT_PUBLIC_API_URL || 'https://api.encypher.com/api/v1').replace(/\/$/, '');
const LOGO_WHITE = '/assets/encypher_full_logo_white.svg';

type ConnectState = 'completing' | 'success' | 'error';

function WordPressConnectContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const [state, setState] = useState<ConnectState>('completing');
  const [error, setError] = useState<string>('');
  const [organizationName, setOrganizationName] = useState<string>('');
  const [siteLabel, setSiteLabel] = useState<string>('your WordPress site');

  useEffect(() => {
    if (!token) {
      setState('error');
      setError('No WordPress connection token was provided.');
      return;
    }

    const completeConnection = async () => {
      try {
        setState('completing');
        const response = await fetch(`${API_BASE}/integrations/wordpress/connect/complete`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token }),
        });
        const payload = await response.json();

        if (!response.ok || !payload.success) {
          throw new Error(payload.detail || payload.error?.message || 'Unable to complete the WordPress connection.');
        }

        const data = payload.data || {};
        setOrganizationName(data.organization_name || data.organization_id || 'your Encypher workspace');
        setSiteLabel(data.site_name || data.site_url || 'your WordPress site');
        setState('success');
      } catch (err: any) {
        setError(err?.message || 'Unable to complete the WordPress connection.');
        setState('error');
      }
    };

    completeConnection();
  }, [token]);

  return (
    <main className="min-h-screen bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex justify-center mb-8">
          <Link href="/">
            <span className="sr-only">Encypher</span>
            <Image
              src={LOGO_WHITE}
              alt="Encypher"
              width={180}
              height={45}
              className="h-12 w-auto object-contain"
              priority
            />
          </Link>
        </div>

        <Card className="shadow-2xl">
          <CardHeader className="text-center">
            {state === 'completing' && (
              <>
                <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                  <svg className="w-8 h-8 text-blue-ncs animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                </div>
                <CardTitle className="text-2xl">Connecting WordPress</CardTitle>
                <CardDescription>Please wait while we approve the site and provision its Encypher API key.</CardDescription>
              </>
            )}

            {state === 'success' && (
              <>
                <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <CardTitle className="text-2xl text-green-600">WordPress Approved</CardTitle>
                <CardDescription>
                  {siteLabel} is now connected to {organizationName}. Return to WordPress and keep the settings page open for a few seconds while the plugin finishes polling.
                </CardDescription>
              </>
            )}

            {state === 'error' && (
              <>
                <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                  <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <CardTitle className="text-2xl text-red-600">Connection Failed</CardTitle>
                <CardDescription className="text-red-600/80">{error}</CardDescription>
              </>
            )}
          </CardHeader>

          <CardContent className="space-y-4">
            {state === 'success' && (
              <>
                <p className="text-sm text-muted-foreground text-center">
                  You can close this tab after WordPress shows the connection as complete.
                </p>
                <Button variant="primary" size="lg" fullWidth onClick={() => window.close()}>
                  Close this tab
                </Button>
              </>
            )}

            {state === 'error' && (
              <>
                <p className="text-sm text-muted-foreground text-center">
                  The magic link may have expired or this connection was already completed.
                </p>
                <div className="space-y-2">
                  <Button variant="outline" size="lg" fullWidth onClick={() => window.location.reload()}>
                    Retry
                  </Button>
                  <Link
                    href="/login"
                    className="inline-flex w-full items-center justify-center rounded-md bg-[#1B3A5F] px-4 py-3 text-sm font-medium text-white transition-opacity hover:opacity-90"
                  >
                    Go to Login
                  </Link>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}

export default function WordPressConnectPage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue flex items-center justify-center p-4">
          <div className="w-full max-w-md text-center text-white">
            <div className="animate-spin w-8 h-8 border-4 border-white border-t-transparent rounded-full mx-auto mb-4" />
            <p>Loading...</p>
          </div>
        </main>
      }
    >
      <WordPressConnectContent />
    </Suspense>
  );
}
