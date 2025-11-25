'use client';

import {
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
          <Card key={key.id} className="border-border">
            <CardContent className="p-6 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Key name</p>
                  <p className="font-semibold text-foreground">{key.name}</p>
                </div>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => deleteKeyMutation.mutate(key.id)}
                  disabled={deleteKeyMutation.isPending}
                >
                  Delete
                </Button>
              </div>

              <div className="flex items-center gap-2">
                <code className="flex-1 bg-muted px-3 py-2 rounded border border-border font-mono text-sm text-muted-foreground">
                  {key.maskedKey}
                </code>
                <span className="text-xs text-muted-foreground italic">
                  Full key shown only at creation
                </span>
              </div>

              <div className="grid md:grid-cols-3 gap-4 text-sm text-muted-foreground">
                <div>
                  <span className="block text-xs uppercase tracking-wide">Created</span>
                  {key.createdAt || '—'}
                </div>
                <div>
                  <span className="block text-xs uppercase tracking-wide">Last used</span>
                  {key.lastUsedAt || 'Never'}
                </div>
                <div>
                  <span className="block text-xs uppercase tracking-wide">Permissions</span>
                  {key.permissions?.join(', ') || '—'}
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
          <Card className="border-columbia-blue bg-columbia-blue/5">
            <CardHeader>
              <CardTitle>New API Key</CardTitle>
              <CardDescription>
                Store this value in a safe place. For security reasons we can’t show it again.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex items-center gap-3">
              <code className="flex-1 bg-white px-3 py-2 rounded border border-border font-mono text-sm">
                {generatedKey}
              </code>
              <Button variant="outline" size="sm" onClick={() => handleCopyKey(generatedKey)}>
                Copy
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setGeneratedKey('')}>
                Dismiss
              </Button>
            </CardContent>
          </Card>
        )}

        {renderKeyList()}
      </div>
    </DashboardLayout>
  );
}
