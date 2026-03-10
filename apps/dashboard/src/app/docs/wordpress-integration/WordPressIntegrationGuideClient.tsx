'use client';

import Link from 'next/link';
import Image from 'next/image';
import type { ReactNode } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useEffect, useMemo, useState } from 'react';
import { Check, Copy, Download, ExternalLink } from 'lucide-react';
import { useSession } from 'next-auth/react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import apiClient from '../../../lib/api';
import { useOrganization } from '../../../contexts/OrganizationContext';

function stripEmojis(input: string): string {
  return input.replace(
    /[\u{1F300}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu,
    ''
  );
}

function hasImageChild(children: React.ReactNode): boolean {
  return Array.isArray(children)
    ? children.some((child) => typeof child === 'object' && child !== null && 'type' in child && child.type === 'img')
    : typeof children === 'object' && children !== null && 'type' in children && children.type === 'img';
}

const CodeBlock = ({ children, language }: { children: string; language?: string }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(children);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group/code">
      <button
        onClick={handleCopy}
        className="absolute right-3 top-3 p-2 rounded-md bg-slate-800/50 border border-slate-700 opacity-0 group-hover/code:opacity-100 transition-opacity hover:bg-slate-700"
        title="Copy code"
      >
        {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4 text-slate-400" />}
      </button>
      <SyntaxHighlighter
        style={oneDark}
        language={language}
        PreTag="div"
        customStyle={{
          margin: 0,
          borderRadius: '0.75rem',
          fontSize: '0.875rem',
          padding: '1.5rem',
          backgroundColor: '#0f172a',
        }}
      >
        {children.replace(/\n$/, '')}
      </SyntaxHighlighter>
    </div>
  );
};

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

type TocItem = { id: string; title: string };

const WORDPRESS_PLUGIN_DOWNLOAD_URL =
  process.env.NEXT_PUBLIC_WORDPRESS_PLUGIN_DOWNLOAD_URL ||
  '/downloads/encypher-provenance.zip';

const WORDPRESS_ADMIN_URL =
  process.env.NEXT_PUBLIC_WORDPRESS_ADMIN_URL ||
  '';

type WordPressGuideProgress = {
  pluginDownloaded: boolean;
  pluginInstalled: boolean;
  connectionTested: boolean;
};

const DEFAULT_WORDPRESS_PROGRESS: WordPressGuideProgress = {
  pluginDownloaded: false,
  pluginInstalled: false,
  connectionTested: false,
};

function getWordPressProgressStorageKey(orgId: string | null | undefined) {
  return `wordpress-guide-progress:${orgId || 'default'}`;
}

export function WordPressIntegrationGuideClient({ markdown }: { markdown: string }) {
  const [activeSection, setActiveSection] = useState<string>('');
  const [progress, setProgress] = useState<WordPressGuideProgress>(DEFAULT_WORDPRESS_PROGRESS);
  const NAV_OFFSET_PX = 72;
  const queryClient = useQueryClient();
  const { data: session } = useSession();
  const { activeOrganization } = useOrganization();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const orgId = activeOrganization?.id;
  const publisherName = activeOrganization?.display_name || activeOrganization?.name || 'your publication';

  const apiKeysQuery = useQuery({
    queryKey: ['api-keys', orgId, 'wordpress-guide'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getApiKeys(accessToken, orgId);
    },
    enabled: Boolean(accessToken && orgId),
    staleTime: 30_000,
    refetchOnWindowFocus: false,
    retry: 1,
  });

  const wordpressStatusQuery = useQuery({
    queryKey: ['wordpress-integration-status'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getWordPressIntegrationStatus(accessToken);
    },
    enabled: Boolean(accessToken),
    staleTime: 15_000,
    refetchOnWindowFocus: true,
    retry: 1,
  });

  const sanitizedMarkdown = useMemo(() => stripEmojis(markdown), [markdown]);
  const hasApiKeys = (apiKeysQuery.data?.length || 0) > 0;
  const wordpressStatus = wordpressStatusQuery.data;
  const installs = wordpressStatus?.installs || [];
  const primaryInstall = installs.find((install) => install.is_primary) || installs[0];
  const wordpressAdminHref = primaryInstall?.admin_url || wordpressStatus?.admin_url || WORDPRESS_ADMIN_URL;
  const pluginInstalled = Boolean(primaryInstall?.plugin_installed || wordpressStatus?.plugin_installed);
  const connectionTested = Boolean(primaryInstall?.connection_tested || wordpressStatus?.connection_tested) || primaryInstall?.connection_status === 'connected' || wordpressStatus?.connection_status === 'connected';
  const hasSignedPost = Boolean(primaryInstall?.last_signed_at || wordpressStatus?.last_signed_at);
  const recentEvents = wordpressStatus?.recent_events || [];
  const queuedActions = (wordpressStatus?.remote_actions || []).filter((action) => action.status === 'queued');

  const queueActionMutation = useMutation({
    mutationFn: async ({ installId, actionType, note }: { installId: string; actionType: 'refresh_status' | 'test_connection'; note?: string }) => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.queueWordPressInstallAction(accessToken, installId, actionType, note);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['wordpress-integration-status'] });
      toast.success(variables.actionType === 'test_connection' ? 'Connection retest queued.' : 'Status refresh queued.');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Failed to queue WordPress action.');
    },
  });

  const guidedSteps = [
    {
      id: 'download-plugin',
      title: 'Download the Encypher plugin',
      description: 'Pull the latest WordPress plugin package directly from your dashboard.',
      completed: progress.pluginDownloaded,
      href: WORDPRESS_PLUGIN_DOWNLOAD_URL,
      cta: 'Download plugin',
    },
    {
      id: 'install-plugin',
      title: 'Install and activate it in WordPress',
      description: 'Upload the zip in WordPress admin, activate the plugin, and open Encypher → Settings.',
      completed: pluginInstalled || progress.pluginInstalled,
      href: wordpressAdminHref || '#step-2-install-in-wordpress',
      cta: wordpressAdminHref ? 'Open WordPress admin' : 'Review install step',
    },
    {
      id: 'configure-plugin',
      title: 'Connect the plugin to your Encypher workspace',
      description: 'Use secure email connect for the fastest setup, or paste an existing API key if your team manages credentials centrally.',
      completed: Boolean(primaryInstall?.organization_id || wordpressStatus?.organization_id || orgId),
      href: '#connect-your-workspace',
      cta: 'Jump to config section',
    },
    {
      id: 'test-connection',
      title: 'Run Test Connection in WordPress',
      description: 'Confirm the plugin can reach Encypher before you publish signed content.',
      completed: connectionTested || progress.connectionTested,
      href: wordpressAdminHref || '#connect-your-workspace',
      cta: wordpressAdminHref ? 'Return to WordPress' : 'Review connection step',
    },
    {
      id: 'publish-verify',
      title: 'Publish and verify your first signed post',
      description: 'Publish once, then use the frontend badge and verification view to confirm provenance is visible publicly.',
      completed: hasSignedPost,
      href: '#verify-on-the-frontend',
      cta: 'Jump to verification',
    },
  ];
  const completedGuidedSteps = guidedSteps.filter((step) => step.completed).length;

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const storageKey = getWordPressProgressStorageKey(orgId);
    const raw = window.localStorage.getItem(storageKey);
    if (!raw) {
      setProgress(DEFAULT_WORDPRESS_PROGRESS);
      return;
    }
    try {
      const parsed = JSON.parse(raw) as Partial<WordPressGuideProgress>;
      setProgress({
        pluginDownloaded: Boolean(parsed.pluginDownloaded),
        pluginInstalled: Boolean(parsed.pluginInstalled),
        connectionTested: Boolean(parsed.connectionTested),
      });
    } catch {
      setProgress(DEFAULT_WORDPRESS_PROGRESS);
    }
  }, [orgId]);

  const tableOfContents: TocItem[] = useMemo(() => {
    const items: TocItem[] = [];
    for (const match of sanitizedMarkdown.matchAll(/^##\s+(.+)$/gm)) {
      const title = match[1]?.trim();
      if (!title) continue;
      items.push({ id: slugify(title), title });
    }
    return items;
  }, [sanitizedMarkdown]);

  useEffect(() => {
    const handleScroll = () => {
      const headings = document.querySelectorAll('h2[id]');
      if (headings.length === 0) return;

      const scrollPosition = window.scrollY + 150;
      let currentId = '';

      headings.forEach((heading) => {
        const element = heading as HTMLElement;
        if (element.offsetTop <= scrollPosition) {
          currentId = element.id;
        }
      });

      if (currentId) {
        setActiveSection(currentId);
      }
    };

    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    const timeoutId = setTimeout(handleScroll, 200);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      clearTimeout(timeoutId);
    };
  }, []);

  const scrollToId = (id: string) => {
    const target = document.getElementById(id);
    if (!target) return;

    const top = target.getBoundingClientRect().top + window.scrollY - NAV_OFFSET_PX;
    window.scrollTo({ top, behavior: 'smooth' });
    window.history.pushState(null, '', `#${id}`);
  };

  const updateProgress = (patch: Partial<WordPressGuideProgress>) => {
    const next = { ...progress, ...patch };
    setProgress(next);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(getWordPressProgressStorageKey(orgId), JSON.stringify(next));
    }
  };

  const handleStepAction = (stepId: string, href: string) => {
    if (stepId === 'download-plugin') {
      updateProgress({ pluginDownloaded: true });
    }
    if (href.startsWith('#')) {
      scrollToId(href.slice(1));
      return;
    }
    window.open(href, href.startsWith('http') ? '_blank' : '_self');
  };

  return (
    <>
      {/* Breadcrumb */}
      <nav className="mb-6">
        <ol className="flex items-center gap-2 text-sm text-muted-foreground">
          <li>
            <Link href="/docs" className="hover:text-blue-ncs transition-colors">
              Documentation
            </Link>
          </li>
          <li>/</li>
          <li>
            <Link href="/docs/publisher-integration" className="hover:text-blue-ncs transition-colors">
              Publisher Integration
            </Link>
          </li>
          <li>/</li>
          <li className="text-delft-blue dark:text-white font-medium">WordPress</li>
        </ol>
      </nav>

      <div className="flex flex-col lg:flex-row gap-12">
        {/* Main Content */}
        <article className="flex-1 min-w-0">
          <header className="mb-12">
            <div className="flex items-center gap-3 mb-4">
              <span className="p-2 bg-[#21759b]/10 text-[#21759b] rounded-lg">
                <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
                  <path d="M12 2C6.486 2 2 6.486 2 12s4.486 10 10 10 10-4.486 10-10S17.514 2 12 2zM3.009 12c0-1.298.29-2.529.8-3.64l4.404 12.065A8.993 8.993 0 013.009 12zm8.991 9c-.924 0-1.813-.15-2.646-.42l2.81-8.162 2.878 7.886c.019.046.042.089.065.13A8.94 8.94 0 0112 21zm1.237-13.22c.564-.03 1.072-.09 1.072-.09.505-.06.446-.802-.059-.772 0 0-1.518.12-2.497.12-.921 0-2.468-.12-2.468-.12-.505-.03-.564.742-.059.772 0 0 .478.06.983.09l1.46 4.002-2.052 6.155-3.413-10.157c.564-.03 1.072-.09 1.072-.09.505-.06.446-.802-.06-.772 0 0-1.517.12-2.496.12-.176 0-.383-.005-.6-.013A8.977 8.977 0 0112 3.009c2.34 0 4.472.895 6.071 2.36-.039-.002-.076-.008-.116-.008-1.005 0-1.716.875-1.716 1.817 0 .843.487 1.557 1.005 2.4.39.675.843 1.54.843 2.79 0 .867-.333 1.872-.773 3.272l-1.013 3.383L12.237 7.78z" />
                </svg>
              </span>
              <span className="text-sm font-semibold uppercase tracking-wider text-[#21759b]">WordPress Plugin</span>
            </div>
            <h1 className="text-4xl font-extrabold text-delft-blue dark:text-white mb-4 tracking-tight leading-tight">
              WordPress Integration Guide
            </h1>
            <p className="text-xl text-slate-500 dark:text-slate-400 max-w-3xl leading-relaxed mb-8">
              Install the plugin, connect your workspace in minutes, and verify your first signed WordPress post with a standards-based provenance workflow.
            </p>

            {/* Quick Action Card */}
            <div className="flex flex-wrap gap-4 mb-8">
              <a
                href={WORDPRESS_PLUGIN_DOWNLOAD_URL}
                className="inline-flex items-center gap-2 px-5 py-3 bg-[#21759b] text-white rounded-xl font-semibold hover:bg-[#1a5f7a] transition-colors shadow-lg shadow-[#21759b]/20"
              >
                <Download className="w-5 h-5" />
                Download Plugin
              </a>
              <button
                type="button"
                onClick={() => scrollToId('connect-your-workspace')}
                className="inline-flex items-center gap-2 px-5 py-3 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-xl font-semibold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
              >
                View Connect Flow
                <ExternalLink className="w-4 h-4" />
              </button>
            </div>

            {/* Time Estimate */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-lg text-sm font-medium">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Setup time: ~5 minutes
            </div>

            <div className="mt-8 rounded-2xl border border-[#21759b]/20 bg-gradient-to-br from-[#21759b]/5 via-white to-blue-50 dark:from-[#21759b]/10 dark:via-slate-900 dark:to-slate-900 p-6 lg:p-7">
              <div className="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-6 mb-6">
                <div className="max-w-3xl">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#21759b] mb-2">Guided WordPress setup</p>
                  <h2 className="text-2xl font-bold text-delft-blue dark:text-white mb-2">Connect {publisherName} to Encypher step by step</h2>
                  <p className="text-sm text-slate-600 dark:text-slate-400 leading-6">
                    This workspace uses your real Encypher organization state so your WordPress team can move from plugin download to first verified signed post without guessing what to configure next. Start with secure email connect, keep manual API keys as a fallback, and use the live telemetry below to confirm the rollout.
                  </p>
                </div>
                <div className="min-w-[220px] rounded-xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/70 p-4">
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">Progress</p>
                  <p className="text-3xl font-bold text-delft-blue dark:text-white">{completedGuidedSteps}/{guidedSteps.length}</p>
                  <p className="text-xs text-muted-foreground mt-1">WordPress setup milestones complete</p>
                  <p className="text-xs text-muted-foreground mt-2">{wordpressStatus?.install_count || installs.length} install{(wordpressStatus?.install_count || installs.length) === 1 ? '' : 's'} connected</p>
                  <div className="mt-3 h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-[#21759b] to-blue-ncs transition-all"
                      style={{ width: `${Math.round((completedGuidedSteps / guidedSteps.length) * 100)}%` }}
                    />
                  </div>
                </div>
              </div>

              <div className="grid lg:grid-cols-[1.2fr_0.8fr] gap-6 mb-6">
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-4">
                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">Recommended setup</p>
                    <p className="text-sm text-delft-blue dark:text-white">Secure email connect provisions the plugin automatically and keeps the onboarding flow inside WordPress.</p>
                    <button
                      type="button"
                      onClick={() => scrollToId('connect-your-workspace')}
                      className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-blue-ncs"
                    >
                      Jump to connection step
                    </button>
                  </div>
                  <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-4">
                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">Manual fallback</p>
                    <p className="text-sm text-delft-blue dark:text-white">
                      {apiKeysQuery.isLoading ? 'Checking workspace credentials…' : hasApiKeys ? `${apiKeysQuery.data?.length || 0} existing API key${(apiKeysQuery.data?.length || 0) === 1 ? '' : 's'} available if you prefer manual setup` : 'No existing API keys detected yet — the guided email flow is still ready to use'}
                    </p>
                    <Link href="/api-keys" className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-blue-ncs">
                      {hasApiKeys ? 'Manage existing API keys' : 'Open API key page'}
                      <ExternalLink className="w-4 h-4" />
                    </Link>
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-4">
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3">Live WordPress status</p>
                  <div className="space-y-3">
                    <div className="rounded-lg bg-slate-50 dark:bg-slate-900 px-3 py-2.5">
                      <p className="text-xs text-slate-500 dark:text-slate-400">Connection</p>
                      <p className="text-sm font-medium text-delft-blue dark:text-white mt-1">
                        {wordpressStatusQuery.isLoading
                          ? 'Checking plugin telemetry…'
                          : connectionTested
                            ? 'Connected and recently tested'
                            : pluginInstalled
                              ? 'Plugin detected, waiting for connection test'
                              : 'Plugin has not reported in yet'}
                      </p>
                    </div>
                    {(primaryInstall?.site_url || wordpressStatus?.site_url) && (
                      <div className="rounded-lg bg-slate-50 dark:bg-slate-900 px-3 py-2.5">
                        <p className="text-xs text-slate-500 dark:text-slate-400">WordPress site</p>
                        <a href={primaryInstall?.site_url || wordpressStatus?.site_url || '#'} target="_blank" rel="noopener noreferrer" className="text-sm font-medium text-blue-ncs break-all hover:underline mt-1 inline-block">
                          {primaryInstall?.site_url || wordpressStatus?.site_url}
                        </a>
                      </div>
                    )}
                    {(primaryInstall?.last_signed_post_url || wordpressStatus?.last_signed_post_url) && (
                      <div className="rounded-lg bg-slate-50 dark:bg-slate-900 px-3 py-2.5">
                        <p className="text-xs text-slate-500 dark:text-slate-400">Last signed post</p>
                        <a href={primaryInstall?.last_signed_post_url || wordpressStatus?.last_signed_post_url || '#'} target="_blank" rel="noopener noreferrer" className="text-sm font-medium text-blue-ncs break-all hover:underline mt-1 inline-block">
                          Open signed article
                        </a>
                        {(primaryInstall?.last_signed_at || wordpressStatus?.last_signed_at) && (
                          <p className="text-xs text-muted-foreground mt-1">Signed at {new Date((primaryInstall?.last_signed_at || wordpressStatus?.last_signed_at) as string).toLocaleString()}</p>
                        )}
                      </div>
                    )}
                    {queuedActions.length > 0 && (
                      <div className="rounded-lg bg-amber-50 dark:bg-amber-950/20 px-3 py-2.5 border border-amber-200/70 dark:border-amber-900/40">
                        <p className="text-xs text-amber-700 dark:text-amber-300">Queued remote actions</p>
                        <p className="text-sm font-medium text-amber-900 dark:text-amber-100 mt-1">{queuedActions.length} action{queuedActions.length === 1 ? '' : 's'} waiting for the plugin to poll.</p>
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col gap-3 mt-4">
                    <a
                      href={WORDPRESS_PLUGIN_DOWNLOAD_URL}
                      onClick={() => updateProgress({ pluginDownloaded: true })}
                      className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-[#21759b] text-white font-medium hover:bg-[#1a5f7a] transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      Download plugin zip
                    </a>
                    {wordpressAdminHref ? (
                      <a
                        href={wordpressAdminHref}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-800 text-delft-blue dark:text-white font-medium hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors"
                      >
                        <ExternalLink className="w-4 h-4" />
                        Open WordPress settings
                      </a>
                    ) : (
                      <button
                        type="button"
                        onClick={() => scrollToId('step-2-install-in-wordpress')}
                        className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-800 text-delft-blue dark:text-white font-medium hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors"
                      >
                        Review install step
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => scrollToId('connect-your-workspace')}
                      className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-800 text-delft-blue dark:text-white font-medium hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors"
                    >
                      Jump to workspace connection
                    </button>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                {guidedSteps.map((step, index) => (
                  <div key={step.id} className={`rounded-xl border p-4 ${step.completed ? 'border-green-200 bg-green-50/50 dark:border-green-900/40 dark:bg-green-900/10' : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950'}`}>
                    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                      <div className="flex items-start gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${step.completed ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-[#21759b]/10 text-[#21759b]'}`}>
                          {step.completed ? '✓' : index + 1}
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-delft-blue dark:text-white">{step.title}</p>
                          <p className="text-xs text-muted-foreground mt-1 leading-5">{step.description}</p>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <button
                          onClick={() => handleStepAction(step.id, step.href)}
                          className="inline-flex items-center justify-center gap-2 px-3.5 py-2 rounded-lg bg-delft-blue text-white text-sm font-medium hover:opacity-90 transition-opacity"
                        >
                          {step.cta}
                        </button>
                        {step.id === 'install-plugin' && !step.completed && !pluginInstalled && (
                          <button
                            onClick={() => updateProgress({ pluginInstalled: true })}
                            className="inline-flex items-center justify-center gap-2 px-3.5 py-2 rounded-lg border border-slate-200 dark:border-slate-800 text-sm font-medium text-delft-blue dark:text-white hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors"
                          >
                            Mark installed
                          </button>
                        )}
                        {step.id === 'test-connection' && !step.completed && !connectionTested && (
                          <button
                            onClick={() => updateProgress({ connectionTested: true })}
                            className="inline-flex items-center justify-center gap-2 px-3.5 py-2 rounded-lg border border-slate-200 dark:border-slate-800 text-sm font-medium text-delft-blue dark:text-white hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors"
                          >
                            Mark connection tested
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {installs.length > 0 && (
                <div className="mt-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/70 p-5">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#21759b] mb-1">Multi-property management</p>
                      <h3 className="text-lg font-semibold text-delft-blue dark:text-white">Connected WordPress installs</h3>
                    </div>
                    <p className="text-sm text-muted-foreground">Manage status refresh and connection retests for each property.</p>
                  </div>

                  <div className="space-y-3">
                    {installs.map((install) => {
                      const latestAction = (wordpressStatus?.remote_actions || []).find((action) => action.install_id === install.install_id);
                      return (
                        <div key={install.install_id} className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-4">
                          <div className="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-4">
                            <div>
                              <div className="flex flex-wrap items-center gap-2 mb-2">
                                <p className="text-sm font-semibold text-delft-blue dark:text-white">{install.site_name || install.site_url || install.install_id}</p>
                                {install.is_primary && <span className="rounded-full bg-[#21759b]/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-[#21759b]">Primary</span>}
                                {install.environment && <span className="rounded-full bg-slate-100 dark:bg-slate-800 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">{install.environment}</span>}
                                {install.is_multisite && <span className="rounded-full bg-violet-100 dark:bg-violet-900/30 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-violet-700 dark:text-violet-300">Multisite</span>}
                              </div>
                              <div className="space-y-1 text-xs text-muted-foreground">
                                <p>Install ID: <span className="font-mono">{install.install_id}</span></p>
                                {install.site_url && <p>Site: {install.site_url}</p>}
                                <p>Connection: {install.connection_status || 'unknown'}{install.last_connection_checked_at ? ` • Last checked ${new Date(install.last_connection_checked_at).toLocaleString()}` : ''}</p>
                                <p>Signing: {install.signed_post_count || 0} signed post{(install.signed_post_count || 0) === 1 ? '' : 's'}{install.last_signed_at ? ` • Last sign ${new Date(install.last_signed_at).toLocaleString()}` : ''}</p>
                                <p>Verification: {install.verified_post_count || 0} event{(install.verified_post_count || 0) === 1 ? '' : 's'}{install.last_verification_status ? ` • Latest ${install.last_verification_status}` : ''}</p>
                                {latestAction?.status && <p>Latest remote action: {latestAction.action_type} • {latestAction.status}</p>}
                              </div>
                            </div>

                            <div className="flex flex-wrap gap-2">
                              <button
                                onClick={() => queueActionMutation.mutate({ installId: install.install_id, actionType: 'refresh_status', note: 'Queued from dashboard WordPress workspace.' })}
                                disabled={queueActionMutation.isPending}
                                className="inline-flex items-center justify-center gap-2 px-3.5 py-2 rounded-lg border border-slate-200 dark:border-slate-800 text-sm font-medium text-delft-blue dark:text-white hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors disabled:opacity-60"
                              >
                                Refresh status
                              </button>
                              <button
                                onClick={() => queueActionMutation.mutate({ installId: install.install_id, actionType: 'test_connection', note: 'Queued from dashboard to retest the Encypher connection.' })}
                                disabled={queueActionMutation.isPending}
                                className="inline-flex items-center justify-center gap-2 px-3.5 py-2 rounded-lg bg-delft-blue text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-60"
                              >
                                Retest connection
                              </button>
                              {install.admin_url && (
                                <a
                                  href={install.admin_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center justify-center gap-2 px-3.5 py-2 rounded-lg border border-slate-200 dark:border-slate-800 text-sm font-medium text-delft-blue dark:text-white hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors"
                                >
                                  Open admin
                                </a>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {recentEvents.length > 0 && (
                <div className="mt-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/70 p-5">
                  <div className="flex items-center justify-between gap-3 mb-4">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#21759b] mb-1">Verification telemetry</p>
                      <h3 className="text-lg font-semibold text-delft-blue dark:text-white">Recent WordPress verification events</h3>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {recentEvents.slice().reverse().slice(0, 6).map((event) => (
                      <div key={event.event_id} className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-4">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                          <div>
                            <p className="text-sm font-semibold text-delft-blue dark:text-white">{event.status || (event.valid ? 'verified' : event.tampered ? 'tampered' : 'failed')}</p>
                            <p className="text-xs text-muted-foreground mt-1">Install {event.install_id}{event.post_id ? ` • Post ${event.post_id}` : ''}{event.verified_at ? ` • ${new Date(event.verified_at).toLocaleString()}` : ''}</p>
                          </div>
                          {event.post_url && (
                            <a href={event.post_url} target="_blank" rel="noopener noreferrer" className="text-sm font-medium text-blue-ncs hover:underline">
                              Open verified post
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </header>

          <div
            className="prose prose-slate dark:prose-invert max-w-none
              prose-headings:scroll-mt-[72px]
              prose-h2:text-2xl prose-h2:font-bold prose-h2:mt-16 prose-h2:mb-6 prose-h2:pb-2 prose-h2:border-b prose-h2:border-slate-200 dark:prose-h2:border-slate-800
              prose-h3:text-xl prose-h3:font-semibold prose-h3:mt-10 prose-h3:mb-4
              prose-p:text-slate-600 dark:prose-p:text-slate-400 prose-p:leading-8 prose-p:mb-6
              prose-strong:text-slate-900 dark:prose-strong:text-white
              prose-a:text-blue-ncs prose-a:no-underline hover:prose-a:underline
              prose-code:before:content-none prose-code:after:content-none
              prose-hr:my-12 prose-hr:border-slate-200 dark:prose-hr:border-slate-800
              prose-table:my-8 prose-table:border-separate prose-table:border-spacing-0 prose-table:rounded-xl prose-table:border prose-table:border-slate-200 dark:prose-table:border-slate-800 prose-table:overflow-hidden
              prose-thead:bg-slate-50 dark:prose-thead:bg-slate-800/50
              prose-th:px-4 prose-th:py-3 prose-th:text-left prose-th:text-xs prose-th:font-semibold prose-th:uppercase prose-th:tracking-wider prose-th:text-slate-500 dark:prose-th:text-slate-400 prose-th:border-b prose-th:border-slate-200 dark:prose-th:border-slate-800
              prose-td:px-4 prose-td:py-4 prose-td:text-sm prose-td:border-b prose-td:border-slate-100 dark:prose-td:border-slate-800/50 last:prose-td:border-b-0
              prose-img:rounded-xl prose-img:shadow-lg prose-img:border prose-img:border-slate-200 dark:prose-img:border-slate-800"
          >
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h1: () => null,
                h2: ({ children }) => {
                  const id = slugify(children?.toString() || '');
                  return (
                    <h2 id={id} className="group relative">
                      <a
                        href={`#${id}`}
                        onClick={(e) => {
                          e.preventDefault();
                          scrollToId(id);
                        }}
                        className="absolute -left-6 top-0 opacity-0 group-hover:opacity-100 text-slate-300 dark:text-slate-600 transition-opacity pr-2"
                        aria-hidden="true"
                      >
                        #
                      </a>
                      {children}
                    </h2>
                  );
                },
                h3: ({ children }) => {
                  const id = slugify(children?.toString() || '');
                  return (
                    <h3 id={id} className="group relative">
                      <a
                        href={`#${id}`}
                        onClick={(e) => {
                          e.preventDefault();
                          scrollToId(id);
                        }}
                        className="absolute -left-5 top-0 opacity-0 group-hover:opacity-100 text-slate-300 dark:text-slate-600 transition-opacity pr-2 text-base"
                        aria-hidden="true"
                      >
                        #
                      </a>
                      {children}
                    </h3>
                  );
                },
                ul: ({ children }) => (
                  <ul className="list-disc pl-6 my-6 text-slate-600 dark:text-slate-400">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal pl-6 my-6 text-slate-600 dark:text-slate-400">{children}</ol>
                ),
                li: ({ children }) => <li className="my-1 leading-7">{children}</li>,
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-blue-ncs bg-blue-50 dark:bg-blue-900/20 pl-4 py-3 pr-4 my-6 rounded-r-lg text-slate-700 dark:text-slate-300 not-italic">
                    {children}
                  </blockquote>
                ),
                p: ({ children }) => {
                  if (hasImageChild(children)) {
                    return <>{children}</>;
                  }

                  return <p>{children}</p>;
                },
                img: ({ src, alt }) => {
                  if (!src || typeof src !== 'string') return null;
                  return (
                    <div className="my-8">
                      <div className="relative rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-lg bg-slate-100 dark:bg-slate-800">
                        <div className="flex items-center gap-2 px-4 py-2 bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
                          <div className="flex gap-1.5">
                            <div className="w-3 h-3 rounded-full bg-red-400" />
                            <div className="w-3 h-3 rounded-full bg-yellow-400" />
                            <div className="w-3 h-3 rounded-full bg-green-400" />
                          </div>
                          <span className="text-xs text-slate-400 ml-2">{alt}</span>
                        </div>
                        <div className="relative aspect-[16/10] bg-white dark:bg-slate-950">
                          <Image
                            src={src}
                            alt={alt || 'Screenshot'}
                            fill
                            className="object-contain"
                            sizes="(max-width: 1280px) 100vw, 900px"
                            unoptimized
                          />
                        </div>
                      </div>
                    </div>
                  );
                },
                code: ({ className, children }) => {
                  const match = /language-(\w+)/.exec(className || '');
                  const isInline = !match;

                  if (isInline) {
                    return (
                      <code className="bg-slate-100 dark:bg-slate-800 text-blue-ncs px-1.5 py-0.5 rounded text-sm font-medium">
                        {children}
                      </code>
                    );
                  }

                  return (
                    <div className="my-6">
                      <CodeBlock language={match?.[1]}>{String(children)}</CodeBlock>
                    </div>
                  );
                },
                a: ({ href, children }) => {
                  const isExternal = href?.startsWith('http');
                  if (isExternal) {
                    return (
                      <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-ncs hover:underline">
                        {children}
                      </a>
                    );
                  }
                  return (
                    <Link href={href || '#'} className="text-blue-ncs hover:underline">
                      {children}
                    </Link>
                  );
                },
                table: ({ children }) => (
                  <div className="my-8 overflow-x-auto">
                    <table className="w-full border-separate border-spacing-0 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
                      {children}
                    </table>
                  </div>
                ),
                thead: ({ children }) => (
                  <thead className="bg-slate-50 dark:bg-slate-800/50">{children}</thead>
                ),
                th: ({ children }) => (
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="px-4 py-4 text-sm border-b border-slate-100 dark:border-slate-800/50">
                    {children}
                  </td>
                ),
                tr: ({ children }) => <tr className="last:[&>td]:border-b-0">{children}</tr>,
              }}
            >
              {sanitizedMarkdown}
            </ReactMarkdown>
          </div>
        </article>

        {/* Table of Contents Sidebar */}
        <aside className="hidden xl:block w-72 flex-shrink-0">
          <div className="sticky top-20 p-6 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-800">
            <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-4">On this page</h4>
            <nav className="space-y-1 max-h-[60vh] overflow-y-auto">
              {tableOfContents.map((item) => (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  onClick={(e) => {
                    e.preventDefault();
                    scrollToId(item.id);
                  }}
                  className={`group flex items-center gap-3 text-sm py-2 px-3 rounded-lg transition-all ${
                    activeSection === item.id
                      ? 'bg-white dark:bg-slate-800 text-blue-ncs font-semibold shadow-sm border border-slate-200 dark:border-slate-700'
                      : 'text-slate-500 dark:text-slate-400 hover:text-delft-blue dark:hover:text-white'
                  }`}
                >
                  <div
                    className={`w-1 h-1 rounded-full transition-all ${
                      activeSection === item.id
                        ? 'bg-blue-ncs scale-150'
                        : 'bg-slate-300 dark:bg-slate-700 group-hover:bg-slate-400'
                    }`}
                  />
                  {item.title}
                </a>
              ))}
            </nav>

            <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-800 space-y-3">
              <a
                href={WORDPRESS_PLUGIN_DOWNLOAD_URL}
                className="flex items-center justify-center gap-2 p-3 rounded-lg bg-[#21759b] text-white hover:bg-[#1a5f7a] transition-all text-sm font-semibold"
              >
                <Download className="w-4 h-4" />
                Download Plugin
              </a>
              <a
                href="/docs/publisher-integration"
                className="flex items-center justify-between group p-3 rounded-lg border border-dashed border-slate-300 dark:border-slate-700 hover:border-blue-ncs hover:bg-blue-ncs/5 transition-all text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-blue-ncs"
              >
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                    />
                  </svg>
                  Publisher API Guide
                </div>
                <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </a>
            </div>
          </div>
        </aside>
      </div>
    </>
  );
}
