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
import Link from 'next/link';
import { useMemo, useState } from 'react';
import { toast } from 'sonner';
import apiClient from '../../lib/api';

type ApiKeyRecord = {
  id: string;
  name: string;
  maskedKey: string;
  createdAt: string;
  lastUsedAt?: string;
  permissions: string[];
};

const normalizeApiKeys = (payload: any): ApiKeyRecord[] => {
  const rawKeys: any[] =
    payload?.data?.api_keys ||
    payload?.data ||
    payload?.api_keys ||
    payload?.keys ||
    payload ||
    [];

  return (Array.isArray(rawKeys) ? rawKeys : []).map((key: any, idx: number) => ({
    id: String(key.id ?? key.key_id ?? key.uuid ?? idx),
    name: key.name ?? key.label ?? 'API Key',
    maskedKey:
      key.masked_key ??
      key.key ??
      key.token ??
      `${String(key.prefix ?? 'ency').slice(0, 6)}****************`,
    createdAt: key.created_at ?? key.created ?? key.inserted_at ?? '',
    lastUsedAt: key.last_used_at ?? key.last_used ?? key.last_accessed_at ?? '—',
    permissions: key.permissions ?? key.scopes ?? ['sign', 'verify'],
  }));
};

const extractFullKey = (payload: any): string =>
  payload?.data?.api_key ??
  payload?.data?.token ??
  payload?.api_key ??
  payload?.token ??
  payload?.key ??
  '';

export default function ApiKeysPage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const isAdmin = ((session?.user as any)?.role ?? '').toLowerCase() === 'admin';
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

  const headerActions = useMemo(
    () => (
      <div className="flex items-center space-x-4">
        <Link href="/billing">
          <Button variant="ghost" size="sm">
            Billing
          </Button>
        </Link>
        <Link href="/analytics">
          <Button variant="ghost" size="sm">
            Analytics
          </Button>
        </Link>
        <Link href="/settings">
          <Button variant="ghost" size="sm">
            Settings
          </Button>
        </Link>
        {isAdmin && (
          <Link href="/admin">
            <Button variant="ghost" size="sm">
              Admin
            </Button>
          </Link>
        )}
        <div className="w-8 h-8 bg-columbia-blue rounded-full flex items-center justify-center text-white font-semibold">
          {session?.user?.name?.charAt(0)?.toUpperCase() ?? 'U'}
        </div>
      </div>
    ),
    [session?.user?.name, isAdmin],
  );

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
                <code className="flex-1 bg-muted px-3 py-2 rounded border border-border font-mono text-sm">
                  {key.maskedKey}
                </code>
                <Button variant="outline" size="sm" onClick={() => handleCopyKey(key.maskedKey)}>
                  Copy
                </Button>
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
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-white sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/">
              <div className="w-8 h-8 bg-gradient-to-br from-delft-blue to-blue-ncs rounded-lg cursor-pointer" />
            </Link>
            <h1 className="text-xl font-bold text-delft-blue">Encypher Dashboard</h1>
          </div>
          {headerActions}
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 flex flex-col gap-6">
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
      </main>
    </div>
  );
}
