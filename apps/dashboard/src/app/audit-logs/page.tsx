'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import Link from 'next/link';
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Input,
} from '@encypher/design-system';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { useOrganization } from '../../contexts/OrganizationContext';

interface AuditLog {
  id: string;
  action: string;
  actor_id: string;
  resource_type: string;
  resource_id?: string;
  details?: Record<string, unknown>;
  created_at: string;
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

// Get action badge color
function getActionColor(action: string): string {
  if (action.includes('created') || action.includes('joined')) return 'bg-green-100 text-green-800';
  if (action.includes('removed') || action.includes('cancelled') || action.includes('revoked')) return 'bg-red-100 text-red-800';
  if (action.includes('updated') || action.includes('changed')) return 'bg-blue-100 text-blue-800';
  if (action.includes('invited')) return 'bg-purple-100 text-purple-800';
  return 'bg-gray-100 text-gray-800';
}

export default function AuditLogsPage() {
  const { data: session } = useSession();
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 25;

  const userTier = (session?.user as any)?.tier || 'starter';
  const hasAuditFeature = ['business', 'enterprise'].includes(userTier);
  const { activeOrganization, isLoading: orgLoading } = useOrganization();
  const orgId = activeOrganization?.id;

  // Fetch audit logs
  const { data: logs, isLoading, error } = useQuery({
    queryKey: ['audit-logs', orgId, page],
    queryFn: async () => {
      if (!orgId) return [];
      const accessToken = (session?.user as any)?.accessToken;
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/organizations/${orgId}/audit-logs?limit=${pageSize}&offset=${(page - 1) * pageSize}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      if (!response.ok) throw new Error('Failed to fetch audit logs');
      const data = await response.json();
      return data.data || [];
    },
    enabled: hasAuditFeature && !!orgId && !!session,
  });

  // Filter logs by search
  const filteredLogs = (logs || []).filter((log: AuditLog) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      log.action.toLowerCase().includes(query) ||
      log.resource_type.toLowerCase().includes(query)
    );
  });

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
            Track all activity in your organization including team changes, API key operations, and more.
            Audit logs are available on Business and Enterprise plans.
          </p>
          <Link href="/billing">
            <Button variant="primary">Upgrade to Business</Button>
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

        {/* Search */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <Input
              type="text"
              placeholder="Search by action or resource..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="max-w-md"
            />
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
                Failed to load audit logs
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
                      <th className="text-left py-3 px-4 font-medium text-sm">Timestamp</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Action</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Resource</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredLogs.map((log: AuditLog) => (
                      <tr key={log.id} className="border-b hover:bg-muted/30">
                        <td className="py-3 px-4 text-sm font-mono text-muted-foreground">
                          {formatDate(log.created_at)}
                        </td>
                        <td className="py-3 px-4">
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getActionColor(log.action)}`}>
                            {log.action.replace(/\./g, ' ').replace(/_/g, ' ')}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm">
                          <div className="font-medium">{log.resource_type}</div>
                          {log.resource_id && (
                            <div className="text-xs text-muted-foreground font-mono">
                              {log.resource_id.slice(0, 12)}...
                            </div>
                          )}
                        </td>
                        <td className="py-3 px-4 text-sm text-muted-foreground">
                          {log.details ? (
                            <span className="text-xs font-mono">
                              {JSON.stringify(log.details).slice(0, 50)}
                              {JSON.stringify(log.details).length > 50 ? '...' : ''}
                            </span>
                          ) : (
                            '—'
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
        {filteredLogs.length >= pageSize && (
          <div className="flex justify-between items-center mt-4">
            <Button
              variant="outline"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">Page {page}</span>
            <Button
              variant="outline"
              onClick={() => setPage(p => p + 1)}
              disabled={filteredLogs.length < pageSize}
            >
              Next
            </Button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
