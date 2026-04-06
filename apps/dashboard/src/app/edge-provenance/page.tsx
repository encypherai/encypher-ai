'use client';

import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@encypher/design-system';
import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import Link from 'next/link';

import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { Loader } from '../../components/ui/Loader';
import { useOrganization } from '../../contexts/OrganizationContext';
import apiClient from '../../lib/api';
import type { CdnEdgeDomain } from '../../lib/api';

const DEPLOY_URL =
  'https://deploy.workers.cloudflare.com/?url=https://github.com/encypher/cloudflare-worker-provenance';

// -- Helpers --

function formatNumber(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K';
  return n.toLocaleString();
}

function relativeTime(dateString: string | null): string {
  if (!dateString) return 'Never';
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMinutes = Math.floor(diffMs / 60_000);
  if (diffMinutes < 1) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 30) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

// -- Empty state --

function EmptyState() {
  return (
    <div className="text-center py-16">
      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
        <svg
          className="w-8 h-8 text-muted-foreground"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <path d="M2 12h20" />
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-foreground mb-2">
        No Edge Provenance Data Yet
      </h3>
      <p className="text-sm text-muted-foreground max-w-md mx-auto mb-6">
        Deploy the Edge Provenance Worker on your Cloudflare site to start
        signing articles with invisible, copy-paste-survivable provenance markers.
      </p>
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <a href={DEPLOY_URL} target="_blank" rel="noopener noreferrer">
          <Button variant="primary">Deploy to Cloudflare</Button>
        </a>
        <Link href="/integrations">
          <Button variant="outline">View Integrations</Button>
        </Link>
      </div>
    </div>
  );
}

// -- Metric card --

function MetricCard({
  label,
  value,
  description,
}: {
  label: string;
  value: string;
  description?: string;
}) {
  return (
    <Card className="border-border">
      <CardContent className="p-5">
        <p className="text-sm font-medium text-muted-foreground">{label}</p>
        <p className="text-2xl font-bold mt-1 text-foreground">{value}</p>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}

// -- Domain row --

function DomainRow({ domain }: { domain: CdnEdgeDomain }) {
  return (
    <div className="flex items-center justify-between p-4 border-b border-border last:border-b-0">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <code className="text-sm font-mono font-medium text-foreground truncate">
            {domain.domain}
          </code>
          <span
            className={`px-1.5 py-0.5 text-[10px] font-medium rounded-full ${
              domain.claim_status === 'verified'
                ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                : domain.claim_status === 'claimed'
                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
            }`}
          >
            {domain.claim_status}
          </span>
        </div>
        <p className="text-xs text-muted-foreground mt-0.5">
          {formatNumber(domain.articles_signed)} article
          {domain.articles_signed !== 1 ? 's' : ''} signed
        </p>
      </div>
      <div className="text-right">
        <p className="text-xs text-muted-foreground">
          Last signed {relativeTime(domain.last_signed_at)}
        </p>
      </div>
    </div>
  );
}

// -- Main page --

export default function EdgeProvenancePage() {
  const { data: session, status } = useSession();
  const accessToken = (session?.user as Record<string, unknown> | undefined)
    ?.accessToken as string | undefined;
  const { isLoading: orgLoading } = useOrganization();

  const domainsQuery = useQuery({
    queryKey: ['cdn-edge-domains'],
    queryFn: async () => {
      if (!accessToken) return [];
      return apiClient.getCdnEdgeDomains(accessToken);
    },
    enabled: Boolean(accessToken),
    staleTime: 60_000,
  });

  const isLoading = status === 'loading' || orgLoading;
  const domains = domainsQuery.data ?? [];
  const totalArticles = domains.reduce((sum, d) => sum + d.articles_signed, 0);
  const activeDomains = domains.length;
  const lastSigned = domains
    .map((d) => d.last_signed_at)
    .filter(Boolean)
    .sort()
    .pop() ?? null;

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-delft-blue dark:text-white">
              Edge Provenance
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Article signing activity from your Cloudflare Edge Provenance Workers.
            </p>
          </div>
          <a href={DEPLOY_URL} target="_blank" rel="noopener noreferrer">
            <Button variant="outline" size="sm">
              Deploy on Another Domain
            </Button>
          </a>
        </div>

        {isLoading || domainsQuery.isLoading ? (
          <div className="flex items-center justify-center py-16">
            <div className="flex flex-col items-center gap-3 text-sm text-muted-foreground">
              <Loader size="lg" />
              <span>Loading edge provenance data...</span>
            </div>
          </div>
        ) : domainsQuery.isError ? (
          <Card className="border-border">
            <CardContent className="p-6 text-center">
              <p className="text-muted-foreground">
                Failed to load edge provenance data. Please try again later.
              </p>
            </CardContent>
          </Card>
        ) : domains.length === 0 ? (
          <EmptyState />
        ) : (
          <>
            {/* Summary cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <MetricCard
                label="Active Domains"
                value={activeDomains.toString()}
                description="Domains with Edge Provenance Workers"
              />
              <MetricCard
                label="Articles Signed"
                value={formatNumber(totalArticles)}
                description="Total articles with provenance markers"
              />
              <MetricCard
                label="Last Activity"
                value={relativeTime(lastSigned)}
                description="Most recent article signed"
              />
            </div>

            {/* Domain list */}
            <Card className="border-border">
              <CardHeader>
                <CardTitle>Domains</CardTitle>
                <CardDescription>
                  Each domain running the Edge Provenance Worker with signing statistics.
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                {domains.map((d) => (
                  <DomainRow key={d.domain} domain={d} />
                ))}
              </CardContent>
            </Card>

            {/* How it works card */}
            <Card className="border-border bg-muted/30">
              <CardContent className="p-6">
                <h3 className="text-sm font-semibold text-foreground mb-3">
                  How Edge Provenance Works
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs text-muted-foreground">
                  <div>
                    <p className="font-medium text-foreground mb-1">1. Intercept</p>
                    <p>The worker intercepts HTML responses at the CDN edge and detects article content automatically.</p>
                  </div>
                  <div>
                    <p className="font-medium text-foreground mb-1">2. Sign</p>
                    <p>Article text is signed with sentence-level micro+ECC+C2PA markers via the Encypher API.</p>
                  </div>
                  <div>
                    <p className="font-medium text-foreground mb-1">3. Embed</p>
                    <p>Invisible Unicode markers are spliced into HTML text nodes. They survive copy-paste, scraping, and aggregation.</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
