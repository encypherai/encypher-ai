'use client';

import {
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@encypher/design-system';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { useState } from 'react';
import { toast } from 'sonner';

import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { EnterpriseGate } from '../../components/ui/enterprise-gate';
import { useOrganization } from '../../contexts/OrganizationContext';
import apiClient from '../../lib/api';
import type { PrintFingerprintMatch } from '../../lib/api';

// -- Helpers --

function formatDate(dateString: string | undefined): string {
  if (!dateString) return '--';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    }).format(date);
  } catch {
    return dateString;
  }
}

function confidenceLabel(confidence: number): { text: string; variant: 'success' | 'primary' | 'secondary' } {
  if (confidence >= 0.9) return { text: 'Very High', variant: 'success' };
  if (confidence >= 0.7) return { text: 'High', variant: 'primary' };
  return { text: 'Moderate', variant: 'secondary' };
}


// -- Detection results panel --

function DetectionResults({ matches }: { matches: PrintFingerprintMatch[] }) {
  if (matches.length === 0) {
    return (
      <Card className="border-border">
        <CardContent className="p-6 text-center">
          <p className="text-muted-foreground">No fingerprint detected in the submitted text.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-4">
      <h3 className="text-lg font-semibold text-foreground">
        Detection Results ({matches.length} match{matches.length !== 1 ? 'es' : ''})
      </h3>
      {matches.map((match, idx) => {
        const conf = confidenceLabel(match.confidence);
        return (
          <Card key={match.fingerprint_id + '-' + idx} className="border-border">
            <CardContent className="p-6 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">Document: {match.document_id}</p>
                  <p className="text-xs text-muted-foreground truncate">
                    Fingerprint: {match.fingerprint_id}
                  </p>
                </div>
                <Badge variant={conf.variant} size="sm">{conf.text} ({(match.confidence * 100).toFixed(1)}%)</Badge>
              </div>
              <div className="flex flex-wrap gap-4 text-sm text-muted-foreground pt-2 border-t border-border">
                <span>Organization: {match.organization_id}</span>
                <span>Markers: {match.markers_found}/{match.markers_expected}</span>
                <span>Fingerprinted: {formatDate(match.created_at)}</span>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}

// -- Main page --

export default function PrintDetectionPage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const { activeOrganization, isLoading: orgLoading } = useOrganization();
  const orgId = activeOrganization?.id;
  const isEnterprise = activeOrganization?.tier === 'enterprise';

  const [scanText, setScanText] = useState('');
  const [detectionResults, setDetectionResults] = useState<PrintFingerprintMatch[] | null>(null);

  const documentsQuery = useQuery({
    queryKey: ['fingerprinted-documents', orgId],
    queryFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      return apiClient.listFingerprintedDocuments(accessToken, orgId);
    },
    enabled: Boolean(accessToken) && Boolean(orgId) && isEnterprise,
    refetchOnWindowFocus: false,
  });

  const detectMutation = useMutation({
    mutationFn: async (text: string) => {
      if (!accessToken) throw new Error('You must be signed in.');
      return apiClient.detectPrintLeak(accessToken, text);
    },
    onSuccess: (data) => {
      setDetectionResults(data.matches);
      if (data.fingerprint_detected) {
        toast.success(`Fingerprint detected with ${data.matches.length} match(es).`);
      } else {
        toast.info('No fingerprint detected in the submitted text.');
      }
    },
    onError: (err: Error) => {
      toast.error(err?.message || 'Detection failed.');
    },
  });

  const handleDetect = () => {
    if (scanText.trim().length < 10) {
      toast.error('Please enter at least 10 characters of text to scan.');
      return;
    }
    setDetectionResults(null);
    detectMutation.mutate(scanText.trim());
  };

  const documents = documentsQuery.data ?? [];
  const isLoading = status === 'loading' || orgLoading;

  // Gate: show upgrade prompt for non-enterprise (after all hooks)
  if (!orgLoading && activeOrganization && !isEnterprise) {
    return (
      <DashboardLayout>
        <EnterpriseGate
          icon={
            <svg className="w-8 h-8 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
          }
          title="Print Leak Detection"
          description="Identify the source of leaked printed or PDF documents. Encypher embeds imperceptible spacing patterns into your content that survive printing and scanning, enabling forensic source identification."
          features={[
            'Imperceptible spacing patterns embedded in documents',
            'Scan printed pages to identify the source copy',
            'Enterprise-grade leak investigation workflow',
            'Works across print-to-scan pipelines',
          ]}
        />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-delft-blue dark:text-white">Print Leak Detection</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Identify the source of leaked printed or PDF documents using imperceptible spacing fingerprints.
          </p>
        </div>

        {/* Scan section */}
        <Card className="border-border">
          <CardHeader>
            <CardTitle>Scan for Fingerprint</CardTitle>
            <CardDescription>
              Paste or type the text from a scanned document to identify its source.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <textarea
              className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring min-h-[160px] font-mono resize-y"
              placeholder="Paste the text extracted from the scanned document here..."
              value={scanText}
              onChange={(e) => setScanText(e.target.value)}
              disabled={detectMutation.isPending}
            />
            <div className="flex items-center justify-between">
              <p className="text-xs text-muted-foreground">
                {scanText.length} characters
              </p>
              <Button
                variant="primary"
                onClick={handleDetect}
                disabled={detectMutation.isPending || scanText.trim().length < 10}
              >
                {detectMutation.isPending ? 'Scanning...' : 'Scan for Source'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Detection results */}
        {detectionResults !== null && (
          <DetectionResults matches={detectionResults} />
        )}

        {/* Fingerprinted documents list */}
        <Card className="border-border">
          <CardHeader>
            <CardTitle>Fingerprinted Documents</CardTitle>
            <CardDescription>
              Documents that have been fingerprinted using Print Leak Detection during signing.
              Enable <code className="text-xs bg-muted px-1 py-0.5 rounded">enable_print_fingerprint</code> in
              your sign requests to fingerprint content.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <p className="text-muted-foreground">Loading...</p>
            ) : documentsQuery.isError ? (
              <p className="text-muted-foreground">
                No fingerprinted documents found. Documents will appear here once you sign content
                with print leak detection enabled.
              </p>
            ) : documents.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
                  <svg className="w-8 h-8 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">No Fingerprinted Documents</h3>
                <p className="text-sm text-muted-foreground max-w-md mx-auto">
                  Sign content with <code className="bg-muted px-1 py-0.5 rounded text-xs">enable_print_fingerprint: true</code> to
                  embed invisible fingerprints for leak detection.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left">
                      <th className="pb-3 font-medium text-muted-foreground">Document</th>
                      <th className="pb-3 font-medium text-muted-foreground">Fingerprint ID</th>
                      <th className="pb-3 font-medium text-muted-foreground">Markers</th>
                      <th className="pb-3 font-medium text-muted-foreground">Status</th>
                      <th className="pb-3 font-medium text-muted-foreground">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((doc) => (
                      <tr key={doc.fingerprint_id} className="border-b border-border last:border-0">
                        <td className="py-3 font-medium text-foreground">
                          {doc.document_name || doc.document_id}
                        </td>
                        <td className="py-3">
                          <code className="text-xs bg-muted px-1.5 py-0.5 rounded font-mono">
                            {doc.fingerprint_id.slice(0, 12)}...
                          </code>
                        </td>
                        <td className="py-3 text-muted-foreground">{doc.markers_count}</td>
                        <td className="py-3">
                          <Badge
                            variant={doc.status === 'active' ? 'primary' : 'secondary'}
                            size="sm"
                          >
                            {doc.status}
                          </Badge>
                        </td>
                        <td className="py-3 text-muted-foreground">{formatDate(doc.created_at)}</td>
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
