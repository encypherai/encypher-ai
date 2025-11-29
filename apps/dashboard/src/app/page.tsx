'use client';

import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent } from '@encypher/design-system';
import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import Link from 'next/link';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { OnboardingModal, useIsNewUser } from '../components/onboarding/OnboardingModal';
import apiClient from '../lib/api';

// Icons as components for cleaner code
const IconKey = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
  </svg>
);

const IconChart = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
);

const IconShield = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
  </svg>
);

const IconDocument = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

const IconCheck = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const IconBook = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
  </svg>
);

const IconArrowRight = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

const IconPlus = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

// Skeleton loader component
function StatCardSkeleton() {
  return (
    <div className="bg-white rounded-xl border border-border p-6 animate-pulse">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="h-4 w-24 bg-muted rounded mb-3" />
          <div className="h-10 w-20 bg-muted rounded mb-2" />
          <div className="h-3 w-32 bg-muted rounded" />
        </div>
        <div className="w-12 h-12 bg-muted rounded-xl" />
      </div>
    </div>
  );
}

function ApiKeysSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2].map((i) => (
        <div key={i} className="bg-gradient-to-r from-slate-50 to-white rounded-xl border border-border p-5 animate-pulse">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-muted rounded-lg" />
            <div className="flex-1">
              <div className="h-5 w-32 bg-muted rounded mb-2" />
              <div className="h-4 w-48 bg-muted rounded" />
            </div>
            <div className="h-6 w-16 bg-muted rounded-full" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function DashboardPage() {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const isNewUser = useIsNewUser();

  // Fetch usage stats
  const statsQuery = useQuery({
    queryKey: ['usage-stats'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getUsageStats(accessToken, 30);
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
    // Return mock data on error for demo purposes
    placeholderData: {
      total_api_calls: 0,
      total_documents_signed: 0,
      total_verifications: 0,
      success_rate: 0,
      avg_response_time_ms: 0,
      period_start: new Date().toISOString(),
      period_end: new Date().toISOString(),
    },
  });

  // Fetch API keys
  const keysQuery = useQuery({
    queryKey: ['api-keys-summary'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getApiKeys(accessToken);
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
  });

  const stats = statsQuery.data;
  const apiKeys = keysQuery.data || [];
  const isLoadingStats = statsQuery.isLoading;
  const isLoadingKeys = keysQuery.isLoading;

  // Format numbers with commas
  const formatNumber = (num: number) => num?.toLocaleString() ?? '0';

  const userName = session?.user?.name || session?.user?.email?.split('@')[0] || 'there';
  const greeting = new Date().getHours() < 12 ? 'Good morning' : new Date().getHours() < 18 ? 'Good afternoon' : 'Good evening';

  return (
    <DashboardLayout>
      {/* Onboarding Modal for new users */}
      <OnboardingModal isNewUser={isNewUser} />

      {/* Welcome Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-delft-blue via-delft-blue to-blue-ncs p-8 mb-8">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-96 h-96 bg-white rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-columbia-blue rounded-full blur-3xl transform -translate-x-1/2 translate-y-1/2" />
        </div>
        
        <div className="relative z-10">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-white mb-2">
                {greeting}, {userName}
              </h1>
              <p className="text-columbia-blue text-lg">
                Your content authentication infrastructure is ready.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link href="/api-keys">
                <button className="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-delft-blue font-medium rounded-lg hover:bg-columbia-blue transition-colors">
                  <IconPlus />
                  New API Key
                </button>
              </Link>
              <a href="https://docs.encypherai.com" target="_blank" rel="noopener noreferrer">
                <button className="inline-flex items-center gap-2 px-5 py-2.5 bg-white/10 text-white font-medium rounded-lg hover:bg-white/20 transition-colors border border-white/20">
                  <IconBook />
                  View Docs
                </button>
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Overview - Enhanced Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8">
        {isLoadingStats ? (
          <>
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </>
        ) : (
          <>
            {/* API Calls Card */}
            <div className="bg-white rounded-xl border border-border p-5 lg:p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">API Calls</p>
                  <p className="text-3xl lg:text-4xl font-bold text-delft-blue">
                    {formatNumber(stats?.total_api_calls || 0)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    Last 30 days
                  </p>
                </div>
                <div className="w-11 h-11 bg-gradient-to-br from-blue-ncs to-columbia-blue rounded-xl flex items-center justify-center text-white">
                  <IconChart />
                </div>
              </div>
            </div>

            {/* Documents Signed Card */}
            <div className="bg-white rounded-xl border border-border p-5 lg:p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Documents Signed</p>
                  <p className="text-3xl lg:text-4xl font-bold text-delft-blue">
                    {formatNumber(stats?.total_documents_signed || 0)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    Last 30 days
                  </p>
                </div>
                <div className="w-11 h-11 bg-gradient-to-br from-delft-blue to-blue-ncs rounded-xl flex items-center justify-center text-white">
                  <IconDocument />
                </div>
              </div>
            </div>

            {/* Verifications Card */}
            <div className="bg-white rounded-xl border border-border p-5 lg:p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Verifications</p>
                  <p className="text-3xl lg:text-4xl font-bold text-delft-blue">
                    {formatNumber(stats?.total_verifications || 0)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    Last 30 days
                  </p>
                </div>
                <div className="w-11 h-11 bg-gradient-to-br from-columbia-blue to-blue-ncs rounded-xl flex items-center justify-center text-white">
                  <IconShield />
                </div>
              </div>
            </div>

            {/* Success Rate Card */}
            <div className="bg-white rounded-xl border border-border p-5 lg:p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Success Rate</p>
                  <p className="text-3xl lg:text-4xl font-bold text-delft-blue">
                    {stats?.success_rate?.toFixed(1) || '100'}%
                  </p>
                  <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    Last 30 days
                  </p>
                </div>
                <div className="w-11 h-11 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center text-white">
                  <IconCheck />
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6 lg:gap-8">
        {/* API Keys Section - Takes 2 columns */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl border border-border overflow-hidden">
            <div className="p-6 border-b border-border">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-delft-blue">API Keys</h2>
                  <p className="text-sm text-muted-foreground mt-1">Manage your authentication credentials</p>
                </div>
                <Link href="/api-keys">
                  <button className="inline-flex items-center gap-2 px-4 py-2 bg-blue-ncs text-white font-medium rounded-lg hover:bg-blue-ncs/90 transition-colors text-sm">
                    <IconPlus />
                    Manage Keys
                  </button>
                </Link>
              </div>
            </div>
            
            <div className="p-6">
              {isLoadingKeys ? (
                <ApiKeysSkeleton />
              ) : apiKeys.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-20 h-20 bg-gradient-to-br from-columbia-blue/20 to-blue-ncs/20 rounded-2xl flex items-center justify-center mx-auto mb-5">
                    <div className="w-12 h-12 bg-gradient-to-br from-columbia-blue to-blue-ncs rounded-xl flex items-center justify-center text-white">
                      <IconKey />
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-delft-blue mb-2">No API Keys Yet</h3>
                  <p className="text-muted-foreground mb-6 max-w-sm mx-auto">
                    Generate your first API key to start authenticating your content with cryptographic proof.
                  </p>
                  <Link href="/api-keys">
                    <button className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-ncs to-delft-blue text-white font-medium rounded-lg hover:opacity-90 transition-opacity">
                      <IconPlus />
                      Generate Your First Key
                    </button>
                  </Link>
                </div>
              ) : (
                <div className="space-y-3">
                  {apiKeys.slice(0, 3).map((key) => (
                    <Link 
                      key={key.id} 
                      href="/api-keys"
                      className="group flex items-center gap-4 p-4 rounded-xl border border-border hover:border-blue-ncs/30 hover:bg-gradient-to-r hover:from-columbia-blue/5 hover:to-transparent transition-all cursor-pointer"
                    >
                      <div className="w-10 h-10 bg-gradient-to-br from-columbia-blue to-blue-ncs rounded-lg flex items-center justify-center text-white flex-shrink-0">
                        <IconKey />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-delft-blue truncate">{key.name}</h3>
                          <span className={`px-2 py-0.5 text-xs font-medium rounded-full flex-shrink-0 ${
                            key.is_revoked 
                              ? 'bg-red-100 text-red-700' 
                              : 'bg-green-100 text-green-700'
                          }`}>
                            {key.is_revoked ? 'Revoked' : 'Active'}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          Created {new Date(key.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                          {key.last_used_at && ` • Last used ${new Date(key.last_used_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`}
                        </p>
                      </div>
                      <div className="text-muted-foreground group-hover:text-blue-ncs transition-colors">
                        <IconArrowRight />
                      </div>
                    </Link>
                  ))}
                  {apiKeys.length > 3 && (
                    <Link href="/api-keys" className="block">
                      <button className="w-full py-3 text-sm font-medium text-blue-ncs hover:text-delft-blue transition-colors">
                        View all {apiKeys.length} keys →
                      </button>
                    </Link>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions Sidebar */}
        <div className="space-y-4">
          {/* Getting Started Card */}
          <div className="bg-gradient-to-br from-delft-blue to-blue-ncs rounded-xl p-6 text-white">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                <IconShield />
              </div>
              <h3 className="font-bold text-lg">Getting Started</h3>
            </div>
            <ul className="space-y-3 text-sm">
              <li className="flex items-center gap-3">
                <span className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center text-xs font-bold">1</span>
                <span className="text-white/90">Generate an API key</span>
              </li>
              <li className="flex items-center gap-3">
                <span className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center text-xs font-bold">2</span>
                <span className="text-white/90">Install our SDK</span>
              </li>
              <li className="flex items-center gap-3">
                <span className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center text-xs font-bold">3</span>
                <span className="text-white/90">Start signing content</span>
              </li>
            </ul>
            <a href="https://docs.encypherai.com/quickstart" target="_blank" rel="noopener noreferrer">
              <button className="w-full mt-5 py-2.5 bg-white text-delft-blue font-medium rounded-lg hover:bg-columbia-blue transition-colors text-sm">
                View Quickstart Guide
              </button>
            </a>
          </div>

          {/* Quick Links */}
          <div className="bg-white rounded-xl border border-border p-5">
            <h3 className="font-bold text-delft-blue mb-4">Quick Links</h3>
            <div className="space-y-2">
              <Link href="/analytics" className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted transition-colors group">
                <div className="w-9 h-9 bg-blue-ncs/10 rounded-lg flex items-center justify-center text-blue-ncs">
                  <IconChart />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-delft-blue text-sm">Analytics</p>
                  <p className="text-xs text-muted-foreground">View usage metrics</p>
                </div>
                <IconArrowRight />
              </Link>
              
              <Link href="/settings" className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted transition-colors group">
                <div className="w-9 h-9 bg-delft-blue/10 rounded-lg flex items-center justify-center text-delft-blue">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="font-medium text-delft-blue text-sm">Settings</p>
                  <p className="text-xs text-muted-foreground">Account preferences</p>
                </div>
                <IconArrowRight />
              </Link>

              <a href="https://docs.encypherai.com" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted transition-colors group">
                <div className="w-9 h-9 bg-columbia-blue/30 rounded-lg flex items-center justify-center text-delft-blue">
                  <IconBook />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-delft-blue text-sm">Documentation</p>
                  <p className="text-xs text-muted-foreground">API reference & guides</p>
                </div>
                <IconArrowRight />
              </a>
            </div>
          </div>

          {/* C2PA Badge */}
          <div className="bg-gradient-to-r from-columbia-blue/20 to-blue-ncs/10 rounded-xl p-5 border border-columbia-blue/30">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shadow-sm">
                <IconShield />
              </div>
              <div>
                <p className="font-bold text-delft-blue text-sm">C2PA Compliant</p>
                <p className="text-xs text-muted-foreground">Industry standard</p>
              </div>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Your content is authenticated using the C2PA text provenance standard, co-developed with Google, Adobe, and Microsoft.
            </p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
