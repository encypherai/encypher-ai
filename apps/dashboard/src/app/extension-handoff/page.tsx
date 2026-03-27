'use client';

import { Button } from '@encypher/design-system';
import Link from 'next/link';
import Image from 'next/image';
import { useSession } from 'next-auth/react';
import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { toast } from 'sonner';
import apiClient from '../../lib/api';
import { useOrganization } from '../../contexts/OrganizationContext';

type RuntimeSendResponse = {
  success?: boolean;
  error?: string;
  identity?: string;
};

type RuntimeLike = {
  sendMessage?: (
    extensionId: string,
    message: Record<string, unknown>,
    callback: (response?: RuntimeSendResponse) => void
  ) => void;
  lastError?: { message?: string };
};

function extractFullKey(payload: unknown): string {
  const data = payload as {
    data?: {
      key?: string;
      api_key?: string;
      token?: string;
    };
    key?: string;
    api_key?: string;
    token?: string;
  };

  return (
    data?.data?.key ||
    data?.data?.api_key ||
    data?.data?.token ||
    data?.key ||
    data?.api_key ||
    data?.token ||
    ''
  );
}

const LOGO_WHITE = '/assets/wordmark-white-nobg.svg';

function HandoffShell({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen bg-delft-blue flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-md flex flex-col gap-8">
        <div className="flex justify-center">
          <Image src={LOGO_WHITE} alt="Encypher" width={180} height={40} priority />
        </div>
        {children}
      </div>
    </main>
  );
}

export default function ExtensionHandoffPage() {
  return (
    <Suspense
      fallback={
        <HandoffShell>
          <div className="rounded-2xl bg-white/10 border border-white/20 p-8 text-center">
            <p className="text-columbia-blue text-sm">Loading extension setup context...</p>
          </div>
        </HandoffShell>
      }
    >
      <ExtensionHandoffContent />
    </Suspense>
  );
}

function sendHandoffToExtension(extensionId: string, apiKey: string): Promise<RuntimeSendResponse> {
  return new Promise((resolve) => {
    if (typeof window === 'undefined') {
      resolve({ success: false, error: 'Window context is unavailable.' });
      return;
    }

    const runtime = (window as Window & { chrome?: { runtime?: RuntimeLike } }).chrome?.runtime;
    if (!runtime?.sendMessage) {
      resolve({ success: false, error: 'Chrome runtime messaging is unavailable in this browser.' });
      return;
    }

    runtime.sendMessage(
      extensionId,
      {
        type: 'DASHBOARD_API_KEY_HANDOFF',
        apiKey,
      },
      (response) => {
        const runtimeError = runtime.lastError?.message;
        if (runtimeError) {
          resolve({ success: false, error: runtimeError });
          return;
        }
        resolve(response || { success: false, error: 'No response from extension.' });
      }
    );
  });
}

function ExtensionHandoffContent() {
  const searchParams = useSearchParams();
  const { data: session, status } = useSession();
  const { activeOrganization, isLoading: orgLoading } = useOrganization();
  const accessToken = (session?.user as { accessToken?: string } | undefined)?.accessToken;
  const extensionId = searchParams.get('extensionId') || '';
  const source = searchParams.get('source') || '';

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successIdentity, setSuccessIdentity] = useState('');
  const [generatedKey, setGeneratedKey] = useState('');
  const [countdown, setCountdown] = useState<number | null>(null);
  const [closeFailed, setCloseFailed] = useState(false);
  const autoRunRef = useRef(false);

  const loginHref = useMemo(() => {
    const params = new URLSearchParams();
    if (source) params.set('source', source);
    if (extensionId) params.set('extensionId', extensionId);
    params.set('callbackUrl', `/extension-handoff?${params.toString()}`);
    return `/login?${params.toString()}`;
  }, [extensionId, source]);

  const handleCopyFallback = useCallback(async () => {
    if (!generatedKey) return;
    await navigator.clipboard.writeText(generatedKey);
    toast.success('API key copied. Paste it into the extension popup to finish setup.');
  }, [generatedKey]);

  const handleCreateAndConnect = useCallback(async () => {
    if (!accessToken) {
      setError('You must be signed in before connecting the extension.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await apiClient.createApiKey(
        accessToken,
        'Encypher Verify Extension Key',
        ['sign', 'verify', 'read'],
        activeOrganization?.id ?? null
      );
      const fullKey = extractFullKey(response);
      if (!fullKey) {
        throw new Error('Could not create an API key for extension setup.');
      }

      setGeneratedKey(fullKey);

      if (!extensionId) {
        setError('Extension ID missing. Copy the key and paste it into the extension popup.');
        return;
      }

      const handoffResult = await sendHandoffToExtension(extensionId, fullKey);
      if (!handoffResult?.success) {
        throw new Error(
          handoffResult?.error ||
          'Could not deliver the API key directly to the extension. Copy and paste fallback is available below.'
        );
      }

      setSuccessIdentity(handoffResult.identity || 'your organization');
      toast.success('Extension connected successfully. You can start signing immediately.');
      setCountdown(3);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Extension handoff failed.';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [accessToken, activeOrganization?.id, extensionId]);

  useEffect(() => {
    if (autoRunRef.current) return;
    // Wait for org context to finish loading so activeOrganization?.id is available.
    // Without this guard, key creation races the org fetch and sends no organization_id.
    if (!accessToken || !extensionId || status !== 'authenticated' || orgLoading) return;
    autoRunRef.current = true;
    handleCreateAndConnect();
  }, [accessToken, extensionId, handleCreateAndConnect, orgLoading, status]);

  useEffect(() => {
    if (countdown === null) return;
    if (countdown === 0) {
      window.close();
      // Detect if close was blocked (tab still open after a tick)
      setTimeout(() => {
        try {
          if (!window.closed) setCloseFailed(true);
        } catch {
          setCloseFailed(true);
        }
      }, 300);
      return;
    }
    const timer = setTimeout(() => setCountdown((c) => (c !== null ? c - 1 : null)), 1000);
    return () => clearTimeout(timer);
  }, [countdown]);

  if (status === 'loading') {
    return (
      <HandoffShell>
        <div className="rounded-2xl bg-white/10 border border-white/20 p-8 text-center">
          <p className="text-columbia-blue text-sm">Checking your session...</p>
        </div>
      </HandoffShell>
    );
  }

  if (!accessToken) {
    return (
      <HandoffShell>
        <div className="rounded-2xl bg-white/10 border border-white/20 p-8 flex flex-col gap-6">
          <div>
            <h1 className="text-white text-xl font-bold mb-1">Sign in to connect your extension</h1>
            <p className="text-columbia-blue text-sm">One more step and your extension will be ready to sign content.</p>
          </div>
          <Button variant="primary" onClick={() => { window.location.href = loginHref; }}>
            Continue to Login
          </Button>
          <p className="text-xs text-columbia-blue/70 text-center">
            You can also{' '}
            <Link href={loginHref} className="underline text-columbia-blue hover:text-white transition-colors">
              open login in a new tab
            </Link>
            .
          </p>
        </div>
      </HandoffShell>
    );
  }

  return (
    <HandoffShell>
      <div className="rounded-2xl bg-white/10 border border-white/20 p-8 flex flex-col gap-6">
        <div>
          <h1 className="text-white text-xl font-bold mb-1">Connect Chrome Extension</h1>
          <p className="text-columbia-blue text-sm">
            We can create a signing key and send it securely to your extension in one step.
          </p>
        </div>

        {successIdentity ? (
          <div className="flex flex-col gap-4">
            <div className="rounded-xl border border-cyber-teal/40 bg-cyber-teal/10 px-4 py-4 flex items-start gap-3">
              <svg className="w-5 h-5 text-cyber-teal mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium text-sm">
                  Connected. Your extension is ready to sign as{' '}
                  <span className="text-cyber-teal">{successIdentity}</span>.
                </p>
                {countdown !== null && !closeFailed && (
                  <p className="text-columbia-blue/70 text-xs mt-1 tabular-nums">
                    This tab will close in {countdown}s...
                  </p>
                )}
                {closeFailed && (
                  <p className="text-columbia-blue/70 text-xs mt-1">
                    You can close this tab now. Open the extension popup to start signing.
                  </p>
                )}
              </div>
            </div>
            {!closeFailed && countdown === null && (
              <p className="text-columbia-blue/70 text-xs text-center">
                Open the extension popup to start signing immediately.
              </p>
            )}
          </div>
        ) : (
          <Button variant="primary" disabled={loading} onClick={handleCreateAndConnect}>
            {loading ? 'Connecting extension...' : 'Create Key and Connect Extension'}
          </Button>
        )}

        {error && (
          <div className="rounded-xl border border-amber-400/40 bg-amber-400/10 px-4 py-3 text-amber-200 text-sm">
            {error}
          </div>
        )}

        {generatedKey && !successIdentity && (
          <div className="rounded-xl border border-white/20 bg-white/5 p-4 flex flex-col gap-3">
            <p className="text-columbia-blue text-xs font-medium uppercase tracking-wide">Manual fallback — copy key</p>
            <code className="block break-all rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-xs text-columbia-blue font-mono">
              {generatedKey}
            </code>
            <Button variant="outline" onClick={handleCopyFallback}>
              Copy API Key
            </Button>
          </div>
        )}
      </div>
    </HandoffShell>
  );
}
