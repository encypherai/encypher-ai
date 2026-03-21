'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Input,
  Badge,
} from '@encypher/design-system';
import { toast } from 'sonner';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { EnterpriseGate } from '../../components/ui/enterprise-gate';
import { useOrganization } from '../../contexts/OrganizationContext';
import apiClient from '../../lib/api';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';

// Role configuration
const ROLE_CONFIG: Record<string, { color: string; bgColor: string }> = {
  owner:   { color: 'text-yellow-600 dark:text-yellow-400', bgColor: 'bg-yellow-100 dark:bg-yellow-900/30' },
  admin:   { color: 'text-blue-600 dark:text-blue-400',     bgColor: 'bg-blue-100 dark:bg-blue-900/30'     },
  manager: { color: 'text-purple-600 dark:text-purple-400', bgColor: 'bg-purple-100 dark:bg-purple-900/30' },
  member:  { color: 'text-green-600 dark:text-green-400',   bgColor: 'bg-green-100 dark:bg-green-900/30'   },
  viewer:  { color: 'text-gray-600 dark:text-gray-400',     bgColor: 'bg-gray-100 dark:bg-gray-800'        },
};

interface TeamMember {
  id: string;
  user_id: string;
  user_email?: string;
  user_name?: string;
  role: string;
  status: string;
  invited_at?: string;
  accepted_at?: string;
  last_active_at?: string;
}

interface Invitation {
  id: string;
  email: string;
  role: string;
  status: string;
  expires_at: string;
  created_at: string;
  tier?: string | null;
  trial_months?: number | null;
}

interface SeatInfo {
  used: number;
  active: number;
  pending: number;
  max: number;
  available: number;
  unlimited: boolean;
}

interface ApiKeysByMemberProps {
  orgId: string;
  members: TeamMember[];
  accessToken: string | undefined;
}

function ApiKeysByMember({ orgId, members, accessToken }: ApiKeysByMemberProps) {
  const queryClient = useQueryClient();
  const [expandedMember, setExpandedMember] = useState<string | null>(null);
  const [revokeConfirm, setRevokeConfirm] = useState<{ open: boolean; member: TeamMember | null }>({ open: false, member: null });

  const { data: apiKeys, isLoading } = useQuery({
    queryKey: ['org-api-keys', orgId],
    queryFn: async () => {
      if (!accessToken) return [];
      const response = await apiClient.getApiKeys(accessToken, orgId);
      return response || [];
    },
    enabled: !!accessToken && !!orgId,
  });

  const revokeKeysByUserMutation = useMutation({
    mutationFn: async (userId: string) => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.revokeKeysByUser(accessToken, orgId, userId);
    },
    onSuccess: (data, userId) => {
      queryClient.invalidateQueries({ queryKey: ['org-api-keys', orgId] });
      toast.success(`Revoked ${data.revoked_count} API key(s) for user`);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to revoke keys');
    },
  });

  const keysByMember = members.map((member) => ({
    member,
    keys: (apiKeys || []).filter((key: any) => key.created_by === member.user_id || key.user_id === member.user_id),
  }));

  if (isLoading) {
    return <div className="text-center py-4 text-muted-foreground">Loading API keys...</div>;
  }

  return (
    <div className="space-y-3">
      <ConfirmDialog
        open={revokeConfirm.open}
        onOpenChange={(open) => setRevokeConfirm((s) => ({ ...s, open }))}
        title="Revoke API Keys"
        description={
          revokeConfirm.member
            ? `Revoke all API keys for ${revokeConfirm.member.user_email || revokeConfirm.member.user_name}?`
            : 'Revoke all API keys for this member?'
        }
        confirmLabel="Revoke All"
        variant="destructive"
        onConfirm={() => {
          if (revokeConfirm.member) {
            revokeKeysByUserMutation.mutate(revokeConfirm.member.user_id);
          }
        }}
      />
      {keysByMember.map(({ member, keys }) => (
        <div key={member.user_id} className="border border-border rounded-lg">
          <button
            onClick={() => setExpandedMember(expandedMember === member.user_id ? null : member.user_id)}
            className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="text-sm font-medium">{member.user_email || member.user_name}</div>
              <Badge variant="secondary">{keys.length} key{keys.length !== 1 ? 's' : ''}</Badge>
            </div>
            <div className="flex items-center gap-2">
              {keys.length > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    setRevokeConfirm({ open: true, member });
                  }}
                  className="text-destructive hover:text-destructive"
                >
                  Revoke All
                </Button>
              )}
              <svg
                className={`w-5 h-5 transition-transform ${expandedMember === member.user_id ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </button>
          {expandedMember === member.user_id && keys.length > 0 && (
            <div className="px-4 pb-4 space-y-2">
              {keys.map((key: any) => (
                <div key={key.id} className="flex items-center justify-between p-3 bg-muted/30 rounded text-sm">
                  <div>
                    <div className="font-medium">{key.name}</div>
                    <div className="text-xs text-muted-foreground font-mono">{key.fingerprint?.slice(0, 16)}...</div>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {new Date(key.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default function TeamPage() {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const queryClient = useQueryClient();
  const {
    activeOrganization,
    isLoading: orgLoading,
    refetch: refetchOrganizations,
    setActiveOrganization,
  } = useOrganization();

  const [removeConfirm, setRemoveConfirm] = useState<{ open: boolean; memberId: string | null }>({ open: false, memberId: null });
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('member');
  const [showInviteForm, setShowInviteForm] = useState(Boolean(process.env.NEXT_PUBLIC_E2E_TEST));
  const [showCreateOrgForm, setShowCreateOrgForm] = useState(false);
  const [orgName, setOrgName] = useState('');
  const [orgEmail, setOrgEmail] = useState('');
  const [showBulkInvite, setShowBulkInvite] = useState(false);
  const [bulkInviteText, setBulkInviteText] = useState('');
  const [bulkInviteParsed, setBulkInviteParsed] = useState<Array<{ email: string; role: string }>>([]);

  // Use active organization from context
  const orgId = activeOrganization?.id;

  // Check if the active organization supports team management
  const activeOrgTier = activeOrganization?.tier || (session?.user as any)?.tier || 'free';
  const hasTeamFeature = activeOrgTier === 'enterprise' || activeOrgTier === 'strategic_partner';

  const createOrgMutation = useMutation({
    mutationFn: async ({ name, email }: { name: string; email: string }) => {
      if (!accessToken) throw new Error('You must be signed in to create an organization.');
      return apiClient.createOrganization(accessToken, { name, email });
    },
    onSuccess: async (response) => {
      await refetchOrganizations();
      if (response?.data) {
        setActiveOrganization(response.data);
      }
      setOrgName('');
      setOrgEmail('');
      setShowCreateOrgForm(false);
      toast.success('Organization created successfully.');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create organization.');
    },
  });

  // Fetch seat info
  const seatsQuery = useQuery({
    queryKey: ['org-seats', orgId],
    queryFn: async () => {
      if (!accessToken || !hasTeamFeature || !orgId) return null;
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/organizations/${orgId}/seats`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        if (!response.ok) return null;
        const data = await response.json();
        return data.data as SeatInfo;
      } catch {
        return null;
      }
    },
    enabled: Boolean(accessToken) && hasTeamFeature && Boolean(orgId),
  });

  // Fetch team members
  const membersQuery = useQuery({
    queryKey: ['org-members', orgId],
    queryFn: async () => {
      if (!accessToken || !hasTeamFeature || !orgId) return [];
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/organizations/${orgId}/members`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        if (!response.ok) return [];
        const data = await response.json();
        return data.data as TeamMember[];
      } catch {
        return [];
      }
    },
    enabled: Boolean(accessToken) && hasTeamFeature && Boolean(orgId),
  });

  // Fetch pending invitations
  const invitationsQuery = useQuery({
    queryKey: ['org-invitations', orgId],
    queryFn: async () => {
      if (!accessToken || !hasTeamFeature || !orgId) return [];
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/organizations/${orgId}/invitations`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        if (!response.ok) return [];
        const data = await response.json();
        return data.data as Invitation[];
      } catch {
        return [];
      }
    },
    enabled: Boolean(accessToken) && hasTeamFeature && Boolean(orgId),
  });

  // Invite mutation
  const inviteMutation = useMutation({
    mutationFn: async ({
      email,
      role,
    }: {
      email: string;
      role: string;
    }) => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/organizations/${orgId}/invitations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ email, role }),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to send invitation');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org-invitations'] });
      queryClient.invalidateQueries({ queryKey: ['org-seats'] });
      setInviteEmail('');
      setInviteRole('member');
      setShowInviteForm(false);
      toast.success('Invitation sent successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  const handleSendInvite = () => {
    if (!inviteEmail) return;

    inviteMutation.mutate({
      email: inviteEmail,
      role: inviteRole,
    });
  };

  const handleBulkInviteParse = (text: string) => {
    setBulkInviteText(text);
    const lines = text.split(/[\n,]+/).map((l) => l.trim()).filter(Boolean);
    const parsed: Array<{ email: string; role: string }> = [];
    for (const line of lines) {
      const parts = line.split(/[,\t;]+/).map((p) => p.trim());
      const email = parts[0] || '';
      const role = parts[1] || 'member';
      if (email && email.includes('@')) {
        parsed.push({ email, role: ['admin', 'member', 'viewer', 'manager'].includes(role) ? role : 'member' });
      }
    }
    setBulkInviteParsed(parsed);
  };

  const handleBulkInviteFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      if (text) handleBulkInviteParse(text);
    };
    reader.readAsText(file);
  };

  const bulkInviteMutation = useMutation({
    mutationFn: async (invitations: Array<{ email: string; role: string }>) => {
      if (!accessToken || !orgId) throw new Error('Not authenticated');
      return apiClient.bulkInviteMembers(accessToken, orgId, invitations);
    },
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: ['org-invitations'] });
      queryClient.invalidateQueries({ queryKey: ['org-seats'] });
      setBulkInviteText('');
      setBulkInviteParsed([]);
      setShowBulkInvite(false);
      toast.success(`Bulk invite complete: ${data.succeeded} sent, ${data.failed} failed`);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Bulk invite failed');
    },
  });

  // Cancel invitation mutation
  const cancelInviteMutation = useMutation({
    mutationFn: async (invitationId: string) => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/organizations/${orgId}/invitations/${invitationId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!response.ok) throw new Error('Failed to cancel invitation');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org-invitations'] });
      queryClient.invalidateQueries({ queryKey: ['org-seats'] });
      toast.success('Invitation cancelled');
    },
    onError: () => {
      toast.error('Failed to cancel invitation');
    },
  });

  const resendInviteMutation = useMutation({
    mutationFn: async (invitationId: string) => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/organizations/${orgId}/invitations/${invitationId}/resend`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!response.ok) {
        const error = await response.json().catch(() => null);
        throw new Error(error?.detail || 'Failed to resend invitation');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org-invitations'] });
      queryClient.invalidateQueries({ queryKey: ['org-seats'] });
      toast.success('Invitation resent');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to resend invitation');
    },
  });

  // Remove member mutation
  const removeMemberMutation = useMutation({
    mutationFn: async (userId: string) => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/organizations/${orgId}/members/${userId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!response.ok) throw new Error('Failed to remove member');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org-members'] });
      queryClient.invalidateQueries({ queryKey: ['org-seats'] });
      toast.success('Member removed');
    },
    onError: () => {
      toast.error('Failed to remove member');
    },
  });

  // Update role mutation
  const updateRoleMutation = useMutation({
    mutationFn: async ({ userId, role }: { userId: string; role: string }) => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/organizations/${orgId}/members/${userId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ role }),
      });
      if (!response.ok) throw new Error('Failed to update role');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org-members'] });
      toast.success('Role updated');
    },
    onError: () => {
      toast.error('Failed to update role');
    },
  });

  const members = membersQuery.data || [];
  const invitations = invitationsQuery.data || [];
  const seats = seatsQuery.data;
  const canInvite = seats ? (seats.unlimited || seats.available > 0) : false;
  const isLoadingTeam = membersQuery.isLoading || orgLoading;

  if (orgLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-ncs"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (!orgId) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center py-16 px-4 text-center gap-6">
          <div>
            <div className="w-20 h-20 mb-6 rounded-full bg-blue-ncs/10 flex items-center justify-center mx-auto">
              <svg className="w-10 h-10 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-foreground mb-2">Select an Organization</h2>
            <p className="text-muted-foreground text-center max-w-md mb-6">
              Choose an organization from the switcher to manage members and invitations, or create a new organization to get started.
            </p>
            <Button variant="outline" onClick={() => setShowCreateOrgForm((current) => !current)}>
              {showCreateOrgForm ? 'Hide Form' : 'Create Organization'}
            </Button>
          </div>
          {showCreateOrgForm && (
            <Card className="w-full max-w-2xl text-left">
              <CardHeader>
                <CardTitle>Create Organization</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-4">
                  <div className="flex flex-col md:flex-row gap-4">
                    <div className="flex-1">
                      <Input
                        type="text"
                        placeholder="Organization name"
                        value={orgName}
                        onChange={(e) => setOrgName(e.target.value)}
                      />
                    </div>
                    <div className="flex-1">
                      <Input
                        type="email"
                        placeholder="Billing contact email"
                        value={orgEmail}
                        onChange={(e) => setOrgEmail(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <Button
                      variant="primary"
                      onClick={() => createOrgMutation.mutate({ name: orgName, email: orgEmail })}
                      disabled={!orgName || !orgEmail || createOrgMutation.isPending}
                    >
                      {createOrgMutation.isPending ? 'Creating...' : 'Create Organization'}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setShowCreateOrgForm(false)}
                      disabled={createOrgMutation.isPending}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </DashboardLayout>
    );
  }

  // Show upgrade prompt for non-Enterprise users
  if (!hasTeamFeature) {
    return (
      <DashboardLayout>
        <EnterpriseGate
          icon={
            <svg className="w-8 h-8 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          }
          title="Team Management"
          description="Invite your organization's team, enforce role-based access control, and manage API keys per member -- all from a single unified dashboard."
          features={[
            'Role-based access control (Owner, Admin, Manager, Member, Viewer)',
            'Bulk team invitations via CSV or paste',
            'API key management per team member',
            'Seat-based billing with usage tracking',
          ]}
        />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-delft-blue dark:text-white">Team Management</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Manage your organization's team members and roles.
            </p>
            {activeOrganization && (
              <p className="text-xs text-muted-foreground mt-2">
                Active organization: <span className="font-medium text-foreground">{activeOrganization.name}</span>
              </p>
            )}
          </div>
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <Button
              variant="outline"
              onClick={() => setShowCreateOrgForm(!showCreateOrgForm)}
              disabled={createOrgMutation.isPending}
              className="w-full sm:w-auto"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Create Organization
            </Button>
            <Button
              variant="primary"
              onClick={() => setShowInviteForm(!showInviteForm)}
              disabled={!canInvite}
              data-testid="invite-toggle"
              className="w-full sm:w-auto"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
              Invite Member
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowBulkInvite(!showBulkInvite)}
              disabled={!canInvite}
              data-testid="bulk-invite-toggle"
              className="w-full sm:w-auto"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Bulk Invite
            </Button>
          </div>
        </div>

        {showCreateOrgForm && (
          <Card>
            <CardHeader>
              <CardTitle>Create Organization</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-4">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <Input
                      type="text"
                      placeholder="Organization name"
                      value={orgName}
                      onChange={(e) => setOrgName(e.target.value)}
                    />
                  </div>
                  <div className="flex-1">
                    <Input
                      type="email"
                      placeholder="Billing contact email"
                      value={orgEmail}
                      onChange={(e) => setOrgEmail(e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button
                    variant="primary"
                    onClick={() => createOrgMutation.mutate({ name: orgName, email: orgEmail })}
                    disabled={!orgName || !orgEmail || createOrgMutation.isPending}
                  >
                    {createOrgMutation.isPending ? 'Creating...' : 'Create Organization'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowCreateOrgForm(false)}
                    disabled={createOrgMutation.isPending}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Seat Usage */}
        {seats && (
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Team Seats</p>
                  <p className="text-2xl font-bold text-delft-blue dark:text-white">
                    {seats.used} / {seats.unlimited ? '∞' : seats.max}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {seats.active} active, {seats.pending} pending
                  </p>
                </div>
                {!seats.unlimited && seats.available === 0 && (
                  <div className="flex items-center gap-3">
                    <Badge variant="warning">Seat limit reached</Badge>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => {
                        window.location.href = `/billing?upgrade=seats&quantity=5&current=${seats.used}&max=${seats.max}`;
                      }}
                    >
                      Upgrade Seats
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Invite Form */}
        {showInviteForm && (
          <Card>
            <CardHeader>
              <CardTitle>Invite Team Member</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-4">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <Input
                      type="email"
                      placeholder="colleague@company.com"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      data-testid="invite-email"
                    />
                  </div>
                  <div className="w-full md:w-48">
                    <select
                      value={inviteRole}
                      onChange={(e) => setInviteRole(e.target.value)}
                      className="w-full h-10 px-3 border border-border rounded-lg bg-background text-foreground"
                      data-testid="invite-role"
                    >
                      <option value="admin">Admin</option>
                      <option value="manager">Manager</option>
                      <option value="member">Member</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  </div>
                  <Button
                    variant="primary"
                    onClick={handleSendInvite}
                    disabled={!inviteEmail || inviteMutation.isPending}
                    data-testid="invite-submit"
                  >
                    {inviteMutation.isPending ? 'Sending...' : 'Send Invite'}
                  </Button>
                  <Button variant="outline" onClick={() => setShowInviteForm(false)}>
                    Cancel
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Bulk Invite */}
        {showBulkInvite && (
          <Card>
            <CardHeader>
              <CardTitle>Bulk Invite Team Members</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-4">
                <p className="text-sm text-muted-foreground">
                  Paste emails (one per line) or upload a CSV file. Optionally include a role after a comma (admin, member, viewer). Default role is member.
                </p>
                <textarea
                  value={bulkInviteText}
                  onChange={(e) => handleBulkInviteParse(e.target.value)}
                  placeholder={"alice@company.com, admin\nbob@company.com\ncarol@company.com, viewer"}
                  className="w-full h-32 px-3 py-2 border border-border rounded-lg bg-background text-foreground font-mono text-sm resize-y"
                  data-testid="bulk-invite-textarea"
                />
                <div className="flex items-center gap-4">
                  <label className="cursor-pointer text-sm text-blue-ncs hover:underline">
                    Upload CSV
                    <input
                      type="file"
                      accept=".csv,.txt"
                      onChange={handleBulkInviteFile}
                      className="hidden"
                    />
                  </label>
                  {bulkInviteParsed.length > 0 && (
                    <span className="text-sm text-muted-foreground">
                      {bulkInviteParsed.length} email{bulkInviteParsed.length !== 1 ? 's' : ''} parsed
                    </span>
                  )}
                </div>
                {bulkInviteParsed.length > 0 && (
                  <div className="border border-border rounded-lg p-3 max-h-48 overflow-y-auto">
                    <div className="space-y-1">
                      {bulkInviteParsed.map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between text-sm">
                          <span className="font-mono">{item.email}</span>
                          <Badge variant="secondary">{item.role}</Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                <div className="flex gap-3">
                  <Button
                    variant="primary"
                    onClick={() => bulkInviteMutation.mutate(bulkInviteParsed)}
                    disabled={bulkInviteParsed.length === 0 || bulkInviteMutation.isPending}
                    data-testid="bulk-invite-submit"
                  >
                    {bulkInviteMutation.isPending
                      ? 'Sending...'
                      : `Send ${bulkInviteParsed.length} Invite${bulkInviteParsed.length !== 1 ? 's' : ''}`}
                  </Button>
                  <Button variant="outline" onClick={() => setShowBulkInvite(false)}>
                    Cancel
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Pending Invitations */}
        {invitations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Pending Invitations ({invitations.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {invitations.map((inv) => (
                  <div key={inv.id} className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center">
                        <svg className="w-5 h-5 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div>
                        <p className="font-medium">{inv.email}</p>
                        <p className="text-xs text-muted-foreground">
                          Expires {new Date(inv.expires_at).toLocaleDateString()}
                        </p>
                        {(inv.tier || inv.trial_months) && (
                          <p className="text-xs text-muted-foreground">
                            Trial: {inv.tier ? inv.tier : 'tier pending'}
                            {inv.trial_months ? ` · ${inv.trial_months} month${inv.trial_months === 1 ? '' : 's'}` : ''}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant="secondary">{inv.role}</Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => resendInviteMutation.mutate(inv.id)}
                        disabled={resendInviteMutation.isPending}
                      >
                        Resend
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => cancelInviteMutation.mutate(inv.id)}
                        disabled={cancelInviteMutation.isPending}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* API Keys by Member */}
        {hasTeamFeature && orgId && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">API Keys by Member</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                View and manage API keys created by team members
              </p>
            </CardHeader>
            <CardContent>
              <ApiKeysByMember orgId={orgId} members={members} accessToken={accessToken} />
            </CardContent>
          </Card>
        )}

        {/* Team Members */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Team Members ({members.length})</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingTeam ? (
              <div className="text-center py-8 text-muted-foreground">Loading team members...</div>
            ) : members.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No team members yet. Invite someone to get started!
              </div>
            ) : (
              <div className="space-y-3">
                {members.map((member) => {
                  const roleConfig = ROLE_CONFIG[member.role] || ROLE_CONFIG.member;
                  const isOwner = member.role === 'owner';

                  return (
                    <div key={member.id} className="flex items-center justify-between p-4 border border-border rounded-lg">
                      <div className="flex items-center gap-4 min-w-0 flex-1">
                        <div className={`w-10 h-10 rounded-full ${roleConfig.bgColor} flex items-center justify-center flex-shrink-0`}>
                          <span className={`text-sm font-semibold ${roleConfig.color}`}>
                            {(member.user_name || member.user_email || '?')[0].toUpperCase()}
                          </span>
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="font-medium">{member.user_name || member.user_email}</p>
                            {member.status === 'active' && (
                              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                          {member.user_name && <p className="text-sm text-muted-foreground">{member.user_email}</p>}
                        </div>
                      </div>
                      <div className="flex items-center gap-3 flex-shrink-0">
                        <Badge variant={isOwner ? 'primary' : 'secondary'}>{member.role}</Badge>
                        {!isOwner && (
                          <div className="flex gap-2">
                            <select
                              value={member.role}
                              onChange={(e) => updateRoleMutation.mutate({ userId: member.user_id, role: e.target.value })}
                              className="h-8 px-2 text-sm border border-border rounded bg-background"
                            >
                              <option value="admin">Admin</option>
                              <option value="manager">Manager</option>
                              <option value="member">Member</option>
                              <option value="viewer">Viewer</option>
                            </select>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setRemoveConfirm({ open: true, memberId: member.user_id })}
                              className="text-destructive hover:text-destructive"
                            >
                              Remove
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <ConfirmDialog
        open={removeConfirm.open}
        onOpenChange={(open) => setRemoveConfirm((s) => ({ ...s, open }))}
        title="Remove Team Member"
        description="Remove this member from the team?"
        confirmLabel="Remove"
        variant="destructive"
        onConfirm={() => {
          if (removeConfirm.memberId) {
            removeMemberMutation.mutate(removeConfirm.memberId);
          }
        }}
      />
    </DashboardLayout>
  );
}
