'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Badge,
} from '@encypher/design-system';
import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { EmptyState } from '../../components/ui/empty-state';
import { EncypherLoader } from '@encypher/icons';
import apiClient from '../../lib/api';
import type { FormalNotice } from '../../lib/api';

// -- Helpers ------------------------------------------------------------------

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '--';
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
  sent: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  delivered: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  acknowledged: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
};

function NoticeStatusBadge({ status }: { status: string }) {
  const cls = STATUS_COLORS[status?.toLowerCase()] ?? STATUS_COLORS.draft;
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cls}`}>
      {status}
    </span>
  );
}

function NoticeTypeBadge({ type }: { type?: string | null }) {
  if (!type) return null;
  const label = type.replace(/_/g, ' ');
  return (
    <Badge variant="outline" className="text-xs capitalize">
      {label}
    </Badge>
  );
}

// -- Summary card component ---------------------------------------------------

function SummaryCard({ title, value, subtitle }: { title: string; value: string | number; subtitle?: string }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        <p className="text-2xl font-bold mt-1">{value}</p>
        {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
      </CardContent>
    </Card>
  );
}

// -- Status pipeline ----------------------------------------------------------

const STATUS_ORDER = ['draft', 'sent', 'delivered', 'acknowledged'];

function StatusPipeline({ current }: { current: string }) {
  const currentIdx = STATUS_ORDER.indexOf(current?.toLowerCase());
  return (
    <div className="flex items-center gap-1">
      {STATUS_ORDER.map((step, i) => {
        const reached = i <= currentIdx;
        return (
          <div key={step} className="flex items-center gap-1">
            <div
              className={`w-2 h-2 rounded-full ${
                reached ? 'bg-blue-500 dark:bg-blue-400' : 'bg-slate-300 dark:bg-slate-600'
              }`}
              title={step}
            />
            {i < STATUS_ORDER.length - 1 && (
              <div
                className={`w-4 h-px ${
                  i < currentIdx ? 'bg-blue-500 dark:bg-blue-400' : 'bg-slate-300 dark:bg-slate-600'
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

// -- Page ---------------------------------------------------------------------

const PER_PAGE = 10;

export default function EnforcementPage() {
  const { data: session } = useSession();
  const router = useRouter();
  const accessToken = (session?.user as Record<string, unknown>)?.accessToken as string | undefined;
  const [page, setPage] = useState(1);

  const { data: notices, isLoading } = useQuery({
    queryKey: ['enforcement-notices'],
    queryFn: () => apiClient.listNotices(accessToken!),
    enabled: Boolean(accessToken),
  });

  // Compute summary stats
  const total = notices?.length ?? 0;
  const delivered = notices?.filter((n) => n.status === 'delivered' || n.status === 'acknowledged').length ?? 0;
  const deliveryRate = total > 0 ? Math.round((delivered / total) * 100) : 0;
  const pending = notices?.filter((n) => n.status === 'sent' || n.status === 'draft').length ?? 0;
  const escalated = notices?.filter((n) => n.notice_type === 'cease_and_desist' || n.notice_type === 'dmca_takedown').length ?? 0;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page header */}
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Enforcement Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage formal notices, track delivery status, and download court-ready evidence packages.
          </p>
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <SummaryCard title="Notices Sent" value={total} />
          <SummaryCard title="Delivery Rate" value={`${deliveryRate}%`} subtitle={`${delivered} of ${total} delivered`} />
          <SummaryCard title="Pending Responses" value={pending} />
          <SummaryCard title="Active Escalations" value={escalated} />
        </div>

        {/* Notice table */}
        <Card>
          <CardHeader>
            <CardTitle>Formal Notices</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <EncypherLoader size="md" />
              </div>
            ) : !notices || notices.length === 0 ? (
              <EmptyState
                icon={<svg className="w-8 h-8 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>}
                title="No formal notices yet"
                description="Notices created from the Rights page will appear here. Use formal notices to document awareness and enforce your content rights."
                actionLabel="Go to Rights"
                onAction={() => router.push('/rights')}
              />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm min-w-[580px]">
                  <thead>
                    <tr className="border-b border-slate-200 dark:border-slate-700">
                      <th className="text-left py-3 px-3 font-medium text-muted-foreground">Recipient</th>
                      <th className="text-left py-3 px-3 font-medium text-muted-foreground">Type</th>
                      <th className="text-left py-3 px-3 font-medium text-muted-foreground">Status</th>
                      <th className="text-left py-3 px-3 font-medium text-muted-foreground">Sent Date</th>
                      <th className="text-right py-3 px-3 font-medium text-muted-foreground">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {notices.slice((page - 1) * PER_PAGE, page * PER_PAGE).map((notice: FormalNotice) => (
                      <tr
                        key={notice.id}
                        className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
                      >
                        <td className="py-3 px-3">
                          <div>
                            <p className="font-medium text-slate-900 dark:text-slate-100">
                              {notice.target_entity_name || notice.recipient_entity || '--'}
                            </p>
                            {(notice.target_contact_email || notice.recipient_contact) && (
                              <p className="text-xs text-muted-foreground">
                                {notice.target_contact_email || notice.recipient_contact}
                              </p>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-3">
                          <NoticeTypeBadge type={notice.notice_type || notice.violation_type} />
                        </td>
                        <td className="py-3 px-3">
                          <div className="flex flex-col gap-1">
                            <NoticeStatusBadge status={notice.status} />
                            <StatusPipeline current={notice.status} />
                          </div>
                        </td>
                        <td className="py-3 px-3 text-muted-foreground">
                          {formatDate(notice.delivered_at || notice.created_at)}
                        </td>
                        <td className="py-3 px-3">
                          <div className="flex items-center justify-end gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => router.push(`/enforcement/${notice.id}`)}
                            >
                              View
                            </Button>
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => {
                                if (accessToken) {
                                  apiClient.downloadEvidencePackagePdf(accessToken, notice.id);
                                }
                              }}
                            >
                              <svg className="w-3.5 h-3.5 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                                <polyline points="7 10 12 15 17 10"/>
                                <line x1="12" y1="15" x2="12" y2="3"/>
                              </svg>
                              Evidence
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {notices && notices.length > PER_PAGE && (
              <div className="flex items-center justify-between pt-4 border-t border-slate-200 dark:border-slate-700">
                <p className="text-sm text-muted-foreground">
                  Showing {(page - 1) * PER_PAGE + 1}-{Math.min(page * PER_PAGE, notices.length)} of {notices.length}
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page === 1}
                    onClick={() => setPage((p) => p - 1)}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page * PER_PAGE >= notices.length}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
