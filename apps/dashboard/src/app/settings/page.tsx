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
import { Copy, Check } from 'lucide-react';
import QRCode from 'qrcode';
import { toast } from 'sonner';
import apiClient from '../../lib/api';
import type { DomainClaimInfo } from '../../lib/api';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { useOrganization } from '../../contexts/OrganizationContext';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'https://api.encypherai.com/api/v1').replace(/\/$/, '');

function ToggleSwitch({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-5 w-10 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-ncs focus-visible:ring-offset-2 ${
        checked ? 'bg-blue-ncs' : 'bg-muted'
      }`}
    >
      <span
        className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition-transform duration-200 ${
          checked ? 'translate-x-5' : 'translate-x-0'
        }`}
      />
    </button>
  );
}

function StyledSelect({ value, onChange, disabled, children }: {
  value: string;
  onChange: (v: string) => void;
  disabled?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="relative w-full">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="flex w-full appearance-none rounded-lg border border-input bg-background px-3 py-2 pr-10 text-sm h-10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
      >
        {children}
      </select>
      <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
}

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
  const [newlyCreatedClaim, setNewlyCreatedClaim] = useState<DomainClaimInfo | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [publisherDisplayName, setPublisherDisplayName] = useState('');
  const [signingIdentityMode, setSigningIdentityMode] = useState<SigningIdentityMode>('organization_name');
  const [anonymousPublisher, setAnonymousPublisher] = useState(false);
  const [totpCode, setTotpCode] = useState('');
  const [totpDisableCode, setTotpDisableCode] = useState('');
  const [totpSetupSecret, setTotpSetupSecret] = useState<string | null>(null);
  const [totpSetupUri, setTotpSetupUri] = useState<string | null>(null);
  const [totpQrCodeDataUrl, setTotpQrCodeDataUrl] = useState<string | null>(null);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [passkeyName, setPasskeyName] = useState('Primary device');
  const [enforceMfa, setEnforceMfa] = useState(false);

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
    if (!session?.user) {
      window.location.href = '/login';
      return;
    }
    if (session?.user) {
      setProfile((prev) => ({
        ...prev,
        name: (session.user as any)?.name || prev.name,
        email: session.user?.email || prev.email,
      }));
    }
  }, [session]);

  useEffect(() => {
    let cancelled = false;

    const renderQr = async () => {
      if (!totpSetupUri) {
        setTotpQrCodeDataUrl(null);
        return;
      }

      try {
        const dataUrl = await QRCode.toDataURL(totpSetupUri, {
          errorCorrectionLevel: 'M',
          margin: 1,
          width: 220,
        });
        if (!cancelled) {
          setTotpQrCodeDataUrl(dataUrl);
        }
      } catch {
        if (!cancelled) {
          setTotpQrCodeDataUrl(null);
        }
      }
    };

    renderQr();

    return () => {
      cancelled = true;
    };
  }, [totpSetupUri]);

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
    onSuccess: (response) => {
      toast.success('Domain added. Check your email for DNS setup instructions.');
      setDomainName('');
      setDomainEmail('');
      setNewlyCreatedClaim(response?.data ?? null);
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
        toast.success('Domain verified.');
      } else {
        toast.info('DNS record not yet detected. Propagation may take a few minutes.');
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

  const orgSecurityQuery = useQuery({
    queryKey: ['org-security', orgId],
    queryFn: async () => {
      if (!accessToken || !orgId) return null;
      const response = await fetch(`${API_BASE}/organizations/${orgId}/security`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!response.ok) return null;
      const data = await response.json();
      return data.data as { enforce_mfa: boolean };
    },
    enabled: Boolean(accessToken && orgId && activeTab === 'organization'),
    refetchOnWindowFocus: false,
  });

  useEffect(() => {
    if (orgSecurityQuery.data) {
      setEnforceMfa(Boolean(orgSecurityQuery.data.enforce_mfa));
    }
  }, [orgSecurityQuery.data]);

  const updateOrgSecurityMutation = useMutation({
    mutationFn: async (enforce: boolean) => {
      if (!accessToken || !orgId) throw new Error('You must be signed in.');
      const response = await fetch(`${API_BASE}/organizations/${orgId}/security`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${accessToken}` },
        body: JSON.stringify({ enforce_mfa: enforce }),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update security settings');
      }
      return response.json();
    },
    onSuccess: (_, enforce) => {
      setEnforceMfa(enforce);
      toast.success(enforce ? '2FA enforcement enabled.' : '2FA enforcement disabled.');
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to update security settings.');
    },
  });

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
                        activeTab === tab ? 'bg-blue-ncs text-white' : 'text-muted-foreground hover:bg-muted'
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
                        {totpQrCodeDataUrl && (
                          <div className="text-sm">
                            <div className="font-medium mb-2">Scan this QR code with Google Authenticator</div>
                            <img
                              src={totpQrCodeDataUrl}
                              alt="TOTP setup QR code"
                              width={220}
                              height={220}
                              className="rounded border border-border bg-white p-2"
                            />
                          </div>
                        )}
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
                          <ToggleSwitch
                            checked={Boolean(value)}
                            onChange={(v) =>
                              setProfile((prev) => ({
                                ...prev,
                                notifications: {
                                  ...(prev.notifications ?? defaultNotifications),
                                  [key]: v,
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
                            <StyledSelect
                              value={signingIdentityMode}
                              onChange={(v) => setSigningIdentityMode(v as SigningIdentityMode)}
                            >
                              <option value="organization_name">Use verified organization name</option>
                              <option value="organization_and_author">Use author + organization</option>
                              <option value="custom" disabled={!hasCustomSigningIdentityEntitlement}>
                                Custom signing identity {!hasCustomSigningIdentityEntitlement ? '(requires add-on)' : ''}
                              </option>
                            </StyledSelect>
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

                          <div className="flex items-start gap-3">
                            <ToggleSwitch
                              checked={anonymousPublisher}
                              onChange={setAnonymousPublisher}
                            />
                            <span className="text-sm">
                              <span className="font-medium">Anonymous publisher</span>
                              <span className="block text-xs text-muted-foreground mt-1">
                                Show only organization ID instead of name (e.g. {orgId}).
                              </span>
                            </span>
                          </div>

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
                            <label className="block text-sm font-medium mb-2">Contact email</label>
                            <Input
                              type="email"
                              placeholder="admin@example.com"
                              value={domainEmail}
                              onChange={(e) => setDomainEmail(e.target.value)}
                            />
                            <p className="text-xs text-muted-foreground mt-1">
                              Must match the domain you are verifying. Used only to send DNS setup instructions.
                            </p>
                          </div>
                        </div>
                        <Button type="submit" variant="primary" disabled={createDomainClaimMutation.isPending}>
                          {createDomainClaimMutation.isPending ? 'Adding…' : 'Add domain'}
                        </Button>
                      </form>

                      {newlyCreatedClaim && (
                        <div className="rounded-lg border border-amber-200 bg-amber-50 dark:bg-amber-950/20 dark:border-amber-800 p-4 space-y-3">
                          <div className="flex items-center justify-between">
                            <h5 className="text-sm font-semibold text-amber-900 dark:text-amber-200">
                              DNS setup required for {newlyCreatedClaim.domain}
                            </h5>
                            <button
                              type="button"
                              onClick={() => setNewlyCreatedClaim(null)}
                              className="text-amber-500 hover:text-amber-700 text-xs"
                            >
                              Dismiss
                            </button>
                          </div>
                          <p className="text-xs text-amber-800 dark:text-amber-300">
                            Add this TXT record to your DNS provider under the{' '}
                            <strong>{newlyCreatedClaim.domain}</strong> zone, then click Verify DNS.
                          </p>
                          <div className="flex items-center gap-2">
                            <code className="flex-1 text-xs bg-white dark:bg-black/30 border border-amber-200 dark:border-amber-800 rounded px-3 py-2 font-mono break-all">
                              {newlyCreatedClaim.dns_txt_record || `encypher-domain-claim=${newlyCreatedClaim.dns_token}`}
                            </code>
                            <button
                              type="button"
                              title="Copy TXT record"
                              onClick={() => {
                                const val = newlyCreatedClaim.dns_txt_record || `encypher-domain-claim=${newlyCreatedClaim.dns_token}`;
                                navigator.clipboard.writeText(val).then(() => {
                                  setCopiedId('new');
                                  setTimeout(() => setCopiedId(null), 2000);
                                });
                              }}
                              className="shrink-0 p-1.5 rounded hover:bg-amber-100 dark:hover:bg-amber-900/40 text-amber-700 dark:text-amber-300"
                            >
                              {copiedId === 'new' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                            </button>
                          </div>
                        </div>
                      )}

                      <div className="border-t border-border pt-6">
                        <h4 className="text-sm font-semibold mb-3">Security requirements</h4>
                        <div className="flex items-start gap-4 py-3">
                          <div className="flex-1">
                            <p className="text-sm font-medium">Require two-factor authentication</p>
                            <p className="text-xs text-muted-foreground mt-0.5">
                              When enabled, members without 2FA set up will be blocked from signing in.
                            </p>
                          </div>
                          <ToggleSwitch
                            checked={enforceMfa}
                            onChange={(v) => updateOrgSecurityMutation.mutate(v)}
                          />
                        </div>
                      </div>

                      <div className="border-t border-border pt-6">
                        <h4 className="text-sm font-semibold mb-3">Domain claims</h4>
                        {domainClaimsQuery.isLoading ? (
                          <div className="text-muted-foreground">Loading domain claims…</div>
                        ) : (domainClaimsQuery.data ?? []).length === 0 ? (
                          <div className="text-center py-8 text-muted-foreground text-sm">
                            No domains added yet. Add your first domain to verify publisher identity.
                          </div>
                        ) : (
                          <div className="space-y-4">
                            {(domainClaimsQuery.data ?? []).map((claim) => {
                              const txtRecord = claim.dns_txt_record || `encypher-domain-claim=${claim.dns_token}`;
                              const statusBadge =
                                claim.status === 'verified'
                                  ? <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300">
                                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                      Verified
                                      {claim.dns_verified_at && (
                                        <span className="text-emerald-600 dark:text-emerald-400">
                                          {' '}&mdash; {new Date(claim.dns_verified_at).toLocaleDateString()}
                                        </span>
                                      )}
                                    </span>
                                  : claim.status === 'failed'
                                  ? <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300">
                                      <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                                      Check failed
                                    </span>
                                  : <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300">
                                      <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                      Pending DNS
                                    </span>;
                              return (
                                <div key={claim.id} className="border border-border rounded-lg p-4 space-y-3">
                                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                                    <div>
                                      <div className="font-medium">{claim.domain}</div>
                                      <div className="text-xs text-muted-foreground">{claim.verification_email}</div>
                                    </div>
                                    {statusBadge}
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <code className="flex-1 text-xs bg-muted rounded px-3 py-2 font-mono break-all">
                                      {txtRecord}
                                    </code>
                                    <button
                                      type="button"
                                      title="Copy TXT record"
                                      onClick={() => {
                                        navigator.clipboard.writeText(txtRecord).then(() => {
                                          setCopiedId(claim.id);
                                          setTimeout(() => setCopiedId(null), 2000);
                                        });
                                      }}
                                      className="shrink-0 p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground"
                                    >
                                      {copiedId === claim.id ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                                    </button>
                                  </div>
                                  <div className="flex flex-col md:flex-row gap-3 md:items-center md:justify-between">
                                    <div className="flex items-center gap-2">
                                      {claim.status !== 'verified' && (
                                        <Button
                                          type="button"
                                          variant="outline"
                                          size="sm"
                                          onClick={() => verifyDnsMutation.mutate(claim.id)}
                                          disabled={verifyDnsMutation.isPending}
                                          title="Check that your TXT record is live"
                                        >
                                          Verify DNS
                                        </Button>
                                      )}
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
                                          <ToggleSwitch
                                            checked={Boolean(claim.auto_join_enabled)}
                                            onChange={(v) =>
                                              updateAutoJoinMutation.mutate({
                                                claimId: claim.id,
                                                enabled: v,
                                              })
                                            }
                                          />
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
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

