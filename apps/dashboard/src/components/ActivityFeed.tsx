'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent } from '@encypher/design-system';

interface ActivityItem {
  id: string;
  type: 'api_call' | 'key_created' | 'key_revoked' | 'sign' | 'verify' | 'login' | 'settings_changed';
  description: string;
  timestamp: Date;
  metadata?: Record<string, string | number>;
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

// Mock data for demo - in production this would come from an API
const mockActivities: ActivityItem[] = [
  { id: '1', type: 'sign', description: 'Signed document via API', timestamp: new Date(Date.now() - 5 * 60000) },
  { id: '2', type: 'verify', description: 'Verified content authenticity', timestamp: new Date(Date.now() - 15 * 60000) },
  { id: '3', type: 'api_call', description: 'API call to /v1/sign endpoint', timestamp: new Date(Date.now() - 30 * 60000), metadata: { status: 200 } },
  { id: '4', type: 'key_created', description: 'Created new API key "Production"', timestamp: new Date(Date.now() - 2 * 3600000) },
  { id: '5', type: 'login', description: 'Logged in from Chrome on Windows', timestamp: new Date(Date.now() - 24 * 3600000) },
];

interface ActivityFeedProps {
  limit?: number;
  showHeader?: boolean;
  compact?: boolean;
}

export function ActivityFeed({ limit = 5, showHeader = true, compact = false }: ActivityFeedProps) {
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
            <CardTitle>Recent Activity</CardTitle>
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
            <CardTitle>Recent Activity</CardTitle>
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
          <CardTitle>Recent Activity</CardTitle>
          <Link href="/audit-logs" className="text-sm text-blue-ncs hover:underline">
            View all
          </Link>
        </CardHeader>
      )}
      <CardContent className={showHeader ? '' : 'pt-6'}>
        <div className={compact ? 'space-y-2' : 'space-y-4'}>
          {activities.map((activity) => {
            const iconConfig = activityIcons[activity.type];
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
                  <p className={`text-slate-700 ${compact ? 'text-sm' : ''}`}>
                    {activity.description}
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {formatTimeAgo(activity.timestamp)}
                  </p>
                </div>

                {/* Metadata badge */}
                {activity.metadata?.status && (
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    activity.metadata.status === 200 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {activity.metadata.status}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

export default ActivityFeed;
