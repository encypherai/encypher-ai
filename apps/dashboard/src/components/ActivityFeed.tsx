'use client';

import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import Link from 'next/link';
import { Badge, Card, CardHeader, CardTitle, CardContent } from '@encypher/design-system';

interface ActivityItem {
  id: string;
  type: 'api_call' | 'key_created' | 'key_revoked' | 'sign' | 'verify' | 'login' | 'settings_changed';
  description: string;
  timestamp: Date;
  metadata?: {
    status?: number;
    latency_ms?: number;
    endpoint?: string;
    method?: string;
    api_key?: string;
    location?: string;
    request_id?: string;
    region?: string;
  };
}

const activityIcons: Record<ActivityItem['type'], { icon: string; color: string; bg: string }> = {
  api_call: { icon: 'M13 10V3L4 14h7v7l9-11h-7z', color: 'text-blue-600', bg: 'bg-blue-100' },
  key_created: { icon: 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z', color: 'text-green-600', bg: 'bg-green-100' },
  key_revoked: { icon: 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636', color: 'text-red-600', bg: 'bg-red-100' },
  sign: { icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z', color: 'text-emerald-600', bg: 'bg-emerald-100' },
  verify: { icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', color: 'text-purple-600', bg: 'bg-purple-100' },
  login: { icon: 'M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1', color: 'text-slate-600', bg: 'bg-slate-100' },
  settings_changed: { icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z', color: 'text-amber-600', bg: 'bg-amber-100' },
};

function formatTimeAgo(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

function formatLatency(latencyMs?: number): string | null {
  if (!latencyMs && latencyMs !== 0) return null;
  if (latencyMs >= 1000) {
    return `${(latencyMs / 1000).toFixed(2)}s`;
  }
  return `${Math.round(latencyMs)}ms`;
}

function getStatusVariant(status?: number): 'success' | 'warning' | 'destructive' | 'secondary' {
  if (!status) return 'secondary';
  if (status >= 200 && status < 300) return 'success';
  if (status >= 400 && status < 500) return 'warning';
  return 'destructive';
}

// Mock data for demo - in production this would come from an API
const mockActivities: ActivityItem[] = [
  {
    id: '1',
    type: 'api_call',
    description: 'Signing request completed for newsroom article',
    timestamp: new Date(Date.now() - 4 * 60000),
    metadata: {
      status: 201,
      latency_ms: 312,
      endpoint: '/v1/sign',
      method: 'POST',
      api_key: 'prod_newsroom_4f2c',
      location: 'New York, US',
      request_id: 'req_9c12f2d',
    },
  },
  {
    id: '2',
    type: 'verify',
    description: 'Verification checks passed for syndicated content',
    timestamp: new Date(Date.now() - 18 * 60000),
    metadata: {
      status: 200,
      latency_ms: 224,
      endpoint: '/v1/verify',
      method: 'POST',
      api_key: 'prod_newsroom_4f2c',
      location: 'Chicago, US',
      request_id: 'req_7d84e8a',
    },
  },
  {
    id: '3',
    type: 'sign',
    description: 'Batch signing job queued for 120 assets',
    timestamp: new Date(Date.now() - 45 * 60000),
    metadata: {
      status: 202,
      latency_ms: 410,
      endpoint: '/v1/sign/batch',
      method: 'POST',
      api_key: 'studio_batch_21a9',
      region: 'eu-west-1',
    },
  },
  {
    id: '4',
    type: 'api_call',
    description: 'Key rotated after security policy update',
    timestamp: new Date(Date.now() - 2 * 3600000),
    metadata: {
      status: 204,
      latency_ms: 180,
      endpoint: '/v1/keys/rotate',
      method: 'POST',
      api_key: 'prod_keys_37b1',
      location: 'London, UK',
    },
  },
  {
    id: '5',
    type: 'login',
    description: 'Admin login from Chrome on macOS',
    timestamp: new Date(Date.now() - 7 * 3600000),
    metadata: {
      status: 200,
      latency_ms: 96,
      endpoint: '/v1/auth/login',
      method: 'POST',
      location: 'San Francisco, US',
    },
  },
  {
    id: '6',
    type: 'settings_changed',
    description: 'Updated webhook alert thresholds',
    timestamp: new Date(Date.now() - 26 * 3600000),
    metadata: {
      status: 200,
      latency_ms: 184,
      endpoint: '/v1/settings/alerts',
      method: 'PATCH',
      api_key: 'ops_monitor_8d2f',
      region: 'us-east-1',
    },
  },
];

interface ActivityFeedProps {
  limit?: number;
  showHeader?: boolean;
  compact?: boolean;
  title?: string;
}

export function ActivityFeed({
  limit = 5,
  showHeader = true,
  compact = false,
  title = 'Recent Activity',
}: ActivityFeedProps) {
  const { data: session } = useSession();
  const accessToken = (session?.user as Record<string, unknown>)?.accessToken as string | undefined;

  // In production, this would fetch from the API
  const activitiesQuery = useQuery({
    queryKey: ['activity-feed'],
    queryFn: async () => {
      // Mock API call - replace with actual API
      await new Promise(resolve => setTimeout(resolve, 500));
      return mockActivities;
    },
    enabled: Boolean(accessToken),
    refetchOnWindowFocus: false,
  });

  const activities = (activitiesQuery.data ?? []).slice(0, limit);
  const isLoading = activitiesQuery.isLoading;

  if (isLoading) {
    return (
      <Card>
        {showHeader && (
          <CardHeader>
            <CardTitle>{title}</CardTitle>
          </CardHeader>
        )}
        <CardContent className={showHeader ? '' : 'pt-6'}>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-start gap-3 animate-pulse">
                <div className="w-8 h-8 rounded-full bg-slate-200" />
                <div className="flex-1">
                  <div className="h-4 w-3/4 bg-slate-200 rounded mb-2" />
                  <div className="h-3 w-1/4 bg-slate-200 rounded" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (activities.length === 0) {
    return (
      <Card>
        {showHeader && (
          <CardHeader>
            <CardTitle>{title}</CardTitle>
          </CardHeader>
        )}
        <CardContent className={showHeader ? '' : 'pt-6'}>
          <div className="text-center py-8">
            <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-100 flex items-center justify-center">
              <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-sm text-slate-500">No recent activity</p>
            <p className="text-xs text-slate-400 mt-1">Activity will appear here as you use the API</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      {showHeader && (
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>{title}</CardTitle>
          <Link href="/audit-logs" className="text-sm text-blue-ncs hover:underline">
            View all
          </Link>
        </CardHeader>
      )}
      <CardContent className={showHeader ? '' : 'pt-6'}>
        <div className={compact ? 'space-y-2' : 'space-y-4'}>
          {activities.map((activity) => {
            const iconConfig = activityIcons[activity.type];
            const latency = formatLatency(activity.metadata?.latency_ms);
            const endpoint = activity.metadata?.endpoint
              ? `${activity.metadata?.method ?? 'POST'} ${activity.metadata.endpoint}`
              : null;
            const statusVariant = getStatusVariant(activity.metadata?.status);
            const detailItems = [
              { label: 'Endpoint', value: endpoint },
              { label: 'Latency', value: latency },
              { label: 'Status', value: activity.metadata?.status ? String(activity.metadata.status) : null },
              { label: 'Key', value: activity.metadata?.api_key },
              { label: 'Origin', value: activity.metadata?.location },
              { label: 'Region', value: activity.metadata?.region },
              { label: 'Request ID', value: activity.metadata?.request_id },
            ].filter((item) => Boolean(item.value));
            return (
              <div
                key={activity.id}
                className={`flex items-start gap-3 ${compact ? 'py-1' : 'py-2'}`}
              >
                {/* Icon */}
                <div className={`flex-shrink-0 w-8 h-8 rounded-full ${iconConfig.bg} flex items-center justify-center`}>
                  <svg className={`w-4 h-4 ${iconConfig.color}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={iconConfig.icon} />
                  </svg>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className={`text-slate-800 dark:text-slate-100 font-medium ${compact ? 'text-sm' : ''}`}>
                      {activity.description}
                    </p>
                    {activity.type === 'api_call' && (
                      <Badge variant="secondary" size="sm">
                        API Call
                      </Badge>
                    )}
                  </div>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                    <span>{formatTimeAgo(activity.timestamp)}</span>
                    {activity.metadata?.location && <span>• {activity.metadata.location}</span>}
                  </div>
                  {detailItems.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {detailItems.map((item) => (
                        <div
                          key={item.label}
                          className="flex items-center gap-1 rounded-full bg-muted/60 px-2.5 py-1 text-[11px] text-muted-foreground"
                        >
                          <span className="uppercase tracking-wide text-[10px]">{item.label}</span>
                          <span className="font-medium text-slate-700 dark:text-slate-200">
                            {item.value}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Metadata badges */}
                <div className="flex flex-col items-end gap-2">
                  {activity.metadata?.status && (
                    <Badge variant={statusVariant} size="sm">
                      Status {activity.metadata.status}
                    </Badge>
                  )}
                  {latency && (
                    <Badge variant="outline" size="sm">
                      Latency {latency}
                    </Badge>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

export default ActivityFeed;
