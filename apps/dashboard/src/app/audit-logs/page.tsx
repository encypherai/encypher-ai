'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import {
  Shield,
  Download,
  Filter,
  Search,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  Lock,
  Key,
  FileText,
  Users,
  Settings,
  CreditCard,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import api from '@/lib/api';

// Action categories for filtering
const ACTION_CATEGORIES = {
  all: 'All Actions',
  'api_key': 'API Keys',
  'document': 'Documents',
  'org': 'Organization',
  'subscription': 'Billing',
  'certificate': 'Certificates',
  'coalition': 'Coalition',
};

// Action icons mapping
const getActionIcon = (action: string) => {
  if (action.startsWith('api_key')) return <Key className="h-4 w-4" />;
  if (action.startsWith('document') || action.startsWith('batch')) return <FileText className="h-4 w-4" />;
  if (action.startsWith('org.member')) return <Users className="h-4 w-4" />;
  if (action.startsWith('org')) return <Settings className="h-4 w-4" />;
  if (action.startsWith('subscription')) return <CreditCard className="h-4 w-4" />;
  if (action.startsWith('certificate')) return <Lock className="h-4 w-4" />;
  if (action.startsWith('coalition')) return <Shield className="h-4 w-4" />;
  return <FileText className="h-4 w-4" />;
};

// Action badge color
const getActionBadgeVariant = (action: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  if (action.includes('created') || action.includes('added')) return 'default';
  if (action.includes('revoked') || action.includes('removed') || action.includes('cancelled')) return 'destructive';
  if (action.includes('updated') || action.includes('changed')) return 'secondary';
  return 'outline';
};

interface AuditLog {
  id: string;
  timestamp: string;
  action: string;
  actor_id: string;
  actor_type: string;
  resource_type: string;
  resource_id?: string;
  details?: Record<string, unknown>;
  ip_address?: string;
  user_agent?: string;
}

interface AuditLogsResponse {
  organization_id: string;
  logs: AuditLog[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export default function AuditLogsPage() {
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState('all');
  const pageSize = 25;

  // Fetch audit logs
  const { data, isLoading, error } = useQuery<AuditLogsResponse>({
    queryKey: ['audit-logs', page, actionFilter],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });
      if (actionFilter !== 'all') {
        params.append('action', actionFilter);
      }
      const response = await api.get<AuditLogsResponse>(`/api/v1/audit-logs?${params}`);
      return response.data;
    },
  });

  // Export audit logs
  const handleExport = async (format: 'json' | 'csv') => {
    try {
      const response = await api.get<string | object>(`/api/v1/audit-logs/export?format=${format}`);
      
      const blob = format === 'csv' 
        ? new Blob([response.data as string], { type: 'text/csv' })
        : new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  // Filter logs by search query
  const filteredLogs = data?.logs.filter(log => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      log.action.toLowerCase().includes(query) ||
      log.actor_id.toLowerCase().includes(query) ||
      log.resource_type.toLowerCase().includes(query) ||
      (log.resource_id && log.resource_id.toLowerCase().includes(query))
    );
  }) || [];

  // Check if feature is available (Business+ tier)
  const isFeatureUnavailable = error && (error as Error).message?.includes('403');

  if (isFeatureUnavailable) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card className="max-w-2xl mx-auto">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 h-12 w-12 rounded-full bg-muted flex items-center justify-center">
              <Lock className="h-6 w-6 text-muted-foreground" />
            </div>
            <CardTitle>Audit Logs</CardTitle>
            <CardDescription>
              Audit logs are available on Business and Enterprise plans
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-sm text-muted-foreground mb-6">
              Track all API key operations, document signing, team changes, and more with comprehensive audit logging.
            </p>
            <Button asChild>
              <a href="/billing">Upgrade to Business</a>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="h-8 w-8" />
            Audit Logs
          </h1>
          <p className="text-muted-foreground mt-1">
            Track all activity in your organization
          </p>
        </div>
        <div className="flex gap-2 mt-4 md:mt-0">
          <Button variant="outline" size="sm" onClick={() => handleExport('csv')}>
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport('json')}>
            <Download className="h-4 w-4 mr-2" />
            Export JSON
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by action, actor, or resource..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="w-full md:w-48">
              <Select value={actionFilter} onValueChange={setActionFilter}>
                <SelectTrigger>
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Filter by action" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(ACTION_CATEGORIES).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 text-center text-muted-foreground">
              Loading audit logs...
            </div>
          ) : error && !isFeatureUnavailable ? (
            <div className="p-8 text-center">
              <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-2" />
              <p className="text-destructive">Failed to load audit logs</p>
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              No audit logs found
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left py-3 px-4 font-medium">Timestamp</th>
                    <th className="text-left py-3 px-4 font-medium">Action</th>
                    <th className="text-left py-3 px-4 font-medium">Actor</th>
                    <th className="text-left py-3 px-4 font-medium">Resource</th>
                    <th className="text-left py-3 px-4 font-medium">Details</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredLogs.map((log) => (
                    <tr key={log.id} className="border-b hover:bg-muted/30">
                      <td className="py-3 px-4 text-sm">
                        <div className="font-mono text-xs">
                          {format(new Date(log.timestamp), 'MMM d, yyyy')}
                        </div>
                        <div className="font-mono text-xs text-muted-foreground">
                          {format(new Date(log.timestamp), 'HH:mm:ss')}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          {getActionIcon(log.action)}
                          <Badge variant={getActionBadgeVariant(log.action)}>
                            {log.action.replace(/\./g, ' ').replace(/_/g, ' ')}
                          </Badge>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm">
                        <div className="font-medium">{log.actor_id.slice(0, 16)}...</div>
                        <div className="text-xs text-muted-foreground">{log.actor_type}</div>
                      </td>
                      <td className="py-3 px-4 text-sm">
                        <div className="font-medium">{log.resource_type}</div>
                        {log.resource_id && (
                          <div className="text-xs text-muted-foreground font-mono">
                            {log.resource_id.slice(0, 16)}...
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-4 text-sm">
                        {log.details && Object.keys(log.details).length > 0 ? (
                          <div className="text-xs text-muted-foreground max-w-xs truncate">
                            {JSON.stringify(log.details)}
                          </div>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
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
      {data && data.total > pageSize && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-muted-foreground">
            Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, data.total)} of {data.total} logs
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => p + 1)}
              disabled={!data.has_more}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
