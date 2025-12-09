'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { useState } from 'react';
import { toast } from 'sonner';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import apiClient, { PendingAccessRequest } from '../../lib/api';

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
  usageThisMonth: number;
  apiKeys: number;
  lastActive?: string;
  createdAt?: string;
};

const normalizeAdminUsers = (payload: any): AdminUser[] => {
  const rows = payload?.data?.users ?? payload?.data ?? payload?.users ?? payload ?? [];
  return (Array.isArray(rows) ? rows : []).map((row: any, idx: number) => ({
    id: String(row.id ?? row.user_id ?? idx),
    name: row.name ?? row.full_name ?? 'Unknown',
    email: row.email ?? '',
    role: (row.role ?? row.permission ?? 'member').toLowerCase(),
    tier: row.tier ?? row.plan ?? 'free',
    status: row.status ?? row.state ?? (row.disabled ? 'suspended' : 'active'),
    usageThisMonth: row.usage_this_month ?? row.usage ?? 0,
    apiKeys: row.api_keys ?? row.key_count ?? 0,
    lastActive: row.last_active_at ?? row.last_login ?? '',
    createdAt: row.created_at ?? row.joined_at ?? '',
  }));
};

const normalizeAdminStats = (payload: any): AdminStats => ({
  totalUsers: payload?.data?.total_users ?? payload?.total_users ?? payload?.total ?? 0,
  activeUsers: payload?.data?.active_users ?? payload?.active_users ?? 0,
  payingCustomers: payload?.data?.paying_customers ?? payload?.paying_customers ?? 0,
  mrr: payload?.data?.mrr ?? payload?.mrr ?? 0,
  totalApiCalls: payload?.data?.total_api_calls ?? payload?.total_api_calls ?? undefined,
});

export default function AdminPage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const queryClient = useQueryClient();

  const [search, setSearch] = useState('');
  const [denyReason, setDenyReason] = useState('');
  const [denyingUserId, setDenyingUserId] = useState<string | null>(null);

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

  const usersQuery = useQuery({
    queryKey: ['admin-users', search],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      const response = await apiClient.getAdminUsers(accessToken, search);
      return normalizeAdminUsers(response);
    },
    enabled: Boolean(accessToken) && isSuperAdmin,
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

  // Loading states
  if (status === 'loading') {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-ncs"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (superAdminQuery.isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-ncs mx-auto mb-4"></div>
            <p className="text-slate-500 dark:text-slate-400">Checking permissions...</p>
          </div>
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
            You need super admin privileges to access this page. Contact erik.svilich@encypherai.com if you believe this is an error.
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

  const users = usersQuery.data ?? [];
  const stats = statsQuery.data;
  const pendingCount = pendingRequestsQuery.data?.length ?? 0;

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
          <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
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
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full sm:w-80 pl-10 pr-4 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-ncs focus:border-transparent"
                />
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
                  <th className="px-6 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                {usersQuery.isLoading && (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-ncs mx-auto"></div>
                    </td>
                  </tr>
                )}
                {!usersQuery.isLoading && users.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-slate-500 dark:text-slate-400">
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
                      <Badge variant={user.tier === 'enterprise' ? 'success' : 'default'}>
                        {user.tier}
                      </Badge>
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
                      {user.usageThisMonth.toLocaleString()} calls
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={user.status === 'active' ? 'success' : 'error'}>
                        {user.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
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
        </div>
      </div>
    </DashboardLayout>
  );
}

