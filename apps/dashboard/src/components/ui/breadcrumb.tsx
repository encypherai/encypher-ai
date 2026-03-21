'use client';

import { useMemo } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const SEGMENT_LABELS: Record<string, string> = {
  'api-keys': 'API Keys',
  'ai-crawlers': 'AI Crawlers',
  'audit-logs': 'Audit Logs',
  'cdn-analytics': 'CDN Analytics',
  'print-detection': 'Print Leak Detection',
  'image-signing': 'Image Signing',
  analytics: 'Content Performance',
  billing: 'Billing',
  compliance: 'EU AI Act Compliance',
  docs: 'Documentation',
  enforcement: 'Enforcement',
  governance: 'Governance',
  integrations: 'Integrations',
  playground: 'API Playground',
  rights: 'Rights Management',
  settings: 'Settings',
  organization: 'Organization',
  support: 'Support',
  team: 'Team',
  webhooks: 'Webhooks',
};

export function Breadcrumb() {
  const pathname = usePathname();

  // Build breadcrumb items (must be before any early returns -- hooks rules)
  const items = useMemo(() => {
    if (pathname === '/' || pathname === '') return [];
    const segs = pathname.split('/').filter(Boolean);
    return segs.map((segment, index) => {
      const href = '/' + segs.slice(0, index + 1).join('/');
      const label =
        SEGMENT_LABELS[segment] ||
        segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');
      const isLast = index === segs.length - 1;
      return { href, label, isLast };
    });
  }, [pathname]);

  if (items.length === 0) return null;

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm text-muted-foreground mb-4">
      <Link href="/" className="hover:text-foreground transition-colors">
        Dashboard
      </Link>
      {items.map((item) => (
        <span key={item.href} className="flex items-center gap-1.5">
          <svg
            className="w-3.5 h-3.5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
          {item.isLast ? (
            <span className="text-foreground font-medium">{item.label}</span>
          ) : (
            <Link href={item.href} className="hover:text-foreground transition-colors">
              {item.label}
            </Link>
          )}
        </span>
      ))}
    </nav>
  );
}
