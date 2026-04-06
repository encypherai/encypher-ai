'use client';

import { useState } from 'react';
import { useSession } from 'next-auth/react';
import { useQuery } from '@tanstack/react-query';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Button,
} from '@encypher/design-system';
import apiClient from '../../lib/api';
import type { CdnEdgeDomain } from '../../lib/api';
import { CopyButton } from './CopyButton';

const DEPLOY_URL =
  'https://deploy.workers.cloudflare.com/?url=https://github.com/encypher/cloudflare-worker-provenance';
const GITHUB_URL = 'https://github.com/encypher/cloudflare-worker-provenance';

export function EdgeProvenanceWorkerCard() {
  const { data: session } = useSession();
  const accessToken = (session?.user as Record<string, unknown> | undefined)
    ?.accessToken as string | undefined;
  const [showClaimInput, setShowClaimInput] = useState(false);
  const [claimDomain, setClaimDomain] = useState('');

  const { data: domains, isLoading } = useQuery({
    queryKey: ['cdn-edge-domains'],
    queryFn: async () => {
      if (!accessToken) return [];
      return apiClient.getCdnEdgeDomains(accessToken);
    },
    enabled: Boolean(accessToken),
  });

  const hasDomains = domains && domains.length > 0;

  if (isLoading) {
    return (
      <Card className="animate-pulse">
        <CardHeader>
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg bg-slate-200 dark:bg-slate-700" />
            <div className="flex-1 space-y-2">
              <div className="h-5 w-48 bg-slate-200 dark:bg-slate-700 rounded" />
              <div className="h-4 w-64 bg-slate-200 dark:bg-slate-700 rounded" />
            </div>
          </div>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card
      className={
        hasDomains
          ? 'border-green-500/30 overflow-hidden'
          : 'hover:border-blue-ncs/50 transition-all duration-200'
      }
    >
      <CardHeader>
        <div className="flex items-start gap-4">
          <WorkerIcon />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <CardTitle className="text-lg">Edge Provenance Worker</CardTitle>
              {hasDomains ? (
                <span className="px-2 py-0.5 text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full">
                  {domains.length} domain{domains.length !== 1 ? 's' : ''} active
                </span>
              ) : (
                <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full">
                  One-Click Deploy
                </span>
              )}
            </div>
            <CardDescription className="mt-1">
              Embed invisible, copy-paste-survivable provenance markers into every article
              at the CDN edge. Zero code changes required.
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {hasDomains ? (
          <ConnectedView domains={domains} />
        ) : (
          <DisconnectedView
            showClaimInput={showClaimInput}
            setShowClaimInput={setShowClaimInput}
            claimDomain={claimDomain}
            setClaimDomain={setClaimDomain}
            accessToken={accessToken}
          />
        )}
      </CardContent>
    </Card>
  );
}

function DisconnectedView({
  showClaimInput,
  setShowClaimInput,
  claimDomain,
  setClaimDomain,
  accessToken,
}: {
  showClaimInput: boolean;
  setShowClaimInput: (v: boolean) => void;
  claimDomain: string;
  setClaimDomain: (v: string) => void;
  accessToken: string | undefined;
}) {
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/70 p-4">
        <p className="text-sm font-medium text-delft-blue dark:text-white">
          Deploy in under 5 minutes, no code changes needed.
        </p>
        <p className="text-xs text-muted-foreground mt-1 leading-5">
          The worker intercepts HTML responses at the CDN edge, detects article content
          automatically, and embeds sentence-level provenance markers that survive
          copy-paste, scraping, and aggregation.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <a
          href={DEPLOY_URL}
          target="_blank"
          rel="noopener noreferrer"
        >
          <Button variant="primary" size="sm">
            Deploy to Cloudflare
          </Button>
        </a>
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-blue-ncs hover:underline font-medium"
        >
          View on GitHub
        </a>
      </div>

      {!showClaimInput ? (
        <button
          onClick={() => setShowClaimInput(true)}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          Already deployed? Claim your domain
        </button>
      ) : (
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={claimDomain}
            onChange={(e) => setClaimDomain(e.target.value)}
            placeholder="yourdomain.com"
            className="flex-1 text-sm px-3 py-1.5 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-blue-ncs/50"
          />
          <Button
            variant="outline"
            size="sm"
            disabled={!claimDomain.trim() || !accessToken}
            onClick={async () => {
              if (!accessToken) return;
              try {
                await apiClient.claimCdnEdgeDomain(accessToken, claimDomain.trim());
                setShowClaimInput(false);
                setClaimDomain('');
              } catch {
                // Error handled by apiClient
              }
            }}
          >
            Claim
          </Button>
          <button
            onClick={() => {
              setShowClaimInput(false);
              setClaimDomain('');
            }}
            className="text-xs text-muted-foreground hover:text-foreground"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}

function ConnectedView({ domains }: { domains: CdnEdgeDomain[] }) {
  return (
    <div className="space-y-3">
      {domains.map((d) => (
        <div
          key={d.domain}
          className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700"
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <code className="text-sm font-mono text-delft-blue dark:text-slate-200 truncate">
                {d.domain}
              </code>
              <span
                className={`px-1.5 py-0.5 text-[10px] font-medium rounded-full ${
                  d.claim_status === 'verified'
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                    : d.claim_status === 'claimed'
                      ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                      : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                }`}
              >
                {d.claim_status}
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              {d.articles_signed} article{d.articles_signed !== 1 ? 's' : ''} signed
              {d.last_signed_at
                ? ` - last signed ${new Date(d.last_signed_at).toLocaleDateString()}`
                : ''}
            </p>
          </div>
          <CopyButton text={`https://${d.domain}/.well-known/encypher-verify`} label="Verify URL" />
        </div>
      ))}

      <div className="flex flex-wrap items-center gap-3 pt-1">
        <a
          href={DEPLOY_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-blue-ncs hover:underline font-medium"
        >
          Deploy on another domain
        </a>
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-blue-ncs hover:underline font-medium"
        >
          View on GitHub
        </a>
      </div>
    </div>
  );
}

function WorkerIcon() {
  return (
    <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-gradient-to-br from-blue-ncs/10 to-columbia-blue/20 flex items-center justify-center border border-blue-ncs/20">
      <svg
        viewBox="0 0 24 24"
        className="w-7 h-7 text-blue-ncs"
        fill="none"
        stroke="currentColor"
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {/* Globe with embedded shield - represents edge provenance */}
        <circle cx="12" cy="12" r="10" />
        <path d="M2 12h20" />
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
        {/* Small shield in center */}
        <path d="M12 8v0c1.5.5 2.5 1 2.5 1v2.5c0 2-1.5 3-2.5 3.5-1-.5-2.5-1.5-2.5-3.5V9s1-.5 2.5-1z" fill="currentColor" opacity="0.3" />
      </svg>
    </div>
  );
}
