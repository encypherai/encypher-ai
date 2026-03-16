'use client';

import React, { useState, useMemo, useCallback } from 'react';
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
  Badge,
  Input,
} from '@encypher/design-system';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../components/ui/tabs';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import apiClient from '../../lib/api';

// -- Types --------------------------------------------------------------------

interface PolicyRule {
  field: string;
  operator: string;
  value: unknown;
  action: string;
}

interface AttestationPolicy {
  id: string;
  name: string;
  description?: string;
  enforcement: string;
  scope?: string;
  rules: PolicyRule[];
  active: boolean;
  created_at: string;
  updated_at: string;
}

interface AttestationRecord {
  id: string;
  document_id: string;
  policy_id?: string;
  reviewer?: string;
  model_provider?: string;
  verdict: string;
  confidence_score?: number;
  created_at: string;
}

// -- Helpers ------------------------------------------------------------------

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '--';
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

const ENFORCEMENT_STYLES: Record<string, string> = {
  warn: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  block: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  audit: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
};

const VERDICT_STYLES: Record<string, string> = {
  active: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  pass: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  fail: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
};

const FIELD_OPTIONS = ['model_provider', 'confidence_score', 'reviewer_role', 'human_reviewed'];
const OPERATOR_OPTIONS = ['eq', 'gte', 'lte', 'in', 'contains'];
const ACTION_OPTIONS = ['warn', 'block', 'require_review'];

// -- Create Policy Form -------------------------------------------------------

function CreatePolicyForm({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const { data: session } = useSession();
  const accessToken = (session?.user as Record<string, unknown>)?.accessToken as string | undefined;
  const [name, setName] = useState('');
  const [enforcement, setEnforcement] = useState('warn');
  const [scope, setScope] = useState('all');
  const [rules, setRules] = useState<PolicyRule[]>([]);

  const createMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      // @ts-ignore -- stub API method
      return apiClient.createAttestationPolicy(accessToken, {
        name,
        enforcement,
        scope,
        rules,
      });
    },
    onSuccess: () => {
      toast.success('Policy created');
      onCreated();
      onClose();
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Failed to create policy');
    },
  });

  const addRule = useCallback(() => {
    setRules((prev) => [...prev, { field: 'model_provider', operator: 'eq', value: '', action: 'warn' }]);
  }, []);

  const removeRule = useCallback((idx: number) => {
    setRules((prev) => prev.filter((_, i) => i !== idx));
  }, []);

  const updateRule = useCallback((idx: number, key: keyof PolicyRule, val: string) => {
    setRules((prev) => prev.map((r, i) => (i === idx ? { ...r, [key]: val } : r)));
  }, []);

  return (
    <Card className="mb-6 border-2 border-dashed">
      <CardHeader>
        <CardTitle>Create Attestation Policy</CardTitle>
        <CardDescription>Define rules for governing AI content attestation workflows.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Policy Name</label>
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Require Human Review" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Enforcement</label>
            <select
              className="w-full rounded-md border px-3 py-2 text-sm bg-background"
              value={enforcement}
              onChange={(e) => setEnforcement(e.target.value)}
            >
              <option value="warn">Warn</option>
              <option value="block">Block</option>
              <option value="audit">Audit</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Scope</label>
            <Input value={scope} onChange={(e) => setScope(e.target.value)} placeholder="all" />
          </div>
        </div>

        {/* Rules builder */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium">Rules</label>
            <Button variant="outline" size="sm" onClick={addRule}>
              + Add Rule
            </Button>
          </div>
          {rules.map((rule, idx) => (
            <div key={idx} className="grid grid-cols-5 gap-2 mb-2 items-end">
              <select
                className="rounded-md border px-2 py-1.5 text-sm bg-background"
                value={rule.field}
                onChange={(e) => updateRule(idx, 'field', e.target.value)}
              >
                {FIELD_OPTIONS.map((f) => (
                  <option key={f} value={f}>{f}</option>
                ))}
              </select>
              <select
                className="rounded-md border px-2 py-1.5 text-sm bg-background"
                value={rule.operator}
                onChange={(e) => updateRule(idx, 'operator', e.target.value)}
              >
                {OPERATOR_OPTIONS.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
              <Input
                className="text-sm"
                value={String(rule.value)}
                onChange={(e) => updateRule(idx, 'value', e.target.value)}
                placeholder="value"
              />
              <select
                className="rounded-md border px-2 py-1.5 text-sm bg-background"
                value={rule.action}
                onChange={(e) => updateRule(idx, 'action', e.target.value)}
              >
                {ACTION_OPTIONS.map((a) => (
                  <option key={a} value={a}>{a}</option>
                ))}
              </select>
              <Button variant="ghost" size="sm" onClick={() => removeRule(idx)}>
                Remove
              </Button>
            </div>
          ))}
          {rules.length === 0 && (
            <p className="text-sm text-muted-foreground">No rules added yet.</p>
          )}
        </div>

        <div className="flex gap-2 pt-2">
          <Button
            onClick={() => createMutation.mutate()}
            disabled={!name.trim() || createMutation.isPending}
          >
            {createMutation.isPending ? 'Creating...' : 'Create Policy'}
          </Button>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
        </div>
      </CardContent>
    </Card>
  );
}

// -- Policies Tab -------------------------------------------------------------

function PoliciesTab() {
  const { data: session } = useSession();
  const accessToken = (session?.user as Record<string, unknown>)?.accessToken as string | undefined;
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ['attestation-policies'],
    queryFn: () => {
      if (!accessToken) throw new Error('Not authenticated');
      // @ts-ignore -- stub API method
      return apiClient.listAttestationPolicies(accessToken);
    },
    enabled: Boolean(accessToken),
  });

  const deleteMutation = useMutation({
    mutationFn: async (policyId: string) => {
      if (!accessToken) throw new Error('Not authenticated');
      // @ts-ignore -- stub API method
      return apiClient.deleteAttestationPolicy(accessToken, policyId);
    },
    onSuccess: () => {
      toast.success('Policy deactivated');
      queryClient.invalidateQueries({ queryKey: ['attestation-policies'] });
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Failed to deactivate policy');
    },
  });

  const policies = (data?.policies ?? []) as unknown as AttestationPolicy[];
  const activePolicies = policies.filter((p) => p.active);

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Total Policies</p>
            <p className="text-2xl font-bold">{policies.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Active Policies</p>
            <p className="text-2xl font-bold">{activePolicies.length}</p>
          </CardContent>
        </Card>
      </div>

      {/* Create policy */}
      {showCreate ? (
        <CreatePolicyForm
          onClose={() => setShowCreate(false)}
          onCreated={() => queryClient.invalidateQueries({ queryKey: ['attestation-policies'] })}
        />
      ) : (
        <Button onClick={() => setShowCreate(true)}>Create Policy</Button>
      )}

      {/* Policy list */}
      {isLoading && <p className="text-muted-foreground">Loading policies...</p>}
      {error && <p className="text-red-500">Failed to load policies.</p>}

      <div className="space-y-3">
        {policies.map((policy) => (
          <Card key={policy.id} className={!policy.active ? 'opacity-60' : ''}>
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">{policy.name}</h3>
                    <Badge className={ENFORCEMENT_STYLES[policy.enforcement] || ''}>
                      {policy.enforcement}
                    </Badge>
                    {!policy.active && (
                      <Badge variant="outline">Inactive</Badge>
                    )}
                  </div>
                  {policy.scope && (
                    <p className="text-sm text-muted-foreground">Scope: {policy.scope}</p>
                  )}
                  <p className="text-sm text-muted-foreground">
                    {policy.rules.length} rule{policy.rules.length !== 1 ? 's' : ''} -- Created {formatDate(policy.created_at)}
                  </p>
                </div>
                <div className="flex gap-2">
                  {policy.active && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteMutation.mutate(policy.id)}
                      disabled={deleteMutation.isPending}
                    >
                      Deactivate
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// -- Attestations Tab ---------------------------------------------------------

function AttestationsTab() {
  const { data: session } = useSession();
  const accessToken = (session?.user as Record<string, unknown>)?.accessToken as string | undefined;
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['attestations'],
    queryFn: () => {
      if (!accessToken) throw new Error('Not authenticated');
      // @ts-ignore -- stub API method
      return apiClient.listAttestations(accessToken, { limit: 100 });
    },
    enabled: Boolean(accessToken),
  });

  const attestations = (data?.attestations ?? []) as AttestationRecord[];
  const total = data?.total ?? 0;

  const stats = useMemo(() => {
    const passCount = attestations.filter((a) => a.verdict === 'active' || a.verdict === 'pass').length;
    const failCount = attestations.filter((a) => a.verdict === 'fail').length;
    const passRate = attestations.length > 0 ? Math.round((passCount / attestations.length) * 100) : 0;
    return { total, passRate, failCount };
  }, [attestations, total]);

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Total Attestations</p>
            <p className="text-2xl font-bold">{stats.total}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Pass Rate</p>
            <p className="text-2xl font-bold">{stats.passRate}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Violations Caught</p>
            <p className="text-2xl font-bold">{stats.failCount}</p>
          </CardContent>
        </Card>
      </div>

      {/* Table */}
      {isLoading && <p className="text-muted-foreground">Loading attestations...</p>}
      {error && <p className="text-red-500">Failed to load attestations.</p>}

      <div className="border rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="text-left px-4 py-3 font-medium">Document</th>
              <th className="text-left px-4 py-3 font-medium">Reviewer</th>
              <th className="text-left px-4 py-3 font-medium">Model</th>
              <th className="text-left px-4 py-3 font-medium">Verdict</th>
              <th className="text-left px-4 py-3 font-medium">Date</th>
            </tr>
          </thead>
          <tbody>
            {attestations.map((a) => (
              <React.Fragment key={a.id}>
                <tr
                  className="border-t hover:bg-muted/30 cursor-pointer"
                  onClick={() => setExpandedId(expandedId === a.id ? null : a.id)}
                >
                  <td className="px-4 py-3 font-mono text-xs truncate max-w-[200px]">{a.document_id}</td>
                  <td className="px-4 py-3">{a.reviewer || '--'}</td>
                  <td className="px-4 py-3">{a.model_provider || '--'}</td>
                  <td className="px-4 py-3">
                    <Badge className={VERDICT_STYLES[a.verdict] || 'bg-gray-100 text-gray-800'}>
                      {a.verdict}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">{formatDate(a.created_at)}</td>
                </tr>
                {expandedId === a.id && (
                  <tr className="border-t bg-muted/10">
                    <td colSpan={5} className="px-4 py-3">
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div><span className="font-medium">ID:</span> {a.id}</div>
                        <div><span className="font-medium">Policy ID:</span> {a.policy_id || '--'}</div>
                        <div><span className="font-medium">Confidence:</span> {a.confidence_score != null ? a.confidence_score : '--'}</div>
                        <div><span className="font-medium">Created:</span> {a.created_at}</div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
            {attestations.length === 0 && !isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">
                  No attestations found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// -- Page ---------------------------------------------------------------------

export default function GovernancePage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Governance</h1>
          <p className="text-muted-foreground">
            Manage attestation policies and review AI content governance records.
          </p>
        </div>

        <Tabs defaultValue="policies">
          <TabsList>
            <TabsTrigger value="policies">Policies</TabsTrigger>
            <TabsTrigger value="attestations">Attestations</TabsTrigger>
          </TabsList>

          <TabsContent value="policies">
            <PoliciesTab />
          </TabsContent>

          <TabsContent value="attestations">
            <AttestationsTab />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
