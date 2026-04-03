'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Dialog, DialogContent, DialogHeader, DialogTitle, Button, Badge } from '@encypher/design-system';
import { Download, Filter, ChevronLeft, ChevronRight } from 'lucide-react';

interface UserActivityModalProps {
  userId: string;
  userEmail: string;
  accessToken: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function UserActivityModal({
  userId,
  userEmail,
  accessToken,
  isOpen,
  onClose,
}: UserActivityModalProps) {
  const [days, setDays] = useState(30);
  const [metricType, setMetricType] = useState<string>('');
  const [page, setPage] = useState(0);
  const limit = 50;

  const activityQuery = useQuery({
    queryKey: ['user-activity', userId, days, metricType, page],
    queryFn: async () => {
      return apiClient.getUserActivityLogs(accessToken, userId, {
        days,
        limit,
        offset: page * limit,
        metricType: metricType || undefined,
      });
    },
    enabled: isOpen && Boolean(accessToken) && Boolean(userId),
  });

  const activities = activityQuery.data?.activities ?? [];
  const total = activityQuery.data?.total ?? 0;
  const hasMore = activityQuery.data?.has_more ?? false;
  const totalPages = Math.ceil(total / limit);

  const exportToCSV = () => {
    if (!activities.length) return;

    const headers = ['Timestamp', 'Type', 'Description', 'Endpoint', 'Method', 'Status', 'Latency (ms)'];
    const rows = activities.map((activity) => [
      new Date(activity.timestamp).toLocaleString(),
      activity.type,
      activity.description,
      activity.metadata.endpoint || '',
      activity.metadata.method || '',
      activity.metadata.status || '',
      activity.metadata.latency_ms || '',
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `activity-logs-${userEmail}-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-hidden flex flex-col bg-white dark:bg-slate-900">
        <DialogHeader>
          <DialogTitle>Activity Logs</DialogTitle>
          <p className="text-sm text-muted-foreground">{userEmail}</p>
        </DialogHeader>

        {/* Filters */}
        <div className="flex items-center gap-4 py-4 border-b">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <select
              value={days}
              onChange={(e) => {
                setDays(Number(e.target.value));
                setPage(0);
              }}
              className="text-sm border border-slate-300 dark:border-slate-600 rounded-md px-3 py-1.5 bg-white dark:bg-slate-800"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={metricType}
              onChange={(e) => {
                setMetricType(e.target.value);
                setPage(0);
              }}
              className="text-sm border border-slate-300 dark:border-slate-600 rounded-md px-3 py-1.5 bg-white dark:bg-slate-800"
            >
              <option value="">All Events</option>
              <option value="document_signed">Sign Events</option>
              <option value="document_verified">Verify Events</option>
            </select>
          </div>

          <div className="ml-auto">
            <Button
              onClick={exportToCSV}
              disabled={!activities.length}
              variant="outline"
              size="sm"
              className="gap-2"
            >
              <Download className="h-4 w-4" />
              Export CSV
            </Button>
          </div>
        </div>

        {/* Activity List */}
        <div className="flex-1 overflow-y-auto">
          {activityQuery.isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : activities.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <p className="text-muted-foreground">No activity logs found</p>
              <p className="text-sm text-muted-foreground mt-1">
                Try adjusting the filters or time range
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {activities.map((activity) => (
                <div
                  key={activity.id}
                  className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge
                          variant={
                            activity.type === 'sign'
                              ? 'default'
                              : activity.type === 'verify'
                              ? 'secondary'
                              : 'outline'
                          }
                        >
                          {activity.type}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {new Date(activity.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm text-slate-900 dark:text-white mb-2">
                        {activity.description}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span>
                          <span className="font-medium">{activity.metadata.method}</span>{' '}
                          {activity.metadata.endpoint}
                        </span>
                        <span
                          className={
                            activity.metadata.status >= 200 && activity.metadata.status < 300
                              ? 'text-green-600 dark:text-green-400'
                              : 'text-red-600 dark:text-red-400'
                          }
                        >
                          {activity.metadata.status}
                        </span>
                        {activity.metadata.latency_ms && (
                          <span>{activity.metadata.latency_ms.toFixed(0)}ms</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between pt-4 border-t">
            <p className="text-sm text-muted-foreground">
              Showing {page * limit + 1}-{Math.min((page + 1) * limit, total)} of {total} events
            </p>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {page + 1} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => p + 1)}
                disabled={!hasMore}
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
