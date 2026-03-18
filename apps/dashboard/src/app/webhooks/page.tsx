'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { toast } from 'sonner';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Input,
  Badge,
} from '@encypher/design-system';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import apiClient from '../../lib/api';
import type { WebhookSummary } from '../../lib/api';

const availableEvents = [
  // Document events
  { id: 'document.signed', label: 'Document Signed', description: 'When content is signed via API', group: 'Document' },
  { id: 'document.verified', label: 'Document Verified', description: 'When content verification is requested', group: 'Document' },
  { id: 'document.revoked', label: 'Document Revoked', description: 'When a signed document is revoked', group: 'Document' },
  { id: 'document.reinstated', label: 'Document Reinstated', description: 'When a revoked document is reinstated', group: 'Document' },
  // Quota events
  { id: 'quota.warning', label: 'Quota Warning', description: 'When usage approaches the plan limit', group: 'Quota' },
  { id: 'quota.exceeded', label: 'Quota Exceeded', description: 'When usage exceeds the plan limit', group: 'Quota' },
  // Key events
  { id: 'key.created', label: 'Key Created', description: 'When a new API key is generated', group: 'API Keys' },
  { id: 'key.revoked', label: 'Key Revoked', description: 'When an API key is revoked', group: 'API Keys' },
  { id: 'key.rotated', label: 'Key Rotated', description: 'When an API key is rotated', group: 'API Keys' },
  // Rights events
  { id: 'rights.profile.updated', label: 'Rights Profile Updated', description: 'When a rights profile is modified', group: 'Rights' },
  { id: 'rights.notice.delivered', label: 'Rights Notice Delivered', description: 'When a formal notice is sent', group: 'Rights' },
  { id: 'rights.licensing.request_received', label: 'Licensing Request Received', description: 'When a new licensing request arrives', group: 'Rights' },
  { id: 'rights.licensing.agreement_created', label: 'Licensing Agreement Created', description: 'When a licensing agreement is finalized', group: 'Rights' },
  { id: 'rights.detection.event', label: 'Detection Event', description: 'When unauthorized content use is detected', group: 'Rights' },
];

const eventGroups = ['Document', 'Quota', 'API Keys', 'Rights'] as const;

export default function WebhooksPage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as Record<string, unknown>)?.accessToken as string | undefined;
  const queryClient = useQueryClient();

  const [isCreating, setIsCreating] = useState(false);
  const [newUrl, setNewUrl] = useState('');
  const [newSecret, setNewSecret] = useState('');
  const [selectedEvents, setSelectedEvents] = useState<string[]>([]);
  const [testingId, setTestingId] = useState<string | null>(null);

  const webhooksQuery = useQuery({
    queryKey: ['webhooks'],
    queryFn: async () => {
      if (!accessToken) throw new Error('No access token');
      const result = await apiClient.listWebhooks(accessToken);
      return result.webhooks;
    },
    enabled: Boolean(accessToken),
  });

  const createWebhookMutation = useMutation({
    mutationFn: async (data: { url: string; events: string[]; secret?: string }) => {
      if (!accessToken) throw new Error('No access token');
      return apiClient.createWebhook(accessToken, data);
    },
    onSuccess: () => {
      toast.success('Webhook created successfully');
      setIsCreating(false);
      setNewUrl('');
      setNewSecret('');
      setSelectedEvents([]);
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create webhook');
    },
  });

  const deleteWebhookMutation = useMutation({
    mutationFn: async (id: string) => {
      if (!accessToken) throw new Error('No access token');
      return apiClient.deleteWebhook(accessToken, id);
    },
    onSuccess: () => {
      toast.success('Webhook deleted');
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete webhook');
    },
  });

  const toggleWebhookMutation = useMutation({
    mutationFn: async ({ id, is_active }: { id: string; is_active: boolean }) => {
      if (!accessToken) throw new Error('No access token');
      return apiClient.updateWebhook(accessToken, id, { is_active });
    },
    onSuccess: (_, { is_active }) => {
      toast.success(`Webhook ${is_active ? 'enabled' : 'disabled'}`);
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update webhook');
    },
  });

  const testWebhookMutation = useMutation({
    mutationFn: async (id: string) => {
      if (!accessToken) throw new Error('No access token');
      return apiClient.testWebhook(accessToken, id);
    },
    onMutate: (id: string) => {
      setTestingId(id);
    },
    onSuccess: (result) => {
      if (result.success) {
        toast.success(`Test successful (${result.status_code || 'OK'}, ${result.response_time_ms ?? '?'}ms)`);
      } else {
        toast.error(`Test failed: ${result.error || 'Unknown error'}`);
      }
      setTestingId(null);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to send test');
      setTestingId(null);
    },
  });

  const webhooks: WebhookSummary[] = webhooksQuery.data ?? [];
  const isLoading = status === 'loading' || webhooksQuery.isLoading;

  const handleCreateWebhook = () => {
    if (!newUrl.trim()) {
      toast.error('Please enter a webhook URL');
      return;
    }
    if (selectedEvents.length === 0) {
      toast.error('Please select at least one event');
      return;
    }
    try {
      new URL(newUrl);
    } catch {
      toast.error('Please enter a valid URL');
      return;
    }
    const payload: { url: string; events: string[]; secret?: string } = {
      url: newUrl,
      events: selectedEvents,
    };
    if (newSecret.trim()) {
      payload.secret = newSecret.trim();
    }
    createWebhookMutation.mutate(payload);
  };

  const toggleEvent = (eventId: string) => {
    setSelectedEvents(prev =>
      prev.includes(eventId)
        ? prev.filter(e => e !== eventId)
        : [...prev, eventId]
    );
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-delft-blue dark:text-white">Webhooks</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Receive real-time notifications when events happen in your account.
            </p>
          </div>
          {!isCreating && (
            <Button variant="primary" onClick={() => setIsCreating(true)}>
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Webhook
            </Button>
          )}
        </div>

        {/* Create Webhook Form */}
        {isCreating && (
          <Card className="mb-6 border-2 border-blue-ncs/20">
            <CardHeader>
              <CardTitle>Create New Webhook</CardTitle>
              <CardDescription>
                Configure a webhook endpoint to receive event notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* URL Input */}
              <div>
                <label className="block text-sm font-medium mb-2">Endpoint URL</label>
                <Input
                  type="url"
                  placeholder="https://your-server.com/webhook"
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Must be a valid HTTPS URL that can receive POST requests
                </p>
              </div>

              {/* Secret Input */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Signing Secret <span className="text-muted-foreground font-normal">(optional)</span>
                </label>
                <Input
                  type="password"
                  placeholder="whsec_..."
                  value={newSecret}
                  onChange={(e) => setNewSecret(e.target.value)}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Used to sign webhook payloads with HMAC-SHA256 so you can verify authenticity.
                  Leave blank to auto-generate.
                </p>
              </div>

              {/* Event Selection */}
              <div>
                <label className="block text-sm font-medium mb-3">Events to Subscribe</label>
                <div className="space-y-4">
                  {eventGroups.map((group) => {
                    const groupEvents = availableEvents.filter(e => e.group === group);
                    return (
                      <div key={group}>
                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">{group}</p>
                        <div className="space-y-2">
                          {groupEvents.map((event) => (
                            <label
                              key={event.id}
                              className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                                selectedEvents.includes(event.id)
                                  ? 'border-blue-ncs bg-blue-ncs/5'
                                  : 'border-slate-200 hover:border-slate-300'
                              }`}
                            >
                              <input
                                type="checkbox"
                                checked={selectedEvents.includes(event.id)}
                                onChange={() => toggleEvent(event.id)}
                                className="mt-1"
                              />
                              <div>
                                <p className="font-medium text-sm">{event.label}</p>
                                <p className="text-xs text-muted-foreground">{event.description}</p>
                              </div>
                            </label>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-3 pt-4 border-t">
                <Button
                  variant="primary"
                  onClick={handleCreateWebhook}
                  disabled={createWebhookMutation.isPending}
                >
                  {createWebhookMutation.isPending ? 'Creating...' : 'Create Webhook'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsCreating(false);
                    setNewUrl('');
                    setNewSecret('');
                    setSelectedEvents([]);
                  }}
                >
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Webhooks List */}
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="pt-6">
                  <div className="h-5 w-1/2 bg-slate-200 rounded mb-3" />
                  <div className="h-4 w-1/3 bg-slate-200 rounded" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : webhooks.length === 0 ? (
          <Card>
            <CardContent className="py-16 text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-100 flex items-center justify-center">
                <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-slate-700 mb-2">No webhooks configured</h3>
              <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                Webhooks allow you to receive real-time notifications when events occur in your account.
              </p>
              {!isCreating && (
                <Button variant="primary" onClick={() => setIsCreating(true)}>
                  Create Your First Webhook
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {webhooks.map((webhook) => (
              <Card key={webhook.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      {/* URL and badges */}
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        <code className="text-sm font-mono text-slate-700 truncate">
                          {webhook.url}
                        </code>
                        <Badge variant={webhook.is_active ? 'success' : 'secondary'} size="sm">
                          {webhook.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                        {webhook.is_verified && (
                          <Badge variant="default" size="sm">
                            Verified
                          </Badge>
                        )}
                        {webhook.failure_count > 0 && (
                          <Badge variant="destructive" size="sm">
                            {webhook.failure_count} {webhook.failure_count === 1 ? 'failure' : 'failures'}
                          </Badge>
                        )}
                      </div>

                      {/* Events */}
                      <div className="flex flex-wrap gap-1.5 mb-3">
                        {webhook.events.map((event) => (
                          <span
                            key={event}
                            className="text-xs px-2 py-0.5 bg-slate-100 text-slate-600 rounded"
                          >
                            {event}
                          </span>
                        ))}
                      </div>

                      {/* Metadata */}
                      <div className="flex items-center gap-4 text-xs text-muted-foreground flex-wrap">
                        <span>Created {new Date(webhook.created_at).toLocaleDateString()}</span>
                        {webhook.last_triggered_at && (
                          <span>Last triggered {new Date(webhook.last_triggered_at).toLocaleDateString()}</span>
                        )}
                        <span>
                          {webhook.success_count} succeeded / {webhook.failure_count} failed
                        </span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => testWebhookMutation.mutate(webhook.id)}
                        disabled={testingId === webhook.id}
                      >
                        {testingId === webhook.id ? 'Testing...' : 'Test'}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toggleWebhookMutation.mutate({ id: webhook.id, is_active: !webhook.is_active })}
                      >
                        {webhook.is_active ? 'Disable' : 'Enable'}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          if (confirm('Are you sure you want to delete this webhook?')) {
                            deleteWebhookMutation.mutate(webhook.id);
                          }
                        }}
                        className="text-red-600 hover:bg-red-50"
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Documentation Link */}
        <div className="mt-8 p-4 bg-slate-50 rounded-lg border border-slate-200">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-blue-ncs mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="font-medium text-sm text-slate-700">Webhook Documentation</p>
              <p className="text-sm text-muted-foreground mt-1">
                Learn how to handle webhook payloads, verify signatures, and implement retry logic.
              </p>
              <a
                href="https://api.encypherai.com/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-ncs hover:underline mt-2 inline-block"
              >
                View documentation -&gt;
              </a>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
