'use client';

import React from 'react';
import { Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { cn } from '@/lib/utils';

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypher.com';

// Feature availability: free, add-on (with price), enterprise-only, or specific value
type FeatureValue = 'free' | 'enterprise' | 'add-on' | string | boolean;

interface Feature {
  name: string;
  description: string;
  free: FeatureValue;
  enterprise: FeatureValue;
  addOn?: string;
}

interface FeatureCategory {
  name: string;
  features: Feature[];
}

// Feature definitions aligned with the new freemium model
// Free tier = full signing infra; Enterprise = unlimited everything + exclusive capabilities
const FEATURE_CATEGORIES: FeatureCategory[] = [
  {
    name: 'Core Platform (Free)',
    features: [
      { name: 'C2PA 2.3 Document Signing', description: 'Sign content with C2PA manifest', free: '1K/mo', enterprise: 'Unlimited' },
      { name: 'Merkle Tree Authentication', description: 'Sentence-level cryptographic proofs', free: true, enterprise: 'Unlimited' },
      { name: 'Invisible Unicode Embeddings', description: 'Survive copy-paste and scraping', free: true, enterprise: true },
      { name: 'Content Verification', description: 'Public verification pages + API', free: 'Unlimited', enterprise: 'Unlimited' },
      { name: 'Tamper Detection', description: 'Detect modifications to signed content', free: true, enterprise: true },
      { name: 'Custom Metadata', description: 'Author, publisher, license, tags', free: true, enterprise: true },
      { name: 'WordPress Plugin', description: 'Auto-sign on publish', free: true, enterprise: 'White-label' },
      { name: 'REST API + SDKs', description: 'Python, TypeScript, Go, Rust', free: true, enterprise: true },
      { name: 'CLI & CI/CD', description: 'CLI tool, GitHub Action, browser extension', free: true, enterprise: true },
    ],
  },
  {
    name: 'Coalition & Licensing (Free)',
    features: [
      { name: 'Coalition Membership', description: 'Auto-enrolled in Encypher Coalition', free: true, enterprise: true },
      { name: 'Content Indexing', description: 'Content indexed for coalition licensing', free: true, enterprise: true },
      { name: 'Basic Attribution View', description: 'See where your content appears', free: true, enterprise: true },
    ],
  },
  {
    name: 'Enterprise-Only Capabilities',
    features: [
      { name: 'Streaming LLM Signing', description: 'WebSocket/SSE real-time signing', free: false, enterprise: true },
      { name: 'OpenAI-Compatible Endpoint', description: '/chat/completions with auto-signing', free: false, enterprise: true },
      { name: 'Custom C2PA Assertions', description: 'Define custom assertion types + schema registry', free: false, enterprise: true },
      { name: 'Batch Operations', description: '100+ documents per request', free: false, enterprise: true },
      { name: 'Document Revocation', description: 'StatusList2021 revocation', free: false, enterprise: true },
      { name: 'Robust Fingerprinting', description: 'Survives paraphrasing, rewriting, translation', free: false, enterprise: true },
      { name: 'Plagiarism Detection', description: 'With Merkle proof linkage', free: false, enterprise: true },
      { name: 'SSO Integration', description: 'SAML, OAuth', free: false, enterprise: true },
      { name: 'Team Management', description: 'Role-based access controls', free: false, enterprise: true },
      { name: 'Dedicated SLA', description: '99.9% uptime, 15-min incident response', free: false, enterprise: true },
      { name: '24/7 Priority Support', description: 'Named account manager', free: false, enterprise: true },
    ],
  },
];

type ColumnId = 'free' | 'enterprise';

interface FeatureComparisonTableProps {
  currentPlan?: ColumnId | null;
}

function renderValue(value: FeatureValue, addOn?: string) {
  if (value === false) {
    if (addOn) {
      return <span className="text-xs font-medium text-primary">{addOn}</span>;
    }
    return <X className="h-4 w-4 text-muted-foreground/50 mx-auto" />;
  }
  if (value === true) {
    return <Check className="h-4 w-4 text-primary mx-auto" />;
  }
  return <span className="text-sm font-medium">{value}</span>;
}

export default function FeatureComparisonTable({
  currentPlan,
}: FeatureComparisonTableProps) {
  const columns: { id: ColumnId; name: string; price: string }[] = [
    { id: 'free', name: 'Free', price: '$0/mo' },
    { id: 'enterprise', name: 'Enterprise', price: 'Custom' },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse min-w-[600px]">
        <thead>
          <tr className="border-b-2 border-border">
            <th className="text-left py-4 px-4 font-semibold w-[320px]">Feature</th>
            {columns.map((col) => {
              const isCurrent = currentPlan === col.id;
              return (
                <th
                  key={col.id}
                  className={cn(
                    'text-center py-4 px-6 font-semibold relative border-l border-border',
                    isCurrent && 'bg-primary/10 border-x-2 border-t-2 border-primary'
                  )}
                >
                  {isCurrent && (
                    <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-xs">
                      Current Plan
                    </Badge>
                  )}
                  <div className="pt-2">
                    {col.name}
                    <br />
                    <span className="text-xs font-normal text-muted-foreground">{col.price}</span>
                  </div>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody className="text-sm">
          {FEATURE_CATEGORIES.map((category) => (
            <React.Fragment key={category.name}>
              <tr className="bg-muted/50">
                <td className="py-3 px-4 font-bold text-foreground" colSpan={3}>
                  {category.name}
                </td>
              </tr>
              {category.features.map((feature) => (
                <tr key={feature.name} className="border-b border-border/50 hover:bg-muted/20">
                  <td className="py-3 px-4">
                    <div className="font-medium">{feature.name}</div>
                    <div className="text-xs text-muted-foreground">{feature.description}</div>
                  </td>
                  {columns.map((col) => {
                    const isCurrent = currentPlan === col.id;
                    const value = feature[col.id];
                    return (
                      <td
                        key={col.id}
                        className={cn(
                          'text-center py-3 px-6 border-l border-border',
                          isCurrent && 'bg-primary/10 border-x-2 border-primary'
                        )}
                      >
                        {renderValue(value, col.id === 'free' ? feature.addOn : undefined)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </React.Fragment>
          ))}
        </tbody>
        <tfoot>
          <tr className="border-t-2 border-border">
            <td className="py-4 px-4"></td>
            <td className="text-center py-4 px-6 border-l border-border">
              <Button className="w-full" asChild>
                <Link href={`${DASHBOARD_URL}/auth/signin?mode=signup&source=pricing-free`}>
                  Get Started Free
                </Link>
              </Button>
            </td>
            <td className="text-center py-4 px-6 border-l border-border">
              <Button variant="outline" className="w-full" asChild>
                <Link href="/company#contact">Contact Sales</Link>
              </Button>
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
