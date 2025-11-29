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

interface Webhook {
  id: string;
  url: string;
  events: string[];
  active: boolean;
  createdAt: string;
  lastTriggered?: string;
  failureCount: number;
}

const availableEvents = [
  { id: 'content.signed', label: 'Content Signed', description: 'When content is signed via API' },
  { id: 'content.verified', label: 'Content Verified', description: 'When content verification is requested' },
  { id: 'key.created', label: 'API Key Created', description: 'When a new API key is generated' },
  { id: 'key.revoked', label: 'API Key Revoked', description: 'When an API key is deleted' },
  { id: 'usage.threshold', label: 'Usage Threshold', description: 'When usage reaches 80% of limit' },
];

// Mock data - replace with actual API calls
const mockWebhooks: Webhook[] = [];

export default function WebhooksPage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as Record<string, unknown>)?.accessToken as string | undefined;
  const queryClient = useQueryClient();

  const [isCreating, setIsCreating] = useState(false);
  const [newUrl, setNewUrl] = useState('');
  const [selectedEvents, setSelectedEvents] = useState<string[]>([]);

  const webhooksQuery = useQuery({
    queryKey: ['webhooks'],
    queryFn: async () => {
      // Mock API call - replace with actual API
      await new Promise(resolve => setTimeout(resolve, 500));
      return mockWebhooks;
    },
    enabled: Boolean(accessToken),
  });

  const createWebhookMutation = useMutation({
    mutationFn: async (data: { url: string; events: string[] }) => {
      // Mock API call - replace with actual API
      await new Promise(resolve => setTimeout(resolve, 500));
      const newWebhook: Webhook = {
        id: `wh_${Date.now()}`,
        url: data.url,
        events: data.events,
        active: true,
        createdAt: new Date().toISOString(),
        failureCount: 0,
      };
      mockWebhooks.push(newWebhook);
      return newWebhook;
    },
    onSuccess: () => {
      toast.success('Webhook created successfully');
      setIsCreating(false);
      setNewUrl('');
      setSelectedEvents([]);
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
    },
    onError: () => {
      toast.error('Failed to create webhook');
    },
  });

  const deleteWebhookMutation = useMutation({
    mutationFn: async (id: string) => {
      // Mock API call - replace with actual API
      await new Promise(resolve => setTimeout(resolve, 500));
      const index = mockWebhooks.findIndex(w => w.id === id);
      if (index > -1) mockWebhooks.splice(index, 1);
    },
    onSuccess: () => {
      toast.success('Webhook deleted');
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
    },
    onError: () => {
      toast.error('Failed to delete webhook');
    },
  });

  const toggleWebhookMutation = useMutation({
    mutationFn: async ({ id, active }: { id: string; active: boolean }) => {
      // Mock API call - replace with actual API
      await new Promise(resolve => setTimeout(resolve, 500));
      const webhook = mockWebhooks.find(w => w.id === id);
      if (webhook) webhook.active = active;
    },
    onSuccess: (_, { active }) => {
      toast.success(`Webhook ${active ? 'enabled' : 'disabled'}`);
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
    },
  });

  const webhooks = webhooksQuery.data ?? [];
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
    createWebhookMutation.mutate({ url: newUrl, events: selectedEvents });
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
            <h2 className="text-3xl font-bold text-delft-blue mb-1">Webhooks</h2>
            <p className="text-muted-foreground">
              Receive real-time notifications when events happen in your account
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

              {/* Event Selection */}
              <div>
                <label className="block text-sm font-medium mb-3">Events to Subscribe</label>
                <div className="space-y-2">
                  {availableEvents.map((event) => (
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
                      {/* URL */}
                      <div className="flex items-center gap-2 mb-2">
                        <code className="text-sm font-mono text-slate-700 truncate">
                          {webhook.url}
                        </code>
                        <Badge variant={webhook.active ? 'success' : 'secondary'} size="sm">
                          {webhook.active ? 'Active' : 'Inactive'}
                        </Badge>
                        {webhook.failureCount > 0 && (
                          <Badge variant="destructive" size="sm">
                            {webhook.failureCount} failures
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
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span>Created {new Date(webhook.createdAt).toLocaleDateString()}</span>
                        {webhook.lastTriggered && (
                          <span>Last triggered {new Date(webhook.lastTriggered).toLocaleDateString()}</span>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toggleWebhookMutation.mutate({ id: webhook.id, active: !webhook.active })}
                      >
                        {webhook.active ? 'Disable' : 'Enable'}
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
                href="https://docs.encypherai.com/webhooks"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-ncs hover:underline mt-2 inline-block"
              >
                View documentation &rarr;
              </a>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
