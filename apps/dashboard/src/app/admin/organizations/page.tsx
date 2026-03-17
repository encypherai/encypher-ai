'use client';

import Link from 'next/link';
import { useMemo, useState, type ChangeEvent } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { toast } from 'sonner';
import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import apiClient, { type DomainClaimInfo, type OrganizationInfo, type OrganizationInvitationInfo, type OrganizationMemberInfo, type OrganizationSeatInfo } from '../../../lib/api';

type OrganizationOption = {
  id: string;
  name: string;
  email: string;
  tier: string;
  slug?: string | null;
};

function StatusBadge({ label, tone = 'default' }: { label: string; tone?: 'default' | 'success' | 'warning' | 'error' }) {
  const tones = {
    default: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
    success: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
    warning: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
    error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  };

  return <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${tones[tone]}`}>{label}</span>;
}

function formatRole(role: string) {
  return role.charAt(0).toUpperCase() + role.slice(1);
}

export default function AdminOrganizationsPage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const queryClient = useQueryClient();
  const [orgSearch, setOrgSearch] = useState('');
  const [selectedOrg, setSelectedOrg] = useState<OrganizationOption | null>(null);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('member');

  const superAdminQuery = useQuery({
    queryKey: ['is-super-admin'],
    queryFn: async () => {
      if (!accessToken) return false;
      return apiClient.isSuperAdmin(accessToken);
    },
    enabled: Boolean(accessToken),
  });

  const isSuperAdmin = superAdminQuery.data === true;
  const selectedOrgId = selectedOrg?.id;

  const orgSearchQuery = useQuery<OrganizationOption[]>({
    queryKey: ['admin-org-search', orgSearch],
    queryFn: async () => {
      if (!accessToken) return [];
      return await apiClient.searchAdminOrganizations(accessToken, orgSearch.trim(), 10) as OrganizationOption[];
    },
    enabled: Boolean(accessToken) && isSuperAdmin && orgSearch.trim().length >= 2 && !selectedOrg,
  });

  const organizationQuery = useQuery<OrganizationInfo>({
    queryKey: ['admin-org-details', selectedOrgId],
    queryFn: async () => {
      if (!accessToken || !selectedOrgId) throw new Error('Organization not selected.');
      return apiClient.getOrganization(accessToken, selectedOrgId);
    },
    enabled: Boolean(accessToken) && Boolean(selectedOrgId) && isSuperAdmin,
  });

  const seatsQuery = useQuery<OrganizationSeatInfo>({
    queryKey: ['admin-org-seats', selectedOrgId],
    queryFn: async () => {
      if (!accessToken || !selectedOrgId) throw new Error('Organization not selected.');
      return apiClient.getOrganizationSeatInfo(accessToken, selectedOrgId);
    },
    enabled: Boolean(accessToken) && Boolean(selectedOrgId) && isSuperAdmin,
  });

  const membersQuery = useQuery<OrganizationMemberInfo[]>({
    queryKey: ['admin-org-members', selectedOrgId],
    queryFn: async () => {
      if (!accessToken || !selectedOrgId) throw new Error('Organization not selected.');
      return apiClient.listOrganizationMembers(accessToken, selectedOrgId);
    },
    enabled: Boolean(accessToken) && Boolean(selectedOrgId) && isSuperAdmin,
  });

  const invitationsQuery = useQuery<OrganizationInvitationInfo[]>({
    queryKey: ['admin-org-invitations', selectedOrgId],
    queryFn: async () => {
      if (!accessToken || !selectedOrgId) throw new Error('Organization not selected.');
      return apiClient.listOrganizationInvitations(accessToken, selectedOrgId);
    },
    enabled: Boolean(accessToken) && Boolean(selectedOrgId) && isSuperAdmin,
  });

  const domainClaimsQuery = useQuery<DomainClaimInfo[]>({
    queryKey: ['admin-org-domain-claims', selectedOrgId],
    queryFn: async () => {
      if (!accessToken || !selectedOrgId) throw new Error('Organization not selected.');
      return apiClient.listDomainClaims(accessToken, selectedOrgId);
    },
    enabled: Boolean(accessToken) && Boolean(selectedOrgId) && isSuperAdmin,
  });

  const inviteMutation = useMutation({
    mutationFn: async ({ email, role }: { email: string; role: string }) => {
      if (!accessToken || !selectedOrgId) throw new Error('Organization not selected.');
      return apiClient.createOrganizationInvitation(accessToken, selectedOrgId, { email, role });
    },
    onSuccess: () => {
      setInviteEmail('');
      setInviteRole('member');
      toast.success('Invitation sent.');
      queryClient.invalidateQueries({ queryKey: ['admin-org-invitations', selectedOrgId] });
      queryClient.invalidateQueries({ queryKey: ['admin-org-seats', selectedOrgId] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to send invitation.');
    },
  });

  const resendInviteMutation = useMutation({
    mutationFn: async (invitationId: string) => {
      if (!accessToken || !selectedOrgId) throw new Error('Organization not selected.');
      return apiClient.resendOrganizationInvitation(accessToken, selectedOrgId, invitationId);
    },
    onSuccess: () => {
      toast.success('Invitation resent.');
      queryClient.invalidateQueries({ queryKey: ['admin-org-invitations', selectedOrgId] });
      queryClient.invalidateQueries({ queryKey: ['admin-org-seats', selectedOrgId] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to resend invitation.');
    },
  });

  const cancelInviteMutation = useMutation({
    mutationFn: async (invitationId: string) => {
      if (!accessToken || !selectedOrgId) throw new Error('Organization not selected.');
      return apiClient.cancelOrganizationInvitation(accessToken, selectedOrgId, invitationId);
    },
    onSuccess: () => {
      toast.success('Invitation cancelled.');
      queryClient.invalidateQueries({ queryKey: ['admin-org-invitations', selectedOrgId] });
      queryClient.invalidateQueries({ queryKey: ['admin-org-seats', selectedOrgId] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to cancel invitation.');
    },
  });

  const updateRoleMutation = useMutation({
    mutationFn: async ({ userId, role }: { userId: string; role: string }) => {
      if (!accessToken || !selectedOrgId) throw new Error('Organization not selected.');
      return apiClient.updateOrganizationMemberRole(accessToken, selectedOrgId, userId, role);
    },
    onSuccess: () => {
      toast.success('Member role updated.');
      queryClient.invalidateQueries({ queryKey: ['admin-org-members', selectedOrgId] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update member role.');
    },
  });

  const removeMemberMutation = useMutation({
    mutationFn: async (userId: string) => {
      if (!accessToken || !selectedOrgId) throw new Error('Organization not selected.');
      return apiClient.removeOrganizationMember(accessToken, selectedOrgId, userId);
    },
    onSuccess: () => {
      toast.success('Member removed.');
      queryClient.invalidateQueries({ queryKey: ['admin-org-members', selectedOrgId] });
      queryClient.invalidateQueries({ queryKey: ['admin-org-seats', selectedOrgId] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to remove member.');
    },
  });

  const organization = organizationQuery.data;
  const seatInfo = seatsQuery.data;
  const members = membersQuery.data ?? [];
  const invitations = invitationsQuery.data ?? [];
  const domainClaims = domainClaimsQuery.data ?? [];

  const pendingInviteCount = useMemo(() => invitations.filter((invite) => invite.status === 'pending').length, [invitations]);

  const handleOrgSearchChange = (value: string) => {
    setOrgSearch(value);
    setSelectedOrg(null);
  };

  const handleSendInvite = () => {
    if (!inviteEmail.trim()) {
      toast.error('Invitee email is required.');
      return;
    }
    inviteMutation.mutate({ email: inviteEmail.trim(), role: inviteRole });
  };

  if (status === 'loading' || superAdminQuery.isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-ncs"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (!isSuperAdmin) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center min-h-[400px] text-center px-4">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Admin Access Required</h1>
          <p className="text-slate-500 dark:text-slate-400 max-w-md mb-6">
            You need super admin privileges to access organization management.
          </p>
          <Link href="/admin" className="inline-flex items-center px-4 py-2 bg-blue-ncs text-white rounded-lg hover:bg-delft-blue transition-colors font-medium">
            Return to Admin Dashboard
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Organization Management</h1>
              <StatusBadge label="Super Admin" tone="warning" />
            </div>
            <p className="text-slate-500 dark:text-slate-400">Search an organization to oversee members, pending invites, and claimed domains.</p>
          </div>
          <Link href="/admin" className="inline-flex items-center justify-center rounded-lg border border-slate-300 dark:border-slate-600 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800">
            Back to Admin Dashboard
          </Link>
        </div>

        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm p-6 space-y-4">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Organization lookup</label>
            <div className="relative mt-1">
              <input
                type="text"
                value={orgSearch}
                onChange={(e: ChangeEvent<HTMLInputElement>) => handleOrgSearchChange(e.target.value)}
                placeholder="Search by org name, slug, email, or ID"
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white"
              />
              {selectedOrg && (
                <button
                  type="button"
                  onClick={() => handleOrgSearchChange('')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-slate-600"
                >
                  Clear
                </button>
              )}
              {orgSearchQuery.isLoading && !selectedOrg && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 border-2 border-blue-ncs border-t-transparent rounded-full animate-spin" />
              )}
            </div>
            {orgSearchQuery.data && orgSearchQuery.data.length > 0 && !selectedOrg && (
              <div className="mt-2 overflow-hidden rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-lg">
                {orgSearchQuery.data.map((org) => (
                  <button
                    key={org.id}
                    type="button"
                    onClick={() => {
                      setSelectedOrg(org);
                      setOrgSearch(`${org.name} (${org.id})`);
                    }}
                    className="w-full border-b border-slate-100 dark:border-slate-800 px-3 py-2 text-left text-sm hover:bg-slate-50 dark:hover:bg-slate-800 last:border-b-0"
                  >
                    <div className="font-medium text-slate-900 dark:text-white">{org.name}</div>
                    <div className="text-xs text-slate-500">{org.id} • {org.email}</div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {selectedOrg && (
            <div className="rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/40 p-4">
              <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <div>
                  <div className="text-sm font-semibold text-slate-900 dark:text-white">{selectedOrg.name}</div>
                  <div className="text-xs text-slate-500">{selectedOrg.id} • {selectedOrg.email}</div>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge label={selectedOrg.tier} tone={selectedOrg.tier === 'enterprise' || selectedOrg.tier === 'strategic_partner' ? 'warning' : 'default'} />
                </div>
              </div>
            </div>
          )}
        </div>

        {selectedOrgId && (
          <>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
              <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
                <div className="text-sm text-slate-500">Members</div>
                <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{members.length}</div>
              </div>
              <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
                <div className="text-sm text-slate-500">Pending invites</div>
                <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{pendingInviteCount}</div>
              </div>
              <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
                <div className="text-sm text-slate-500">Seat usage</div>
                <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{seatInfo ? `${seatInfo.used}${seatInfo.unlimited ? '' : ` / ${seatInfo.max}`}` : '—'}</div>
              </div>
              <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 shadow-sm">
                <div className="text-sm text-slate-500">Claimed domains</div>
                <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{domainClaims.length}</div>
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
              <div className="space-y-6">
                <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm overflow-hidden">
                  <div className="border-b border-slate-200 dark:border-slate-700 px-6 py-4">
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Members</h2>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="bg-slate-50 dark:bg-slate-900/40">
                          <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">User</th>
                          <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Role</th>
                          <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Status</th>
                          <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                        {membersQuery.isLoading && (
                          <tr><td colSpan={4} className="px-6 py-10 text-center text-sm text-slate-500">Loading members…</td></tr>
                        )}
                        {!membersQuery.isLoading && members.length === 0 && (
                          <tr><td colSpan={4} className="px-6 py-10 text-center text-sm text-slate-500">No members found.</td></tr>
                        )}
                        {members.map((member) => (
                          <tr key={member.id}>
                            <td className="px-6 py-4">
                              <div className="font-medium text-slate-900 dark:text-white">{member.user_name || member.user_email || member.user_id}</div>
                              <div className="text-xs text-slate-500">{member.user_email || member.user_id}</div>
                            </td>
                            <td className="px-6 py-4">
                              <select
                                value={member.role}
                                onChange={(e) => updateRoleMutation.mutate({ userId: member.user_id, role: e.target.value })}
                                disabled={member.role === 'owner' || updateRoleMutation.isPending}
                                className="rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-2 py-1 text-sm text-slate-900 dark:text-white disabled:opacity-60"
                              >
                                <option value="admin">Admin</option>
                                <option value="manager">Manager</option>
                                <option value="member">Member</option>
                                <option value="viewer">Viewer</option>
                              </select>
                            </td>
                            <td className="px-6 py-4">
                              <StatusBadge label={member.status} tone={member.status === 'active' ? 'success' : 'default'} />
                            </td>
                            <td className="px-6 py-4 text-right">
                              {member.role !== 'owner' && (
                                <button
                                  type="button"
                                  onClick={() => removeMemberMutation.mutate(member.user_id)}
                                  disabled={removeMemberMutation.isPending}
                                  className="text-sm font-medium text-red-600 hover:text-red-700 disabled:opacity-50"
                                >
                                  Remove
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm overflow-hidden">
                  <div className="border-b border-slate-200 dark:border-slate-700 px-6 py-4">
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Pending Invitations</h2>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="bg-slate-50 dark:bg-slate-900/40">
                          <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Invitee</th>
                          <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Role</th>
                          <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Expires</th>
                          <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                        {invitationsQuery.isLoading && (
                          <tr><td colSpan={4} className="px-6 py-10 text-center text-sm text-slate-500">Loading invitations…</td></tr>
                        )}
                        {!invitationsQuery.isLoading && invitations.length === 0 && (
                          <tr><td colSpan={4} className="px-6 py-10 text-center text-sm text-slate-500">No pending invites.</td></tr>
                        )}
                        {invitations.map((invite) => (
                          <tr key={invite.id}>
                            <td className="px-6 py-4">
                              <div className="font-medium text-slate-900 dark:text-white">{invite.email}</div>
                              <div className="text-xs text-slate-500">Sent {new Date(invite.created_at).toLocaleString()}</div>
                            </td>
                            <td className="px-6 py-4 text-sm text-slate-700 dark:text-slate-300">{formatRole(invite.role)}</td>
                            <td className="px-6 py-4 text-sm text-slate-700 dark:text-slate-300">{new Date(invite.expires_at).toLocaleString()}</td>
                            <td className="px-6 py-4">
                              <div className="flex justify-end gap-3">
                                <button
                                  type="button"
                                  onClick={() => resendInviteMutation.mutate(invite.id)}
                                  disabled={resendInviteMutation.isPending}
                                  className="text-sm font-medium text-blue-ncs hover:text-delft-blue disabled:opacity-50"
                                >
                                  Resend
                                </button>
                                <button
                                  type="button"
                                  onClick={() => cancelInviteMutation.mutate(invite.id)}
                                  disabled={cancelInviteMutation.isPending}
                                  className="text-sm font-medium text-red-600 hover:text-red-700 disabled:opacity-50"
                                >
                                  Cancel
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm p-6 space-y-4">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Send Invitation</h2>
                    <p className="text-sm text-slate-500 dark:text-slate-400">Invite an admin or regular user into this organization.</p>
                  </div>
                  <div>
                    <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Email</label>
                    <input
                      type="email"
                      value={inviteEmail}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setInviteEmail(e.target.value)}
                      placeholder="name@company.com"
                      className="mt-1 w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Role</label>
                    <select
                      value={inviteRole}
                      onChange={(e: ChangeEvent<HTMLSelectElement>) => setInviteRole(e.target.value)}
                      className="mt-1 w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white"
                    >
                      <option value="admin">Admin</option>
                      <option value="manager">Manager</option>
                      <option value="member">Member</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  </div>
                  <button
                    type="button"
                    onClick={handleSendInvite}
                    disabled={inviteMutation.isPending}
                    className="w-full rounded-lg bg-blue-ncs px-4 py-2 text-sm font-medium text-white hover:bg-delft-blue disabled:opacity-50"
                  >
                    {inviteMutation.isPending ? 'Sending…' : 'Send Invitation'}
                  </button>
                </div>

                <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm overflow-hidden">
                  <div className="border-b border-slate-200 dark:border-slate-700 px-6 py-4">
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Domain Claims</h2>
                  </div>
                  <div className="divide-y divide-slate-200 dark:divide-slate-700">
                    {domainClaimsQuery.isLoading && <div className="px-6 py-8 text-sm text-slate-500">Loading domains…</div>}
                    {!domainClaimsQuery.isLoading && domainClaims.length === 0 && <div className="px-6 py-8 text-sm text-slate-500">No claimed domains yet.</div>}
                    {domainClaims.map((claim) => (
                      <div key={claim.id} className="px-6 py-4">
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <div className="font-medium text-slate-900 dark:text-white">{claim.domain}</div>
                            <div className="text-xs text-slate-500">{claim.verification_email}</div>
                          </div>
                          <div className="flex items-center gap-2">
                            <StatusBadge label={claim.status} tone={claim.status === 'verified' ? 'success' : 'warning'} />
                            {claim.auto_join_enabled && <StatusBadge label="Auto-join" tone="default" />}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm p-6">
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Organization Details</h2>
                  {organizationQuery.isLoading ? (
                    <p className="mt-4 text-sm text-slate-500">Loading organization details…</p>
                  ) : organization ? (
                    <dl className="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
                      <div>
                        <dt className="text-slate-500">Name</dt>
                        <dd className="font-medium text-slate-900 dark:text-white">{organization.name}</dd>
                      </div>
                      <div>
                        <dt className="text-slate-500">Email</dt>
                        <dd className="font-medium text-slate-900 dark:text-white">{organization.email}</dd>
                      </div>
                      <div>
                        <dt className="text-slate-500">Tier</dt>
                        <dd className="font-medium text-slate-900 dark:text-white">{organization.tier}</dd>
                      </div>
                      <div>
                        <dt className="text-slate-500">Subscription</dt>
                        <dd className="font-medium text-slate-900 dark:text-white">{organization.subscription_status}</dd>
                      </div>
                    </dl>
                  ) : (
                    <p className="mt-4 text-sm text-slate-500">Organization details unavailable.</p>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
