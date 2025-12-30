'use client';

import { DashboardLayout } from '../../components/layout/DashboardLayout';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@encypher/design-system';

const guides = [
  {
    title: 'Publisher Integration Guide',
    description: 'Complete guide to integrating Encypher into your CMS or publishing workflow. Covers all tiers from Starter to Enterprise.',
    href: '/docs/publisher-integration',
    icon: '📰',
    tags: ['CMS', 'Publishing', 'Integration'],
  },
];

const externalResources = [
  {
    title: 'API Reference',
    description: 'Interactive Swagger UI documentation for all API endpoints',
    href: 'https://api.encypherai.com/docs',
    icon: '📚',
    external: true,
  },
  {
    title: 'Python SDK',
    description: 'Official Python client library on PyPI',
    href: 'https://pypi.org/project/encypher/',
    icon: '🐍',
    external: true,
  },
  {
    title: 'TypeScript SDK',
    description: 'Official TypeScript/Node.js client on npm',
    href: 'https://www.npmjs.com/package/@encypher/sdk',
    icon: '📦',
    external: true,
  },
];

export default function DocsPage() {
  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-delft-blue dark:text-white mb-2">Documentation</h1>
          <p className="text-muted-foreground">Guides, tutorials, and API reference for integrating Encypher</p>
        </div>

        {/* Integration Guides */}
        <section className="mb-10">
          <h2 className="text-xl font-semibold text-delft-blue dark:text-white mb-4">Integration Guides</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {guides.map((guide) => (
              <Link key={guide.href} href={guide.href} className="block group">
                <Card className="h-full transition-all duration-200 hover:shadow-lg hover:border-blue-ncs/50">
                  <CardHeader>
                    <div className="flex items-start gap-3">
                      <span className="text-3xl">{guide.icon}</span>
                      <div>
                        <CardTitle className="group-hover:text-blue-ncs transition-colors">
                          {guide.title}
                        </CardTitle>
                        <CardDescription className="mt-1">{guide.description}</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {guide.tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-1 text-xs font-medium bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </section>

        {/* External Resources */}
        <section>
          <h2 className="text-xl font-semibold text-delft-blue dark:text-white mb-4">External Resources</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {externalResources.map((resource) => (
              <a
                key={resource.href}
                href={resource.href}
                target="_blank"
                rel="noopener noreferrer"
                className="block group"
              >
                <Card className="h-full transition-all duration-200 hover:shadow-lg hover:border-blue-ncs/50">
                  <CardHeader>
                    <div className="flex items-start gap-3">
                      <span className="text-3xl">{resource.icon}</span>
                      <div>
                        <CardTitle className="group-hover:text-blue-ncs transition-colors flex items-center gap-2">
                          {resource.title}
                          <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </CardTitle>
                        <CardDescription className="mt-1">{resource.description}</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              </a>
            ))}
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}
