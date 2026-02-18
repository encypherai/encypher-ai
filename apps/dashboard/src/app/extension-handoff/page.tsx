'use client';

import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from '@encypher/design-system';
import Link from 'next/link';
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

export default function ExtensionHandoffPage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue flex items-center justify-center p-4">
          <Card className="w-full max-w-xl">
            <CardHeader>
              <CardTitle>Preparing extension handoff...</CardTitle>
              <CardDescription>Loading extension setup context.</CardDescription>
            </CardHeader>
          </Card>
        </main>
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

  if (status === 'loading') {
    return (
      <main className="min-h-screen bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue flex items-center justify-center p-4">
        <Card className="w-full max-w-xl">
          <CardHeader>
            <CardTitle>Preparing extension handoff...</CardTitle>
            <CardDescription>Checking your session and extension context.</CardDescription>
          </CardHeader>
        </Card>
      </main>
    );
  }

  if (!accessToken) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue flex items-center justify-center p-4">
        <Card className="w-full max-w-xl">
          <CardHeader>
            <CardTitle>Sign in to connect your extension</CardTitle>
            <CardDescription>One more step and your extension will be ready to sign content.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <Button variant="primary" onClick={() => { window.location.href = loginHref; }}>
              Continue to Login
            </Button>
            <p className="text-xs text-muted-foreground">
              You can also <Link href={loginHref} className="underline">open login in a new tab</Link>.
            </p>
          </CardContent>
        </Card>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-columbia-blue via-blue-ncs to-delft-blue flex items-center justify-center p-4">
      <Card className="w-full max-w-xl">
        <CardHeader>
          <CardTitle>Connect Chrome Extension</CardTitle>
          <CardDescription>
            We can create a signing key and send it securely to your extension in one step.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          {successIdentity ? (
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-emerald-800">
              Connected. Your extension is ready to sign as {successIdentity}.
            </div>
          ) : (
            <Button variant="primary" disabled={loading} onClick={handleCreateAndConnect}>
              {loading ? 'Connecting extension...' : 'Create Key and Connect Extension'}
            </Button>
          )}

          {error && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-amber-900">
              {error}
            </div>
          )}

          {generatedKey && !successIdentity && (
            <div className="rounded-lg border border-border bg-muted/30 p-4">
              <p className="text-sm font-medium mb-2">Fallback: copy key manually</p>
              <code className="block break-all rounded border border-border bg-background px-3 py-2 text-xs">
                {generatedKey}
              </code>
              <Button variant="outline" className="mt-3" onClick={handleCopyFallback}>
                Copy API Key
              </Button>
            </div>
          )}

          {successIdentity && (
            <p className="text-sm text-muted-foreground">
              Return to your browser tab and open the extension popup. You can start signing immediately.
            </p>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
