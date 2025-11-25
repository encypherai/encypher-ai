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
import { useMutation, useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import apiClient from '../../lib/api';
import { DashboardLayout } from '../../components/layout/DashboardLayout';

type Profile = {
  name: string;
  email: string;
  company?: string;
  phone?: string;
  jobTitle?: string;
  notifications?: {
    emailAlerts: boolean;
    usageAlerts: boolean;
    securityAlerts: boolean;
    marketingEmails: boolean;
  };
};

const defaultNotifications = {
  emailAlerts: true,
  usageAlerts: true,
  securityAlerts: true,
  marketingEmails: true,  // Default to true - users can opt-out
};

const normalizeProfile = (raw: any): Profile => ({
  name: raw?.name ?? '',
  email: raw?.email ?? '',
  company: raw?.company ?? raw?.organization ?? '',
  phone: raw?.phone ?? '',
  jobTitle: raw?.job_title ?? raw?.role ?? '',
  notifications: {
    emailAlerts: raw?.notifications?.emailAlerts ?? raw?.notifications?.email_alerts ?? true,
    usageAlerts: raw?.notifications?.usageAlerts ?? raw?.notifications?.usage_alerts ?? true,
    securityAlerts:
      raw?.notifications?.securityAlerts ?? raw?.notifications?.security_alerts ?? true,
    marketingEmails:
      raw?.notifications?.marketingEmails ?? raw?.notifications?.marketing_emails ?? false,
  },
});

export default function SettingsPage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'notifications'>('profile');
  const [profile, setProfile] = useState<Profile>({
    name: '',
    email: '',
    company: '',
    phone: '',
    jobTitle: '',
    notifications: defaultNotifications,
  });

  const profileQuery = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in to manage settings.');
      const response = await apiClient.getProfile(accessToken) as any;
      return normalizeProfile(response?.data ?? response);
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
  });

  useEffect(() => {
    if (profileQuery.data) {
      setProfile(profileQuery.data);
    }
  }, [profileQuery.data]);

  const updateProfileMutation = useMutation({
    mutationFn: async (changes: Profile) => {
      if (!accessToken) throw new Error('You must be signed in to update your profile.');
      await apiClient.updateProfile(accessToken, {
        name: changes.name,
        company: changes.company,
        phone: changes.phone,
        job_title: changes.jobTitle,
        notifications: changes.notifications,
      });
    },
    onSuccess: () => {
      toast.success('Profile updated.');
      profileQuery.refetch();
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to update profile.');
    },
  });

  const isLoading = status === 'loading' || profileQuery.isLoading;

  const handleProfileSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfileMutation.mutate(profile);
  };

  const handleNotificationsSave = () => {
    updateProfileMutation.mutate(profile);
  };

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-delft-blue mb-2">Settings</h2>
        <p className="text-muted-foreground">Manage your account settings and preferences</p>
      </div>

      <div className="grid md:grid-cols-4 gap-6">
          <div className="md:col-span-1">
            <Card>
              <CardContent className="p-4">
                <nav className="space-y-1">
                  {['profile', 'security', 'notifications'].map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab as typeof activeTab)}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        activeTab === tab ? 'bg-columbia-blue text-white' : 'text-muted-foreground hover:bg-muted'
                      }`}
                    >
                      {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                  ))}
                </nav>
              </CardContent>
            </Card>
          </div>

          <div className="md:col-span-3 space-y-6">
            {activeTab === 'profile' && (
              <Card>
                <CardHeader>
                  <CardTitle>Profile Information</CardTitle>
                  <CardDescription>Update your personal information</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="text-muted-foreground">Loading profile…</div>
                  ) : (
                    <form className="space-y-4" onSubmit={handleProfileSave}>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">Full Name</label>
                          <Input
                            value={profile.name}
                            onChange={(e) => setProfile((prev) => ({ ...prev, name: e.target.value }))}
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">Email</label>
                          <Input type="email" value={profile.email} disabled />
                        </div>
                      </div>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">Company</label>
                          <Input
                            value={profile.company ?? ''}
                            onChange={(e) => setProfile((prev) => ({ ...prev, company: e.target.value }))}
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">Phone</label>
                          <Input
                            value={profile.phone ?? ''}
                            onChange={(e) => setProfile((prev) => ({ ...prev, phone: e.target.value }))}
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Job Title</label>
                        <Input
                          value={profile.jobTitle ?? ''}
                          onChange={(e) => setProfile((prev) => ({ ...prev, jobTitle: e.target.value }))}
                        />
                      </div>
                      <Button type="submit" variant="primary" disabled={updateProfileMutation.isPending}>
                        {updateProfileMutation.isPending ? 'Saving…' : 'Save changes'}
                      </Button>
                    </form>
                  )}
                </CardContent>
              </Card>
            )}

            {activeTab === 'security' && (
              <Card>
                <CardHeader>
                  <CardTitle>Change password</CardTitle>
                  <CardDescription>Update your password</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Password changes are managed via the Encypher API. Use the “Forgot password” link on the login
                    screen to reset your credentials securely.
                  </p>
                  <div className="mt-4">
                    <Link href="/forgot-password">
                      <Button variant="primary">Reset password</Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            )}

            {activeTab === 'notifications' && (
              <Card>
                <CardHeader>
                  <CardTitle>Notification preferences</CardTitle>
                  <CardDescription>Choose what notifications you want to receive</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="text-muted-foreground">Loading preferences…</div>
                  ) : (
                    <div className="space-y-4">
                      {Object.entries(profile.notifications ?? defaultNotifications).map(([key, value]) => (
                        <div
                          key={key}
                          className="flex items-center justify-between p-4 border border-border rounded-lg"
                        >
                          <div>
                            <div className="font-medium capitalize">{key.replace(/([A-Z])/g, ' $1')}</div>
                            <p className="text-sm text-muted-foreground">
                              {key === 'marketingEmails'
                                ? 'Product updates and marketing insights'
                                : 'Critical account and usage alerts'}
                            </p>
                          </div>
                          <input
                            type="checkbox"
                            checked={Boolean(value)}
                            onChange={(e) =>
                              setProfile((prev) => ({
                                ...prev,
                                notifications: {
                                  ...(prev.notifications ?? defaultNotifications),
                                  [key]: e.target.checked,
                                },
                              }))
                            }
                          />
                        </div>
                      ))}
                      <Button
                        variant="primary"
                        onClick={handleNotificationsSave}
                        disabled={updateProfileMutation.isPending}
                      >
                        {updateProfileMutation.isPending ? 'Saving…' : 'Save preferences'}
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
    </DashboardLayout>
  );
}
