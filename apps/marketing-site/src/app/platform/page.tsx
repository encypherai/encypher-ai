'use client';

import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  ArrowRight,
  CheckCircle2,
  Shield,
  Fingerprint,
  FileSearch,
  Scale,
  Code2,
  Layers,
  Globe,
  Terminal,
  BookOpen,
  Server,
} from 'lucide-react';
import Link from 'next/link';
import StandardsCompliance from '@/components/solutions/standards-compliance';
import AISummary from '@/components/seo/AISummary';
import SalesContactModal from '@/components/forms/SalesContactModal';

const DASHBOARD_URL = process.env.NEXT_PUBLIC_DASHBOARD_URL || 'https://dashboard.encypher.com';

const CORE_CAPABILITIES = [
  {
    icon: Shield,
    title: 'C2PA Document Signing',
    description:
      'Sign text content with C2PA 2.3-compliant manifests. Sentence-level Merkle tree authentication creates tamper-evident provenance for every paragraph.',
  },
  {
    icon: Fingerprint,
    title: 'Invisible Embeddings',
    description:
      'Patent-pending Unicode watermarks survive copy-paste, CMS rendering, email forwarding, and web scraping. Invisible to readers, machine-readable for verification.',
  },
  {
    icon: FileSearch,
    title: 'Attribution & Verification',
    description:
      'Public verification API lets anyone confirm content origin. Quote integrity verification checks whether AI-generated citations match signed source material.',
  },
  {
    icon: Scale,
    title: 'Enforcement Pipeline',
    description:
      'From detection to licensing: attribution analytics show where content appears in AI outputs, formal notices establish willful infringement, and evidence packages are court-ready.',
  },
  {
    icon: Layers,
    title: 'Rights Management',
    description:
      'Publisher rights profiles, licensing terms, and usage policies travel with content. AI companies can resolve rights programmatically before ingestion.',
  },
  {
    icon: Globe,
    title: 'Coalition Licensing',
    description:
      'Auto-enrolled in the Encypher Coalition. Content is indexed for licensing deals. Publishers receive the majority of revenue on every deal -- same splits across all tiers.',
  },
];

const INFRASTRUCTURE_STACK = [
  { layer: 'Signing', detail: 'C2PA 2.3 manifests, Merkle trees, invisible embeddings' },
  { layer: 'Storage', detail: 'Content references, Merkle subhashes, attribution reports' },
  { layer: 'Verification', detail: 'Public API, tamper detection, quote integrity' },
  { layer: 'Enforcement', detail: 'Attribution analytics, formal notices, evidence packages' },
  { layer: 'Licensing', detail: 'Rights profiles, resolution URLs, coalition deals' },
  { layer: 'Distribution', detail: 'WordPress plugin, REST API, CLI, GitHub Action, browser extension' },
];

const COMPETITIVE_POSITIONING = [
  {
    us: 'Sentence-level Merkle tree authentication',
    them: 'Document-level hashing only',
  },
  {
    us: 'Invisible embeddings survive copy-paste and scraping',
    them: 'Visible watermarks easily removed',
  },
  {
    us: 'Co-Chair of C2PA Text Provenance Task Force',
    them: 'Third-party C2PA implementation',
  },
  {
    us: 'Quote integrity verification for AI attribution',
    them: 'No AI-specific verification capabilities',
  },
  {
    us: 'Court-ready evidence packages with chain of custody',
    them: 'Basic detection reports',
  },
  {
    us: 'Free signing infrastructure with paid enforcement',
    them: 'Per-document signing fees from day one',
  },
];

export default function PlatformPage() {
  const [showContactModal, setShowContactModal] = useState(false);

  return (
    <div className="bg-background text-foreground">
      <AISummary
        title="Encypher Platform"
        whatWeDo="Co-Chair of C2PA Text Provenance Task Force. Enterprise API and SDKs in Python, TypeScript, Go, and Rust for content authentication infrastructure. Standard publishes January 8, 2026."
        whoItsFor="Publishers needing provable content ownership. AI labs needing performance intelligence and quote integrity verification. Enterprises requiring EU AI Act and China watermarking compliance."
        keyDifferentiator="Cryptographic watermarking survives copy-paste, B2B distribution, and scraping. One API for entire publisher ecosystem."
        primaryValue="Building standards with NYT, BBC, AP, Google, OpenAI, Adobe, Microsoft and others through C2PA (c2pa.org). Working with industry leaders to define content licensing frameworks."
      />

      {/* Hero Section */}
      <section className="relative w-full py-20 md:py-32 bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4 text-center">
          <Badge variant="outline" className="mb-6 text-sm px-4 py-1.5">
            <Layers className="h-3.5 w-3.5 mr-1.5" />
            C2PA Text Infrastructure
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            The Complete Stack for<br />Text Content Authenticity
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-muted-foreground mb-8">
            Sign, verify, attribute, and license text content with cryptographic provenance.
            Built on the C2PA standard we co-authored. Free infrastructure for every publisher.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="font-semibold">
              <Link href={`${DASHBOARD_URL}/auth/signin?mode=signup&source=platform`}>
                Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/publisher-demo">
                See Live Demo <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button
              onClick={() => setShowContactModal(true)}
              size="lg"
              variant="ghost"
              className="font-semibold"
            >
              Contact Sales <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>

      {/* Infrastructure Stack */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              <Link href="/c2pa-standard/media-types" className="text-primary underline underline-offset-2 hover:no-underline">C2PA</Link> Text Infrastructure Stack
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Six layers that take content from signing through licensing.
              Each layer is production-ready and accessible via REST API.
            </p>
          </div>

          <div className="max-w-3xl mx-auto space-y-0">
            {INFRASTRUCTURE_STACK.map((item, i) => (
              <div
                key={item.layer}
                className={`flex items-center gap-6 p-5 border border-border ${
                  i === 0 ? 'rounded-t-lg' : ''
                } ${i === INFRASTRUCTURE_STACK.length - 1 ? 'rounded-b-lg' : ''} ${
                  i % 2 === 0 ? 'bg-card/50' : 'bg-background'
                }`}
              >
                <span className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center text-sm font-bold">
                  {i + 1}
                </span>
                <div>
                  <span className="font-semibold">{item.layer}</span>
                  <span className="text-muted-foreground ml-2 text-sm">
                    {item.detail}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Core Capabilities Grid (6 cards) */}
      <section className="py-20 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Core Capabilities
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Everything you need to protect, verify, and monetize text content.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {CORE_CAPABILITIES.map((item) => {
              const IconComponent = item.icon;
              return (
                <div
                  key={item.title}
                  className="bg-card p-6 rounded-lg border border-border hover:border-primary/30 transition-colors"
                >
                  <IconComponent className="h-10 w-10 text-primary mb-4" />
                  <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-muted-foreground">
                    {item.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Standards Compliance */}
      <StandardsCompliance />

      {/* Developer Section */}
      <section className="py-20 w-full bg-background border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Built for Developers
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              One API call to sign. One API call to verify. Production-grade SLAs for every scale.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {/* API Specifications */}
            <div className="bg-card p-6 rounded-lg border border-border">
              <Server className="h-8 w-8 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-2">API Specifications</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Production-grade infrastructure with documented limits and uptime guarantees.
              </p>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between items-start border-b border-border pb-2">
                  <span className="text-muted-foreground">Rate limit</span>
                  <span className="font-mono font-medium text-right text-xs">1K / min (Growth)<br />10K / min (Ent.)</span>
                </div>
                <div className="flex justify-between items-start border-b border-border pb-2">
                  <span className="text-muted-foreground">Batch size</span>
                  <span className="font-mono font-medium">10K docs/req</span>
                </div>
                <div className="flex justify-between items-start border-b border-border pb-2">
                  <span className="text-muted-foreground">Uptime SLA</span>
                  <span className="font-mono font-medium">99.95%</span>
                </div>
                <div className="flex justify-between items-start">
                  <span className="text-muted-foreground">Idempotency</span>
                  <span className="font-mono font-medium text-xs">Idempotency-Key</span>
                </div>
              </div>
            </div>

            {/* REST API */}
            <div className="bg-card p-6 rounded-lg border border-border">
              <Terminal className="h-8 w-8 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-2">REST API</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Full-featured REST API with Python, TypeScript, Go, and Rust SDKs. Batch endpoints for archive workflows.
              </p>
              <div className="bg-muted rounded-md p-3 font-mono text-xs space-y-1">
                <div>
                  <span className="text-muted-foreground">POST</span>{' '}
                  <span className="text-primary">/api/v1/sign</span>
                </div>
                <div>
                  <span className="text-muted-foreground">POST</span>{' '}
                  <span className="text-primary">/api/v1/sign/batch</span>
                </div>
                <div>
                  <span className="text-muted-foreground">POST</span>{' '}
                  <span className="text-primary">/api/v1/verify/advanced</span>
                </div>
                <div>
                  <span className="text-muted-foreground">POST</span>{' '}
                  <span className="text-primary">/api/v1/verify/quote-integrity</span>
                </div>
                <div>
                  <span className="text-muted-foreground">GET</span>{' '}
                  <span className="text-primary">/api/v1/rights/analytics</span>
                </div>
              </div>
            </div>

            {/* Integrations */}
            <div className="bg-card p-6 rounded-lg border border-border">
              <Code2 className="h-8 w-8 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-2">Integrations</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Drop-in plugins for existing workflows. Kafka event streaming for high-throughput pipelines.
              </p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  WordPress plugin
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  GitHub Action
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  Kafka event streaming
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  CLI tool + browser extension
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  OpenAPI 3.1 spec included
                </li>
              </ul>
            </div>

            {/* Documentation */}
            <div className="bg-card p-6 rounded-lg border border-border">
              <BookOpen className="h-8 w-8 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-2">Documentation</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Comprehensive guides, API reference, and interactive playground for testing before you commit.
              </p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  Quick-start guide
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  Full API reference
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  Interactive playground
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  Publisher integration guide
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                  Archive signing cookbook
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Competitive Positioning */}
      <section className="py-20 w-full bg-muted/30 border-b border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Why Encypher
            </h2>
            <p className="text-lg text-muted-foreground mt-4 max-w-3xl mx-auto">
              Purpose-built for text content authenticity. Not an afterthought bolted onto image tools.
            </p>
          </div>

          <div className="max-w-4xl mx-auto overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-border">
                  <th className="text-left py-4 px-4 font-semibold">Capability</th>
                  <th className="text-center py-4 px-4 font-semibold w-40 bg-primary/5 rounded-t-lg">
                    Encypher
                  </th>
                  <th className="text-center py-4 px-4 font-semibold w-40">
                    Alternatives
                  </th>
                </tr>
              </thead>
              <tbody>
                {COMPETITIVE_POSITIONING.map((row, i) => (
                  <tr key={i} className={i % 2 === 0 ? 'bg-card/50' : ''}>
                    <td className="py-3 px-4 text-sm bg-primary/5 font-medium">
                      {row.us}
                    </td>
                    <td className="py-3 px-4 text-center bg-primary/5">
                      <CheckCircle2 className="h-5 w-5 text-primary mx-auto" />
                    </td>
                    <td className="py-3 px-4 text-center text-sm text-muted-foreground">
                      {row.them}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 w-full bg-background border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Start Protecting Your Content Today
          </h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto text-muted-foreground">
            Free signing infrastructure for every publisher. Add enforcement tools when you are ready to license.
            Enterprise plans for organizations that need unlimited volume and dedicated support.
            Read our guide to <Link href="/content-provenance/verification" className="text-primary underline underline-offset-2 hover:no-underline">content provenance verification</Link>.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="font-semibold">
              <Link href={`${DASHBOARD_URL}/auth/signin?mode=signup&source=platform`}>
                Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/pricing">
                View Pricing <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button
              onClick={() => setShowContactModal(true)}
              size="lg"
              variant="ghost"
              className="font-semibold"
            >
              Contact Sales <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>

      {/* Sales Contact Modal */}
      <AnimatePresence>
        {showContactModal && (
          <SalesContactModal
            onClose={() => setShowContactModal(false)}
            context="general"
          />
        )}
      </AnimatePresence>
    </div>
  );
}
