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
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import apiClient from '../../lib/api';
import { DashboardLayout } from '../../components/layout/DashboardLayout';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'https://api.encypherai.com/api/v1').replace(/\/$/, '');

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
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'notifications'>('profile');
  const [profile, setProfile] = useState<Profile>({
    name: '',
    email: '',
    company: '',
    phone: '',
    jobTitle: '',
    notifications: defaultNotifications,
  });

  // Email change state
  const [showEmailChange, setShowEmailChange] = useState(false);
  const [newEmail, setNewEmail] = useState('');
  const [emailChangePassword, setEmailChangePassword] = useState('');
  const [pendingEmailChange, setPendingEmailChange] = useState<string | null>(null);

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

  // Pre-populate with session data as fallback, then update with API data
  useEffect(() => {
    if (session?.user) {
      setProfile((prev) => ({
        ...prev,
        name: (session.user as any)?.name || prev.name,
        email: session.user?.email || prev.email,
      }));
    }
  }, [session]);

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

  // Email change request mutation
  const requestEmailChangeMutation = useMutation({
    mutationFn: async ({ newEmail, password }: { newEmail: string; password: string }) => {
      if (!accessToken) throw new Error('You must be signed in.');
      const response = await fetch(`${API_BASE}/auth/request-email-change`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ new_email: newEmail, password }),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to request email change');
      }
      return response.json();
    },
    onSuccess: () => {
      toast.success('Verification email sent to your new address. Please check your inbox.');
      setPendingEmailChange(newEmail);
      setShowEmailChange(false);
      setNewEmail('');
      setEmailChangePassword('');
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Failed to request email change');
    },
  });

  // Cancel pending email change
  const cancelEmailChangeMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      const response = await fetch(`${API_BASE}/auth/cancel-email-change`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to cancel email change');
      }
    },
    onSuccess: () => {
      toast.success('Email change request cancelled');
      setPendingEmailChange(null);
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Failed to cancel email change');
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

  const handleEmailChangeRequest = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail.trim()) {
      toast.error('Please enter a new email address');
      return;
    }
    if (newEmail === profile.email) {
      toast.error('New email must be different from current email');
      return;
    }
    if (!emailChangePassword) {
      toast.error('Please enter your current password');
      return;
    }
    requestEmailChangeMutation.mutate({ newEmail, password: emailChangePassword });
  };

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-delft-blue dark:text-white mb-2">Settings</h2>
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
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <Input type="email" value={profile.email} disabled className="flex-1" />
                              {!showEmailChange && !pendingEmailChange && (
                                <Button
                                  type="button"
                                  variant="outline"
                                  size="sm"
                                  onClick={() => setShowEmailChange(true)}
                                >
                                  Change
                                </Button>
                              )}
                            </div>
                            {pendingEmailChange && (
                              <div className="flex items-center gap-2 p-2 bg-amber-50 border border-amber-200 rounded-lg">
                                <svg className="w-4 h-4 text-amber-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span className="text-sm text-amber-800 flex-1">
                                  Pending change to <strong>{pendingEmailChange}</strong>
                                </span>
                                <Button
                                  type="button"
                                  variant="outline"
                                  size="sm"
                                  onClick={() => cancelEmailChangeMutation.mutate()}
                                  disabled={cancelEmailChangeMutation.isPending}
                                >
                                  Cancel
                                </Button>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Email Change Form */}
                      {showEmailChange && (
                        <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-4">
                          <div className="flex items-center justify-between">
                            <h4 className="font-medium text-sm">Change Email Address</h4>
                            <button
                              type="button"
                              onClick={() => {
                                setShowEmailChange(false);
                                setNewEmail('');
                                setEmailChangePassword('');
                              }}
                              className="text-slate-400 hover:text-slate-600"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            We&apos;ll send a verification link to your new email address. Your email won&apos;t change until you verify it.
                          </p>
                          <div className="grid md:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-sm font-medium mb-1">New Email Address</label>
                              <Input
                                type="email"
                                placeholder="newemail@example.com"
                                value={newEmail}
                                onChange={(e) => setNewEmail(e.target.value)}
                              />
                            </div>
                            <div>
                              <label className="block text-sm font-medium mb-1">Current Password</label>
                              <Input
                                type="password"
                                placeholder="Enter your password"
                                value={emailChangePassword}
                                onChange={(e) => setEmailChangePassword(e.target.value)}
                              />
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              type="button"
                              variant="primary"
                              size="sm"
                              onClick={handleEmailChangeRequest}
                              disabled={requestEmailChangeMutation.isPending}
                            >
                              {requestEmailChangeMutation.isPending ? 'Sending...' : 'Send Verification Email'}
                            </Button>
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                setShowEmailChange(false);
                                setNewEmail('');
                                setEmailChangePassword('');
                              }}
                            >
                              Cancel
                            </Button>
                          </div>
                        </div>
                      )}
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

