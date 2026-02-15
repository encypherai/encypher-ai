'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Input } from '@encypher/design-system';
import apiClient from '../../lib/api';
import type { GhostIntegrationResponse } from '../../lib/api';
import { CopyButton } from './CopyButton';

type ViewState = 'loading' | 'disconnected' | 'setup' | 'connected';

function formatLastWebhook(value?: string | null): string {
  if (!value) return 'Never';
  return new Date(value).toLocaleString();
}

export function GhostIntegrationCard() {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const queryClient = useQueryClient();

  const [viewState, setViewState] = useState<ViewState>('loading');
  const [setupStep, setSetupStep] = useState(1);
  const [ghostUrl, setGhostUrl] = useState('');
  const [adminApiKey, setAdminApiKey] = useState('');
  const [error, setError] = useState('');
  const [newToken, setNewToken] = useState<string | null>(null);
  const [newWebhookUrl, setNewWebhookUrl] = useState<string | null>(null);
  const [showDisconnectConfirm, setShowDisconnectConfirm] = useState(false);
  const [showRegenerateConfirm, setShowRegenerateConfirm] = useState(false);

  // Fetch current integration status
  const { data: integration, isLoading, isError } = useQuery({
    queryKey: ['ghost-integration'],
    queryFn: async () => {
      if (!accessToken) return null;
      return apiClient.getGhostIntegration(accessToken);
    },
    enabled: Boolean(accessToken),
  });

  // Sync viewState from query result (v5-compatible — no onSuccess/onError)
  useEffect(() => {
    if (isLoading) return;
    if (viewState === 'setup') return; // Don't interrupt the setup wizard
    if (isError) {
      setViewState('disconnected');
    } else {
      setViewState(integration ? 'connected' : 'disconnected');
    }
  }, [integration, isLoading, isError]);

  // Create integration
  const createMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.createGhostIntegration(accessToken, {
        ghost_url: ghostUrl,
        ghost_admin_api_key: adminApiKey,
      });
    },
    onSuccess: (data) => {
      setNewToken(data.webhook_token);
      setNewWebhookUrl(data.webhook_url);
      setSetupStep(3);
      queryClient.invalidateQueries({ queryKey: ['ghost-integration'] });
    },
    onError: (err: any) => {
      setError(err.message || 'Failed to create integration');
    },
  });

  // Delete integration
  const deleteMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.deleteGhostIntegration(accessToken);
    },
    onSuccess: () => {
      setViewState('disconnected');
      setShowDisconnectConfirm(false);
      setNewToken(null);
      setNewWebhookUrl(null);
      setGhostUrl('');
      setAdminApiKey('');
      queryClient.invalidateQueries({ queryKey: ['ghost-integration'] });
    },
  });

  // Regenerate token
  const regenerateMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.regenerateGhostToken(accessToken);
    },
    onSuccess: (data) => {
      setNewToken(data.webhook_token);
      setNewWebhookUrl(data.webhook_url);
      setShowRegenerateConfirm(false);
      queryClient.invalidateQueries({ queryKey: ['ghost-integration'] });
    },
  });

  const handleSetupSubmit = () => {
    setError('');
    if (!ghostUrl.startsWith('http://') && !ghostUrl.startsWith('https://')) {
      setError('Ghost URL must start with http:// or https://');
      return;
    }
    if (!adminApiKey.includes(':')) {
      setError('Admin API key must be in format {id}:{secret}');
      return;
    }
    createMutation.mutate();
  };

  const handleSetupDone = () => {
    setNewToken(null);
    setNewWebhookUrl(null);
    setViewState('connected');
    setSetupStep(1);
  };

  if (isLoading) {
    return (
      <Card variant="bordered" className="animate-pulse">
        <CardHeader>
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg bg-slate-200 dark:bg-slate-700" />
            <div className="flex-1 space-y-2">
              <div className="h-5 w-24 bg-slate-200 dark:bg-slate-700 rounded" />
              <div className="h-4 w-48 bg-slate-200 dark:bg-slate-700 rounded" />
            </div>
          </div>
        </CardHeader>
      </Card>
    );
  }

  // ── Disconnected state ──
  if (viewState === 'disconnected') {
    return (
      <Card variant="bordered" className="hover:border-blue-ncs/50 transition-all duration-200">
        <CardHeader>
          <div className="flex items-start gap-4">
            <GhostIcon />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <CardTitle className="text-lg">Ghost CMS</CardTitle>
              </div>
              <CardDescription className="mt-1">
                Automatically sign all published Ghost content with C2PA provenance markers.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Button
            variant="primary"
            size="sm"
            onClick={() => setViewState('setup')}
          >
            Connect Ghost
          </Button>
        </CardContent>
      </Card>
    );
  }

  // ── Setup wizard ──
  if (viewState === 'setup') {
    return (
      <Card variant="bordered" className="border-blue-ncs/50 col-span-full lg:col-span-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <GhostIcon />
              <CardTitle className="text-lg">Connect Ghost CMS</CardTitle>
            </div>
            <button
              onClick={() => { setViewState('disconnected'); setSetupStep(1); setError(''); }}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Step indicator */}
          <div className="flex items-center gap-2 mb-6">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex items-center gap-2">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
                    step < setupStep
                      ? 'bg-green-500 text-white'
                      : step === setupStep
                      ? 'bg-blue-ncs text-white'
                      : 'bg-slate-200 dark:bg-slate-700 text-slate-500'
                  }`}
                >
                  {step < setupStep ? (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    step
                  )}
                </div>
                {step < 3 && (
                  <div className={`w-8 h-0.5 ${step < setupStep ? 'bg-green-500' : 'bg-slate-200 dark:bg-slate-700'}`} />
                )}
              </div>
            ))}
          </div>

          {/* Step 1: Ghost URL */}
          {setupStep === 1 && (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-delft-blue dark:text-white mb-1">
                  Step 1: Enter your Ghost URL
                </h3>
                <p className="text-xs text-muted-foreground mb-3">
                  The URL of your Ghost instance (e.g. https://myblog.ghost.io)
                </p>
                <Input
                  placeholder="https://myblog.ghost.io"
                  value={ghostUrl}
                  onChange={(e) => setGhostUrl(e.target.value)}
                />
              </div>
              <Button
                variant="primary"
                size="sm"
                onClick={() => {
                  if (!ghostUrl) { setError('Ghost URL is required'); return; }
                  setError('');
                  setSetupStep(2);
                }}
              >
                Next
              </Button>
              {error && <p className="text-sm text-red-500">{error}</p>}
            </div>
          )}

          {/* Step 2: Admin API Key */}
          {setupStep === 2 && (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-delft-blue dark:text-white mb-1">
                  Step 2: Enter your Ghost Admin API Key
                </h3>
                <p className="text-xs text-muted-foreground mb-3">
                  In Ghost Admin, go to <strong>Settings &rarr; Integrations &rarr; Add custom integration</strong>.
                  Copy the <strong>Admin API Key</strong> (format: <code className="text-xs bg-slate-100 dark:bg-slate-700 px-1 rounded">id:secret</code>).
                </p>
                <Input
                  type="password"
                  placeholder="64f8a1b2c3d4e5f6:a1b2c3d4e5f6..."
                  value={adminApiKey}
                  onChange={(e) => setAdminApiKey(e.target.value)}
                />
              </div>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={() => setSetupStep(1)}>
                  Back
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  loading={createMutation.isPending}
                  onClick={handleSetupSubmit}
                >
                  Connect
                </Button>
              </div>
              {error && <p className="text-sm text-red-500">{error}</p>}
            </div>
          )}

          {/* Step 3: Copy webhook URL */}
          {setupStep === 3 && newWebhookUrl && (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-delft-blue dark:text-white mb-1">
                  Step 3: Add webhooks in Ghost
                </h3>
                <p className="text-xs text-muted-foreground mb-3">
                  In Ghost Admin, go to your custom integration and add webhooks for these events,
                  each pointing to the URL below:
                </p>
                <ul className="text-xs text-muted-foreground mb-3 space-y-1 ml-4 list-disc">
                  <li><code className="bg-slate-100 dark:bg-slate-700 px-1 rounded">Post published</code></li>
                  <li><code className="bg-slate-100 dark:bg-slate-700 px-1 rounded">Published post updated</code> <span className="text-[11px]">(or <code className="bg-slate-100 dark:bg-slate-700 px-1 rounded">Post updated</code> if your Ghost version shows that label)</span></li>
                  <li><code className="bg-slate-100 dark:bg-slate-700 px-1 rounded">Page published</code></li>
                  <li><code className="bg-slate-100 dark:bg-slate-700 px-1 rounded">Published page updated</code> <span className="text-[11px]">(or <code className="bg-slate-100 dark:bg-slate-700 px-1 rounded">Page updated</code>)</span></li>
                </ul>
              </div>

              {/* Webhook URL */}
              <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                <label className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 block">
                  Webhook URL
                </label>
                <div className="flex items-center gap-2">
                  <code className="text-xs flex-1 break-all text-delft-blue dark:text-slate-200 font-mono">
                    {newWebhookUrl}
                  </code>
                  <CopyButton text={newWebhookUrl} />
                </div>
              </div>

              {/* Token warning */}
              <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                <div className="flex gap-2">
                  <svg className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <div>
                    <p className="text-xs font-semibold text-amber-800 dark:text-amber-300">
                      Save this URL now
                    </p>
                    <p className="text-xs text-amber-700 dark:text-amber-400 mt-0.5">
                      The webhook token is only shown once. If you lose it, you can regenerate a new one from the integration settings.
                    </p>
                  </div>
                </div>
              </div>

              <Button variant="primary" size="sm" onClick={handleSetupDone}>
                Done
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  // ── Connected state ──
  return (
    <Card variant="bordered" className="border-green-500/30 overflow-hidden">
      <CardHeader>
        <div className="flex items-start gap-4">
          <GhostIcon />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <CardTitle className="text-lg">Ghost CMS</CardTitle>
              <span className="px-2 py-0.5 text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full">
                Connected
              </span>
            </div>
            <CardDescription className="mt-1 truncate">
              {integration?.ghost_url}
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Stats */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="p-2 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <p className="text-xs text-muted-foreground">Posts signed</p>
            <p className="text-lg font-semibold text-delft-blue dark:text-white">
              {integration?.sign_count || '0'}
            </p>
          </div>
          <div className="p-2 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <p className="text-xs text-muted-foreground">Last webhook</p>
            <p className="text-sm font-medium text-delft-blue dark:text-white">
              {formatLastWebhook(integration?.last_webhook_at)}
            </p>
          </div>
        </div>

        {/* Active webhook URL */}
        <div className="mb-4 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">Configured webhook URL</p>
          <div className="flex items-start gap-2">
            <code className="text-xs flex-1 break-all text-delft-blue dark:text-slate-200 font-mono leading-relaxed">
              {newWebhookUrl || integration?.webhook_url}
            </code>
            <CopyButton text={newWebhookUrl || integration?.webhook_url || ''} />
          </div>
          <p className="text-[11px] text-muted-foreground mt-2">
            In Ghost, use this URL for: Post published, Published post updated, Page published, and Published page updated.
          </p>
        </div>

        {/* Config summary */}
        <div className="text-xs text-muted-foreground space-y-2 mb-4 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
          <p className="leading-relaxed">
            <span className="font-medium">API Key:</span>{' '}
            <code className="bg-slate-100 dark:bg-slate-700 px-1 rounded break-all inline-block max-w-full align-top">
              {integration?.ghost_admin_api_key_masked}
            </code>
          </p>
          <p>
            <span className="font-medium">Mode:</span> <code className="bg-slate-100 dark:bg-slate-700 px-1 rounded">{integration?.manifest_mode}</code> / <code className="bg-slate-100 dark:bg-slate-700 px-1 rounded">{integration?.segmentation_level}</code>
          </p>
          <p>
            <span className="font-medium">Auto-sign:</span>{' '}
            {integration?.auto_sign_on_publish ? 'On publish' : ''}{integration?.auto_sign_on_publish && integration?.auto_sign_on_update ? ' + ' : ''}{integration?.auto_sign_on_update ? 'On update' : ''}
          </p>
        </div>

        {/* New token display (after regeneration) */}
        {newToken && newWebhookUrl && (
          <div className="mb-4 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
            <p className="text-xs font-semibold text-amber-800 dark:text-amber-300 mb-2">
              New webhook URL — update this in Ghost:
            </p>
            <div className="flex items-center gap-2">
              <code className="text-xs flex-1 break-all text-amber-900 dark:text-amber-200 font-mono">
                {newWebhookUrl}
              </code>
              <CopyButton text={newWebhookUrl} />
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-wrap gap-2 items-start">
          {/* Regenerate token */}
          {!showRegenerateConfirm ? (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowRegenerateConfirm(true)}
            >
              Regenerate Token
            </Button>
          ) : (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-muted-foreground">Regenerate token?</span>
              <Button
                variant="destructive"
                size="sm"
                loading={regenerateMutation.isPending}
                onClick={() => regenerateMutation.mutate()}
              >
                Yes, regenerate
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowRegenerateConfirm(false)}
              >
                Cancel
              </Button>
            </div>
          )}

          {/* Disconnect */}
          {!showDisconnectConfirm ? (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowDisconnectConfirm(true)}
              className="text-red-500 hover:text-red-600"
            >
              Disconnect
            </Button>
          ) : (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-red-500">Remove integration?</span>
              <Button
                variant="destructive"
                size="sm"
                loading={deleteMutation.isPending}
                onClick={() => deleteMutation.mutate()}
              >
                Yes, disconnect
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDisconnectConfirm(false)}
              >
                Cancel
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function GhostIcon() {
  return (
    <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center">
      <svg viewBox="0 0 24 24" className="w-8 h-8 text-[#15171A] dark:text-white" fill="currentColor">
        <path d="M12 2C6.477 2 2 6.477 2 12c0 3.89 2.22 7.254 5.467 8.91.054-.964.196-2.594.725-3.942.264-.673 1.703-4.342 1.703-4.342s-.435-.87-.435-2.156c0-2.02 1.17-3.528 2.627-3.528 1.24 0 1.838.93 1.838 2.046 0 1.246-.794 3.11-1.203 4.838-.342 1.446.725 2.626 2.15 2.626 2.58 0 4.31-3.322 4.31-7.257 0-2.99-2.014-5.228-5.683-5.228-4.14 0-6.72 3.088-6.72 6.528 0 1.187.35 2.025.896 2.672.252.298.287.418.196.76-.066.25-.214.853-.275 1.092-.09.35-.362.476-.668.346-1.862-.76-2.728-2.8-2.728-5.094 0-3.79 3.2-8.34 9.543-8.34 5.103 0 8.453 3.692 8.453 7.653 0 5.243-2.913 9.163-7.21 9.163-1.44 0-2.795-.778-3.26-1.662 0 0-.775 3.07-.938 3.66-.288 1.03-.852 2.063-1.37 2.873A11.96 11.96 0 0012 22c5.523 0 10-4.477 10-10S17.523 2 12 2z" />
      </svg>
    </div>
  );
}
