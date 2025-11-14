'use client';

import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Input,
  Badge,
} from '@encypher/design-system';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { useMemo, useState } from 'react';
import { toast } from 'sonner';
import apiClient from '../../lib/api';

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
  const isAdmin = ((session?.user as any)?.role ?? '').toLowerCase() === 'admin';
  const queryClient = useQueryClient();

  const [search, setSearch] = useState('');

  const statsQuery = useQuery({
    queryKey: ['admin-stats'],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      const response = await apiClient.getAdminStats(accessToken);
      return normalizeAdminStats(response);
    },
    enabled: Boolean(accessToken) && isAdmin,
  });

  const usersQuery = useQuery({
    queryKey: ['admin-users', search],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      const response = await apiClient.getAdminUsers(accessToken, search);
      return normalizeAdminUsers(response);
    },
    enabled: Boolean(accessToken) && isAdmin,
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

  const headerActions = useMemo(
    () => (
      <div className="flex items-center space-x-4">
        <Link href="/">
          <Button variant="ghost" size="sm">
            Dashboard
          </Button>
        </Link>
        <Link href="/api-keys">
          <Button variant="ghost" size="sm">
            API Keys
          </Button>
        </Link>
        <Link href="/analytics">
          <Button variant="ghost" size="sm">
            Analytics
          </Button>
        </Link>
        <Link href="/billing">
          <Button variant="ghost" size="sm">
            Billing
          </Button>
        </Link>
        <Link href="/settings">
          <Button variant="ghost" size="sm">
            Settings
          </Button>
        </Link>
        <div className="w-8 h-8 bg-columbia-blue rounded-full flex items-center justify-center text-white font-semibold">
          {session?.user?.name?.charAt(0)?.toUpperCase() ?? 'A'}
        </div>
      </div>
    ),
    [session?.user?.name],
  );

  if (status === 'loading') {
    return <div className="p-10 text-muted-foreground">Loading session…</div>;
  }

  if (!isAdmin) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-background text-center">
        <h1 className="text-3xl font-bold mb-4">Admin access required</h1>
        <p className="text-muted-foreground">
          You need to be part of the Encypher core team to manage users and permissions. Contact support if you
          believe this is an error.
        </p>
        <Link href="/">
          <Button className="mt-6">Return to dashboard</Button>
        </Link>
      </div>
    );
  }

  const users = usersQuery.data ?? [];
  const stats = statsQuery.data;

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-white sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/">
              <div className="w-8 h-8 bg-gradient-to-br from-delft-blue to-blue-ncs rounded-lg cursor-pointer" />
            </Link>
            <h1 className="text-xl font-bold text-delft-blue">Encypher Admin</h1>
          </div>
          {headerActions}
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-delft-blue mb-2">User management</h2>
          <p className="text-muted-foreground">
            Manage customer accounts, permissions, and enterprise entitlements without leaving the dashboard.
          </p>
        </div>

        <section className="grid md:grid-cols-4 gap-6">
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-1">Total users</p>
              <p className="text-3xl font-bold text-delft-blue">
                {stats?.totalUsers?.toLocaleString() ?? '—'}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-1">Active users</p>
              <p className="text-3xl font-bold text-delft-blue">
                {stats?.activeUsers?.toLocaleString() ?? '—'}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-1">Paying customers</p>
              <p className="text-3xl font-bold text-delft-blue">
                {stats?.payingCustomers?.toLocaleString() ?? '—'}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-1">Monthly recurring revenue</p>
              <p className="text-3xl font-bold text-delft-blue">
                {stats?.mrr ? `$${stats.mrr.toLocaleString()}` : '—'}
              </p>
            </CardContent>
          </Card>
        </section>

        <Card>
          <CardHeader className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <CardTitle>Workspace directory</CardTitle>
              <CardDescription>Search, edit roles, and suspend accounts across the tenant base.</CardDescription>
            </div>
            <Input
              placeholder="Search by name, email, or plan…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="md:w-80"
            />
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground border-b border-border">
                    <th className="py-3 px-4">User</th>
                    <th className="py-3 px-4">Plan</th>
                    <th className="py-3 px-4">Permissions</th>
                    <th className="py-3 px-4">Usage (30d)</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4" />
                  </tr>
                </thead>
                <tbody>
                  {usersQuery.isLoading && (
                    <tr>
                      <td colSpan={6} className="py-6 text-center text-muted-foreground">
                        Loading users…
                      </td>
                    </tr>
                  )}
                  {!usersQuery.isLoading && users.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-6 text-center text-muted-foreground">
                        No users match your filters.
                      </td>
                    </tr>
                  )}
                  {users.map((user) => (
                    <tr key={user.id} className="border-b border-border/60 last:border-0">
                      <td className="py-3 px-4">
                        <div className="font-semibold text-foreground">{user.name}</div>
                        <div className="text-muted-foreground">{user.email}</div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={user.tier === 'enterprise' ? 'default' : 'secondary'}>
                          {user.tier}
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <select
                          className="border border-border rounded-md px-2 py-1 bg-transparent"
                          value={user.role}
                          onChange={(e) =>
                            updateUserMutation.mutate({
                              userId: user.id,
                              updates: { role: e.target.value },
                            })
                          }
                        >
                          <option value="member">Member</option>
                          <option value="manager">Manager</option>
                          <option value="admin">Admin</option>
                        </select>
                      </td>
                      <td className="py-3 px-4">{user.usageThisMonth.toLocaleString()} calls</td>
                      <td className="py-3 px-4 capitalize">{user.status}</td>
                      <td className="py-3 px-4 text-right space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() =>
                            toggleStatusMutation.mutate({
                              userId: user.id,
                              enabled: user.status !== 'active',
                            })
                          }
                        >
                          {user.status === 'active' ? 'Suspend' : 'Activate'}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          asChild
                        >
                          <Link href={`mailto:${user.email}`}>Contact</Link>
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
