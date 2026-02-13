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

const guides: GuideItem[] = [
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
];

const externalResources: ResourceItem[] = [
  {
    title: 'API Reference',
    description: 'Interactive Swagger UI documentation for all API endpoints.',
    href: 'https://api.encypherai.com/docs',
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
