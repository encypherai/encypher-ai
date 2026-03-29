'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { useEffect, useState, type ChangeEvent } from 'react';
import { toast } from 'sonner';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import apiClient, {
  PendingAccessRequest,
  ApiAccessStatusType,
  AdminNewsletterSubscriber,
} from '../../lib/api';
import UserActivityModal from '../../components/UserActivityModal';
import { EncypherLoader } from '@encypher/icons';

// Stat card component matching dashboard design
function StatCard({ label, value, icon }: { label: string; value: string | number; icon: React.ReactNode }) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
          <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{value}</p>
        </div>
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-ncs/10 to-delft-blue/10 flex items-center justify-center">
          {icon}
        </div>
      </div>
    </div>
  );
}

// Badge component matching dashboard design
function Badge({ children, variant = 'default' }: { children: React.ReactNode; variant?: 'default' | 'success' | 'warning' | 'error' }) {
  const variants = {
    default: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
    success: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
    warning: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
    error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]}`}>
      {children}
    </span>
  );
}

type AdminStats = {
  totalUsers: number;
  activeUsers: number;
  payingCustomers: number;
  mrr: number;
  totalApiCalls?: number;
};

type AdminUser = {
  id: string;
  name: string;
  email: string;
  role: string;
  tier: string;
  status: 'active' | 'suspended';
  apiAccessStatus: ApiAccessStatusType;
  usageThisMonth: number;
  apiKeys: number;
  lastActive?: string;
  createdAt?: string;
};

type OrganizationOption = {
  id: string;
  name: string;
  email: string;
  tier: string;
  slug?: string | null;
};

const normalizeAdminUsers = (payload: any): { users: AdminUser[]; total: number; page: number; pageSize: number; totalPages: number } => {
  const data = payload?.data ?? payload ?? {};
  const rows = data?.users ?? data ?? [];
  const users = (Array.isArray(rows) ? rows : []).map((row: any, idx: number) => ({
    id: String(row.id ?? row.user_id ?? idx),
    name: row.name ?? row.full_name ?? 'Unknown',
    email: row.email ?? '',
    role: (row.role ?? row.permission ?? 'member').toLowerCase(),
    tier: row.tier ?? row.plan ?? 'free',
    status: row.status ?? row.state ?? (row.disabled ? 'suspended' : 'active'),
    usageThisMonth: row.usage_this_month ?? row.usage ?? 0,
    apiKeys: row.api_keys ?? row.key_count ?? 0,
    apiAccessStatus: row.api_access_status ?? 'not_requested',
    lastActive: row.last_active_at ?? row.last_login ?? '',
    createdAt: row.created_at ?? row.joined_at ?? '',
  }));
  const total = data?.total ?? payload?.total ?? users.length;
  const page = data?.page ?? payload?.page ?? 1;
  const pageSize = (data?.page_size ?? payload?.page_size ?? users.length) || 10;
  const totalPages = data?.total_pages ?? payload?.total_pages ?? (pageSize ? Math.ceil(total / pageSize) : 1);
  return { users, total, page, pageSize, totalPages };
};

const normalizeAdminStats = (payload: any): AdminStats => ({
  totalUsers: payload?.data?.total_users ?? payload?.total_users ?? payload?.total ?? 0,
  activeUsers: payload?.data?.active_users ?? payload?.active_users ?? 0,
  payingCustomers: payload?.data?.paying_customers ?? payload?.paying_customers ?? 0,
  mrr: payload?.data?.mrr ?? payload?.mrr ?? 0,
  totalApiCalls: payload?.data?.total_api_calls ?? payload?.total_api_calls ?? undefined,
});

const getNewsletterStatusVariant = (status: AdminNewsletterSubscriber['status']) => {
  if (status === 'active') return 'success';
  if (status === 'invalid') return 'error';
  return 'default';
};

const getNewsletterStatusLabel = (status: AdminNewsletterSubscriber['status']) => {
  if (status === 'active') return 'Active';
  if (status === 'invalid') return 'Invalid';
  return 'Unsubscribed';
};

export default function AdminPage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const queryClient = useQueryClient();

  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [customPageSize, setCustomPageSize] = useState('');
  const [denyReason, setDenyReason] = useState('');
  const [denyingUserId, setDenyingUserId] = useState<string | null>(null);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [inviteOrgId, setInviteOrgId] = useState('');
  const [orgSearch, setOrgSearch] = useState('');
  const [selectedOrg, setSelectedOrg] = useState<OrganizationOption | null>(null);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteFirstName, setInviteFirstName] = useState('');
  const [inviteLastName, setInviteLastName] = useState('');
  const [inviteOrgName, setInviteOrgName] = useState('');
  const [inviteRole, setInviteRole] = useState('member');
  const [inviteTier, setInviteTier] = useState('');
  const [inviteTrialMonths, setInviteTrialMonths] = useState('');
  const [adminView, setAdminView] = useState<'overview' | 'newsletter'>('overview');
  const [newsletterPage, setNewsletterPage] = useState(1);
  const [newsletterPageSize, setNewsletterPageSize] = useState(25);
  const [newsletterActiveOnly, setNewsletterActiveOnly] = useState(false);

  // TEAM_006: Check if user is super admin via API
  const superAdminQuery = useQuery({
    queryKey: ['is-super-admin'],
    queryFn: async () => {
      if (!accessToken) return false;
      return apiClient.isSuperAdmin(accessToken);
    },
    enabled: Boolean(accessToken),
  });

  const isSuperAdmin = superAdminQuery.data === true;

  const statsQuery = useQuery({
    queryKey: ['admin-stats'],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      const response = await apiClient.getAdminStats(accessToken);
      return normalizeAdminStats(response);
    },
    enabled: Boolean(accessToken) && isSuperAdmin,
  });

  const updateNewsletterSubscriberMutation = useMutation({
    mutationFn: async ({ subscriberId, status, reason }: { subscriberId: number; status: AdminNewsletterSubscriber['status']; reason?: string }) => {
      if (!accessToken) throw new Error('You must be signed in.');
      return apiClient.updateAdminNewsletterSubscriberStatus(accessToken, subscriberId, status, reason);
    },
    onSuccess: (_, variables) => {
      const message = variables.status === 'invalid'
        ? 'Subscriber marked invalid.'
        : variables.status === 'active'
          ? 'Subscriber reactivated.'
          : 'Subscriber updated.';
      toast.success(message);
      queryClient.invalidateQueries({ queryKey: ['admin-newsletter-subscribers'] });
    },
    onError: (err: any) => toast.error(err?.message || 'Failed to update newsletter subscriber.'),
  });

  const deleteNewsletterSubscriberMutation = useMutation({
    mutationFn: async (subscriberId: number) => {
      if (!accessToken) throw new Error('You must be signed in.');
      await apiClient.deleteAdminNewsletterSubscriber(accessToken, subscriberId);
    },
    onSuccess: () => {
      toast.success('Subscriber deleted.');
      queryClient.invalidateQueries({ queryKey: ['admin-newsletter-subscribers'] });
    },
    onError: (err: any) => toast.error(err?.message || 'Failed to delete subscriber.'),
  });

  const newsletterQuery = useQuery({
    queryKey: ['admin-newsletter-subscribers', newsletterPage, newsletterPageSize, newsletterActiveOnly],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      return apiClient.getAdminNewsletterSubscribers(accessToken, {
        page: newsletterPage,
        pageSize: newsletterPageSize,
        activeOnly: newsletterActiveOnly,
      });
    },
    enabled: Boolean(accessToken) && isSuperAdmin,
  });

  const orgSearchQuery = useQuery<OrganizationOption[]>({
    queryKey: ['admin-org-search', orgSearch],
    queryFn: async () => {
      if (!accessToken) return [];
      return await apiClient.searchAdminOrganizations(accessToken, orgSearch.trim(), 10) as OrganizationOption[];
    },
    enabled: Boolean(accessToken) && isSuperAdmin && orgSearch.trim().length >= 2 && !selectedOrg,
  });

  const usersQuery = useQuery({
    queryKey: ['admin-users', search, page, pageSize],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      const response = await apiClient.getAdminUsers(accessToken, search, undefined, page, pageSize);
      return normalizeAdminUsers(response);
    },
    enabled: Boolean(accessToken) && isSuperAdmin,
  });

  const usageCountsQuery = useQuery({
    queryKey: ['admin-usage-counts', usersQuery.data],
    queryFn: async () => {
      if (!accessToken || !usersQuery.data?.users) return {};
      const userIds = usersQuery.data.users.map((user: AdminUser) => user.id);
      return apiClient.getAdminUsageCounts(accessToken, userIds, 30);
    },
    enabled: Boolean(accessToken) && isSuperAdmin && Boolean(usersQuery.data),
  });

  const inviteMutation = useMutation({
    mutationFn: async (
      payload:
        | {
            mode: 'existing';
            orgId: string;
            email: string;
            role: string;
            first_name?: string;
            last_name?: string;
            tier?: string;
            trial_months?: number;
          }
        | {
            mode: 'new-org';
            email: string;
            first_name: string;
            last_name: string;
            organization_name: string;
            tier: string;
            trial_months: number;
          }
    ) => {
      if (!accessToken) throw new Error('You must be signed in.');
      const endpoint =
        payload.mode === 'existing'
          ? `${process.env.NEXT_PUBLIC_API_URL}/organizations/${payload.orgId}/invitations`
          : `${process.env.NEXT_PUBLIC_API_URL}/organizations/invitations/trial`;
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(payload.mode === 'existing' ? {
          email: payload.email,
          role: payload.role,
          first_name: payload.first_name,
          last_name: payload.last_name,
          tier: payload.tier,
          trial_months: payload.trial_months,
        } : {
          email: payload.email,
          first_name: payload.first_name,
          last_name: payload.last_name,
          organization_name: payload.organization_name,
          tier: payload.tier,
          trial_months: payload.trial_months,
        }),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error((typeof error.detail === 'string' ? error.detail : null) || 'Failed to send invitation');
      }
      return response.json();
    },
    onSuccess: () => {
      setInviteOrgId('');
      setInviteEmail('');
      setInviteFirstName('');
      setInviteLastName('');
      setInviteOrgName('');
      setInviteRole('member');
      setInviteTier('');
      setInviteTrialMonths('');
      setOrgSearch('');
      setSelectedOrg(null);
      toast.success('Invitation sent successfully.');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to send invitation');
    },
  });

  // TEAM_006: Pending API access requests
  const pendingRequestsQuery = useQuery({
    queryKey: ['pending-access-requests'],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      return apiClient.getPendingAccessRequests(accessToken);
    },
    enabled: Boolean(accessToken) && isSuperAdmin,
  });

  const approveAccessMutation = useMutation({
    mutationFn: async (userId: string) => {
      if (!accessToken) throw new Error('You must be signed in.');
      await apiClient.approveApiAccess(accessToken, userId);
    },
    onSuccess: () => {
      toast.success('API access approved!');
      queryClient.invalidateQueries({ queryKey: ['pending-access-requests'] });
    },
    onError: (err: any) => toast.error(err?.message || 'Failed to approve access.'),
  });

  const denyAccessMutation = useMutation({
    mutationFn: async ({ userId, reason }: { userId: string; reason: string }) => {
      if (!accessToken) throw new Error('You must be signed in.');
      await apiClient.denyApiAccess(accessToken, userId, reason);
    },
    onSuccess: () => {
      toast.success('API access denied.');
      setDenyingUserId(null);
      setDenyReason('');
      queryClient.invalidateQueries({ queryKey: ['pending-access-requests'] });
    },
    onError: (err: any) => toast.error(err?.message || 'Failed to deny access.'),
  });

  const updateUserMutation = useMutation({
    mutationFn: async ({ userId, updates }: { userId: string; updates: Record<string, unknown> }) => {
      if (!accessToken) throw new Error('You must be signed in.');
      await apiClient.updateAdminUser(accessToken, userId, updates);
    },
    onSuccess: () => {
      toast.success('User updated.');
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
    onError: (err: any) => toast.error(err?.message || 'Failed to update user.'),
  });

  const updateTierMutation = useMutation({
    mutationFn: async ({ userId, newTier, reason }: { userId: string; newTier: string; reason?: string }) => {
      if (!accessToken) throw new Error('You must be signed in.');
      await apiClient.updateUserTier(accessToken, userId, newTier, reason);
    },
    onSuccess: () => {
      toast.success('User tier updated.');
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      queryClient.invalidateQueries({ queryKey: ['admin-stats'] });
    },
    onError: (err: any) => toast.error(err?.message || 'Failed to update tier.'),
  });

  const toggleStatusMutation = useMutation({
    mutationFn: async ({ userId, enabled }: { userId: string; enabled: boolean }) => {
      if (!accessToken) throw new Error('You must be signed in.');
      await apiClient.toggleUserStatus(accessToken, userId, enabled);
    },
    onSuccess: () => {
      toast.success('User status updated.');
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
    onError: (err: any) => toast.error(err?.message || 'Failed to update user status.'),
  });

  // TEAM_164: Mutation to set a user's API access status
  const setApiAccessStatusMutation = useMutation({
    mutationFn: async ({ userId, newStatus, reason }: { userId: string; newStatus: ApiAccessStatusType; reason?: string }) => {
      if (!accessToken) throw new Error('You must be signed in.');
      await apiClient.setApiAccessStatus(accessToken, userId, newStatus, reason);
    },
    onSuccess: () => {
      toast.success('API access status updated.');
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      queryClient.invalidateQueries({ queryKey: ['pending-access-requests'] });
    },
    onError: (err: any) => toast.error(err?.message || 'Failed to update API access status.'),
  });

  useEffect(() => {
    const totalPages = usersQuery.data?.totalPages ?? 1;
    if (totalPages > 0 && page > totalPages) {
      setPage(totalPages);
    }
  }, [page, usersQuery.data?.totalPages]);

  // Loading states
  if (status === 'loading') {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <EncypherLoader size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  if (superAdminQuery.isLoading) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-3">
          <EncypherLoader size="lg" />
          <p className="text-sm text-muted-foreground">Checking permissions...</p>
        </div>
      </DashboardLayout>
    );
  }

  if (!isSuperAdmin) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center min-h-[400px] text-center px-4">
          <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mb-6">
            <svg className="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Admin Access Required</h1>
          <p className="text-slate-500 dark:text-slate-400 max-w-md mb-6">
            You need super admin privileges to access this page. Contact erik.svilich@encypher.com if you believe this is an error.
          </p>
          <Link
            href="/"
            className="inline-flex items-center px-4 py-2 bg-blue-ncs text-white rounded-lg hover:bg-delft-blue transition-colors font-medium"
          >
            Return to Dashboard
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  const users = usersQuery.data?.users ?? [];
  const totalUsers = usersQuery.data?.total ?? 0;
  const totalPages = usersQuery.data?.totalPages ?? 1;
  const stats = statsQuery.data;
  const pendingCount = pendingRequestsQuery.data?.length ?? 0;
  const realUsageCounts = usageCountsQuery.data ?? {};
  const newsletterData = newsletterQuery.data;
  const newsletterRows = newsletterData?.subscribers ?? [];

  const handleSendInvite = () => {
    if (!inviteEmail) {
      toast.error('Invitee email is required.');
      return;
    }

    const tierValue = inviteTier ? inviteTier : undefined;
    const trialMonthsValue = inviteTrialMonths ? Number(inviteTrialMonths) : undefined;

    if (tierValue || inviteTrialMonths) {
      if (!tierValue || !inviteTrialMonths) {
        toast.error('Select both a tier and trial months for trial invitations.');
        return;
      }
      if (Number.isNaN(trialMonthsValue) || trialMonthsValue! < 1 || trialMonthsValue! > 24) {
        toast.error('Trial months must be between 1 and 24.');
        return;
      }
      if (!inviteFirstName.trim() || !inviteLastName.trim()) {
        toast.error('First and last name are required for trial invitations.');
        return;
      }
    }

    if (!inviteOrgId && !(tierValue && inviteTrialMonths)) {
      toast.error('Select an organization for standard invitations.');
      return;
    }

    if (!inviteOrgId && tierValue && inviteTrialMonths) {
      if (!inviteOrgName.trim()) {
        toast.error('Organization name is required to create a trial for a new org.');
        return;
      }
      inviteMutation.mutate({
        mode: 'new-org',
        email: inviteEmail,
        first_name: inviteFirstName.trim(),
        last_name: inviteLastName.trim(),
        organization_name: inviteOrgName.trim(),
        tier: tierValue,
        trial_months: trialMonthsValue!,
      });
      return;
    }

    inviteMutation.mutate({
      mode: 'existing',
      orgId: inviteOrgId,
      email: inviteEmail,
      role: inviteRole,
      first_name: inviteFirstName.trim() || undefined,
      last_name: inviteLastName.trim() || undefined,
      tier: tierValue,
      trial_months: trialMonthsValue,
    });
  };

  const handleOrgSearchChange = (value: string) => {
    setOrgSearch(value);
    setInviteOrgId('');
    setSelectedOrg(null);
  };

  const handleOrgSelect = (org: OrganizationOption) => {
    setSelectedOrg(org);
    setInviteOrgId(org.id);
    setOrgSearch(`${org.name} (${org.id})`);
  };

  const handlePageSizeChange = (value: number) => {
    setPageSize(value);
    setPage(1);
    setCustomPageSize('');
  };

  const handleApplyCustomPageSize = () => {
    const parsed = Number(customPageSize);
    if (!parsed || parsed < 1 || parsed > 500) {
      toast.error('Custom page size must be between 1 and 500.');
      return;
    }
    handlePageSizeChange(parsed);
  };

  const handleShowAll = () => {
    if (totalUsers > 0) {
      handlePageSizeChange(totalUsers);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Admin Dashboard</h1>
              <Badge variant="warning">Super Admin</Badge>
            </div>
            <p className="text-slate-500 dark:text-slate-400">
              Manage users, review API access requests, and monitor platform health.
            </p>
          </div>
        </div>

        <div className="inline-flex rounded-lg border border-slate-200 dark:border-slate-700 p-1 bg-white dark:bg-slate-800 w-fit">
          <button
            onClick={() => setAdminView('overview')}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              adminView === 'overview'
                ? 'bg-blue-ncs text-white'
                : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setAdminView('newsletter')}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              adminView === 'newsletter'
                ? 'bg-blue-ncs text-white'
                : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
            }`}
          >
            Newsletter
          </button>
          <Link
            href="/admin/organizations"
            className="px-3 py-1.5 text-sm rounded-md transition-colors text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
          >
            Organizations
          </Link>
        </div>

        {adminView === 'overview' && (
          <>
        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Total Users"
            value={stats?.totalUsers?.toLocaleString() ?? '—'}
            icon={
              <svg className="w-6 h-6 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            }
          />
          <StatCard
            label="Active Users"
            value={stats?.activeUsers?.toLocaleString() ?? '—'}
            icon={
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          />
          <StatCard
            label="Paying Customers"
            value={stats?.payingCustomers?.toLocaleString() ?? '—'}
            icon={
              <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
            }
          />
          <StatCard
            label="Monthly Revenue"
            value={stats?.mrr ? `$${stats.mrr.toLocaleString()}` : '—'}
            icon={
              <svg className="w-6 h-6 text-delft-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          />
        </div>

        {/* Trial Invitations */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Trial Invitations</h2>
                <p className="text-sm text-slate-500 dark:text-slate-400">Send tiered trial invites on behalf of an organization</p>
              </div>
              <Badge variant="warning">Super Admin</Badge>
            </div>
          </div>
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Organization Lookup</label>
                <div className="relative mt-1">
                  <input
                    type="text"
                    placeholder="Search by org name, slug, or ID"
                    value={orgSearch}
                    onChange={(e) => handleOrgSearchChange(e.target.value)}
                    data-testid="invite-org-search"
                    className="w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
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
                    <div className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 border-2 border-blue-ncs border-t-transparent rounded-full animate-spin" />
                  )}
                  {orgSearchQuery.data && orgSearchQuery.data.length > 0 && !selectedOrg && (
                    <div className="absolute z-10 mt-2 w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-lg">
                      {orgSearchQuery.data.map((org: OrganizationOption) => (
                        <button
                          key={org.id}
                          type="button"
                          onClick={() => handleOrgSelect(org)}
                          data-testid={`invite-org-option-${org.id}`}
                          className="w-full px-3 py-2 text-left text-sm hover:bg-slate-50 dark:hover:bg-slate-800"
                        >
                          <div className="font-medium text-slate-900 dark:text-white">{org.name}</div>
                          <div className="text-xs text-slate-500">{org.id} • {org.email}</div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {selectedOrg && (
                  <div className="mt-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/40 px-3 py-2 text-xs text-slate-600 dark:text-slate-300">
                    Selected: <span className="font-semibold">{selectedOrg.name}</span> ({selectedOrg.id})
                  </div>
                )}
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Invitee Email</label>
                <input
                  type="email"
                  placeholder="invitee@company.com"
                  value={inviteEmail}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setInviteEmail(e.target.value)}
                  data-testid="invite-email"
                  className="mt-1 w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">First Name</label>
                  <input
                    type="text"
                    placeholder="Jane"
                    value={inviteFirstName}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => setInviteFirstName(e.target.value)}
                    data-testid="invite-first-name"
                    className="mt-1 w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Last Name</label>
                  <input
                    type="text"
                    placeholder="Doe"
                    value={inviteLastName}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => setInviteLastName(e.target.value)}
                    data-testid="invite-last-name"
                    className="mt-1 w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Role</label>
                <select
                  value={inviteRole}
                  onChange={(e: ChangeEvent<HTMLSelectElement>) => setInviteRole(e.target.value)}
                  data-testid="invite-role"
                  disabled={!selectedOrg}
                  className="mt-1 w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white disabled:opacity-60"
                >
                  <option value="admin">Admin</option>
                  <option value="manager">Manager</option>
                  <option value="member">Member</option>
                  <option value="viewer">Viewer</option>
                </select>
                {!selectedOrg && (
                  <p className="mt-1 text-[11px] text-slate-400">New org trials set the invitee as owner.</p>
                )}
              </div>
            </div>
            {!selectedOrg && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">New Organization Name</label>
                  <input
                    type="text"
                    placeholder="Acme Labs"
                    value={inviteOrgName}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => setInviteOrgName(e.target.value)}
                    data-testid="invite-org-name"
                    className="mt-1 w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                  />
                </div>
              </div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Trial Tier</label>
                <select
                  value={inviteTier}
                  onChange={(e: ChangeEvent<HTMLSelectElement>) => setInviteTier(e.target.value)}
                  data-testid="invite-tier"
                  className="mt-1 w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                >
                  <option value="">Select tier</option>
                  <option value="business">Business</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Trial Months</label>
                <input
                  type="number"
                  min={1}
                  max={24}
                  placeholder="e.g. 2"
                  value={inviteTrialMonths}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setInviteTrialMonths(e.target.value)}
                  data-testid="invite-trial-months"
                  className="mt-1 w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                />
              </div>
              <div className="flex items-end">
                <button
                  onClick={handleSendInvite}
                  disabled={inviteMutation.isPending}
                  data-testid="invite-submit"
                  className="w-full px-4 py-2 text-sm font-medium text-white bg-blue-ncs rounded-lg hover:bg-delft-blue transition-colors disabled:opacity-50"
                >
                  {inviteMutation.isPending ? 'Sending...' : 'Send Trial Invite'}
                </button>
              </div>
            </div>
            <p className="text-xs text-slate-500">
              Include both a tier and trial months to issue a trial. Leave blank to send a standard invite.
            </p>
          </div>
        </div>

        {/* Pending API Access Requests */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                  <svg className="w-5 h-5 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Pending API Access Requests</h2>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Review and approve users requesting API access</p>
                </div>
              </div>
              {pendingCount > 0 && (
                <Badge variant="error">{pendingCount} pending</Badge>
              )}
            </div>
          </div>
          <div className="p-6">
            {pendingRequestsQuery.isLoading && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-ncs"></div>
              </div>
            )}
            {!pendingRequestsQuery.isLoading && pendingCount === 0 && (
              <div className="text-center py-8">
                <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mx-auto mb-3">
                  <svg className="w-6 h-6 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p className="text-slate-500 dark:text-slate-400">No pending requests. All caught up!</p>
              </div>
            )}
            <div className="space-y-4">
              {(pendingRequestsQuery.data ?? []).map((request: PendingAccessRequest) => (
                <div key={request.user_id} className="bg-slate-50 dark:bg-slate-900/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                  <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-ncs to-delft-blue flex items-center justify-center text-white font-semibold text-sm">
                          {(request.name || request.email).charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p className="font-semibold text-slate-900 dark:text-white">{request.name || 'Unknown'}</p>
                          <p className="text-sm text-slate-500 dark:text-slate-400">{request.email}</p>
                        </div>
                      </div>
                      <p className="text-xs text-slate-400 dark:text-slate-500 mb-3">
                        Requested {new Date(request.requested_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                          hour: 'numeric',
                          minute: '2-digit',
                        })}
                      </p>
                      <div className="bg-white dark:bg-slate-800 rounded-lg p-3 border border-slate-200 dark:border-slate-700">
                        <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Use Case</p>
                        <p className="text-sm text-slate-700 dark:text-slate-300">{request.use_case}</p>
                      </div>
                    </div>
                    <div className="flex flex-col gap-2 lg:items-end shrink-0">
                      {denyingUserId === request.user_id ? (
                        <div className="flex flex-col gap-2">
                          <input
                            type="text"
                            placeholder="Reason for denial..."
                            value={denyReason}
                            onChange={(e) => setDenyReason(e.target.value)}
                            className="w-64 px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-ncs focus:border-transparent"
                          />
                          <div className="flex gap-2">
                            <button
                              onClick={() => {
                                setDenyingUserId(null);
                                setDenyReason('');
                              }}
                              className="px-3 py-1.5 text-sm font-medium text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={() => denyAccessMutation.mutate({ userId: request.user_id, reason: denyReason })}
                              disabled={!denyReason.trim() || denyAccessMutation.isPending}
                              className="px-3 py-1.5 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              Confirm Deny
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex gap-2">
                          <button
                            onClick={() => setDenyingUserId(request.user_id)}
                            disabled={approveAccessMutation.isPending}
                            className="px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors disabled:opacity-50"
                          >
                            Deny
                          </button>
                          <button
                            onClick={() => approveAccessMutation.mutate(request.user_id)}
                            disabled={approveAccessMutation.isPending}
                            className="px-4 py-2 text-sm font-medium text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50"
                          >
                            {approveAccessMutation.isPending ? 'Approving...' : 'Approve'}
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* User Directory */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">User Directory</h2>
                <p className="text-sm text-slate-500 dark:text-slate-400">Search, edit roles, and manage accounts</p>
              </div>
              <div className="relative">
                <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                  type="text"
                  placeholder="Search by name, email, or plan..."
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                    setPage(1);
                  }}
                  className="w-full sm:w-80 pl-10 pr-4 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-ncs focus:border-transparent"
                />
              </div>
            </div>
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
              <p className="text-xs text-slate-500">
                Showing {users.length} of {totalUsers} users
              </p>
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs text-slate-500">Rows per page</span>
                <select
                  value={pageSize}
                  onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                  className="px-2 py-1 text-xs border border-slate-300 dark:border-slate-600 rounded-md bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                >
                  {[10, 25, 50, 100].map((size) => (
                    <option key={size} value={size}>{size}</option>
                  ))}
                </select>
                <button
                  onClick={handleShowAll}
                  disabled={totalUsers === 0}
                  className="px-2 py-1 text-xs font-medium text-blue-ncs border border-blue-ncs rounded-md hover:bg-blue-ncs/10 disabled:opacity-50"
                >
                  Show all
                </button>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    min={1}
                    max={500}
                    placeholder="Custom"
                    value={customPageSize}
                    onChange={(e) => setCustomPageSize(e.target.value)}
                    className="w-24 px-2 py-1 text-xs border border-slate-300 dark:border-slate-600 rounded-md bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                  />
                  <button
                    onClick={handleApplyCustomPageSize}
                    className="px-2 py-1 text-xs font-medium text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-600 rounded-md hover:bg-slate-50 dark:hover:bg-slate-700"
                  >
                    Apply
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-900/50">
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">User</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Plan</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Role</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Usage (30d)</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">API Access</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                {usersQuery.isLoading && (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-ncs mx-auto"></div>
                    </td>
                  </tr>
                )}
                {!usersQuery.isLoading && users.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-slate-500 dark:text-slate-400">
                      No users match your filters.
                    </td>
                  </tr>
                )}
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-50 dark:hover:bg-slate-900/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-ncs to-delft-blue flex items-center justify-center text-white text-xs font-semibold">
                          {user.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p className="font-medium text-slate-900 dark:text-white">{user.name}</p>
                          <p className="text-sm text-slate-500 dark:text-slate-400">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <select
                        value={user.tier}
                        onChange={(e) => updateTierMutation.mutate({ userId: user.id, newTier: e.target.value })}
                        className="text-sm border border-slate-300 dark:border-slate-600 rounded-md px-2 py-1 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-ncs"
                      >
                        <option value="starter">Starter</option>
                        <option value="professional">Professional</option>
                        <option value="business">Business</option>
                        <option value="enterprise">Enterprise</option>
                        <option value="strategic_partner">Strategic Partner</option>
                      </select>
                    </td>
                    <td className="px-6 py-4">
                      <select
                        value={user.role}
                        onChange={(e) => updateUserMutation.mutate({ userId: user.id, updates: { role: e.target.value } })}
                        className="text-sm border border-slate-300 dark:border-slate-600 rounded-md px-2 py-1 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-ncs"
                      >
                        <option value="member">Member</option>
                        <option value="manager">Manager</option>
                        <option value="admin">Admin</option>
                      </select>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-700 dark:text-slate-300">
                      {(realUsageCounts[user.id] ?? user.usageThisMonth ?? 0).toLocaleString()} calls
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={user.status === 'active' ? 'success' : 'error'}>
                        {user.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      <select
                        value={user.apiAccessStatus}
                        onChange={(e) => {
                          const newStatus = e.target.value as ApiAccessStatusType;
                          if (newStatus === 'suspended') {
                            const reason = window.prompt('Reason for suspending API access (optional):');
                            setApiAccessStatusMutation.mutate({ userId: user.id, newStatus, reason: reason || undefined });
                          } else {
                            setApiAccessStatusMutation.mutate({ userId: user.id, newStatus });
                          }
                        }}
                        data-testid={`api-access-status-${user.id}`}
                        className={`text-sm border rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-ncs ${
                          user.apiAccessStatus === 'approved'
                            ? 'border-emerald-300 dark:border-emerald-700 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400'
                            : user.apiAccessStatus === 'suspended'
                            ? 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400'
                            : user.apiAccessStatus === 'denied'
                            ? 'border-amber-300 dark:border-amber-700 bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400'
                            : user.apiAccessStatus === 'pending'
                            ? 'border-blue-300 dark:border-blue-700 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400'
                            : 'border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300'
                        }`}
                      >
                        <option value="not_requested">Not Requested</option>
                        <option value="pending">Pending</option>
                        <option value="approved">Approved</option>
                        <option value="denied">Denied</option>
                        <option value="suspended">Suspended</option>
                      </select>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setSelectedUserId(user.id)}
                          className="px-3 py-1.5 text-xs font-medium text-blue-ncs hover:text-delft-blue transition-colors"
                        >
                          View Logs
                        </button>
                        <button
                          onClick={() => toggleStatusMutation.mutate({ userId: user.id, enabled: user.status !== 'active' })}
                          className="px-3 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-md hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                        >
                          {user.status === 'active' ? 'Suspend' : 'Activate'}
                        </button>
                        <a
                          href={`mailto:${user.email}`}
                          className="px-3 py-1.5 text-xs font-medium text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
                        >
                          Contact
                        </a>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <p className="text-xs text-slate-500">
              Page {page} of {totalPages}
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page <= 1}
                className="px-3 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-600 rounded-md hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page >= totalPages}
                className="px-3 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-600 rounded-md hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </div>
          </>
        )}

        {adminView === 'newsletter' && (
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                <div>
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Newsletter Subscribers</h2>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Blog newsletter opt-ins from the marketing site.</p>
                </div>
                <div className="flex items-center gap-3">
                  <label className="inline-flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
                    <input
                      type="checkbox"
                      checked={newsletterActiveOnly}
                      onChange={(e) => {
                        setNewsletterActiveOnly(e.target.checked);
                        setNewsletterPage(1);
                      }}
                      className="rounded border-slate-300 text-blue-ncs focus:ring-blue-ncs"
                    />
                    Active only
                  </label>
                  <select
                    value={newsletterPageSize}
                    onChange={(e) => {
                      setNewsletterPageSize(Number(e.target.value));
                      setNewsletterPage(1);
                    }}
                    className="px-2 py-1 text-xs border border-slate-300 dark:border-slate-600 rounded-md bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                  >
                    {[25, 50, 100].map((size) => (
                      <option key={size} value={size}>{size} / page</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-900/50">
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Source</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Subscribed At</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                  {newsletterQuery.isLoading && (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-ncs mx-auto"></div>
                      </td>
                    </tr>
                  )}
                  {!newsletterQuery.isLoading && newsletterRows.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center text-slate-500 dark:text-slate-400">
                        No newsletter subscribers found.
                      </td>
                    </tr>
                  )}
                  {newsletterRows.map((subscriber: AdminNewsletterSubscriber) => (
                    <tr key={subscriber.id} className="hover:bg-slate-50 dark:hover:bg-slate-900/30 transition-colors">
                      <td className="px-6 py-4 text-sm text-slate-900 dark:text-white">{subscriber.email}</td>
                      <td className="px-6 py-4">
                        <div className="space-y-1">
                          <Badge variant={getNewsletterStatusVariant(subscriber.status)}>
                            {getNewsletterStatusLabel(subscriber.status)}
                          </Badge>
                          {subscriber.status_reason && (
                            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs break-words">{subscriber.status_reason}</p>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-700 dark:text-slate-300">{subscriber.source || '—'}</td>
                      <td className="px-6 py-4 text-sm text-slate-700 dark:text-slate-300">
                        {subscriber.subscribed_at
                          ? new Date(subscriber.subscribed_at).toLocaleString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })
                          : '—'}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-2">
                          {subscriber.status !== 'invalid' && (
                            <button
                              onClick={() => {
                                const reason = window.prompt('Optional reason for marking this subscriber invalid:', subscriber.status_reason || '');
                                if (reason === null) return;
                                updateNewsletterSubscriberMutation.mutate({
                                  subscriberId: subscriber.id,
                                  status: 'invalid',
                                  reason: reason.trim() || undefined,
                                });
                              }}
                              disabled={updateNewsletterSubscriberMutation.isPending || deleteNewsletterSubscriberMutation.isPending}
                              className="px-3 py-1.5 text-xs font-medium text-amber-700 dark:text-amber-300 border border-amber-300 dark:border-amber-700 rounded-md hover:bg-amber-50 dark:hover:bg-amber-900/20 disabled:opacity-50"
                            >
                              Mark invalid
                            </button>
                          )}
                          {subscriber.status !== 'active' && (
                            <button
                              onClick={() => {
                                updateNewsletterSubscriberMutation.mutate({
                                  subscriberId: subscriber.id,
                                  status: 'active',
                                });
                              }}
                              disabled={updateNewsletterSubscriberMutation.isPending || deleteNewsletterSubscriberMutation.isPending}
                              className="px-3 py-1.5 text-xs font-medium text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700 rounded-md hover:bg-emerald-50 dark:hover:bg-emerald-900/20 disabled:opacity-50"
                            >
                              Reactivate
                            </button>
                          )}
                          <button
                            onClick={() => {
                              if (!window.confirm(`Delete newsletter subscriber ${subscriber.email}? This cannot be undone.`)) return;
                              deleteNewsletterSubscriberMutation.mutate(subscriber.id);
                            }}
                            disabled={updateNewsletterSubscriberMutation.isPending || deleteNewsletterSubscriberMutation.isPending}
                            className="px-3 py-1.5 text-xs font-medium text-red-700 dark:text-red-300 border border-red-300 dark:border-red-700 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20 disabled:opacity-50"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <p className="text-xs text-slate-500">
                Showing {newsletterRows.length} of {newsletterData?.total ?? 0} subscribers
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setNewsletterPage(Math.max(1, newsletterPage - 1))}
                  disabled={newsletterPage <= 1}
                  className="px-3 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-600 rounded-md hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50"
                >
                  Previous
                </button>
                <span className="text-xs text-slate-500">
                  Page {newsletterPage} of {Math.max(newsletterData?.total_pages ?? 1, 1)}
                </span>
                <button
                  onClick={() => setNewsletterPage(newsletterPage + 1)}
                  disabled={newsletterPage >= (newsletterData?.total_pages ?? 1)}
                  className="px-3 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-600 rounded-md hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* User Activity Modal */}
      {selectedUserId && (
        <UserActivityModal
          userId={selectedUserId}
          userEmail={users.find((u) => u.id === selectedUserId)?.email || ''}
          accessToken={accessToken || ''}
          isOpen={Boolean(selectedUserId)}
          onClose={() => setSelectedUserId(null)}
        />
      )}
    </DashboardLayout>
  );
}
