'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Badge,
} from '@encypher/design-system';
import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import apiClient from '../../../lib/api';

// -- Helpers ------------------------------------------------------------------

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '--';
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function truncateHash(hash?: string | null): string {
  if (!hash) return '--';
  if (hash.length <= 16) return hash;
  return hash.slice(0, 8) + '...' + hash.slice(-8);
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

// -- Evidence timeline event --------------------------------------------------

const EVENT_ICONS: Record<string, string> = {
  notice_created: 'bg-blue-500',
  notice_delivered: 'bg-green-500',
  notice_acknowledged: 'bg-purple-500',
  delivery_confirmed: 'bg-green-500',
};

function TimelineEvent({ event }: { event: { event_type: string; created_at: string | null; event_hash: string; event_data?: Record<string, unknown> | null } }) {
  const dotColor = EVENT_ICONS[event.event_type] || 'bg-slate-400';
  return (
    <div className="flex gap-3">
      <div className="flex flex-col items-center">
        <div className={`w-3 h-3 rounded-full mt-1 ${dotColor}`} />
        <div className="w-px flex-1 bg-slate-200 dark:bg-slate-700" />
      </div>
      <div className="pb-6">
        <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
          {event.event_type.replace(/_/g, ' ')}
        </p>
        <p className="text-xs text-muted-foreground mt-0.5">{formatDate(event.created_at)}</p>
        <p className="text-xs text-muted-foreground font-mono mt-0.5">
          Hash: {truncateHash(event.event_hash)}
        </p>
        {event.event_data && Object.keys(event.event_data).length > 0 && (
          <details className="mt-1">
            <summary className="text-xs text-blue-600 dark:text-blue-400 cursor-pointer">
              Details
            </summary>
            <pre className="text-xs mt-1 p-2 bg-slate-50 dark:bg-slate-800 rounded overflow-x-auto max-h-40">
              {JSON.stringify(event.event_data, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
}

// -- Collapsible section ------------------------------------------------------

function CollapsibleSection({ title, children, defaultOpen = false }: { title: string; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-slate-200 dark:border-slate-700 rounded-lg">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-slate-900 dark:text-slate-100 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors rounded-lg"
      >
        <span>{title}</span>
        <svg
          className={`w-4 h-4 transition-transform ${open ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && <div className="px-4 pb-4">{children}</div>}
    </div>
  );
}

// -- Page ---------------------------------------------------------------------

export default function NoticeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const noticeId = params.noticeId as string;
  const { data: session } = useSession();
  const accessToken = (session?.user as Record<string, unknown>)?.accessToken as string | undefined;

  const { data: notice, isLoading: noticeLoading } = useQuery({
    queryKey: ['notice-detail', noticeId],
    queryFn: () => apiClient.getNoticeDetail(accessToken!, noticeId),
    enabled: Boolean(accessToken) && Boolean(noticeId),
  });

  const { data: evidence, isLoading: evidenceLoading } = useQuery({
    queryKey: ['notice-evidence', noticeId],
    queryFn: () => apiClient.getNoticeEvidence(accessToken!, noticeId),
    enabled: Boolean(accessToken) && Boolean(noticeId),
  });

  const isLoading = noticeLoading || evidenceLoading;

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-24">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-slate-300 border-t-blue-500" />
        </div>
      </DashboardLayout>
    );
  }

  if (!notice) {
    return (
      <DashboardLayout>
        <div className="text-center py-24">
          <p className="text-muted-foreground">Notice not found.</p>
          <Button variant="outline" className="mt-4" onClick={() => router.push('/enforcement')}>
            Back to Enforcement
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  const entityName = notice.target_entity_name || notice.recipient_entity || 'Unknown';
  const noticeType = notice.notice_type || notice.violation_type || 'formal_awareness';
  const noticeHash = notice.notice_hash || notice.content_hash;
  const detectionCount = evidence?.evidence_chain?.length ?? notice.evidence_chain?.length ?? 0;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Back + header */}
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => router.push('/enforcement')}>
            &lt;- Back
          </Button>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">{entityName}</h1>
              <Badge variant="outline" className="capitalize">
                {noticeType.replace(/_/g, ' ')}
              </Badge>
              <NoticeStatusBadge status={notice.status} />
            </div>
          </div>
        </div>

        {/* Notice text + hash */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              Notice Content
              {noticeHash && (
                <span className="inline-flex items-center gap-1.5 text-xs font-mono font-normal text-muted-foreground bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
                  SHA-256: {truncateHash(noticeHash)}
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {notice.notice_text ? (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <pre className="whitespace-pre-wrap text-sm text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-800 p-4 rounded-lg">
                  {notice.notice_text}
                </pre>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No notice text available.</p>
            )}
          </CardContent>
        </Card>

        {/* Evidence chain timeline */}
        <Card>
          <CardHeader>
            <CardTitle>Evidence Chain Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            {(() => {
              const chain = evidence?.evidence_chain ?? notice.evidence_chain;
              if (!chain || chain.length === 0) {
                return <p className="text-sm text-muted-foreground">No evidence events recorded yet.</p>;
              }
              return (
                <div>
                  {chain.map((event: any, i: any) => (
                    <TimelineEvent key={event.id || i} event={event} />
                  ))}
                </div>
              );
            })()}
          </CardContent>
        </Card>

        {/* Evidence package viewer */}
        {evidence && (
          <Card>
            <CardHeader>
              <CardTitle>Evidence Package</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Chain integrity */}
              <div className="flex items-center gap-2 text-sm">
                <span className="font-medium">Chain Integrity:</span>
                {evidence.chain_integrity_verified ? (
                  <span className="text-green-600 dark:text-green-400 font-medium">[Verified]</span>
                ) : (
                  <span className="text-red-600 dark:text-red-400 font-medium">[NOT Verified]</span>
                )}
              </div>

              <CollapsibleSection title="Merkle Proof / Hash Chain">
                <div className="space-y-2 mt-2">
                  <p className="text-xs text-muted-foreground">Package hash: <span className="font-mono">{evidence.package_hash}</span></p>
                  <p className="text-xs text-muted-foreground">Generated at: {formatDate(evidence.generated_at)}</p>
                  {evidence.evidence_chain?.map((entry, i) => (
                    <div key={entry.id || i} className="text-xs font-mono bg-slate-50 dark:bg-slate-800 p-2 rounded">
                      <div>Event: {entry.event_type}</div>
                      <div>Hash: {entry.event_hash}</div>
                      <div>Prev: {entry.previous_hash || '(genesis)'}</div>
                      {entry.hash_verified !== undefined && (
                        <div>Verified: {entry.hash_verified ? 'yes' : 'no'}</div>
                      )}
                    </div>
                  ))}
                </div>
              </CollapsibleSection>

              <CollapsibleSection title="Signature Chain">
                <pre className="text-xs mt-2 p-2 bg-slate-50 dark:bg-slate-800 rounded overflow-x-auto max-h-60">
                  {JSON.stringify(evidence.notice, null, 2)}
                </pre>
              </CollapsibleSection>

              <CollapsibleSection title="Detection Events">
                <div className="mt-2 text-sm text-muted-foreground">
                  <p>{detectionCount} event(s) recorded in the evidence chain.</p>
                </div>
              </CollapsibleSection>
            </CardContent>
          </Card>
        )}

        {/* Download evidence button */}
        <div className="flex gap-3">
          <Button
            onClick={() => {
              if (accessToken) {
                apiClient.downloadEvidencePackagePdf(accessToken, noticeId);
              }
            }}
          >
            Download Evidence Package (PDF)
          </Button>
        </div>

        {/* Executive summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Executive Summary</span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const el = document.getElementById('executive-summary');
                    if (el) {
                      navigator.clipboard.writeText(el.innerText);
                    }
                  }}
                >
                  Copy
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    window.print();
                  }}
                >
                  Print
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div id="executive-summary" className="prose prose-sm dark:prose-invert max-w-none space-y-3">
              <table className="w-full text-sm">
                <tbody>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <td className="py-2 pr-4 font-medium text-muted-foreground w-48">Notice Type</td>
                    <td className="py-2 capitalize">{noticeType.replace(/_/g, ' ')}</td>
                  </tr>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <td className="py-2 pr-4 font-medium text-muted-foreground">Recipient</td>
                    <td className="py-2">{entityName}</td>
                  </tr>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <td className="py-2 pr-4 font-medium text-muted-foreground">Date Created</td>
                    <td className="py-2">{formatDate(notice.created_at)}</td>
                  </tr>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <td className="py-2 pr-4 font-medium text-muted-foreground">Delivery Confirmation</td>
                    <td className="py-2">
                      {notice.delivered_at ? (
                        <span className="text-green-600 dark:text-green-400">
                          Delivered on {formatDate(notice.delivered_at)} via {notice.delivery_method || 'API'}
                        </span>
                      ) : (
                        <span className="text-yellow-600 dark:text-yellow-400">Pending delivery</span>
                      )}
                    </td>
                  </tr>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <td className="py-2 pr-4 font-medium text-muted-foreground">Content Hash (SHA-256)</td>
                    <td className="py-2 font-mono text-xs">{noticeHash || '--'}</td>
                  </tr>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <td className="py-2 pr-4 font-medium text-muted-foreground">Evidence Events</td>
                    <td className="py-2">{detectionCount}</td>
                  </tr>
                  {Boolean(notice.acknowledged_at) && (
                    <tr className="border-b border-slate-200 dark:border-slate-700">
                      <td className="py-2 pr-4 font-medium text-muted-foreground">Acknowledged</td>
                      <td className="py-2">{formatDate(notice.acknowledged_at as string)}</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
