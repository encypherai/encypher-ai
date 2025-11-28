'use client';

import {
  Badge,
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Input,
} from '@encypher/design-system';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { useState } from 'react';
import { toast } from 'sonner';
import apiClient from '../../lib/api';
import { DashboardLayout } from '../../components/layout/DashboardLayout';

type ApiKeyRecord = {
  id: string;
  name: string;
  maskedKey: string;
  createdAt: string;
  lastUsedAt?: string;
  permissions: string[];
};

const normalizeApiKeys = (payload: any): ApiKeyRecord[] => {
  // Handle various response formats from the API
  // Note: Don't use payload?.keys as arrays have a .keys() method that would match
  let rawKeys: any[];
  if (Array.isArray(payload)) {
    rawKeys = payload;
  } else if (Array.isArray(payload?.data?.api_keys)) {
    rawKeys = payload.data.api_keys;
  } else if (Array.isArray(payload?.data)) {
    rawKeys = payload.data;
  } else if (Array.isArray(payload?.api_keys)) {
    rawKeys = payload.api_keys;
  } else {
    rawKeys = [];
  }

  return rawKeys.map((key: any, idx: number) => ({
    id: String(key.id ?? key.key_id ?? key.uuid ?? idx),
    name: key.name ?? key.label ?? 'API Key',
    maskedKey:
      key.key_prefix ??  // Prefer key_prefix (e.g., "ency_y7T2mUv...")
      key.masked_key ??
      key.fingerprint ??
      key.key ??
      key.token ??
      `${String(key.prefix ?? 'ency').slice(0, 6)}****************`,
    createdAt: key.created_at ?? key.created ?? key.inserted_at ?? '',
    lastUsedAt: key.last_used_at ?? key.last_used ?? key.last_accessed_at ?? '—',
    permissions: key.permissions ?? key.scopes ?? ['sign', 'verify'],
  }));
};

const extractFullKey = (payload: any): string =>
  payload?.data?.key ??  // API client wraps response in { data: { key: ... } }
  payload?.data?.api_key ??
  payload?.data?.token ??
  payload?.key ??
  payload?.api_key ??
  payload?.token ??
  '';

/**
 * Format ISO date string to human-readable format
 */
const formatDate = (dateString: string | undefined): string => {
  if (!dateString || dateString === '—') return 'Never';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    }).format(date);
  } catch {
    return dateString;
  }
};

export default function ApiKeysPage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const queryClient = useQueryClient();

  const [newKeyName, setNewKeyName] = useState('');
  const [generatedKey, setGeneratedKey] = useState('');

  const apiKeysQuery = useQuery({
    queryKey: ['api-keys'],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in to manage API keys.');
      const response = await apiClient.getApiKeys(accessToken);
      return normalizeApiKeys(response);
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
  });

  const createKeyMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('You must be signed in to create API keys.');
      const response = await apiClient.createApiKey(accessToken, newKeyName || 'New API key', [
        'sign',
        'verify',
        'read',
      ]);
      return response;
    },
    onSuccess: (data) => {
      const fullKey = extractFullKey(data);
      if (fullKey) {
        setGeneratedKey(fullKey);
        toast.success('API key created. Copy it now — it will not be shown again.');
      } else {
        setGeneratedKey('');
        toast.success('API key created.');
      }
      setNewKeyName('');
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to create API key.');
    },
  });

  const deleteKeyMutation = useMutation({
    mutationFn: async (keyId: string) => {
      if (!accessToken) throw new Error('You must be signed in to delete API keys.');
      await apiClient.deleteApiKey(accessToken, keyId);
    },
    onSuccess: () => {
      toast.success('API key deleted.');
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to delete API key.');
    },
  });

  const apiKeys = apiKeysQuery.data ?? [];
  const isLoadingSession = status === 'loading';
  const isLoadingKeys = apiKeysQuery.isLoading || !accessToken;

  const handleCopyKey = (key: string) => {
    navigator.clipboard.writeText(key);
    toast.success('API key copied to clipboard.');
  };

  const renderKeyList = () => {
    if (isLoadingSession || isLoadingKeys) {
      return <div className="text-muted-foreground">Loading API keys…</div>;
    }

    if (apiKeysQuery.isError) {
      return (
        <div className="text-destructive">
          {(apiKeysQuery.error as Error)?.message || 'Unable to load API keys.'}
        </div>
      );
    }

    if (!apiKeys.length) {
      return (
        <div className="text-muted-foreground">
          You have not generated any API keys yet.
        </div>
      );
    }

    return (
      <div className="grid gap-4">
        {apiKeys.map((key) => (
          <Card key={key.id} className="border-border hover:shadow-md transition-shadow">
            <CardContent className="p-6 flex flex-col gap-4">
              {/* Header: Name + Delete */}
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-foreground">{key.name}</h3>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    Created {formatDate(key.createdAt)}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    if (confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
                      deleteKeyMutation.mutate(key.id);
                    }
                  }}
                  disabled={deleteKeyMutation.isPending}
                  className="text-destructive hover:text-destructive hover:bg-destructive/10"
                >
                  Delete
                </Button>
              </div>

              {/* API Key Display */}
              <div className="flex items-center gap-3">
                <code className="flex-1 bg-muted px-4 py-2.5 rounded-lg border border-border font-mono text-sm text-foreground">
                  {key.maskedKey}
                </code>
                <span className="text-xs text-muted-foreground italic whitespace-nowrap">
                  Full key shown only at creation
                </span>
              </div>

              {/* Metadata: Permissions + Last Used */}
              <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-border">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground uppercase tracking-wide">Permissions:</span>
                  <div className="flex gap-1.5">
                    {key.permissions?.map((perm) => (
                      <Badge key={perm} variant="primary" size="sm">
                        {perm}
                      </Badge>
                    )) || <span className="text-muted-foreground">—</span>}
                  </div>
                </div>
                <div className="text-sm text-muted-foreground">
                  <span className="text-xs uppercase tracking-wide">Last used:</span>{' '}
                  {formatDate(key.lastUsedAt)}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold text-delft-blue mb-1">API Keys</h2>
            <p className="text-muted-foreground">
              Generate and manage API keys for your WordPress plugin, SDKs, or custom integrations.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Input
              placeholder="Key name (e.g., WordPress Production)"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              disabled={createKeyMutation.isPending || !accessToken}
              className="w-64"
            />
            <Button
              variant="primary"
              onClick={() => createKeyMutation.mutate()}
              disabled={!accessToken || createKeyMutation.isPending}
            >
              {createKeyMutation.isPending ? 'Generating…' : 'Generate key'}
            </Button>
          </div>
        </div>

        {generatedKey && (
          <Card className="border-2 border-warning bg-warning/5 shadow-lg">
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-warning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <CardTitle className="text-lg">New API Key Created</CardTitle>
              </div>
              <CardDescription className="text-foreground/80 font-medium">
                Copy this key now — you won't be able to see it again!
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <code className="flex-1 bg-white px-4 py-3 rounded-lg border-2 border-border font-mono text-sm select-all">
                  {generatedKey}
                </code>
                <Button variant="primary" size="sm" onClick={() => handleCopyKey(generatedKey)}>
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy
                </Button>
              </div>
              <div className="flex justify-end">
                <Button variant="ghost" size="sm" onClick={() => setGeneratedKey('')}>
                  I've copied it, dismiss
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {renderKeyList()}
      </div>
    </DashboardLayout>
  );
}
