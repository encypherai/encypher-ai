'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { toast } from 'sonner';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Badge,
  Input,
  type BadgeProps,
} from '@encypher/design-system';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../components/ui/tabs';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { EmptyState } from '../../components/ui/empty-state';
import apiClient from '../../lib/api';
import { downloadCsv } from '../../lib/exportCsv';
import type {
  RightsProfile,
  RightsTier,
  RightsTemplate,
  FormalNotice,
  LicensingRequest,
  LicensingAgreement,
  CrawlerSummaryEntry,
  ContentDiscoveryItem,
  DomainAlertItem,
  DomainSummaryItem,
  DetectionSummary,
  RightsProfileVersion,
} from '../../lib/api';

// ── Tier config ──────────────────────────────────────────────────────────────

const TIER_META = {
  bronze: {
    label: 'Bronze — Scraping / Crawling',
    color: 'bg-amber-50 border-amber-200 dark:bg-amber-950/30 dark:border-amber-800',
    badge: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
    dot: 'bg-amber-500',
    description: 'Controls broad read-only access: search indexing, price comparisons, web archiving.',
  },
  silver: {
    label: 'Silver — RAG / Retrieval',
    color: 'bg-slate-50 border-slate-200 dark:bg-slate-800/40 dark:border-slate-700',
    badge: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
    dot: 'bg-slate-400',
    description: 'Controls AI-powered search and retrieval-augmented generation (RAG) pipelines.',
  },
  gold: {
    label: 'Gold — Training / Fine-tuning',
    color: 'bg-yellow-50 border-yellow-200 dark:bg-yellow-950/30 dark:border-yellow-800',
    badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    dot: 'bg-yellow-500',
    description: 'Controls use of your content for AI model training and fine-tuning.',
  },
} as const;

type TierKey = 'bronze' | 'silver' | 'gold';

// ── Types ─────────────────────────────────────────────────────────────────────

type BadgeVariant = NonNullable<BadgeProps['variant']>;

// ── Helpers ──────────────────────────────────────────────────────────────────

function tierBadgeVariant(tier: string): BadgeVariant {
  if (tier === 'gold') return 'warning';
  if (tier === 'silver') return 'secondary';
  return 'default';
}

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function StatusBadge({ status }: { status: string }) {
  const variantMap: Record<string, BadgeVariant> = {
    delivered: 'success',
    pending: 'warning',
    draft: 'secondary',
    created: 'secondary',
    approved: 'success',
    rejected: 'destructive',
    active: 'primary',
    expired: 'secondary',
  };
  const variant: BadgeVariant = variantMap[status?.toLowerCase()] ?? 'secondary';
  return <Badge variant={variant}>{status}</Badge>;
}

// ── Tier display card ─────────────────────────────────────────────────────────

function TierCard({ tierKey, tier }: { tierKey: TierKey; tier?: RightsTier | null }) {
  const meta = TIER_META[tierKey];
  const permitted = tier?.permissions?.allowed !== false;

  return (
    <div className={`rounded-xl border p-5 ${meta.color}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 mt-0.5 ${meta.dot}`} />
          <span className="font-semibold text-sm text-slate-900 dark:text-slate-100">{meta.label}</span>
        </div>
        <Badge variant={permitted ? 'success' : 'secondary'}>
          {permitted ? 'Permitted' : 'Not Permitted'}
        </Badge>
      </div>
      <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">{meta.description}</p>
      {tier ? (
        <dl className="space-y-1 text-xs">
          {tier.usage_type && (
            <div className="flex gap-2">
              <dt className="text-slate-400 w-28 flex-shrink-0">Usage type</dt>
              <dd className="text-slate-700 dark:text-slate-300 font-mono">{tier.usage_type}</dd>
            </div>
          )}
          {tier.permissions?.requires_license && (
            <div className="flex gap-2">
              <dt className="text-slate-400 w-28 flex-shrink-0">Requires license</dt>
              <dd className="text-slate-700 dark:text-slate-300">Yes</dd>
            </div>
          )}
          {tier.permissions?.license_url && (
            <div className="flex gap-2">
              <dt className="text-slate-400 w-28 flex-shrink-0">License URL</dt>
              <dd className="text-slate-700 dark:text-slate-300 truncate max-w-xs">
                <a href={tier.permissions.license_url} target="_blank" rel="noopener noreferrer"
                  className="text-blue-600 dark:text-blue-400 hover:underline">
                  {tier.permissions.license_url}
                </a>
              </dd>
            </div>
          )}
          {tier.attribution?.required && (
            <div className="flex gap-2">
              <dt className="text-slate-400 w-28 flex-shrink-0">Attribution</dt>
              <dd className="text-slate-700 dark:text-slate-300">Required</dd>
            </div>
          )}
          {tier.contact_for_licensing && (
            <div className="flex gap-2">
              <dt className="text-slate-400 w-28 flex-shrink-0">Contact</dt>
              <dd className="text-slate-700 dark:text-slate-300">{tier.contact_for_licensing}</dd>
            </div>
          )}
          {tier.description && (
            <div className="flex gap-2">
              <dt className="text-slate-400 w-28 flex-shrink-0">Notes</dt>
              <dd className="text-slate-700 dark:text-slate-300 italic">{tier.description}</dd>
            </div>
          )}
        </dl>
      ) : (
        <p className="text-xs text-slate-400 italic">No terms set — inherits platform defaults.</p>
      )}
    </div>
  );
}

// ── Profile tab ───────────────────────────────────────────────────────────────

function ProfileTab({ accessToken }: { accessToken: string }) {
  const queryClient = useQueryClient();
  const [showTemplates, setShowTemplates] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  const historyQuery = useQuery({
    queryKey: ['rights-profile-history'],
    queryFn: () => apiClient.getRightsProfileHistory(accessToken),
    enabled: Boolean(accessToken) && showHistory,
  });

  const profileQuery = useQuery({
    queryKey: ['rights-profile'],
    queryFn: () => apiClient.getRightsProfile(accessToken),
    enabled: Boolean(accessToken),
  });

  const templatesQuery = useQuery({
    queryKey: ['rights-templates'],
    queryFn: () => apiClient.getRightsTemplates(accessToken),
    enabled: Boolean(accessToken) && showTemplates,
  });

  const applyTemplateMutation = useMutation({
    mutationFn: (templateId: string) => apiClient.applyRightsTemplate(accessToken, templateId),
    onSuccess: () => {
      toast.success('Template applied — profile updated.');
      queryClient.invalidateQueries({ queryKey: ['rights-profile'] });
      setShowTemplates(false);
    },
    onError: () => toast.error('Failed to apply template.'),
  });

  const profile = profileQuery.data;
  const hasProfile = Boolean(profile?.bronze_tier || profile?.silver_tier || profile?.gold_tier);

  return (
    <div className="space-y-6">
      {/* Header row */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Rights Profile</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Define how your content may be used across AI use cases. Each signed document embeds a
            <code className="mx-1 text-xs font-mono bg-slate-100 dark:bg-slate-700 px-1 rounded">
              rights_resolution_url
            </code>
            that resolves to these terms.
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowTemplates(!showTemplates)}
          >
            {showTemplates ? 'Hide templates' : 'Apply template'}
          </Button>
          <a
            href="/docs/publisher-integration"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            Guide
          </a>
        </div>
      </div>

      {/* Template picker */}
      {showTemplates && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Choose a template</CardTitle>
            <CardDescription>Start from a preset and customise via API.</CardDescription>
          </CardHeader>
          <CardContent>
            {templatesQuery.isLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-14 bg-muted rounded-lg animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="grid gap-3 sm:grid-cols-2">
                {(templatesQuery.data ?? []).map((tpl: RightsTemplate) => (
                  <Button
                    key={tpl.id}
                    variant="outline"
                    onClick={() => applyTemplateMutation.mutate(tpl.id)}
                    disabled={applyTemplateMutation.isPending}
                    className="h-auto text-left rounded-xl p-4 flex-col items-start hover:border-[#2A87C4] hover:bg-blue-50/40 dark:hover:bg-blue-950/20 group"
                  >
                    <p className="font-medium text-sm text-slate-900 dark:text-slate-100 group-hover:text-[#2A87C4]">
                      {tpl.name}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{tpl.description}</p>
                  </Button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Status strip */}
      {profileQuery.isLoading ? (
        <div className="h-16 bg-muted rounded-xl animate-pulse" />
      ) : hasProfile ? (
        <div className="flex items-center gap-3 rounded-xl bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 px-5 py-3">
          <svg className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          <div className="min-w-0">
            <p className="text-sm font-medium text-green-800 dark:text-green-300">
              Active rights profile — version {profile?.profile_version ?? 1}
            </p>
            <p className="text-xs text-green-600 dark:text-green-400">
              Last updated {formatDate(profile?.effective_date ?? profile?.created_at)}
              {profile?.contact_email && ` · ${profile.contact_email}`}
            </p>
          </div>
          {profile?.notice_endpoint && (
            <a
              href={profile.notice_endpoint}
              target="_blank"
              rel="noopener noreferrer"
              className="ml-auto text-xs text-green-700 dark:text-green-400 hover:underline flex-shrink-0"
            >
              Public link ↗
            </a>
          )}
        </div>
      ) : (
        <div className="flex items-center gap-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 px-5 py-3">
          <svg className="w-5 h-5 text-amber-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p className="text-sm text-amber-800 dark:text-amber-300">
            No rights profile set. Apply a template or use the API to define your licensing terms.
          </p>
        </div>
      )}

      {/* Tier cards */}
      <div className="grid gap-4 lg:grid-cols-3">
        {(['bronze', 'silver', 'gold'] as TierKey[]).map(key => (
          <TierCard key={key} tierKey={key} tier={(profile as RightsProfile | null | undefined)?.[`${key}_tier` as keyof RightsProfile] as RightsTier | null | undefined} />
        ))}
      </div>

      {/* Public endpoints reference */}
      {hasProfile && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-semibold">Public discovery endpoints</CardTitle>
            <CardDescription className="text-xs">
              These unauthenticated URLs let any system or publisher discover your terms programmatically.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {[
                { label: 'Machine-readable (JSON)', path: `/api/v1/public/rights/organization/${profile?.organization_id}` },
                { label: 'W3C ODRL', path: `/api/v1/public/rights/organization/${profile?.organization_id}` },
                { label: 'RSL 1.0 XML', path: `/api/v1/public/rights/organization/${profile?.organization_id}/rsl` },
                { label: 'robots.txt additions', path: `/api/v1/public/rights/organization/${profile?.organization_id}/robots-txt` },
              ].map(item => (
                <div key={item.label} className="flex items-center gap-3 text-xs">
                  <span className="w-40 flex-shrink-0 text-slate-500">{item.label}</span>
                  <code className="flex-1 font-mono bg-slate-50 dark:bg-slate-800 px-2 py-1 rounded text-slate-700 dark:text-slate-300 truncate">
                    {item.path}
                  </code>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Version history */}
      {hasProfile && (
        <div className="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
          <Button
            variant="ghost"
            onClick={() => setShowHistory(!showHistory)}
            className="w-full flex items-center justify-between px-5 py-3 text-sm font-medium rounded-none"
          >
            <span>Version history</span>
            <svg className={`w-4 h-4 transition-transform ${showHistory ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </Button>
          {showHistory && (
            <div className="px-5 pb-4 border-t border-slate-100 dark:border-slate-800">
              {historyQuery.isLoading ? (
                <div className="space-y-2 pt-3">
                  {[1, 2, 3].map(i => <div key={i} className="h-8 bg-muted rounded animate-pulse" />)}
                </div>
              ) : (historyQuery.data ?? []).length === 0 ? (
                <div className="pt-3">
                  <EmptyState
                    icon={
                      <svg className="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    }
                    title="No version history yet"
                    description="Profile versions will appear here each time you update your rights terms."
                  />
                </div>
              ) : (
                <div className="mt-3 space-y-2">
                  {(historyQuery.data ?? []).map((version: RightsProfileVersion) => (
                    <div key={version.id} className="flex items-start gap-3 text-xs">
                      <div className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="font-medium text-blue-700 dark:text-blue-300">{version.profile_version}</span>
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-slate-700 dark:text-slate-300 font-medium">
                          Version {version.profile_version}
                          <span className="font-normal text-slate-400 ml-2">{formatDate(version.effective_date ?? version.created_at)}</span>
                        </p>
                        {version.change_summary && (
                          <p className="text-slate-500 dark:text-slate-400 mt-0.5">{version.change_summary}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

  // ── Analytics tab ─────────────────────────────────────────────────────────────

function AnalyticsTab({ accessToken }: { accessToken: string }) {
  const queryClient = useQueryClient();
  const [days, setDays] = useState<'7' | '30' | '90'>('30');
  const [externalOnly, setExternalOnly] = useState(false);

  const detectionsQuery = useQuery({
    queryKey: ['rights-detections', days],
    queryFn: () => apiClient.getDetectionAnalytics(accessToken, parseInt(days, 10)),
    enabled: Boolean(accessToken),
  });

  const crawlersQuery = useQuery({
    queryKey: ['rights-crawlers', days],
    queryFn: () => apiClient.getCrawlerAnalytics(accessToken, parseInt(days, 10)),
    enabled: Boolean(accessToken),
  });

  const discoveryEventsQuery = useQuery({
    queryKey: ['rights-discovery-events', days, externalOnly],
    queryFn: () => apiClient.getDiscoveryEvents(accessToken, { days: parseInt(days, 10), externalOnly, limit: 50, offset: 0 }),
    enabled: Boolean(accessToken),
  });

  const discoveryDomainsQuery = useQuery({
    queryKey: ['rights-discovery-domains', externalOnly],
    queryFn: () => apiClient.getDiscoveryDomains(accessToken, { externalOnly }),
    enabled: Boolean(accessToken),
  });

  const discoveryAlertsQuery = useQuery({
    queryKey: ['rights-discovery-alerts'],
    queryFn: () => apiClient.getDiscoveryAlerts(accessToken),
    enabled: Boolean(accessToken),
  });

  const acknowledgeAlertMutation = useMutation({
    mutationFn: (alertId: string) => apiClient.acknowledgeDiscoveryAlert(accessToken, alertId),
    onSuccess: () => {
      toast.success('Alert acknowledged.');
      queryClient.invalidateQueries({ queryKey: ['rights-discovery-alerts'] });
      queryClient.invalidateQueries({ queryKey: ['rights-discovery-domains'] });
    },
    onError: () => toast.error('Failed to acknowledge alert.'),
  });

  const crawlers = crawlersQuery.data?.crawlers ?? [];
  const detectionSummary = detectionsQuery.data;
  const discoveryEvents = discoveryEventsQuery.data?.data ?? [];
  const discoveryDomains = discoveryDomainsQuery.data?.data ?? [];
  const discoveryAlerts = discoveryAlertsQuery.data?.data ?? [];

  const exportDiscoveries = () => {
    if (discoveryEvents.length === 0) {
      toast.error('No discovery events to export.');
      return;
    }
    downloadCsv(
      discoveryEvents.map((item: ContentDiscoveryItem) => ({
        page_url: item.page_url,
        page_domain: item.page_domain,
        page_title: item.page_title ?? '',
        signer_name: item.signer_name ?? '',
        document_id: item.document_id ?? '',
        original_domain: item.original_domain ?? '',
        verification_status: item.verification_status ?? '',
        marker_type: item.marker_type ?? '',
        is_external_domain: item.is_external_domain ? 'yes' : 'no',
        discovered_at: item.discovered_at,
      })),
      {
        filename: `encypher-content-discoveries-${new Date().toISOString().split('T')[0]}`,
        headers: ['page_url', 'page_domain', 'page_title', 'signer_name', 'document_id', 'original_domain', 'verification_status', 'marker_type', 'is_external_domain', 'discovered_at'],
      }
    );
    toast.success('Discovery events exported.');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Content Access Analytics</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Phone-home telemetry and owner-visible discovery events when signed content is verified on any webpage.
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <div className="inline-flex rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
            {(['7', '30', '90'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setDays(range)}
                className={`px-3 py-1.5 text-xs font-medium transition-colors ${days === range ? 'bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900' : 'bg-white text-slate-600 hover:bg-slate-50 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800'}`}
              >
                {range}d
              </button>
            ))}
          </div>
          <Button variant={externalOnly ? 'primary' : 'outline'} size="sm" onClick={() => setExternalOnly(v => !v)}>
            {externalOnly ? 'External only' : 'All domains'}
          </Button>
          <Button variant="outline" size="sm" onClick={exportDiscoveries}>
            Export CSV
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardContent className="pt-5">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Total detections</p>
            <p className="text-3xl font-bold text-slate-900 dark:text-slate-100">
              {detectionsQuery.isLoading ? '—' : (detectionSummary?.total_events ?? 0).toLocaleString()}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Discovery events</p>
            <p className="text-3xl font-bold text-slate-900 dark:text-slate-100">
              {discoveryEventsQuery.isLoading ? '—' : (discoveryEventsQuery.data?.total ?? 0).toLocaleString()}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">External domains</p>
            <p className="text-3xl font-bold text-amber-600 dark:text-amber-400">
              {discoveryDomainsQuery.isLoading ? '—' : discoveryDomains.filter((item: DomainSummaryItem) => !item.is_owned_domain).length.toLocaleString()}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Open alerts</p>
            <p className="text-3xl font-bold text-red-600 dark:text-red-400">
              {discoveryAlertsQuery.isLoading ? '—' : discoveryAlerts.length.toLocaleString()}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Rights acknowledged</p>
            <p className="text-3xl font-bold text-green-600 dark:text-green-400">
              {detectionsQuery.isLoading ? '—' : (detectionSummary?.rights_acknowledged_count ?? 0).toLocaleString()}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">External discovery alerts</CardTitle>
          <CardDescription>New non-owned domains where your signed content has been found.</CardDescription>
        </CardHeader>
        <CardContent>
          {discoveryAlertsQuery.isLoading ? (
            <div className="space-y-2">{[1, 2].map(i => <div key={i} className="h-12 bg-muted rounded animate-pulse" />)}</div>
          ) : discoveryAlerts.length === 0 ? (
            <EmptyState
              icon={
                <svg className="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              }
              title="No open alerts"
              description="You will be notified here when signed content is found on an external domain you do not own."
            />
          ) : (
            <div className="space-y-3">
              {discoveryAlerts.map((alert: DomainAlertItem) => (
                <div key={alert.id} className="flex items-center justify-between gap-3 rounded-xl border border-red-200 dark:border-red-900/40 bg-red-50 dark:bg-red-950/20 p-4">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{alert.page_domain}</p>
                    <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
                      {alert.discovery_count.toLocaleString()} discoveries · first seen {formatDate(alert.first_seen_at)} · last seen {formatDate(alert.last_seen_at)}
                    </p>
                  </div>
                  <Button size="sm" variant="outline" onClick={() => acknowledgeAlertMutation.mutate(alert.id)} disabled={acknowledgeAlertMutation.isPending}>
                    Acknowledge
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Detection summary</CardTitle>
          <CardDescription>Aggregate breakdown over the last {detectionSummary?.period_days ?? parseInt(days, 10)} days.</CardDescription>
        </CardHeader>
        <CardContent>
          {detectionsQuery.isLoading ? (
            <div className="space-y-2">{[1, 2, 3].map(i => <div key={i} className="h-10 bg-muted rounded animate-pulse" />)}</div>
          ) : !detectionSummary || detectionSummary.total_events === 0 ? (
            <EmptyState
              icon={
                <svg className="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              }
              title="No detections yet"
              description="Detection events appear once your signed content is verified or accessed by a crawler or publisher integration."
            />
          ) : (
            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <p className="text-xs font-medium text-slate-500 mb-2">By source</p>
                <div className="space-y-1">
                  {Object.entries(detectionSummary.by_source).map(([source, count]) => (
                    <div key={source} className="flex justify-between text-xs">
                      <span className="font-mono text-slate-600 dark:text-slate-400">{source}</span>
                      <span className="font-medium text-slate-800 dark:text-slate-200">{(count as number).toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-xs font-medium text-slate-500 mb-2">By category</p>
                <div className="space-y-1">
                  {Object.entries(detectionSummary.by_category).map(([cat, count]) => (
                    <div key={cat} className="flex justify-between text-xs">
                      <span className="font-mono text-slate-600 dark:text-slate-400">{cat}</span>
                      <span className="font-medium text-slate-800 dark:text-slate-200">{(count as number).toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-xs font-medium text-slate-500 mb-2">Integrity</p>
                <div className="space-y-1">
                  {Object.entries(detectionSummary.by_integrity_status ?? {}).map(([status, count]) => (
                    <div key={status} className="flex justify-between text-xs">
                      <span className="font-mono text-slate-600 dark:text-slate-400">{status}</span>
                      <span className="font-medium text-slate-800 dark:text-slate-200">{(count as number).toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Discovery domains</CardTitle>
          <CardDescription>Where your signed content has been found, grouped by domain.</CardDescription>
        </CardHeader>
        <CardContent>
          {discoveryDomainsQuery.isLoading ? (
            <div className="space-y-2">{[1, 2, 3].map(i => <div key={i} className="h-10 bg-muted rounded animate-pulse" />)}</div>
          ) : discoveryDomains.length === 0 ? (
            <EmptyState
              icon={
                <svg className="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                </svg>
              }
              title="No domains discovered yet"
              description="Domains where your signed content is found will be grouped and listed here."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-700">
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Domain</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Owned</th>
                    <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">Discoveries</th>
                    <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">First seen</th>
                    <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">Last seen</th>
                  </tr>
                </thead>
                <tbody>
                  {discoveryDomains.map((domain: DomainSummaryItem) => (
                    <tr key={domain.id} className="border-b border-slate-50 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                      <td className="py-2.5 px-3 font-mono text-xs text-slate-700 dark:text-slate-300">{domain.page_domain}</td>
                      <td className="py-2.5 px-3">
                        <Badge variant="secondary" className={domain.is_owned_domain ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200'}>
                          {domain.is_owned_domain ? 'Owned' : 'External'}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 text-right font-medium text-slate-800 dark:text-slate-200">{domain.discovery_count.toLocaleString()}</td>
                      <td className="py-2.5 px-3 text-right text-slate-500 text-xs">{formatDate(domain.first_seen_at)}</td>
                      <td className="py-2.5 px-3 text-right text-slate-500 text-xs">{formatDate(domain.last_seen_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Raw discovery events</CardTitle>
          <CardDescription>Evidence-quality rows showing where and when your signed content was found.</CardDescription>
        </CardHeader>
        <CardContent>
          {discoveryEventsQuery.isLoading ? (
            <div className="space-y-2">{[1, 2, 3, 4].map(i => <div key={i} className="h-10 bg-muted rounded animate-pulse" />)}</div>
          ) : discoveryEvents.length === 0 ? (
            <EmptyState
              icon={
                <svg className="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
              }
              title="No discovery events recorded"
              description="Each time your signed content is verified on a webpage, the event is logged here as evidence-quality provenance data."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-700">
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Found URL</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Status</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Document</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Original domain</th>
                    <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">Discovered</th>
                  </tr>
                </thead>
                <tbody>
                  {discoveryEvents.map((event: ContentDiscoveryItem) => (
                    <tr key={event.id} className="border-b border-slate-50 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 align-top">
                      <td className="py-2.5 px-3 text-xs text-slate-600 dark:text-slate-400 max-w-sm">
                        <div className="space-y-1">
                          <a href={event.page_url} target="_blank" rel="noopener noreferrer" className="font-mono text-blue-600 dark:text-blue-400 hover:underline break-all">
                            {event.page_url}
                          </a>
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-slate-500">{event.page_domain}</span>
                            {event.is_external_domain && (
                              <Badge variant="secondary" className="bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">External</Badge>
                            )}
                          </div>
                          {event.page_title && <p className="text-slate-500 line-clamp-2">{event.page_title}</p>}
                        </div>
                      </td>
                      <td className="py-2.5 px-3 text-xs">
                        <div className="space-y-1">
                          <Badge variant="secondary" className={event.verified ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}>
                            {event.verification_status ?? (event.verified ? 'verified' : 'invalid')}
                          </Badge>
                          {event.marker_type && <p className="font-mono text-slate-500">{event.marker_type}</p>}
                        </div>
                      </td>
                      <td className="py-2.5 px-3 text-xs text-slate-600 dark:text-slate-400">
                        <div className="space-y-1">
                          <p>{event.document_id ?? '—'}</p>
                          <p>{event.signer_name ?? '—'}</p>
                        </div>
                      </td>
                      <td className="py-2.5 px-3 text-xs text-slate-600 dark:text-slate-400">{event.original_domain ?? '—'}</td>
                      <td className="py-2.5 px-3 text-right text-xs text-slate-500">{formatDate(event.discovered_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Crawler activity</CardTitle>
          <CardDescription>Systems that have accessed your signed content.</CardDescription>
        </CardHeader>
        <CardContent>
          {crawlersQuery.isLoading ? (
            <div className="space-y-2">{[1, 2, 3, 4].map(i => <div key={i} className="h-10 bg-muted rounded animate-pulse" />)}</div>
          ) : crawlers.length === 0 ? (
            <EmptyState
              icon={
                <svg className="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              }
              title="No crawler activity yet"
              description="AI crawlers and retrieval systems that access your signed content will be identified and logged here."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-700">
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Crawler</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Company</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">RSL</th>
                    <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">Events</th>
                    <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">Last seen</th>
                  </tr>
                </thead>
                <tbody>
                  {crawlers.map((c: CrawlerSummaryEntry) => (
                    <tr key={c.crawler_name} className="border-b border-slate-50 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                      <td className="py-2.5 px-3 font-mono text-xs text-slate-700 dark:text-slate-300">{c.crawler_name}</td>
                      <td className="py-2.5 px-3 text-slate-600 dark:text-slate-400">{c.operator_org ?? c.company ?? '—'}</td>
                      <td className="py-2.5 px-3">
                        {c.respects_rsl ? (
                          <span className="inline-flex items-center gap-1 text-xs text-green-700 dark:text-green-400">
                            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>
                            Yes
                          </span>
                        ) : (
                          <span className="text-xs text-slate-400">—</span>
                        )}
                      </td>
                      <td className="py-2.5 px-3 text-right font-medium text-slate-800 dark:text-slate-200">{c.total_events.toLocaleString()}</td>
                      <td className="py-2.5 px-3 text-right text-slate-500 text-xs">{formatDate(c.last_seen)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ── Notices tab ───────────────────────────────────────────────────────────────

function NoticesTab({ accessToken }: { accessToken: string }) {
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [evidenceNoticeId, setEvidenceNoticeId] = useState<string | null>(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [form, setForm] = useState({
    recipient_entity: '',
    recipient_contact: '',
    violation_type: 'unauthorized_training',
    notice_text: '',
  });

  const evidenceQuery = useQuery({
    queryKey: ['notice-evidence', evidenceNoticeId],
    queryFn: () => apiClient.getNoticeEvidence(accessToken, evidenceNoticeId!),
    enabled: Boolean(accessToken) && Boolean(evidenceNoticeId),
  });

  const noticesQuery = useQuery({
    queryKey: ['rights-notices'],
    queryFn: () => apiClient.listNotices(accessToken),
    enabled: Boolean(accessToken),
  });

  const createMutation = useMutation({
    mutationFn: () => apiClient.createNotice(accessToken, form),
    onSuccess: () => {
      toast.success('Formal notice created.');
      queryClient.invalidateQueries({ queryKey: ['rights-notices'] });
      setShowCreate(false);
    },
    onError: () => toast.error('Failed to create notice.'),
  });

  const deliverMutation = useMutation({
    mutationFn: (noticeId: string) => apiClient.deliverNotice(accessToken, noticeId),
    onSuccess: () => {
      toast.success('Notice delivered.');
      queryClient.invalidateQueries({ queryKey: ['rights-notices'] });
    },
    onError: () => toast.error('Delivery failed.'),
  });

  const notices = noticesQuery.data ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Formal Notices</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Cryptographically-provable notices that eliminate the &ldquo;innocent infringement&rdquo; defense.
            Each notice is immutable with a tamper-evident evidence chain.
          </p>
        </div>
        <Button size="sm" onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? 'Cancel' : '+ New notice'}
        </Button>
      </div>

      {showCreate && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Create formal notice</CardTitle>
            <CardDescription>Once created, the notice is immutable. Deliver it to generate a court-ready evidence package.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300">Recipient entity *</label>
                  <Input
                    placeholder="AI Company Inc."
                    value={form.recipient_entity}
                    onChange={e => setForm(f => ({ ...f, recipient_entity: e.target.value }))}
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300">Recipient contact</label>
                  <Input
                    placeholder="legal@example.com"
                    value={form.recipient_contact}
                    onChange={e => setForm(f => ({ ...f, recipient_contact: e.target.value }))}
                  />
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-700 dark:text-slate-300">Violation type</label>
                <select
                  value={form.violation_type}
                  onChange={e => setForm(f => ({ ...f, violation_type: e.target.value }))}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="unauthorized_training">Unauthorized training</option>
                  <option value="unauthorized_scraping">Unauthorized scraping</option>
                  <option value="unauthorized_rag">Unauthorized RAG / retrieval</option>
                  <option value="license_violation">License violation</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-700 dark:text-slate-300">Notice text *</label>
                <textarea
                  rows={4}
                  placeholder="Describe the violation and your rights claim..."
                  value={form.notice_text}
                  onChange={e => setForm(f => ({ ...f, notice_text: e.target.value }))}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 resize-y"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" size="sm" onClick={() => setShowCreate(false)}>Cancel</Button>
                <Button
                  size="sm"
                  onClick={() => createMutation.mutate()}
                  disabled={createMutation.isPending || !form.recipient_entity || !form.notice_text}
                >
                  {createMutation.isPending ? 'Creating…' : 'Create notice'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="pt-4">
          {noticesQuery.isLoading ? (
            <div className="space-y-3">{[1, 2, 3].map(i => <div key={i} className="h-14 bg-muted rounded-lg animate-pulse" />)}</div>
          ) : notices.length === 0 ? (
            <EmptyState
              icon={
                <svg className="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              }
              title="No formal notices issued"
              description="Send a cryptographically-provable notice to any party using your content without permission. Each notice creates a tamper-evident evidence chain."
              actionLabel="Create your first notice"
              onAction={() => setShowCreate(true)}
            />
          ) : (
            <div className="divide-y divide-slate-100 dark:divide-slate-700">
              {notices.map((notice: FormalNotice) => (
                <div key={notice.id} className="flex items-start justify-between gap-4 py-4 first:pt-0 last:pb-0">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <StatusBadge status={notice.status} />
                      <span className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
                        {notice.recipient_entity ?? 'Unknown recipient'}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">{notice.notice_text}</p>
                    <p className="text-xs text-slate-400 mt-1">
                      Created {formatDate(notice.created_at)}
                      {notice.delivered_at && ` · Delivered ${formatDate(notice.delivered_at)}`}
                      {notice.recipient_contact && ` · ${notice.recipient_contact}`}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {(notice.status === 'created' || notice.status === 'draft') && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => deliverMutation.mutate(notice.id)}
                        disabled={deliverMutation.isPending}
                      >
                        Deliver
                      </Button>
                    )}
                    {notice.status === 'delivered' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setEvidenceNoticeId(evidenceNoticeId === notice.id ? null : notice.id)}
                      >
                        Evidence
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {evidenceNoticeId && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Evidence Package</CardTitle>
              <Button variant="ghost" size="sm" onClick={() => setEvidenceNoticeId(null)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 p-1 h-auto">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </Button>
            </div>
            <CardDescription>Court-ready evidence chain for this notice.</CardDescription>
          </CardHeader>
          <CardContent>
            {evidenceQuery.isLoading ? (
              <div className="space-y-2">{[1, 2, 3].map(i => <div key={i} className="h-8 bg-muted rounded animate-pulse" />)}</div>
            ) : evidenceQuery.error ? (
              <p className="text-sm text-red-500">Failed to load evidence package.</p>
            ) : evidenceQuery.data ? (
              <div className="space-y-4">
                <div className="font-mono text-xs bg-slate-50 dark:bg-slate-800 rounded-lg p-3">
                  <p className="text-slate-500 mb-1">Notice hash (SHA-256)</p>
                  <p className="text-slate-700 dark:text-slate-300 break-all">{evidenceQuery.data.notice?.notice_hash}</p>
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      navigator.clipboard.writeText(JSON.stringify(evidenceQuery.data, null, 2));
                      toast.success('Evidence package copied to clipboard.');
                    }}
                  >
                    Copy as JSON
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    loading={pdfLoading}
                    disabled={pdfLoading}
                    onClick={async () => {
                      if (!evidenceNoticeId) return;
                      setPdfLoading(true);
                      try {
                        await apiClient.downloadEvidencePackagePdf(accessToken, evidenceNoticeId);
                        toast.success('Evidence package downloaded.');
                      } catch {
                        toast.error('Failed to download PDF. Please try again.');
                      } finally {
                        setPdfLoading(false);
                      }
                    }}
                  >
                    {pdfLoading ? 'Generating...' : 'Download PDF'}
                  </Button>
                </div>
              </div>
            ) : null}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// ── Licensing tab ─────────────────────────────────────────────────────────────

function LicensingTab({ accessToken }: { accessToken: string }) {
  const queryClient = useQueryClient();
  const [rejectingId, setRejectingId] = useState<string | null>(null);
  const [rejectMessage, setRejectMessage] = useState('');

  const requestsQuery = useQuery({
    queryKey: ['rights-licensing-requests'],
    queryFn: () => apiClient.listLicensingRequests(accessToken),
    enabled: Boolean(accessToken),
  });

  const agreementsQuery = useQuery({
    queryKey: ['rights-licensing-agreements'],
    queryFn: () => apiClient.listLicensingAgreements(accessToken),
    enabled: Boolean(accessToken),
  });

  const respondMutation = useMutation({
    mutationFn: ({ requestId, action, message }: { requestId: string; action: 'approve' | 'counter' | 'reject'; message?: string }) =>
      apiClient.respondToLicensingRequest(accessToken, requestId, action, { message }),
    onSuccess: (_data, vars) => {
      toast.success(
        vars.action === 'approve' ? 'Request approved — agreement created.' :
        vars.action === 'reject' ? 'Request rejected.' : 'Counter-proposal sent.'
      );
      setRejectingId(null);
      setRejectMessage('');
      queryClient.invalidateQueries({ queryKey: ['rights-licensing-requests'] });
      queryClient.invalidateQueries({ queryKey: ['rights-licensing-agreements'] });
    },
    onError: () => toast.error('Failed to respond to request. Please try again.'),
  });

  const requests = requestsQuery.data ?? [];
  const agreements = agreementsQuery.data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Licensing Transactions</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
          Manage incoming licensing requests and view active agreements.
          Two-track model: Coalition deals (60/40) or Self-service deals (80/20).
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Licensing requests</CardTitle>
          <CardDescription>Inbound requests from parties seeking to license your content.</CardDescription>
        </CardHeader>
        <CardContent>
          {requestsQuery.isLoading ? (
            <div className="space-y-2">{[1, 2].map(i => <div key={i} className="h-12 bg-muted rounded animate-pulse" />)}</div>
          ) : requests.length === 0 ? (
            <EmptyState
              icon={
                <svg className="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              }
              title="No licensing requests yet"
              description="When a party requests permission to use your content, their request will appear here for you to approve, counter, or reject."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-700">
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">From</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Tier</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Status</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Message</th>
                    <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">Date</th>
                    <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {requests.map((req: LicensingRequest) => (
                    <React.Fragment key={req.id}>
                      <tr className="border-b border-slate-50 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                        <td className="py-2.5 px-3 font-mono text-xs text-slate-600 dark:text-slate-400 max-w-[120px] truncate">
                          {req.requester_org_id?.slice(0, 12)}…
                        </td>
                        <td className="py-2.5 px-3">
                          {req.tier && (
                            <Badge variant={tierBadgeVariant(req.tier)}>
                              {req.tier}
                            </Badge>
                          )}
                        </td>
                        <td className="py-2.5 px-3"><StatusBadge status={req.status} /></td>
                        <td className="py-2.5 px-3 text-xs text-slate-500 max-w-[200px] truncate">{(req.requester_info as Record<string, string> | null)?.message ?? '—'}</td>
                        <td className="py-2.5 px-3 text-right text-xs text-slate-500">{formatDate(req.created_at)}</td>
                        <td className="py-2.5 px-3 text-right">
                          {(req.status === 'pending' || req.status === 'countered') ? (
                            <div className="flex items-center justify-end gap-1.5">
                              <Button
                                variant="success"
                                size="sm"
                                onClick={() => respondMutation.mutate({ requestId: req.id, action: 'approve' })}
                                disabled={respondMutation.isPending}
                              >
                                Approve
                              </Button>
                              <Button
                                variant="secondary"
                                size="sm"
                                onClick={() => setRejectingId(rejectingId === req.id ? null : req.id)}
                                disabled={respondMutation.isPending}
                              >
                                Reject
                              </Button>
                            </div>
                          ) : (
                            <span className="text-xs text-slate-400">—</span>
                          )}
                        </td>
                      </tr>
                      {rejectingId === req.id && (
                        <tr key={`${req.id}-reject`} className="bg-red-50 dark:bg-red-950/20">
                          <td colSpan={6} className="px-3 py-3">
                            <div className="flex items-center gap-2">
                              <Input
                                placeholder="Optional rejection message..."
                                value={rejectMessage}
                                onChange={e => setRejectMessage(e.target.value)}
                                className="flex-1 text-sm h-8"
                              />
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={() => respondMutation.mutate({ requestId: req.id, action: 'reject', message: rejectMessage })}
                                disabled={respondMutation.isPending}
                                className="whitespace-nowrap"
                              >
                                Confirm reject
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => { setRejectingId(null); setRejectMessage(''); }}
                              >
                                Cancel
                              </Button>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Active agreements</CardTitle>
          <CardDescription>Approved licensing agreements and their terms.</CardDescription>
        </CardHeader>
        <CardContent>
          {agreementsQuery.isLoading ? (
            <div className="space-y-2">{[1, 2].map(i => <div key={i} className="h-12 bg-muted rounded animate-pulse" />)}</div>
          ) : agreements.length === 0 ? (
            <EmptyState
              icon={
                <svg className="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              }
              title="No active agreements"
              description="Approved licensing agreements will appear here. Approve an incoming request above to create one."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-700">
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Licensee</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Tier</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Status</th>
                    <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">Expires</th>
                  </tr>
                </thead>
                <tbody>
                  {agreements.map((agr: LicensingAgreement) => (
                    <tr key={agr.id} className="border-b border-slate-50 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                      <td className="py-2.5 px-3 text-xs text-slate-600 dark:text-slate-400">
                        {agr.licensee_name || agr.licensee_org_id}
                      </td>
                      <td className="py-2.5 px-3">
                        {agr.tier && (
                          <Badge variant={tierBadgeVariant(agr.tier)}>
                            {agr.tier}
                          </Badge>
                        )}
                      </td>
                      <td className="py-2.5 px-3"><StatusBadge status={agr.status} /></td>
                      <td className="py-2.5 px-3 text-right text-xs text-slate-500">{formatDate(agr.expiry_date)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function RightsPage() {
  const { data: session } = useSession();
  const accessToken = (session?.user as { accessToken?: string })?.accessToken ?? '';

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page header */}
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Rights Management</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Define machine-readable licensing terms, track AI crawler activity, and issue formal notices.
          </p>
        </div>

        <Tabs defaultValue="profile">
          <TabsList className="bg-slate-100 dark:bg-slate-800 p-1 rounded-xl mb-2">
            <TabsTrigger value="profile" className="rounded-lg text-sm">
              Profile
            </TabsTrigger>
            <TabsTrigger value="analytics" className="rounded-lg text-sm">
              Analytics
            </TabsTrigger>
            <TabsTrigger value="notices" className="rounded-lg text-sm">
              Notices
            </TabsTrigger>
            <TabsTrigger value="licensing" className="rounded-lg text-sm">
              Licensing
            </TabsTrigger>
          </TabsList>

          <TabsContent value="profile">
            <ProfileTab accessToken={accessToken} />
          </TabsContent>
          <TabsContent value="analytics">
            <AnalyticsTab accessToken={accessToken} />
          </TabsContent>
          <TabsContent value="notices">
            <NoticesTab accessToken={accessToken} />
          </TabsContent>
          <TabsContent value="licensing">
            <LicensingTab accessToken={accessToken} />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
