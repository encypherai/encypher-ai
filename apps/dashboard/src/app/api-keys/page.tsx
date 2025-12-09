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
import { useState, useRef, useEffect } from 'react';
import { toast } from 'sonner';
import apiClient from '../../lib/api';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { ApiAccessGate } from '../../components/ApiAccessGate';
import { exportApiKeys } from '../../lib/exportCsv';

// Modal component for creating API keys
function CreateKeyModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (name: string) => void;
  isLoading: boolean;
}) {
  const [keyName, setKeyName] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setKeyName('');
      // Focus input after modal opens
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (keyName.trim()) {
      onSubmit(keyName.trim());
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white dark:bg-slate-900 rounded-xl shadow-2xl w-full max-w-md mx-4 p-6">
        <h3 className="text-xl font-semibold text-foreground mb-2">Create New API Key</h3>
        <p className="text-sm text-muted-foreground mb-6">
          Give your API key a descriptive name to help you identify it later.
        </p>
        
        <form onSubmit={handleSubmit}>
          <Input
            ref={inputRef}
            placeholder="e.g., WordPress Production, Development Server"
            value={keyName}
            onChange={(e) => setKeyName(e.target.value)}
            disabled={isLoading}
            className="mb-6"
          />
          
          <div className="flex justify-end gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={!keyName.trim() || isLoading}
            >
              {isLoading ? 'Creating...' : 'Create Key'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

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

  const [isModalOpen, setIsModalOpen] = useState(false);
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
    mutationFn: async (keyName: string) => {
      if (!accessToken) throw new Error('You must be signed in to create API keys.');
      const response = await apiClient.createApiKey(accessToken, keyName, [
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
      setIsModalOpen(false);
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to create API key.');
    },
  });

  const handleCreateKey = (name: string) => {
    createKeyMutation.mutate(name);
  };

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
      const errorMessage = (apiKeysQuery.error as Error)?.message || '';
      // Treat 404 or "Not Found" as empty state (service may not have keys endpoint yet)
      if (errorMessage.includes('404') || errorMessage.toLowerCase().includes('not found')) {
        return (
          <div className="flex flex-col items-center justify-center py-16 px-4">
            <div className="w-20 h-20 mb-6 rounded-full bg-blue-ncs/10 flex items-center justify-center">
              <svg className="w-10 h-10 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-foreground mb-2">No API Keys Yet</h3>
            <p className="text-muted-foreground text-center max-w-md mb-6">
              Generate your first API key to start authenticating your content with cryptographic proof.
            </p>
            <Button
              variant="primary"
              onClick={() => setIsModalOpen(true)}
              disabled={!accessToken || createKeyMutation.isPending}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Generate Your First Key
            </Button>
          </div>
        );
      }
      return (
        <div className="text-destructive">
          {errorMessage || 'Unable to load API keys.'}
        </div>
      );
    }

    if (!apiKeys.length) {
      return (
        <div className="flex flex-col items-center justify-center py-16 px-4">
          <div className="w-20 h-20 mb-6 rounded-full bg-blue-ncs/10 flex items-center justify-center">
            <svg className="w-10 h-10 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-foreground mb-2">No API Keys Yet</h3>
          <p className="text-muted-foreground text-center max-w-md mb-6">
            Generate your first API key to start authenticating your content with cryptographic proof.
          </p>
          <Button
            variant="primary"
            onClick={() => setIsModalOpen(true)}
            disabled={!accessToken || createKeyMutation.isPending}
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Generate Your First Key
          </Button>
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
      {/* TEAM_006: Gate API key generation behind approval workflow */}
      <ApiAccessGate>
        <div className="flex flex-col gap-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h2 className="text-3xl font-bold text-delft-blue dark:text-white mb-1">API Keys</h2>
              <p className="text-muted-foreground">
                Generate and manage API keys for your WordPress plugin, SDKs, or custom integrations.
              </p>
            </div>
            <div className="flex items-center gap-3">
              {apiKeys.length > 0 && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      exportApiKeys(apiKeys);
                      toast.success('API keys exported');
                    }}
                  >
                    <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Export
                  </Button>
                  <Button
                    variant="primary"
                    onClick={() => setIsModalOpen(true)}
                    disabled={!accessToken || createKeyMutation.isPending}
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    {createKeyMutation.isPending ? 'Generating…' : 'Generate Key'}
                  </Button>
                </>
              )}
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

        {/* Create Key Modal */}
        <CreateKeyModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleCreateKey}
          isLoading={createKeyMutation.isPending}
        />
      </ApiAccessGate>
    </DashboardLayout>
  );
}

