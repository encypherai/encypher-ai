'use client';

import { useSession, signOut } from 'next-auth/react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { ReactNode, useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { OrganizationSwitcher } from '../OrganizationSwitcher';
import { MobileNav } from '../MobileNav';
import { NotificationCenter } from '../NotificationCenter';
import { ThemeToggleButton } from '../../contexts/ThemeContext';
import apiClient from '../../lib/api';
import { useOrganization } from '../../contexts/OrganizationContext';
import { SetupWizard } from '../onboarding/SetupWizard';

interface DashboardLayoutProps {
  children: ReactNode;
}

// ── Icon components (inline SVG for zero-dependency sidebar) ──

function IconOverview({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>
  );
}

function IconKey({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
    </svg>
  );
}

function IconPlayground({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function IconRights({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  );
}

function IconIntegrations({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
    </svg>
  );
}

function IconAnalytics({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  );
}

function IconDocs({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
  );
}

function IconWebhooks({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  );
}

function IconTeam({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
  );
}

function IconSettings({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  );
}

function IconBilling({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
    </svg>
  );
}

function IconAICrawlers({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="4" width="10" height="8" rx="2" stroke="currentColor" strokeWidth="1.5"/>
      <circle cx="5.5" cy="7" r="1" fill="currentColor"/>
      <circle cx="10.5" cy="7" r="1" fill="currentColor"/>
      <path d="M5.5 10h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M6 4V2.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M10 4V2.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <path d="M1 8h2M13 8h2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  );
}

function IconAuditLogs({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  );
}

function IconAdmin({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  );
}

function IconSignOut({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
    </svg>
  );
}

function IconApiDocs({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
    </svg>
  );
}

// ── Nav structure ──

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  enterpriseOnly?: boolean;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const navGroupsByLayout: Record<'publisher' | 'enterprise', NavGroup[]> = {
  publisher: [
    {
      label: '',
      items: [
        { href: '/', label: 'Overview', icon: IconOverview },
        { href: '/integrations', label: 'Integrations', icon: IconIntegrations },
      ],
    },
    {
      label: 'Publish',
      items: [
        { href: '/rights', label: 'Rights', icon: IconRights },
        { href: '/api-keys', label: 'API Keys', icon: IconKey },
        { href: '/playground', label: 'Playground', icon: IconPlayground },
      ],
    },
    {
      label: 'Insights',
      items: [
        { href: '/analytics', label: 'Content Performance', icon: IconAnalytics },
        { href: '/ai-crawlers', label: 'AI Crawlers', icon: IconAICrawlers },
        { href: '/docs', label: 'Docs', icon: IconDocs },
      ],
    },
    {
      label: 'Enterprise',
      items: [
        { href: '/webhooks', label: 'Webhooks', icon: IconWebhooks, enterpriseOnly: true },
        { href: '/team', label: 'Team', icon: IconTeam, enterpriseOnly: true },
        { href: '/audit-logs', label: 'Audit Logs', icon: IconAuditLogs, enterpriseOnly: true },
      ],
    },
    {
      label: 'Account',
      items: [
        { href: '/settings', label: 'Settings', icon: IconSettings },
        { href: '/billing', label: 'Billing', icon: IconBilling },
      ],
    },
  ],
  enterprise: [
    {
      label: '',
      items: [
        { href: '/', label: 'Overview', icon: IconOverview },
        { href: '/playground', label: 'Playground', icon: IconPlayground },
      ],
    },
    {
      label: 'Publish',
      items: [
        { href: '/api-keys', label: 'API Keys', icon: IconKey },
        { href: '/rights', label: 'Rights', icon: IconRights },
        { href: '/integrations', label: 'Integrations', icon: IconIntegrations },
      ],
    },
    {
      label: 'Insights',
      items: [
        { href: '/analytics', label: 'Content Performance', icon: IconAnalytics },
        { href: '/ai-crawlers', label: 'AI Crawlers', icon: IconAICrawlers },
        { href: '/docs', label: 'Docs', icon: IconDocs },
      ],
    },
    {
      label: 'Enterprise',
      items: [
        { href: '/webhooks', label: 'Webhooks', icon: IconWebhooks, enterpriseOnly: true },
        { href: '/team', label: 'Team', icon: IconTeam, enterpriseOnly: true },
        { href: '/audit-logs', label: 'Audit Logs', icon: IconAuditLogs, enterpriseOnly: true },
      ],
    },
    {
      label: 'Account',
      items: [
        { href: '/settings', label: 'Settings', icon: IconSettings },
        { href: '/billing', label: 'Billing', icon: IconBilling },
      ],
    },
  ],
};

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { data: session, status } = useSession();
  const pathname = usePathname();
  const router = useRouter();
  const { activeOrganization } = useOrganization();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const userTier = (session?.user as any)?.tier || 'free';
  const sessionError = (session?.user as any)?.error as string | undefined;
  const isEnterprise = userTier === 'enterprise';
  const userName = session?.user?.name || session?.user?.email || 'User';
  const userInitial = userName.charAt(0).toUpperCase();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [setupWizardLatchedOpen, setSetupWizardLatchedOpen] = useState(false);

  // TEAM_006: Check if user is super admin via API
  const { data: isSuperAdmin } = useQuery({
    queryKey: ['is-super-admin'],
    queryFn: async () => {
      if (!accessToken) return false;
      return apiClient.isSuperAdmin(accessToken);
    },
    enabled: Boolean(accessToken),
    staleTime: 5 * 60 * 1000,
  });

  const isAdmin = isSuperAdmin === true;

  // Session guard: redirect unauthenticated users and force-logout on refresh failure
  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login?callbackUrl=' + encodeURIComponent(pathname));
      return;
    }
    if (sessionError === 'RefreshAccessTokenError') {
      signOut({ callbackUrl: '/login?reason=session_expired' });
    }
  }, [status, sessionError, router, pathname]);

  // TEAM_191: Check if mandatory setup wizard is complete
  const { data: setupStatus, isLoading: setupLoading } = useQuery({
    queryKey: ['setup-status'],
    queryFn: async () => {
      if (!accessToken) return null;
      return apiClient.getSetupStatus(accessToken);
    },
    enabled: Boolean(accessToken),
    staleTime: 60_000,
    retry: 1,
  });

  useEffect(() => {
    if (setupStatus?.setup_completed === false) {
      setSetupWizardLatchedOpen(true);
      return;
    }

    if (setupStatus?.setup_completed === true) {
      setSetupWizardLatchedOpen(false);
    }
  }, [setupStatus?.setup_completed]);

  const showSetupWizard = setupWizardLatchedOpen || (!setupLoading && setupStatus?.setup_completed === false);
  const dashboardLayoutPreference =
    activeOrganization?.dashboard_layout === 'enterprise' || setupStatus?.dashboard_layout === 'enterprise'
      ? 'enterprise'
      : 'publisher';

  // Filter groups: hide enterprise group for free users, remove empty groups
  const visibleGroups = navGroupsByLayout[dashboardLayoutPreference]
    .map(group => ({
      ...group,
      items: group.items.filter(item => !item.enterpriseOnly || isEnterprise || isAdmin),
    }))
    .filter(group => group.items.length > 0);

  // Flat list for MobileNav compatibility
  const visibleNavItems = visibleGroups.flatMap(g => g.items);

  const handleSignOut = () => {
    signOut({ callbackUrl: process.env.NEXT_PUBLIC_SITE_URL || 'https://s-www.encypherai.com' });
  };

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/';
    return pathname === href || pathname.startsWith(href + '/');
  };

  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-slate-900">
      {/* TEAM_191: Mandatory setup wizard overlay */}
      {showSetupWizard && <SetupWizard />}

      {/* ── Desktop Sidebar ── */}
      <aside
        className={`hidden lg:flex flex-col fixed inset-y-0 left-0 z-40 bg-[#1B2F50] transition-all duration-200 ${
          sidebarCollapsed ? 'w-[68px]' : 'w-60'
        }`}
      >
        {/* Logo */}
        <div className="flex items-center h-16 px-4 border-b border-white/10 flex-shrink-0">
          <Link href="/" className="flex items-center min-w-0">
            {sidebarCollapsed ? (
              <Image
                src="/assets/encypher_check_white.svg"
                alt="Encypher"
                width={28}
                height={28}
                className="h-7 w-7"
                priority
              />
            ) : (
              <Image
                src="/assets/encypher_full_logo_white.svg"
                alt="Encypher"
                width={120}
                height={30}
                className="h-7 w-auto"
                priority
              />
            )}
          </Link>
          {!sidebarCollapsed && (
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="ml-auto p-1.5 rounded-md text-white/50 hover:text-white hover:bg-white/10 transition-colors"
              aria-label="Collapse sidebar"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
            </button>
          )}
          {sidebarCollapsed && (
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="ml-auto p-1 rounded-md text-white/50 hover:text-white hover:bg-white/10 transition-colors"
              aria-label="Expand sidebar"
            >
              <svg className="w-3.5 h-3.5 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
            </button>
          )}
        </div>

        {/* Org switcher (enterprise) */}
        {isEnterprise && !sidebarCollapsed && (
          <div className="px-3 py-3 border-b border-white/10">
            <OrganizationSwitcher />
          </div>
        )}

        {/* Nav groups */}
        <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-4">
          {visibleGroups.map((group, gi) => (
            <div key={gi}>
              {group.label && !sidebarCollapsed && (
                <p className="px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-white/40">
                  {group.label}
                </p>
              )}
              {group.label && sidebarCollapsed && gi > 0 && (
                <div className="mx-2 mb-2 border-t border-white/10" />
              )}
              <ul className="space-y-0.5">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.href);
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        title={sidebarCollapsed ? item.label : undefined}
                        className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                          active
                            ? 'bg-white/15 text-white'
                            : 'text-white/70 hover:bg-white/10 hover:text-white'
                        } ${sidebarCollapsed ? 'justify-center' : ''}`}
                      >
                        <Icon className="w-[18px] h-[18px] flex-shrink-0" />
                        {!sidebarCollapsed && <span className="truncate">{item.label}</span>}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}

          {/* Admin link */}
          {isAdmin && (
            <div>
              {!sidebarCollapsed && (
                <p className="px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-white/40">
                  Admin
                </p>
              )}
              {sidebarCollapsed && <div className="mx-2 mb-2 border-t border-white/10" />}
              <Link
                href="/admin"
                title={sidebarCollapsed ? 'Admin' : undefined}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive('/admin')
                    ? 'bg-white/15 text-white'
                    : 'text-white/70 hover:bg-white/10 hover:text-white'
                } ${sidebarCollapsed ? 'justify-center' : ''}`}
              >
                <IconAdmin className="w-[18px] h-[18px] flex-shrink-0" />
                {!sidebarCollapsed && <span>Admin</span>}
              </Link>
            </div>
          )}
        </nav>

        {/* Sidebar footer */}
        <div className="flex-shrink-0 border-t border-white/10 p-2 space-y-0.5">
          <a
            href="https://api.encypherai.com/docs"
            target="_blank"
            rel="noopener noreferrer"
            title={sidebarCollapsed ? 'API Reference' : undefined}
            className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-white/50 hover:text-white hover:bg-white/10 transition-colors ${
              sidebarCollapsed ? 'justify-center' : ''
            }`}
          >
            <IconApiDocs className="w-[18px] h-[18px] flex-shrink-0" />
            {!sidebarCollapsed && <span>API Reference</span>}
          </a>
          <button
            onClick={handleSignOut}
            title={sidebarCollapsed ? 'Sign out' : undefined}
            className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm font-medium text-white/50 hover:text-red-300 hover:bg-white/10 transition-colors ${
              sidebarCollapsed ? 'justify-center' : ''
            }`}
          >
            <IconSignOut className="w-[18px] h-[18px] flex-shrink-0" />
            {!sidebarCollapsed && <span>Sign out</span>}
          </button>
        </div>
      </aside>

      {/* ── Main area (offset by sidebar width) ── */}
      <div className={`flex-1 flex flex-col min-h-screen transition-all duration-200 ${
        sidebarCollapsed ? 'lg:ml-[68px]' : 'lg:ml-60'
      }`}>
        {/* ── Top header bar ── */}
        <header className="sticky top-0 z-30 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between h-14 px-4 sm:px-6">
            {/* Mobile: hamburger + logo */}
            <div className="flex items-center gap-3 lg:hidden">
              <button
                onClick={() => setIsMobileMenuOpen(true)}
                className="p-2 -ml-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                aria-label="Open menu"
              >
                <svg className="w-5 h-5 text-slate-600 dark:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <Link href="/" className="flex items-center">
                <Image
                  src="/assets/encypher_full_logo_color.svg"
                  alt="Encypher"
                  width={110}
                  height={28}
                  className="h-6 w-auto dark:hidden"
                  priority
                />
                <Image
                  src="/assets/encypher_full_logo_white.svg"
                  alt="Encypher"
                  width={110}
                  height={28}
                  className="h-6 w-auto hidden dark:block"
                  priority
                />
              </Link>
            </div>

            {/* Desktop: breadcrumb-style page title area (empty for now, keeps header balanced) */}
            <div className="hidden lg:block" />

            {/* Right side: theme + notifications + user */}
            <div className="flex items-center gap-1.5">
              <ThemeToggleButton />
              <NotificationCenter />
              <Link
                href="/settings"
                className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-[#2A87C4] to-[#1B2F50] rounded-full flex items-center justify-center text-white text-sm font-semibold">
                  {userInitial}
                </div>
                <span className="hidden sm:block text-sm font-medium text-slate-700 dark:text-slate-200 max-w-[120px] truncate">
                  {userName}
                </span>
              </Link>
            </div>
          </div>
        </header>

        {/* ── Page content ── */}
        <main className="flex-1 px-4 sm:px-6 lg:px-8 py-6 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>

      {/* ── Mobile Navigation (slide-out drawer) ── */}
      <MobileNav
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
        navItems={visibleNavItems}
        isAdmin={isAdmin}
        userName={userName}
        userEmail={session?.user?.email || ''}
        userInitial={userInitial}
      />
    </div>
  );
}

export default DashboardLayout;
