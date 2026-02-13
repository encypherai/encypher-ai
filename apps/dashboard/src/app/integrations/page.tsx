'use client';

import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { GhostIntegrationCard } from './GhostIntegrationCard';
import { ChromeExtensionCard } from './ChromeExtensionCard';
import { Card, CardHeader, CardTitle, CardDescription } from '@encypher/design-system';

const comingSoonIntegrations = [
  {
    name: 'WordPress',
    description: 'Automatic C2PA signing for WordPress posts via our plugin.',
    icon: (
      <svg viewBox="0 0 24 24" className="w-8 h-8 text-[#21759b]" fill="currentColor">
        <path d="M12 2C6.486 2 2 6.486 2 12s4.486 10 10 10 10-4.486 10-10S17.514 2 12 2zM3.009 12c0-1.298.29-2.529.8-3.64l4.404 12.065A8.993 8.993 0 013.009 12zm8.991 9c-.924 0-1.813-.15-2.646-.42l2.81-8.162 2.878 7.886c.019.046.042.089.065.13A8.94 8.94 0 0112 21zm1.237-13.22c.564-.03 1.072-.09 1.072-.09.505-.06.446-.802-.059-.772 0 0-1.518.12-2.497.12-.921 0-2.468-.12-2.468-.12-.505-.03-.564.742-.059.772 0 0 .478.06.983.09l1.46 4.002-2.052 6.155-3.413-10.157c.564-.03 1.072-.09 1.072-.09.505-.06.446-.802-.06-.772 0 0-1.517.12-2.496.12-.176 0-.383-.005-.6-.013A8.977 8.977 0 0112 3.009c2.34 0 4.472.895 6.071 2.36-.039-.002-.076-.008-.116-.008-1.005 0-1.716.875-1.716 1.817 0 .843.487 1.557 1.005 2.4.39.675.843 1.54.843 2.79 0 .867-.333 1.872-.773 3.272l-1.013 3.383L12.237 7.78z" />
      </svg>
    ),
    status: 'Plugin available' as const,
    href: '/docs/publisher-integration',
  },
  {
    name: 'Substack',
    description: 'Sign your Substack newsletter content with C2PA provenance.',
    icon: (
      <svg viewBox="0 0 24 24" className="w-8 h-8 text-[#FF6719]" fill="currentColor">
        <path d="M22.539 8.242H1.46V5.406h21.08v2.836zM1.46 10.812V24L12 18.11 22.54 24V10.812H1.46zM22.54 0H1.46v2.836h21.08V0z" />
      </svg>
    ),
    status: 'coming_soon' as const,
  },
  {
    name: 'Medium',
    description: 'Embed provenance markers in your Medium articles automatically.',
    icon: (
      <svg viewBox="0 0 24 24" className="w-8 h-8 text-slate-800 dark:text-slate-200" fill="currentColor">
        <path d="M13.54 12a6.8 6.8 0 01-6.77 6.82A6.8 6.8 0 010 12a6.8 6.8 0 016.77-6.82A6.8 6.8 0 0113.54 12zM20.96 12c0 3.54-1.51 6.42-3.38 6.42-1.87 0-3.39-2.88-3.39-6.42s1.52-6.42 3.39-6.42 3.38 2.88 3.38 6.42M24 12c0 3.17-.53 5.75-1.19 5.75-.66 0-1.19-2.58-1.19-5.75s.53-5.75 1.19-5.75C23.47 6.25 24 8.83 24 12z" />
      </svg>
    ),
    status: 'coming_soon' as const,
  },
];

export default function IntegrationsPage() {
  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-delft-blue dark:text-white">
            Integrations
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Connect your CMS to automatically sign content with C2PA provenance. One webhook, zero infrastructure.
          </p>
        </div>

        {/* Browser Extensions */}
        <section className="mb-10">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">
            Browser Extensions
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <ChromeExtensionCard />
          </div>
        </section>

        {/* CMS Platforms */}
        <section className="mb-10">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">
            CMS Platforms
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Ghost — fully functional */}
            <GhostIntegrationCard />

            {/* Coming soon cards */}
            {comingSoonIntegrations.map((integration) => (
              <Card
                key={integration.name}
                variant="bordered"
                className="relative overflow-hidden opacity-80"
              >
                <CardHeader>
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center">
                      {integration.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-lg">{integration.name}</CardTitle>
                        {integration.status === 'coming_soon' ? (
                          <span className="px-2 py-0.5 text-xs font-medium bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 rounded-full">
                            Coming Soon
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full">
                            Plugin
                          </span>
                        )}
                      </div>
                      <CardDescription className="mt-1">
                        {integration.description}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                {integration.href && (
                  <div className="px-6 pb-4">
                    <a
                      href={integration.href}
                      className="text-sm text-blue-ncs hover:underline font-medium"
                    >
                      View setup guide &rarr;
                    </a>
                  </div>
                )}
              </Card>
            ))}
          </div>
        </section>

        {/* Help section */}
        <section className="mt-12 p-6 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-semibold text-delft-blue dark:text-white mb-2">
            Need a different integration?
          </h3>
          <p className="text-sm text-muted-foreground mb-3">
            You can use our REST API or SDKs to integrate Encypher into any publishing workflow.
            Check the docs or contact us for custom integration support.
          </p>
          <div className="flex gap-3">
            <a
              href="/docs/publisher-integration"
              className="text-sm font-medium text-blue-ncs hover:underline"
            >
              Publisher Integration Guide &rarr;
            </a>
            <a
              href="https://api.encypherai.com/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-blue-ncs hover:underline"
            >
              API Reference &rarr;
            </a>
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}
