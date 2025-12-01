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
import { useOrganization } from '../../contexts/OrganizationContext';
import apiClient from '../../lib/api';

// Role configuration
const ROLE_CONFIG: Record<string, { color: string; bgColor: string }> = {
  owner: { color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
  admin: { color: 'text-blue-600', bgColor: 'bg-blue-100' },
  manager: { color: 'text-purple-600', bgColor: 'bg-purple-100' },
  member: { color: 'text-green-600', bgColor: 'bg-green-100' },
  viewer: { color: 'text-gray-600', bgColor: 'bg-gray-100' },
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
}

interface SeatInfo {
  used: number;
  active: number;
  pending: number;
  max: number;
  available: number;
  unlimited: boolean;
}

export default function TeamPage() {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const queryClient = useQueryClient();
  const { activeOrganization, isLoading: orgLoading } = useOrganization();
  
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('member');
  const [showInviteForm, setShowInviteForm] = useState(false);

  // Use active organization from context
  const orgId = activeOrganization?.id;

  // Check if user has Business+ tier
  const userTier = (session?.user as any)?.tier || 'starter';
  const hasTeamFeature = ['business', 'enterprise'].includes(userTier);

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
    mutationFn: async ({ email, role }: { email: string; role: string }) => {
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

  // Show upgrade prompt for non-Business users
  if (!hasTeamFeature) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center py-16 px-4">
          <div className="w-20 h-20 mb-6 rounded-full bg-blue-ncs/10 flex items-center justify-center">
            <svg className="w-10 h-10 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-2">Team Management</h2>
          <p className="text-muted-foreground text-center max-w-md mb-6">
            Invite team members, assign roles, and manage access to your organization's resources.
            Team management is available on Business and Enterprise plans.
          </p>
          <Button variant="primary" onClick={() => window.location.href = '/billing'}>
            Upgrade to Business
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold text-delft-blue dark:text-white mb-1">Team Management</h2>
            <p className="text-muted-foreground">
              Manage your organization's team members and roles
            </p>
          </div>
          <Button
            variant="primary"
            onClick={() => setShowInviteForm(!showInviteForm)}
            disabled={!canInvite}
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
            Invite Member
          </Button>
        </div>

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
                  <Badge variant="warning">Seat limit reached</Badge>
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
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <Input
                    type="email"
                    placeholder="colleague@company.com"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                  />
                </div>
                <div className="w-full md:w-48">
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                    className="w-full h-10 px-3 border border-border rounded-lg bg-background text-foreground"
                  >
                    <option value="admin">Admin</option>
                    <option value="manager">Manager</option>
                    <option value="member">Member</option>
                    <option value="viewer">Viewer</option>
                  </select>
                </div>
                <Button
                  variant="primary"
                  onClick={() => inviteMutation.mutate({ email: inviteEmail, role: inviteRole })}
                  disabled={!inviteEmail || inviteMutation.isPending}
                >
                  {inviteMutation.isPending ? 'Sending...' : 'Send Invite'}
                </Button>
                <Button variant="outline" onClick={() => setShowInviteForm(false)}>
                  Cancel
                </Button>
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
                      <div className="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
                        <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div>
                        <p className="font-medium">{inv.email}</p>
                        <p className="text-xs text-muted-foreground">
                          Expires {new Date(inv.expires_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant="secondary">{inv.role}</Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => cancelInviteMutation.mutate(inv.id)}
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

        {/* Team Members */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Team Members ({members.length})</CardTitle>
          </CardHeader>
          <CardContent>
            {membersQuery.isLoading ? (
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
                      <div className="flex items-center gap-4">
                        <div className={`w-10 h-10 rounded-full ${roleConfig.bgColor} flex items-center justify-center`}>
                          <span className={`text-sm font-semibold ${roleConfig.color}`}>
                            {(member.user_name || member.user_email || '?')[0].toUpperCase()}
                          </span>
                        </div>
                        <div>
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
                      <div className="flex items-center gap-3">
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
                              onClick={() => {
                                if (confirm('Remove this member from the team?')) {
                                  removeMemberMutation.mutate(member.user_id);
                                }
                              }}
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
    </DashboardLayout>
  );
}

