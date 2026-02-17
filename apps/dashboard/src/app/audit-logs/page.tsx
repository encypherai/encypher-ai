'use client';

import { useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import Link from 'next/link';
import {
  Button,
  Card,
  CardContent,
  Input,
} from '@encypher/design-system';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { useOrganization } from '../../contexts/OrganizationContext';
import apiClient from '../../lib/api';

interface AuditLog {
  id: string;
  type: string;
  description: string;
  timestamp: string;
  metadata?: {
    status?: number;
    latency_ms?: number;
    endpoint?: string;
    method?: string;
    api_key?: string;
    request_id?: string;
    error_code?: string;
    error_message?: string;
    error_details?: string;
    error_stack?: string;
    severity?: 'critical' | 'high' | 'medium' | 'low';
    event_type?: string;
    actor_type?: string;
    actor_id?: string;
    resource_type?: string;
    resource_id?: string;
    organization_id?: string;
  };
}

interface AuditEventsPage {
  items: AuditLog[];
  total: number;
  page: number;
  limit: number;
}

interface AlertCodeCount {
  error_code: string;
  count: number;
}

interface AuditAlertSummary {
  total_requests: number;
  failure_requests: number;
  critical_failures: number;
  failure_rate: number;
  top_error_codes: AlertCodeCount[];
  period_start: string;
  period_end: string;
}

interface SavedAuditView {
  name: string;
  query: string;
  status: string;
  api_key_prefix: string;
  event_types: string[];
  severities: string[];
  has_stack: boolean;
  preset: string;
  start_at?: string;
  end_at?: string;
}

interface SessionUser {
  tier?: string;
  accessToken?: string;
}

// Format date helper
function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function getStatusBadgeClass(status?: number): string {
  if (!status) return 'bg-slate-100 text-slate-700';
  if (status >= 200 && status < 300) return 'bg-green-100 text-green-800';
  if (status >= 400 && status < 500) return 'bg-amber-100 text-amber-800';
  if (status >= 500) return 'bg-red-100 text-red-800';
  return 'bg-gray-100 text-gray-800';
}

function getSeverityBadgeClass(severity?: string): string {
  if (severity === 'critical') return 'bg-red-200 text-red-900';
  if (severity === 'high') return 'bg-orange-100 text-orange-900';
  if (severity === 'medium') return 'bg-amber-100 text-amber-900';
  if (severity === 'low') return 'bg-emerald-100 text-emerald-900';
  return 'bg-slate-100 text-slate-700';
}

export default function AuditLogsPage() {
  const { data: session } = useSession();
  const [searchQuery, setSearchQuery] = useState('');
  const [apiKeyFilter, setApiKeyFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [severityFilters, setSeverityFilters] = useState<string[]>([]);
  const [eventTypeFilters, setEventTypeFilters] = useState<string[]>([]);
  const [hasStackOnly, setHasStackOnly] = useState(false);
  const [datePreset, setDatePreset] = useState<'24h' | '7d' | '30d' | 'custom'>('30d');
  const [startAt, setStartAt] = useState('');
  const [endAt, setEndAt] = useState('');
  const [savedViews, setSavedViews] = useState<SavedAuditView[]>([]);
  const [savedViewName, setSavedViewName] = useState('');
  const [selectedSavedView, setSelectedSavedView] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 25;

  const storageKey = 'audit-log-saved-views-v1';

  const sessionUser = session?.user as SessionUser | undefined;
  const userTier = sessionUser?.tier || 'free';
  const accessToken = sessionUser?.accessToken;
  const { data: isSuperAdmin } = useQuery({
    queryKey: ['is-super-admin'],
    queryFn: async () => {
      if (!accessToken) return false;
      return apiClient.isSuperAdmin(accessToken);
    },
    enabled: Boolean(accessToken),
    staleTime: 5 * 60 * 1000,
  });
  const hasAuditFeature = userTier === 'enterprise' || isSuperAdmin === true;
  const { activeOrganization, isLoading: orgLoading } = useOrganization();

  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const raw = window.localStorage.getItem(storageKey);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) return;
      const normalized = parsed
        .map((entry): SavedAuditView | null => {
          if (!entry || typeof entry !== 'object') return null;
          const candidate = entry as Partial<SavedAuditView>;
          if (typeof candidate.name !== 'string' || !candidate.name.trim()) return null;
          return {
            name: candidate.name,
            query: typeof candidate.query === 'string' ? candidate.query : '',
            status: typeof candidate.status === 'string' ? candidate.status : 'all',
            api_key_prefix: typeof candidate.api_key_prefix === 'string' ? candidate.api_key_prefix : '',
            event_types: Array.isArray(candidate.event_types) ? candidate.event_types.filter((value): value is string => typeof value === 'string') : [],
            severities: Array.isArray(candidate.severities) ? candidate.severities.filter((value): value is string => typeof value === 'string') : [],
            has_stack: Boolean(candidate.has_stack),
            preset: typeof candidate.preset === 'string' ? candidate.preset : '30d',
            start_at: typeof candidate.start_at === 'string' ? candidate.start_at : undefined,
            end_at: typeof candidate.end_at === 'string' ? candidate.end_at : undefined,
          };
        })
        .filter((entry): entry is SavedAuditView => entry !== null);
      setSavedViews(normalized);
    } catch {
      // no-op: malformed localStorage payload
    }
  }, []);

  // Fetch API telemetry activity (analytics-service)
  const { data: auditPage, isLoading, error } = useQuery({
    queryKey: [
      'audit-logs-activity',
      page,
      apiKeyFilter,
      statusFilter,
      searchQuery,
      eventTypeFilters,
      severityFilters,
      hasStackOnly,
      datePreset,
      startAt,
      endAt,
    ],
    queryFn: async () => {
      if (!accessToken) {
        return { items: [], total: 0, page: 1, limit: pageSize } satisfies AuditEventsPage;
      }
      const params = new URLSearchParams({ page: String(page), limit: String(pageSize) });
      if (datePreset === '24h') params.set('days', '1');
      if (datePreset === '7d') params.set('days', '7');
      if (datePreset === '30d') params.set('days', '30');
      if (datePreset === 'custom') {
        if (startAt) params.set('start_at', new Date(startAt).toISOString());
        if (endAt) params.set('end_at', new Date(endAt).toISOString());
      }
      if (apiKeyFilter) params.set('api_key_prefix', apiKeyFilter);
      if (statusFilter === 'errors') params.set('status', 'failure');
      if (statusFilter === 'success') params.set('status', 'success');
      if (searchQuery.trim()) params.set('query', searchQuery.trim());
      eventTypeFilters.forEach((value) => params.append('event_types', value));
      severityFilters.forEach((value) => params.append('severities', value));
      if (hasStackOnly) params.set('has_stack', 'true');
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/analytics/activity/audit-events?${params}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      if (!response.ok) throw new Error('Failed to fetch audit logs');
      const data = await response.json();
      return {
        items: Array.isArray(data?.items) ? data.items : [],
        total: typeof data?.total === 'number' ? data.total : 0,
        page: typeof data?.page === 'number' ? data.page : page,
        limit: typeof data?.limit === 'number' ? data.limit : pageSize,
      } satisfies AuditEventsPage;
    },
    enabled: hasAuditFeature && !!session && !!accessToken,
  });

  const logs = useMemo(() => auditPage?.items ?? [], [auditPage]);

  const { data: alertSummary } = useQuery({
    queryKey: ['audit-logs-alert-summary'],
    queryFn: async () => {
      if (!accessToken) {
        return {
          total_requests: 0,
          failure_requests: 0,
          critical_failures: 0,
          failure_rate: 0,
          top_error_codes: [],
          period_start: new Date().toISOString(),
          period_end: new Date().toISOString(),
        } satisfies AuditAlertSummary;
      }
      const params = new URLSearchParams({ days: '7' });
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/analytics/activity/audit-events/alerts?${params}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      if (!response.ok) throw new Error('Failed to fetch alert summary');
      const data = await response.json();
      return {
        total_requests: typeof data?.total_requests === 'number' ? data.total_requests : 0,
        failure_requests: typeof data?.failure_requests === 'number' ? data.failure_requests : 0,
        critical_failures: typeof data?.critical_failures === 'number' ? data.critical_failures : 0,
        failure_rate: typeof data?.failure_rate === 'number' ? data.failure_rate : 0,
        top_error_codes: Array.isArray(data?.top_error_codes)
          ? data.top_error_codes
              .map((entry: unknown): AlertCodeCount | null => {
                if (!entry || typeof entry !== 'object') return null;
                const record = entry as { error_code?: unknown; count?: unknown };
                if (typeof record.error_code !== 'string') return null;
                return {
                  error_code: record.error_code,
                  count: typeof record.count === 'number' ? record.count : 0,
                };
              })
              .filter((entry: AlertCodeCount | null): entry is AlertCodeCount => entry !== null)
          : [],
        period_start: typeof data?.period_start === 'string' ? data.period_start : new Date().toISOString(),
        period_end: typeof data?.period_end === 'string' ? data.period_end : new Date().toISOString(),
      } satisfies AuditAlertSummary;
    },
    enabled: hasAuditFeature && !!session && !!accessToken,
    staleTime: 60_000,
  });

  const availableApiKeys = useMemo(() => {
    const values = new Set<string>();
    logs.forEach((log: AuditLog) => {
      const key = log.metadata?.api_key;
      if (key) values.add(key);
    });
    return Array.from(values).sort();
  }, [logs]);

  const availableEventTypes = useMemo(() => {
    const values = new Set<string>();
    logs.forEach((log: AuditLog) => {
      const eventType = log.metadata?.event_type;
      if (eventType) values.add(eventType);
      else if (log.type) values.add(log.type);
    });
    return Array.from(values).sort();
  }, [logs]);

  const filteredLogs = logs;

  const totalPages = Math.max(1, Math.ceil((auditPage?.total || 0) / pageSize));

  async function handleExport(format: 'csv' | 'json') {
    if (!accessToken) return;

    const params = new URLSearchParams({ format });
    if (datePreset === '24h') params.set('days', '1');
    if (datePreset === '7d') params.set('days', '7');
    if (datePreset === '30d') params.set('days', '30');
    if (datePreset === 'custom') {
      if (startAt) params.set('start_at', new Date(startAt).toISOString());
      if (endAt) params.set('end_at', new Date(endAt).toISOString());
    }
    if (apiKeyFilter) params.set('api_key_prefix', apiKeyFilter);
    if (statusFilter === 'errors') params.set('status', 'failure');
    if (statusFilter === 'success') params.set('status', 'success');
    if (searchQuery.trim()) params.set('query', searchQuery.trim());
    eventTypeFilters.forEach((value) => params.append('event_types', value));
    severityFilters.forEach((value) => params.append('severities', value));
    if (hasStackOnly) params.set('has_stack', 'true');

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/analytics/activity/audit-events/export?${params}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
    if (!response.ok) throw new Error(`Failed to export ${format.toUpperCase()}`);

    const blob = await response.blob();
    const downloadUrl = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = downloadUrl;
    anchor.download = `audit-events.${format}`;
    anchor.click();
    URL.revokeObjectURL(downloadUrl);
  }

  function toggleValue(current: string[], value: string): string[] {
    return current.includes(value) ? current.filter((item) => item !== value) : [...current, value];
  }

  function saveCurrentView() {
    const trimmedName = savedViewName.trim();
    if (!trimmedName) return;
    const next: SavedAuditView = {
      name: trimmedName,
      query: searchQuery,
      status: statusFilter,
      api_key_prefix: apiKeyFilter,
      event_types: eventTypeFilters,
      severities: severityFilters,
      has_stack: hasStackOnly,
      preset: datePreset,
      start_at: startAt || undefined,
      end_at: endAt || undefined,
    };
    const deduped = [...savedViews.filter((view) => view.name !== trimmedName), next];
    setSavedViews(deduped);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(storageKey, JSON.stringify(deduped));
    }
    setSavedViewName('');
    setSelectedSavedView(trimmedName);
  }

  function applySavedView(name: string) {
    setSelectedSavedView(name);
    const view = savedViews.find((item) => item.name === name);
    if (!view) return;
    setSearchQuery(view.query);
    setStatusFilter(view.status);
    setApiKeyFilter(view.api_key_prefix);
    setEventTypeFilters(view.event_types);
    setSeverityFilters(view.severities);
    setHasStackOnly(view.has_stack);
    if (view.preset === '24h' || view.preset === '7d' || view.preset === '30d' || view.preset === 'custom') {
      setDatePreset(view.preset);
    }
    setStartAt(view.start_at ?? '');
    setEndAt(view.end_at ?? '');
    setPage(1);
  }

  // Upgrade prompt for non-Business users
  if (!hasAuditFeature) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
          <div className="w-16 h-16 mb-6 rounded-full bg-blue-ncs/10 flex items-center justify-center">
            <svg className="w-8 h-8 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-foreground mb-2">Audit Logs</h1>
          <p className="text-muted-foreground max-w-md mb-6">
            Diagnose signing and verification failures with endpoint, API key, request ID,
            and error diagnostics.
          </p>
          <Link href="/billing">
            <Button variant="primary">Upgrade to Enterprise</Button>
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-foreground">Audit Logs</h1>
          <p className="text-muted-foreground mt-1">
            Track all activity in your organization
          </p>
          {activeOrganization && (
            <p className="text-xs text-muted-foreground mt-2">
              Active organization: <span className="font-medium text-foreground">{activeOrganization.name}</span>
            </p>
          )}
        </div>

        {/* Search and Filters */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="text-xs uppercase tracking-wide text-muted-foreground">Failure Rate</div>
              <div className="mt-2 text-2xl font-semibold">{alertSummary?.failure_rate ?? 0}%</div>
              <div className="mt-1 text-xs text-muted-foreground">
                {alertSummary?.failure_requests ?? 0} failures / {alertSummary?.total_requests ?? 0} requests
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-xs uppercase tracking-wide text-muted-foreground">Critical Failures</div>
              <div className="mt-2 text-2xl font-semibold text-red-700">{alertSummary?.critical_failures ?? 0}</div>
              <div className="mt-1 text-xs text-muted-foreground">Status 5xx in last 7 days</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-xs uppercase tracking-wide text-muted-foreground">Top Error Codes</div>
              <div className="mt-2 space-y-1 text-sm">
                {(alertSummary?.top_error_codes || []).slice(0, 3).map((item: AlertCodeCount) => (
                  <div key={item.error_code} className="flex justify-between">
                    <span className="font-mono">{item.error_code}</span>
                    <span className="text-muted-foreground">{item.count}</span>
                  </div>
                ))}
                {(alertSummary?.top_error_codes || []).length === 0 && (
                  <div className="text-xs text-muted-foreground">No recent failures</div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="flex gap-3 flex-wrap">
              <Input
                type="text"
                placeholder="Search endpoint, request ID, error, key..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(1);
                }}
                className="max-w-md flex-1"
              />
              <select
                value={datePreset}
                onChange={(e) => {
                  const preset = e.target.value as '24h' | '7d' | '30d' | 'custom';
                  setDatePreset(preset);
                  setPage(1);
                }}
                className="w-[200px] px-3 py-2 border border-input bg-background rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="24h">Date Range: Last 24 Hours</option>
                <option value="7d">Date Range: Last 7 Days</option>
                <option value="30d">Date Range: Last 30 Days</option>
                <option value="custom">Date Range: Custom Range</option>
              </select>
              {datePreset === 'custom' && (
                <>
                  <Input type="datetime-local" value={startAt} onChange={(e) => setStartAt(e.target.value)} className="w-[220px]" />
                  <Input type="datetime-local" value={endAt} onChange={(e) => setEndAt(e.target.value)} className="w-[220px]" />
                </>
              )}
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(1);
                }}
                className="w-[240px] px-3 py-2 border border-input bg-background rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="all">All statuses</option>
                <option value="errors">Failures only (4xx/5xx)</option>
                <option value="success">Successful only (2xx/3xx)</option>
              </select>
              <details className="w-[240px] px-3 py-2 border border-input bg-background rounded-md text-sm">
                <summary className="cursor-pointer">Severities ({severityFilters.length || 'all'})</summary>
                <div className="mt-2 space-y-1">
                  {['critical', 'high', 'medium', 'low'].map((severity) => (
                    <label key={severity} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={severityFilters.includes(severity)}
                        onChange={() => {
                          setSeverityFilters((current) => toggleValue(current, severity));
                          setPage(1);
                        }}
                      />
                      <span className="capitalize">{severity}</span>
                    </label>
                  ))}
                </div>
              </details>
              <details className="w-[240px] px-3 py-2 border border-input bg-background rounded-md text-sm">
                <summary className="cursor-pointer">Event Types ({eventTypeFilters.length || 'all'})</summary>
                <div className="mt-2 max-h-40 overflow-y-auto space-y-1">
                  {availableEventTypes.map((eventType) => (
                    <label key={eventType} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={eventTypeFilters.includes(eventType)}
                        onChange={() => {
                          setEventTypeFilters((current) => toggleValue(current, eventType));
                          setPage(1);
                        }}
                      />
                      <span className="font-mono text-xs">{eventType}</span>
                    </label>
                  ))}
                </div>
              </details>
              <select
                value={apiKeyFilter}
                onChange={(e) => {
                  setApiKeyFilter(e.target.value);
                  setPage(1);
                }}
                className="w-[240px] px-3 py-2 border border-input bg-background rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">All API keys</option>
                {availableApiKeys.map((key) => (
                  <option key={key} value={key}>{key}</option>
                ))}
              </select>
              <label className="flex items-center gap-2 px-3 py-2 border border-input bg-background rounded-md text-sm">
                <input
                  type="checkbox"
                  checked={hasStackOnly}
                  onChange={(e) => {
                    setHasStackOnly(e.target.checked);
                    setPage(1);
                  }}
                />
                Only failures with stack trace
              </label>
              <div className="flex items-center gap-2">
                <Input
                  type="text"
                  placeholder="Saved Views"
                  value={savedViewName}
                  onChange={(e) => setSavedViewName(e.target.value)}
                  className="w-[180px]"
                />
                <Button variant="outline" onClick={saveCurrentView}>Save current view</Button>
              </div>
              <select
                value={selectedSavedView}
                onChange={(e) => applySavedView(e.target.value)}
                className="w-[220px] px-3 py-2 border border-input bg-background rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">Saved Views</option>
                {savedViews.map((view) => (
                  <option key={view.name} value={view.name}>{view.name}</option>
                ))}
              </select>
              <Button variant="outline" onClick={() => handleExport('csv')}>Export CSV</Button>
              <Button variant="outline" onClick={() => handleExport('json')}>Export JSON</Button>
            </div>
          </CardContent>
        </Card>

        {/* Logs Table */}
        <Card>
          <CardContent className="p-0">
            {isLoading || orgLoading ? (
              <div className="p-8 text-center text-muted-foreground">
                Loading audit logs...
              </div>
            ) : error ? (
              <div className="p-8 text-center text-red-600">
                Failed to load API telemetry
              </div>
            ) : filteredLogs.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                No matching telemetry events
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left py-3 px-4 font-medium text-sm">Timestamp</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Endpoint</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Status</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Severity</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">API key</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredLogs.map((log: AuditLog) => (
                      <tr key={log.id} className="border-b hover:bg-muted/30">
                        <td className="py-3 px-4 text-sm font-mono text-muted-foreground">
                          {formatDate(log.timestamp)}
                        </td>
                        <td className="py-3 px-4 text-sm">
                          <div className="font-medium">{log.metadata?.method || 'API'} {log.metadata?.endpoint || '—'}</div>
                          <div className="text-xs text-muted-foreground">{log.description}</div>
                        </td>
                        <td className="py-3 px-4 text-sm">
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(log.metadata?.status)}`}>
                            {log.metadata?.status ? `Status ${log.metadata.status}` : 'Unknown'}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm">
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getSeverityBadgeClass(log.metadata?.severity)}`}>
                            Severity: {log.metadata?.severity || 'n/a'}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm">
                          <code className="text-xs bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">
                            {log.metadata?.api_key || '—'}
                          </code>
                        </td>
                        <td className="py-3 px-4 text-sm">
                          <div className="space-y-1 text-xs text-muted-foreground">
                            <div><span className="font-medium text-foreground">Event type:</span> {log.metadata?.event_type || log.type}</div>
                            <div><span className="font-medium text-foreground">Actor:</span> {log.metadata?.actor_type || 'api_key'} / {log.metadata?.actor_id || '—'}</div>
                            <div><span className="font-medium text-foreground">Request ID:</span> {log.metadata?.request_id || '—'}</div>
                            {log.metadata?.request_id && (
                              <button
                                type="button"
                                className="text-xs text-blue-700 underline"
                                onClick={() => setSearchQuery(log.metadata?.request_id || '')}
                              >
                                Correlate by request ID
                              </button>
                            )}
                            {log.metadata?.error_code && (
                              <div><span className="font-medium text-foreground">Error code:</span> {log.metadata.error_code}</div>
                            )}
                            {log.metadata?.error_message && (
                              <div><span className="font-medium text-foreground">Error message:</span> {log.metadata.error_message}</div>
                            )}
                            {log.metadata?.error_details && (
                              <div><span className="font-medium text-foreground">Error details:</span> {log.metadata.error_details}</div>
                            )}
                            {log.metadata?.error_stack && (
                              <details>
                                <summary className="cursor-pointer text-foreground">Stack trace</summary>
                                <pre className="mt-1 whitespace-pre-wrap rounded bg-slate-100 dark:bg-slate-800 p-2 text-[11px] overflow-x-auto">
                                  {log.metadata.error_stack}
                                </pre>
                              </details>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Pagination */}
        {(auditPage?.total || 0) > pageSize && (
          <div className="flex justify-between items-center mt-4">
            <Button
              variant="outline"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">Page {page} of {totalPages}</span>
            <Button
              variant="outline"
              onClick={() => setPage(p => p + 1)}
              disabled={page >= totalPages}
            >
              Next
            </Button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
