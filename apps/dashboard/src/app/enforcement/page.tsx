'use client';

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

export default function EnforcementPage() {
  const { data: session } = useSession();
  const router = useRouter();
  const accessToken = (session?.user as Record<string, unknown>)?.accessToken as string | undefined;

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
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
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
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-slate-300 border-t-blue-500" />
              </div>
            ) : !notices || notices.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <p className="text-sm">No formal notices yet.</p>
                <p className="text-xs mt-1">
                  Notices created from the Rights page will appear here.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
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
                    {notices.map((notice: FormalNotice) => (
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
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                if (accessToken) {
                                  apiClient.downloadEvidencePackagePdf(accessToken, notice.id);
                                }
                              }}
                            >
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
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
