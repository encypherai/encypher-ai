'use client';

import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  ArrowRight,
  CheckCircle2,
  Shield,
  Zap,
  Users,
  Lock,
  BarChart3,
  FileCheck,
  Infinity,
  Crown,
  Handshake,
  Scale,
} from 'lucide-react';
import Link from 'next/link';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import AISummary from '@/components/seo/AISummary';
import SalesContactModal from '@/components/forms/SalesContactModal';
import {
  ENTERPRISE_TIER,
  LICENSING_REV_SHARE,
} from '@/lib/pricing-config';

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypherai.com';

const ENTERPRISE_HIGHLIGHTS = [
  {
    icon: Infinity,
    title: 'Unlimited Everything',
    description: 'No caps on signing volume, API calls, Merkle trees, embeddings, or verifications. Scale without limits.',
  },
  {
    icon: Shield,
    title: 'Dedicated SLA & Support',
    description: '99.9% uptime guarantee, 15-minute incident response, 24/7 priority support with a named account manager.',
  },
  {
    icon: Lock,
    title: 'SSO, BYOK & Team Management',
    description: 'SAML/OAuth single sign-on, bring your own signing certificates, and role-based access controls for unlimited team members.',
  },
  {
    icon: BarChart3,
    title: 'Advanced Attribution Intelligence',
    description: 'Cross-org search, fuzzy fingerprint matching, multi-source attribution with authority ranking, and robust fingerprinting that survives paraphrasing.',
  },
  {
    icon: Zap,
    title: 'Streaming LLM Signing',
    description: 'Real-time WebSocket/SSE signing for LLM outputs. OpenAI-compatible /chat/completions endpoint with automatic signing.',
  },
  {
    icon: FileCheck,
    title: 'Court-Ready Evidence & Revocation',
    description: 'Evidence package generation, document revocation (StatusList2021), full audit trail, and C2PA provenance chain tracking.',
  },
];

const FREE_VS_ENTERPRISE = [
  { feature: 'C2PA signing + Merkle tree auth', free: true, enterprise: true },
  { feature: 'Invisible Unicode embeddings', free: true, enterprise: true },
  { feature: 'Public verification API', free: true, enterprise: true },
  { feature: 'Coalition membership & licensing', free: true, enterprise: true },
  { feature: 'Streaming signing (SSE/WebSocket)', free: true, enterprise: true },
  { feature: 'Monthly signing quota', free: '1,000 docs', enterprise: 'Unlimited' },
  { feature: 'Batch operations', free: '10 docs', enterprise: '100+ docs' },
  { feature: 'API keys', free: '2', enterprise: 'Unlimited' },
  { feature: 'Cross-org search & fuzzy matching', free: false, enterprise: true },
  { feature: 'Robust fingerprinting', free: false, enterprise: true },
  { feature: 'Evidence package generation', free: false, enterprise: true },
  { feature: 'Document revocation', free: false, enterprise: true },
  { feature: 'Custom C2PA assertions & schemas', free: false, enterprise: true },
  { feature: 'C2PA provenance chain', free: false, enterprise: true },
  { feature: 'Team management (RBAC)', free: false, enterprise: true },
  { feature: 'SSO (SAML/OAuth)', free: false, enterprise: true },
  { feature: 'BYOK (own signing keys)', free: false, enterprise: true },
  { feature: 'Webhooks', free: false, enterprise: true },
  { feature: 'Dedicated SLA (99.9%)', free: false, enterprise: true },
  { feature: '24/7 support + named account manager', free: false, enterprise: true },
];

export default function EnterprisePage() {
  const [showContactModal, setShowContactModal] = useState(false);

  return (
    <div className="bg-background text-foreground">
      <AISummary
        title="Encypher Enterprise"
        whatWeDo="Encypher Enterprise provides unlimited content signing, court-ready evidence generation, and advanced attribution intelligence built on the C2PA standard we authored (Section A.7, published January 8, 2026)."
        whoItsFor="Major publishers, news organizations, and content platforms needing unlimited signing volume, dedicated SLA, SSO/BYOK, team management, and advanced enforcement capabilities."
        keyDifferentiator="Everything in Free tier — unlimited. Plus exclusive capabilities: streaming LLM signing, robust fingerprinting, cross-org search, fuzzy matching, evidence generation, document revocation, and dedicated enterprise support."
        primaryValue="Custom implementation with all add-ons included. Two-track licensing: coalition deals (60/40) or self-service deals (80/20). Founding coalition members get implementation fees waived."
      />

      {/* Hero Section */}
      <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4 text-center">
          <Badge variant="outline" className="mb-6 text-sm px-4 py-1.5">
            <Crown className="h-3.5 w-3.5 mr-1.5" />
            Enterprise Plan
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            Unlimited Signing.<br />Full Enforcement.<br />Dedicated Support.
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-8">
            Everything in the Free tier — with no limits. Plus exclusive capabilities for streaming LLM signing, 
            advanced attribution, court-ready evidence, and enterprise-grade security. 
            Custom implementation from the authors of the C2PA text standard.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              onClick={() => setShowContactModal(true)}
              size="lg"
              className="font-semibold"
            >
              Contact Sales <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href={`${DASHBOARD_URL}/auth/signin?mode=signup&source=enterprise`}>
                Start Free — Upgrade Later <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="ghost" size="lg">
              <Link href="/pricing">
                Compare Plans <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Enterprise Highlights */}
      <section className="py-20 w-full bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Enterprise-Exclusive Capabilities
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Beyond unlimited volume — capabilities that only Enterprise customers get access to.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {ENTERPRISE_HIGHLIGHTS.map((item) => {
              const IconComponent = item.icon;
              return (
                <div key={item.title} className="bg-card p-6 rounded-lg border border-border hover:border-primary/30 transition-colors">
                  <IconComponent className="h-10 w-10 text-primary mb-4" />
                  <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-muted-foreground">{item.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Feature Comparison Table */}
      <section className="py-20 w-full bg-muted/30 border-y border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Free vs. Enterprise
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Free gives you full signing infrastructure. Enterprise removes all limits and adds exclusive capabilities.
            </p>
          </div>

          <div className="max-w-4xl mx-auto overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-border">
                  <th className="text-left py-4 px-4 font-semibold">Feature</th>
                  <th className="text-center py-4 px-4 font-semibold w-32">Free</th>
                  <th className="text-center py-4 px-4 font-semibold w-32 bg-primary/5 rounded-t-lg">Enterprise</th>
                </tr>
              </thead>
              <tbody>
                {FREE_VS_ENTERPRISE.map((row, i) => (
                  <tr key={row.feature} className={i % 2 === 0 ? 'bg-card/50' : ''}>
                    <td className="py-3 px-4 text-sm">{row.feature}</td>
                    <td className="py-3 px-4 text-center">
                      {row.free === true ? (
                        <CheckCircle2 className="h-5 w-5 text-primary mx-auto" />
                      ) : row.free === false ? (
                        <span className="text-muted-foreground">—</span>
                      ) : (
                        <span className="text-sm font-medium">{row.free}</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center bg-primary/5">
                      {row.enterprise === true ? (
                        <CheckCircle2 className="h-5 w-5 text-primary mx-auto" />
                      ) : (
                        <span className="text-sm font-medium text-primary">{row.enterprise}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Standards Compliance */}
      <StandardsCompliance />

      {/* Final CTA */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Scale Your Content Protection?
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            Start free today and upgrade when you need unlimited volume, exclusive capabilities, and dedicated support. Or talk to sales to discuss enterprise implementation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              onClick={() => setShowContactModal(true)}
              size="lg"
              className="font-semibold"
            >
              Contact Enterprise Sales <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href={`${DASHBOARD_URL}/auth/signin?mode=signup&source=enterprise`}>
                Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="ghost" size="lg">
              <Link href="/publisher-demo">
                See Publisher Demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Sales Contact Modal */}
      <AnimatePresence>
        {showContactModal && (
          <SalesContactModal
            onClose={() => setShowContactModal(false)}
            context="enterprise"
          />
        )}
      </AnimatePresence>
    </div>
  );
}
