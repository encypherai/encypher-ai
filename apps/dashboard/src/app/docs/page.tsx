'use client';

import { DashboardLayout } from '../../components/layout/DashboardLayout';
import Link from 'next/link';

// ── Icon components ──

function IconPublisher({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
    </svg>
  );
}

function IconIntegrations({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
    </svg>
  );
}

function IconApi({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
    </svg>
  );
}

function IconPython({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  );
}

function IconTypeScript({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
    </svg>
  );
}

function IconExternal({ className = 'w-4 h-4' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
    </svg>
  );
}

function IconArrowRight({ className = 'w-4 h-4' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
  );
}

// ── Data ──

interface GuideItem {
  title: string;
  description: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  iconBg: string;
  tags: string[];
}

interface ResourceItem {
  title: string;
  description: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  iconBg: string;
}

function IconKey({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
    </svg>
  );
}

function IconStream({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  );
}

function IconUsers({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
  );
}

function IconQuote({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function IconAddOns({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
    </svg>
  );
}

function IconPrint({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
    </svg>
  );
}

function IconWordPress({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.486 2 2 6.486 2 12s4.486 10 10 10 10-4.486 10-10S17.514 2 12 2zM3.009 12c0-1.298.29-2.529.8-3.64l4.404 12.065A8.993 8.993 0 013.009 12zm8.991 9c-.924 0-1.813-.15-2.646-.42l2.81-8.162 2.878 7.886c.019.046.042.089.065.13A8.94 8.94 0 0112 21zm1.237-13.22c.564-.03 1.072-.09 1.072-.09.505-.06.446-.802-.059-.772 0 0-1.518.12-2.497.12-.921 0-2.468-.12-2.468-.12-.505-.03-.564.742-.059.772 0 0 .478.06.983.09l1.46 4.002-2.052 6.155-3.413-10.157c.564-.03 1.072-.09 1.072-.09.505-.06.446-.802-.06-.772 0 0-1.517.12-2.496.12-.176 0-.383-.005-.6-.013A8.977 8.977 0 0112 3.009c2.34 0 4.472.895 6.071 2.36-.039-.002-.076-.008-.116-.008-1.005 0-1.716.875-1.716 1.817 0 .843.487 1.557 1.005 2.4.39.675.843 1.54.843 2.79 0 .867-.333 1.872-.773 3.272l-1.013 3.383L12.237 7.78z" />
    </svg>
  );
}

const guides: GuideItem[] = [
  {
    title: 'WordPress Plugin Guide',
    description: 'Step-by-step installation and configuration of the Encypher Provenance plugin for WordPress.',
    href: '/docs/wordpress-integration',
    icon: IconWordPress,
    iconBg: 'bg-gradient-to-br from-[#21759b] to-[#464646]',
    tags: ['WordPress', 'Plugin', '5 min setup'],
  },
  {
    title: 'Publisher Integration Guide',
    description: 'Complete guide to integrating Encypher into your CMS or publishing workflow.',
    href: '/docs/publisher-integration',
    icon: IconPublisher,
    iconBg: 'bg-gradient-to-br from-[#1B2F50] to-[#2A87C4]',
    tags: ['CMS', 'Publishing', 'Integration'],
  },
  {
    title: 'CMS Integrations',
    description: 'Connect Ghost, WordPress, or other CMS platforms to automatically sign content with C2PA provenance.',
    href: '/integrations',
    icon: IconIntegrations,
    iconBg: 'bg-gradient-to-br from-[#2A87C4] to-[#00CED1]',
    tags: ['Ghost', 'WordPress', 'Webhook', 'Setup'],
  },
  {
    title: 'Bring Your Own Key (BYOK)',
    description: 'Sign content with your own Ed25519 key pairs for full key custody and independent verification.',
    href: '/docs/byok',
    icon: IconKey,
    iconBg: 'bg-gradient-to-br from-[#1B2F50] to-[#00CED1]',
    tags: ['Enterprise', 'Security', 'Ed25519'],
  },
  {
    title: 'Streaming LLM Signing',
    description: 'Sign AI-generated text in real-time as it streams from language models with sub-millisecond overhead.',
    href: '/docs/streaming',
    icon: IconStream,
    iconBg: 'bg-gradient-to-br from-[#2A87C4] to-[#1B2F50]',
    tags: ['AI', 'Streaming', 'LLM', 'Real-time'],
  },
  {
    title: 'Coalition & Licensing',
    description: 'Join the Publisher Coalition to collectively license content to AI companies with 60/40 revenue share.',
    href: '/docs/coalition',
    icon: IconUsers,
    iconBg: 'bg-gradient-to-br from-[#00CED1] to-[#2A87C4]',
    tags: ['Coalition', 'Licensing', 'Revenue'],
  },
  {
    title: 'Quote Integrity Verification',
    description: 'Detect AI hallucinations and misattributions by verifying quotes against signed source documents.',
    href: '/docs/quote-integrity',
    icon: IconQuote,
    iconBg: 'bg-gradient-to-br from-[#1B2F50] to-[#2A87C4]',
    tags: ['Verification', 'AI', 'Fact-checking'],
  },
  {
    title: 'Print Leak Detection',
    description: 'Identify the source of leaked physical documents by embedding imperceptible spacing fingerprints that survive printing and scanning.',
    href: '/docs/print-leak-detection',
    icon: IconPrint,
    iconBg: 'bg-gradient-to-br from-[#1B2F50] to-[#00CED1]',
    tags: ['Enterprise', 'Print', 'Forensics'],
  },
  {
    title: 'Add-Ons',
    description: 'Overview of all purchasable add-ons: Custom Signing Identity, White-Label Verification, BYOK, Priority Support, and Bulk Archive Backfill.',
    href: '/docs/add-ons',
    icon: IconAddOns,
    iconBg: 'bg-gradient-to-br from-[#2A87C4] to-[#00CED1]',
    tags: ['Billing', 'Add-ons', 'Self-service'],
  },
];

const externalResources: ResourceItem[] = [
  {
    title: 'API Reference',
    description: 'Interactive Swagger UI documentation for all API endpoints.',
    href: 'https://api.encypher.com/docs',
    icon: IconApi,
    iconBg: 'bg-gradient-to-br from-[#1B2F50] to-[#2A87C4]',
  },
  {
    title: 'Python SDK',
    description: 'Official Python client library on PyPI.',
    href: 'https://pypi.org/project/encypher/',
    icon: IconPython,
    iconBg: 'bg-gradient-to-br from-[#2A87C4] to-[#1B2F50]',
  },
  {
    title: 'TypeScript SDK',
    description: 'Official TypeScript/Node.js client on npm.',
    href: 'https://www.npmjs.com/package/@encypher/sdk',
    icon: IconTypeScript,
    iconBg: 'bg-gradient-to-br from-[#00CED1] to-[#2A87C4]',
  },
];

export default function DocsPage() {
  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto">
        {/* Page header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-delft-blue dark:text-white">Documentation</h1>
          <p className="text-sm text-muted-foreground mt-1">Guides, references, and SDKs for integrating Encypher into your workflow.</p>
        </div>

        {/* Integration Guides */}
        <section className="mb-10">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">Integration Guides</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {guides.map((guide) => {
              const Icon = guide.icon;
              return (
                <Link key={guide.href} href={guide.href} className="group block">
                  <div className="h-full bg-white dark:bg-slate-800 rounded-xl border border-border p-5 transition-all duration-200 hover:shadow-md hover:border-[#2A87C4]/40">
                    <div className="flex items-start gap-4">
                      <div className={`w-10 h-10 ${guide.iconBg} rounded-lg flex items-center justify-center text-white flex-shrink-0`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-delft-blue dark:text-white group-hover:text-[#2A87C4] transition-colors">
                          {guide.title}
                        </h3>
                        <p className="text-sm text-muted-foreground mt-1 leading-relaxed">{guide.description}</p>
                        <div className="flex flex-wrap gap-1.5 mt-3">
                          {guide.tags.map((tag) => (
                            <span
                              key={tag}
                              className="px-2 py-0.5 text-[11px] font-medium bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="text-slate-300 dark:text-slate-600 group-hover:text-[#2A87C4] transition-colors mt-1">
                        <IconArrowRight />
                      </div>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

        {/* External Resources */}
        <section>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">SDKs &amp; References</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {externalResources.map((resource) => {
              const Icon = resource.icon;
              return (
                <a
                  key={resource.href}
                  href={resource.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group block"
                >
                  <div className="h-full bg-white dark:bg-slate-800 rounded-xl border border-border p-5 transition-all duration-200 hover:shadow-md hover:border-[#2A87C4]/40">
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`w-9 h-9 ${resource.iconBg} rounded-lg flex items-center justify-center text-white flex-shrink-0`}>
                        <Icon className="w-[18px] h-[18px]" />
                      </div>
                      <h3 className="font-semibold text-delft-blue dark:text-white group-hover:text-[#2A87C4] transition-colors flex items-center gap-1.5">
                        {resource.title}
                        <IconExternal className="w-3.5 h-3.5 text-slate-400" />
                      </h3>
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed">{resource.description}</p>
                  </div>
                </a>
              );
            })}
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}
