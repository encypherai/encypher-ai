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
import { useMutation, useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import apiClient from '../../lib/api';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { useOrganization } from '../../contexts/OrganizationContext';

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

type SigningIdentityMode = 'organization_name' | 'organization_and_author' | 'custom';

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
  const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'notifications' | 'organization'>('profile');
  const { activeOrganization, isLoading: orgLoading, refetch: refetchOrganizations } = useOrganization();
  const orgId = activeOrganization?.id;
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
  const [domainName, setDomainName] = useState('');
  const [domainEmail, setDomainEmail] = useState('');
  const [publisherDisplayName, setPublisherDisplayName] = useState('');
  const [signingIdentityMode, setSigningIdentityMode] = useState<SigningIdentityMode>('organization_name');
  const [anonymousPublisher, setAnonymousPublisher] = useState(false);
  const [totpCode, setTotpCode] = useState('');
  const [totpDisableCode, setTotpDisableCode] = useState('');
  const [totpSetupSecret, setTotpSetupSecret] = useState<string | null>(null);
  const [totpSetupUri, setTotpSetupUri] = useState<string | null>(null);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [passkeyName, setPasskeyName] = useState('Primary device');

  const mfaStatusQuery = useQuery({
    queryKey: ['mfa-status'],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      return apiClient.getMfaStatus(accessToken);
    },
    enabled: Boolean(accessToken && activeTab === 'security'),
    refetchOnWindowFocus: false,
  });

  const beginTotpMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      return apiClient.beginTotpSetup(accessToken);
    },
    onSuccess: (result) => {
      setTotpSetupSecret(result.secret);
      setTotpSetupUri(result.provisioning_uri);
      setBackupCodes(result.backup_codes || []);
      toast.success('Authenticator setup initialized. Save your backup codes now.');
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to start TOTP setup.');
    },
  });

  const confirmTotpMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      return apiClient.confirmTotpSetup(accessToken, totpCode);
    },
    onSuccess: () => {
      setTotpCode('');
      setTotpSetupSecret(null);
      setTotpSetupUri(null);
      setBackupCodes([]);
      mfaStatusQuery.refetch();
      toast.success('Two-factor authentication enabled.');
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Invalid authentication code.');
    },
  });

  const disableTotpMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      await apiClient.disableTotp(accessToken, totpDisableCode);
    },
    onSuccess: () => {
      setTotpDisableCode('');
      mfaStatusQuery.refetch();
      toast.success('Two-factor authentication disabled.');
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to disable two-factor authentication.');
    },
  });

  const deletePasskeyMutation = useMutation({
    mutationFn: async (credentialId: string) => {
      if (!accessToken) throw new Error('You must be signed in.');
      await apiClient.deletePasskey(accessToken, credentialId);
    },
    onSuccess: () => {
      mfaStatusQuery.refetch();
      toast.success('Passkey deleted.');
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to delete passkey.');
    },
  });

  const toBase64Url = (buffer: ArrayBuffer): string => {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    bytes.forEach((b) => {
      binary += String.fromCharCode(b);
    });
    return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
  };

  const fromBase64Url = (value: string): Uint8Array => {
    const padded = `${value}${'='.repeat((4 - (value.length % 4)) % 4)}`;
    const base64 = padded.replace(/-/g, '+').replace(/_/g, '/');
    const binary = atob(base64);
    return Uint8Array.from(binary, (char) => char.charCodeAt(0));
  };

  const handleRegisterPasskey = async () => {
    if (!accessToken) {
      toast.error('You must be signed in.');
      return;
    }
    if (typeof window === 'undefined' || !window.PublicKeyCredential) {
      toast.error('Passkeys are not supported in this browser.');
      return;
    }

    try {
      const options = await apiClient.startPasskeyRegistration(accessToken);
      const parsed = JSON.parse(options.options_json);
      const publicKey: PublicKeyCredentialCreationOptions = {
        ...parsed,
        challenge: fromBase64Url(parsed.challenge),
        user: {
          ...parsed.user,
          id: fromBase64Url(parsed.user.id),
        },
        excludeCredentials: (parsed.excludeCredentials || []).map((cred: any) => ({
          ...cred,
          id: fromBase64Url(cred.id),
        })),
      };

      const credential = (await navigator.credentials.create({ publicKey })) as PublicKeyCredential | null;
      if (!credential) throw new Error('Passkey registration was cancelled.');

      const response = credential.response as AuthenticatorAttestationResponse;
      const payload = {
        id: credential.id,
        rawId: toBase64Url(credential.rawId),
        type: credential.type,
        response: {
          clientDataJSON: toBase64Url(response.clientDataJSON),
          attestationObject: toBase64Url(response.attestationObject),
        },
      };

      await apiClient.completePasskeyRegistration(accessToken, payload, passkeyName);
      mfaStatusQuery.refetch();
      toast.success('Passkey registered.');
    } catch (err: any) {
      toast.error(err?.message || 'Passkey registration failed.');
    }
  };

  const updatePublisherSettingsMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken || !orgId) throw new Error('You must be signed in.');

      const customLabel = publisherDisplayName.trim();
      if (signingIdentityMode === 'custom' && !customLabel) {
        throw new Error('Custom signing identity label cannot be empty.');
      }

      return apiClient.updatePublisherSettings(accessToken, orgId, {
        ...(signingIdentityMode === 'custom' ? { display_name: customLabel } : {}),
        signing_identity_mode: signingIdentityMode,
        anonymous_publisher: anonymousPublisher,
      });
    },
    onSuccess: async () => {
      toast.success('Publisher settings updated.');
      await refetchOrganizations();
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to update publisher settings.');
    },
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

  useEffect(() => {
    const resolvedMode = (activeOrganization?.signing_identity_mode as SigningIdentityMode | undefined) ?? 'organization_name';
    setSigningIdentityMode(resolvedMode);
    setPublisherDisplayName(
      activeOrganization?.signing_identity_custom_label ?? activeOrganization?.display_name ?? activeOrganization?.name ?? ''
    );
    setAnonymousPublisher(Boolean(activeOrganization?.anonymous_publisher));
  }, [activeOrganization]);

  const hasCustomSigningIdentityEntitlement =
    activeOrganization?.tier === 'enterprise' || Boolean(activeOrganization?.add_ons?.['custom-signing-identity']);

  const signingIdentityPreview = (() => {
    const baseName = activeOrganization?.display_name || activeOrganization?.name || 'Your organization';
    if (anonymousPublisher) return orgId || baseName;
    if (signingIdentityMode === 'custom') return publisherDisplayName.trim() || baseName;
    if (signingIdentityMode === 'organization_and_author') return `Author Name · ${baseName}`;
    return baseName;
  })();

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

  const domainClaimsQuery = useQuery({
    queryKey: ['domain-claims', orgId],
    queryFn: async () => {
      if (!accessToken || !orgId) return [];
      return apiClient.listDomainClaims(accessToken, orgId);
    },
    enabled: Boolean(accessToken && orgId),
    refetchOnWindowFocus: false,
  });

  const createDomainClaimMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken || !orgId) throw new Error('You must be signed in.');
      return apiClient.createDomainClaim(accessToken, orgId, {
        domain: domainName,
        verification_email: domainEmail,
      });
    },
    onSuccess: () => {
      toast.success('Domain claim created. Check your inbox to verify email ownership.');
      setDomainName('');
      setDomainEmail('');
      domainClaimsQuery.refetch();
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to create domain claim.');
    },
  });

  const verifyDnsMutation = useMutation({
    mutationFn: async (claimId: string) => {
      if (!accessToken || !orgId) throw new Error('You must be signed in.');
      return apiClient.verifyDomainClaimDns(accessToken, orgId, claimId);
    },
    onSuccess: (response) => {
      if (response?.data?.status === 'verified') {
        toast.success('Domain fully verified (DNS + email).');
      } else {
        toast.success('DNS verified. Finish email verification to complete domain verification.');
      }
      domainClaimsQuery.refetch();
    },
    onError: (err: any) => {
      toast.error(err?.message || 'DNS verification failed.');
    },
  });

  const deleteDomainClaimMutation = useMutation({
    mutationFn: async (claimId: string) => {
      if (!accessToken || !orgId) throw new Error('You must be signed in.');
      return apiClient.deleteDomainClaim(accessToken, orgId, claimId);
    },
    onSuccess: () => {
      toast.success('Domain claim removed.');
      domainClaimsQuery.refetch();
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to remove domain claim.');
    },
  });

  const updateAutoJoinMutation = useMutation({
    mutationFn: async ({ claimId, enabled }: { claimId: string; enabled: boolean }) => {
      if (!accessToken || !orgId) throw new Error('You must be signed in.');
      return apiClient.updateDomainAutoJoin(accessToken, orgId, claimId, enabled);
    },
    onSuccess: () => {
      toast.success('Auto-join setting updated.');
      domainClaimsQuery.refetch();
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to update auto-join setting.');
    },
  });

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

  const handleCreateDomainClaim = (e: React.FormEvent) => {
    e.preventDefault();
    if (!domainName.trim()) {
      toast.error('Please enter a domain.');
      return;
    }
    if (!domainEmail.trim()) {
      toast.error('Please enter a verification email.');
      return;
    }
    createDomainClaimMutation.mutate();
  };

  const handlePublisherSettingsSave = (e: React.FormEvent) => {
    e.preventDefault();
    updatePublisherSettingsMutation.mutate();
  };

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-delft-blue dark:text-white">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">Manage your account settings and preferences.</p>
      </div>

      <div className="grid md:grid-cols-4 gap-6">
          <div className="md:col-span-1">
            <Card>
              <CardContent className="p-4">
                <nav className="space-y-1">
                  {['profile', 'security', 'notifications', 'organization'].map((tab) => (
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
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Change password</CardTitle>
                    <CardDescription>Reset your password if you suspect your credentials were exposed.</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      Password changes are managed via the Encypher API. Use the “Forgot password” flow for secure
                      reset links.
                    </p>
                    <div className="mt-4">
                      <Link href="/forgot-password">
                        <Button variant="primary">Reset password</Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Two-factor authentication (TOTP)</CardTitle>
                    <CardDescription>
                      Protect your account with an authenticator app and one-time backup codes.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="text-sm text-muted-foreground">
                      Status: {mfaStatusQuery.data?.totp_enabled ? 'Enabled' : 'Not enabled'}
                      {mfaStatusQuery.data?.totp_enabled && (
                        <span className="ml-2">• Backup codes remaining: {mfaStatusQuery.data.backup_codes_remaining}</span>
                      )}
                    </div>

                    {!mfaStatusQuery.data?.totp_enabled && !totpSetupSecret && (
                      <Button variant="primary" onClick={() => beginTotpMutation.mutate()} disabled={beginTotpMutation.isPending}>
                        {beginTotpMutation.isPending ? 'Preparing…' : 'Set up authenticator app'}
                      </Button>
                    )}

                    {!mfaStatusQuery.data?.totp_enabled && totpSetupSecret && (
                      <div className="space-y-3 border border-border rounded-lg p-4">
                        <div className="text-sm">
                          <div className="font-medium">Manual setup code</div>
                          <div className="font-mono text-xs mt-1">{totpSetupSecret}</div>
                        </div>
                        {totpSetupUri && (
                          <div className="text-xs text-muted-foreground break-all">
                            otpauth URI: {totpSetupUri}
                          </div>
                        )}

                        {backupCodes.length > 0 && (
                          <div>
                            <div className="text-sm font-medium mb-2">Backup codes (save these now)</div>
                            <div className="grid grid-cols-2 gap-2">
                              {backupCodes.map((code) => (
                                <div key={code} className="font-mono text-xs rounded bg-muted px-2 py-1">
                                  {code}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="flex gap-2 items-end">
                          <div className="flex-1">
                            <label className="block text-sm font-medium mb-2">Authenticator code</label>
                            <Input
                              value={totpCode}
                              onChange={(e) => setTotpCode(e.target.value)}
                              placeholder="Enter 6-digit code"
                            />
                          </div>
                          <Button
                            variant="primary"
                            onClick={() => confirmTotpMutation.mutate()}
                            disabled={confirmTotpMutation.isPending || !totpCode.trim()}
                          >
                            {confirmTotpMutation.isPending ? 'Verifying…' : 'Enable 2FA'}
                          </Button>
                        </div>
                      </div>
                    )}

                    {mfaStatusQuery.data?.totp_enabled && (
                      <div className="space-y-3 border border-border rounded-lg p-4">
                        <label className="block text-sm font-medium">Disable 2FA with code</label>
                        <div className="flex gap-2 items-end">
                          <div className="flex-1">
                            <Input
                              value={totpDisableCode}
                              onChange={(e) => setTotpDisableCode(e.target.value)}
                              placeholder="Authenticator code or backup code"
                            />
                          </div>
                          <Button
                            variant="outline"
                            onClick={() => disableTotpMutation.mutate()}
                            disabled={disableTotpMutation.isPending || !totpDisableCode.trim()}
                          >
                            {disableTotpMutation.isPending ? 'Disabling…' : 'Disable 2FA'}
                          </Button>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Passkeys</CardTitle>
                    <CardDescription>
                      Register hardware or platform passkeys for phishing-resistant sign-in.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex gap-2 items-end">
                      <div className="flex-1">
                        <label className="block text-sm font-medium mb-2">Passkey label</label>
                        <Input value={passkeyName} onChange={(e) => setPasskeyName(e.target.value)} placeholder="e.g. MacBook Touch ID" />
                      </div>
                      <Button variant="primary" onClick={handleRegisterPasskey}>Register passkey</Button>
                    </div>

                    {(mfaStatusQuery.data?.passkeys || []).length === 0 ? (
                      <div className="text-sm text-muted-foreground">No passkeys registered yet.</div>
                    ) : (
                      <div className="space-y-2">
                        {(mfaStatusQuery.data?.passkeys || []).map((item) => (
                          <div key={item.credential_id} className="flex items-center justify-between border border-border rounded-lg px-3 py-2">
                            <div>
                              <div className="font-medium text-sm">{item.name || 'Passkey'}</div>
                              <div className="text-xs text-muted-foreground font-mono">{item.credential_id}</div>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => deletePasskeyMutation.mutate(item.credential_id)}
                              disabled={deletePasskeyMutation.isPending}
                            >
                              Remove
                            </Button>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
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

            {activeTab === 'organization' && (
              <Card>
                <CardHeader>
                  <CardTitle>Organization domains</CardTitle>
                  <CardDescription>
                    Verify your company domain to enable automatic org joins for matching emails.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {orgLoading ? (
                    <div className="text-muted-foreground">Loading organization…</div>
                  ) : !orgId ? (
                    <div className="text-muted-foreground">Select an organization to manage domain claims.</div>
                  ) : (
                    <>
                      <div className="rounded-lg border border-border p-4 space-y-4">
                        <div>
                          <h4 className="text-sm font-semibold">Publisher identity in verification</h4>
                          <p className="text-xs text-muted-foreground mt-1">
                            Control how your publisher name appears to readers when signed content is verified.
                          </p>
                        </div>

                        <form className="space-y-4" onSubmit={handlePublisherSettingsSave}>
                          <div>
                            <label className="block text-sm font-medium mb-2">Signing identity mode</label>
                            <select
                              value={signingIdentityMode}
                              onChange={(e) => setSigningIdentityMode(e.target.value as SigningIdentityMode)}
                              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                            >
                              <option value="organization_name">Use verified organization name</option>
                              <option value="organization_and_author">Use author + organization</option>
                              <option value="custom" disabled={!hasCustomSigningIdentityEntitlement}>
                                Custom signing identity {!hasCustomSigningIdentityEntitlement ? '(requires add-on)' : ''}
                              </option>
                            </select>
                            {!hasCustomSigningIdentityEntitlement && (
                              <p className="text-xs text-muted-foreground mt-2">
                                Custom Signing Identity add-on is available for $9/month.
                              </p>
                            )}
                          </div>

                          {signingIdentityMode === 'custom' && (
                            <div>
                              <label className="block text-sm font-medium mb-2">Custom label</label>
                              <Input
                                value={publisherDisplayName}
                                onChange={(e) => setPublisherDisplayName(e.target.value)}
                                placeholder="e.g. Encypher Editorial"
                              />
                            </div>
                          )}

                          <label className="flex items-start gap-3 text-sm">
                            <input
                              type="checkbox"
                              className="mt-0.5"
                              checked={anonymousPublisher}
                              onChange={(e) => setAnonymousPublisher(e.target.checked)}
                            />
                            <span>
                              <span className="font-medium">Don&apos;t show my name/org on verification</span>
                              <span className="block text-xs text-muted-foreground mt-1">
                                Show only organization ID instead (e.g. {orgId}).
                              </span>
                            </span>
                          </label>

                          <div className="rounded-md bg-muted px-3 py-2 text-xs text-muted-foreground">
                            Preview: {signingIdentityPreview}
                          </div>

                          <Button type="submit" variant="primary" disabled={updatePublisherSettingsMutation.isPending}>
                            {updatePublisherSettingsMutation.isPending ? 'Saving…' : 'Save publisher settings'}
                          </Button>
                        </form>
                      </div>

                      <form className="space-y-4" onSubmit={handleCreateDomainClaim}>
                        <div className="grid md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium mb-2">Domain</label>
                            <Input
                              placeholder="example.com"
                              value={domainName}
                              onChange={(e) => setDomainName(e.target.value)}
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium mb-2">Verification email</label>
                            <Input
                              type="email"
                              placeholder="admin@example.com"
                              value={domainEmail}
                              onChange={(e) => setDomainEmail(e.target.value)}
                            />
                          </div>
                        </div>
                        <Button type="submit" variant="primary" disabled={createDomainClaimMutation.isPending}>
                          {createDomainClaimMutation.isPending ? 'Submitting…' : 'Request verification'}
                        </Button>
                      </form>

                      <div className="border-t border-border pt-6">
                        <h4 className="text-sm font-semibold mb-3">Domain claims</h4>
                        {domainClaimsQuery.isLoading ? (
                          <div className="text-muted-foreground">Loading domain claims…</div>
                        ) : (domainClaimsQuery.data ?? []).length === 0 ? (
                          <div className="text-muted-foreground">No domain claims yet.</div>
                        ) : (
                          <div className="space-y-4">
                            {(domainClaimsQuery.data ?? []).map((claim) => (
                              <div key={claim.id} className="border border-border rounded-lg p-4 space-y-3">
                                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                                  <div>
                                    <div className="font-medium">{claim.domain}</div>
                                    <div className="text-xs text-muted-foreground">{claim.verification_email}</div>
                                  </div>
                                  <Badge variant="outline">{claim.status}</Badge>
                                </div>
                                <div className="text-xs text-muted-foreground">
                                  DNS TXT:{' '}
                                  <span className="font-mono">
                                    {claim.dns_txt_record || `encypher-domain-claim=${claim.dns_token}`}
                                  </span>
                                </div>
                                <div className="flex flex-col md:flex-row gap-3 md:items-center md:justify-between">
                                  <div className="flex items-center gap-2">
                                    <Button
                                      type="button"
                                      variant="outline"
                                      size="sm"
                                      onClick={() => verifyDnsMutation.mutate(claim.id)}
                                      disabled={verifyDnsMutation.isPending}
                                    >
                                      Verify DNS
                                    </Button>
                                    <Button
                                      type="button"
                                      variant="outline"
                                      size="sm"
                                      onClick={() => deleteDomainClaimMutation.mutate(claim.id)}
                                      disabled={deleteDomainClaimMutation.isPending}
                                    >
                                      Remove
                                    </Button>
                                    {claim.status === 'verified' && (
                                      <div className="flex items-center gap-2 text-sm">
                                        <span className="text-muted-foreground">Auto-join</span>
                                        <input
                                          type="checkbox"
                                          checked={claim.auto_join_enabled}
                                          onChange={(e) =>
                                            updateAutoJoinMutation.mutate({
                                              claimId: claim.id,
                                              enabled: e.target.checked,
                                            })
                                          }
                                        />
                                      </div>
                                    )}
                                  </div>
                                  <div className="text-xs text-muted-foreground">
                                    {claim.verified_at
                                      ? `Verified ${new Date(claim.verified_at).toLocaleDateString()}`
                                      : 'Awaiting verification'}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
    </DashboardLayout>
  );
}

