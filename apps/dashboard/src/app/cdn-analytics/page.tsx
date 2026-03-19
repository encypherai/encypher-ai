'use client';

import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@encypher/design-system';
import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { useState } from 'react';
import Link from 'next/link';

import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { useOrganization } from '../../contexts/OrganizationContext';
import apiClient from '../../lib/api';
import type { CdnAnalyticsTimelineDay } from '../../lib/api';

// -- Time range options --

type TimeRange = 7 | 30 | 90;

const TIME_RANGES: { label: string; value: TimeRange }[] = [
  { label: '7 days', value: 7 },
  { label: '30 days', value: 30 },
  { label: '90 days', value: 90 },
];

// -- Helpers --

function formatNumber(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K';
  return n.toLocaleString();
}

const dateFormatter = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' });

function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    return dateFormatter.format(date);
  } catch {
    return dateString;
  }
}

function recoverableColor(percent: number): string {
  if (percent >= 80) return 'text-green-600 dark:text-green-400';
  if (percent >= 50) return 'text-yellow-600 dark:text-yellow-400';
  return 'text-red-600 dark:text-red-400';
}

// -- Enterprise gate --

function EnterpriseGate() {
  return (
    <DashboardLayout>
      <div className="flex flex-col items-center justify-center py-24 px-4">
        <div className="w-20 h-20 mb-6 rounded-full bg-blue-ncs/10 flex items-center justify-center">
          <svg className="w-10 h-10 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-foreground mb-2">CDN Provenance Analytics</h2>
        <p className="text-muted-foreground text-center max-w-lg mb-8">
          Track how your images are protected and served through Encypher CDN provenance.
          Monitor signing coverage, request volume, and recoverability across your assets.
        </p>
        <p className="text-sm text-muted-foreground mb-6">
          This feature is available on the Enterprise plan.
        </p>
        <Link href="/billing">
          <Button variant="primary">Upgrade to Enterprise</Button>
        </Link>
      </div>
    </DashboardLayout>
  );
}

// -- Empty state --

function EmptyState() {
  return (
    <div className="text-center py-16">
      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
        <svg className="w-8 h-8 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-foreground mb-2">No CDN Data Yet</h3>
      <p className="text-sm text-muted-foreground max-w-md mx-auto mb-6">
        CDN analytics will appear here once you start serving images through
        Encypher CDN provenance. Set up your CDN integration to get started.
      </p>
      <Link href="/integrations">
        <Button variant="outline">Set Up CDN Integration</Button>
      </Link>
    </div>
  );
}

// -- Summary metric card --

function MetricCard({
  label,
  value,
  description,
  colorClass,
}: {
  label: string;
  value: string;
  description?: string;
  colorClass?: string;
}) {
  return (
    <Card className="border-border">
      <CardContent className="p-5">
        <p className="text-sm font-medium text-muted-foreground">{label}</p>
        <p className={`text-2xl font-bold mt-1 ${colorClass || 'text-foreground'}`}>
          {value}
        </p>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}

// -- CSS bar chart --

function TimelineChart({ data }: { data: CdnAnalyticsTimelineDay[] }) {
  if (data.length === 0) {
    return (
      <p className="text-muted-foreground text-sm text-center py-8">
        No timeline data available for this period.
      </p>
    );
  }

  const maxValue = Math.max(
    ...data.map((d) => Math.max(d.images_signed, d.image_requests)),
    1,
  );

  return (
    <div className="space-y-4">
      {/* Legend */}
      <div className="flex items-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-blue-ncs" />
          <span className="text-muted-foreground">Images Signed</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-columbia-blue" />
          <span className="text-muted-foreground">Image Requests</span>
        </div>
      </div>

      {/* Chart */}
      <div className="overflow-x-auto">
        <div className="flex items-end gap-1 min-w-[400px]" style={{ height: '200px' }}>
          {data.map((day) => {
            const signedHeight = maxValue > 0 ? (day.images_signed / maxValue) * 100 : 0;
            const requestHeight = maxValue > 0 ? (day.image_requests / maxValue) * 100 : 0;
            return (
              <div
                key={day.date}
                className="flex-1 flex items-end gap-px min-w-[8px] group relative"
              >
                {/* Tooltip */}
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                  <div className="bg-popover text-popover-foreground border border-border rounded-md px-3 py-2 text-xs shadow-md whitespace-nowrap">
                    <p className="font-medium">{formatDate(day.date)}</p>
                    <p>Signed: {day.images_signed.toLocaleString()}</p>
                    <p>Requests: {day.image_requests.toLocaleString()}</p>
                  </div>
                </div>
                {/* Bars */}
                <div
                  className="flex-1 bg-blue-ncs rounded-t-sm transition-all duration-200 hover:opacity-80"
                  style={{ height: `${signedHeight}%`, minHeight: day.images_signed > 0 ? '2px' : '0px' }}
                />
                <div
                  className="flex-1 bg-columbia-blue rounded-t-sm transition-all duration-200 hover:opacity-80"
                  style={{ height: `${requestHeight}%`, minHeight: day.image_requests > 0 ? '2px' : '0px' }}
                />
              </div>
            );
          })}
        </div>
        {/* X-axis labels */}
        <div className="flex gap-1 mt-1 min-w-[400px]">
          {data.map((day, i) => {
            // Show labels at intervals to avoid crowding
            const showLabel = data.length <= 14 || i % Math.ceil(data.length / 10) === 0;
            return (
              <div key={day.date} className="flex-1 text-center">
                {showLabel && (
                  <span className="text-[10px] text-muted-foreground">{formatDate(day.date)}</span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// -- Main page --

export default function CdnAnalyticsPage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as Record<string, unknown> | undefined)?.accessToken as string | undefined;
  const { activeOrganization, isLoading: orgLoading } = useOrganization();
  const isEnterprise =
    activeOrganization?.tier === 'enterprise' ||
    activeOrganization?.tier === 'strategic_partner';

  const [timeRange, setTimeRange] = useState<TimeRange>(30);

  const summaryQuery = useQuery({
    queryKey: ['cdn-analytics-summary'],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      return apiClient.getCdnAnalyticsSummary(accessToken);
    },
    enabled: Boolean(accessToken) && isEnterprise,
    staleTime: 60_000,
  });

  const timelineQuery = useQuery({
    queryKey: ['cdn-analytics-timeline', timeRange],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      return apiClient.getCdnAnalyticsTimeline(accessToken, timeRange);
    },
    enabled: Boolean(accessToken) && isEnterprise,
    staleTime: 60_000,
  });

  const isLoading = status === 'loading' || orgLoading;

  // Gate: show upgrade prompt for non-enterprise (after all hooks)
  if (!orgLoading && activeOrganization && !isEnterprise) {
    return <EnterpriseGate />;
  }

  const summary = summaryQuery.data;
  const timeline = timelineQuery.data;
  const hasData = summary && summary.assets_protected > 0;

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-delft-blue dark:text-white">CDN Analytics</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Monitor your CDN image provenance coverage, request volume, and recoverability.
          </p>
        </div>

        {isLoading || summaryQuery.isLoading ? (
          <div className="flex items-center justify-center py-16">
            <div className="flex flex-col items-center gap-3 text-sm text-muted-foreground">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-300 border-t-blue-ncs dark:border-slate-700 dark:border-t-columbia-blue" />
              <span>Loading CDN analytics...</span>
            </div>
          </div>
        ) : summaryQuery.isError ? (
          <Card className="border-border">
            <CardContent className="p-6 text-center">
              <p className="text-muted-foreground">
                Failed to load CDN analytics. Please try again later.
              </p>
            </CardContent>
          </Card>
        ) : !hasData ? (
          <EmptyState />
        ) : (
          <>
            {/* Summary cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard
                label="Assets Protected"
                value={formatNumber(summary.assets_protected)}
                description="Unique images with provenance"
              />
              <MetricCard
                label="Variants Registered"
                value={formatNumber(summary.variants_registered)}
                description="Resized/cropped versions tracked"
              />
              <MetricCard
                label="Image Requests Tracked"
                value={formatNumber(summary.image_requests_tracked)}
                description="Total CDN requests monitored"
              />
              <MetricCard
                label="Recoverable"
                value={`${summary.recoverable_percent.toFixed(1)}%`}
                description="Images with recoverable provenance"
                colorClass={recoverableColor(summary.recoverable_percent)}
              />
            </div>

            {/* Timeline */}
            <Card className="border-border">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Activity Timeline</CardTitle>
                    <CardDescription>
                      Images signed and requests over time
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-1">
                    {TIME_RANGES.map((range) => (
                      <button
                        key={range.value}
                        onClick={() => setTimeRange(range.value)}
                        className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                          timeRange === range.value
                            ? 'bg-blue-ncs text-white'
                            : 'text-muted-foreground hover:bg-muted'
                        }`}
                      >
                        {range.label}
                      </button>
                    ))}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {timelineQuery.isLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="h-6 w-6 animate-spin rounded-full border-2 border-slate-300 border-t-blue-ncs dark:border-slate-700 dark:border-t-columbia-blue" />
                  </div>
                ) : timelineQuery.isError ? (
                  <p className="text-muted-foreground text-sm text-center py-8">
                    Failed to load timeline data.
                  </p>
                ) : (
                  <TimelineChart data={timeline?.data ?? []} />
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
