'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button } from '@encypher/design-system';
import apiClient from '../../lib/api';
import { CopyButton } from './CopyButton';

type ViewState = 'loading' | 'disconnected' | 'setup' | 'connected';

// Cloudflare log fields to select in the Logpush job
const CF_REQUIRED_FIELDS = [
  'ClientIP',
  'ClientRequestHost',
  'ClientRequestURI',
  'ClientRequestMethod',
  'ClientRequestUserAgent',
  'EdgeStartTimestamp',
  'EdgeResponseStatus',
  'ZoneName',
];

// Generate a cryptographically random secret the user can paste into Cloudflare
function generateSecret(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  const arr = new Uint8Array(40);
  crypto.getRandomValues(arr);
  return Array.from(arr, (b) => chars[b % chars.length]).join('');
}

export function CloudflareIntegrationCard() {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const queryClient = useQueryClient();

  const [viewState, setViewState] = useState<ViewState>('loading');
  const [setupStep, setSetupStep] = useState(1);
  const [secret, setSecret] = useState('');
  const [savedWebhookUrl, setSavedWebhookUrl] = useState('');
  const [error, setError] = useState('');
  const [showDisconnectConfirm, setShowDisconnectConfirm] = useState(false);
  const [showRegenerateConfirm, setShowRegenerateConfirm] = useState(false);

  // Fetch current integration status
  const { data: integration, isLoading, isError } = useQuery({
    queryKey: ['cdn-integration-cloudflare'],
    queryFn: async () => {
      if (!accessToken) return null;
      return apiClient.getCdnIntegration(accessToken);
    },
    enabled: Boolean(accessToken),
  });

  // Sync viewState from query
  useEffect(() => {
    if (isLoading) return;
    if (viewState === 'setup') return;
    setViewState(isError || !integration ? 'disconnected' : 'connected');
  }, [integration, isLoading, isError]);

  // Save (create/update) integration
  const saveMutation = useMutation({
    mutationFn: async (generatedSecret?: string) => {
      if (!accessToken) throw new Error('Not authenticated');
      const secretToSave = generatedSecret ?? secret;
      return apiClient.saveCdnIntegration(accessToken, {
        provider: 'cloudflare',
        zone_id: null,
        webhook_secret: secretToSave,
        enabled: true,
      });
    },
    onSuccess: (data, generatedSecret) => {
      if (generatedSecret) {
        setSecret(generatedSecret);
      }
      setSavedWebhookUrl(data.webhook_url);
      setSetupStep(1);
      queryClient.invalidateQueries({ queryKey: ['cdn-integration-cloudflare'] });
    },
    onError: (err: any) => {
      setError(err.message || 'Failed to save integration');
    },
  });

  // Delete integration
  const deleteMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.deleteCdnIntegration(accessToken);
    },
    onSuccess: () => {
      setViewState('disconnected');
      setShowDisconnectConfirm(false);
      setSavedWebhookUrl('');
      setSecret('');
      setSetupStep(1);
      queryClient.invalidateQueries({ queryKey: ['cdn-integration-cloudflare'] });
    },
  });

  // Regenerate: save with a brand-new secret
  const regenerateMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      const newSecret = generateSecret();
      setSecret(newSecret);
      return apiClient.saveCdnIntegration(accessToken, {
        provider: 'cloudflare',
        zone_id: integration?.zone_id ?? null,
        webhook_secret: newSecret,
        enabled: true,
      });
    },
    onSuccess: (data) => {
      setSavedWebhookUrl(data.webhook_url);
      setShowRegenerateConfirm(false);
      queryClient.invalidateQueries({ queryKey: ['cdn-integration-cloudflare'] });
    },
  });

  const handleStartSetup = () => {
    const newSecret = generateSecret();
    setSecret(newSecret);
    setSavedWebhookUrl('');
    setViewState('setup');
    setSetupStep(1);
    setError('');
    saveMutation.mutate(newSecret);
  };

  const handleSetupDone = () => {
    setSavedWebhookUrl('');
    setSecret('');
    setViewState('connected');
    setSetupStep(1);
  };

  // -- Loading --
  if (isLoading) {
    return (
      <Card variant="bordered" className="animate-pulse">
        <CardHeader>
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg bg-slate-200 dark:bg-slate-700" />
            <div className="flex-1 space-y-2">
              <div className="h-5 w-32 bg-slate-200 dark:bg-slate-700 rounded" />
              <div className="h-4 w-56 bg-slate-200 dark:bg-slate-700 rounded" />
            </div>
          </div>
        </CardHeader>
      </Card>
    );
  }

  // -- Disconnected --
  if (viewState === 'disconnected') {
    return (
      <Card variant="bordered" className="hover:border-blue-ncs/50 transition-all duration-200">
        <CardHeader>
          <div className="flex items-start gap-4">
            <CloudflareIcon />
            <div className="flex-1 min-w-0">
              <CardTitle className="text-lg">Cloudflare Logpush</CardTitle>
              <CardDescription className="mt-1">
                Stream CDN access logs to detect every AI bot visiting your site and identify robots.txt bypass attempts.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Button variant="primary" size="sm" onClick={handleStartSetup}>
            Connect Cloudflare
          </Button>
        </CardContent>
      </Card>
    );
  }

  // -- Setup wizard --
  if (viewState === 'setup') {
    return (
      <Card variant="bordered" className="border-blue-ncs/50 col-span-full lg:col-span-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CloudflareIcon />
              <CardTitle className="text-lg">Connect Cloudflare Logpush</CardTitle>
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

          {/* Step 1: Copy destination URL + secret */}
          {setupStep === 1 && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-delft-blue dark:text-white mb-1">
                Step 1: Copy destination URL and secret
              </h3>
              <p className="text-xs text-muted-foreground">
                We generated and saved your webhook secret automatically. Copy both values below into Cloudflare.
              </p>

              {saveMutation.isPending && !savedWebhookUrl ? (
                <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                  <p className="text-xs text-muted-foreground">Generating secure setup values...</p>
                </div>
              ) : (
                <>
                  <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                    <label className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 block">
                      Logpush Destination URL
                    </label>
                    <div className="flex items-center gap-2">
                      <code className="text-xs flex-1 break-all text-delft-blue dark:text-slate-200 font-mono">
                        {savedWebhookUrl}
                      </code>
                      <CopyButton text={savedWebhookUrl} />
                    </div>
                  </div>

                  <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                    <label className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 block">
                      Webhook Secret
                    </label>
                    <div className="flex items-center gap-2">
                      <code className="text-xs flex-1 break-all text-delft-blue dark:text-slate-200 font-mono">
                        {secret}
                      </code>
                      <CopyButton text={secret} />
                    </div>
                  </div>

                  <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                    <div className="flex gap-2">
                      <svg className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <p className="text-xs text-amber-800 dark:text-amber-300">
                        Copy and save this secret now. After setup, Encypher stores it hashed and you cannot retrieve it. You can regenerate a new one at any time.
                      </p>
                    </div>
                  </div>
                </>
              )}

              <Button variant="primary" size="sm" onClick={() => setSetupStep(2)} disabled={!savedWebhookUrl || !secret}>
                Continue to Cloudflare setup
              </Button>
              {error && <p className="text-sm text-red-500">{error}</p>}
            </div>
          )}

          {/* Step 2: Create Logpush job in Cloudflare */}
          {setupStep === 2 && savedWebhookUrl && (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-delft-blue dark:text-white mb-1">
                  Step 2: Create the Logpush job in Cloudflare
                </h3>
                <p className="text-xs text-muted-foreground mb-4">
                  Follow these steps exactly in your Cloudflare dashboard.
                </p>

                <ol className="space-y-4">
                  {/* 3a */}
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-ncs text-white text-[10px] font-bold flex items-center justify-center mt-0.5">1</span>
                    <div>
                      <p className="text-xs font-medium text-slate-800 dark:text-slate-100">Open Logpush</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        In Cloudflare Dashboard &rarr; <strong>Analytics &amp; Logs</strong> &rarr; <strong>Logpush</strong> &rarr; click <strong>Create a Logpush job</strong>.
                      </p>
                    </div>
                  </li>

                  {/* 3b */}
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-ncs text-white text-[10px] font-bold flex items-center justify-center mt-0.5">2</span>
                    <div>
                      <p className="text-xs font-medium text-slate-800 dark:text-slate-100">Select dataset</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Choose <strong>HTTP requests</strong> as the dataset.
                      </p>
                    </div>
                  </li>

                  {/* 3c */}
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-ncs text-white text-[10px] font-bold flex items-center justify-center mt-0.5">3</span>
                    <div>
                      <p className="text-xs font-medium text-slate-800 dark:text-slate-100">Choose destination: HTTPS</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Select <strong>HTTPS</strong> as the destination type and paste in your destination URL:
                      </p>
                      <div className="mt-2 flex items-center gap-2 p-2 bg-slate-100 dark:bg-slate-700 rounded-lg">
                        <code className="text-[11px] flex-1 break-all text-delft-blue dark:text-slate-200 font-mono">
                          {savedWebhookUrl}
                        </code>
                        <CopyButton text={savedWebhookUrl} />
                      </div>
                    </div>
                  </li>

                  {/* 3d */}
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-ncs text-white text-[10px] font-bold flex items-center justify-center mt-0.5">4</span>
                    <div>
                      <p className="text-xs font-medium text-slate-800 dark:text-slate-100">Add custom header</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Under <strong>Custom headers</strong>, add exactly one header:
                      </p>
                      <div className="mt-2 grid grid-cols-2 gap-2">
                        <div className="p-2 bg-slate-100 dark:bg-slate-700 rounded-lg">
                          <p className="text-[10px] text-muted-foreground mb-1">Header name</p>
                          <div className="flex items-center gap-1">
                            <code className="text-[11px] text-delft-blue dark:text-slate-200 font-mono flex-1">x-cf-secret</code>
                            <CopyButton text="x-cf-secret" label="Copy" />
                          </div>
                        </div>
                        <div className="p-2 bg-slate-100 dark:bg-slate-700 rounded-lg">
                          <p className="text-[10px] text-muted-foreground mb-1">Header value</p>
                          <div className="flex items-center gap-1">
                            <code className="text-[11px] text-delft-blue dark:text-slate-200 font-mono flex-1 truncate">{secret || '(your secret from step 1)'}</code>
                            {secret && <CopyButton text={secret} label="Copy" />}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>

                  {/* 3e */}
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-ncs text-white text-[10px] font-bold flex items-center justify-center mt-0.5">5</span>
                    <div>
                      <p className="text-xs font-medium text-slate-800 dark:text-slate-100">Select log fields</p>
                      <p className="text-xs text-muted-foreground mt-0.5 mb-2">
                        Enable these fields (at minimum) in the field selector:
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {CF_REQUIRED_FIELDS.map((field) => (
                          <code key={field} className="text-[11px] px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded font-mono">
                            {field}
                          </code>
                        ))}
                      </div>
                    </div>
                  </li>

                  {/* 3f */}
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-ncs text-white text-[10px] font-bold flex items-center justify-center mt-0.5">6</span>
                    <div>
                      <p className="text-xs font-medium text-slate-800 dark:text-slate-100">Set format to JSON and save</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Make sure the output format is set to <strong>JSON</strong> (one record per line), then click <strong>Save and enable</strong>.
                      </p>
                    </div>
                  </li>
                </ol>
              </div>

              <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <div className="flex gap-2">
                  <svg className="w-4 h-4 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-xs text-green-800 dark:text-green-300">
                    Cloudflare sends logs every 30 seconds when traffic is present. Your first bot detections will appear on the <strong>Provenance Activity</strong> page shortly after the job is active.
                  </p>
                </div>
              </div>

              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={() => setSetupStep(1)}>Back</Button>
                <Button variant="primary" size="sm" onClick={() => setSetupStep(3)}>
                  Done, I saved the job
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Confirmation */}
          {setupStep === 3 && (
            <div className="space-y-4">
              <div className="flex flex-col items-center text-center py-4">
                <div className="w-14 h-14 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mb-4">
                  <svg className="w-7 h-7 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className="text-sm font-semibold text-delft-blue dark:text-white mb-2">
                  Cloudflare Logpush connected
                </h3>
                <p className="text-xs text-muted-foreground max-w-sm">
                  Encypher is ready to receive logs from Cloudflare. Bot detections and bypass alerts will appear on the
                  <strong> Provenance Activity</strong> page once your Logpush job starts sending data.
                </p>
              </div>

              {/* Summary box */}
              <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 text-xs space-y-2">
                <p className="font-medium text-slate-700 dark:text-slate-200">What happens next</p>
                <ul className="text-muted-foreground space-y-1 ml-3 list-disc">
                  <li>Cloudflare pushes HTTP access logs every ~30 seconds</li>
                  <li>Encypher classifies bot user-agents automatically (GPTBot, ClaudeBot, etc.)</li>
                  <li>Bots that skip the RSL protocol check are flagged as bypass attempts</li>
                  <li>All detections appear under <strong>Insights &rarr; Provenance Activity</strong></li>
                </ul>
              </div>

              <Button variant="primary" size="sm" onClick={handleSetupDone}>
                View Provenance Activity
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  // -- Connected state --
  const displayWebhookUrl = savedWebhookUrl || integration?.webhook_url || '';

  return (
    <Card variant="bordered" className="border-green-500/30 overflow-hidden">
      <CardHeader>
        <div className="flex items-start gap-4">
          <CloudflareIcon />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <CardTitle className="text-lg">Cloudflare Logpush</CardTitle>
              <span className="px-2 py-0.5 text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full">
                Connected
              </span>
            </div>
            <CardDescription className="mt-1">
              {integration?.zone_id
                ? `Zone: ${integration.zone_id}`
                : 'Receiving HTTP access logs from Cloudflare'}
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Webhook URL */}
        <div className="mb-4 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Logpush destination URL</p>
          <div className="flex items-start gap-2">
            <code className="text-xs flex-1 break-all text-delft-blue dark:text-slate-200 font-mono leading-relaxed">
              {displayWebhookUrl}
            </code>
            <CopyButton text={displayWebhookUrl} />
          </div>
          <p className="text-[11px] text-muted-foreground mt-2">
            Configure this as the HTTPS destination in your Cloudflare Logpush job, with header{' '}
            <code className="bg-slate-100 dark:bg-slate-700 px-1 rounded">x-cf-secret: &lt;your secret&gt;</code>.
          </p>
        </div>

        {/* New secret alert (after regeneration) */}
        {secret && savedWebhookUrl && (
          <div className="mb-4 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
            <p className="text-xs font-semibold text-amber-800 dark:text-amber-300 mb-2">
              New secret generated - update the x-cf-secret header in Cloudflare:
            </p>
            <div className="flex items-center gap-2">
              <code className="text-xs flex-1 break-all text-amber-900 dark:text-amber-200 font-mono">
                {secret}
              </code>
              <CopyButton text={secret} />
            </div>
          </div>
        )}

        {/* Quick reference fields */}
        <div className="mb-4 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">Required Logpush fields</p>
          <div className="flex flex-wrap gap-1.5">
            {CF_REQUIRED_FIELDS.map((field) => (
              <code key={field} className="text-[11px] px-1.5 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded font-mono">
                {field}
              </code>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-2 items-start">
          {!showRegenerateConfirm ? (
            <Button variant="outline" size="sm" onClick={() => setShowRegenerateConfirm(true)}>
              Regenerate Secret
            </Button>
          ) : (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-muted-foreground">Generate a new secret? You must update the Cloudflare header.</span>
              <Button
                variant="destructive"
                size="sm"
                loading={regenerateMutation.isPending}
                onClick={() => regenerateMutation.mutate()}
              >
                Yes, regenerate
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setShowRegenerateConfirm(false)}>
                Cancel
              </Button>
            </div>
          )}

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
              <Button variant="ghost" size="sm" onClick={() => setShowDisconnectConfirm(false)}>
                Cancel
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function CloudflareIcon() {
  return (
    <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-[#F48120]/10 flex items-center justify-center">
      <svg viewBox="0 0 200 200" className="w-8 h-8" fill="none">
        {/* Cloudflare cloud logo shape */}
        <path
          d="M152.1 117.4c1.1-3.8 1.7-7.8 1.7-12 0-25.3-20.5-45.8-45.8-45.8-20.1 0-37.2 12.9-43.4 30.9-4.1-2.6-8.9-4.1-14.1-4.1-14.3 0-25.9 11.6-25.9 25.9 0 .9.1 1.7.2 2.6C15.2 117.4 8 125.8 8 136c0 11 8.9 19.9 19.9 19.9h120.6c11 0 19.9-8.9 19.9-19.9 0-9.5-6.6-17.5-15.8-19.2-.2-.5-.3-.9-.5-1.4z"
          fill="#F48120"
        />
        <path
          d="M152.1 117.4c1.1-3.8 1.7-7.8 1.7-12 0-.9 0-1.7-.1-2.6-5.2 1.7-11.3 2.7-17.7 2.7-20.3 0-38.2-10.3-48.8-26-8.1 5.5-13.5 14.7-13.5 25.2 0 1.1.1 2.2.2 3.2-1.5-.1-3.1-.2-4.7-.2-9.7 0-18.4 3.6-25 9.5h92.2c5.5 0 10.6-1.4 15.1-3.9-.5 1.4-.9 2.8-1.4 4.1z"
          fill="#FBAD41"
        />
      </svg>
    </div>
  );
}
