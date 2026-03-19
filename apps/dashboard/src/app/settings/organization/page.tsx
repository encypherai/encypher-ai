'use client';

import {
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
} from '@encypher/design-system';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { Suspense, useEffect, useState } from 'react';
import { Shield, Settings, Package, ArrowLeft, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import { useOrganization } from '../../../contexts/OrganizationContext';
import apiClient from '../../../lib/api';
import { ADD_ONS, ENTERPRISE_TIER, FREE_TIER } from '../../../lib/pricing-config/tiers';

type UserRole = 'owner' | 'admin' | 'manager' | 'member' | 'viewer';

const ADMIN_ROLES: UserRole[] = ['owner', 'admin'];

function useCurrentUserRole(orgId: string | undefined, accessToken: string | undefined) {
  const { data: session } = useSession();
  const userEmail = session?.user?.email;

  const { data: members, isLoading } = useQuery({
    queryKey: ['org-members-role-check', orgId],
    queryFn: async () => {
      if (!accessToken || !orgId) return [];
      return apiClient.listOrganizationMembers(accessToken, orgId);
    },
    enabled: Boolean(accessToken) && Boolean(orgId) && Boolean(userEmail),
    staleTime: 5 * 60_000,
  });

  const currentMember = members?.find(
    (m) => (m as any).user_email?.toLowerCase() === userEmail?.toLowerCase()
      || (m as any).email?.toLowerCase() === userEmail?.toLowerCase()
  );

  return {
    role: (currentMember?.role as UserRole) || null,
    isAdmin: currentMember ? ADMIN_ROLES.includes(currentMember.role as UserRole) : false,
    isLoading,
  };
}

function SecurityPoliciesCard({
  orgId,
  accessToken,
}: {
  orgId: string;
  accessToken: string | undefined;
}) {
  const { data: orgSecurity, isLoading } = useQuery({
    queryKey: ['org-security', orgId],
    queryFn: async () => {
      if (!accessToken) return null;
      return apiClient.getOrganizationSecurity(accessToken, orgId);
    },
    enabled: Boolean(accessToken) && Boolean(orgId),
    staleTime: 5 * 60_000,
  });

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-blue-ncs" />
          <CardTitle>Security Policies</CardTitle>
        </div>
        <CardDescription>
          Organization-wide security requirements and access controls.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-sm text-muted-foreground">Loading security policies...</div>
        ) : (
          <div className="space-y-4">
            <div className="grid gap-4">
              <div className="flex items-center justify-between rounded-lg border border-border p-4">
                <div>
                  <p className="text-sm font-medium">MFA Enforcement</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Require all members to use two-factor authentication.
                  </p>
                </div>
                <Badge
                  className={
                    orgSecurity?.enforce_mfa
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
                  }
                >
                  {orgSecurity?.enforce_mfa ? 'Required' : 'Optional'}
                </Badge>
              </div>

              <div className="flex items-center justify-between rounded-lg border border-border p-4">
                <div>
                  <p className="text-sm font-medium">Session Timeout</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Automatic session expiry after inactivity.
                  </p>
                </div>
                <Badge className="bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                  Default (24h)
                </Badge>
              </div>

              <div className="flex items-center justify-between rounded-lg border border-border p-4">
                <div>
                  <p className="text-sm font-medium">Password Requirements</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Minimum complexity for member passwords.
                  </p>
                </div>
                <Badge className="bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                  Standard
                </Badge>
              </div>
            </div>

            <p className="text-xs text-muted-foreground">
              To change security policies, visit the{' '}
              <Link href="/settings?tab=organization" className="text-blue-ncs hover:underline">
                Organization settings
              </Link>{' '}
              tab or contact your account administrator.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function DefaultSigningConfigCard() {
  const { activeOrganization } = useOrganization();

  const signingIdentityMode = activeOrganization?.signing_identity_mode || 'organization_name';
  const signingIdentityLabel =
    signingIdentityMode === 'custom'
      ? activeOrganization?.signing_identity_custom_label || activeOrganization?.display_name || activeOrganization?.name
      : signingIdentityMode === 'organization_and_author'
        ? `Author + ${activeOrganization?.display_name || activeOrganization?.name || 'Organization'}`
        : activeOrganization?.display_name || activeOrganization?.name || 'Organization name';

  const isEnterprise = activeOrganization?.tier === 'enterprise';

  const identityModeLabels: Record<string, string> = {
    organization_name: 'Organization name',
    organization_and_author: 'Author + organization',
    custom: 'Custom label',
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Settings className="w-5 h-5 text-blue-ncs" />
          <CardTitle>Default Signing Configuration</CardTitle>
        </div>
        <CardDescription>
          Organization-level signing defaults applied to new documents.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid gap-4">
            <div className="flex items-center justify-between rounded-lg border border-border p-4">
              <div>
                <p className="text-sm font-medium">Signing Identity Mode</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  How the publisher name appears on signed content.
                </p>
              </div>
              <div className="text-right">
                <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                  {identityModeLabels[signingIdentityMode] || signingIdentityMode}
                </Badge>
              </div>
            </div>

            <div className="flex items-center justify-between rounded-lg border border-border p-4">
              <div>
                <p className="text-sm font-medium">Signing Identity Preview</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  What verifiers will see as the publisher.
                </p>
              </div>
              <span className="text-sm font-mono text-muted-foreground">{signingIdentityLabel}</span>
            </div>

            <div className="flex items-center justify-between rounded-lg border border-border p-4">
              <div>
                <p className="text-sm font-medium">Anonymous Publishing</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Show only organization ID instead of name.
                </p>
              </div>
              <Badge
                className={
                  activeOrganization?.anonymous_publisher
                    ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'
                    : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
                }
              >
                {activeOrganization?.anonymous_publisher ? 'Enabled' : 'Disabled'}
              </Badge>
            </div>

            <div className="flex items-center justify-between rounded-lg border border-border p-4">
              <div>
                <p className="text-sm font-medium">C2PA Compliance</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Content Provenance and Authenticity standard.
                </p>
              </div>
              <Badge className="bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
                C2PA 2.3
              </Badge>
            </div>

            {isEnterprise && (
              <div className="flex items-center justify-between rounded-lg border border-border p-4">
                <div>
                  <p className="text-sm font-medium">Custom C2PA Assertions</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Enterprise schema registry for custom assertions.
                  </p>
                </div>
                <Badge className="bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
                  Available
                </Badge>
              </div>
            )}
          </div>

          <p className="text-xs text-muted-foreground">
            To change signing defaults, visit the{' '}
            <Link href="/settings?tab=organization" className="text-blue-ncs hover:underline">
              Organization settings
            </Link>{' '}
            tab.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function FeatureOverviewCard() {
  const { activeOrganization } = useOrganization();
  const tier = activeOrganization?.tier || 'free';
  const isEnterprise = tier === 'enterprise';
  const addOns = activeOrganization?.add_ons || {};

  const tierFeatures = isEnterprise ? ENTERPRISE_TIER.features : [
    ...FREE_TIER.signingFeatures.slice(0, 4),
    ...FREE_TIER.distributionFeatures.slice(0, 3),
  ];

  const exclusiveFeatures = isEnterprise ? ENTERPRISE_TIER.exclusiveCapabilities : [];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Package className="w-5 h-5 text-blue-ncs" />
          <CardTitle>Feature Overview</CardTitle>
        </div>
        <CardDescription>
          Current plan features and active add-ons for your organization.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Current tier */}
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium">Current Plan:</span>
            <Badge
              className={
                isEnterprise
                  ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400'
                  : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
              }
            >
              {isEnterprise ? 'Enterprise' : 'Free'}
            </Badge>
            <span className="text-xs text-muted-foreground">
              {activeOrganization?.subscription_status === 'active' ? '-- Active' : ''}
            </span>
          </div>

          {/* Tier features */}
          <div>
            <h4 className="text-sm font-semibold mb-3">Included Features</h4>
            <div className="grid gap-2">
              {tierFeatures.map((feature, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <span className="text-emerald-500 mt-0.5 shrink-0">[+]</span>
                  <span className="text-muted-foreground">{feature}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Enterprise exclusive features */}
          {isEnterprise && exclusiveFeatures.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold mb-3">Enterprise-Exclusive Capabilities</h4>
              <div className="grid gap-2">
                {exclusiveFeatures.map((feature, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm">
                    <span className="text-purple-500 mt-0.5 shrink-0">[*]</span>
                    <span className="text-muted-foreground">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Active add-ons */}
          <div>
            <h4 className="text-sm font-semibold mb-3">Add-Ons</h4>
            {Object.keys(addOns).length === 0 && !isEnterprise ? (
              <p className="text-sm text-muted-foreground">No active add-ons.</p>
            ) : isEnterprise ? (
              <p className="text-sm text-muted-foreground">
                All add-ons are included with your Enterprise plan.
              </p>
            ) : (
              <div className="grid gap-2">
                {ADD_ONS.map((addon) => {
                  const isActive = Boolean(addOns[addon.id]);
                  if (!isActive) return null;
                  return (
                    <div
                      key={addon.id}
                      className="flex items-center justify-between rounded-lg border border-border p-3"
                    >
                      <div>
                        <p className="text-sm font-medium">{addon.name}</p>
                        <p className="text-xs text-muted-foreground">{addon.description}</p>
                      </div>
                      <Badge className="bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
                        Active
                      </Badge>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {!isEnterprise && (
            <div className="rounded-lg border border-dashed border-border p-4 text-center">
              <p className="text-sm text-muted-foreground mb-2">
                Need more features? Explore add-ons or upgrade to Enterprise.
              </p>
              <Link href="/billing" className="text-sm text-blue-ncs hover:underline">
                View plans and add-ons -&gt;
              </Link>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function DeletionManagementCard({
  accessToken,
}: {
  accessToken: string | undefined;
}) {
  const queryClient = useQueryClient();
  const [purgeEmail, setPurgeEmail] = useState('');
  const [purgeReason, setPurgeReason] = useState('');
  const [showPurgeForm, setShowPurgeForm] = useState(false);

  const { data: deletionRequests, isLoading } = useQuery({
    queryKey: ['admin-deletion-requests'],
    queryFn: async () => {
      if (!accessToken) return { requests: [], total: 0 };
      return apiClient.listDeletionRequests(accessToken);
    },
    enabled: Boolean(accessToken),
    staleTime: 30_000,
  });

  const confirmMutation = useMutation({
    mutationFn: async (requestId: string) => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.confirmDeletionRequest(accessToken, requestId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-deletion-requests'] });
      toast.success('Deletion request confirmed.');
    },
    onError: (err: Error) => toast.error(err.message || 'Failed to confirm'),
  });

  const cancelMutation = useMutation({
    mutationFn: async (requestId: string) => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.cancelDeletionRequest(accessToken, requestId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-deletion-requests'] });
      toast.success('Deletion request cancelled.');
    },
    onError: (err: Error) => toast.error(err.message || 'Failed to cancel'),
  });

  const purgeMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.adminPurgeUser(accessToken, {
        user_email: purgeEmail.trim(),
        reason: purgeReason.trim(),
        confirm: true,
      });
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['admin-deletion-requests'] });
      toast.success(`Purge initiated for ${purgeEmail}. ${data.records_marked} records marked.`);
      setPurgeEmail('');
      setPurgeReason('');
      setShowPurgeForm(false);
    },
    onError: (err: Error) => toast.error(err.message || 'Failed to purge user data'),
  });

  const pendingRequests = (deletionRequests?.requests || []).filter(
    (r) => r.status === 'pending' || r.status === 'confirmed'
  );

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Trash2 className="w-5 h-5 text-destructive" />
          <CardTitle>Data Deletion Management</CardTitle>
        </div>
        <CardDescription>
          Review and manage GDPR data deletion requests. Deletions follow a 90-day grace period.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Pending requests */}
        <div>
          <h4 className="text-sm font-semibold mb-3">
            Active Requests ({pendingRequests.length})
          </h4>
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : pendingRequests.length === 0 ? (
            <p className="text-sm text-muted-foreground">No active deletion requests.</p>
          ) : (
            <div className="space-y-3">
              {pendingRequests.map((req) => (
                <div
                  key={req.id}
                  className="flex items-center justify-between rounded-lg border border-border p-3"
                >
                  <div>
                    <p className="text-sm font-medium">
                      {req.scope === 'account' ? 'Account Deletion' : req.scope === 'user_data' ? 'User Data Purge' : 'Personal Data Deletion'}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Requested: {new Date(req.requested_at).toLocaleDateString()} |
                      Purge: {new Date(req.scheduled_purge_at).toLocaleDateString()} |
                      ID: {req.id}
                    </p>
                    {req.reason && (
                      <p className="text-xs text-muted-foreground mt-1">Reason: {req.reason}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      className={
                        req.status === 'confirmed'
                          ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'
                          : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                      }
                    >
                      {req.status}
                    </Badge>
                    {req.status === 'pending' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => confirmMutation.mutate(req.id)}
                        disabled={confirmMutation.isPending}
                      >
                        Approve
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => cancelMutation.mutate(req.id)}
                      disabled={cancelMutation.isPending}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Admin purge user */}
        <div className="border-t border-border pt-4">
          <h4 className="text-sm font-semibold mb-2">Purge User Data</h4>
          <p className="text-xs text-muted-foreground mb-3">
            Remove a specific user's data from the organization. API keys will be revoked
            immediately. Account data follows the 90-day purge schedule.
          </p>
          {!showPurgeForm ? (
            <Button
              variant="outline"
              size="sm"
              className="text-destructive border-destructive/50 hover:bg-destructive/10"
              onClick={() => setShowPurgeForm(true)}
            >
              Purge user data
            </Button>
          ) : (
            <div className="space-y-3 rounded-lg border border-destructive/30 bg-destructive/5 p-4">
              <div>
                <label className="block text-xs font-medium mb-1">User email</label>
                <Input
                  value={purgeEmail}
                  onChange={(e) => setPurgeEmail(e.target.value)}
                  placeholder="user@example.com"
                  className="text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium mb-1">Reason</label>
                <Input
                  value={purgeReason}
                  onChange={(e) => setPurgeReason(e.target.value)}
                  placeholder="e.g. Employee offboarding, GDPR request"
                  className="text-sm"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="text-destructive border-destructive/50 hover:bg-destructive/10"
                  onClick={() => purgeMutation.mutate()}
                  disabled={purgeMutation.isPending || !purgeEmail.trim() || !purgeReason.trim()}
                >
                  {purgeMutation.isPending ? 'Purging...' : 'Confirm purge'}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setShowPurgeForm(false);
                    setPurgeEmail('');
                    setPurgeReason('');
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function OrganizationAdminPageInner() {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const router = useRouter();
  const { activeOrganization, isLoading: orgLoading } = useOrganization();
  const orgId = activeOrganization?.id;

  const { role, isAdmin, isLoading: roleLoading } = useCurrentUserRole(orgId, accessToken);

  const [redirecting, setRedirecting] = useState(false);

  useEffect(() => {
    // Wait for all data to be loaded before making redirect decision
    if (roleLoading || orgLoading || !orgId) return;
    if (!isAdmin && !redirecting) {
      setRedirecting(true);
      router.replace('/settings');
    }
  }, [isAdmin, roleLoading, orgLoading, orgId, router, redirecting]);

  if (orgLoading || roleLoading) {
    return (
      <DashboardLayout>
        <div className="p-8 text-muted-foreground">Loading organization administration...</div>
      </DashboardLayout>
    );
  }

  if (!isAdmin || redirecting) {
    return (
      <DashboardLayout>
        <div className="p-8 text-center">
          <p className="text-muted-foreground">
            You do not have permission to view this page. Redirecting...
          </p>
        </div>
      </DashboardLayout>
    );
  }

  if (!orgId) {
    return (
      <DashboardLayout>
        <div className="p-8 text-center">
          <p className="text-muted-foreground">No organization selected.</p>
          <Link href="/settings" className="text-sm text-blue-ncs hover:underline mt-2 inline-block">
            Back to settings
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="mb-8">
        <Link
          href="/settings"
          className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Settings
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-delft-blue dark:text-white">
            Organization Administration
          </h1>
          <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
            {role}
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Manage security policies, signing defaults, and feature configuration for{' '}
          <span className="font-medium">{activeOrganization?.name}</span>.
        </p>
      </div>

      <div className="space-y-6">
        <SecurityPoliciesCard orgId={orgId} accessToken={accessToken} />
        <DefaultSigningConfigCard />
        <FeatureOverviewCard />
        <DeletionManagementCard accessToken={accessToken} />
      </div>
    </DashboardLayout>
  );
}

export default function OrganizationAdminPage() {
  return (
    <Suspense fallback={<div className="p-8 text-muted-foreground">Loading...</div>}>
      <OrganizationAdminPageInner />
    </Suspense>
  );
}
